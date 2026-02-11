#!/usr/bin/env bun
/**
 * TEST UTILITIES
 *
 * Helper functions for:
 * - Screenshot comparison
 * - HTML report generation
 * - Test result analysis
 */

import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

/**
 * Compare two screenshots and return difference percentage
 */
export async function compareScreenshots(image1Path, image2Path, outputPath = null) {
  try {
    const img1 = PNG.sync.read(readFileSync(image1Path));
    const img2 = PNG.sync.read(readFileSync(image2Path));

    const { width, height } = img1;
    const diff = new PNG({ width, height });

    const numDiffPixels = pixelmatch(
      img1.data,
      img2.data,
      diff.data,
      width,
      height,
      { threshold: 0.1 }
    );

    const totalPixels = width * height;
    const diffPercentage = (numDiffPixels / totalPixels) * 100;

    // Save diff image if output path provided
    if (outputPath) {
      writeFileSync(outputPath, PNG.sync.write(diff));
    }

    return {
      numDiffPixels,
      totalPixels,
      diffPercentage: diffPercentage.toFixed(2),
      similar: diffPercentage < 5 // Less than 5% difference = similar
    };
  } catch (error) {
    console.error('Screenshot comparison error:', error.message);
    return null;
  }
}

/**
 * Generate HTML test report
 */
export function generateHTMLReport(testResults, outputPath) {
  const passRate = ((testResults.passed / testResults.totalTests) * 100).toFixed(1);
  const status = testResults.failed === 0 ? 'PASSED' : 'FAILED';
  const statusColor = testResults.failed === 0 ? '#4ade80' : '#f87171';

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - Spatial Worlds</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 40px 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        h1 {
            font-size: 36px;
            margin-bottom: 10px;
            color: #fff;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 14px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: #1e293b;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #334155;
        }

        .stat-value {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .stat-label {
            color: #94a3b8;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
        }

        .test-list {
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 40px;
        }

        .test-item {
            padding: 20px 24px;
            border-bottom: 1px solid #334155;
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }

        .test-item:last-child {
            border-bottom: none;
        }

        .test-icon {
            font-size: 24px;
            flex-shrink: 0;
        }

        .test-content {
            flex: 1;
        }

        .test-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .test-message {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .test-details {
            background: #0f172a;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin-top: 8px;
            overflow-x: auto;
        }

        .screenshots {
            background: #1e293b;
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 40px;
        }

        .screenshots h2 {
            margin-bottom: 20px;
        }

        .screenshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .screenshot-item {
            background: #0f172a;
            border-radius: 8px;
            overflow: hidden;
        }

        .screenshot-item img {
            width: 100%;
            height: auto;
            display: block;
        }

        .screenshot-label {
            padding: 12px;
            font-size: 14px;
            color: #94a3b8;
        }

        .errors {
            background: #1e293b;
            padding: 24px;
            border-radius: 8px;
        }

        .error-item {
            background: #0f172a;
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 12px;
            border-left: 4px solid #ef4444;
        }

        .error-type {
            font-weight: bold;
            color: #ef4444;
            margin-bottom: 4px;
        }

        .error-message {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #cbd5e1;
        }

        .timestamp {
            color: #64748b;
            font-size: 11px;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 Spatial Worlds - Test Report</h1>
            <div class="subtitle">Generated on ${new Date(testResults.startTime).toLocaleString()}</div>
        </header>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-value" style="color: ${statusColor};">${status}</div>
                <div class="stat-label">Test Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #4ade80;">${testResults.passed}</div>
                <div class="stat-label">Tests Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #f87171;">${testResults.failed}</div>
                <div class="stat-label">Tests Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #60a5fa;">${passRate}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>

        <div class="test-list">
            ${testResults.tests.map(test => `
                <div class="test-item">
                    <div class="test-icon">${test.passed ? '✅' : '❌'}</div>
                    <div class="test-content">
                        <div class="test-name">${test.name}</div>
                        <div class="test-message">${test.message}</div>
                        ${Object.keys(test).length > 4 ? `
                            <details>
                                <summary style="cursor: pointer; color: #60a5fa; margin-top: 8px;">View Details</summary>
                                <div class="test-details">
                                    ${JSON.stringify(test, null, 2)}
                                </div>
                            </details>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>

        ${testResults.screenshots.length > 0 ? `
            <div class="screenshots">
                <h2>📸 Screenshots (${testResults.screenshots.length})</h2>
                <div class="screenshot-grid">
                    ${testResults.screenshots.map(screenshot => `
                        <div class="screenshot-item">
                            <img src="../screenshots/${screenshot.filename}" alt="${screenshot.label}">
                            <div class="screenshot-label">
                                ${screenshot.player} - ${screenshot.label}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}

        ${(testResults.consoleErrors.player1.length > 0 || testResults.consoleErrors.player2.length > 0) ? `
            <div class="errors">
                <h2>🐛 Console Errors</h2>
                ${testResults.consoleErrors.player1.length > 0 ? `
                    <h3 style="margin: 20px 0 12px 0; color: #94a3b8;">Player 1 (${testResults.consoleErrors.player1.length})</h3>
                    ${testResults.consoleErrors.player1.map(error => `
                        <div class="error-item">
                            <div class="error-type">${error.type.toUpperCase()}</div>
                            <div class="error-message">${error.message}</div>
                            <div class="timestamp">${new Date(error.timestamp).toLocaleTimeString()}</div>
                        </div>
                    `).join('')}
                ` : ''}
                ${testResults.consoleErrors.player2.length > 0 ? `
                    <h3 style="margin: 20px 0 12px 0; color: #94a3b8;">Player 2 (${testResults.consoleErrors.player2.length})</h3>
                    ${testResults.consoleErrors.player2.map(error => `
                        <div class="error-item">
                            <div class="error-type">${error.type.toUpperCase()}</div>
                            <div class="error-message">${error.message}</div>
                            <div class="timestamp">${new Date(error.timestamp).toLocaleTimeString()}</div>
                        </div>
                    `).join('')}
                ` : ''}
            </div>
        ` : ''}
    </div>
</body>
</html>
  `.trim();

  writeFileSync(outputPath, html);
  return outputPath;
}

/**
 * Analyze test results and provide insights
 */
export function analyzeTestResults(testResults) {
  const insights = [];

  // Check pass rate
  const passRate = (testResults.passed / testResults.totalTests) * 100;
  if (passRate === 100) {
    insights.push({
      type: 'success',
      message: 'All tests passed! The multiplayer sync is working perfectly.'
    });
  } else if (passRate >= 80) {
    insights.push({
      type: 'warning',
      message: 'Most tests passed, but some issues detected. Review failed tests.'
    });
  } else {
    insights.push({
      type: 'error',
      message: 'Multiple test failures detected. Critical issues need attention.'
    });
  }

  // Check for specific failures
  const failedTests = testResults.tests.filter(t => !t.passed);

  if (failedTests.some(t => t.name === 'Multiplayer Connection')) {
    insights.push({
      type: 'critical',
      message: 'WebSocket connection failed. Check server status.'
    });
  }

  if (failedTests.some(t => t.name === 'Position Sync')) {
    insights.push({
      type: 'error',
      message: 'Position synchronization is broken. Player positions are not syncing correctly.'
    });
  }

  if (failedTests.some(t => t.name === 'Sync Stability')) {
    insights.push({
      type: 'warning',
      message: 'Position drift detected. Positions diverge over time.'
    });
  }

  // Check console errors
  const totalErrors = testResults.consoleErrors.player1.length + testResults.consoleErrors.player2.length;
  if (totalErrors > 0) {
    insights.push({
      type: 'warning',
      message: `${totalErrors} console errors detected. Check browser console logs.`
    });
  }

  return insights;
}

/**
 * Format test duration
 */
export function formatDuration(startTime, endTime) {
  const duration = new Date(endTime) - new Date(startTime);
  const seconds = Math.floor(duration / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  }
  return `${seconds}s`;
}
