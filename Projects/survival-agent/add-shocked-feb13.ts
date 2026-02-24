import { ShockedAlphaScanner } from './strategies/shocked-alpha-scanner';

const scanner = new ShockedAlphaScanner();
await scanner.initialize();

console.log('📄 Processing Shocked Discord Chat - Feb 13-14, 2026\n');

// Feb 13 tokens (original)
const feb13tokens = [
  {
    address: '331Xm7D5WRBT3W5UcDjKa57AhRZU12ctXWnJVwdDpump',
    symbol: 'BABYBOO',
    priority: 'medium' as const,
    source: 'shocked-feb13',
    notes: 'TikTok viral - 250k videos, discussed 6:38 PM'
  },
  {
    address: 'Y47Svo5kZJxdEgTvCwM2LDv8twbQHTKtfLr3CJyLFy9',
    symbol: 'FRAMEMOG',
    priority: 'low' as const,
    source: 'shocked-feb13',
    notes: 'Chart share by RickAPP, 6 days old, already ran'
  },
  {
    address: 'BVPQuES4tDnVSfycm8bASuQne7LXzRJVTFtnW1uCGN3T',
    symbol: 'NEOFORM',
    priority: 'low' as const,
    source: 'shocked-feb13',
    notes: 'Post-pump discussion, dumping -37% 24h'
  },
  {
    address: 'A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump',
    symbol: 'FWOG',
    priority: 'low' as const,
    source: 'shocked-feb13',
    notes: 'Brief mention, AI/PE context, established token'
  }
];

// Feb 14 3:14 PM tokens (NEW - verified performers)
const feb14tokens = [
  {
    address: 'Dza3Bey5tvyYiPgcGRKoXKU6rNrdoNrWNVmjqePcpump',
    symbol: 'UNSYS',
    priority: 'high' as const,
    source: 'shocked-feb14',
    notes: '2.2K% gain, 830K FDV, highest conviction "every cook does 1M+"'
  },
  {
    address: 'HYhnRdn7nridbDUUcRsd3JtmvMCyKrVDew52CWGtpump',
    symbol: 'Crabs',
    priority: 'high' as const,
    source: 'shocked-feb14',
    notes: '1.1K% gain, 422K FDV, traders saying "1 million soon"'
  },
  {
    address: '9X8VSUD8yhYbHtR3KdKeCvnb7TNfgTKMFufgpCympump',
    symbol: 'right',
    priority: 'high' as const,
    source: 'shocked-feb14',
    notes: '1.1K% gain, 740K FDV, 2M volume'
  },
  {
    address: 'Ec64vZRywN6cz9Tw3tgVMPnoAQJvFD5bqZ23oTfrpump',
    symbol: 'AGI',
    priority: 'medium' as const,
    source: 'shocked-feb14',
    notes: '188% in 1h, team-backed by Superteam Japan, hackathon entry'
  },
  {
    address: 'ANw9dNZmXxbjw7VAoWshDZmUpFd5ATdQ3GQH4wDtpump',
    symbol: 'AGI',
    priority: 'medium' as const,
    source: 'shocked-feb14',
    notes: '379% in 5 minutes, fast mover'
  }
];

const tokens = [...feb13tokens, ...feb14tokens];

for (const token of tokens) {
  await scanner.addCall(token.address, {
    symbol: token.symbol,
    priority: token.priority,
    source: token.source,
    notes: token.notes
  });
}

console.log('\n✅ All tokens from Feb 13-14 shocked alpha added to watchlist');
console.log(`   Feb 13: ${feb13tokens.length} tokens`);
console.log(`   Feb 14: ${feb14tokens.length} tokens (verified performers)`);
console.log(`   Total: ${tokens.length} tokens`);
console.log('\n📊 Testing scan...');

const opportunities = await scanner.scan();
console.log(`\nFound ${opportunities.length} opportunities:\n`);

for (const opp of opportunities) {
  console.log(`💎 ${opp.symbol}`);
  console.log(`   Score: ${opp.score}/100`);
  console.log(`   Priority: ${opp.priority}`);
  console.log(`   Call Active: ${opp.isCallActive ? 'YES' : 'NO'}`);
  console.log(`   Momentum 1h: ${opp.momentum.priceChange1h.toFixed(2)}%`);
  console.log(`   Volume 1h: $${opp.momentum.volume1h.toLocaleString()}`);
  console.log();
}
