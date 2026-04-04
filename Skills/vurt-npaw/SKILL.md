---
name: vurt-npaw
description: Pull VURT platform viewing analytics from NPAW/Youbora API — top content, devices, geo, quality metrics, concurrent viewers. Use when you need to know what people actually watch on myvurt.com and the app.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Usage

```bash
python3 Skills/vurt-npaw/scripts/npaw.py --top-content
python3 Skills/vurt-npaw/scripts/npaw.py --devices
python3 Skills/vurt-npaw/scripts/npaw.py --geo
python3 Skills/vurt-npaw/scripts/npaw.py --quality
python3 Skills/vurt-npaw/scripts/npaw.py --concurrent
python3 Skills/vurt-npaw/scripts/npaw.py --all
python3 Skills/vurt-npaw/scripts/npaw.py --top-content --days 30
python3 Skills/vurt-npaw/scripts/npaw.py --raw-sessions --days 1
```

## Env Vars Required
- `NPAW_SYSTEM_CODE` — account system code ("vurt")
- `NPAW_API_SECRET` — API secret for HMAC auth

## Auth
Uses HMAC MD5 signing: `md5(path + "?" + query_params + api_secret)` with a dateToken (future timestamp). No bearer token or API key header needed.

## API Reference
- Base: `https://api.youbora.com`
- Data endpoint: `GET /{system_code}/data`
- Rawdata endpoint: `GET /{system_code}/rawdata`
- Events endpoint: `GET /{system_code}/rawdata/events`
