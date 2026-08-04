# -*- coding: utf-8 -*-
"""Is each `mechanic ===` site a DISPATCH or a QUERY? The question I skipped.

FOURTH CORRECTION IN THIS AREA, SAME CATEGORY AS THE OTHER THREE: the tool
measured one property and I read it as a different one. `mechanic_portable.py`
measures WHAT LOCALS A BODY READS. I reported that as "can this become a table
row", which is a different question, and the gap between them is where three of
the five "clean rows" live.

  hidden_cards       G.oCards.some(cid => ... mechanic==='hidden_cards')
  reduce_first_roll  G.oCards.find(cid => ... mechanic==='reduce_first_roll')

Those are not dispatch. They are QUERIES - "does the opponent hold a card with
this mechanic" - and the body inside the callback is just a comparison. So they
score as MAXIMALLY portable (they read nothing) while being the LEAST
table-able sites in the file: there is no effect to put in a row. A table row
needs a behaviour to carry, and a predicate has none.

BREAK_TRIGGERS works because every branch it replaced was a dispatch with a
body. A table cannot replace a `.find()` that is looking something up.

SO THIS CLASSIFIES BY SYNTACTIC POSITION, which is the thing that actually
decides it:

  QUERY     the test sits inside a .find/.some/.filter/.every callback, or is
            assigned to a variable/const - it is ANSWERING something
  DISPATCH  the test is an `if` condition guarding a block that DOES something

Only DISPATCH sites can become table rows. Queries want a different move
entirely - a helper like `_oppHas(mechanic)` - which is worth doing but is not
this refactor and should not be counted as part of it.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def classify(pos):
    """Look backward from the test for what encloses it."""
    head = s[max(0, pos - 260):pos]
    # innermost opener before the test
    if re.search(r'\.(find|some|filter|every|findIndex)\s*\(\s*function\s*\([^)]*\)\s*\{[^{}]*$', head):
        return 'QUERY'
    if re.search(r'\.(find|some|filter|every|findIndex)\s*\(\s*(\w+|\([^)]*\))\s*=>[^{};]*$', head):
        return 'QUERY'
    # `var x = ...cond...` with no `if (` in between
    tail = head[head.rfind(';') + 1:]
    if re.search(r'\b(var|let|const)\s+\w+\s*=', tail) and 'if(' not in tail.replace(' ', ''):
        return 'QUERY'
    if re.search(r'\bif\s*\([^;]*$', head):
        return 'DISPATCH'
    return 'OTHER'

rows = collections.defaultdict(lambda: collections.Counter())
for m in re.finditer(r"mechanic\s*===\s*'([a-z_0-9]+)'", s):
    rows[m.group(1)][classify(m.start())] += 1

CLAIMED = ['hidden_cards', 'reduce_first_roll', 'reroll_all_kept', 'steal_die', 'swap_die']
print('THE FIVE I CALLED "STRAIGHT TABLE ROWS":\n')
print('%-20s %-9s %-9s %s' % ('mechanic', 'dispatch', 'query', 'verdict'))
print('-' * 62)
real = []
for mech in CLAIMED:
    c = rows[mech]
    d, q = c['DISPATCH'], c['QUERY'] + c['OTHER']
    ok = d > 0 and q == 0
    print('%-20s %-9d %-9d %s' % (mech, d, q, 'table row' if ok else 'NOT a table row - it is a lookup'))
    if ok:
        real.append(mech)

tot = collections.Counter()
for c in rows.values():
    tot.update(c)
print('\n' + '=' * 62)
print('WHOLE FILE: %d dispatch, %d query, %d other  (of %d sites)'
      % (tot['DISPATCH'], tot['QUERY'], tot['OTHER'], sum(tot.values())))
print('\nACTUALLY MOVABLE, of the five claimed: %d - %s'
      % (len(real), ', '.join(real) or 'none'))
print("""
The queries are not a smaller version of the same job. They want `_oppHas(mech)`,
a one-line helper, which is worth doing and is NOT this refactor.""")
