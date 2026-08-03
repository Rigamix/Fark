# -*- coding: utf-8 -*-
"""P436 - a match decided by the cap says so, and DEFEAT stops using the old font.

THE FINDING BEHIND THIS. Late nights are not harder, they are LONGER: targets
climb while opponent bank barely moves, so cap-decided endings went 0.3% at
tier 3 to 85.5% at tier 7 in the sim. The player is never told. The result
screen shows VICTORY or DEFEAT identically whether you crossed the target or
the clock ran out with you ahead - and nothing anywhere records which happened.

So the most common ending in the late game is the one the game never names.

WHAT THIS DOES NOT DO: touch a single balance number. The other half of the
ruling - raise NPC aggression with tier - is deliberately left alone, because
the evidence for it is stale by its own document's admission and aggression
already climbs .50 to .82 across the ladder. Tuning against numbers that
predate the sweep removal is the thing the sim doc warns against on the page
below the finding. That half waits for the re-run.

THE WORDING IS NOT NEW. It reuses the phrasing already on the in-match status
line for the same event - "THE CAP - YOU HOLD THE HIGHER TALLY" - rather than
inventing result-screen copy, which is Denis's.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# ── 1. record HOW it ended, at each cap decision ──────────────────────
s = sub_once(s,
  u"""    if(G.pPts>G.oPts){
      setStatusMsg('THE CAP — YOU HOLD THE HIGHER TALLY!','gold');""",
  u"""    if(G.pPts>G.oPts){
      /* WHAT ENDED THE MATCH, recorded because nothing did. The result screen
         cannot tell a target win from a clock win without it, and in the late
         game the clock is the common one. */
      G._endReason='cap';
      setStatusMsg('THE CAP — YOU HOLD THE HIGHER TALLY!','gold');""",
  'cap win stamp')

s = sub_once(s,
  u"""    setStatusMsg('THE CAP — '+(G.pPts>G.oPts?'THE LAST WORD LANDS':'NOT ENOUGH')+'!','gold');""",
  u"""    G._endReason='cap';
    setStatusMsg('THE CAP — '+(G.pPts>G.oPts?'THE LAST WORD LANDS':'NOT ENOUGH')+'!','gold');""",
  'cap final-answer stamp')

# ── 2. say so on the result screen ────────────────────────────────────
s = sub_once(s,
  u"  resTitle.textContent=win?'':'DEFEAT';\n",
  u"""  resTitle.textContent=win?'':'DEFEAT';
  /* A CAP ENDING NAMES ITSELF. Without this the most common late-game result
     is indistinguishable from crossing the target, so the player never learns
     that the clock is what they are racing. Wording reused from the in-match
     line for the same event rather than invented here. */
  (function(){
    var _how=document.getElementById('resHow');
    if(!_how){
      _how=document.createElement('div');_how.id='resHow';_how.className='res-how';
      (resTitle.parentElement||document.getElementById('end-ov')).appendChild(_how);
    }
    var _capped=!!(typeof G!=='undefined'&&G&&G._endReason==='cap');
    _how.textContent=_capped?(win?'THE CAP — YOU HELD THE HIGHER TALLY'
                                 :'THE CAP — NOT ENOUGH'):'';
    _how.classList.toggle('on',_capped);
  })();
""",
  'result screen cap line')

# ── 3. the old font on DEFEAT ─────────────────────────────────────────
# --font-px is 'Alagard','Press Start 2P' - the PREVIOUS game's pixel font.
# This is the same mistake already corrected on the win board, still live on
# the one word the loss screen shows.
s = sub_once(s,
  u".res-title{font-family:var(--font-px);font-size:clamp(36px,11vw,60px);letter-spacing:8px}",
  u"""/* 'JMH Beda', not --font-px. --font-px is 'Alagard','Press Start 2P' - the
   PREVIOUS game's pixel font - and this rule put it on the single word the
   loss screen shows. Same mistake already fixed on the win board. */
.res-title{font-family:'JMH Beda',serif;font-size:clamp(36px,11vw,60px);letter-spacing:8px}
/* the cap line: small, under the title, same voice as the in-match status */
.res-how{position:absolute;top:44%;left:50%;transform:translateX(-50%);
  font-family:'JMH Beda',serif;font-size:clamp(13px,3.6vw,18px);letter-spacing:.08em;
  color:#d8b878;text-shadow:0 2px 0 rgba(20,12,4,.8);white-space:nowrap;
  opacity:0;transition:opacity .4s ease;z-index:4;pointer-events:none}
.res-how.on{opacity:1}""",
  'res-title font + cap line css')

assert s != orig, 'nothing changed'
assert u"var(--font-px);font-size:clamp(36px,11vw,60px)" not in s, 'old font survives on res-title'
assert s.count(u"G._endReason='cap'") == 2, "stamp count %d" % s.count(u"G._endReason='cap'")
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P436 applied: cap endings named, res-title off the old font')
