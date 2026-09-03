# -*- coding: utf-8 -*-
u"""P939: silver's price had THREE homes and P931 moved one of them.

THE FILE SAID SO, TWO LINES ABOVE THE ONE I MISSED:

  /* P892: silver 580 -> 320 here too. Three places hold this price - the
     shop row, the die def and this table - and they have to move together. */
  var FAM_PRICE={amber:180,obsidian:500,silver:320,...};

P931 changed the shop row to 120 and left the other two at 320. So the shop sold
silver at 120 while the die def and the economy model both priced it at 320 - and
my dependency check for that patch found the stock consumer and missed the price
table the file explicitly points at. The neighbours had written it down.

AND THE DIE DEF IS NOT COSMETIC. dieRank() is `getDie(id).cost`, and Fair Trade
compares dieRank to decide whether a borrowed die is an upgrade. At cost 320
silver outranked lead (200), amber (180) and flint (150); at 120 it ranks just
above iron. That is a real behaviour change, and it is the RIGHT one - the whole
basis of the 120 ruling is that silver measures as parity with iron, so a rank
that placed it above lead was asserting a quality the measurement denies.

ONE HOME IS COLLAPSED RATHER THAN SYNCHRONISED. FAM_PRICE was DICE_STORE's
prices retyped - every other entry matches exactly - so it is derived from
DICE_STORE instead. Two homes left, and they hold different things: a shop row
(price, stock, label) and a die definition (faces, effect, cost). Collapsing
those is a larger refactor than a price ruling should carry, so instead
zv_price_homes.js asserts they agree, and will fail the day one moves alone.

THE LADDER IS RUNNING AGAINST THIS FILE. ladder_band.js extracts gearLevel and
`var FAMS=[...]` from _runEconomySim.toString(); neither is touched, and the
ladder never calls _runEconomySim itself. The parse gate covers the rest.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the die def ──────────────────────────────────────────────────
sub(u"""  {id:'silver',name:'SILVER',icon:'\U0001f518',cost:320,""",
    u"""  /* P939 (brief 3.9): cost 320 -> 120, with the shop row. This is NOT
     cosmetic - dieRank() is getDie(id).cost and Fair Trade ranks by it, so at
     320 silver outranked lead, amber and flint. At 120 it ranks just above
     iron, which is what the measurement says it is worth. */
  {id:'silver',name:'SILVER',icon:'\U0001f518',cost:120,""",
    '1 the die def')

# ── 2. the model's table is derived, not retyped ────────────────────
sub(u"""  /* P892: silver 580 -> 320 here too. Three places hold this price - the
     shop row, the die def and this table - and they have to move together. */
  var FAM_PRICE={amber:180,obsidian:500,silver:320,starstone:700,vagabond:700,jade:750,jade2:1800};""",
    u"""  /* P939: DERIVED FROM THE SHOP, not retyped from it. P892's note here said
     "three places hold this price - the shop row, the die def and this table -
     and they have to move together", and then P931 moved the shop row to 120
     and left this at 320. A note asking future authors to keep three copies in
     step is the thing that fails; this table was DICE_STORE's prices written
     out a second time, every entry identical, so it reads them instead.
     Two homes are left and they hold different things - a shop row is price,
     stock and label, a die definition is faces, effect and cost - so
     tools/zv_price_homes.js asserts the two agree rather than pretending one
     can be deleted. */
  var FAM_PRICE=(function(){
    var o={};
    try{(typeof DICE_STORE!=='undefined'?DICE_STORE:[]).forEach(function(d){
      if(d&&d.mat)o[d.mat]=d.price;});}catch(e){}
    return o;
  })();""",
    '2 the model derives its prices')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# no 320 survives for silver anywhere
if re.search(r"silver[^\n]{0,40}320", code) or re.search(r"320[^\n]{0,40}silver", code):
    sys.exit('a silver price of 320 survives (nothing written)')
# the die def is 120, once
if code.count("{id:'silver',name:'SILVER',icon:'\U0001f518',cost:120,") != 1:
    sys.exit('the die def is not cost 120 exactly once (nothing written)')
# the shop row is still 120
if code.count("{mat:'silver',   price:120, stock:3, label:'Silver'}") != 1:
    sys.exit('the shop row changed (nothing written)')
# FAM_PRICE is derived and holds no literals
_fp = code.index('var FAM_PRICE=')
_seg = code[_fp:_fp + 300]
if re.search(r'\b(amber|silver|obsidian|starstone|jade)\s*:', _seg):
    sys.exit('FAM_PRICE still holds price literals (nothing written)')
if 'DICE_STORE' not in _seg:
    sys.exit('FAM_PRICE does not read DICE_STORE (nothing written)')
# THE LADDER IS RUNNING AGAINST THIS FILE - its two extractions must survive
_sim = code.index('function _runEconomySim(')
_simSrc = code[_sim:_sim + 12000]
if not re.search(r'function gearLevel\(fam\)\{', _simSrc):
    sys.exit('gearLevel no longer matches the ladder extraction (nothing written)')
if not re.search(r'var FAMS=\[[^\]]*\];', _simSrc):
    sys.exit('FAMS no longer matches the ladder extraction (nothing written)')
# dieRank still reads cost - the consumer this change is about
if code.count('function dieRank(id){var dt=getDie(id);return dt?dt.cost:0;}') != 1:
    sys.exit('dieRank changed (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
