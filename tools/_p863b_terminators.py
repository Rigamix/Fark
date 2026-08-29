# -*- coding: utf-8 -*-
"""P863b: NPC_RESCUES and NPC_ARMS get their `];` back.

P863's row-deleter took each row from its `{id:` to the start of the NEXT
`{id:`, falling back to the table's outer bound for the LAST row - and that
bound was the following top-level declaration rather than the array's own
terminator, so deleting the final row of each table swallowed the `];`. The
parse gate caught it on the next run (Unexpected token 'var'), which is the
job it is in the chain to do. P863's table_bounds is fixed at the source;
this repairs the two live tables.

Uses the house sub() with the \r?\n fallback: this region is CRLF while most
of the ones patched today are LF, and a plain \n anchor found nothing twice
before that was noticed."""
import io, sys, re
P = 'fark_proto.html'
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\n', '\n').replace('\n', '\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub("""REROLLED";}},
var NPC_ARMS=[""",
    """REROLLED";}},
];
var NPC_ARMS=[""", 'NPC_RESCUES terminator')

sub("""     by the P521 join regardless. */
function _npcRunArms(moment,ctx){""",
    """     by the P521 join regardless. */
];
function _npcRunArms(moment,ctx){""", 'NPC_ARMS terminator')

if s.count('var NPC_RESCUES=[') != 1 or s.count('var NPC_ARMS=[') != 1:
    sys.exit('TABLE DECLARATIONS DISTURBED (nothing written)')
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d terminators restored' % len(edits))
