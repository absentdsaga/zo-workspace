#!/usr/bin/env bash
#
# Validator Health Check -- Diagnostic Command Bundle
# Run this script ON the validator node. Outputs JSON-friendly diagnostics.

set -euo pipefail

VOTE_ACCOUNT="${1:-}"
IDENTITY="${2:-}"

cat << 'SCRIPT'
#!/usr/bin/env bash
set -uo pipefail

OUTPUT_FILE="/tmp/validator-diagnostics-$(date +%Y%m%d-%H%M%S).json"

echo "{"

# 1. Validator identity and vote account
echo '"identity": {'
if command -v solana &>/dev/null; then
    IDENTITY_KEY=$(solana address 2>/dev/null || echo "unknown")
    echo "\"address\": \"${IDENTITY_KEY}\","
    VOTE_KEY=$(solana-keygen pubkey ~/vote-account-keypair.json 2>/dev/null || echo "unknown")
    echo "\"vote_account\": \"${VOTE_KEY}\""
else
    echo '"error": "solana CLI not found"'
fi
echo '},'

# 2. Vote account status
echo '"vote_status": {'
if command -v solana &>/dev/null; then
    VOTE_INFO=$(solana vote-account "$VOTE_KEY" --output json 2>/dev/null || echo '{"error": "failed to query vote account"}')
    echo "\"raw\": $(echo "$VOTE_INFO" | head -c 10000)"
else
    echo '"error": "solana CLI not found"'
fi
echo '},'

# 3. Catchup status
echo '"catchup": {'
if command -v solana &>/dev/null; then
    CATCHUP=$(solana catchup --our-localhost 2>/dev/null || echo "error")
    echo "\"status\": \"$(echo "$CATCHUP" | tr '\n' ' ' | tr '"' "'")\""
else
    echo '"error": "solana CLI not found"'
fi
echo '},'

# 4. Vote latency (from recent logs)
echo '"vote_latency": {'
VOTE_LOG=$(journalctl -u solana-validator --since "5 minutes ago" --no-pager 2>/dev/null | grep -i "vote" | tail -20 || echo "")
if [ -n "$VOTE_LOG" ]; then
    VOTE_COUNT=$(echo "$VOTE_LOG" | wc -l)
    echo "\"recent_vote_log_lines\": $VOTE_COUNT,"
    echo "\"sample\": \"$(echo "$VOTE_LOG" | tail -3 | tr '\n' '|' | tr '"' "'")\""
else
    echo '"note": "no vote log lines found in last 5 minutes, check journalctl unit name"'
fi
echo '},'

# 5. Skip rate
echo '"skip_rate": {'
if command -v solana &>/dev/null; then
    SKIP=$(solana block-production --output json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for v in data.get('leaders', []):
        if v.get('identityPubkey') == '$(solana address 2>/dev/null)':
            total = v.get('leaderSlots', 0)
            skipped = v.get('skippedSlots', 0)
            rate = (skipped / total * 100) if total > 0 else 0
            print(json.dumps({'leader_slots': total, 'skipped_slots': skipped, 'skip_rate_pct': round(rate, 2)}))
            break
    else:
        print(json.dumps({'note': 'validator not found in block production'}))
except:
    print(json.dumps({'error': 'failed to parse block production'}))
" 2>/dev/null || echo '{"error": "failed to get block production"}')
    echo "\"data\": $SKIP"
else
    echo '"error": "solana CLI not found"'
fi
echo '},'

# 6. DoubleZero interface stats
echo '"doublezero": {'
if ip link show | grep -q "dz0\|dznet"; then
    DZ_IFACE=$(ip link show | grep -oP '(dz\w+)' | head -1)
    DZ_STATS=$(ip -s link show "$DZ_IFACE" 2>/dev/null || echo "")
    if [ -n "$DZ_STATS" ]; then
        RX_BYTES=$(echo "$DZ_STATS" | awk '/RX:/{getline; print $1}')
        TX_BYTES=$(echo "$DZ_STATS" | awk '/TX:/{getline; print $1}')
        RX_ERRORS=$(echo "$DZ_STATS" | awk '/RX:/{getline; print $3}')
        TX_ERRORS=$(echo "$DZ_STATS" | awk '/TX:/{getline; print $3}')
        echo "\"interface\": \"$DZ_IFACE\","
        echo "\"rx_bytes\": \"$RX_BYTES\","
        echo "\"tx_bytes\": \"$TX_BYTES\","
        echo "\"rx_errors\": \"$RX_ERRORS\","
        echo "\"tx_errors\": \"$TX_ERRORS\""
    fi
else
    echo '"status": "no DoubleZero interface detected"'
fi
echo '},'

# 7. BAM connection status
echo '"bam": {'
if pgrep -f "bam" &>/dev/null; then
    BAM_PID=$(pgrep -f "bam" | head -1)
    echo "\"running\": true,"
    echo "\"pid\": $BAM_PID,"
    BAM_CONNS=$(ss -tnp | grep "$BAM_PID" | wc -l)
    echo "\"active_connections\": $BAM_CONNS"
elif systemctl is-active bam &>/dev/null 2>&1; then
    echo '"running": true,'
    echo '"via": "systemd"'
else
    echo '"running": false,'
    echo '"note": "BAM process not detected. Check if bam service is configured."'
fi
echo '},'

# 8. NIC stats
echo '"nic": {'
PRIMARY_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -n "$PRIMARY_IFACE" ]; then
    echo "\"interface\": \"$PRIMARY_IFACE\","
    if command -v ethtool &>/dev/null; then
        SPEED=$(ethtool "$PRIMARY_IFACE" 2>/dev/null | grep "Speed:" | awk '{print $2}')
        DUPLEX=$(ethtool "$PRIMARY_IFACE" 2>/dev/null | grep "Duplex:" | awk '{print $2}')
        echo "\"speed\": \"$SPEED\","
        echo "\"duplex\": \"$DUPLEX\","
    fi
    RX_DROPS=$(cat /sys/class/net/$PRIMARY_IFACE/statistics/rx_dropped 2>/dev/null || echo "unknown")
    TX_DROPS=$(cat /sys/class/net/$PRIMARY_IFACE/statistics/tx_dropped 2>/dev/null || echo "unknown")
    RX_ERRORS=$(cat /sys/class/net/$PRIMARY_IFACE/statistics/rx_errors 2>/dev/null || echo "unknown")
    echo "\"rx_dropped\": \"$RX_DROPS\","
    echo "\"tx_dropped\": \"$TX_DROPS\","
    echo "\"rx_errors\": \"$RX_ERRORS\""
else
    echo '"error": "could not determine primary interface"'
fi
echo '},'

# 9. System resources
echo '"system": {'
echo "\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","

# CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' 2>/dev/null || echo "unknown")
echo "\"cpu_usage_pct\": \"$CPU_USAGE\","
LOAD=$(cat /proc/loadavg 2>/dev/null | awk '{print $1","$2","$3}')
echo "\"load_avg\": \"$LOAD\","

# Memory
MEM_TOTAL=$(free -g | awk '/Mem:/{print $2}')
MEM_USED=$(free -g | awk '/Mem:/{print $3}')
MEM_AVAIL=$(free -g | awk '/Mem:/{print $7}')
echo "\"mem_total_gb\": $MEM_TOTAL,"
echo "\"mem_used_gb\": $MEM_USED,"
echo "\"mem_available_gb\": $MEM_AVAIL,"

# Disk
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
LEDGER_DISK=""
if [ -d /mnt/ledger ]; then
    LEDGER_DISK=$(df -h /mnt/ledger | tail -1 | awk '{print $5}')
elif [ -d /mnt/solana/ledger ]; then
    LEDGER_DISK=$(df -h /mnt/solana/ledger | tail -1 | awk '{print $5}')
fi
echo "\"root_disk_usage\": \"$DISK_USAGE\","
if [ -n "$LEDGER_DISK" ]; then
    echo "\"ledger_disk_usage\": \"$LEDGER_DISK\","
fi

# Solana process
SOL_PID=$(pgrep -f "solana-validator\|agave-validator" | head -1 || echo "")
if [ -n "$SOL_PID" ]; then
    SOL_MEM=$(ps -p "$SOL_PID" -o rss= 2>/dev/null | awk '{printf "%.1f", $1/1048576}')
    SOL_CPU=$(ps -p "$SOL_PID" -o %cpu= 2>/dev/null)
    echo "\"validator_pid\": $SOL_PID,"
    echo "\"validator_mem_gb\": $SOL_MEM,"
    echo "\"validator_cpu_pct\": $SOL_CPU,"
fi

# Uptime
echo "\"uptime\": \"$(uptime -p 2>/dev/null || uptime)\""
echo '}'

echo "}"
SCRIPT
