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
OUT="${1:?usage: _run_band_ladder.sh <results-file> [policy] [n-per-seat] [bands]}"
POL="${2:-carl}"
# N IS SIZED TO THE QUESTION, NOT TRIMMED TO FIT THE CLOCK. Separating
# PWIN[2]=0.62 from the sim's 0.443 is a 17.7pp gap; n=50 gives a Wilson
# half-width near 13.9pp, which excludes 0.62 if the result lands near 0.44.
# n=120's 8.9pp is precision this question does not consume. Bands 1 and 3 are
# corroboration - they ran close to their stored values - so they are deferred
# and run only if band 2 comes back surprising.
NPER="${3:-120}"
BANDS="${4:-2 3 1}"
# BATCH IS SEAT-AWARE, and both halves of this were needed. Advancing the
# counter by the ACHIEVED count is necessary but not sufficient: a boss batch of
# 15 blows a 25-minute budget every time - measured 68-248s per boss match, so
# 15 of them is 17 to 62 minutes - so the counter alone would report the
# shortfall honestly while it kept happening. Six boss matches fit with room for
# the slow tail; patron matches run 49-138s and 15 fit.
BATCH_PATRON=15
BATCH_BOSS=6
BUDGET=25          # minutes; the page stops itself past this and reports

# One cell, assembled from batches. Three consecutive failed batches abandons
# the cell rather than grinding - but the batches already banked are kept, and
# the reason is written down where the numbers are.
cell() {
  b=$1; s=$2; total=$3; got=0; fails=0
  if [ "$s" = "boss" ]; then BATCH=$BATCH_BOSS; else BATCH=$BATCH_PATRON; fi
  while [ "$got" -lt "$total" ]; do
    n=$BATCH
    if [ $((got + n)) -gt "$total" ]; then n=$((total - got)); fi
    echo "=== BATCH band=$b seat=$s n=$n at=$got/$total $(date +%H:%M:%S) ===" >> "$OUT"
    node tools/shoot.js \
      --url "http://localhost:8087/fark_proto.html#lb=$b,$s,$POL,$n&budget=$BUDGET" \
      --eval-file tools/ladder_band.js \
      --out "$OUT.b${b}_${s}.png" > "$OUT.tmp.$b.$s" 2>&1
    rc=$?
    cat "$OUT.tmp.$b.$s" >> "$OUT"
    # THE COUNTER ADVANCES BY WHAT WAS MEASURED, NOT BY WHAT WAS ASKED. The
    # first run logged at=15/120 for a batch that completed 9 matches and hit
    # its budget at 11/15, so a cell would have "finished" 120 having measured
    # perhaps 70, with nothing reporting the gap. Anchored on "asked":N,"n":M
    # because a bare "n": also matches the per-tier counts in the same JSON.
    # AND NO BACKSLASH ESCAPES. The first version was a sed capture group
    # written through a heredoc and the backslashes did not survive: Python
    # read the backslash-one as an octal escape and wrote a literal control byte, so the
    # replacement was EMPTY and every batch would have parsed achieved=0 -
    # abandoning every cell after three 'empty' batches. grep -o and cut need
    # no escapes at all.
    ach=$(grep -o '"asked":[0-9]*,"n":[0-9]*' "$OUT.tmp.$b.$s" | head -1 | cut -d: -f3)
    rm -f "$OUT.tmp.$b.$s"
    echo "=== BATCH-END band=$b seat=$s rc=$rc asked=$n achieved=${ach:-0} $(date +%H:%M:%S) ===" >> "$OUT"
    if [ "$rc" -ne 0 ]; then
      fails=$((fails + 1))
      echo "=== BATCH-FAIL band=$b seat=$s rc=$rc consecutive=$fails ===" >> "$OUT"
      if [ "$fails" -ge 3 ]; then
        echo "=== CELL-ABANDONED band=$b seat=$s at=$got/$total after 3 failed batches ===" >> "$OUT"
        return 1
      fi
    elif [ -z "$ach" ] || [ "$ach" -eq 0 ] 2>/dev/null; then
      fails=$((fails + 1))
      echo "=== BATCH-EMPTY band=$b seat=$s rc=0 achieved=0 consecutive=$fails ===" >> "$OUT"
      if [ "$fails" -ge 3 ]; then
        echo "=== CELL-ABANDONED band=$b seat=$s at=$got/$total after 3 empty batches ===" >> "$OUT"
        return 1
      fi
    else
      fails=0
      got=$((got + ach))
    fi
  done
  echo "=== CELL-DONE band=$b seat=$s n=$got $(date +%H:%M:%S) ===" >> "$OUT"
}

echo "=== BAND SWEEP START policy=$POL n=$NPER bands=$BANDS batch=patron:$BATCH_PATRON,boss:$BATCH_BOSS budget=${BUDGET}m $(date +%Y-%m-%d\ %H:%M:%S) ===" >> "$OUT"
# BAND ORDER IS PRIORITY ORDER and is driven by the argument, so a scoped run
# ("2") and the full sweep ("2 3 1") are the same code path rather than two.
for b in $BANDS; do
  cell "$b" boss "$NPER" & cell "$b" patron "$NPER" & wait
done
echo "=== BAND SWEEP COMPLETE $(date +%H:%M:%S) ===" >> "$OUT"
