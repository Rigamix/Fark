# -*- coding: utf-8 -*-
"""P675: the new pause icon, and Whisper's cards actually hide.

── THE PAUSE ──
Denis added pause_new.png (92x94, full-bleed). The button's box still carried
the OLD icon's 129/150 aspect - a near-square image in a tall box paints with
letterboxing, which is the misalignment Denis is seeing. The optimized webp is
in place (3KB via the established browser-encoder pipeline); the box takes the
new image's own ratio.

── WHISPER'S TELL ──
Denis: "fix Whisper's tell so their card are hidden yes."
old_roads (mechanic 'hidden_cards', eff "Cards hidden until triggered") only
ever hid the mid-match loadout panel; the table bar always showed every card
face-up - true of the old .mcard bar and inherited by P670's fold. Now:

  - famRenderRow bakes a hidden npc card as a face-down .fcv: the CARD_BG
    cover mechanism from P670 with a night-blue back and no art img at all -
    reusing the fallback face rather than inventing a back system.
  - "until triggered" gets its second half: triggerCard marks the card
    revealed (G._npcRevealed) and re-renders the row BEFORE locating its
    flash target, so the reveal and the pulse land on the same element the
    player is looking at.
  - npcOppTap on a hidden card says so instead of reading the rules out.
  - _npcRevealed rides the famState snapshot, because a reveal that a reload
    un-reveals is the resume trap the memory file warns about.

The loadout panel's own gate is untouched - same rule, second surface.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the pause icon ───────────────────────────────────────────────────
sub(u'<div id="matchPause" onclick="SFX.nav();showQuitConfirm()"><img src="Art/Assets/Match/optimized/pause_opt.webp" alt="pause"></div>',
    u'<div id="matchPause" onclick="SFX.nav();showQuitConfirm()"><img src="Art/Assets/Match/optimized/pause_new_opt.webp" alt="pause"></div>',
    'P675 the new icon')

sub(u"  width:9.5cqw;height:auto;aspect-ratio:129/150;z-index:21;cursor:pointer;transition:transform .1s}",
    u"  /* P675: the NEW icon's own ratio (92x94, full-bleed) - the old 129/150 box\n"
    u"     letterboxed a near-square image, which read as misalignment */\n"
    u"  width:9.5cqw;height:auto;aspect-ratio:92/94;z-index:21;cursor:pointer;transition:transform .1s}",
    'P675 the box takes its ratio')

# ── 2. whisper's cards hide ─────────────────────────────────────────────
sub(u"function _npcCardSpent(cid){",
    u"/* P675: IS THE RIVAL'S HAND HIDDEN? Whisper's old_roads ('hidden_cards',\n"
    u"   eff \"Cards hidden until triggered\") only ever gated the loadout panel;\n"
    u"   the table bar showed everything face-up - before AND after the P670 fold.\n"
    u"   One question, asked by the row bake, the tap, and the reveal. */\n"
    u"function _npcHandHidden(){\n"
    u"  try{return !!(G&&G.oCards&&G.oCards.some(function(cid){\n"
    u"    var c=getNpcCard(cid);return c&&c.effect&&c.effect.mechanic==='hidden_cards';}));\n"
    u"  }catch(e){return false;}\n"
    u"}\n"
    u"function _npcCardRevealed(cid){return !!(G&&G._npcRevealed&&G._npcRevealed[cid]);}\n"
    u"function _npcCardSpent(cid){",
    'P675 the hidden question')

sub(u"  (G&&G.oCards||[]).forEach(function(cid){\n"
    u"    ho+=famCardArt(cid,1,{cls:'oppcard npccard'+(_npcCardSpent(cid)?' spent':''),\n"
    u"                          onclick:\"npcOppTap('\"+cid+\"')\"});\n"
    u"  });",
    u"  var _oHid=_npcHandHidden();\n"
    u"  (G&&G.oCards||[]).forEach(function(cid){\n"
    u"    if(_oHid&&!_npcCardRevealed(cid)){\n"
    u"      /* P675: FACE DOWN. The P670 cover face, worn as a back: night-blue,\n"
    u"         no art img at all - not display:none over a real face, so nothing\n"
    u"         can un-hide it by accident. Revealed cards fall through to the\n"
    u"         normal face below. */\n"
    u"      ho+='<div class=\"fcv oppcard npccard facedown\" data-cid=\"'+cid+'\"'\n"
    u"        +' onclick=\"npcOppTap('+String.fromCharCode(39)+cid+String.fromCharCode(39)+')\">'\n"
    u"        +'<div class=\"fcvIn\"><div class=\"fcvCover\" style=\"background:#1c2233\">?</div></div></div>';\n"
    u"      return;\n"
    u"    }\n"
    u"    ho+=famCardArt(cid,1,{cls:'oppcard npccard'+(_npcCardSpent(cid)?' spent':''),\n"
    u"                          onclick:\"npcOppTap('\"+cid+\"')\"});\n"
    u"  });",
    'P675 the row bakes face-down')

sub(u"  var spent=_npcCardSpent(cid);\n"
    u"  /* P672: grow-and-read, like every other card at the table */\n"
    u"  _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"    title:c.name,\n"
    u"    sub:spent?'spent — used up for this match':'their card',\n"
    u"    body:(c.desc||_sentenceCase(c.eff||'')),below:true});\n"
    u"}",
    u"  var spent=_npcCardSpent(cid);\n"
    u"  /* P675: a hidden card does not read its rules out */\n"
    u"  if(_npcHandHidden()&&!_npcCardRevealed(cid)){\n"
    u"    _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"      title:'HIDDEN',sub:'their card',\n"
    u"      body:'Whisper keeps it face down. It shows itself when it fires.',below:true});\n"
    u"    return;\n"
    u"  }\n"
    u"  /* P672: grow-and-read, like every other card at the table */\n"
    u"  _cardFocusToggle(document.querySelector('#famRowO .fcv[data-cid=\"'+cid+'\"]'),{\n"
    u"    title:c.name,\n"
    u"    sub:spent?'spent — used up for this match':'their card',\n"
    u"    body:(c.desc||_sentenceCase(c.eff||'')),below:true});\n"
    u"}",
    'P675 the hidden tap')

sub(u"  const row=document.getElementById(isPlayer?'famRowP':'famRowO');\n"
    u"  const fcv=(!mc&&row)?row.querySelector('.fcv[data-cid=\"'+cardId+'\"]'):null;",
    u"  /* P675: \"until triggered\", second half. Firing reveals the card: mark it,\n"
    u"     rebuild the row so the face is up, THEN locate the flash target - the\n"
    u"     order matters, or the pulse lands on the discarded face-down element. */\n"
    u"  if(!isPlayer&&typeof _npcHandHidden==='function'&&_npcHandHidden()&&!_npcCardRevealed(cardId)\n"
    u"     &&G&&(G.oCards||[]).indexOf(cardId)>=0){\n"
    u"    (G._npcRevealed=G._npcRevealed||{})[cardId]=true;\n"
    u"    try{famRenderRow();}catch(e){}\n"
    u"  }\n"
    u"  const row=document.getElementById(isPlayer?'famRowP':'famRowO');\n"
    u"  const fcv=(!mc&&row)?row.querySelector('.fcv[data-cid=\"'+cardId+'\"]'):null;",
    'P675 firing reveals')

# ── the reveal survives a reload ────────────────────────────────────────
sub(u"  oF:G.oF?JSON.parse(JSON.stringify(G.oF)):null,",
    u"  oF:G.oF?JSON.parse(JSON.stringify(G.oF)):null,\n"
    u"  /* P675: a reveal a reload un-reveals is the resume trap - carried with\n"
    u"     the same snapshot the hands ride */\n"
    u"  npcRev:G._npcRevealed?JSON.parse(JSON.stringify(G._npcRevealed)):null,",
    'P675 snapshot the reveals')

sub(u"  if(Array.isArray(_rdFam.oF))G.oF=JSON.parse(JSON.stringify(_rdFam.oF));",
    u"  if(Array.isArray(_rdFam.oF))G.oF=JSON.parse(JSON.stringify(_rdFam.oF));\n"
    u"  if(_rdFam.npcRev)G._npcRevealed=JSON.parse(JSON.stringify(_rdFam.npcRev));/* P675 */",
    'P675 restore the reveals')

# ── the face-down look ──────────────────────────────────────────────────
sub(u"/* P670: spent npc card, same statement as the player row's spent family\n",
    u"/* P675: the face-down back - the cover IS the face here, so it centres its\n"
    u"   glyph large and dim. Slightly darker than the row's live cards. */\n"
    u"#screen-match #famRowO .fcv.facedown .fcvCover{color:rgba(190,200,230,.5);\n"
    u"  font-size:6cqw;font-family:'JMH Beda',serif}\n"
    u"#screen-match #famRowO .fcv.facedown{filter:brightness(.62) saturate(.7)\n"
    u"         drop-shadow(0 0.2cqw 0.3cqw rgba(10,6,2,.55))\n"
    u"         drop-shadow(0 0.9cqw 1.4cqw rgba(10,6,2,.5))}\n"
    u"/* P670: spent npc card, same statement as the player row's spent family\n",
    'P675 the face-down look')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
