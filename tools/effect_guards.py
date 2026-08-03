# -*- coding: utf-8 -*-
"""EFFECT PHASE 2, step one — what do the handlers actually guard on?

famFire dispatches and checks nothing. Every CFX handler opens with its own
hand-written guard, and that is where Vagabond's stale read, Starstone's wrong
gate and Still Waters' wrong field all lived. So the shared condition layer's
vocabulary has to be read OUT of those guards, not designed first and fitted
after.

This pulls every `CFX.<id> = { <hook>: function(ev){ ... } }` body out of the
source and reports the guard clauses - the early-return tests each one performs
before doing any work. Read from source rather than the live page because CFX
handler bodies are function objects: toString gives the text back, but the
mapping from id+hook to text is cleaner to take from the file.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# every `CFX.<id>={ ... };` block
blocks = {}
for m in re.finditer(r'\nCFX\.([a-z0-9_]+)\s*=\s*\{', s):
    cid = m.group(1)
    i = m.end() - 1
    depth, j = 0, i
    while j < len(s):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    blocks[cid] = s[i:j + 1]

HOOKS = ['canUse', 'use', 'roll', 'bank', 'bankBonus', 'turnStart', 'bust']
rows, guards = [], collections.Counter()

for cid, body in sorted(blocks.items()):
    for hook in HOOKS:
        hm = re.search(r'\b' + hook + r'\s*:\s*function\s*\(([^)]*)\)\s*\{', body)
        if not hm: continue
        k = hm.end() - 1
        depth, e = 0, k
        while e < len(body):
            if body[e] == '{': depth += 1
            elif body[e] == '}':
                depth -= 1
                if depth == 0: break
            e += 1
        fn = body[k:e + 1]
        # the guard clauses: every `if(...)return` before real work
        gs = re.findall(r'if\s*\(([^;{]*?)\)\s*return', fn)
        gs = [re.sub(r'\s+', '', g) for g in gs]
        rows.append((cid, hook, gs))
        for g in gs:
            # normalise to the CONDITION being asked, not the exact spelling
            for token, label in [
                ('!ev.mine', 'is this MINE (ev.mine)'),
                ("ev.owner!=='p'", "am I the PLAYER (ev.owner)"),
                ("ev.owner==='o'", "am I the PLAYER (ev.owner)"),
                ("G.phase==='opp'", 'is it the OPPONENT phase'),
                ("G.phase!=='choosing'", 'is the phase right'),
                ("G.phase!=='opp'", 'is the phase right'),
                ('!G', 'does G exist'),
                ('inst.state', 'per-card STATE'),
                ('c.turnPts', 'turn points threshold'),
                ('ev.amt', 'bank amount threshold'),
                ('G.turnRollCount', 'roll count threshold'),
            ]:
                if token in g:
                    guards[label] += 1
                    break
            else:
                guards['(other) ' + g[:44]] += 1

print('CFX handlers with guards: %d hooks across %d cards\n' % (len(rows), len(blocks)))
print('%-18s %-11s %s' % ('card', 'hook', 'guard clauses'))
for cid, hook, gs in rows:
    print('%-18s %-11s %s' % (cid, hook, ' | '.join(gs)[:76] if gs else '(none)'))

print('\n\nTHE VOCABULARY, BY HOW OFTEN THE CONTENT ASKS FOR IT')
for label, n in guards.most_common():
    print('  %-42s %d' % (label, n))

noguard = [(c, h) for c, h, g in rows if not g]
print('\nhandlers with NO guard at all: %d  %s' % (len(noguard), noguard[:8]))
