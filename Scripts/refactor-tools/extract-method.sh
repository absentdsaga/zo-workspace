#!/bin/bash
# Extract a method from a TypeScript file
FILE=$1
METHOD=$2

if [ -z "$FILE" ] || [ -z "$METHOD" ]; then
  echo "Usage: $0 <file> <method-name>"
  exit 1
fi

awk "/private.*$METHOD.*\{/,/^  \}/" "$FILE"
