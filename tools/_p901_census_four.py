# -*- coding: utf-8 -*-
u"""P901: the census is a standing tool, and the first thing it found was four
more unmarked rerolls.

THE COUNT TRIPWIRE WAS THE DEFECT IT WAS GUARDING AGAINST. P900's census lived
inside a one-shot patch script - it ran once and never again - and what it
printed on failure was "the census in the comment is stale: _setDieVal 6,
reDrawDieFace 25". A number to reconcile, in a file that would never run again.
Both halves wrong.

tools/zv_reroll_census.js replaces it: runnable any time, and it DERIVES rather
than enumerates. A site is a reroll when the value it writes comes from a random
face source near the call; a forced value is not. No hand-maintained exempt
list - that would be the same defect one level up - and the exemption is an
inline NOT-A-REROLL comment, so a reason lives with the code it excuses.
Checked against a hand classification of all 33 in-place value changes: the
derived rule agreed on every one.

AND IT IMMEDIATELY FOUND FOUR MORE, which is the point:

  15247  ENCORE, RIVAL SEAT. The same card as the player's encore, which I
         tagged, and the rival's copy of it, which I did not - one seat marked
         and the other not, the exact failure the seven-site round was supposed
         to have finished with. Takes the same starstone blue.
  17580  FOOL'S GOLD - "EVERYTHING REROLLS", and nothing showed it.
  24862  JADE's break effect - "JADE SCATTERS - EVERYTHING ROLLS AGAIN".
  37922  SLIPPERY TABLE re-rolls the die it slips. It already fires a red beat
         for the slip; the rim now says the die is being re-thrown, in the same
         red, so the two read as one idea rather than two.

Eleven sites, not seven. The comment at the row said seven and is corrected -
and it now points at the tool rather than carrying a number, because a number
in a comment is a number to bump.

THE WINDOW WIDENED FROM 3 TO 5 LINES. At 3 the tool classified the rival
sleight site as a forced value: its `d.val=rollFace(d.mat)` sits four lines
above its reDrawDieFace, past the window, so a tagged reroll was being counted
as something that needed no tag. A false negative in a census is worse than a
false positive - the false positive prints a prompt and costs a reading.
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


TOOL = os.path.join(ROOT, 'tools', 'zv_reroll_census.js')
PAGE = os.path.join(ROOT, 'fark_proto.html')

# ══ 1. the window ══════════════════════════════════════════════════
sub(TOOL,
    u"""/* the window is the STATEMENT, not the line: a site may compute its face a
   line or two above the write, and a tag is armed just before it */
const W = 3;""",
    u"""/* the window is the STATEMENT, not the line: a site may compute its face a
   line or two above the write, and a tag is armed just before it.
   FIVE, not three, and the third value it was tried at. At 3 the rival's
   sleight site read as a forced value - its `d.val=rollFace(d.mat)` sits four
   lines above its reDrawDieFace, outside the window - so a tagged reroll was
   scored as one that needed no tag. A census that misses a site is worse than
   one that asks about an innocent line: the false positive costs a reading,
   the false negative is the bug this tool exists to prevent. */
const W = 5;""",
    '1 the window')

# ══ 2. the four ════════════════════════════════════════════════════
sub(PAGE,
    u"""      var _oFree2=(G.oppDice||[]).filter(function(d){return !d.kept;});
      if(!_oFree2.length)return false;
      _oFree2.forEach(function(d){d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});""",
    u"""      var _oFree2=(G.oppDice||[]).filter(function(d){return !d.kept;});
      if(!_oFree2.length)return false;
      /* P901: the SAME CARD as the player's encore, so the same starstone
         blue. The player's copy was tagged in P899 and this one was not -
         one seat marked and the other not, on one card. */
      _oFree2.forEach(function(d){
        if(d.el)_dieReroll(d.el,D3X.BEAT_INK.encore);
        d.val=rollFace(d.mat);try{reDrawDieFace(d);}catch(e){}});""",
    '2a encore, rival seat')

sub(PAGE,
    u"""  famLog("FOOL'S GOLD — EVERYTHING REROLLS");
  free.forEach(function(d){d.val=_rollD(d);try{reDrawDieFace(d);}catch(e){}});""",
    u"""  famLog("FOOL'S GOLD — EVERYTHING REROLLS");
  /* P901: it says everything rerolls and nothing showed it. */
  free.forEach(function(d){
    if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
    d.val=_rollD(d);try{reDrawDieFace(d);}catch(e){}});""",
    '2b fools gold')

sub(PAGE,
    u"""    var free=G.pool.filter(function(d){return !d.committed;});
    free.forEach(function(d){d.val=_rollD(d);d.sel=false;try{reDrawDieFace(d);}catch(e){}});""",
    u"""    var free=G.pool.filter(function(d){return !d.committed;});
    /* P901: jade scatters the whole table and said so only in the log */
    free.forEach(function(d){
      if(d.el)_dieReroll(d.el,D3X.BEAT_INK.reroll);
      d.val=_rollD(d);d.sel=false;try{reDrawDieFace(d);}catch(e){}});""",
    '2c jade scatters')

sub(PAGE,
    u"""          var _stMat=_stVic.mat||'bone';_stVic.val=rollFace(_stMat);reDrawDieFace(_stVic);
          if(_stVic.el){_dieBeat(_stVic.el,'rim',D3X.BEAT_INK.red,_oppDelay(700));spawnPixelSparks(_stVic.el,4);}""",
    u"""          /* P901: the slip already fires a red beat; the rim says the die is
             being re-thrown, in the same red, so the two read as one idea. */
          if(_stVic.el)_dieReroll(_stVic.el,D3X.BEAT_INK.red);
          var _stMat=_stVic.mat||'bone';_stVic.val=rollFace(_stMat);reDrawDieFace(_stVic);
          if(_stVic.el){_dieBeat(_stVic.el,'rim',D3X.BEAT_INK.red,_oppDelay(700));spawnPixelSparks(_stVic.el,4);}""",
    '2d slippery table')

# ══ 3. the row stops carrying a number ═════════════════════════════
sub(PAGE,
    u"""       SO: seven sites, and here is how to find an eighth. Every in-place value
       change in this file is a `_setDieVal(` or a `reDrawDieFace(` call. Any
       reroll outside that union does not exist; any inside it without a
       _dieReroll beside it is an unmarked one. */""",
    u"""       SO: many sites, and no number here - `node tools/zv_reroll_census.js`
       is the count, derived from the code every time it runs. A number in a
       comment is a number to bump, and this one was already wrong: it said
       seven, the census found eleven, and the four it added included the
       RIVAL's copy of the same encore whose player copy was already tagged.
       The tool classifies every `_setDieVal(` and `reDrawDieFace(` by whether
       its value comes from a random face source, names any reroll without a
       tag, and takes an inline NOT-A-REROLL comment as the exemption so the
       reason lives with the code it excuses. */""",
    '3 the row points at the tool')

# ── post-asserts ────────────────────────────────────────────────────
page = io.open(PAGE, encoding='utf-8', newline='').read()
code = re.sub(r'/\*.*?\*/', '', page, flags=re.S)
if code.count('_dieReroll(') - 1 != 11:
    sys.exit('%d reroll sites, expected 11 (already written - re-run the census)'
             % (code.count('_dieReroll(') - 1))
# the tag must still precede the value change at every site
for mm in re.finditer(r'_dieReroll\(', code):
    if code[max(0, mm.start() - 9):mm.start()] == 'function ':
        continue
    after = code[mm.end():mm.end() + 320]
    if not re.search(r'_setDieVal\(|reDrawDieFace\(|\.val\s*=', after):
        sys.exit('a tag at offset %d is not followed by a value change '
                 '(already written)' % mm.start())
# and the row must no longer carry a count to bump
if 'SO: seven sites' in page:
    sys.exit('the row still states a number (already written)')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
