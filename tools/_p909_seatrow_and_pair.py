# -*- coding: utf-8 -*-
u"""P909: the dead seat CSS that cost two probe runs comes out, and the outcome
check becomes a pair.

.seat-row IS DEAD, AND IT READ AS A LEAD. Five rules, zero writes anywhere in
the file. Two probe runs went looking for `.seat-row` elements to tap after a
match and found none at every timing and on every screen, because there is
nothing to find - the seats render as .ptcard (21279) and the click handler is
`sit.onclick=function(){_ptOpen=false;launchSeat(st.i);}` at 21526. Third dead
-code instance this stretch after die-kindred and spawnBankPop, and the first
one to cost anything: the others were invisible, this one impersonated a path.
That is the argument for deleting dead CSS rather than leaving it.

WHAT COMES OUT IS ONLY WHAT IS PROVEN DEAD. Censused by whether the class is
ever named beyond the stylesheet: seat-row (x5), seat-main, seat-meta (x2),
seat-hc and seat-stamp (x3) have zero uses. Twelve rules.

WHAT STAYS, and it is the reason this was not a block delete: .seat-name,
.seat-dice and .seat-die sit in the same run of lines and ARE live - but as the
definitions at 3064-3069, belonging to the .seat-frame family. The copies at
387-389 are shadowed duplicates of live classes, which is a different thing from
dead, and deleting a shadowed rule is only safe if every property it sets is
overridden. Not checked, so not touched.

THE OUTCOME CHECK BECOMES A PAIR, for the reason the per-match score floor was
thrown out. An absolute band on one tier is the same shape: 2 of 10 is both a
limping driver and a genuinely hard cell, so the lower edge can refuse a real
finding - and a brutal band-2 boss cell is exactly what the ladder exists to
discover. Two tiers, and the win rate must FALL. Flatness is the tell for the
outcome the way it is for the score. 0/10 and winning everything still fail on
sight; a legitimately hard cell no longer does.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    io.open(path, 'w', encoding='utf-8', newline='').write(
        s[:m.start()] + rep + s[m.end():])
    edits.append(label)


PAGE = os.path.join(ROOT, 'fark_proto.html')
DRV = os.path.join(ROOT, 'tools', 'fark_driver.js')

# ── 1. the dead seat rules ──────────────────────────────────────────
sub(PAGE,
    u""".seat-row{position:relative;padding:9px 12px 10px;border-radius:5px;cursor:pointer;
  background:rgba(20,14,8,.82);border:1px solid rgba(180,140,60,.35);
  font-family:var(--font-ui);transition:transform .06s}
.seat-row:active{transform:scale(.985)}
.seat-row.hc{border-color:var(--hc-color,#c0a050);box-shadow:inset 0 0 14px rgba(200,140,40,.12)}
.seat-row.spent{cursor:default;opacity:.55;filter:saturate(.6)}
.seat-row.spent:active{transform:none}
.seat-main{display:flex;align-items:center;justify-content:space-between;gap:8px}""",
    u"""/* P909: .seat-row and .seat-main deleted - five rules and one, named nowhere
   outside this stylesheet. The gauntlet's seats are .ptcard (21279) and their
   handler is `sit.onclick=function(){_ptOpen=false;launchSeat(st.i);}` (21526).
   Dead CSS is not merely unused here: two probe runs went hunting for
   `.seat-row` elements to tap after a match and found none at any timing,
   because there was nothing to find. It impersonated a path. */""",
    '1a seat-row and seat-main')

sub(PAGE,
    u""".seat-meta{display:flex;gap:14px;margin-top:6px;font-size:9px;letter-spacing:1px;color:var(--textdim)}
.seat-meta b{color:var(--gold);font-weight:normal;font-size:11px;letter-spacing:.5px}""",
    u"""/* P909: .seat-meta, same census - no use outside this stylesheet. */""",
    '1b seat-meta')

sub(PAGE,
    u""".seat-hc{margin-top:6px;font-size:9px;letter-spacing:1.5px;color:var(--hc-color,#e0a040)}""",
    u"""/* P909: .seat-hc, same census. */""",
    '1c seat-hc')

sub(PAGE,
    u""".seat-stamp{position:absolute;top:50%;right:14px;transform:translateY(-50%) rotate(-8deg);
  font-size:15px;letter-spacing:3px;padding:2px 8px;border:2px solid;border-radius:3px;opacity:.9}
.seat-stamp.won{color:#7ddc84;border-color:rgba(90,180,90,.7)}
.seat-stamp.lost{color:#e0868e;border-color:rgba(180,80,90,.7)}""",
    u"""/* P909: .seat-stamp and its .won/.lost variants, same census - three more
   rules named nowhere outside this stylesheet. Included rather than left for
   later: half a deletion leaves the other half looking deliberate. */""",
    '1d seat-stamp')

# ── 2. the outcome check becomes a pair ─────────────────────────────
sub(DRV,
    u"""  /* THE OUTCOME CHECK, on the axis the pair test cannot see. Scoring that
     scales correctly and winning 0% or 100% are both broken, and the score
     gate would pass either. Ten matches at one tier before six hours are
     committed; two to eight wins. That band is deliberately wide - this is a
     smoke test for a broken driver, not a measurement of difficulty, and a
     narrow one would refuse real results. The original run's 0 from 8 fails it
     immediately, with no argument about luck required. */
  const WIN_MIN = 2, WIN_MAX = 8, WIN_N = 10;
  function sanityWinRate(results) {
    const done = (results || []).filter(r => r && !r.err && !r.stalled);
    if (done.length < WIN_N) return {ok: false,
      why: 'only ' + done.length + ' of ' + WIN_N + ' matches completed; a win ' +
           'rate over fewer is not the check this is'};
    const wins = done.filter(r => r.win).length;
    if (wins < WIN_MIN || wins > WIN_MAX) return {ok: false, wins, n: done.length,
      why: wins + ' wins in ' + done.length + '. Anything outside ' + WIN_MIN +
           '-' + WIN_MAX + ' at one tier is a driver that is not playing, not a ' +
           'difficulty finding - the run this replaces went 0 from 8 while ' +
           'scoring a quarter of the target. Fix the driver, not the band.'};
    return {ok: true, wins, n: done.length};
  }""",
    u"""  /* THE OUTCOME CHECK, on the axis the score gate cannot see - and A PAIR, for
     the same reason the per-match score floor was thrown out. An absolute band
     on one tier is that shape again: 2 of 10 is both a limping driver and a
     genuinely hard cell, so its lower edge can refuse a real finding, and a
     brutal band-2 boss cell is exactly what the ladder exists to discover.
     Two tiers, and the win rate must FALL. Flatness is the tell for the outcome
     the way it is for the score.
     SAME SCOPE NOTE AS THE OTHER PAIR: at ten matches a cell the variance is
     large, so this catches a driver that does not play, not one that plays
     slightly wrong. A pass is a smoke test, not calibration. */
  const WIN_N = 10;
  function sanityWinRate(easy, hard) {
    const clean = a => (a || []).filter(r => r && !r.err && !r.stalled);
    const e = clean(easy), h = clean(hard);
    if (e.length < WIN_N || h.length < WIN_N) return {ok: false,
      why: 'need ' + WIN_N + ' completed matches in each cell; got ' + e.length +
           ' easy and ' + h.length + ' hard. A win rate over fewer is not this ' +
           'check'};
    const ew = e.filter(r => r.win).length, hw = h.filter(r => r.win).length;
    /* the two that fail on sight, whatever the other cell says */
    if (ew === 0) return {ok: false, easyWins: ew, hardWins: hw,
      why: 'zero wins in ' + e.length + ' at the EASY tier. A driver that never ' +
           'wins where it should is not playing - the run this replaces went 0 ' +
           'from 8 while scoring a quarter of the target'};
    if (ew === e.length && hw === h.length) return {ok: false, easyWins: ew,
      hardWins: hw, why: 'won every match at both tiers, which is not a game'};
    /* and the tell: a working player wins LESS as the match gets harder */
    if (hw >= ew) return {ok: false, easyWins: ew, hardWins: hw,
      why: ew + ' wins at the easy tier and ' + hw + ' at the hard one - the ' +
           'outcome did not fall. Flat against difficulty is the same defect as ' +
           'flat against target, and a ladder on top of it would be measuring ' +
           'something other than difficulty. Fix the driver, not the gate.'};
    return {ok: true, easyWins: ew, hardWins: hw, n: e.length};
  }""",
    '2 the outcome check is a pair')

sub(DRV,
    u"""          sanityWinRate, targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD, WIN_MIN, WIN_MAX, WIN_N,
          RELOAD_PER_MATCH};""",
    u"""          sanityWinRate, targetOf, extractWhy, until, sleep, tap,
          TARGET_SPREAD, TOTAL_SPREAD, WIN_N, RELOAD_PER_MATCH};""",
    '3 the export drops the retired band')

# ── post-asserts ────────────────────────────────────────────────────
page = io.open(PAGE, encoding='utf-8', newline='').read()
drv = io.open(DRV, encoding='utf-8', newline='').read()

# the dead rules are gone, and ONLY those
code = re.sub(r'/\*.*?\*/', '', page, flags=re.S)
for gone in ('.seat-row', '.seat-main', '.seat-meta', '.seat-hc',
             '.seat-stamp'):
    if gone in code:
        sys.exit('%s survived the deletion (already written)' % gone)
# the LIVE neighbours must not have gone with them
for keep in ('.seat-frame', '.seat-name', '.seat-dice', '.seat-die',
             '.seat-port', '.seat-stake', '.seat-seal'):
    if keep not in code:
        sys.exit('%s was deleted and is live (already written)' % keep)
if 'WIN_MIN' in drv or 'WIN_MAX' in drv:
    sys.exit('the retired absolute band survives (already written)')
if drv.count('function sanityWinRate(easy, hard)') != 1:
    sys.exit('the outcome check is not a pair (already written)')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
