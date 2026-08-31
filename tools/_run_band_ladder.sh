#!/bin/sh
# The band ladder: PWIN/BWIN measured on the REAL engine, keyed by the axis the
# constants actually consume.
#
# IT RUNS IN BATCHES, and that is the whole change from the first version.
# That one asked for a 130-match cell in a single shoot.js invocation. It ran
# for two and a half hours across both seats and returned NOTHING - the debug
# connection died at an unknown point, shoot.js had no close handler, and the
# process exited silently with no result, no error and no screenshot. There was
# no way afterwards to tell whether it had reached match 20 or match 129,
# because the per-match lines only reached disk inside the final result.
#   So: ~15 matches per invocation, each landing on disk in about twenty
# minutes, and a failure costs one batch instead of a whole cell. The page also
# carries its own budget (budget=NN minutes) so an invocation always comes back
# with what it has rather than running away.
#
# CELL ORDER IS PRIORITY ORDER. Band 2 is the decisive cell - the balance sim
# measured 0.443 against a stored 0.62, and nothing else in the table is 18
# points out - so it runs FIRST and with the largest n. Bands 1 and 3 measured
# close to stored (0.527 vs 0.55, 0.683 vs 0.68) and are confirmatory. Stopping
# this at any point keeps every completed batch.
#
# SIZING, from a measured 43-139s per match (median ~90s, ~69s observed under
# two-way concurrency):
#   band 2, 120 per seat -> Wilson halfwidth ~8.9pp at p=0.5, which separates
#                           0.443 from 0.62 with the intervals clear
#   bands 1/3, 60 per seat -> ~12.6pp, enough to say "not wildly different"
# 480 matches total. Concurrency is TWO, enforced by shoot.js's own cap rather
# than by this file, and the browsers run below normal priority.
set -u
cd "$(dirname "$0")/.."
OUT="${1:?usage: _run_band_ladder.sh <results-file> [policy]}"
POL="${2:-carl}"
BATCH=15
BUDGET=25          # minutes; the page stops itself past this and reports

# One cell, assembled from batches. Three consecutive failed batches abandons
# the cell rather than grinding - but the batches already banked are kept, and
# the reason is written down where the numbers are.
cell() {
  b=$1; s=$2; total=$3; got=0; fails=0
  while [ "$got" -lt "$total" ]; do
    n=$BATCH
    if [ $((got + n)) -gt "$total" ]; then n=$((total - got)); fi
    echo "=== BATCH band=$b seat=$s n=$n at=$got/$total $(date +%H:%M:%S) ===" >> "$OUT"
    node tools/shoot.js \
      --url "http://localhost:8087/fark_proto.html#lb=$b,$s,$POL,$n&budget=$BUDGET" \
      --eval-file tools/ladder_band.js \
      --out "$OUT.b${b}_${s}.png" >> "$OUT" 2>&1
    rc=$?
    echo "=== BATCH-END band=$b seat=$s rc=$rc $(date +%H:%M:%S) ===" >> "$OUT"
    if [ "$rc" -ne 0 ]; then
      fails=$((fails + 1))
      echo "=== BATCH-FAIL band=$b seat=$s rc=$rc consecutive=$fails ===" >> "$OUT"
      if [ "$fails" -ge 3 ]; then
        echo "=== CELL-ABANDONED band=$b seat=$s at=$got/$total after 3 failed batches ===" >> "$OUT"
        return 1
      fi
    else
      fails=0
      got=$((got + n))
    fi
  done
  echo "=== CELL-DONE band=$b seat=$s n=$got $(date +%H:%M:%S) ===" >> "$OUT"
}

echo "=== BAND SWEEP START policy=$POL batch=$BATCH budget=${BUDGET}m $(date +%Y-%m-%d\ %H:%M:%S) ===" >> "$OUT"
cell 2 boss 120 & cell 2 patron 120 & wait
cell 3 boss 60  & cell 3 patron 60  & wait
cell 1 boss 60  & cell 1 patron 60  & wait
echo "=== BAND SWEEP COMPLETE $(date +%H:%M:%S) ===" >> "$OUT"
