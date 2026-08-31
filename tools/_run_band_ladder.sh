#!/bin/sh
# The band ladder: PWIN/BWIN measured on the REAL engine, keyed by the axis the
# constants actually consume.
#
# CELL ORDER IS PRIORITY ORDER, and that is the whole design of this script.
# Band 2 is the decisive cell - the balance sim measured 0.443 against a stored
# 0.62, and nothing else in the table is 18 points out - so it runs FIRST and
# with the largest n. Bands 1 and 3 measured close to stored (0.527 vs 0.55,
# 0.683 vs 0.68) and are confirmatory. If this is stopped early, the completed
# cells still answer the question that motivated the run.
#
# SIZING, from a measured 43-139s per match (median ~90s):
#   band 2, n=130 -> Wilson halfwidth ~8.6pp at p=0.5, which separates 0.443
#                    from 0.62 with the intervals clear of each other
#   bands 1/3, n=60 -> ~12.6pp, enough to say "not wildly different from stored"
#   500 matches total ~ 12.5 browser-hours ~ 6.3h wall-clock at two concurrent.
# The 6x500 originally sketched would have been ~37h at the same concurrency;
# that arithmetic is why this is smaller, and it is stated rather than quietly
# trimmed.
#
# Concurrency is TWO, enforced by shoot.js's own cap rather than by this file -
# the browsers also run below normal priority, so the machine stays usable.
set -u
cd "$(dirname "$0")/.."
OUT="${1:?usage: _run_band_ladder.sh <results-file> [policy]}"
POL="${2:-carl}"

run_cell() {
  b=$1; s=$2; n=$3
  echo "=== CELL band=$b seat=$s n=$n policy=$POL $(date +%H:%M:%S) ===" >> "$OUT"
  node tools/shoot.js \
    --url "http://localhost:8087/fark_proto.html#lb=$b,$s,$POL,$n" \
    --eval-file tools/ladder_band.js \
    --out "$OUT.b${b}_${s}.png" >> "$OUT" 2>&1
  echo "=== CELL-END band=$b seat=$s $(date +%H:%M:%S) ===" >> "$OUT"
}

echo "=== BAND SWEEP START policy=$POL $(date +%Y-%m-%d\ %H:%M:%S) ===" >> "$OUT"
run_cell 2 boss 130 & run_cell 2 patron 130 & wait
run_cell 3 boss 60  & run_cell 3 patron 60  & wait
run_cell 1 boss 60  & run_cell 1 patron 60  & wait
echo "=== BAND SWEEP COMPLETE $(date +%H:%M:%S) ===" >> "$OUT"
grep -h '^LB-CELL' "$OUT" >> "$OUT" 2>/dev/null || true
