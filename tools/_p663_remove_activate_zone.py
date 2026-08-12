# -*- coding: utf-8 -*-
"""P663: the activation box is gone, not hidden.

Denis, checking the design: "there should be the cards at the bottom, nothing
above, only an invisible threshold line that when dragging cards past, they
activate. Is that what you have? No activation box area with dotted lines
anymore, etc."

VISUALLY YES, STRUCTURALLY NO - which is the honest answer and the reason for
this patch. P612 replaced the box with the threshold and turned the box off with
`.activate-zone{display:none!important}`, but left everything behind it:

  the element   <div class="activate-zone" id="activateZone"> with an SVG rect
                border and an "ACTIVATE" label, still in the markup
  the CSS       its own positioning rules at two breakpoints, plus .mcard.in-zone
  the code      showActivateZone, hideActivateZone, hitTestActivateZone
  a caller      showActivateZone(cardId) on the legacy drag's start

Counted before removing: hideActivateZone and hitTestActivateZone have NO
callers, and nothing anywhere adds .in-zone - there is only a line that removes
it. So the layer is one live call away from being entirely dead, and that call
is on the legacy row P657 showed is empty in every real run.

A feature switched off with display:none is worse than one deleted. It reads as
present to anyone scanning the file, it keeps its CSS alive at two breakpoints,
and `!important` is exactly the kind of guard that gets lifted by someone who
does not know why it is there. P414's finding, already recorded in this file:
"a producer left wired is how the last removed overlay survived removal".
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the element ──────────────────────────────────────────────────────────
sub(u'  <div class="activate-zone" id="activateZone"><svg class="az-border" width="100%" height="100%" preserveAspectRatio="none"><rect x="1" y="1" rx="8" ry="8"></rect></svg><span class="az-label">ACTIVATE</span></div>\n',
    u'  <!-- P663: the activation box is gone. The threshold replaced it in P612 and\n'
    u'       the box was only switched off with display:none, which reads as present\n'
    u'       to anyone scanning this file. Cards sit at the bottom, nothing above\n'
    u'       them, and an invisible line decides. -->\n',
    'P663 the element')

# ── the caller, then the three functions ─────────────────────────────────
sub(u"      showActivateZone(cardId);\n", u"", 'P663 the last caller')

sub(u"function showActivateZone(cardId){\n"
    u"  const zone=document.getElementById('activateZone');\n"
    u"  const canUse=canActivateCard(cardId);\n"
    u"  zone.classList.add('dragging-active');zone.classList.remove('hot','unavailable');\n"
    u"  let label=zone.querySelector('.az-label');\n"
    u"  if(!label){label=document.createElement('span');label.className='az-label';zone.prepend(label);}\n"
    u"  if(canUse){label.textContent='ACTIVATE';}\n"
    u"  else{zone.classList.add('unavailable');label.textContent='NOT AVAILABLE';}\n"
    u"}\n"
    u"function hideActivateZone(){\n"
    u"  const zone=document.getElementById('activateZone');\n"
    u"  zone.classList.remove('dragging-active','hot','unavailable');\n"
    u"  /* Restore label text but preserve any .in-zone cards */\n"
    u"  const label=zone.querySelector('.az-label');\n"
    u"  if(label)label.textContent='ACTIVATE';\n"
    u"}\n",
    u"/* P663: showActivateZone / hideActivateZone / hitTestActivateZone removed with\n"
    u"   the box. Counted first: the last two had no callers at all, and the first\n"
    u"   had exactly one - on the legacy row's drag start, a row P657 showed is\n"
    u"   empty in every real run. */\n",
    'P663 show/hide')

# hitTestActivateZone: uncalled, remove whole function
i = s.find('function hitTestActivateZone(clientX,clientY){')
if i < 0:
    sys.exit('hitTestActivateZone not found')
j = s.find('\nfunction ', i + 10)
if j < 0:
    sys.exit('could not find the end of hitTestActivateZone')
s = s[:i] + s[j + 1:]
n += 1
print('  ok  P663 hitTestActivateZone (uncalled)')

# ── the CSS ──────────────────────────────────────────────────────────────
sub(u"#screen-match .activate-zone{left:20%;right:20%;height:auto;aspect-ratio:720/218}\n", u"", 'P663 css a')
sub(u".activate-zone{display:none!important}\n", u"", 'P663 css b')
sub(u"  .activate-zone{bottom:calc(100% + 50px);height:50px}\n", u"", 'P663 css c')

# .mcard.in-zone: nothing adds the class
i = s.find('.mcard.in-zone{')
if i < 0:
    sys.exit('.mcard.in-zone not found')
j = s.find('}', i)
if j < 0:
    sys.exit('unterminated .mcard.in-zone')
s = s[:i] + s[j + 1:].lstrip('\n')
n += 1
print('  ok  P663 .mcard.in-zone (nothing adds it)')

sub(u"    el.classList.remove('used');el.classList.remove('in-zone');",
    u"    el.classList.remove('used');",
    'P663 the last in-zone reference')

sub(u"  var _atz=document.getElementById('activateZone');\n"
    u"  if(_atz)_atz.querySelectorAll('.card-trig-label').forEach(e=>e.remove());\n",
    u"",
    'P663 the label cleanup that queried it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
