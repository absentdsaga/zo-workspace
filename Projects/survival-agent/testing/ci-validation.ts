#!/usr/bin/env bun

/**
 * CI/CD VALIDATION FRAMEWORK
 *
 * Purpose: Automated checks that MUST pass before any deployment
 * Run this automatically before every code change is committed
 */

interface ValidationResult {
  category: string;
  checks: Array<{
    name: string;
    passed: boolean;
    error?: string;
    severity: 'critical' | 'warning' | 'info';
  }>;
}

class CIValidator {
  private results: ValidationResult[] = [];

  // Colors
  private green(text: string) { return `\x1b[32m${text}\x1b[0m`; }
  private red(text: string) { return `\x1b[31m${text}\x1b[0m`; }
  private yellow(text: string) { return `\x1b[33m${text}\x1b[0m`; }
  private blue(text: string) { return `\x1b[36m${text}\x1b[0m`; }

  // ==================== CODE QUALITY CHECKS ====================

  async validateCodeQuality() {
    const checks = [];

    // Check 1: No commented-out code blocks
    checks.push(await this.checkNoCommentedCode());

    // Check 2: No TODO/FIXME in production code
    checks.push(await this.checkNoTODOs());

    // Check 3: No console.log in production (except bot logging)
    checks.push(await this.checkNoDebugLogs());

    // Check 4: All functions have error handling
    checks.push(await this.checkErrorHandling());

    this.results.push({
      category: 'Code Quality',
      checks
    });
  }

  private async checkNoCommentedCode() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();
    const validatorCode = await Bun.file('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts').text();

    // Look for large commented-out blocks (3+ consecutive comment lines)
    const commentBlockPattern = /\/\/.*\n\/\/.*\n\/\/.*/g;
    const botBlocks = botCode.match(commentBlockPattern) || [];
    const validatorBlocks = validatorCode.match(commentBlockPattern) || [];

    const totalBlocks = botBlocks.length + validatorBlocks.length;

    return {
      name: 'No large commented-out code blocks',
      passed: totalBlocks === 0,
      error: totalBlocks > 0 ? `Found ${totalBlocks} commented code blocks - clean up dead code` : undefined,
      severity: 'warning' as const
    };
  }

  private async checkNoTODOs() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();
    const validatorCode = await Bun.file('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts').text();

    const todoPattern = /\/\/\s*(TODO|FIXME|HACK|XXX)/gi;
    const botTodos = botCode.match(todoPattern) || [];
    const validatorTodos = validatorCode.match(todoPattern) || [];

    const totalTodos = botTodos.length + validatorTodos.length;

    return {
      name: 'No unresolved TODOs/FIXMEs',
      passed: totalTodos === 0,
      error: totalTodos > 0 ? `Found ${totalTodos} TODO/FIXME comments - resolve before deploy` : undefined,
      severity: 'warning' as const
    };
  }

  private async checkNoDebugLogs() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    // Allow intentional logging, flag suspicious console.log with variables
    const debugPattern = /console\.log\(['"].*\$\{/g;
    const debugLogs = botCode.match(debugPattern) || [];

    return {
      name: 'No debug console.logs',
      passed: debugLogs.length === 0,
      error: debugLogs.length > 0 ? `Found ${debugLogs.length} potential debug logs` : undefined,
      severity: 'info' as const
    };
  }

  private async checkErrorHandling() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();
    const validatorCode = await Bun.file('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts').text();

    // Check for try-catch blocks around critical operations
    const fetchCalls = (botCode.match(/fetch\(/g) || []).length;
    const tryCatchBlocks = (botCode.match(/try\s*\{/g) || []).length;

    const hasEnoughErrorHandling = tryCatchBlocks >= fetchCalls * 0.8; // 80% coverage

    return {
      name: 'Adequate error handling',
      passed: hasEnoughErrorHandling,
      error: !hasEnoughErrorHandling ? `Only ${tryCatchBlocks} try-catch for ${fetchCalls} fetch calls` : undefined,
      severity: 'critical' as const
    };
  }

  // ==================== CONFIGURATION CHECKS ====================

  async validateConfiguration() {
    const checks = [];

    // Check 1: Position limits are safe
    checks.push(await this.checkPositionLimits());

    // Check 2: API intervals are within rate limits
    checks.push(await this.checkAPIRateLimits());

    // Check 3: Confidence threshold is reasonable
    checks.push(await this.checkConfidenceThreshold());

    // Check 4: Stop loss / take profit are set
    checks.push(await this.checkRiskParameters());

    this.results.push({
      category: 'Configuration',
      checks
    });
  }

  private async checkPositionLimits() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    const maxPosMatch = botCode.match(/MAX_CONCURRENT_POSITIONS\s*=\s*(\d+)/);
    const maxPositions = maxPosMatch ? parseInt(maxPosMatch[1]) : 0;

    const isSafe = maxPositions > 0 && maxPositions <= 10;

    return {
      name: 'Position limits are safe',
      passed: isSafe,
      error: !isSafe ? `MAX_CONCURRENT_POSITIONS=${maxPositions} (expected 1-10)` : undefined,
      severity: 'critical' as const
    };
  }

  private async checkAPIRateLimits() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    // Extract check intervals
    const criticalInterval = botCode.match(/checkInterval = 2000/) ? 2000 : 0;
    const safeInterval = botCode.match(/checkInterval = (\d+)000.*Safe/);
    const safeMs = safeInterval ? parseInt(safeInterval[1]) * 1000 : 0;

    // Calculate worst-case API load
    const maxPosMatch = botCode.match(/MAX_CONCURRENT_POSITIONS\s*=\s*(\d+)/);
    const maxPositions = maxPosMatch ? parseInt(maxPosMatch[1]) : 7;

    // Worst case: all positions in critical state (2s checks)
    const maxCallsPerMin = (60000 / criticalInterval) * maxPositions;

    const isWithinLimits = maxCallsPerMin <= 60; // Conservative limit

    return {
      name: 'API rate limits respected',
      passed: isWithinLimits,
      error: !isWithinLimits ? `Max ${maxCallsPerMin} calls/min (limit: 60)` : undefined,
      severity: 'critical' as const
    };
  }

  private async checkConfidenceThreshold() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    const thresholdMatch = botCode.match(/MIN_SMART_MONEY_CONFIDENCE\s*=\s*(\d+)/);
    const threshold = thresholdMatch ? parseInt(thresholdMatch[1]) : 0;

    const isReasonable = threshold >= 40 && threshold <= 80;

    return {
      name: 'Confidence threshold is reasonable',
      passed: isReasonable,
      error: !isReasonable ? `Threshold ${threshold} (expected 40-80)` : undefined,
      severity: 'warning' as const
    };
  }

  private async checkRiskParameters() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    const hasStopLoss = botCode.includes('STOP_LOSS') || botCode.includes('stopLoss');
    const hasTakeProfit = botCode.includes('TAKE_PROFIT') || botCode.includes('takeProfit');

    const passed = hasStopLoss && hasTakeProfit;

    return {
      name: 'Risk parameters configured',
      passed,
      error: !passed ? 'Missing stop loss or take profit configuration' : undefined,
      severity: 'critical' as const
    };
  }

  // ==================== STATE INTEGRITY CHECKS ====================

  async validateStateIntegrity() {
    const checks = [];

    // Check 1: Data file exists and is valid JSON
    checks.push(await this.checkDataFileIntegrity());

    // Check 2: Balance is positive
    checks.push(await this.checkPositiveBalance());

    // Check 3: No orphaned positions
    checks.push(await this.checkNoOrphanedPositions());

    // Check 4: Timestamps are recent
    checks.push(await this.checkRecentTimestamps());

    this.results.push({
      category: 'State Integrity',
      checks
    });
  }

  private async checkDataFileIntegrity() {
    try {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const hasBalance = typeof data.balance === 'number';
      const hasTrades = Array.isArray(data.trades);

      const passed = hasBalance && hasTrades;

      return {
        name: 'Data file integrity',
        passed,
        error: !passed ? 'Data file is corrupted or missing required fields' : undefined,
        severity: 'critical' as const
      };
    } catch (error) {
      return {
        name: 'Data file integrity',
        passed: false,
        error: 'Cannot read or parse data file',
        severity: 'critical' as const
      };
    }
  }

  private async checkPositiveBalance() {
    const data = await Bun.file('/tmp/paper-trades-master.json').json();

    const passed = data.balance > 0;

    return {
      name: 'Positive balance',
      passed,
      error: !passed ? `Balance is ${data.balance.toFixed(4)} SOL` : undefined,
      severity: 'critical' as const
    };
  }

  private async checkNoOrphanedPositions() {
    const data = await Bun.file('/tmp/paper-trades-master.json').json();

    const openPositions = data.trades.filter((t: any) => t.status === 'open');

    // Check that all open positions have required fields
    const orphaned = openPositions.filter((t: any) =>
      !t.tokenAddress || !t.tokenSymbol || !t.entryPrice || !t.timestamp
    );

    const passed = orphaned.length === 0;

    return {
      name: 'No orphaned positions',
      passed,
      error: !passed ? `Found ${orphaned.length} positions with missing data` : undefined,
      severity: 'critical' as const
    };
  }

  private async checkRecentTimestamps() {
    const data = await Bun.file('/tmp/paper-trades-master.json').json();

    const now = Date.now();
    const oneWeekAgo = now - (7 * 24 * 60 * 60 * 1000);

    const recentTrades = data.trades.filter((t: any) => t.timestamp > oneWeekAgo);

    const passed = recentTrades.length > 0 || data.trades.length === 0;

    return {
      name: 'Recent activity detected',
      passed,
      error: !passed ? 'No trades in the last 7 days - bot may be stuck' : undefined,
      severity: 'warning' as const
    };
  }

  // ==================== REGRESSION CHECKS ====================

  async validateNoRegression() {
    const checks = [];

    // Check 1: No rate limit false positives
    checks.push(await this.checkNoRateLimitRugs());

    // Check 2: Dynamic intervals implemented
    checks.push(await this.checkDynamicIntervals());

    // Check 3: Trailing stop implemented
    checks.push(await this.checkTrailingStop());

    this.results.push({
      category: 'Regression Prevention',
      checks
    });
  }

  private async checkNoRateLimitRugs() {
    const validatorCode = await Bun.file('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts').text();

    // Must have rate limit detection logic
    const hasRateLimitCheck = validatorCode.includes('429') && validatorCode.includes('liquidityInsufficient');

    return {
      name: 'Rate limit detection implemented',
      passed: hasRateLimitCheck,
      error: !hasRateLimitCheck ? 'Missing 429 rate limit detection - will classify as rugs!' : undefined,
      severity: 'critical' as const
    };
  }

  private async checkDynamicIntervals() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    // Must have different intervals based on P&L
    const hasDynamicIntervals =
      botCode.includes('checkInterval') &&
      botCode.includes('pnlPercent') &&
      botCode.match(/checkInterval\s*=\s*\d+/g)?.length! >= 3;

    return {
      name: 'Dynamic check intervals',
      passed: hasDynamicIntervals,
      error: !hasDynamicIntervals ? 'Missing dynamic interval logic' : undefined,
      severity: 'critical' as const
    };
  }

  private async checkTrailingStop() {
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();

    const hasTrailingStop =
      botCode.includes('peakPrice') &&
      botCode.includes('tp1Hit') &&
      botCode.includes('dropFromPeak');

    return {
      name: 'Trailing stop implemented',
      passed: hasTrailingStop,
      error: !hasTrailingStop ? 'Missing trailing stop logic' : undefined,
      severity: 'warning' as const
    };
  }

  // ==================== RUN ALL VALIDATIONS ====================

  async runAll() {
    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('🔍 CI/CD VALIDATION FRAMEWORK'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    const startTime = Date.now();

    await this.validateCodeQuality();
    await this.validateConfiguration();
    await this.validateStateIntegrity();
    await this.validateNoRegression();

    const duration = Date.now() - startTime;
    this.printResults(duration);

    // Determine if safe to deploy
    const criticalFailures = this.results.flatMap(r =>
      r.checks.filter(c => !c.passed && c.severity === 'critical')
    );

    if (criticalFailures.length > 0) {
      console.log(this.red('\n❌ CRITICAL FAILURES - DEPLOYMENT BLOCKED\n'));
      process.exit(1);
    } else {
      console.log(this.green('\n✅ ALL CRITICAL CHECKS PASSED - SAFE TO DEPLOY\n'));
    }
  }

  private printResults(totalDuration: number) {
    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('📊 VALIDATION RESULTS'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    for (const result of this.results) {
      console.log(this.blue(`\n${result.category}:\n`));

      for (const check of result.checks) {
        let status: string;
        if (check.passed) {
          status = this.green('✓ PASS');
        } else if (check.severity === 'critical') {
          status = this.red('✗ FAIL');
        } else if (check.severity === 'warning') {
          status = this.yellow('⚠ WARN');
        } else {
          status = this.yellow('ℹ INFO');
        }

        console.log(`  ${status} ${check.name}`);

        if (check.error) {
          console.log(this.red(`       ↳ ${check.error}`));
        }
      }
    }

    console.log(this.blue('\n═══════════════════════════════════════════════════════'));

    const allChecks = this.results.flatMap(r => r.checks);
    const passed = allChecks.filter(c => c.passed).length;
    const failed = allChecks.filter(c => !c.passed).length;
    const critical = allChecks.filter(c => !c.passed && c.severity === 'critical').length;

    console.log(`Total: ${allChecks.length} | ${this.green(`Passed: ${passed}`)} | ${failed > 0 ? this.red(`Failed: ${failed}`) : 'Failed: 0'}`);
    if (critical > 0) {
      console.log(this.red(`CRITICAL FAILURES: ${critical}`));
    }
    console.log(`Duration: ${totalDuration}ms`);
  }
}

// Run validation
const validator = new CIValidator();
await validator.runAll();
