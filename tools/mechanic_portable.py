# -*- coding: utf-8 -*-
"""Are the 17 single-site mechanics actually portable? Criterion 2, measured.

THE SCOPE FILE CALLED THEM "STRAIGHT TABLE ROWS" ON THE SITE COUNT ALONE, and
that is the wrong evidence for the claim. A count answers WHERE a mechanic
appears. It says nothing about whether the branch BODY can leave the function
it is sitting in - which is the thing that decides if a table row is possible.

A branch reading only `effect`, `G` and its own numbers is portable: the row
becomes data and the dispatcher passes nothing special. A branch reading four
locals out of the middle of handleBank is not, and merging it anyway is how a
"shared" table ends up with a parameter per caller - which is the scattered
dispatch it was supposed to replace, wearing a nicer hat.

SO THIS MEASURES, PER BRANCH: which identifiers the body reads that are LOCAL
to the enclosing function - parameters, `var`/`let`/`const` declarations, and
`for` binders. Those are the threading cost. Everything else is either a global
the row can reach on its own, or a property access, or a call to a top-level
function.

TWO THINGS THIS DELIBERATELY DOES NOT DO:

  It does not treat a nonzero local count as a verdict. `effect` itself is a
  local at nearly every site - it is the loop binder over the relic list - and
  it is exactly the thing a table row RECEIVES. So the interesting number is
  locals OTHER than the ones a dispatcher would naturally hand over.

  It does not guess at what the dispatcher's signature should be. It prints the
  actual names so the shape can be read off the evidence rather than designed
  in advance and then justified.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── enclosing function spans, smallest-wins ──
scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(([^)]*)\)', s):
    b = s.find('{', m.end())
    if b < 0:
        continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    scopes.append((m.start(), j, m.group(1), m.group(2)))

def enclosing(pos):
    best = None
    span = None
    for a, b, nm, params in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = (a, b, nm, params), b - a
    return best

# what a dispatcher would hand a row anyway - not a threading cost
# WHAT A DISPATCHER HANDS THE ROW ANYWAY - not a threading cost.
# `npc` AND `cid` BELONG HERE AND I ORIGINALLY LEFT THEM OUT, which produced the
# whole "owner signature" finding and it was wrong. Every binding site is
# `var npc=getNpcCard(cid)` - npc is the CARD OBJECT, the loop binder over the
# boss's card ids, exactly what `effect` is. It is not "which side". Counting a
# row's own subject as an outside dependency is what made eight unrelated
# branches look like they shared a parameter.
GIVEN = {'effect', 'e', 'eff', 'r', 'rel', 'mat', 'm', 'd', 'def', 'card', 'c',
         'npc', 'cid'}
KEYWORDS = set('''var let const function return if else for while do break continue
new typeof instanceof this true false null undefined in of try catch throw
switch case default delete void yield await async class extends super'''.split())

def branch_body(pos):
    """The `if (...) { ... }` body this mechanic test sits in, or the line."""
    b = s.find('{', pos)
    nl = s.find('\n', pos)
    if b < 0 or (0 < nl < b):
        return s[pos:nl if nl > 0 else pos + 200]
    d, j = 0, b
    while j < len(s) and j - b < 4000:
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[b:j + 1]
        j += 1
    return s[pos:pos + 400]

def locals_of(fnsrc, params):
    out = set(p.strip() for p in params.split(',') if p.strip())
    for m in re.finditer(r'\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)', fnsrc):
        out.add(m.group(1))
    for m in re.finditer(r'\bfor\s*\(\s*(?:var|let)?\s*([A-Za-z_$][\w$]*)\s+in\b', fnsrc):
        out.add(m.group(1))
    return out

# A LOCAL DECLARED INSIDE THE BRANCH IS NOT A THREADING COST - it travels with
# the body. JS `var` hoisting puts it in the FUNCTION scope, so a naive
# "is it a local of the enclosing function" test cannot tell a branch's own
# scratch variable from a real outside dependency, and counts both. That is the
# instrument inventing work in the direction of more findings, again, so the
# body's own declarations are subtracted before anything is reported.
def declared_in(body):
    out = set()
    for m in re.finditer(r'\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)', body):
        out.add(m.group(1))
    for m in re.finditer(r',\s*([A-Za-z_$][\w$]*)\s*=', body):
        out.add(m.group(1))
    return out

sites = collections.defaultdict(list)
for m in re.finditer(r"mechanic\s*===\s*'([a-z_0-9]+)'", s):
    enc = enclosing(m.start())
    if not enc:
        continue
    a, b, nm, params = enc
    sites[m.group(1)].append((nm, m.start(), s[a:b], params))

single = {k: v for k, v in sites.items() if len({x[0] for x in v}) == 1}

print('THE 17 SINGLE-SITE MECHANICS, by what their body needs from around it\n')
print('%-20s %-18s %-5s %s' % ('mechanic', 'in function', 'loc', 'the locals it reads'))
print('-' * 84)

clean, threaded = [], []
for mech in sorted(single):
    nm, pos, fnsrc, params = single[mech][0]
    body = branch_body(pos)
    loc = locals_of(fnsrc, params) - declared_in(body)
    used = set()
    for t in re.finditer(r'(?<![.\w$])([A-Za-z_$][\w$]*)', body):
        w = t.group(1)
        if w in KEYWORDS or w in GIVEN:
            continue
        # a call to a top-level function is reachable from anywhere
        if re.match(r'\s*\(', body[t.end():]) and w not in loc:
            continue
        if w in loc:
            used.add(w)
    used -= GIVEN
    tag = ', '.join(sorted(used)[:5]) or '(none)'
    print('%-20s %-18s %-5d %s' % (mech, nm, len(used), tag))
    (clean if not used else threaded).append((mech, nm, sorted(used)))

print('\n' + '=' * 84)
print('PORTABLE AS-IS (%d) - body reads nothing local beyond what a dispatcher' % len(clean))
print('gives it. These are the straight table rows the scope file claimed:')
print('   ' + (', '.join(m for m, _, _ in clean) or '(none)'))
print('\nNEEDS THREADING (%d) - each local here is a parameter the dispatcher' % len(threaded))
print('would have to carry, or a value the row has to be handed:')
for mech, nm, us in threaded:
    print('   %-20s %-16s %s' % (mech, nm, ', '.join(us)))
print("""
READ THE RIGHT-HAND COLUMN, NOT THE COUNTS. Several rows needing the SAME local
is a dispatcher signature emerging from evidence. Every row needing a DIFFERENT
one is the warning that the table would be a switch with extra steps.""")
