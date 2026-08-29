# -*- coding: utf-8 -*-
u"""P865 (BOSS REWARD BRIEF section 2, the last of the sweep): the twenty
activate* handlers nothing can reach any more, and the match state only they
ever wrote.

Section 7's order was: rows first, parse gate, THEN the handlers - "not the
other way round, or a live `case` in activateCard points at a function that no
longer exists". P862 took the rows, P863 took the cases, so by here every one
of these has zero callers.

TWENTY, NOT EIGHTEEN. A reference count over the raw text says eighteen,
because activateSleightOfHand and activateVanishingAct are each named once
more - both times inside a COMMENT (a P510 cross-reference at 13570 and a site
list at 31999). Neither is a call. The two comments are left in place: they
describe a bug's shape and a line's history, and both remain true statements
about code that used to be there.

THE MATCH STATE IS MARKED, NOT REMOVED, AND THAT IS A DELIBERATE STOP.
stitchActive, vowActive, ledgerActive and allInActive were each SET in exactly
one place - a handler deleted here - so every block that TESTS them is now
unreachable. The tempting move is to delete those blocks too. They are not
small: the Stitch reader is a whole bust-save branch, Vow's is a roll-scoring
branch, and Ledger's and All In's sit inside the bank. That is surgery in the
bust and bank paths - the highest-risk code in this file and the area with the
longest history of regressions - for zero behaviour change, since a flag with
no writer is a branch that cannot be taken.

So the four flags keep their init and their reset, and the reset line carries a
comment naming them as dead. An initialised-and-cleared-but-never-set flag is
the cheapest possible marker for the branches downstream, and it costs nothing
at runtime. The removal is written up as follow-up rather than smuggled into
the end of a long session. secondWindActive and pyreBonus are LIVE and
untouched: second_wind IS Mabel's Stitch and the_pyre IS Ambrose's Pyre.

EACH CHUNK IS SYNTAX-CHECKED BEFORE ANYTHING IS WRITTEN. The function bodies
are found by scanning from `function NAME(` at column 0 to the next line that
is exactly `}` - a convention this file follows, but a convention is not a
guarantee, so every extracted chunk is handed to `node --check` on its own. A
chunk that does not parse as a complete function means the boundary was wrong,
and the run aborts before touching the file rather than after.
"""
import io, os, re, sys, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

ORPHANS = ['activateAlchemistTouch', 'activateAldricsVow', 'activateAllIn',
           'activateAmbroseGrace', 'activateBrokenLantern', 'activateBrutusFist',
           'activateCoinFlip', 'activateCorvusLedger', 'activateDoubleDownDie',
           'activateFinnicksPalm', 'activateMabelsStitch', 'activateOldBones',
           'activateSevenDice', 'activateTheNudge', 'activateTheTab',
           'activateTwinningCharm', 'activateWhispersHex', 'activateWildDie',
           'activateSleightOfHand', 'activateVanishingAct']


def chunk_of(src, fn):
    m = re.search(r'(?m)^function\s+%s\s*\(' % re.escape(fn), src)
    if not m:
        sys.exit('FUNCTION NOT FOUND AT COLUMN 0: %s (nothing written)' % fn)
    if len(re.findall(r'(?m)^function\s+%s\s*\(' % re.escape(fn), src)) != 1:
        sys.exit('FUNCTION DEFINED TWICE: %s (nothing written)' % fn)
    end = re.search(r'(?m)^\}[ \t]*\r?\n', src[m.start():])
    if not end:
        sys.exit('NO COLUMN-0 CLOSING BRACE AFTER %s (nothing written)' % fn)
    return m.start(), m.start() + end.end()


# ---- extract, syntax-check, then delete -----------------------------
chunks = []
for fn in ORPHANS:
    a, b = chunk_of(s, fn)
    chunks.append((fn, a, b, s[a:b]))

tmp = tempfile.mkdtemp(prefix='p865_')
for fn, a, b, body in chunks:
    f = os.path.join(tmp, fn + '.js')
    io.open(f, 'w', encoding='utf-8', newline='\n').write(body)
    r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('CHUNK FOR %s DOES NOT PARSE - the boundary is wrong, not the '
                 'code (nothing written):\n%s' % (fn, (r.stderr or '')[:400]))

for fn, a, b, body in sorted(chunks, key=lambda c: -c[1]):
    s = s[:a] + s[b:]

# ---- the state only they wrote --------------------------------------
def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]


# ---- the state is MARKED, not removed, and that is a deliberate stop ----
# Deleting the handlers strands four flags - stitchActive, vowActive,
# ledgerActive, allInActive - whose only writers these were. Their READERS are
# not small: the Stitch block is a whole bust-save branch, Vow's is a
# roll-scoring branch, Ledger's and All In's sit inside the bank. Removing
# them means surgery in the bust and bank paths, which is the highest-risk
# code in this file, for a purely cosmetic gain - the blocks are already inert,
# because a flag with no writer is a branch that cannot be taken.
# Section 7 asks for the orphaned HANDLERS and that is what this takes. The
# blocks are marked in place so the next reader is not misled into thinking
# they run, and the removal is written up as follow-up rather than smuggled in
# at the end of a long session.
sub("""  if(G.activeCardState){G.activeCardState.stitchActive=false;G.activeCardState.vowActive=false;""",
    """  /* P865: stitchActive, vowActive, ledgerActive and allInActive ARE NOW
     DEAD - their only writers were the four handlers deleted with the cards
     they belonged to, so every block that tests them is unreachable. They are
     reset here, and the resets are kept, precisely so this line keeps naming
     them: a flag that is initialised and cleared but never set is the cheapest
     possible marker for the branches downstream that can no longer be taken
     (the Stitch bust-save, the Vow roll check, the Ledger and All In bank
     blocks). Removing those four blocks is surgery in the bust and bank paths
     for no behaviour change, so it is written up rather than done here.
     secondWindActive and pyreBonus are LIVE: second_wind is Mabel's Stitch and
     the_pyre is Ambrose's Pyre. */
  if(G.activeCardState){G.activeCardState.stitchActive=false;G.activeCardState.vowActive=false;""",
    'dead state marked')

# ---- post-asserts ----------------------------------------------------
for fn in ORPHANS:
    if re.search(r'(?m)^function\s+%s\s*\(' % re.escape(fn), s):
        sys.exit('ORPHAN SURVIVES: %s (nothing written)' % fn)
for keep in ('activateGrogsFlask', 'activateSecondWind', 'activateGamblersEye',
             'activateLoan', 'activateFrozenDie', 'activateAlchemistsChisel',
             'activateDoubleDown', 'activateThePyre'):
    if not re.search(r'(?m)^function\s+%s\s*\(' % re.escape(keep), s):
        sys.exit('LIVE HANDLER DELETED: %s (nothing written)' % keep)
if 'secondWindActive' not in s or 'pyreBonus' not in s:
    sys.exit('LIVE STATE LOST (nothing written)')
# the marker has to name the flags it is marking, or it stops being one
for flag in ('stitchActive', 'vowActive', 'ledgerActive', 'allInActive'):
    if flag not in s:
        sys.exit('DEAD-STATE MARKER LOST %s (nothing written)' % flag)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d orphan handlers deleted, match state trimmed' % len(ORPHANS))
