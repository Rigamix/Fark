#!/bin/sh
# Remaining priority ladder cells: AMBROSE rita (tier 7) + FINNICK
# (tier 2) x carl,rita. Server 8086.
set -u
cd "$(dirname "$0")/.."
OUT="${1:?usage: _run_ladder_sweep3.sh <results-file>}"
for cell in 7,rita 2,carl 2,rita; do
  tier=${cell%,*}; pol=${cell#*,}
  echo "=== CELL $tier,$pol,20 $(date +%H:%M:%S) ===" >> "$OUT"
  node tools/shoot.js \
    --url "http://localhost:8086/fark_proto.html#lad=$tier,$pol,20" \
    --eval-file tools/ladder_real.js \
    --out "$OUT.cell_${tier}_${pol}.png" >> "$OUT" 2>&1
  echo "=== CELL-END $tier,$pol $(date +%H:%M:%S) ===" >> "$OUT"
done
echo "=== SWEEP COMPLETE $(date +%H:%M:%S) ===" >> "$OUT"
