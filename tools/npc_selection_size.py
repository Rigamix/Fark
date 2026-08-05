# -*- coding: utf-8 -*-
u"""Sizing: real NPC dice selection, `commit`, and opponent-side enchants.

RULED: NPCs should make real dice selections the way a player does - actually
choosing which dice, forming an actual triple or straight - rather than
computing an abstracted optimal total and skipping to the result. Once true,
`commit`'s payload stops being an open design question because the data exists
in the same shape the player's own commit produces.

FOUR QUESTIONS, and only measurement answers any of them:

  1. What does real NPC selection MINIMALLY require - can it reuse the player's
     own selection-evaluation path, or is that path welded to the UI?
  2. Does that naturally produce commit's payload (sel, isTriple, isStraight,
     jade, hitFirst, hitLast), or is there a gap once it is actually read?
  3. Where do opponent-side enchants sit - before, after, or parallel?
  4. What is the smallest real slice of hesitation/timing levers, given the
     persona / dieBias / behavior structure already exists?

THE TRAP THIS PASS IS BUILT TO AVOID: assuming the NPC "just needs to call what
the player calls". If the player's selection logic reads the DOM, mutates
element state, or depends on a tap having happened, then reusing it is not a
call - it is an extraction, and that is a different size of job. So this
measures how UI-bound each candidate function is, rather than whether it exists.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def body_of(name):
    for m in re.finditer(r'\bfunction\s+' + re.escape(name) + r'\s*\(', s):
        b = s.index('{', m.end() - 1)
        d, j = 0, b
        while j < len(s):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    return s[b:j + 1]
            j += 1
    return None

UI = re.compile(r'document\.|querySelector|getElementById|classList|\.style\b|innerHTML|'
                r'addEventListener|\.el\b|spawnPop|triggerCard|setStatusMsg|D3\.|SFX\.|Haptic\.')

print('=== Q1: how UI-bound is each candidate the NPC would reuse? ===')
print('%-22s %-7s %-7s %-6s %s' % ('function', 'lines', 'UI hits', 'DOM?', 'verdict'))
print('-' * 76)
CAND = ['scoreRoll', 'scoreSelection', 'anyScoring', 'legalKeeps', 'allScorers',
        'handleScore', 'famCommitBonus', 'oppShouldBank', 'dieRank']
for fn in CAND:
    b = body_of(fn)
    if b is None:
        print('%-22s %s' % (fn, 'not a top-level function'))
        continue
    lines = b.count('\n') + 1
    hits = len(UI.findall(b))
    dom = 'yes' if re.search(r'document\.|querySelector|getElementById', b) else 'no'
    verdict = ('PURE - callable as-is' if hits == 0 else
               ('mostly pure - %d presentation calls' % hits if hits <= 4 else
                'UI-BOUND - extraction, not a call'))
    print('%-22s %-7d %-7d %-6s %s' % (fn, lines, hits, dom, verdict))

print('\n=== Q2: does commit\'s payload exist outside the player\'s tap path? ===')
cev = re.search(r"famFire\('commit',\s*(\w+)", s)
if cev:
    var = cev.group(1)
    dm = re.search(r'(?:var|let|const)\s+' + var + r'\s*=\s*\{([^}]*)\}', s)
    fields = re.findall(r'(\w+)\s*:', dm.group(1)) if dm else []
    print('  payload fields:', ', '.join(fields))
    for f in fields:
        if f == 'actor':
            continue
        src = dm.group(1)
        val = re.search(f + r'\s*:\s*([A-Za-z_$][\w$]*)', src)
        v = val.group(1) if val else '?'
        # where does that local come from?
        decl = re.search(r'(?:var|let|const)\s+' + re.escape(v) + r'\s*=\s*([^;\n]{0,70})', s)
        print('    %-12s <- %-14s %s' % (f, v, (decl.group(1).strip()[:52] if decl else 'no local decl found')))

print('\n=== Q3: opponent-side enchants - what exists already? ===')
for label, pat in [('enchant defs', r'ENCH(?:ANTS)?\s*=\s*\{|mkEnch\s*\('),
                   ('player ench array', r'_enchArr'),
                   ('opp ench array', r'_oppEnchArr|matchOppEnch'),
                   ('ench applied in scoring', r'dieEnchs'),
                   ('_lm* lane markers', r'_lmArm\s*\(')]:
    print('  %-24s %d' % (label, len(re.findall(pat, s))))

print('\n=== Q4: the persona / bias structure the levers would hang on ===')
for label, pat in [('rung.agg', r'\.agg\b'), ('rung.chaotic', r'\.chaotic\b'),
                   ('rung.adaptive', r'\.adaptive\b'), ('rung.minBank', r'\.minBank\b'),
                   ('rung.diceStop', r'\.diceStop\b'), ('dieBias', r'dieBias'),
                   ('behavior', r'\bbehavior\b'), ('persona', r'\bpersona\b')]:
    print('  %-24s %d' % (label, len(re.findall(pat, s))))
