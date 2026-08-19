# -*- coding: utf-8 -*-
"""P800: the bust lighting goes properly red, and stays red through the
scatter.

Denis: "you didn't make the lighting more red on bust." Measured at
the true bust moment: both red mechanisms DO fire - the room multiply
(#matchBustRed opacity 1) and the 3D light flare (lights at #d16f58) -
but the envelope is a blink: 260ms hold, gone by ~1.2s, faded before
the scatter even finishes. Every end-pose capture (and the player's
eye, busy with the BUST word) lands after it died.

At his request, redder and longer:
  BUSTLIGHT  mix .72 -> .86, col c03818 -> c82812 (deeper, less
             orange), hold 260 -> 700ms, out 900 -> 1500ms - the dice
             stay red through the whole kick and ease back with it.
  matchBustRed  the .on hold 380 -> 850ms, the fade .9s -> 1.4s, and
             the pool centre deepens (.55 -> .62).
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


sub("""  BUSTLIGHT:{col:0xc03818, mix:0.72, holdMs:260, outMs:900},""",
    """  /* P800 (Denis: 'make the lighting more red on bust'): deeper red,
     held through the whole scatter instead of a 260ms blink. */
  BUSTLIGHT:{col:0xc82812, mix:0.86, holdMs:700, outMs:1500},""",
    'the dice light flare deepens and holds')

sub("""#matchBustRed{position:absolute;inset:0;z-index:0;pointer-events:none;
  mix-blend-mode:multiply;opacity:0;background:radial-gradient(ellipse at 50% 46%,
  rgba(192,56,24,.55) 0%, rgba(120,24,10,.85) 100%);
  transition:opacity .16s ease-out}""",
    """#matchBustRed{position:absolute;inset:0;z-index:0;pointer-events:none;
  mix-blend-mode:multiply;opacity:0;background:radial-gradient(ellipse at 50% 46%,
  rgba(192,44,20,.62) 0%, rgba(120,24,10,.85) 100%);/* P800: redder pool */
  transition:opacity .16s ease-out}""",
    'the room red deepens')

sub("""      var br=document.getElementById('matchBustRed');
      if(br){
        br.style.transition='none';br.classList.add('on');
        setTimeout(function(){
          br.style.transition='opacity .9s ease-in';br.classList.remove('on');
        },380);
      }""",
    """      var br=document.getElementById('matchBustRed');
      if(br){
        br.style.transition='none';br.classList.add('on');
        /* P800: the red lives through the scatter, not a blink */
        setTimeout(function(){
          br.style.transition='opacity 1.4s ease-in';br.classList.remove('on');
        },850);
      }""",
    'the room red holds')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
