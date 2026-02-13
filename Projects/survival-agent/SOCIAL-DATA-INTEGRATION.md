# 📱 Real-Time Social Data Integration Guide

**Date**: 2026-02-11
**Goal**: Pull real-time Telegram and X (Twitter) data for viral detection

## X (Twitter) Real-Time APIs

### Option 1: Official X API v2 (Paid)

**Streaming API** (Real-time tweets):
```
https://api.twitter.com/2/tweets/search/stream
```

**Pricing**:
- **Free tier**: 50 tweets/month (useless)
- **Basic**: $100/month - 10,000 tweets/month
- **Pro**: $5,000/month - 1M tweets/month
- **Enterprise**: Custom pricing

**What you get**:
- Real-time keyword monitoring
- Filtered stream (track specific tokens/tickers)
- User mentions and engagement metrics
- Tweet volume tracking

**Worth it?**: ❌ Too expensive for meme coin trading ($100-5k/month)

### Option 2: Twitter Scraping (Free but Risky)

**Tools**:
- **Nitter** (free Twitter frontend): `https://nitter.net`
- **twscrape** (Python library): No API needed
- **Tweepy** with scraping: Rate limited but free

**How it works**:
```python
# Example with Nitter
import requests

def get_token_mentions(ticker):
    url = f"https://nitter.net/search?q=%24{ticker}"
    response = requests.get(url)
    # Parse HTML for tweet count, engagement
    return tweet_count
```

**Risks**:
- Can get IP banned
- Breaks Twitter TOS
- Not reliable for production

**Worth it?**: ⚠️ Okay for testing, not production

### Option 3: Social Sentiment APIs (Third-Party)

**LunarCrush API** (Crypto social analytics):
- **Free tier**: 100 requests/day
- Tracks Twitter mentions, engagement, sentiment
- Crypto-specific (perfect for meme coins)
- API: `https://api.lunarcrush.com/v2`

```bash
# Example
curl "https://api.lunarcrush.com/v2?data=assets&symbol=SOL&interval=day"
```

**Santiment API** (Crypto social data):
- Tracks social volume, sentiment
- Free tier available
- Good for established tokens

**CryptoMood** (AI sentiment analysis):
- Real-time news and social sentiment
- Paid (starts ~$50/month)

**Worth it?**: ✅ LunarCrush free tier is good starting point

### Option 4: X Webhooks (Advanced)

If you have X API access, set up webhooks for real-time notifications:

```javascript
// Subscribe to account activity
POST https://api.twitter.com/1.1/account_activity/all/:env_name/webhooks.json
```

**Use case**: Get notified when influencers tweet about tokens

---

## Telegram Real-Time APIs

### Option 1: Telegram Bot API (FREE ✅)

**Official Telegram Bot API**:
- 100% FREE forever
- Real-time message monitoring
- Can join public channels/groups
- No rate limits (within reason)

**How to set up**:

1. **Create a bot** with @BotFather on Telegram
2. **Get API token**
3. **Add bot to channels** you want to monitor
4. **Receive real-time messages** via webhook or polling

**Example code**:
```typescript
import TelegramBot from 'node-telegram-bot-api';

const bot = new TelegramBot('YOUR_BOT_TOKEN', { polling: true });

// Listen to all messages in channels bot is added to
bot.on('message', (msg) => {
  const text = msg.text || '';

  // Check for token mentions
  if (text.includes('CA:') || text.includes('pump.fun')) {
    console.log('New token mentioned:', text);
    // Extract contract address, add to queue
  }
});
```

**Channels to monitor**:
- Pump.fun announcement channels
- Alpha call groups
- Smart money signal channels
- Influencer channels

**Worth it?**: ✅✅✅ HIGHLY RECOMMENDED - Free and effective

### Option 2: Telegram MTProto API (Advanced)

**Official lower-level API**:
- More powerful than Bot API
- Can read ANY public channel (don't need to be admin)
- Can scrape message history
- Free

**Libraries**:
- **gramjs** (TypeScript): Most popular
- **Telethon** (Python): Widely used

**Example**:
```typescript
import { TelegramClient } from 'telegram';

const client = new TelegramClient(session, apiId, apiHash, {});

// Read messages from any public channel
const messages = await client.getMessages('pumpfun_calls', {
  limit: 100
});
```

**Worth it?**: ✅✅ Great for monitoring multiple channels without being added

### Option 3: Telegram Channel Scraping Services

**Third-party APIs**:
- **TGStat**: Channel analytics and monitoring
- **Telemetr**: Telegram analytics
- **ComBot**: Channel statistics

**Pricing**: $10-50/month typically

**Worth it?**: ⚠️ Only if you need historical data or analytics

---

## Recommended Integration Strategy

### Phase 1: FREE Telegram Integration (Start Today)

**Why first**:
- 100% free
- Most meme coin alpha comes from Telegram
- Real-time signal with zero cost
- Easy to implement (2-3 hours)

**What to monitor**:
1. **Pump.fun official channels**
2. **Alpha call groups** (paid groups often post public signals)
3. **Smart money wallets** sharing calls
4. **Developer communities**

**Implementation**:
```typescript
// Create TelegramMonitor.ts
class TelegramMonitor {
  private bot: TelegramBot;
  private watchedChannels = [
    '@pumpfun_calls',
    '@solana_alpha',
    '@memecoin_hunters'
  ];

  onTokenMention(callback: (address: string, sentiment: string) => void) {
    this.bot.on('message', (msg) => {
      const contractAddress = this.extractContractAddress(msg.text);
      const sentiment = this.analyzeSentiment(msg.text);

      if (contractAddress) {
        callback(contractAddress, sentiment);
      }
    });
  }
}
```

**Expected signals**:
- 5-20 token mentions/day from good channels
- 2-5 high-conviction calls/day
- 10-30 second latency (faster than Twitter)

### Phase 2: LunarCrush API (Free Tier)

**When**: After Telegram is working

**Why**:
- 100 requests/day free
- Twitter sentiment without paying Twitter
- Good for confirming viral momentum

**Use case**:
```typescript
// Check if token is trending on Twitter
const sentiment = await lunarcrush.getTokenSentiment(ticker);
if (sentiment.tweetVolume > 100) {
  // Viral signal - adjust exit strategy to 50/50
}
```

### Phase 3: Twitter Scraping (If Needed)

**When**: Only if you need MORE data than LunarCrush provides

**How**: Use Nitter + rotating proxies

**Risk**: Medium (can get blocked)

---

## Viral Detection Scoring System

**Combine all sources**:

```typescript
interface ViralScore {
  telegramMentions: number;    // 0-100 points
  twitterVolume: number;        // 0-100 points
  sentimentScore: number;       // 0-100 points
  influencerMentions: number;   // 0-100 points
  totalViralScore: number;      // 0-100 composite
}

function calculateViralScore(token: string): ViralScore {
  const telegram = getTelegramMentions(token); // Last 1 hour
  const twitter = getTwitterVolume(token);     // Last 1 hour
  const sentiment = analyzeSentiment(token);   // Positive vs negative
  const influencers = getInfluencerMentions(token); // Known alpha callers

  return {
    telegramMentions: Math.min(telegram * 10, 100),
    twitterVolume: Math.min(twitter / 10, 100),
    sentimentScore: sentiment * 100,
    influencerMentions: influencers * 25, // 4 mentions = 100 points
    totalViralScore: (telegram + twitter + sentiment + influencers) / 4
  };
}
```

**Use in exit strategy**:
```typescript
const viralScore = calculateViralScore(tokenAddress);

if (viralScore.totalViralScore > 70) {
  // VIRAL - Keep 50% for runner
  sellPercent = 0.50;
} else {
  // Normal - Sell 80%
  sellPercent = 0.80;
}
```

---

## Implementation Priority

### 1. ✅ PumpPortal WebSocket (Implementing Now)
- Real-time token launches
- 1-5 second entry
- FREE

### 2. 🔲 Telegram Bot API (Next - 2 hours)
- Monitor alpha channels
- FREE
- High signal quality

### 3. 🔲 LunarCrush API (After Telegram - 1 hour)
- Twitter sentiment without paying X
- 100 requests/day FREE
- Viral confirmation

### 4. 🔲 Advanced: Twitter Scraping (Optional)
- Only if need more than LunarCrush provides
- Free but risky
- Not recommended initially

---

## Example: Full Integration

```typescript
// Combined social + WebSocket scanner
class UltraScanner {
  private pumpportal: PumpPortalWebSocket;
  private telegram: TelegramMonitor;
  private lunarcrush: LunarCrushAPI;

  async evaluateToken(tokenAddress: string) {
    // 1. Real-time launch detection (PumpPortal)
    const launchData = await this.pumpportal.getToken(tokenAddress);

    // 2. Check Telegram alpha calls
    const telegramSignals = await this.telegram.getRecentMentions(tokenAddress);

    // 3. Check Twitter sentiment
    const twitterData = await this.lunarcrush.getTokenData(tokenAddress);

    // 4. Calculate composite score
    const score = {
      speed: launchData.ageSeconds < 60 ? 100 : 50,
      social: telegramSignals.length * 20,
      viral: twitterData.tweetVolume > 100 ? 100 : 50,
      total: (speed + social + viral) / 3
    };

    return score.total > 70; // High conviction trade
  }
}
```

---

## Cost Summary

| Data Source | Cost | Quality | Speed | Recommendation |
|-------------|------|---------|-------|----------------|
| PumpPortal WS | FREE | High | 1-5s | ✅✅✅ Do Now |
| Telegram Bot | FREE | Very High | 10-30s | ✅✅✅ Do Next |
| LunarCrush | FREE (100/day) | Medium | 1-5min | ✅✅ Phase 2 |
| X API Basic | $100/mo | High | Real-time | ❌ Too expensive |
| Twitter Scraping | FREE | Medium | 1-5min | ⚠️ Risky |

**Total cost for full setup**: $0/month (100% free!)

---

Want me to implement Telegram monitoring next? It's free and will give you 5-20 alpha signals per day.
