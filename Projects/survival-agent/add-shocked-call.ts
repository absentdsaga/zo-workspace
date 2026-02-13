#!/usr/bin/env bun
/**
 * Add Shocked Group Call to Watchlist
 *
 * Usage:
 *   bun add-shocked-call.ts <address> [symbol] [--high|--medium|--low] [--notes "..."]
 *
 * Examples:
 *   bun add-shocked-call.ts HiNkp9CdKqTgPtB6WnnrrUAu9YwQqnrvT6Ceuxoypump Accelerando --high --notes "POW tweeted CA"
 *   bun add-shocked-call.ts 84hqMeGHxqegpvf4kGaRp38iVd145DSoEBwnmBTtpump MooNutPeng --high
 */

import { ShockedAlphaScanner } from './strategies/shocked-alpha-scanner';

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: bun add-shocked-call.ts <address> [symbol] [--high|--medium|--low] [--notes "..."]');
    console.log('');
    console.log('Examples:');
    console.log('  bun add-shocked-call.ts HiNkp9Cd... Accelerando --high --notes "POW tweeted"');
    console.log('  bun add-shocked-call.ts 84hqMeGH... MooNutPeng --medium');
    console.log('  bun add-shocked-call.ts 0xa9FEE... --low');
    process.exit(1);
  }

  const address = args[0];
  let symbol: string | undefined;
  let priority: 'high' | 'medium' | 'low' = 'medium';
  let notes: string | undefined;

  // Parse arguments
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--high') priority = 'high';
    else if (arg === '--medium') priority = 'medium';
    else if (arg === '--low') priority = 'low';
    else if (arg === '--notes' && args[i + 1]) {
      notes = args[++i];
    } else if (!symbol && !arg.startsWith('--')) {
      symbol = arg;
    }
  }

  const scanner = new ShockedAlphaScanner();
  await scanner.initialize();

  await scanner.addCall(address, {
    symbol,
    priority,
    notes,
    source: 'shocked-group'
  });

  console.log('');
  console.log('Current watchlist:');
  const watchlist = scanner.getWatchlist();
  console.log(`Total: ${watchlist.length} tokens\n`);

  for (const call of watchlist.slice(0, 10)) {
    const age = Math.floor((Date.now() - call.addedAt) / (1000 * 60 * 60));
    console.log(`  ${call.priority === 'high' ? '🔥' : call.priority === 'medium' ? '📌' : '👀'} ${call.symbol || call.address.slice(0, 8)} - ${age}h ago`);
    if (call.notes) console.log(`     Note: ${call.notes}`);
  }

  console.log('');
  console.log('✅ The paper trader will now prioritize this token!');
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
