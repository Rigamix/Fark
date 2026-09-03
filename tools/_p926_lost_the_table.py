# -*- coding: utf-8 -*-
u"""P926: P920's claim was too strong, and the field it dismissed is a live signal.

P920 concluded the old inferred-bust path "never fires at all" - 0 on matches
carrying two and one real busts, which is what made the diagnosis structural
rather than lossy. Then a silver match returned bustsInferred=16.

BOTH ARE TRUE, AND THE CLAIM NARROWS. The path never fires on a real farkle:
a farkle does not produce a choosing phase, so the branch is unreachable from
the event it was written to detect. It DOES fire when the loop finds a choosing
phase whose dice score nothing and which never resolves - the driver spinning on
a table it has lost. Sixteen of those in one match, against 0 in every other
match of the run.

So it is not a vestigial second opinion about busts. It is a HARNESS-HEALTH
signal, and it is renamed to say so: lostTheTable. Nonzero means the driver was
looking at a board it could not act on, which is exactly the condition that
produced the two impossible rows in the silver run - three banks against two
completed turns, and four banks against zero points.

AND IT IS ASSERTED, not merely reported. A field nobody checks is how the
sixteen went unnoticed until an identity in a different patch tripped over the
same row.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(path, pairs, checks):
    s = io.open(path, encoding='utf-8', newline='').read()
    for _i, (old, new) in enumerate(pairs):
        label = '%s edit %d' % (os.path.basename(path), _i + 1)
        pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
        ms = list(re.finditer(pat, s))
        if len(ms) != 1:
            sys.exit('ANCHOR x%d for %s in %s (nothing written)'
                     % (len(ms), label, os.path.basename(path)))
        m = ms[0]
        rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
        s = s[:m.start()] + rep + s[m.end():]
        edits.append(label)
    code = re.sub(r'/\*[\s\S]*?\*/', '', s)
    for fn, msg in checks:
        if not fn(code, s):
            sys.exit('%s (nothing written)' % msg)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)


D = os.path.join(ROOT, 'tools', 'fark_driver.js')
patch(D, [
    (u"""    let bustsInferred = 0, endPTurnsSeen = 0, bustJustFired = false;""",
     u"""    /* P926: RENAMED FROM bustsInferred, because P920's reading of it was too
       strong and the correction makes it useful. P920 said the old inferred
       path "never fires at all"; a later match returned 16. Both hold once the
       claim narrows: it never fires on a real FARKLE - a farkle produces no
       choosing phase, so the branch is unreachable from the event it was
       written to detect - and it DOES fire when the loop finds a choosing
       phase whose dice score nothing and which never resolves. That is the
       driver spinning on a board it has lost, not a bust.
       Sixteen of them appeared in the one match that also returned three banks
       against two completed turns. Nonzero here means the numbers from that
       match are about nothing, so it is asserted rather than reported. */
    let lostTheTable = 0, endPTurnsSeen = 0, bustJustFired = false;"""),
    (u"""        bustsInferred++;""",
     u"""        lostTheTable++;"""),
    (u"""      bustsInferred, endPTurnsSeen, bustHooked,""",
     u"""      lostTheTable, endPTurnsSeen, bustHooked,
      /* the driver held the table for the whole match - a false here says the
         loop sat on a board it could not act on, and every count below it is
         about a match that did not happen the way it looks */
      heldTheTable: lostTheTable === 0,"""),
], [
    (lambda c, s: 'bustsInferred' not in c, 'the old name survives'),
    (lambda c, s: c.count('lostTheTable++') == 1, 'the counter is not incremented once'),
    (lambda c, s: c.count('heldTheTable:') == 1, 'heldTheTable is not returned once'),
    (lambda c, s: c.count('turnsAddUp:') == 1, "P920's identity was disturbed"),
])

Y = os.path.join(ROOT, 'tools', 'apv_yield.js')
patch(Y, [
    (u"""    driverBusts: r.busts, driverBustsInferred: r.bustsInferred,""",
     u"""    driverBusts: r.busts, driverLostTheTable: r.lostTheTable,
    driverHeldTheTable: r.heldTheTable,"""),
    (u"""      inferred: r.driverBustsInferred, endReason: r.endReason,""",
     u"""      lostTheTable: r.driverLostTheTable, endReason: r.endReason,"""),
], [
    (lambda c, s: 'BustsInferred' not in c and 'bustsInferred' not in c,
     'the probe still reads the old field'),
    (lambda c, s: c.count('driverHeldTheTable:') == 1,
     'the probe does not carry heldTheTable'),
])

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
