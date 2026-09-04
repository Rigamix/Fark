#!/bin/sh
# THE RUNNER, EXERCISED END TO END WITHOUT A BROWSER. Procedure before any real
# launch: it takes a minute and it has already been worth it twice.
#
#   - a sed capture group written through a heredoc lost its backslashes, so the
#     achieved-count parser had an EMPTY replacement. Every batch would have
#     parsed achieved=0 and every cell abandoned after three "empty" batches - a
#     fix that breaks the thing it fixes, silently.
#   - the seat-aware split removed the global BATCH and the START banner still
#     printed it. set -u caught that one on launch; this catches it before.
#
# THREE STUBS, because a stub that only succeeds tests only the happy path and
# the abandon-after-3 branch is the one nobody exercises:
#   ok      every batch returns a full result
#   short   every batch returns FEWER matches than asked - the budget case, and
#           the reason the counter must advance by achieved rather than asked
#   fail    every batch exits non-zero - must abandon each cell after 3, and the
#           sweep must still finish rather than hang
set -u
cd "$(dirname "$0")/.."
BIN=$(mktemp -d)
OUT=$(mktemp)
rc_all=0

mkstub() {
  case "$1" in
    ok)    printf '#!/bin/sh\necho "setup: {\\"band\\":2,\\"seat\\":\\"boss\\",\\"policy\\":\\"bea\\",\\"asked\\":6,\\"n\\":6,\\"wins\\":2}"\nexit 0\n' > "$BIN/node" ;;
    short) printf '#!/bin/sh\necho "setup: {\\"band\\":2,\\"seat\\":\\"boss\\",\\"policy\\":\\"bea\\",\\"asked\\":6,\\"n\\":2,\\"wins\\":1}"\nexit 0\n' > "$BIN/node" ;;
    fail)  printf '#!/bin/sh\necho "FAILED: the browser closed the debug connection mid-run"\nexit 1\n' > "$BIN/node" ;;
  esac
  chmod +x "$BIN/node"
}

check() {
  name=$1; want=$2; got=$3
  if [ "$want" = "$got" ]; then
    echo "  PASS $name ($got)"
  else
    echo "  FAIL $name: want $want got $got"; rc_all=1
  fi
}

for mode in ok short fail; do
  echo "=== stub: $mode ==="
  mkstub "$mode"
  : > "$OUT"
  PATH="$BIN:$PATH" timeout 120 sh tools/_run_band_ladder.sh "$OUT" bea >/dev/null 2>&1
  sweep_rc=$?
  # NO `|| echo 0`. grep -c PRINTS 0 and EXITS 1 when there are no matches, so
  # the fallback appended a SECOND zero, so every count became two lines and
  # three checks reported "want 0 got 0" as a failure. The exit status is the
  # thing to discard here, not the output.
  ends=$(grep -c 'BATCH-END' "$OUT" 2>/dev/null); ends=${ends:-0}
  dones=$(grep -c 'CELL-DONE' "$OUT" 2>/dev/null); dones=${dones:-0}
  aband=$(grep -c 'CELL-ABANDONED' "$OUT" 2>/dev/null); aband=${aband:-0}
  compl=$(grep -c 'SWEEP COMPLETE' "$OUT" 2>/dev/null); compl=${compl:-0}
  echo "  sweep_rc=$sweep_rc batch_ends=$ends cells_done=$dones abandoned=$aband complete=$compl"
  case "$mode" in
    ok)
      # every cell completes, and a full-size batch advances by its full count
      check "the sweep completes" 1 "$compl"
      check "every cell finishes" 6 "$dones"
      check "nothing is abandoned" 0 "$aband"
      ach=$(grep -o 'achieved=[0-9]*' "$OUT" | head -1 | cut -d= -f2)
      check "achieved is parsed" 6 "$ach"
      ;;
    short)
      # THE BUDGET CASE. Batches return 2 of 6, so a 120-match cell needs 60
      # batches rather than 20 - the counter must not advance by the ask.
      check "the sweep completes" 1 "$compl"
      check "every cell finishes" 6 "$dones"
      check "nothing is abandoned" 0 "$aband"
      short_ach=$(grep -o 'achieved=[0-9]*' "$OUT" | head -1 | cut -d= -f2)
      check "achieved is the short count" 2 "$short_ach"
      # 480 matches at 2 per batch, so far more batches than the ok run
      [ "$ends" -gt 200 ] && echo "  PASS batches scale with the shortfall ($ends)" \
        || { echo "  FAIL batches did not scale: $ends"; rc_all=1; }
      ;;
    fail)
      # THE BRANCH NOBODY EXERCISES: three consecutive failures abandon a cell,
      # and the sweep still reaches its end rather than spinning.
      check "every cell is abandoned" 6 "$aband"
      check "no cell reports done" 0 "$dones"
      check "the sweep still completes" 1 "$compl"
      check "three attempts per cell" 18 "$ends"
      ;;
  esac
done

rm -rf "$BIN" "$OUT"
[ "$rc_all" -eq 0 ] && echo "ALL PASS" || echo "FAILED"
exit $rc_all
