#!/usr/bin/env bun

import { parseArgs } from "util";
import { readdir, stat, readFile, writeFile, mkdir } from "fs/promises";
import { join, basename, extname, resolve } from "path";

const BASE = "https://api.assemblyai.com/v2";
const VIDEO_EXTS = new Set([".mp4", ".mov", ".mkv", ".avi", ".webm", ".mp3", ".wav", ".m4a", ".flac", ".ogg"]);

const { values } = parseArgs({
  args: process.argv.slice(2),
  options: {
    input: { type: "string", short: "i" },
    output: { type: "string", short: "o" },
    concurrency: { type: "string", short: "c", default: "5" },
    "url-list": { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
});

if (values.help || !values.input) {
  console.log(`
VURT Subtitle Generator — Batch SRT via AssemblyAI

Usage:
  bun run generate-srt.ts --input <path|file> [options]

Options:
  -i, --input       Video file, directory of videos, or URL list (.txt)
  -o, --output      Output directory for SRT files (default: same as source)
  --url-list        Treat input as a text file of URLs (one per line)
  -c, --concurrency Max parallel jobs (default: 5)
  -h, --help        Show this help

Examples:
  bun run generate-srt.ts -i ./videos/
  bun run generate-srt.ts -i video.mp4
  bun run generate-srt.ts -i urls.txt --url-list -o ./srts/
  bun run generate-srt.ts -i ./videos/ -c 10 -o ./output/
`);
  process.exit(0);
}

const API_KEY = process.env.ASSEMBLYAI_API_KEY;
if (!API_KEY) {
  console.error("ERROR: Set ASSEMBLYAI_API_KEY in Settings > Advanced");
  process.exit(1);
}
const HEADERS = { authorization: API_KEY, "content-type": "application/json" };

const CONCURRENCY = parseInt(values.concurrency || "5");
const OUTPUT_DIR = values.output ? resolve(values.output) : null;

interface Job {
  name: string;
  source: string; // file path or URL
  isUrl: boolean;
  outputPath: string;
}

interface Result {
  name: string;
  status: "success" | "error";
  srtPath?: string;
  duration?: number;
  error?: string;
}

async function collectJobs(): Promise<Job[]> {
  const input = resolve(values.input!);
  const jobs: Job[] = [];

  if (values["url-list"]) {
    const content = await readFile(input, "utf-8");
    const urls = content.split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"));
    for (const url of urls) {
      const name = decodeURIComponent(basename(new URL(url).pathname)).replace(extname(basename(new URL(url).pathname)), "");
      const outDir = OUTPUT_DIR || resolve(".");
      jobs.push({ name, source: url, isUrl: true, outputPath: join(outDir, `${name}.srt`) });
    }
  } else {
    const s = await stat(input);
    if (s.isFile()) {
      const name = basename(input, extname(input));
      const outDir = OUTPUT_DIR || resolve(input, "..");
      jobs.push({ name, source: input, isUrl: false, outputPath: join(outDir, `${name}.srt`) });
    } else if (s.isDirectory()) {
      const files = await readdir(input);
      for (const f of files.sort()) {
        if (!VIDEO_EXTS.has(extname(f).toLowerCase())) continue;
        const name = basename(f, extname(f));
        const outDir = OUTPUT_DIR || input;
        jobs.push({ name, source: join(input, f), isUrl: false, outputPath: join(outDir, `${name}.srt`) });
      }
    }
  }
  return jobs;
}

async function uploadFile(filePath: string): Promise<string> {
  const data = await readFile(filePath);
  const res = await fetch(`${BASE}/upload`, {
    method: "POST",
    headers: { authorization: API_KEY!, "content-type": "application/octet-stream" },
    body: data,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status} ${await res.text()}`);
  const json = await res.json() as { upload_url: string };
  return json.upload_url;
}

async function requestTranscript(audioUrl: string): Promise<string> {
  const res = await fetch(`${BASE}/transcript`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ audio_url: audioUrl }),
  });
  if (!res.ok) throw new Error(`Transcript request failed: ${res.status} ${await res.text()}`);
  const json = await res.json() as { id: string };
  return json.id;
}

async function pollTranscript(id: string): Promise<any> {
  while (true) {
    const res = await fetch(`${BASE}/transcript/${id}`, { headers: HEADERS });
    const json = await res.json() as { status: string; error?: string };
    if (json.status === "completed") return json;
    if (json.status === "error") throw new Error(`Transcription failed: ${json.error}`);
    await new Promise(r => setTimeout(r, 3000));
  }
}

async function getSrt(id: string): Promise<string> {
  const res = await fetch(`${BASE}/transcript/${id}/srt`, { headers: HEADERS });
  if (!res.ok) throw new Error(`SRT fetch failed: ${res.status}`);
  return res.text();
}

async function processJob(job: Job, index: number, total: number): Promise<Result> {
  const tag = `[${index + 1}/${total}]`;
  try {
    console.log(`${tag} Processing: ${job.name}`);
    const start = Date.now();

    let audioUrl: string;
    if (job.isUrl) {
      audioUrl = job.source;
    } else {
      console.log(`${tag}   Uploading...`);
      audioUrl = await uploadFile(job.source);
    }

    console.log(`${tag}   Transcribing...`);
    const transcriptId = await requestTranscript(audioUrl);
    const transcript = await pollTranscript(transcriptId);

    console.log(`${tag}   Fetching SRT...`);
    const srt = await getSrt(transcriptId);

    if (OUTPUT_DIR) await mkdir(OUTPUT_DIR, { recursive: true });
    await writeFile(job.outputPath, srt, "utf-8");

    const duration = (Date.now() - start) / 1000;
    const audioDur = transcript.audio_duration ? `${Math.round(transcript.audio_duration / 60)}min` : "?";
    console.log(`${tag}   ✓ Done (${audioDur} audio, ${duration.toFixed(0)}s processing) → ${job.outputPath}`);

    return { name: job.name, status: "success", srtPath: job.outputPath, duration: transcript.audio_duration };
  } catch (err: any) {
    console.error(`${tag}   ✗ FAILED: ${err.message}`);
    return { name: job.name, status: "error", error: err.message };
  }
}

async function runWithConcurrency(jobs: Job[], concurrency: number): Promise<Result[]> {
  const results: Result[] = [];
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < jobs.length) {
      const i = nextIndex++;
      results[i] = await processJob(jobs[i], i, jobs.length);
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, jobs.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

async function main() {
  console.log("VURT Subtitle Generator\n");

  const jobs = await collectJobs();
  if (jobs.length === 0) {
    console.log("No video/audio files found.");
    process.exit(0);
  }

  console.log(`Found ${jobs.length} file(s), processing with concurrency=${CONCURRENCY}\n`);

  const startTime = Date.now();
  const results = await runWithConcurrency(jobs, CONCURRENCY);
  const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);

  const succeeded = results.filter(r => r.status === "success");
  const failed = results.filter(r => r.status === "error");
  const totalAudioMin = succeeded.reduce((sum, r) => sum + (r.duration || 0), 0) / 60;
  const estimatedCost = totalAudioMin * 0.0025;

  console.log(`\n${"=".repeat(60)}`);
  console.log(`SUMMARY`);
  console.log(`${"=".repeat(60)}`);
  console.log(`Total files:    ${jobs.length}`);
  console.log(`Succeeded:      ${succeeded.length}`);
  console.log(`Failed:         ${failed.length}`);
  console.log(`Audio processed: ${totalAudioMin.toFixed(1)} minutes`);
  console.log(`Est. cost:      $${estimatedCost.toFixed(2)}`);
  console.log(`Wall time:      ${elapsed} minutes`);

  if (failed.length > 0) {
    console.log(`\nFailed files:`);
    for (const f of failed) console.log(`  - ${f.name}: ${f.error}`);
  }

  const reportPath = join(OUTPUT_DIR || resolve(values.input!, ".."), "subtitle-report.json");
  await writeFile(reportPath, JSON.stringify({ timestamp: new Date().toISOString(), results, summary: { total: jobs.length, succeeded: succeeded.length, failed: failed.length, audioMinutes: totalAudioMin, estimatedCost } }, null, 2));
  console.log(`\nReport saved: ${reportPath}`);
}

main().catch(err => { console.error(err); process.exit(1); });
