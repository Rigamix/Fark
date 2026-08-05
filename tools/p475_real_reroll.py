# -*- coding: utf-8 -*-
u"""P475 - reroll_all_kept actually rerolls. Law 7's first application.

RULED: the card says reroll, so it rerolls. The text stays as written.

WHAT WAS THERE: `G.kept=[]; G.turnPts=0;` plus the bust SFX, the bust haptic,
the bust shake and "KEPT DICE WIPED!". No reroll anywhere. blessed_dice
(Ambrose) and crown_authority (Whisper) both promise, in all three text fields,
to "reroll every die you selected - scoring or not".

WHAT IT DOES NOW: every die in every kept group gets a fresh face from
rollFace(mat) - the game's own roller - and each group is RESCORED with the real
scorer. Points follow the new faces. A group that no longer scores is worth
nothing; a group that rolls better is worth more.

WHY THIS SHAPE RATHER THAN RETURNING THE DICE TO THE POOL: pool entries carry
DOM elements, lanes and selection state, and hand-building them is a large
surface for a small card. The kept groups already hold {vals, mat, pts, dice:[
{val,mat}]}, which is everything a reroll and a rescore need. The dice stay set
aside - as the text says, they were SELECTED - and only their faces change.

AND IT NOW SATISFIES THE BET LAW, which the wipe did not. A wipe is pure
downside with a known outcome. A reroll can come back better or worse, so the
card became a wager instead of a punishment - which is why "fix the code, keep
the text" was the right way round rather than rewording to match a wipe.

THE NON-DICE GROUPS ARE LEFT ALONE. Some kept entries are bonus rows with an
empty `dice` array (Obsidian's shatter payout, Pickpocket's steal). They were
never selected dice, so a card about rerolling selected dice must not touch
them - it would silently delete points the card never mentions.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""      G.kept=[];G.turnPts=0;
      /* Pulse the NPC card so it's obvious which card fired */
      triggerCard(cid,npc.name+'!',false);
      setStatusMsg(npc.name+' — KEPT DICE WIPED!','red');"""
assert s.count(OLD) == 1, 'wipe block matched %d' % s.count(OLD)

NEW = u"""      /* P475 - A REAL REROLL (Law 7: the card says reroll, so it rerolls).
         This used to be `G.kept=[];G.turnPts=0;` - a wipe, which is not what
         any of the card's three text fields promise. Every selected die now
         takes a fresh face from the game's own roller and each group is
         RESCORED, so points follow the new faces: worse, better, or nothing.
         That also makes it a wager rather than a punishment, which the wipe
         never was.
         GROUPS WITH NO DICE ARE LEFT ALONE - shatter payouts and steals are
         kept rows that were never selected dice, and a card about rerolling
         selected dice must not quietly delete them. */
      var _rrTotal=0;
      (G.kept||[]).forEach(function(k){
        if(!k||!k.dice||!k.dice.length){ _rrTotal+=(k&&k.pts)||0; return; }
        k.dice.forEach(function(dd){ try{ dd.val=rollFace(dd.mat); }catch(e){} });
        k.vals=k.dice.map(function(dd){ return dd.val; });
        var _rrR=null;
        try{ _rrR=scoreRoll(k.vals,G.pCards||[],0,{},k.dice.map(function(dd){return dd.mat;})); }catch(e){}
        k.pts=(_rrR&&_rrR.total)||0;
        _rrTotal+=k.pts;
      });
      G.turnPts=_rrTotal+(G._turnBonusPot||0);
      triggerCard(cid,npc.name+'!',false);
      setStatusMsg(npc.name+' — KEPT DICE REROLLED!','red');"""

s = s.replace(OLD, NEW)

assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert 'KEPT DICE REROLLED' in body
assert 'KEPT DICE WIPED' not in body, 'the old message survives'
assert 'rollFace(dd.mat)' in body and '_rrTotal' in body
# the wipe form must be gone from THIS branch, though _turnScoreClear elsewhere is fine
i = body.index('_rrTotal')
seg = body[max(0, i - 900):i]
assert 'G.kept=[];G.turnPts=0;' not in seg, 'the wipe is still in the branch'
# the bust SFX/haptic stay - being rerolled is still a shock - but nothing else moved
assert body.count("mechanic==='reroll_all_kept'") == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P475 applied: reroll_all_kept rerolls and rescores; non-dice kept rows untouched')
