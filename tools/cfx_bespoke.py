# -*- coding: utf-8 -*-
"""Phase 4 group 1 - are the 20 cards on CFX ACTUALLY on it, or half-on?

"On the bus" was measured by asking CFX which ids it holds. That answers "does
an entry exist", not the question Phase 4 needs: is the entry where the card's
behaviour LIVES. A card can have a CFX entry AND bespoke logic elsewhere, and
that combination is the worst available - the entry makes the card look
migrated, so a later change goes into CFX while the bespoke half keeps doing the
old thing.

THE FIRST VERSION OF THIS FLAGGED 18 OF THE 20 AND WAS ALMOST ENTIRELY WRONG.
Three artifact classes, all of them mine, each caught by reading the flagged
lines instead of the summary:

  1. `\bpreserve\b` MATCHES INSIDE `preserve-3d`. A hyphen is a word boundary,
     so the Preserve card "had 15 bespoke sites", all of them CSS transform
     declarations. Any id that is also an English word hits this.
  2. PROSE IN /* */ COMMENTS fell through to CODE. The classifier treated
     QUOTED strings as strings, so a comment saying "POWDER KEG, ENCORE and
     STEADY HAND were taught this" counted as three implementations.
  3. THE SIM HARNESS IS A SECOND IMPLEMENTATION ON PURPOSE. FSIM re-implements
     scoring so it can run thousands of matches headless; `cs.ids.slow_cook`
     there is the simulator modelling the card, not the game duplicating it.
     Counting it as drift would have condemned the thing that MEASURES drift.

That is the fifth instrument-manufactured finding today and they all ran the
same direction - more findings than were real. Reported here rather than
quietly fixed, because the pattern is the point: an instrument that invents
work is more expensive than one that misses it, since nothing prompts you to
re-check a finding you already believe.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
raw = io.open(SRC, encoding='utf-8').read()

ON_BUS = ['transmute', 'fools_gold_f', 'preserve', 'honeytrap', 'slow_cook',
          'steady_hand', 'retort', 'reprisal', 'fair_trade', 'powder_keg',
          'double_or_nothing', 'sacrifice', 'short_fuse', 'encore', 'stargazer',
          'ill_omen', 'falling_star', 'sleight', 'pickpocket', 'tamper']

# ── 1. blank out /* */ comments, keeping line numbers intact ──
def blank_comments(t):
    out = list(t)
    for m in re.finditer(r'/\*.*?\*/', t, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != '\n':
                out[i] = ' '
    return ''.join(out)

# ── 2. blank out the sim harness, same way ──
SIM_START = raw.find('BALANCE SIM HARNESS')
assert SIM_START > 0, 'sim harness banner not found - has it moved?'
sim_line = raw[:SIM_START].count('\n') + 1

s = blank_comments(raw)
s = s[:SIM_START] + re.sub(r'[^\n]', ' ', s[SIM_START:])
print('comments blanked; sim harness blanked from line %d to EOF\n' % sim_line)

def cfx_block(cid):
    for pat in (r'CFX\.' + re.escape(cid) + r'\s*=\s*\{',
                r'CFX\[' + re.escape("'" + cid + "'") + r'\]\s*=\s*\{',
                r'\b' + re.escape(cid) + r'\s*:\s*\{'):
        m = re.search(pat, s)
        if not m:
            continue
        b = s.index('{', m.end() - 1)
        d, j = 0, b
        while j < len(s):
            if s[j] == '{': d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    return (m.start(), j + 1)
            j += 1
    return None

# ── 3. the id, NOT followed by a hyphen (preserve-3d) or preceded by one ──
def mentions(text, cid):
    return [m.start() for m in
            re.finditer(r'(?<![\w-])' + re.escape(cid) + r'(?![\w-])', text)]

print('%-18s %-8s %s' % ('card', 'outside', 'classification'))
print('-' * 74)
suspect = []
for cid in ON_BUS:
    blk = cfx_block(cid)
    rest = (s[:blk[0]] + re.sub(r'[^\n]', ' ', s[blk[0]:blk[1]]) + s[blk[1]:]
            if blk else s)
    kinds = {'definition': 0, 'live-table': 0, 'string': 0,
             'opponent': 0, 'collision': 0, 'CODE': 0}
    code_lines = []
    for h in mentions(rest, cid):
        ls = rest.rfind('\n', 0, h) + 1
        le = rest.find('\n', h)
        line = rest[ls:le if le > 0 else len(rest)]
        if ("{id:'" + cid + "'") in line:
            kinds['definition'] += 1
        # the live table's THIRD form: an array of quoted ids fed to a forEach.
        # Quoted, so the identifier rule below would call it code; it is a
        # registration list, not an implementation.
        elif 'FAM_LIVE' in line:
            kinds['live-table'] += 1
        # THE LIVE TABLE IS WRITTEN TWO WAYS. Most ids arrive through an array
        # forEach or an object literal (`tamper:1`); three are set as
        # properties (`FAM_LIVE.tamper=1;/* P5: opponent cards visible */`).
        # Only knowing the literal form left tamper as the last "half-on" card
        # in the report - one survivor out of an original eighteen, which is
        # exactly when a wrong finding is most believable.
        elif re.search(r'(?<![\w-])' + re.escape(cid) + r"\s*:\s*1\b", line) \
                or re.search(r'FAM_LIVE\.' + re.escape(cid) + r'\s*=\s*1\b', line):
            kinds['live-table'] += 1
        # A QUOTED ID IS NOT AUTOMATICALLY A LOG STRING, and treating it as one
        # is how this tool reported "group 1 is clean" when it is not.
        # `famInst('short_fuse')` is a LOOKUP - the id is an argument, the line
        # is code, and short_fuse duplicating its x2 inside famCommitBonus while
        # also sitting on CFX is exactly the half-on case this file exists to
        # find. The seventh artifact of the day and the first FALSE NEGATIVE:
        # the other six invented work, this one hid it, which is worse here
        # because a clean result ends the investigation.
        #
        # THE OPPONENT SIDE IS A SEPARATE IMPLEMENTATION BY DESIGN, not drift.
        # _npcFamCard is how the NPC reads family cards, and PROTO_NOTES has NPC
        # usage landing in P5 with G.oF deliberately empty until then. Counting
        # it as half-on would condemn a split the plan chose.
        elif '_npcFamCard' in line:
            kinds['opponent'] += 1
        # NAME COLLISIONS. `pickpocket` is BOTH a vagabond card and a
        # sealed-seat table rule in _SEAL_POOL - unrelated things sharing a
        # string. The same trap the Ward audit fell into one level up, where a
        # shared PREFIX was read as a shared feature.
        elif '_SEAL_POOL' in line or 'tell:{id:' in line:
            kinds['collision'] += 1
        # THE TEST IS WHETHER THE LITERAL *IS* THE ID. 'short_fuse' on its own
        # is an identifier being passed; 'x2 SHORT FUSE' or 'THE SNARE BITES'
        # is prose that happens to contain it.
        elif re.search(r"['\"]" + re.escape(cid) + r"['\"]", line):
            kinds['CODE'] += 1
            code_lines.append(rest[:h].count('\n') + 1)
        elif re.search(r"['\"][^'\"]*(?<![\w-])" + re.escape(cid) + r"(?![\w-])[^'\"]*['\"]", line):
            kinds['string'] += 1
        else:
            kinds['CODE'] += 1
            code_lines.append(rest[:h].count('\n') + 1)
    print('%-18s %-8d %s' % (cid, sum(kinds.values()),
          ', '.join('%s %d' % (k, v) for k, v in kinds.items() if v) or '-'))
    if kinds['CODE']:
        suspect.append((cid, kinds['CODE'], code_lines[:8]))

print('\n' + '=' * 74)
if not suspect:
    print('CLEAN after separating opponent-side and name-collision sites.')
else:
    print('CODE outside the CFX entry - real source lines, comments and sim')
    print('excluded. A mention is still only somewhere to LOOK:')
    for cid, n, lines in suspect:
        print('  %-18s %2d  lines %s' % (cid, n, lines))
