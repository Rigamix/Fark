# -*- coding: utf-8 -*-
"""P803+P804: a boss loss gets ONE screen, and the Last Orders sign
hangs lower with its readings registered to the paint.

Denis: "when I lose to a boss I get two screens: a loss screen (same as
losing to a patron) and a heart loss screen. Remove the basic loss
screen and fix the heart loss screen so things are aligned properly on
the top panel, they all sit too high right now on my phone... And move
those and panel down a bit."

P803 THE FLOW: endMatch keeps doing everything it does (state settles
at its bottom via _settleEndRoute as always; the loss sting plays) but
for a non-practice BOSS loss the generic end overlay is never shown -
after the bust beat clears we walk straight out through exitMatch,
whose routing already lands on the room (where initTierScreen consumes
_lastOrders and shows the heart-loss sign) or on the painted GAME OVER
when the run died. The queued end-overlay animation timers act on a
hidden overlay and are cancelled by exitMatch besides.

P804 THE SIGN (verified against the shipped panel art's own bands -
frame inner edge 52.7%, clear label strip to ~56%, icon ink 56-71.5%):
the whole sign hangs lower (--lo-top 8% -> 13%, Denis's call - the
ropes ride against slightly lit ceiling planks now and that is the
look he asked for), and the overlaid readings drop onto the painted
row: labels fully inside the clear strip (54.4%, and 2.55cqw so they
FIT it - at 2.9cqw the text was taller than the strip and bled onto
the beam), night number and hearts centred on the painted moon/mug
band instead of a hair above it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── P803: the generic overlay never shows for a boss loss ──
sub("""  /* ── Animation sequence ── */
  ov.classList.add('show');
  win?SFX.win():SFX.lose();""",
    """  /* ── Animation sequence ── */
  /* P803 (Denis): a BOSS loss gets ONE screen - the heart-loss beat.
     The generic loss overlay duplicated it (same button, nothing the
     sign does not already say). The sting still plays, the state still
     settles at the bottom of this function, and after the bust beat
     clears we walk straight out - exitMatch routes to the room (Last
     Orders mourns the heart there) or to GAME OVER on a dead run. The
     queued overlay timers act on a hidden overlay and exitMatch
     cancels them besides. */
  var _skipEndOv=(!win&&isBoss&&!(G&&G._practice));
  if(_skipEndOv){
    SFX.lose();
    setTimeout(function(){try{exitMatch();}catch(e){}},900);
  }else{
  ov.classList.add('show');
  win?SFX.win():SFX.lose();
  }""",
    'one screen for a boss loss')

# ── P804: the sign hangs lower ──
sub(""".lo-screen .lo-sign{--lo-tilt:0deg;--lo-top:8%;""",
    """/* P804: Denis - 'move those and panel down a bit'. The ropes now ride
   against the slightly lit ceiling planks; his call, his look. */
.lo-screen .lo-sign{--lo-tilt:0deg;--lo-top:13%;""",
    'the sign hangs lower')

# ── P804: labels fit INSIDE the clear strip ──
sub(""".lo-screen .lo-c{position:absolute;top:53.6%;height:3.6%;""",
    """/* P804: 54.4% and a size that FITS - at 2.9cqw the text was taller
   than the 3.6% strip and bled up onto the beam's frame line, which is
   Denis's 'they all sit too high'. */
.lo-screen .lo-c{position:absolute;top:54.4%;height:3.6%;""",
    'labels drop into the strip')

sub(""".lo-screen .lo-lab{font-size:2.9cqw;letter-spacing:.08em;white-space:nowrap}""",
    """.lo-screen .lo-lab{font-size:2.55cqw;letter-spacing:.08em;white-space:nowrap}""",
    'labels fit the strip')

# ── P804: night + hearts centre on the painted icon band ──
sub(""".lo-screen .lo-night{position:absolute;left:23.5%;width:8.5%;
  top:56.7%;height:14.5%;""",
    """.lo-screen .lo-night{position:absolute;left:23.5%;width:8.5%;
  top:57.9%;height:14.5%;/* P804: centred on the painted moon */""",
    'the night number drops')

sub(""".lo-screen .lo-hearts{position:absolute;left:32.8%;right:37.2%;
  top:57.6%;height:13.0%;""",
    """.lo-screen .lo-hearts{position:absolute;left:32.8%;right:37.2%;
  top:58.8%;height:13.0%;/* P804: centred on the painted icon row */""",
    'the hearts drop')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
