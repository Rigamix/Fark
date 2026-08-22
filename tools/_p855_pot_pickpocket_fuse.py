# -*- coding: utf-8 -*-
"""P855: Denis's two P854 regressions + the Short Fuse scaling ruling.

Both regressions are mine and both are the session's recurring lesson
at a smaller scale: a value that SHADOWS an existing one has to die
everywhere the original does, and a retune has to move every site -
not the two a comment happens to name.

1. ONE POT CLEAR, NOT NINE (+ a tenth). G._sacPot shadowed
   G._turnBonusPot but was cleared at 2 of the 9 sites, so it leaked
   across turns: sacrifice on turn 3 -> bust into Thick Skin (which
   banks half the turn INCLUDING the sacrifice points and clears only
   the shared pot) -> a clean winning bank on turn 5 measured against
   a stale _sacHeld and REFUSED THE WON MATCH. Denis: "do not add a
   sixth _sacPot=0. Nine call sites is what caused this and a tenth is
   the same bet." So: _clearTurnPot() zeroes both, and all nine sites
   route through it - the _removeDieAt move. A future third tally is
   added in ONE place.

2. PICKPOCKET'S THIRD SITE. P854 moved the RUNGS record and the
   fallback - the pair the P563 comment named - and missed the rival
   turn's own literal at 35520, so the badge became ASYMMETRIC: 15%
   palming from the player, 30% palming for them. Twice as strong in
   the player's favour, an asymmetry that did not exist before my
   patch. Fixed by DELETING the literal: that site now reads the same
   record, so there is one number and no next time. The comment that
   claimed P854 "moved BOTH" is corrected to name all three.

3. SHORT FUSE SCALES (Denis's ruling): gate first, then multiplier,
   burn stays absolute at every tier.
     I   lights from roll 3, x2, full burn
     II  lights from roll 2, x2, full burn
     III lights from roll 2, x3, full burn
   Reasoning kept in the source so it is not re-litigated: the card's
   other two dials are already taken inside Obsidian (sacrifice scales
   the upside, double_or_nothing the downside), and softening the burn
   would make an Obsidian card SAFER as it levels, which fights the
   family. The gate is where the decision lives ("do I push to a third
   roll?"), and it cannot carry all three tiers because roll 1 means
   always-lit, which deletes the decision - so III takes the
   multiplier.
   DATA, not branches: p:[2,2,3] (the multiplier, sacrifice's p:
   convention) and lit:[3,2,2] (the roll it lights from). CFX reads
   ev.me.tier, the established accessor (see bookends at 17577).
   BOTH SEATS: commit() already branches on ev.owner for the roll
   count (P765), so the tier read is owner-correct by construction -
   ev.me IS the acting seat's instance. Driven on the rival side, not
   taken on inspection.
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
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the canonical clear, defined beside the pot's own documentation ──
sub("""function famApplyRollForces(){""",
    """/* P855: ONE PLACE TO EMPTY THE TURN POT. _turnBonusPot had NINE clear
   sites; P854's _sacPot tally shadowed it and reached only two of them,
   so a sacrifice from an earlier turn survived a bust-save and later
   REFUSED A WON MATCH. Adding a sixth clear would have been the same
   bet that caused it - this is the _removeDieAt move instead: every
   site calls this, and the next tally that rides the pot is added here
   once rather than at nine call sites minus the ones someone misses. */
function _clearTurnPot(){
  if(typeof G==='undefined'||!G)return;
  G._turnBonusPot=0;
  G._sacPot=0;/* P854: sacrifice's slice, which cannot win a match */
}
function famApplyRollForces(){""",
    '1 _clearTurnPot')

# ── all nine sites route through it ──────────────────────────────────
sub("""     already on the table"). Tracked in G._turnBonusPot so it survives
     commit overwrites of G.turnPts and gets folded into the bank total. */
  G._turnBonusPot=0;""",
    """     already on the table"). Tracked in G._turnBonusPot so it survives
     commit overwrites of G.turnPts and gets folded into the bank total. */
  _clearTurnPot();/* P855 */""",
    '1a startPTurn')
sub("""      G.turnPts=0;G.kept=[];G._turnBonusPot=0;refreshKeptTray();updHUD();""",
    """      G.turnPts=0;G.kept=[];_clearTurnPot();/* P855 */refreshKeptTray();updHUD();""",
    '1b vow failed')
sub("""    _turnScoreClear();G._turnBonusPot=0;G._sacPot=0;/* P854 */""",
    """    _turnScoreClear();_clearTurnPot();/* P855 */""",
    '1c ward path')
sub("""    var _tsSaved=Math.floor(_tsTurnPts/2);
    G._turnBonusPot=0;""",
    """    var _tsSaved=Math.floor(_tsTurnPts/2);
    _clearTurnPot();/* P855: the sacrifice slice dies with the pot - a
       bust-save banks half the turn and used to leave the tally full */""",
    '1d thick skin')
sub("""    var _lsSaved=Math.floor(_lsTurnPts/2);
    G._turnBonusPot=0;""",
    """    var _lsSaved=Math.floor(_lsTurnPts/2);
    _clearTurnPot();/* P855 */""",
    '1e bust_bank_half')
sub("""    const saved=G.kept.reduce((a,k)=>a+k.pts,0)+(G._turnBonusPot||0);
    G._turnBonusPot=0;""",
    """    const saved=G.kept.reduce((a,k)=>a+k.pts,0)+(G._turnBonusPot||0);
    _clearTurnPot();/* P855 */""",
    "1f mabel's stitch")
sub("""  G._turnBonusPot=0;G._sacPot=0;/* P854: the tally dies with the pot */""",
    """  _clearTurnPot();/* P855 */""",
    '1g doBust')
sub("""      triggerCard('stakes_rising','+'+G._turnBonusPot,true);
    }
    G._turnBonusPot=0;""",
    """      triggerCard('stakes_rising','+'+G._turnBonusPot,true);
    }
    G._turnBonusPot=0;/* P855: the SAC slice is cleared by the win check
       just below, which needs to read it first - see _sacHeld */""",
    '1h handleBank credit')

# the win check's own clears become the canonical call
sub("""    G._sacPot=0;
    showYieldButton();return;
  }
  G._sacPot=0;""",
    """    _clearTurnPot();/* P855 */
    showYieldButton();return;
  }
  _clearTurnPot();/* P855 */""",
    '1i win-check clears')

# ── 2. pickpocket's third site reads the record ──────────────────────
sub("""    if(_ruleActive('pickpocket','o')&&Math.random()<0.3&&left>1){left--;setStatusMsg('A DIE PALMED FROM THEIR HAND','gold');}""",
    """    /* P855: READS THE RECORD, CARRIES NO LITERAL. This site kept its own
       0.3 through P854's retune, so the badge went asymmetric - 15%
       palming from the player, 30% palming for them. One number now. */
    if(_ruleActive('pickpocket','o')&&Math.random()<((_tellById('pickpocket')||{}).chance||0.15)&&left>1){left--;setStatusMsg('A DIE PALMED FROM THEIR HAND','gold');}""",
    '2a third pickpocket site')

sub("""     They agree today (the RUNGS record carries chance:.15 against a 0.15
     fallback) - which is precisely D22's point: retune the record and the two
     paths diverge in silence. P854 retuned it (.30 -> .15 on Denis's note)
     and moved BOTH, because this comment said what would happen otherwise. */""",
    """     THREE sites read this rule, not two: the RUNGS record (chance:.15),
     this fallback, and the rival turn's own roll. P854 retuned the first
     two and MISSED THE THIRD, which is exactly the silent divergence this
     comment warns about - the badge ran 15% against the player and 30%
     for them until P855. The third site now reads the record instead of
     carrying a literal, so the number lives in one place. */""",
    '2b comment corrected')

# ── 3. Short Fuse scales, as data ────────────────────────────────────
sub(""" /* P854: tiers II and III were EMPTY STRINGS - an upgraded Short Fuse
    showed a blank card (Denis: "Short Fuse doesn't have a description").
    They read the same because the CARD behaves the same: CFX.short_fuse
    reads no tier at all - rc<3 gate, flat ev.mul(2), full-loss burn -
    so it is the one family card an upgrade does not change. Whether
    II/III should scale is a design question in OPEN.md; the text is not
    the place to promise something the code does not do. */
 {id:'short_fuse',fam:'obsidian',kind:'passive',name:'Short Fuse',
  text:['From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.']},""",
    """ /* P855 (Denis's ruling): SHORT FUSE SCALES - gate first, then
    multiplier, and the burn stays ABSOLUTE at every tier because that is
    the card's price. Kept here so it is not re-litigated: the card has
    three dials and Obsidian already spends the other two - sacrifice
    scales the upside (p:[800,1200,2000]), double_or_nothing the downside
    (half/third/quarter). Softening the burn would be a third copy of
    that pattern AND would make an Obsidian card safer as it levels,
    which fights the family. The gate is where the decision lives ("do I
    push to a third roll?"), so moving it changes the shape of a turn
    rather than paying a bigger number - but it cannot carry all three
    tiers, because lighting from roll 1 means always-lit and deletes the
    decision. So III takes the multiplier.
      p:  the multiplier      (sacrifice's p: convention)
      lit: the roll it lights from */
 {id:'short_fuse',fam:'obsidian',kind:'passive',name:'Short Fuse',p:[2,2,3],lit:[3,2,2],
  text:['From your third roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your SECOND roll each turn, everything scores double. But bust after that and the fire spreads to your banked points.',
        'From your SECOND roll each turn, everything scores TRIPLE. But bust after that and the fire spreads to your banked points.']},""",
    '3a short_fuse data')

sub("""  commit:function(ev){if(!ev.mine)return;
    var rc=(ev.owner==='p')?(G.turnRollCount||0):(G._oRollNum||0);
    if(rc<3)return;
    ev.mul(2);ev.me.state.lit=true;
    if(ev.owner==='p'){_famPop('x2 SHORT FUSE');""",
    """  commit:function(ev){if(!ev.mine)return;
    var rc=(ev.owner==='p')?(G.turnRollCount||0):(G._oRollNum||0);
    /* P855: TIER-SHAPED, from the card's own data. ev.me is the ACTING
       seat's instance, so the tier read is owner-correct the same way
       the roll count above is (P765) - a boss's upgraded fuse lights on
       its own schedule, not the player's. Same accessor the bookends
       commit handler uses. */
    var _sfD=famDef('short_fuse')||{},_sfT=ev.me.tier||1;
    var _sfLit=(_sfD.lit&&_sfD.lit[_sfT-1])||3;
    var _sfMul=(_sfD.p&&_sfD.p[_sfT-1])||2;
    if(rc<_sfLit)return;
    ev.mul(_sfMul);ev.me.state.lit=true;
    if(ev.owner==='p'){_famPop('x'+_sfMul+' SHORT FUSE');""",
    '3b CFX reads the tier')
sub("""    else setStatusMsg('THEIR FUSE BURNS \u2014 x2','red');},""",
    """    else setStatusMsg('THEIR FUSE BURNS \u2014 x'+_sfMul,'red');},""",
    '3c rival message')

# ── post-asserts ─────────────────────────────────────────────────────
# exactly TWO direct writes survive by design: the one INSIDE
# _clearTurnPot, and handleBank's credit site - which must empty the pot
# while LEAVING the sac tally for the win check three lines below it.
if s.count('G._turnBonusPot=0;') != 2:
    sys.exit('turnBonusPot direct clears = %d, expected 2 (_clearTurnPot body + handleBank credit) (nothing written)'
             % s.count('G._turnBonusPot=0;'))
if s.count('G._sacPot=0;') != 1:
    sys.exit('_sacPot direct clears = %d, expected 1 (inside _clearTurnPot) (nothing written)'
             % s.count('G._sacPot=0;'))
if s.count('_clearTurnPot()') < 10:
    sys.exit('_clearTurnPot call sites = %d (nothing written)' % s.count('_clearTurnPot()'))
if 'Math.random()<0.3&&left>1' in s:
    sys.exit('THIRD PICKPOCKET LITERAL SURVIVED (nothing written)')
for needed in ['p:[2,2,3],lit:[3,2,2]', 'ev.mul(_sfMul)', 'rc<_sfLit']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits; _clearTurnPot sites=%d' % (len(edits), s.count('_clearTurnPot()')))
