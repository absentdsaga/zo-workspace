#!/bin/bash

# Live monitor - updates every 5 seconds
# Shows clean, validated position data

while true; do
  bun "$(dirname "$0")/monitor.ts"
  sleep 5
done
