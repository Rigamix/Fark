# -*- coding: utf-8 -*-
"""P669: the in-match line stops being cropped, and Last Call stops overwriting
its own refusal.

Denis: "the text that appears to tell me what my cards do is too big and cropped
out. This text should also be part of the audit for card and dice, enchant
effects. It should all follow the same pipeline... When I can't bank for example
in a grog match because my score ain't high enough there should be a text that
tells me so."

── 1. THE CROP ──
.status-msg is `white-space:nowrap` and sits in a centred flex strip with no
min-width, so a message wider than the strip cannot wrap AND cannot shrink - it
just grows past both edges at once. Centred, it loses the beginning and the end
together, which is why Denis's photo reads "RED — THEIR SHORT FUSE IS BROKEN FOR
THE".

Measured on the real element, real font, in a real match (430px screen, 418px
strip, 21.5px type):

    55 chars   610px wide    90.2px off EACH side
    54 chars   588px          79.2
    51 chars   564px          67.0
    42 chars   462px          16.1
    20 chars   205px          fits

so anything past ~38 characters is cropped. And the corpus is not short: of 181
literal messages handed to famLog/setStatusMsg, 73 are over 26 characters and
the longest is 55 - before counting the concatenated ones like Tamper's 50.

The line wraps now, is held inside the strip, and steps down one size for long
messages so two lines stay comfortable rather than filling the table. The step
is computed in setStatusMsg - ONE place, every caller, no per-message code -
because famLog funnels every card, die, enchant and rule announcement through
setStatusMsg while the match screen is up.

Wrapping is safe in both directions, which is why this is a CSS change and not a
layout one: _placeTurnText anchors the rival's strip by its BOTTOM and the
player's by its TOP, so a second line grows away from the dice on both sides.

── 2. LAST CALL WRITES ITS REFUSAL AND THEN DELETES IT ──
Denis asked for a message when a Grog match refuses a bank. It already exists:

    setStatusMsg('LAST CALL — NOTHING UNDER '+_lcT,'red');

and then, eight lines later and unconditionally,

    const msg='BANKED '+total.toLocaleString()+(bonusMsg||'');
    setStatusMsg(msg,'gold');

Same element. The refusal is on screen for no frames at all, and what the player
actually sees is "BANKED 0" in gold - a success-coloured message for a rejected
bank, which is worse than silence. The refusal now stands, and the BANKED line
is skipped when there was no bank.
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


# ── 1. the line wraps and fits ──────────────────────────────────────────
sub(u"  font-size:5cqw;text-align:center;letter-spacing:.03em;\n"
    u"  white-space:nowrap;color:var(--textdim);opacity:.55;",
    u"  font-size:5cqw;text-align:center;letter-spacing:.03em;\n"
    u"  /* P669: WAS `nowrap`, AND THAT WAS THE CROP. The strip is a centred flex\n"
    u"     box with no min-width, so a line too wide to fit could neither wrap nor\n"
    u"     shrink - it grew past both edges at once and, being centred, lost its\n"
    u"     start and its end together. Measured at 430px: 55 characters rendered\n"
    u"     610px wide and hung 90px off each side; the crop begins around 38.\n"
    u"     max-width and min-width:0 are what actually hold it inside the strip -\n"
    u"     wrapping alone does not, because a flex item will not shrink below its\n"
    u"     content width without them. */\n"
    u"  white-space:normal;max-width:100%;min-width:0;\n"
    u"  overflow-wrap:break-word;text-wrap:balance;\n"
    u"  color:var(--textdim);opacity:.55;",
    'P669 the line wraps')

sub(u".status-msg.active{color:var(--text);opacity:.85}",
    u".status-msg.active{color:var(--text);opacity:.85}\n"
    u"/* P669: and long messages come down a step, so a wrapped line reads as two\n"
    u"   tidy lines rather than filling the table. The class is chosen in\n"
    u"   setStatusMsg from the message length - one place, every caller. The bands\n"
    u"   come from the corpus: the median message is 24 characters and 73 of 181\n"
    u"   are over 26, so the common case keeps the full size. */\n"
    u".status-msg.sm-long{font-size:4.2cqw}\n"
    u".status-msg.sm-xlong{font-size:3.6cqw;letter-spacing:.02em}",
    'P669 the size step')

sub(u"function setStatusMsg(m,c){\n"
    u"  const isOpp=G&&G.phase==='opp';\n"
    u"  const topEl=document.getElementById('statusTop'),botEl=document.getElementById('statusBot');\n"
    u"  if(isOpp){topEl.textContent=m;topEl.className='status-msg '+(c||'');botEl.textContent='';botEl.className='status-msg';}\n"
    u"  else{botEl.textContent=m;botEl.className='status-msg '+(c||'');topEl.textContent='';topEl.className='status-msg';}",
    u"/* P669: THE SIZE STEP LIVES HERE, once, rather than at 105 famLog call sites.\n"
    u"   Every card, die, enchant and rule announcement reaches the table through\n"
    u"   this function while the match screen is up - famLog -> _famAnnounce ->\n"
    u"   setStatusMsg - so this is the one place that sees every message and can\n"
    u"   size it. */\n"
    u"function _statusCls(m,c){\n"
    u"  var n=(m==null?0:String(m).length);\n"
    u"  return 'status-msg '+(c||'')+(n>44?' sm-xlong':(n>26?' sm-long':''));\n"
    u"}\n"
    u"function setStatusMsg(m,c){\n"
    u"  const isOpp=G&&G.phase==='opp';\n"
    u"  const topEl=document.getElementById('statusTop'),botEl=document.getElementById('statusBot');\n"
    u"  if(isOpp){topEl.textContent=m;topEl.className=_statusCls(m,c);botEl.textContent='';botEl.className='status-msg';}\n"
    u"  else{botEl.textContent=m;botEl.className=_statusCls(m,c);topEl.textContent='';topEl.className='status-msg';}",
    'P669 size step at the funnel')

# ── 2. the refusal survives ─────────────────────────────────────────────
# TWO rules refuse a bank, not one. Denis named Grog's; Ambrose's Reckoning has
# the identical shape three lines up and the identical bug. Counted before
# patching, because fixing the reported one and leaving its twin is how the same
# defect gets reported twice.
sub(u"  if(G._tell){\n"
    u"    /* Steeped (Mabel): +50 per roll past first, accumulated in G._tellState.bonus */",
    u"  /* P669: DID THE BANK GET REFUSED? Two house rules below zero a bank and\n"
    u"     announce it in red - Ambrose's Reckoning and Grog's Last Call - and both\n"
    u"     were overwritten unconditionally by the gold 'BANKED 0' line at the end\n"
    u"     of this function: same element, same turn, so the red was on screen for\n"
    u"     no frames at all. What the player saw was a success-coloured message for\n"
    u"     a rejected bank, which is why Denis reported the refusal as missing. */\n"
    u"  var _bankRefused=false;\n"
    u"  if(G._tell){\n"
    u"    /* Steeped (Mabel): +50 per roll past first, accumulated in G._tellState.bonus */",
    'P669 declare the refusal flag')

sub(u"      total=0;bonusMsg=' RECKONING — BANK <'+_rkFloor;\n"
    u"      setStatusMsg(\"RECKONING — BANK BELOW \"+_rkFloor+'!','red');",
    u"      total=0;bonusMsg=' RECKONING — BANK <'+_rkFloor;\n"
    u"      _bankRefused=true;/* P669 - or the gold BANKED line below erases this */\n"
    u"      setStatusMsg(\"RECKONING — BANK BELOW \"+_rkFloor+'!','red');",
    'P669 flag Reckoning')

sub(u"      total=0;bonusMsg=' LAST CALL — BANK <'+_lcT;\n"
    u"      setStatusMsg('LAST CALL — NOTHING UNDER '+_lcT,'red');",
    u"      total=0;bonusMsg=' LAST CALL — BANK <'+_lcT;\n"
    u"      _bankRefused=true;/* P669 - the one Denis reported */\n"
    u"      setStatusMsg('LAST CALL — NOTHING UNDER '+_lcT,'red');",
    'P669 flag Last Call')

sub(u"  const msg='BANKED '+total.toLocaleString()+(bonusMsg||'');setStatusMsg(msg,'gold');",
    u"  /* P669: no gold BANKED line over a refusal - the red one above is the\n"
    u"     message, and it is the only one that is true. */\n"
    u"  if(!_bankRefused){\n"
    u"    const msg='BANKED '+total.toLocaleString()+(bonusMsg||'');setStatusMsg(msg,'gold');\n"
    u"  }",
    'P669 do not clobber it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
