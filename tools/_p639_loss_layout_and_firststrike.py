# -*- coding: utf-8 -*-
"""P639: what the new loss painting collided with, and First Strike says what it does.

── PART 1: THE LOSS SCREEN'S OTHER TEXT ──
P637 put a painting behind a screen that had been laid out for a plain dark
background, and photographing it showed three things standing in the wrong place.
All three are mine, from that patch.

  .exit-parchment  landed at 6.4-10.1% of the screen - printed ACROSS THE
                   BANNER. It is inserted after .res-scores, which .loss-art-on
                   hides, so it fell to the top of the overlay.
  #resDlg          sits at calc(38% + 200px), about 56-65%, which runs under the
                   hanging sign's lower edge (the sign ends at 65%).
  .res-how         the cap-ending line, fixed at 44%, which is across the hands.

TWO VOICES BECAME ONE, and that is a choice worth stating rather than burying.
The loss screen was already speaking twice - #resDlg carries _dlgOutcome, the
patron's own per-character line, and .exit-parchment carries a generic
EXIT_LINES bark keyed only on persona. They never collided before because they
sat at different heights on an empty background. The painting has room for one,
so the parchment goes and the per-patron line stays: it is the specific one, it
is what P626/P627 wrote the pools for, and it has a painted surface of its own.

── PART 2: FIRST STRIKE, PER DENIS'S RULING (a) ──
"Rewriting the description to name the actual trigger is the right call."

AND THE EFFECT IS CONFIRMED BEFORE IT IS WRITTEN DOWN, because Denis's source
described a second clause - a standing gold tax - and asked for that checked
rather than restated. It is NOT shipped, and it is dead in three independent
places:
  * the charger is `if(false&&S&&S.run)` at fark_proto.html:28252, with a
    comment reading "First Strike is pure information - no gold drain"
  * the badge it would print into reads getElementById('arrearsVal'), and NO
    element with that id exists anywhere in the file
  * the end-of-match refund gates on `G._tellState.totalRollCost>0`, a counter
    only ever initialised to 0 and only ever incremented behind that `if(false)`
So the source was not inventing it: `first_strike` INHERITED the id from In
Arrears, which did tax gold per roll, and all of In Arrears' machinery is still
in the file with its switch off. A document written against that shape would
describe exactly the two clauses Denis read. The shipped effect is the reveal,
and only the reveal.

The new line names the trigger and the effect and keeps Denis's own image. The
wording is his to overwrite; what it must not do is go back to describing a
mechanic that is not there.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the three that collided with the painting ─────────────────────────
sub(u"/* what the painting replaces - the same list the win screen suppresses */\n"
    u"#end-ov.loss-art-on .res-scores,\n"
    u"#end-ov.loss-art-on .res-gold-wrap{display:none!important}",
    u"/* what the painting replaces - the same list the win screen suppresses */\n"
    u"#end-ov.loss-art-on .res-scores,\n"
    u"#end-ov.loss-art-on .res-gold-wrap{display:none!important}\n"
    u"/* P639: AND THE GENERIC BARK, because the screen was speaking twice. #resDlg\n"
    u"   carries _dlgOutcome - the patron's own line, from the pools P626/P627 wrote\n"
    u"   - and .exit-parchment carries an EXIT_LINES bark keyed only on persona. On\n"
    u"   the old flat background they sat at different heights and both fitted; the\n"
    u"   painting has room for one, so the specific one stays.\n"
    u"   It was also landing at 6.4% - printed straight across the banner - because\n"
    u"   it is inserted after .res-scores, which the rule above hides. */\n"
    u"#end-ov.loss-art-on .exit-parchment{display:none!important}\n"
    u"/* CLEAR OF THE SIGN. #resDlg's own top is calc(38% + 200px), which put it\n"
    u"   under the hanging board's lower edge at 65%. */\n"
    u"#end-ov.loss-art-on #resDlg{top:67%!important}\n"
    u"/* the cap line is pinned at 44%, which is across the hands. Under the banner\n"
    u"   is where a subtitle belongs anyway. */\n"
    u"#end-ov.loss-art-on .res-how{top:21%}",
    'P639 the three collisions')

# ── 2. First Strike says what it does ────────────────────────────────────
sub(u"    tell:{id:'first_strike',name:'FIRST STRIKE',"
    u"desc:\"\u201cReach across the table and I read both sides of the book.\u201d\",icon:'\U0001F4D2'}},",
    u"    /* P639: NAMES THE TRIGGER, per Denis's ruling. The old line was pure\n"
    u"       metaphor, so a player who never owned a lane brand saw a sealed seat\n"
    u"       that did nothing all match and no way to find out why - the rule only\n"
    u"       fires from _firstStrike, called by the fire handler of Snare, Trade,\n"
    u"       Snuff and Fog. The reveal is the WHOLE effect: the per-roll gold drain\n"
    u"       that shares this id belonged to In Arrears and is dead in three places\n"
    u"       (an `if(false)` charger, a badge element that does not exist, and a\n"
    u"       refund gated on a counter nothing increments). Wording is Denis's to\n"
    u"       overwrite; it must not go back to describing a tax that is not there. */\n"
    u"    tell:{id:'first_strike',name:'FIRST STRIKE',"
    u"desc:\"\u201cReach across my table with a brand \u2014 Snare, Trade, Snuff, Fog \u2014 "
    u"and every die on both sides shows.\u201d\",icon:'\U0001F4D2'}},",
    'P639 First Strike names its trigger')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
