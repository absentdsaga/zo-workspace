#!/usr/bin/env bun
/**
 * MAIN TEST RUNNER
 *
 * Orchestrates test execution and report generation
 *
 * Usage: bun run scripts/run-tests.js
 */

import { spawn } from 'child_process';
import { existsSync, readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { generateHTMLReport, analyzeTestResults, formatDuration } from './test-utils.js';

const outputDir = join(process.cwd(), 'test-results');
const reportDir = join(outputDir, 'reports');

console.log('\n🚀 AUTOMATED QA TEST RUNNER\n');
console.log('================================================');
console.log('Starting comprehensive multiplayer sync tests...');
console.log('================================================\n');

/**
 * Check if spatial-worlds server is running
 */
async function checkServerRunning() {
  try {
    const response = await fetch('http://localhost:3000', { signal: AbortSignal.timeout(2000) });
    return response.ok || response.status === 404; // Server responding
  } catch (error) {
    return false;
  }
}

/**
 * Run the test script
 */
function runTestScript() {
  return new Promise((resolve, reject) => {
    const testScript = join(process.cwd(), 'scripts', 'test-multiplayer-sync.js');

    const child = spawn('bun', ['run', testScript], {
      stdio: 'inherit',
      cwd: process.cwd()
    });

    child.on('close', (code) => {
      if (code !== null) {
        resolve(code);
      } else {
        reject(new Error('Test process terminated unexpectedly'));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Get the most recent test report
 */
function getLatestReport() {
  if (!existsSync(reportDir)) {
    return null;
  }

  const files = readdirSync(reportDir)
    .filter(f => f.startsWith('test-report-') && f.endsWith('.json'))
    .sort()
    .reverse();

  if (files.length === 0) {
    return null;
  }

  const latestFile = join(reportDir, files[0]);
  const data = JSON.parse(readFileSync(latestFile, 'utf-8'));

  return { path: latestFile, data };
}

/**
 * Main execution
 */
async function main() {
  try {
    // Check if server is running
    console.log('🔍 Checking if spatial-worlds server is running...\n');

    const serverRunning = await checkServerRunning();

    if (!serverRunning) {
      console.error('❌ ERROR: spatial-worlds server is not running!');
      console.error('\nPlease start the server first:');
      console.error('  cd Skills/spatial-worlds');
      console.error('  bun run dev\n');
      process.exit(1);
    }

    console.log('✅ Server is running!\n');

    // Run tests
    console.log('🎬 Starting test execution...\n');

    const exitCode = await runTestScript();

    console.log('\n📊 Generating HTML report...\n');

    // Get the latest test report
    const report = getLatestReport();

    if (!report) {
      console.error('❌ Could not find test results');
      process.exit(1);
    }

    // Generate HTML report
    const htmlPath = join(reportDir, `test-report-${Date.now()}.html`);
    generateHTMLReport(report.data, htmlPath);

    console.log(`✅ HTML report generated: ${htmlPath}\n`);

    // Analyze results
    console.log('🔍 TEST ANALYSIS\n');
    console.log('================================================');

    const insights = analyzeTestResults(report.data);

    insights.forEach(insight => {
      const icon = {
        success: '✅',
        warning: '⚠️',
        error: '❌',
        critical: '🚨'
      }[insight.type];

      console.log(`${icon} ${insight.message}`);
    });

    console.log('================================================\n');

    // Summary
    const duration = formatDuration(report.data.startTime, report.data.endTime);

    console.log('📈 FINAL SUMMARY\n');
    console.log('================================================');
    console.log(`Total Tests: ${report.data.totalTests}`);
    console.log(`Passed: ${report.data.passed} ✅`);
    console.log(`Failed: ${report.data.failed} ❌`);
    console.log(`Duration: ${duration}`);
    console.log(`Screenshots: ${report.data.screenshots.length}`);
    console.log(`Console Errors: ${report.data.consoleErrors.player1.length + report.data.consoleErrors.player2.length}`);
    console.log('\nReports:');
    console.log(`  JSON: ${report.path}`);
    console.log(`  HTML: ${htmlPath}`);
    console.log('================================================\n');

    if (report.data.failed > 0) {
      console.log('⚠️  Some tests failed. Review the report for details.\n');
      process.exit(1);
    } else {
      console.log('🎉 All tests passed! Ready for deployment.\n');
      process.exit(0);
    }

  } catch (error) {
    console.error('\n💥 Test runner failed:', error.message);
    process.exit(1);
  }
}

main();
