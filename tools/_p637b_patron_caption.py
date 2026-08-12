# -*- coding: utf-8 -*-
"""P637b: the sixth P637 edit, split out because of an encoding trap worth naming.

The boss-loss caption and the patron-loss caption are forty lines apart and
store the minus sign DIFFERENTLY: the boss site holds a real U+2212 character,
the patron site holds the six literal characters backslash-u-2-2-1-2. The main
P637 script matched the first and missed the second, which is the file mixing
escapes and real characters exactly as the project's notes have said twice.

And the retry failed too, for the reason the same notes give: a bash heredoc
mangles a backslash-u sequence on the way in, so `\\u2212` typed into a heredoc
arrived as a real minus sign and matched nothing. That is why patches here go
through a Written .py file and never through a heredoc.

The anchor below builds the escape by CONCATENATION - a backslash character and
the text 'u2212' - so no amount of escape processing anywhere in the chain can
turn it into something else.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

MINUS = chr(92) + 'u2212'          # the literal two-token escape, built safely

old = ("    var _lostBuy=(typeof LO!=='undefined'&&LO&&LO.buyIn)||0;\n"
       "    if(_lostBuy>0){\n"
       "      setTimeout(function(){\n"
       "        if(resGoldWrap){resGoldWrap.style.display='flex';resGoldWrap.classList.add('fade-in');}\n"
       "        if(resCoinBig)resCoinBig.style.display='none';\n"
       "        if(resGoldText){resGoldText.textContent='" + MINUS + "'+_lostBuy+'g';"
       "resGoldText.style.color='#e0868e';resGoldText.classList.add('show');}\n"
       "      },1300);\n"
       "    }")

new = ("    /* P637: the patron loss's minus-Xg is on the painted sign now. This block\n"
       "       only ever existed to carry that string - it hid the coin outright, so\n"
       "       nothing else was happening here - and .loss-art-on suppresses the wrap\n"
       "       regardless. Deleted rather than left behind a dead timer. */")

c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)\n  %r' % (c, old[:140]))
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P637b drop the patron-loss caption')
