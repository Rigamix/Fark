# -*- coding: utf-8 -*-
"""P676: the bubble gets the six pixels it was missing.

Denis: "dialogue should be on two lines for example here, no reason to be on
three which takes too much room."

MEASURED, not assumed - the fitter was instrumented on a fresh show of his
exact example line, in Raritas, in a real match:

    the box offers      349px   (94% of the inner box, minus 48px padding)
    two lines need      355px
    at 349 the line is  3 lines, so the fitter correctly returns a 3-line fit

The fitter has been minimising lines all along (it measures the line count at
the full available width and preserves it) - the CAP was binding, by six
pixels. max-width 94->96% and the side padding 24->20 hand the text ~365px, so
the example - and everything narrower than it - sets on two lines with margin
to spare. The corpus-wide three-line guarantee is re-measured after this, not
carried over: Raritas's metrics are not JMH Beda's.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = u"  box-shadow:none;padding:22px 24px;max-width:94%;margin:0 0 0 3cqw;flex:0 1 auto;"
new = (u"  /* P676: 94%/24px -> 96%/20px. Instrumented: the box offered the text 349px\n"
       u"     and two lines of Denis's example need 355 - the fitter was already\n"
       u"     minimising lines, the cap was binding by SIX pixels. This hands it ~365. */\n"
       u"  box-shadow:none;padding:22px 20px;max-width:96%;margin:0 0 0 3cqw;flex:0 1 auto;")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P676 six pixels')
