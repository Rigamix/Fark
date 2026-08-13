# -*- coding: utf-8 -*-
"""P679: the tip's word gaps close for good.

Denis, third pass: "too much space between words still."

The gaps ARE justification: on a 50cqw column, `text-align:justify` stretches
the spaces of every non-final line to reach both edges, and no box width makes
that stop - narrowing only changes WHICH lines get the chasms. The latest
instruction outranks the earlier "justified both sides", so the stretch goes:
balanced centered text - natural single spaces, near-even line lengths, tidy
edges without the padding.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;\n"
       u"  color:#f2e6c8;line-height:1.4;margin-top:1.1cqw;letter-spacing:.075em;\n"
       u"  text-align:justify;text-align-last:center}")
new = (u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;\n"
       u"  color:#f2e6c8;line-height:1.4;margin-top:1.1cqw;letter-spacing:.075em;\n"
       u"  /* P679: justify WAS the word gaps - it stretches every non-final line's\n"
       u"     spaces to both edges, and no box width stops that. Balanced centred\n"
       u"     text instead: natural spaces, near-even lines. */\n"
       u"  text-align:center;text-wrap:balance}")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P679 the stretch goes')
