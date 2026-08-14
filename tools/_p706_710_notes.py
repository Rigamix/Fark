# -*- coding: utf-8 -*-
"""P706-P710: five playthrough notes, each driven to its measured cause.

P706 THE BUBBLE. (a) Short lines wrapped because scrollWidth rounds the
fractional line width to the NEAREST integer - up to half a pixel SHORT -
and P682's +1 slack went on the comparison, not the returned width; the pin
was then exactly too narrow and text-wrap:balance made the accident look
deliberate. The slack moves to the return. (b) Text sat low on phone: the
P677 top-heavy padding sink survived P682, and Raritas's hhea/typo metric
split adds ~1.6px on mobile stacks; padding flips slightly bottom-heavy and
the @font-face pins the typo metrics where overrides are supported.
(c) Not bold: the Regular cut (already on disk) registers at 400 and the
bubble asks for it. (d) Outline: strokeW 2.5 -> 1.5 (the SVG margin
self-adjusts off strokeW).

P707 THE RIVAL REROLL GLITCH. During the rival's subset reroll the rethrown
chips leave the DOM for a few frames, so only the KEPT dice carry hx -
_rowMid's span midpoint then yanked the whole settled table group sideways
(shadows in lockstep, every frame) until _measureHomes caught up. A partial
population no longer centres the row: the DOM row is the authority on the
count (the _laneGrid rule), and short of it the row-rect fallback that
already serves N==1 serves N-partial too.

P708 ILL OMEN. (a) "It gave no points": a right call was a transfer capped
by the rival's BOARD - declared early, the rival busts with 0 on the board,
'YOU TAKE 0'. A right call now pays the full tier reward, minting what the
board cannot fund - exactly as the miss branch already mints the rival's
consolation. (b) An omen still armed at endMatch judged nothing: the charge
returns. (c) The activation line and card text name the RIGHT turn
(their NEXT), and Stargazer stops calling itself an omen.

P709 A survived boss loss is a LAST ORDERS beat - the same flag +
initTierScreen consumer the failed-night path already uses; the end
overlay keeps its heart-drain, the gauntlet return drops the second
mourning animation.

P710 A heart loss RESETS THE NIGHT through one path: points 0, chalk
wiped, night re-rolled (immediately, so the title's live-run check never
reads a hole). The boss gate is derived from points, so it re-locks with
zero new UI. All four heart sites route through it.
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
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ══ P706 ══
sub(u"  if (natural <= maxW + 1) return natural;",
    u"  /* P706: scrollWidth rounds to NEAREST - it can be half a pixel SHORT\n"
    u"     of the true line, and a pin that exact wraps the line it measured.\n"
    u"     P682 put the slack on the comparison; it belongs on the width. */\n"
    u"  if (natural <= maxW + 1) return natural + 1;",
    'P706 fit slack on the returned width')

sub(u"  box-shadow:none;padding:5.4cqw 6cqw 4.6cqw;max-width:99%;margin:0 0 0 3cqw;flex:0 1 auto;",
    u"  /* P706: the P677 top-heavy sink retired; slightly BOTTOM-heavy now to\n"
    u"     offset the ~1.6px hhea-metric drop on mobile text stacks (Safari\n"
    u"     ignores the @font-face metric overrides, so padding carries it). */\n"
    u"  box-shadow:none;padding:4.7cqw 6cqw 5.3cqw;max-width:99%;margin:0 0 0 3cqw;flex:0 1 auto;",
    'P706 bubble padding recentres')

sub(u"@font-face{font-family:'Raritas';src:url('Art/Assets/Fonts/fonnts.com-Raritas-Semi-Bold.otf') format('opentype');\n"
    u"  font-weight:600;font-display:swap}",
    u"@font-face{font-family:'Raritas';src:url('Art/Assets/Fonts/fonnts.com-Raritas-Semi-Bold.otf') format('opentype');\n"
    u"  font-weight:600;font-display:swap;\n"
    u"  /* P706: pin the typo metrics (hhea says 0.96em ascent, OS/2 typo says\n"
    u"     0.76 with USE_TYPO_METRICS - desktop honours it, Android reads hhea;\n"
    u"     the overrides make them agree where supported) */\n"
    u"  ascent-override:76%;descent-override:24%;line-gap-override:20%}\n"
    u"/* P706: the REGULAR cut - already in the folder, never registered - so\n"
    u"   the bubble can stop borrowing Semi-Bold (Denis: \"don't make it bold\") */\n"
    u"@font-face{font-family:'Raritas';src:url('Art/Assets/Fonts/fonnts.com-Raritas-.otf') format('opentype');\n"
    u"  font-weight:400;font-display:swap;\n"
    u"  ascent-override:76%;descent-override:24%;line-gap-override:20%}",
    'P706 Raritas Regular + metric pins')

sub(u"#screen-match .dlg-text{font-family:var(--font-dlg);font-style:normal;font-weight:600;font-size:3.8cqw;",
    u"#screen-match .dlg-text{font-family:var(--font-dlg);font-style:normal;font-weight:400;/* P706 */font-size:3.8cqw;",
    'P706 bubble unbolds')

sub(u"  strokeW: 2.5, cornerRadius: 37,",
    u"  strokeW: 1.5, cornerRadius: 37,/* P706: outline 1px thinner, per Denis */",
    'P706 outline 1.5')

# ══ P707 ══
sub(u"  _rowMid:function(key){\n"
    u"    var self=this,xs=[];\n"
    u"    this.dice.forEach(function(d){\n"
    u"      if(d.match&&d.hx!==undefined&&(!key||self._rowKey(d)===key))xs.push(d.hx);\n"
    u"    });\n"
    u"    if(xs.length>1)return (Math.min.apply(null,xs)+Math.max.apply(null,xs))/2;",
    u"  _rowMid:function(key){\n"
    u"    var self=this,xs=[];\n"
    u"    this.dice.forEach(function(d){\n"
    u"      if(d.match&&d.hx!==undefined&&(!key||self._rowKey(d)===key))xs.push(d.hx);\n"
    u"    });\n"
    u"    /* P707: a PARTIAL population must not centre the row. During the\n"
    u"       rival's subset reroll the rethrown chips leave the DOM for a few\n"
    u"       frames, so only the KEPT dice carry hx - their span midpoint\n"
    u"       yanked the whole settled group sideways (shadows in lockstep)\n"
    u"       until _measureHomes caught up. The DOM row is the authority on\n"
    u"       the count (_laneGrid's rule); short of it, fall through to the\n"
    u"       row-rect fallback that already serves the N==1 case. */\n"
    u"    var _n=0;try{var _dom=document.getElementById(key);if(_dom)_n=_dom.querySelectorAll('.die').length;}catch(e){}\n"
    u"    if(xs.length>1&&(!_n||xs.length>=_n))return (Math.min.apply(null,xs)+Math.max.apply(null,xs))/2;",
    'P707 _rowMid refuses partial readings')

# ══ P708 ══
sub(u"    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;G.pPts+=take;\n"
    u"      G._featOmenTrue=true;/* OMENS TRUE */\n"
    u"      famLog('THE OMEN LANDS — YOU TAKE '+take);",
    u"    if(ev.pts<=0){var take=Math.min(_ioP[0],G.oPts);G.oPts-=take;\n"
    u"      /* P708: a right call pays the FULL tier reward - what their board\n"
    u"         cannot fund is minted, exactly as the miss branch mints theirs.\n"
    u"         'YOU TAKE 0' on a first-turn bust was Denis's missing points. */\n"
    u"      G.pPts+=_ioP[0];\n"
    u"      G._featOmenTrue=true;/* OMENS TRUE */\n"
    u"      famLog('THE OMEN LANDS — YOU TAKE '+_ioP[0]);",
    'P708 full payout on a right call')

sub(u"  use:function(inst){\n"
    u"    G._famIllOmen={tier:inst.tier};\n"
    u"    famLog('ILL OMEN DECLARED — THEY BUST THIS TURN, OR PAY YOU DO');\n"
    u"    return true;\n"
    u"  }",
    u"  use:function(inst){\n"
    u"    G._famIllOmen={tier:inst.tier};\n"
    u"    /* P708: name the RIGHT turn and both outcomes plainly - the old line\n"
    u"       said 'THIS TURN, OR PAY YOU DO', which was wrong twice over. */\n"
    u"    var _ioPu=famDef('ill_omen').p[inst.tier-1];\n"
    u"    famLog('ILL OMEN — THEY BUST THEIR NEXT TURN: YOU TAKE '+_ioPu[0]+'. THEY SCORE: THEY GAIN '+_ioPu[1]);\n"
    u"    return true;\n"
    u"  }",
    'P708 honest activation line')

sub(u"  text:[\"At your turn's end, declare they will bust this turn. Right: take 800 from them. Wrong: they gain 400.\",\n"
    u"        \"At your turn's end, declare they will bust this turn. Right: take 1200 from them. Wrong: they gain 400.\",\n"
    u"        \"At your turn's end, declare they will bust this turn. Right: take 1600 from them. Wrong: they gain 300.\"]},",
    u"  text:[\"Declare their next turn a bust. Right: take 800. Wrong: they gain 400.\",\n"
    u"        \"Declare their next turn a bust. Right: take 1200. Wrong: they gain 400.\",\n"
    u"        \"Declare their next turn a bust. Right: take 1600. Wrong: they gain 300.\"]},",
    'P708 card text names the next turn')

sub(u"    famLog('OMEN — NEXT ROLL: '+G._famPeekVals.join(' · '));",
    u"    famLog('STARGAZER — NEXT ROLL: '+G._famPeekVals.join(' · '));/* P708: only Ill Omen says OMEN */",
    'P708 stargazer announces itself')

sub(u"    famLog('THE OMEN HOLDS');",
    u"    famLog('THE STARS HOLD');/* P708 */",
    'P708 stars hold')

sub(u"function endMatch(win){\n"
    u"  if(G&&win&&G._arrearsPot>0){",
    u"function endMatch(win){\n"
    u"  /* P708: an omen still armed when the match ends judged nothing - the\n"
    u"     charge comes home. Self-guarding: the flag nulls right here. */\n"
    u"  try{\n"
    u"    if(G&&G._famIllOmen&&G.pF){\n"
    u"      var _ioBack=G.pF.find(function(c){return c&&c.id==='ill_omen';});\n"
    u"      if(_ioBack)_ioBack.charges=(_ioBack.charges||0)+1;\n"
    u"      G._famIllOmen=null;\n"
    u"      famLog('THE OMEN GOES UNREAD — THE CHARGE RETURNS');\n"
    u"    }\n"
    u"  }catch(e){}\n"
    u"  if(G&&win&&G._arrearsPot>0){",
    'P708 unread omen refunds')

# ══ P710: the one reset, then P709 riding its call sites ══
sub(u"function _showLastOrders(){",
    u"/* P710: ONE reset for every heart loss. Points to zero re-locks the boss\n"
    u"   (the gate is derived, nothing stored), the chalk wipes, and the night\n"
    u"   re-rolls IMMEDIATELY - a lazily-null night made the title's live-run\n"
    u"   check read false until the next tier render. */\n"
    u"function _heartLossReset(){\n"
    u"  S.run.points=0;S.run._chalkMeta=[];S.run.night=null;\n"
    u"  try{_ensureNight();}catch(e){}\n"
    u"}\n"
    u"function _showLastOrders(){",
    'P710 _heartLossReset')

sub(u"  S.run.points=0;S.run._chalkMeta=[];S.run.night=null;S.run._lastOrders=true;",
    u"  _heartLossReset();S.run._lastOrders=true;/* P710: one reset path */",
    'P710 night-fail routes through it')

sub(u"  }else if(!route.win&&route.isBoss){\n"
    u"    /* Boss loss — the boss eats a heart; at 0 the run dies. */\n"
    u"    S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"    if(S.run.coins<=0)S.run._died=true;\n"
    u"    else route._heartAnim='lose';\n"
    u"  }",
    u"  }else if(!route.win&&route.isBoss){\n"
    u"    /* Boss loss — the boss eats a heart; at 0 the run dies. */\n"
    u"    S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"    if(S.run.coins<=0)S.run._died=true;\n"
    u"    else{\n"
    u"      /* P709/P710: a survived boss loss is a LAST ORDERS beat - the\n"
    u"         heart is mourned on that screen (initTierScreen consumes the\n"
    u"         flag, same as a failed night), the boss locks again and the\n"
    u"         crowd re-rolls. The sign's NEW ROSTER line is true here. */\n"
    u"      _heartLossReset();\n"
    u"      S.run._lastOrders=true;\n"
    u"    }\n"
    u"  }",
    'P709/710 boss loss = Last Orders + reset')

sub(u"      showScreen('gauntlet',{heartAnim:route._heartAnim||'lose'});",
    u"      showScreen('gauntlet');/* P709: Last Orders mourns the heart - no second animation */",
    'P709 no double mourning')

sub(u"    if(_abSnap.isBoss){\n"
    u"      S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"      if(S.run.coins<=0){S.run._died=true;save();showScreen('gameover');return;}\n"
    u"    }else{",
    u"    if(_abSnap.isBoss){\n"
    u"      S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"      if(S.run.coins<=0){S.run._died=true;save();showScreen('gameover');return;}\n"
    u"      _heartLossReset();S.run._lastOrders=true;/* P710: abandon = the same beat */\n"
    u"    }else{",
    'P710 boss abandon resets')

sub(u"    if(S.pendingMatch.isBoss){\n"
    u"      S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"      if(S.run.coins<=0)S.run._died=true;/* surfaces at the next tier screen */\n"
    u"    }",
    u"    if(S.pendingMatch.isBoss){\n"
    u"      S.run.coins=Math.max(0,(S.run.coins||0)-1);\n"
    u"      if(S.run.coins<=0)S.run._died=true;/* surfaces at the next tier screen */\n"
    u"      else{_heartLossReset();S.run._lastOrders=true;}/* P710 */\n"
    u"    }",
    'P710 pending-boss discard resets')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
