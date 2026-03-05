# Saga DAO Validator — Ops Reference

> Living document. Updated as new info is discovered.

## Hardware & Hosting

| Field | Value |
|---|---|
| **Provider** | Latitude.sh |
| **Location** | Ashburn, VA |
| **Hostname** | `Saga-Dao-Mainnet` |
| **IP** | `45.250.254.141` |
| **Plan** | m4.metal.large |
| **CPU** | AMD EPYC 9254 @ 4.15GHz (24 cores) |
| **RAM** | 384 GB |
| **Disk** | 2x 480GB NVMe + 2x 4TB NVMe |
| **NICs** | 2x 10Gb/s |
| **OS** | Ubuntu 24.04 |
| **Created** | Oct 22, 2024 |
| **Cost** | $6,500/yr |
| **SSH keys** | Dioni, Bored King (Gabriel), Saga Team |

### Network Interfaces
- `eno1`: 45.250.254.141/31 — public-facing
- `eno2`: 100.64.160.34/20 — Latitude internal (used for proxy/updates)

## Infrastructure Overview

| | Testnet | Mainnet |
|---|---|---|
| **Server** | — | `Saga-Dao-Mainnet` |
| **Client** | Frankendancer (Firedancer) | Jito/Agave (with BAM merged in) |
| **Management** | Manual | solv (Gabriel's fork, v5.6.43) |
| **Service name** | `frankendancer.service` | `solv.service` |
| **Service file** | — | `/etc/systemd/system/solv.service` |
| **Run user** | — | `solv` |
| **Working dir** | — | `/home/solv` |
| **Vote account** | — | `ELLB9W7ZCwRCV3FzWcCWoyKP6NjZJKArLyGtkqefnHcG` |

## Version Check

| | Testnet | Mainnet |
|---|---|---|
| **Validator version** | `./build/native/gcc/bin/fdctl --version` | `agave-validator --version` |
| **CLI version** | `./build/native/gcc/bin/solana --version` | `solana --version` |
| **Binary location** | `./build/native/gcc/bin/` | `/home/solv/.local/share/solana/install/active_release/bin/` |
| **Past releases** | — | `/home/solv/.local/share/solana/install/releases/` |

### Current Mainnet Version
- agave-validator 3.1.9 (src:f34231b8; feat:1620780344, client:JitoLabs)
- **Running as of March 5, 2026** — upgraded from 3.1.8, BAM active
- Upgrade history: 2.3.10 → 2.3.11 → 2.3.13 → 3.0.6 → 3.0.8 → 3.0.10 → 3.0.11 → 3.0.12 → 3.0.14 → 3.1.8 → 3.1.9

### Testnet Versions (from solv4.config.json)
- Testnet Solana: 3.1.8
- Mainnet Solana (in config): 3.1.8

## BAM (Block Awareness Module)

**Status:** Active and connected (confirmed March 5, 2026).

BAM was previously a separate fork (`jito-labs/bam-client`) but has been **merged back into mainnet jito-solana**. The separate BAM repo is deprecated — releases have stopped. Running Jito 3.1.9+ with `--bam-url` flag is all that's needed.

**How BAM was enabled:**
1. Changed `VALIDATOR_TYPE` in `solv4.config.json` from `"jito"` to `"bam"`
2. Ran: `solv update --startup && solv update config && solv i`
3. solv pulled `/tmp/v3.1.9-jito` (same repo — BAM is merged into Jito now)
4. Manually added `--bam-url` to `start-validator.sh`

**Key gotcha:** `solv update --startup` can wipe custom flags from `start-validator.sh`. Always check the script after running it and re-add:
- `--accounts-db-cache-limit-mb 65536`
- `--accounts-index-scan-results-limit-mb 200000`
- Any other custom flags

**BAM endpoint:** `http://ny.mainnet.bam.jito.wtf`
Without `--bam-url`, validator runs as normal Jito (no BAM).

### Verifying BAM is working
```bash
grep -i bam /home/solv/solana-validator.log | tail -20
```
Healthy BAM connection looks like:
- `bam_connection-metrics` entries streaming every ~1 second
- `heartbeat_received=1` and `heartbeat_sent=1` cycling (bidirectional)
- `builder_config_received=1` — receiving builder configs from BAM server
- `unhealthy_connection_count=0` — no connection issues
- `bundle_received=0` is normal when not in a leader slot; bundles arrive during your leader slots

## DoubleZero (DZ)

DoubleZero provides low-latency networking infrastructure for validators. Built by Malbec Labs.

- **DZ pubkey:** `YL6gVvw8EtDLnq1byoNf8F9RWXotEzgY2tHoBVmxUL5`
- **Protocol:** GRE tunnel (IBRL mode)
- **Connect command:** `doublezero connect ibrl`
- **Interface:** `doublezero0` (GRE tunnel, IP 169.254.2.129/31)
- **Dashboard:** https://ecosystem.doublezero.dev (custom-built, LLM-powered query interface)

### DZ Packages
Two separate packages, updated independently:
1. **`doublezero`** — core networking client
   - Repo: https://github.com/malbeclabs/doublezero
   - Update: `sudo apt update && sudo apt install --only-upgrade doublezero`
2. **`doublezero-solana`** — Solana-specific CLI tools (validator access, revenue distribution, etc.)
   - Repo: https://github.com/doublezerofoundation/doublezero-offchain
   - Update: `sudo apt update && sudo apt install doublezero-solana`

### DZ Version History
| Date | Version | Notes |
|---|---|---|
| Jan 21, 2026 | v0.8.2 | Added port 44880 requirement for routing features |
| Feb 9, 2026 | v0.8.6 | — |
| Feb 18, 2026 | v0.8.9 | — |
| Feb 20, 2026 | v0.8.10 | — |
| Feb 27, 2026 | v0.8.11 | Only needed if running IBRL + multicast simultaneously |

doublezero-solana: v0.4.0 (Jan 30, 2026) — changed default leader schedule lookahead from 2 epochs to 1

### DZ Network Stats (as of Feb 2026)
- 405+ mainnet-beta validators (~40% of total stake)
- 87 RPCs connected

### DZ Modes
- **IBRL (Inter-Block Relay Layer):** Primary mode. Low-latency block relay via GRE tunnel.
- **Multicast:** Additional mode that can run simultaneously with IBRL. v0.8.11+ recommended if using both.

### DZ-specific UFW rules
Port 8899 is correctly absent from the rules — having it open caused RPC search failures in Sept 2025.
GRE protocol (47) requires a special `before.rules` edit.
DoubleZero creates a `doublezero0` tunnel interface with UDP port 44880.

**Current UFW config (March 2026):**
```
22/tcp                     ALLOW IN    Anywhere                   # SSH
53                         ALLOW IN    Anywhere                   # DNS
9600/tcp                   ALLOW IN    Anywhere
8000:8898/udp              ALLOW IN    Anywhere                   # Validator gossip/turbine
8000:8898/tcp              ALLOW IN    Anywhere
8900:10000/tcp             ALLOW IN    Anywhere                   # Validator services
8900:10000/udp             ALLOW IN    Anywhere
179/tcp                    ALLOW IN    Anywhere                   # BGP (DZ)
Anywhere/gre               ALLOW IN    Anywhere/gre               # GRE for DoubleZero
44880/udp on doublezero0   ALLOW IN    Anywhere                   # DZ tunnel interface
44880/udp                  ALLOW OUT   Anywhere on doublezero0    # DZ tunnel outbound
```
(v6 rules mirror the above)

**Note:** The UFW rules on the box reference `dobulezero0` (typo) for the inbound rule. This typo actually came from Jared's official DZ announcement — the `ufw allow in` command had `dobulezero0` while the `ufw allow out` command had `doublezero0` (correct). The real interface is `doublezero0`, so **the inbound 44880/udp rule is not matching.** Fix with:
```bash
# Delete the broken inbound rule and re-add with correct interface name
sudo ufw delete allow in on dobulezero0 to any port 44880 proto udp
sudo ufw allow in on doublezero0 to any port 44880 proto udp
sudo ufw reload
```

The correct iptables equivalent (from DZ docs):
```bash
sudo iptables -A INPUT -i doublezero0 -p udp --dport 44880 -j ACCEPT
sudo iptables -A OUTPUT -o doublezero0 -p udp --dport 44880 -j ACCEPT
```

**Full DZ-compatible UFW setup (for reference/reinstall):**
```bash
sudo ufw reset
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 53
sudo ufw allow 9600/tcp
sudo ufw allow 8000:8898/udp
sudo ufw allow 8000:8898/tcp
sudo ufw allow 8900:10000/tcp
sudo ufw allow 8900:10000/udp
sudo ufw allow 179/tcp
sudo ufw allow in on doublezero0 to any port 44880 proto udp
sudo ufw allow out on doublezero0 to any port 44880 proto udp
sudo ufw reload

# GRE tunnel support (protocol 47)
sudo sed -i '/# drop INVALID packets (logs these in loglevel medium and higher)/i # gre\n-A ufw-before-input -p 47 -j ACCEPT\n-A ufw-before-output -p 47 -j ACCEPT' /etc/ufw/before.rules

sudo ufw disable
sudo ufw enable
sudo ufw reload
```

## Yellowstone Jet (Triton/Cascade)

Provides transaction bandwidth to Triton's Cascade Bandwidth Marketplace. Runs ON the validator.

- **Service:** `yellowstone-jet.service`
- **Config:** `/home/solv/yellowstone-jet/yellowstone-jet.yml`
- **Docs:** https://docs.triton.one/chains/solana/cascade/providing-transaction-bandwidth
- **Git:** https://github.com/rpcpool/yellowstone-jet
- Requires Triton credentials (API keys in the yml config)

## Failover / Hot Identity Swap

Gabriel's solv fork supports zero-downtime identity switching between validators.

### How it works:
The `solv switch` command transfers the validator identity from one machine to another. The backup validator (Gabriel's at `109.94.97.187`) catches up as an unstaked node, then the identity is swapped over.

### Failover procedure:
```bash
# On your mainnet validator
solv switch
# Select: INCOMING
# IP: 109.94.97.187  (Gabriel's backup)
# User: solv

# Then verify on the backup:
solv catchup
```

### Returning identity after maintenance:
```bash
# On the backup validator
solv switch
# Select: INCOMING
# IP: 45.250.254.141  (your machine)
# User: solv
```

### When to use failover vs. simple restart:
- **Simple restart** (`solv restart`): For minor upgrades where you're confident. Quick, some missed slots.
- **Hot swap failover**: For risky upgrades (major version bumps, config changes, first BAM activation). Zero missed slots but requires coordination with Gabriel.
- After a failed upgrade, you can also just `solv restart` without `--rm` flag and the validator usually catches up quickly.

## solv4.config.json

Location: `/home/solv/solv4.config.json`

Key fields:
```json
{
  "NETWORK": "mainnet-beta",
  "NODE_TYPE": "validator",
  "VALIDATOR_TYPE": "bam",
  "RPC_TYPE": "none",
  "MNT_DISK_TYPE": "triple",
  "TESTNET_SOLANA_VERSION": "3.1.8",
  "MAINNET_SOLANA_VERSION": "3.1.8",
  "NODE_VERSION": "20.17.0",
  "TESTNET_DELINQUENT_STAKE": 10,
  "MAINNET_DELINQUENT_STAKE": 5,
  "COMMISSION": 5,
  "DEFAULT_VALIDATOR_VOTE_ACCOUNT_PUBKEY": "ELLB9W7ZCwRCV3FzWcCWoyKP6NjZJKArLyGtkqefnHcG",
  "STAKE_ACCOUNTS": [],
  "HARVEST_ACCOUNT": "",
  "IS_MEV_MODE": false,
  "RPC_URL": "https://api.mainnet-beta.solana.com",
  "KEYPAIR_PATH": "",
  "DISCORD_WEBHOOK_URL": "",
  "AUTO_UPDATE": false,
  "AUTO_RESTART": false,
  "IS_DUMMY": false,
  "API_KEY": "",
  "LEDGER_PATH": "/mnt/ledger",
  "ACCOUNTS_PATH": "/mnt/accounts",
  "SNAPSHOTS_PATH": "/mnt/snapshots",
  "MOD": false
}
```

**Commission note:** `solv4.config.json` says `"COMMISSION": 5` (5%). The `start-validator.sh` uses `--commission-bps 1000` (= 10%). The solv config value is what shows on Grafana. The `--commission-bps` in the startup script controls the Jito MEV commission (tip distribution), not the overall validator commission.

## start-validator.sh (V3 — Current, pending restart)

Location: `/home/solv/start-validator.sh`

Key flags and what they do:
- **Identity/voting:** `--identity`, `--vote-account`, `--authorized-voter`
- **Storage (triple mount):** `--accounts /mnt/accounts`, `--ledger /mnt/ledger`, `--snapshots /mnt/snapshots`
- **Jito MEV:** `--tip-payment-program-pubkey`, `--tip-distribution-program-pubkey`, `--merkle-root-upload-authority`, `--commission-bps 1000`, `--block-engine-url https://ny.mainnet.block-engine.jito.wtf`
- **BAM:** `--bam-url http://ny.mainnet.bam.jito.wtf`
- **Shred receivers:** `141.98.216.96:1002`, `233.84.178.1:7733` (second one added in V3)
- **Expected shred version:** `50093` (new in V3, safety check)
- **Performance tuning:** `--accounts-db-cache-limit-mb 65536`, `--accounts-index-scan-results-limit-mb 200000`
- **Scheduler:** `--block-production-method central-scheduler-greedy`, `--block-verification-method unified-scheduler`
- **Snapshots:** max 1 full, 2 incremental
- **Ledger:** limit 50M slots, skip_any_corrupted_record WAL recovery
- **RPC:** private, full API, bound to 127.0.0.1:8899
- **Ports:** dynamic range 8000-8025

### Version History of start-validator.sh
- **V1 (original):** Basic Jito setup, 5 entrypoints, 6 known validators, no BAM
- **V2 (post-BAM config):** solv regenerated script — added `--bam-url undefined`, `--expected-shred-version 50093`, reset `--commission-bps` to 0 (had to fix back to 1000), wiped performance tuning flags
- **V3 (current):** Fixed commission-bps back to 1000, added `--bam-url http://ny.mainnet.bam.jito.wtf`, re-added `--accounts-db-cache-limit-mb` and `--accounts-index-scan-results-limit-mb`, added second shred receiver, expanded known validators list significantly

## Debugging & Logs

| | Testnet | Mainnet |
|---|---|---|
| **Why it crashed** (systemd context) | `sudo journalctl -u frankendancer.service -f -n 200` | `sudo journalctl -u solv.service -f -n 200` |
| **What's happening** (validator stream) | same as above | `solv log` or `tail -f -n 200 /home/solv/solana-validator.log` |
| **Log file location** | journald only | `/home/solv/solana-validator.log` |

### Debugging Tips
- `journalctl` shows exit codes, signals, and errors that happen before the log file opens — use it for **root cause** analysis
- `solv log` / the log file shows the validator's own output — use it to see **where** things break
- **Best practice: run both** in separate terminals when debugging

## Service Management (Mainnet)

```bash
# Via solv
solv start
solv stop
solv restart                # graceful restart (keeps ledger)
solv restart --rm           # restart with fresh snapshot download (nuclear option)
solv status
solv log                    # tail validator log
solv monitor               # monitor node
solv catchup               # check catchup status
solv config                # show solv config
solv vv                    # show solv version

# Via systemd (same thing, lower level)
sudo systemctl start solv.service
sudo systemctl stop solv.service
sudo systemctl restart solv.service
systemctl status solv.service
systemctl cat solv.service
```

## Upgrade Procedure (via solv)

### Routine mainnet upgrade:
```bash
solv update && solv update --config && solv i
```
Then check `agave-validator --version` and `cat start-validator.sh` for wiped flags, then:
```bash
solv restart
```

### Standard version bump (manual):
1. Update version in `/home/solv/solv4.config.json`
2. Run `solv update && solv update --config && solv i`
3. Check `agave-validator --version`
4. Check `start-validator.sh` for wiped flags
5. `solv restart`

### Switching validator type (e.g., jito → bam):
1. Edit `VALIDATOR_TYPE` in `solv4.config.json`
2. Run `solv update --startup && solv update config && solv i`
3. **IMPORTANT:** Check `start-validator.sh` — solv may wipe custom flags
4. Re-add any missing flags (accounts-db-cache, performance tuning, etc.)
5. Verify `start-validator.sh` looks correct
6. `solv restart`

### Rollback to previous version:
```bash
# See available versions
ls /home/solv/.local/share/solana/install/releases/

# Swap active release symlink (ln -sf overwrites in one step, no rm needed)
ln -sf /home/solv/.local/share/solana/install/releases/v3.1.8-jito /home/solv/.local/share/solana/install/active_release

# Restart
sudo systemctl restart solv.service

# Verify
agave-validator --version

# Mark bad release
mv /home/solv/.local/share/solana/install/releases/v3.1.9-jito /home/solv/.local/share/solana/install/releases/v3.1.9-jito.BAD.$(date +%Y-%m-%d)
```

**Symlink confirmed working (March 2026):** `active_release` is a proper symlink (not an overwritten directory). Gabriel fixed the solv fork to use symlinks correctly. `ln -sf` is all you need to swap versions.

## Known Issues & Lessons Learned

### solv i quirks
- `solv install --version X` sometimes fails due to custom naming conventions in Jito releases (`.1` suffix). Plain `solv i` (reading version from solv4.config.json) is more reliable.
- Since Agave 3.0.0, Anza no longer publishes pre-built binaries — solv builds from source as fallback. This is normal.
- If you cancel a `solv i` mid-install, need to `rm -rf /tmp/v3.x.x-jito` (whatever version) before retrying — the partial download blocks the next attempt.

### Deprecated flags (caught during 3.0.x upgrade)
- `--accounts-index-memory-limit-mb` → replaced by `--accounts-index-scan-results-limit-mb`
- Using the old flag causes validator to fail to start with: `error: Found argument '--accounts-index-memory-limit-mb' which wasn't expected`

### The Sept 29, 2025 incident (0 RPC nodes found)
After a server reboot + remount, validator couldn't find any RPC nodes. Root cause:
1. UFW had port 8899 set to ALLOW instead of DENY
2. Missing `contact-info.bin` in `/mnt/ledger`
3. **Fix:** Gabriel transferred a working `contact-info.bin`, did full reinstall, fixed UFW, hot-swapped identity back
4. **Lesson:** After any reinstall, run `ssh-keygen -R 45.250.254.141` on your local machine (new fingerprint)

### solv update --startup wipes custom flags
Every time `solv update --startup` regenerates `start-validator.sh`, it may:
- Reset `--commission-bps` to 0 (should be 1000)
- Remove `--accounts-db-cache-limit-mb` and `--accounts-index-scan-results-limit-mb`
- Set `--bam-url undefined` instead of the actual URL
- **Always diff or review the script after running this command**

### The symlink naming confusion (Oct 2025)
For months, the `active_release` symlink pointed to `releases/2.3.13-jito/solana-release` even though the actual binaries inside were 3.0.x. Gabriel's solv was overwriting files in-place within the old directory name. Functionally correct but confusing. Fixed in later solv versions to use proper symlinks with correct version names.

## Key Contacts

- **Gabriel (gabrieldotsol):** Maintains the solv fork. Go-to for solv bugs, version bumps, and validator type switching. Responsive on Discord. Has SSH access to the validator. SOL address: `2fquRXDqK1YLLC8E7z74CtLevw1ZiTtd6LG3L2bQsZdM`. Backup validator at `109.94.97.187`.

## Pending Actions

- [x] ~~Restart validator to activate 3.1.9 + BAM~~ (done March 5, 2026)
- [x] ~~Verify BAM is working after restart~~ (confirmed: healthy connection, heartbeats flowing)
- [ ] Confirm `--expected-shred-version 50093` is correct for current epoch
- [ ] **Fix UFW typo:** `dobulezero0` → `doublezero0` in the 44880/udp inbound rule (see DZ section)
- [ ] Document failover setup procedure (need Gabriel's initial setup chat logs)
- [ ] Ask Gabriel how he does the identity swap (confirm if `solv switch` is his current method)

## Environment (Mainnet)

- **Metrics:** `host=https://metrics.solana.com:8086,db=mainnet-beta`
- **Startup script:** `/home/solv/start-validator.sh`
- **Solv config:** `/home/solv/solv4.config.json`
- **File limits:** NOFILE=1000000, MEMLOCK=infinity
- **Restart policy:** always, 1s delay
- **Disk layout:** triple mount (accounts, ledger, snapshots on separate mounts)
- **PATH:** `/home/solv/.local/share/solana/install/active_release/bin` (set in `~/.profile`)
