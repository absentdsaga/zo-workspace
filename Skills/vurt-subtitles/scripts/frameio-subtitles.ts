#!/usr/bin/env bun

/**
 * VURT Frame.io → AssemblyAI Subtitle Generator
 * Pulls video assets from Frame.io and generates SRT files via AssemblyAI
 */

import { writeFile, mkdir } from "fs/promises";
import { join, resolve } from "path";
import { parseArgs } from "util";

const FRAMEIO_BASE = "https://api.frame.io/v2";
const ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2";

const { values } = parseArgs({
  args: process.argv.slice(2),
  options: {
    project:     { type: "string",  short: "p" },
    folder:      { type: "string",  short: "f" },
    output:      { type: "string",  short: "o", default: "./srts" },
    concurrency: { type: "string",  short: "c", default: "3" },
    list:        { type: "boolean", default: false },
    limit:       { type: "string",  default: "5" },
    help:        { type: "boolean", short: "h", default: false },
  },
});

const USAGE = `
VURT Frame.io → AssemblyAI Subtitle Generator

Usage:
  bun run frameio-subtitles.ts [options]

Options:
  -p, --project     Frame.io project ID (or use --folder)
  -f, --folder      Frame.io folder/asset ID to process
  -o, --output      Output directory for SRT files (default: ./srts)
  -c, --concurrency Max parallel transcription jobs (default: 3)
  --list            List projects/assets without transcribing
  --limit           Max assets to process in test batch (default: 5)
  -h, --help        Show this help

Examples:
  # List all projects to find your project ID
  bun run frameio-subtitles.ts --list

  # Test batch: first 5 videos from a project
  bun run frameio-subtitles.ts --project <id> --limit 5

  # Full run on a folder
  bun run frameio-subtitles.ts --folder <folder_id> --output ./srts

Required env vars:
  FRAMEIO_API_KEY     — Frame.io developer token
  ASSEMBLYAI_API_KEY  — AssemblyAI API key
`;

if (values.help) { console.log(USAGE); process.exit(0); }

const FRAMEIO_KEY = process.env.FRAMEIO_API_KEY;
const ASSEMBLY_KEY = process.env.ASSEMBLYAI_API_KEY;

if (!FRAMEIO_KEY) { console.error("ERROR: FRAMEIO_API_KEY not set. Add it in Settings > Advanced"); process.exit(1); }
if (!ASSEMBLY_KEY && !values.list) { console.error("ERROR: ASSEMBLYAI_API_KEY not set. Add it in Settings > Advanced"); process.exit(1); }

const FIO_HEADERS = { "Authorization": `Bearer ${FRAMEIO_KEY}`, "Content-Type": "application/json" };
const ASM_HEADERS = { "authorization": ASSEMBLY_KEY!, "content-type": "application/json" };

// ── Frame.io helpers ──────────────────────────────────────────────────────────

async function fioGet(path: string): Promise<any> {
  const res = await fetch(`${FRAMEIO_BASE}${path}`, { headers: FIO_HEADERS });
  if (!res.ok) throw new Error(`Frame.io ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

async function getMe(): Promise<any> {
  return fioGet("/me");
}

async function getTeams(accountId: string): Promise<any[]> {
  return fioGet(`/accounts/${accountId}/teams`);
}

async function getProjects(teamId: string): Promise<any[]> {
  return fioGet(`/teams/${teamId}/projects`);
}

async function getRootAssets(projectId: string): Promise<any[]> {
  const project = await fioGet(`/projects/${projectId}`);
  return fioGet(`/assets/${project.root_asset_id}/children`);
}

async function getFolderChildren(folderId: string): Promise<any[]> {
  return fioGet(`/assets/${folderId}/children`);
}

interface VideoAsset {
  id: string;
  name: string;
  type: string;
  filesize?: number;
  duration?: number;
  original?: string;
  download_url?: string;
}

async function collectVideos(assetId: string, depth = 0): Promise<VideoAsset[]> {
  const children: any[] = await getFolderChildren(assetId);
  const videos: VideoAsset[] = [];

  for (const child of children) {
    if (child.type === "file" && child.properties?.duration) {
      // Get the download URL for this asset
      const asset = await fioGet(`/assets/${child.id}`);
      const downloadUrl = asset.original || asset.media_links?.source?.download_url;
      if (downloadUrl) {
        videos.push({
          id: child.id,
          name: child.name,
          type: child.type,
          filesize: child.filesize,
          duration: child.properties?.duration,
          download_url: downloadUrl,
        });
      }
    } else if (child.type === "folder" && depth < 3) {
      const nested = await collectVideos(child.id, depth + 1);
      videos.push(...nested);
    }
  }
  return videos;
}

// ── AssemblyAI helpers ────────────────────────────────────────────────────────

async function requestTranscript(audioUrl: string): Promise<string> {
  const res = await fetch(`${ASSEMBLYAI_BASE}/transcript`, {
    method: "POST",
    headers: ASM_HEADERS,
    body: JSON.stringify({ audio_url: audioUrl, speech_model: "best" }),
  });
  if (!res.ok) throw new Error(`AssemblyAI request failed: ${res.status} ${await res.text()}`);
  const json = await res.json() as { id: string };
  return json.id;
}

async function pollTranscript(id: string): Promise<any> {
  while (true) {
    const res = await fetch(`${ASSEMBLYAI_BASE}/transcript/${id}`, { headers: ASM_HEADERS });
    const json = await res.json() as { status: string; error?: string };
    if (json.status === "completed") return json;
    if (json.status === "error") throw new Error(`Transcription failed: ${json.error}`);
    await new Promise(r => setTimeout(r, 5000));
  }
}

async function getSrt(id: string): Promise<string> {
  const res = await fetch(`${ASSEMBLYAI_BASE}/transcript/${id}/srt`, { headers: ASM_HEADERS });
  if (!res.ok) throw new Error(`SRT fetch failed: ${res.status}`);
  return res.text();
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function listMode() {
  console.log("Fetching your Frame.io account...\n");
  const me = await getMe();
  console.log(`Account: ${me.name} (${me.email})`);
  console.log(`Account ID: ${me.account_id}\n`);

  const teams = await getTeams(me.account_id);
  for (const team of teams) {
    console.log(`Team: ${team.name} (${team.id})`);
    const projects = await getProjects(team.id);
    for (const project of projects) {
      console.log(`  Project: ${project.name}`);
      console.log(`    ID: ${project.id}`);
      console.log(`    Root Asset: ${project.root_asset_id}`);
    }
  }
}

async function processVideo(video: VideoAsset, index: number, total: number, outDir: string) {
  const tag = `[${index + 1}/${total}]`;
  const safeName = video.name.replace(/\.[^.]+$/, "").replace(/[/\\:*?"<>|]/g, "_");
  const outPath = join(outDir, `${safeName}.srt`);

  try {
    const durationMin = video.duration ? `${(video.duration / 60).toFixed(1)}min` : "?";
    console.log(`${tag} ${video.name} (${durationMin})`);
    console.log(`${tag}   Requesting transcription...`);

    const transcriptId = await requestTranscript(video.download_url!);

    console.log(`${tag}   Polling... (ID: ${transcriptId})`);
    const transcript = await pollTranscript(transcriptId);

    const srt = await getSrt(transcriptId);
    await writeFile(outPath, srt, "utf-8");

    const audioDur = transcript.audio_duration ? `${(transcript.audio_duration / 60).toFixed(1)}min` : "?";
    console.log(`${tag}   ✓ Done (${audioDur} audio) → ${outPath}`);
    return { name: video.name, status: "success" as const, outPath, duration: transcript.audio_duration };
  } catch (err: any) {
    console.error(`${tag}   ✗ FAILED: ${err.message}`);
    return { name: video.name, status: "error" as const, error: err.message };
  }
}

async function main() {
  if (values.list) {
    await listMode();
    return;
  }

  if (!values.project && !values.folder) {
    console.log("Run with --list to find your project ID, then use --project <id>\n");
    console.log(USAGE);
    process.exit(1);
  }

  const outDir = resolve(values.output!);
  await mkdir(outDir, { recursive: true });

  let rootId: string;
  if (values.folder) {
    rootId = values.folder;
  } else {
    // Get root asset ID from project
    const project = await fioGet(`/projects/${values.project}`);
    rootId = project.root_asset_id;
    console.log(`Project: ${project.name}`);
    console.log(`Root asset: ${rootId}\n`);
  }

  console.log("Collecting video assets...");
  const allVideos = await collectVideos(rootId);
  const limit = parseInt(values.limit!);
  const videos = allVideos.slice(0, limit);

  if (videos.length === 0) {
    console.log("No video assets found.");
    return;
  }

  console.log(`Found ${allVideos.length} videos, processing ${videos.length} (limit=${limit})\n`);

  const concurrency = parseInt(values.concurrency!);
  const results: any[] = new Array(videos.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < videos.length) {
      const i = nextIndex++;
      results[i] = await processVideo(videos[i], i, videos.length, outDir);
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, videos.length) }, () => worker());
  await Promise.all(workers);

  const succeeded = results.filter(r => r.status === "success");
  const failed = results.filter(r => r.status === "error");
  const totalMin = succeeded.reduce((s, r) => s + (r.duration || 0), 0) / 60;
  const cost = totalMin * 0.003;

  console.log(`\n${"=".repeat(50)}`);
  console.log(`SUMMARY`);
  console.log(`${"=".repeat(50)}`);
  console.log(`Processed:  ${videos.length} files`);
  console.log(`Succeeded:  ${succeeded.length}`);
  console.log(`Failed:     ${failed.length}`);
  console.log(`Audio:      ${totalMin.toFixed(1)} minutes`);
  console.log(`Est. cost:  $${cost.toFixed(2)}`);
  console.log(`Output:     ${outDir}`);

  if (failed.length > 0) {
    console.log(`\nFailed:`);
    for (const f of failed) console.log(`  - ${f.name}: ${f.error}`);
  }

  const reportPath = join(outDir, "subtitle-report.json");
  await writeFile(reportPath, JSON.stringify({ timestamp: new Date().toISOString(), results }, null, 2));
  console.log(`\nReport: ${reportPath}`);
}

main().catch(err => { console.error(err.message); process.exit(1); });
