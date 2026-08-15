# -*- coding: utf-8 -*-
"""P741: the match tooltip - width between, real justification, a title
that reads, and the scores actually gone.

Denis: 'too wide now, do an in between. Make the card titles brighter
and maybe an outline. The score still overlaps because it doesn't
disappear. The text overlaps the top of the cards. And when I say
justified I mean left and right line up vertically.'

- 62cqw, between the old 50 (a column) and 74 (too wide).
- THE SCORES: P728 faded them with a plain rule, but _renderSelTags and
  _renderOppTags write INLINE styles on those elements, and inline wins
  over any stylesheet rule without !important. That is why they never
  went. Now !important, and visibility with it so a tag that is written
  fresh mid-tip cannot reappear.
- JUSTIFIED means both edges line up: text-align:justify needs
  text-align-last to leave the final line alone, and the words must be
  allowed to break, or a long word forces a ragged edge. Hyphens on.
- The title takes the outline treatment the game's own headings use
  (paint-order stroke), and lifts to near-cream.
- The tip clears the card by a proper gap and is clamped to the screen,
  so it can no longer sit on the card's top edge.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


sub(u"""  /* P737b: WIDER, per Denis - 50cqw was a column; the justified body
     reads badly in a narrow measure and the box crowded the card. */
  max-width:74cqw;width:74cqw;text-align:center}""",
    u"""  /* P737b: 50cqw was a column and justification could not work in it.
     P741: 74 was too wide - 62 is the in-between Denis asked for. */
  max-width:62cqw;width:62cqw;text-align:center}""",
    'width in between')

sub(u"""#screen-match.tip-open .selTag,#screen-match.tip-open #selTotal,
#screen-match.tip-open .oppTag,#screen-match.tip-open #oppTotal{
  opacity:0;transition:opacity .18s ease}""",
    u"""/* P741: !important, because _renderSelTags and _renderOppTags write
   INLINE styles on these elements - and an inline style beats any
   stylesheet rule without it. That is why the scores never went away
   however many selectors P728 listed. visibility goes with it so a tag
   written FRESH while the tip is open cannot appear either. */
#screen-match.tip-open .selTag,#screen-match.tip-open #selTotal,
#screen-match.tip-open .oppTag,#screen-match.tip-open #oppTotal,
#screen-match.tip-open .kept-total,#screen-match.tip-open #turnPts{
  opacity:0 !important;visibility:hidden !important;
  transition:opacity .18s ease}""",
    'scores really hide')

sub(u"""#cardFocusTip .cft-name{font-family:'JMH Beda',serif;font-size:3.9cqw;
  letter-spacing:.09em;""",
    u"""#cardFocusTip .cft-name{font-family:'JMH Beda',serif;font-size:4.1cqw;
  letter-spacing:.09em;
  /* P741: brighter, with the ink outline the game's own headings wear -
     stroke first so the letterform stays crisp on the dark wood */
  -webkit-text-stroke:0.55cqw #1a1008;paint-order:stroke fill;
  text-shadow:0 0.35cqw 0.5cqw rgba(8,4,2,.85);""",
    'title brighter + outlined')

sub(u"""  color:color-mix(in srgb,var(--cft-a,#f0c860) 82%,#ffdf9e)}""",
    u"""  color:color-mix(in srgb,var(--cft-a,#f0c860) 55%,#fff2cf)}/* P741: lifted */""",
    'title colour lifted')

sub(u"""  text-align:justify;text-align-last:center;text-wrap:pretty;
  hyphens:auto;-webkit-hyphens:auto}""",
    u"""  /* P741: JUSTIFIED means both edges line up. text-wrap:pretty fights
     that (it re-balances lines), so it goes; the last line stays centred
     because a justified two-word final line is a chasm, and hyphenation
     is what keeps a long word from forcing a ragged edge. */
  text-align:justify;text-align-last:center;
  hyphens:auto;-webkit-hyphens:auto;overflow-wrap:break-word}""",
    'real justification')

sub(u"""  if(o.below){tip.style.top=(cr.bottom-sr.top+sr.width*0.045)+'px';}
  else{tip.style.top=(cr.top-sr.top-tip.offsetHeight-sr.width*0.045)+'px';}""",
    u"""  /* P741: a real gap off the card (0.045 of the width was ~19px and the
     taller box ate it, so the text sat on the card's top edge), and
     clamped inside the screen so a long rule text cannot ride off the
     top and land back on the art. */
  var _gap=sr.width*0.075;
  if(o.below){tip.style.top=(cr.bottom-sr.top+_gap)+'px';}
  else{
    var _t=cr.top-sr.top-tip.offsetHeight-_gap;
    if(_t<sr.height*0.02)_t=sr.height*0.02;
    tip.style.top=_t+'px';
  }""",
    'tip clears the card')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
