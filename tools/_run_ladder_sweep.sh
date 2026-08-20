#!/bin/sh
# The priority ladder sweep (Denis's §1): tiers 5,6,7,2 (nights 6,7,8,3)
# x carl,rita, n=20 real matches per cell, sequential. Server: 8086
# (the sweep's own port - probes stay on 8087). Appends everything to
# $OUT; each cell's shoot.js return carries the per-match log lines.
set -u
cd "$(dirname "$0")/.."
OUT="${1:?usage: _run_ladder_sweep.sh <results-file>}"
for cell in 5,carl 5,rita 6,carl 6,rita 7,carl 7,rita 2,carl 2,rita; do
  tier=${cell%,*}; pol=${cell#*,}
  echo "=== CELL $tier,$pol,20 $(date +%H:%M:%S) ===" >> "$OUT"
  node tools/shoot.js \
    --url "http://localhost:8086/fark_proto.html#lad=$tier,$pol,20" \
    --eval-file tools/ladder_real.js \
    --out "$OUT.cell_${tier}_${pol}.png" >> "$OUT" 2>&1
  echo "=== CELL-END $tier,$pol $(date +%H:%M:%S) ===" >> "$OUT"
done
echo "=== SWEEP COMPLETE $(date +%H:%M:%S) ===" >> "$OUT"
