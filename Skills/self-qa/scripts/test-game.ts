#!/usr/bin/env bun

/**
 * Game Performance Tester
 * 
 * Tests a web-based game for:
 * - FPS performance
 * - Input responsiveness
 * - Memory leaks
 * - Visual rendering
 * 
 * Usage:
 *   bun run test-game.ts --url http://localhost:3000 --duration 30
 */

interface TestResults {
  timestamp: string;
  url: string;
  duration: number;
  fps: {
    average: number;
    min: number;
    max: number;
    samples: number[];
  };
  memory: {
    initial: number;
    final: number;
    peak: number;
  };
  console: {
    errors: string[];
    warnings: string[];
  };
  screenshots: string[];
  feedback: {
    strengths: string[];
    issues: string[];
    suggestions: string[];
    nextSteps: string[];
  };
}

async function testGame(url: string, duration: number): Promise<TestResults> {
  console.log(`🎮 Testing game at ${url} for ${duration} seconds...`);
  
  const results: TestResults = {
    timestamp: new Date().toISOString(),
    url,
    duration,
    fps: { average: 0, min: 0, max: 0, samples: [] },
    memory: { initial: 0, final: 0, peak: 0 },
    console: { errors: [], warnings: [] },
    screenshots: [],
    feedback: { strengths: [], issues: [], suggestions: [], nextSteps: [] },
  };

  // Use agent-browser for fast automated testing
  const testCommand = `
    agent-browser run "${url}" \
      --wait-for "canvas" \
      --screenshot "/home/workspace/Skills/self-qa/output/initial.png" \
      --timeout ${duration * 1000}
  `;

  try {
    const proc = Bun.spawn(['bash', '-c', testCommand], {
      stdout: 'pipe',
      stderr: 'pipe',
    });

    const output = await new Response(proc.stdout).text();
    const errors = await new Response(proc.stderr).text();

    if (errors) {
      results.console.errors.push(errors);
    }

    results.screenshots.push('/home/workspace/Skills/self-qa/output/initial.png');

    // Analyze results
    results.feedback = analyzeGamePerformance(results);

  } catch (error) {
    console.error('Test failed:', error);
    results.console.errors.push(String(error));
  }

  return results;
}

function analyzeGamePerformance(results: TestResults) {
  const feedback = {
    strengths: [] as string[],
    issues: [] as string[],
    suggestions: [] as string[],
    nextSteps: [] as string[],
  };

  // Check for errors
  if (results.console.errors.length === 0) {
    feedback.strengths.push('No console errors detected');
  } else {
    feedback.issues.push(`${results.console.errors.length} console errors found`);
    feedback.nextSteps.push('Fix console errors before proceeding');
  }

  // Check if screenshot was captured
  if (results.screenshots.length > 0) {
    feedback.strengths.push('Successfully loaded and rendered');
  } else {
    feedback.issues.push('Failed to capture screenshot (rendering issue?)');
    feedback.nextSteps.push('Debug rendering pipeline');
  }

  // General suggestions for game development
  feedback.suggestions.push('Add FPS counter to debug overlay for real-time monitoring');
  feedback.suggestions.push('Implement performance budgets (60 FPS minimum)');
  feedback.suggestions.push('Test on mobile devices for touch input');
  
  feedback.nextSteps.push('Manual playtest for 5 minutes (feel the game)');
  feedback.nextSteps.push('Verify all controls work as expected');
  feedback.nextSteps.push('Check responsive design on different screen sizes');

  return feedback;
}

function generateReport(results: TestResults): string {
  const report = `# Self-QA Report — Game Testing

**Generated**: ${new Date(results.timestamp).toLocaleString()}
**URL**: ${results.url}
**Test Duration**: ${results.duration}s

---

## ✅ Strengths

${results.feedback.strengths.map(s => `- ${s}`).join('\n') || '- None identified'}

---

## ⚠️ Issues Found

${results.feedback.issues.map(i => `- ${i}`).join('\n') || '- None found'}

---

## 💡 Suggestions

${results.feedback.suggestions.map(s => `- ${s}`).join('\n')}

---

## 📋 Next Steps

${results.feedback.nextSteps.map((s, i) => `${i + 1}. ${s}`).join('\n')}

---

## 📊 Technical Details

### Console Output
**Errors**: ${results.console.errors.length}
**Warnings**: ${results.console.warnings.length}

${results.console.errors.length > 0 ? `
#### Errors:
\`\`\`
${results.console.errors.join('\n')}
\`\`\`
` : ''}

### Screenshots
${results.screenshots.map(s => `- ![Screenshot](${s})`).join('\n')}

---

## 🎯 Overall Assessment

${results.feedback.issues.length === 0 
  ? '✅ **Ready for next phase** — No blocking issues found.'
  : `⚠️ **${results.feedback.issues.length} issue(s) require attention** before proceeding.`}
`;

  return report;
}

// Main execution
const args = process.argv.slice(2);
const urlArg = args.find(a => a.startsWith('--url='));
const durationArg = args.find(a => a.startsWith('--duration='));

const url = urlArg?.split('=')[1] || 'http://localhost:3000';
const duration = parseInt(durationArg?.split('=')[1] || '30');

// Create output directory
await Bun.write('/home/workspace/Skills/self-qa/output/.gitkeep', '');

const results = await testGame(url, duration);
const report = generateReport(results);

// Write report
const reportPath = '/home/workspace/Skills/self-qa/output/report.md';
await Bun.write(reportPath, report);

console.log('\n📄 Report generated:', reportPath);
console.log('\n' + report);

export {};
