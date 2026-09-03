# -*- coding: utf-8 -*-
u"""P935 (brief 3.10 + 3.11): the sim stops rolling past a won match, and the
store is actually sorted by price.

3.10 - THE SIM WAS MODELLING A MISTAKE, NOT A PERSONA. simTurn had the hot-dice
reset ABOVE the target check and `continue`d past it:

    if(!left.length){mats=dice6.slice();if(pushHot&&turn<3000)continue;}
    else mats=left;
    if((myTotal+turn+bankAdd)>=target)return bank();

So a pushHot policy that cleared the table rolled straight past a winning total.
_handBackOrCap ends the match the moment pPts>=target, which means those extra
rolls could only ever LOSE a match already won. No player does that, and `hot`
and `push750` are PLAYER policies - the sim was giving the player a mistake and
calling it a strategy. The browser driver already had the two rules in the
opposite order, so the two engines were never running the same policy.

RULED BY DENIS: fix the sim. The target check is hoisted above the hot-dice
block, where the driver has always had it.

EVERY STORED SIM FINDING INVOLVING hot OR push750 IS NOW RE-DERIVE-REQUIRED.
That is unconditional and would have held whichever way the ruling went: if the
orders differ, the two engines were not measuring the same policy, so any
comparison between them was invalid before this patch and any sim-only number
for those two policies was measured on a mistake.

3.11 - THE STORE IS SORTED BY PRICE, which its own comment already claimed. It
read bone 0, flint 150, iron 100, lead 200, amber 180, silver 120 ... - flint
before iron, lead before amber - under a note saying it was "re-sorted after Lead
so the store stays cheap->expensive". The claim was false before silver moved and
is simply made true here. Sorting is done by parsing the array and reordering
whole entries WITH their comments, rather than by hand-moving lines, so a comment
cannot be separated from the row it describes.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []
NL = '\r\n' if '\r\n' in s[:20000] else '\n'


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


# ── 3.10: the target check goes above the hot-dice reset ────────────
sub(u"""      if(!left.length){mats=dice6.slice();if(pushHot&&turn<3000)continue;}
      else mats=left;
      if((myTotal+turn+bankAdd)>=target)return bank();""",
    u"""      /* P935 (brief 3.10): THE TARGET CHECK COMES FIRST. It used to sit BELOW
         the hot-dice reset, and that reset `continue`s - so a pushHot policy
         that cleared the table rolled straight past a winning total.
         _handBackOrCap ends the match the moment pPts>=target, so those extra
         rolls could only lose a match already won. No player does that, and
         `hot` and `push750` are PLAYER policies, so the sim was modelling a
         mistake rather than a persona. The browser driver has always had the
         two in this order, which means the two engines were not running the
         same policy - every stored sim finding involving those two policies
         needs re-deriving. */
      if((myTotal+turn+bankAdd)>=target)return bank();
      if(!left.length){mats=dice6.slice();if(pushHot&&turn<3000)continue;}
      else mats=left;""",
    '1 (3.10) the sim banks a won match')

# ── 3.11: sort the store by price, entries with their comments ──────
_start = s.index('var DICE_STORE=[')
_bodyStart = s.index('[', _start) + 1
_end = s.index('\n];', _bodyStart)
body = s[_bodyStart:_end]

# split into chunks: any run of comment/blank lines followed by one row line
lines = body.split('\n')
chunks, pending = [], []
for ln in lines:
    m = re.match(r"\s*\{mat:'(\w+)',\s*price:(\d+),", ln)
    pending.append(ln)
    if m:
        chunks.append({'mat': m.group(1), 'price': int(m.group(2)),
                       'lines': pending})
        pending = []
tail = pending  # anything after the last row (should be empty/whitespace)

if len(chunks) != 11:
    sys.exit('parsed %d store rows, expected 11 (nothing written)' % len(chunks))

before_order = [(c['mat'], c['price']) for c in chunks]
chunks.sort(key=lambda c: (c['price'], c['mat']))
after_order = [(c['mat'], c['price']) for c in chunks]

newBody = '\n'.join(sum([c['lines'] for c in chunks], []) + tail)
s = s[:_bodyStart] + newBody + s[_end:]
edits.append('2 (3.11) the store is sorted by price')

# the amber note claimed a sort that was not happening; make it true
sub(u"""  /* Amber 120\u2192180 to match DICE_TYPES.cost (and the +200 triple buff).
     Re-sorted after Lead so the store stays cheap\u2192expensive. */""",
    u"""  /* Amber 120\u2192180 to match DICE_TYPES.cost (and the +200 triple buff).
     P935 (brief 3.11): the store is now genuinely sorted by price. This note
     used to say Amber had been "re-sorted after Lead so the store stays
     cheap\u2192expensive", which put 180 after 200 and was self-contradicting -
     flint 150 also sat before iron 100. The order is generated from the prices
     now rather than maintained by hand. */""",
    '3 the sort note is made true')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# 3.10: exactly one target check, and it precedes the hot-dice reset
_sim = code.index('function simTurn(')
_seg = code[_sim:code.index('function playerTurn(', _sim)]
if _seg.count('if((myTotal+turn+bankAdd)>=target)return bank();') != 1:
    sys.exit('simTurn has %d target checks, expected 1 (nothing written)'
             % _seg.count('if((myTotal+turn+bankAdd)>=target)return bank();'))
if _seg.index('if((myTotal+turn+bankAdd)>=target)return bank();') > \
   _seg.index('if(!left.length){mats=dice6.slice();'):
    sys.exit('the target check still sits below the hot-dice reset (nothing written)')
# the oppDone check and bankFn are untouched and still below it
for need in ('if(oppDone){', 'else if(bankFn(turn,mats.length))return bank();'):
    if need not in _seg:
        sys.exit('%s was disturbed in simTurn (nothing written)' % need)

# 3.11: the store is sorted, and no row was lost or duplicated
prices = [int(m.group(1)) for m in
          re.finditer(r"\{mat:'\w+',\s*price:(\d+),", code[code.index('var DICE_STORE=['):
                                                          code.index('var DICE_STORE=[') + 4000])]
if prices != sorted(prices):
    sys.exit('the store is not in price order: %s (nothing written)' % prices)
if sorted(before_order) != sorted(after_order):
    sys.exit('a store row changed during the sort (nothing written)')
if len(prices) != 11:
    sys.exit('the sorted store has %d rows, expected 11 (nothing written)' % len(prices))
# and the rows kept their own comments - silver's placeholder note must still sit
# with silver, not have drifted onto whatever row took its old position
# matched on the patch id, not on a word from the prose - the first version
# looked for lowercase 'blind' against text that reads "IS BLIND", which is the
# same case-blindness that makes a string search a poor proxy for a thing
_sIdx = s.index("{mat:'silver'")
if 'P931 (brief 3.9' not in s[max(0, _sIdx - 2000):_sIdx]:
    sys.exit("silver's placeholder comment did not travel with it (nothing written)")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
print('store order before: %s' % [m for m, p in before_order])
print('store order after : %s' % [m for m, p in after_order])
