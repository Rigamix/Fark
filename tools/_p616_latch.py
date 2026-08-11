# -*- coding: utf-8 -*-
"""P616: the legacy-card cutover stops running on every load.

The other half of the reachability defect. This block converts "legacy equipped
cards" to 15g each and blanks S.run.cards / S.run.pouch - and it runs on EVERY
_getS() invocation with NO LATCH. It cannot tell a card left over from the P1.2
cutover from one the player equipped five seconds ago, so equipping a card and
then touching anything that reads state hands it straight back as 15 gold.

THE FILE ALREADY KNOWS THE PATTERN. Twenty lines above, the one-shot un-mute
latches on S.settings._protoUnmuted with the comment that a player who then
mutes deliberately keeps that choice - "the un-mute never fights the user". This
one fought the user on every call.

A latch, not a deletion: a save written before the cutover still needs converting
exactly once, and the flag records that it happened.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = (u"  if(typeof S!=='undefined'&&S&&S.run){\n"
       u"    var _mg=0;/* audit P1.2: legacy equipped cards (incl. signatures) -> sell value */\n"
       u"    if(Array.isArray(S.run.cards)&&S.run.cards.some(function(c){return !!c;})){\n"
       u"      _mg+=S.run.cards.filter(function(c){return !!c;}).length;S.run.cards=[null,null,null,null];\n"
       u"    }\n"
       u"    if(Array.isArray(S.run.pouch)&&S.run.pouch.some(function(c){return !!c;})){\n"
       u"      _mg+=S.run.pouch.filter(function(c){return !!c;}).length;S.run.pouch=[null,null,null];\n"
       u"    }\n"
       u"    if(_mg)S.run.gold=(S.run.gold||0)+15*_mg;\n"
       u"  }\n")

NEW = (u"  /* P616: LATCHED, ONCE PER RUN. This converts legacy equipped cards to 15g\n"
       u"     and blanks the slots - and it used to run on EVERY _getS() call, with\n"
       u"     nothing to distinguish a card left over from the P1.2 cutover from one\n"
       u"     the player equipped five seconds ago. So equipping a card and then\n"
       u"     touching anything that reads state sold it back, every time, and\n"
       u"     S.run.cards could never hold anything. That is the other half of why\n"
       u"     the player's hand was always empty.\n"
       u"     The pattern is the file's own: the one-shot un-mute twenty lines up\n"
       u"     latches on S.settings._protoUnmuted precisely so it \"never fights the\n"
       u"     user\". A latch rather than a deletion, because a save written before\n"
       u"     the cutover still needs converting exactly once. */\n"
       u"  if(typeof S!=='undefined'&&S&&S.run&&!S.run._p12CardsConverted){\n"
       u"    var _mg=0;/* audit P1.2: legacy equipped cards (incl. signatures) -> sell value */\n"
       u"    if(Array.isArray(S.run.cards)&&S.run.cards.some(function(c){return !!c;})){\n"
       u"      _mg+=S.run.cards.filter(function(c){return !!c;}).length;S.run.cards=[null,null,null,null];\n"
       u"    }\n"
       u"    if(Array.isArray(S.run.pouch)&&S.run.pouch.some(function(c){return !!c;})){\n"
       u"      _mg+=S.run.pouch.filter(function(c){return !!c;}).length;S.run.pouch=[null,null,null];\n"
       u"    }\n"
       u"    if(_mg)S.run.gold=(S.run.gold||0)+15*_mg;\n"
       u"    S.run._p12CardsConverted=1;\n"
       u"  }\n")

c = s.count(OLD)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW))
print('P616 applied: cutover latched on S.run._p12CardsConverted')
