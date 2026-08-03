# -*- coding: utf-8 -*-
"""Is the old CARDS roster retired legacy, or live content nobody wired up?

Denis's distinction, and it is the right one: "unused on every path I drove" is
not "unreachable on every path that exists". Two very different situations look
identical from a single driven match:

  (a) pre-redesign legacy - content that died when the six-family system
      replaced it, like the measure_twice card found earlier in this project
  (b) unreachable by OMISSION - content that is supposed to be live and simply
      never got wired into a draft or shop pool

Deleting (a) is cleanup. Deleting (b) destroys work and hides a bug.

GIT DATING DOES NOT SEPARATE THEM HERE, which is worth stating rather than
quietly not using: both CARDS and FAM_CARDS first appear on 2026-07-08, because
that is the day fark_proto.html was created as an isolated dev copy. The old
roster arrived wholesale in the initial port. So "when was it added" has the
same answer for everything and settles nothing.

WHAT DOES SEPARATE THEM: whether the roster has been MAINTAINED since the
family engine landed the same day. Legacy content gets ported once and then
frozen. Content someone still intends to ship gets edited. So this diffs the
CARDS roster at the family-engine commit against HEAD, and reports every id
added, removed, or edited since.
"""
import io, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAM_COMMIT = '55408b3'          # P1a: family card engine

def at(rev):
    return subprocess.check_output(
        ['git', 'show', '%s:fark_proto.html' % rev],
        cwd=ROOT).decode('utf-8', 'replace')

def roster(src, name):
    """the ids inside one top-level array, brace-matched from its opening [."""
    m = re.search(r'\b(?:const|var)\s+%s\s*=\s*\[' % name, src)
    if not m: return {}
    i = src.index('[', m.end() - 1)
    depth, j = 0, i
    while j < len(src):
        if src[j] == '[': depth += 1
        elif src[j] == ']':
            depth -= 1
            if depth == 0: break
        j += 1
    body = src[i:j + 1]
    out = {}
    # each definition object, keyed by id, so an EDIT shows as a changed value
    for dm in re.finditer(r"\{id:'([a-z0-9_]+)'", body):
        k = dm.start()
        d, e = 0, k
        while e < len(body):
            if body[e] == '{': d += 1
            elif body[e] == '}':
                d -= 1
                if d == 0: break
            e += 1
        out[dm.group(1)] = re.sub(r'\s+', ' ', body[k:e + 1])
    return out

old_then, old_now = roster(at(FAM_COMMIT), 'CARDS'), roster(at('HEAD'), 'CARDS')
fam_then, fam_now = roster(at(FAM_COMMIT), 'FAM_CARDS'), roster(at('HEAD'), 'FAM_CARDS')

def report(label, then, now):
    added = sorted(set(now) - set(then))
    removed = sorted(set(then) - set(now))
    edited = sorted(k for k in set(then) & set(now) if then[k] != now[k])
    print('\n%s: %d at the family-engine commit -> %d at HEAD' % (label, len(then), len(now)))
    print('  added since:   %d %s' % (len(added), added[:14]))
    print('  removed since: %d %s' % (len(removed), removed[:14]))
    print('  edited since:  %d %s' % (len(edited), edited[:14]))
    return added, removed, edited

oa, orm, oe = report('OLD CARDS roster', old_then, old_now)
fa, frm, fe = report('FAM_CARDS roster', fam_then, fam_now)

print('\n' + '=' * 68)
churn_old = len(oa) + len(orm) + len(oe)
churn_fam = len(fa) + len(frm) + len(fe)
print('churn since the family engine landed:  old %d   family %d' % (churn_old, churn_fam))
print('READ THIS AS: a roster that is still being shipped gets edited. One that')
print('was ported and abandoned does not. Neither number proves intent on its')
print('own - a frozen roster could also just be finished - so this is evidence')
print('for Denis to rule on, not a verdict.')
