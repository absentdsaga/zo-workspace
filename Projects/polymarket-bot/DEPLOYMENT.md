# 🚀 Production Deployment Guide

For running the bot 24/7 on a VPS for optimal performance.

## Why Deploy to VPS?

- **24/7 uptime**: Never miss opportunities
- **Lower latency**: Faster order execution
- **Stable internet**: No connection drops
- **Multiple bots**: Run different strategies simultaneously

## Recommended VPS Providers

### Budget Option: DigitalOcean ($6/month)
- 1GB RAM, 1 vCPU
- Perfect for single bot
- [Sign up here](https://www.digitalocean.com/)

### Premium Option: AWS Lightsail ($5/month)
- More regions (lower latency to Polymarket servers)
- Better uptime
- [Sign up here](https://aws.amazon.com/lightsail/)

## VPS Setup (Ubuntu 22.04)

### 1. Connect to VPS

```bash
ssh root@your-vps-ip
```

### 2. Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install -y python3 python3-pip git

# Install screen (for persistent sessions)
apt install -y screen
```

### 3. Clone Bot

```bash
# Create trading directory
mkdir -p /opt/polymarket-bot
cd /opt/polymarket-bot

# Copy your bot files (use scp or git)
# Option 1: SCP from local machine
# scp -r /home/workspace/Projects/polymarket-bot/* root@vps-ip:/opt/polymarket-bot/

# Option 2: Git clone (if you have a private repo)
# git clone https://github.com/yourusername/polymarket-bot.git .
```

### 4. Install Bot Dependencies

```bash
cd /opt/polymarket-bot
pip3 install py-clob-client web3 python-dotenv aiohttp requests
```

### 5. Configure Environment

```bash
# Create .env file
nano .env
```

Add your credentials:
```
POLYMARKET_PRIVATE_KEY=0xYOUR_KEY_HERE
```

### 6. Run Bot in Screen

```bash
# Start a screen session
screen -S polymarket-bot

# Start the bot
python3 bot.py

# Detach from screen: Ctrl+A then D
# Bot keeps running in background
```

### 7. Reconnect to Bot

```bash
# List screen sessions
screen -ls

# Reconnect to bot
screen -r polymarket-bot
```

## Monitoring & Maintenance

### Check Bot Status

```bash
# View live logs
tail -f /opt/polymarket-bot/bot.log

# Check if bot is running
ps aux | grep bot.py

# Check system resources
htop
```

### Auto-restart on Crash

Create systemd service:

```bash
nano /etc/systemd/system/polymarket-bot.service
```

Add:
```ini
[Unit]
Description=Polymarket Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/polymarket-bot
ExecStart=/usr/bin/python3 /opt/polymarket-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable polymarket-bot
systemctl start polymarket-bot

# Check status
systemctl status polymarket-bot

# View logs
journalctl -u polymarket-bot -f
```

## Security Best Practices

### 1. Firewall Setup

```bash
# Enable UFW firewall
ufw enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
```

### 2. SSH Key Authentication

```bash
# On local machine, generate SSH key
ssh-keygen -t ed25519

# Copy to VPS
ssh-copy-id root@vps-ip

# Disable password auth
nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
systemctl restart sshd
```

### 3. Separate Trading Wallet

- **NEVER** use your main wallet for bot
- Create dedicated wallet with only trading funds
- Transfer profits out regularly
- Limit exposure to $100-500 max

### 4. Environment Variable Security

```bash
# Set strict permissions on .env
chmod 600 /opt/polymarket-bot/.env

# Never commit .env to git
echo ".env" >> .gitignore
```

## Performance Optimization

### 1. Reduce Latency

Choose VPS region closest to Polymarket servers:
- **Recommended**: US East (NYC/Virginia)
- **Alternative**: US West (San Francisco)

### 2. Resource Monitoring

```bash
# Install monitoring
apt install -y htop iotop

# Check CPU usage
htop

# Check disk I/O
iotop
```

### 3. Log Rotation

```bash
# Prevent logs from filling disk
nano /etc/logrotate.d/polymarket-bot
```

Add:
```
/opt/polymarket-bot/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## Scaling to Multiple Bots

### Run Different Strategies

```bash
# Terminal 1: Sum-to-one arbitrage
screen -S bot-arb
python3 bot.py

# Terminal 2: Momentum trading
screen -S bot-momentum
python3 advanced_bot.py

# Terminal 3: Market making
screen -S bot-mm
python3 market_maker.py  # (future implementation)
```

### Separate Wallets

Use different private keys for each bot:

```bash
# .env.arb
POLYMARKET_PRIVATE_KEY=0xKEY1

# .env.momentum
POLYMARKET_PRIVATE_KEY=0xKEY2
```

Run with:
```bash
python3 bot.py --env .env.arb
python3 advanced_bot.py --env .env.momentum
```

## Backup & Recovery

### Daily Backups

```bash
# Backup trade history
crontab -e

# Add:
0 0 * * * cp /opt/polymarket-bot/bot.log /opt/backups/bot-$(date +\%Y\%m\%d).log
```

### Wallet Backup

1. Export private key to secure password manager
2. Save recovery phrase offline
3. Test recovery process

## Troubleshooting VPS Issues

### Bot Stops Running

```bash
# Check logs
journalctl -u polymarket-bot -n 100

# Restart service
systemctl restart polymarket-bot
```

### High Memory Usage

```bash
# Check memory
free -h

# If low, add swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Network Issues

```bash
# Test connectivity
ping -c 5 clob.polymarket.com

# Check DNS
nslookup clob.polymarket.com

# Restart networking
systemctl restart networking
```

## Cost Analysis

### Monthly VPS Costs

- **Basic**: $5-6/month (1GB RAM, sufficient for 1-2 bots)
- **Standard**: $12/month (2GB RAM, 3-5 bots)
- **Premium**: $24/month (4GB RAM, 10+ bots)

### ROI Calculation

```
Initial: $100 capital
Target: 20% monthly return = $20/month
VPS cost: $6/month
Net profit: $14/month

After covering VPS, effective return: 14% monthly
```

As capital scales, VPS becomes negligible cost.

## When to Scale

**After 1 Month:**
- If profitable: Add $100 more capital
- If very profitable (>30%): Double capital
- Keep VPS the same (handles it)

**After 3 Months:**
- If consistent: Upgrade to 2GB VPS
- Run multiple strategy bots
- Diversify across markets

**After 6 Months:**
- Consider dedicated server
- Run 10+ strategy variations
- Implement cross-platform arbitrage

---

**Ready to deploy?** Start with basic VPS, validate profitability, then scale. 🚀
