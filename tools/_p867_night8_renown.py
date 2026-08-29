# -*- coding: utf-8 -*-
u"""P867 (Denis, direct): night 8 pays its renown, and Ambrose keeps his
three tiles.

THE BUG. The night-8 branch gated on `G.rung.key==='ambrose'`. Ambrose's rung
key is 'bishop' (RUNGS[7]; the file's own idiom for him is key==='bishop' in
the FEATS check), so the branch has never fired in the history of the game.
Its +150 renown and its trophy push are a reward that does not exist.

AND THE SAME BUG WAS FOUND, FIXED AND DOCUMENTED TWELVE LINES BELOW IT. The
else-if directly underneath carries the comment "the boss's NAME, not
rung.key - see _bossKey. This read rung.key and always missed, so 'HIS DIE'
was an empty card that paid gold instead." Somebody hit this exact defect,
understood it, wrote down what it was, fixed their instance - and did not look
up. That is the whole argument for `_bossKey` existing: rung.key is
drunkard/peasant/commoner/merchant/soldier/knight/noble/bishop, and NOTHING in
the file assigns key:'ambrose'. Any comparison of rung.key against a boss's
NAME is dead code by construction.

THE FIX IS NOT "CORRECT THE KEY". Correcting it in place would make the branch
fire and DELETE Ambrose's spoils screen, which section 2 needs - his Pyre is
won there. The payout and the screen were fused into one if/else and they are
two different things, so they are separated:

  * The payout LIFTS OUT of the chain, above it, unconditional on any boss
    win, keyed with _bossKey. It runs before anything can branch past it.
  * The chain loses its first arm entirely, so Ambrose falls through to the
    ordinary spoils branch with his three tiles like every other boss.
  * "THE HOUSE REMEMBERS YOUR NAME" survives as a HEADER above those tiles
    rather than as a replacement for them.

ONE WRITER FOR THE TROPHIES, NOT TWO. Denis asked for the renown and the
ambrose_weight trophy to lift together. P864 had already added a trophy grant
inside the spoils branch for every boss, so lifting a second Ambrose-only push
would have made two writers for one shelf - the shape that produced this bug
in the first place. Instead the WHOLE grant moves up into the lifted block and
covers all eight bosses from one place, and _spKey/_spRelic are computed once
there rather than redeclared below.

_n8Paid is run-scoped (S.run), so no existing save carries it and every run in
flight pays correctly the first time it beats him.
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


# ── 1. the dead branch is replaced by the lifted payout ──────────────
OLD_BRANCH = u"""  /* Night 8 (Ambrose): renown payout, his die is a trophy \u2014 no spoils */
  /* P864: THIS BRANCH HAS NEVER FIRED AND IS LEFT THAT WAY DELIBERATELY.
     Ambrose's rung key is 'bishop' (RUNGS[7]; the file's own idiom for him is
     key==='bishop', see the FEATS check), so `key==='ambrose'` never matches
     and he falls through to the ordinary boss-spoils branch below - where
     _bossKey resolves him BY NAME and his tiles render correctly. That is why
     the brief's eighth card is winnable at all.
     Two things follow, and neither is fixed here. The +150 renown and the
     trophy push below have never paid, so that is a reward the game does not
     have. And correcting the key would DELETE Ambrose's spoils screen, which
     section 2 needs, so this is a design ruling and not a typo fix. The
     trophy half is already honoured: P864 grants every boss's die at the win,
     ambrose_weight included. Denis's call on the renown. */
  if(win&&isBoss&&G.rung&&G.rung.key==='ambrose'){
    _getS();
    if(!S.run._n8Paid){
      S.run._n8Paid=true;
      S.renown=(S.renown||0)+150;
      S.trophies=S.trophies||[];if(S.trophies.indexOf('ambrose_weight')<0)S.trophies.push('ambrose_weight');
      save();
    }
    if(resCard){resCard.innerHTML='<div style="font-family:monospace;color:#dc5;padding:24px 10px;text-align:center;line-height:2">'
      +'THE HOUSE REMEMBERS YOUR NAME<br>'
      +'<span style="color:#999;font-size:11px">+150 renown \u00b7 his weight sits on your shelf</span></div>';
      resCard.classList.add('show');}
    if(endBtns)endBtns.style.display='';_endScreenPhase='ready';
  }
  else if(win&&isBoss){
    /* the boss's NAME, not rung.key - see _bossKey. This read rung.key and
       always missed, so "HIS DIE" was an empty card that paid gold instead. */
    var _spKey=_bossKey(G&&G.rung);
    /* keyed by boss name - see _bossKey; this read rung.key and always missed,
       so "HIS DIE" was an empty card that silently paid gold instead */
    var _spRelic={grog:'grogs_tooth',mabel:'mabels_thimble',finnick:'finnicks_palm',corvus:'corvus_ledger_d',
      brutus:'brutus_shield',aldric:'aldrics_square',whisper:'whispers_fang',ambrose:'ambrose_weight'}[_spKey];
    var _spTell=G.rung&&G.rung.tell;"""

NEW_BRANCH = u"""  /* \u2550\u2550\u2550 P867: THE BOSS-WIN PAYOUT, LIFTED OUT OF THE CHAIN \u2550\u2550\u2550
     What stood here compared G.rung.key against his NAME, and it has never
     fired once: Ambrose's rung key is 'bishop'. Nothing in this file
     assigns key:'ambrose' to anything, so that comparison was dead by
     construction and his +150 renown is a reward the game does not have.
     AND THE SAME BUG IS FIXED AND DOCUMENTED TWELVE LINES BELOW, in the branch
     that follows: "the boss's NAME, not rung.key - see _bossKey. This read
     rung.key and always missed." Someone hit this defect, understood it, wrote
     down what it was, fixed their own instance and did not look up. That is
     what _bossKey is FOR - it resolves the boss by name, because rung.key is
     drunkard/peasant/.../bishop and never a boss's name.
     THE FIX IS NOT TO CORRECT THE KEY IN PLACE. Doing that would make the
     branch fire and delete Ambrose's spoils screen, which is where his Pyre is
     won. The payout and the screen were fused into one if/else and they are
     two different things, so the payout lifts OUT, above the chain, keyed with
     _bossKey - and Ambrose now falls through to the ordinary spoils branch
     with his three tiles like every other boss. His line survives as a header
     above them (see _n8Hdr) rather than as a replacement for them.
     ONE WRITER FOR THE SHELF. P864 granted the trophy inside the spoils branch
     for every boss; Denis asked for Ambrose's trophy to lift with his renown.
     Doing both would leave two writers for one shelf - which is the shape that
     produced this bug. So the whole grant moved up here instead, and
     _spKey/_spRelic are computed ONCE, in this block, for everything below. */
  var _spKey=_bossKey(G&&G.rung);
  var _spRelic={grog:'grogs_tooth',mabel:'mabels_thimble',finnick:'finnicks_palm',corvus:'corvus_ledger_d',
    brutus:'brutus_shield',aldric:'aldrics_square',whisper:'whispers_fang',ambrose:'ambrose_weight'}[_spKey];
  if(win&&isBoss){
    _getS();
    var _paid=false;
    /* his die goes on the shelf for beating him - P834 made relics trophies,
       so a trophy should not have to beat a reward to be yours */
    try{
      if(_spRelic){S.trophies=S.trophies||[];
        if(S.trophies.indexOf(_spRelic)<0){S.trophies.push(_spRelic);_paid=true;}}
    }catch(e){}
    /* night 8's renown. _n8Paid is run-scoped, so no existing save carries it
       and every run in flight pays the first time it beats him. */
    if(_spKey==='ambrose'&&S.run&&!S.run._n8Paid){
      S.run._n8Paid=true;S.renown=(S.renown||0)+150;_paid=true;
    }
    if(_paid){try{save();}catch(e){}}
  }
  if(win&&isBoss){
    var _spTell=G.rung&&G.rung.tell;"""

sub(OLD_BRANCH, NEW_BRANCH, '1 payout lifted, chain split removed')

# ── 2. the trophy grant that used to live in the branch goes ─────────
sub(u"""    /* P864: THE TROPHY IS GRANTED, NOT OFFERED. P834 made relics trophies -
       rank 0 against real dice, never seated - so the die was a keepsake
       competing with two mechanical rewards and losing every time (Denis: "no
       one will pick a relic as a reward if it's just visual"). Dropping the
       tile on its own would have left S.trophies with NO live writer at all,
       because this pick was its only one; the other push is in the night-8
       branch above, which has never fired. A shelf that cannot gain an entry
       is not a kept shelf, so winning the boss now puts his die on it. */
    try{
      if(_spRelic){S.trophies=S.trophies||[];
        if(S.trophies.indexOf(_spRelic)<0){S.trophies.push(_spRelic);save();}}
    }catch(e){}
""",
    u"""    /* P867: the trophy grant MOVED UP into the lifted payout block, so the
       shelf has one writer covering all eight bosses instead of two. */
""",
    '2 trophy grant deduplicated')

# ── 3. his line becomes a header above the tiles ─────────────────────
sub(u"""    var sh='<div style="font-family:monospace;color:#eee;text-align:left;padding:10px 6px">'
      +'<div style="font-size:12px;letter-spacing:2px;color:#dc5;margin-bottom:10px">SPOILS \u2014 TAKE ONE, IT IS FINAL</div>'""",
    u"""    /* P867: night 8 keeps its line, ABOVE the tiles rather than instead of
       them. It used to be the entire screen, which is what made the renown and
       the spoils mutually exclusive. */
    var _n8Hdr=(_spKey==='ambrose')
      ?'<div style="color:#dc5;text-align:center;line-height:1.8;margin-bottom:10px">THE HOUSE REMEMBERS YOUR NAME<br>'
       +'<span style="color:#999;font-size:11px">+150 renown \u00b7 his weight sits on your shelf</span></div>'
      :'';
    var sh='<div style="font-family:monospace;color:#eee;text-align:left;padding:10px 6px">'
      +_n8Hdr
      +'<div style="font-size:12px;letter-spacing:2px;color:#dc5;margin-bottom:10px">SPOILS \u2014 TAKE ONE, IT IS FINAL</div>'""",
    '3 his line becomes a header')

# ── post-asserts ─────────────────────────────────────────────────────
# the CODE form, not the phrase: an earlier draft of this assert matched the
# literal quoted inside its own new comment and failed on itself. Third time
# today - assert against code, never against prose that describes it.
if "G.rung.key==='ambrose'" in s:
    sys.exit('THE DEAD rung.key COMPARISON SURVIVES (nothing written)')
# count the WRITE, not the word. The bare token also appears in this patch's
# own explanatory comment, which is the fourth time today an assert has matched
# prose it wrote itself. A code-shaped pattern (`S.run.x=true`) cannot.
if s.count('S.run._n8Paid=true') != 1:
    sys.exit('_n8Paid has %d writers, expected exactly 1 (nothing written)'
             % s.count('S.run._n8Paid=true'))
if s.count('S.trophies.push(') != 1:
    sys.exit('S.trophies has %d writers, expected 1 (nothing written)'
             % s.count('S.trophies.push('))
if s.count('var _spKey=_bossKey(') != 1:
    sys.exit('_spKey declared %d times, expected 1 (nothing written)'
             % s.count('var _spKey=_bossKey('))
if s.count('var _spRelic={grog:') != 1:
    sys.exit('the relic map appears %d times, expected 1 (nothing written)'
             % s.count('var _spRelic={grog:'))
for needed in ['_n8Hdr', "_spKey==='ambrose'", 'THE HOUSE REMEMBERS YOUR NAME']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
