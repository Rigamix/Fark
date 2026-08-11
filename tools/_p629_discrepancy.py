# -*- coding: utf-8 -*-
"""P629 (Part 8): "The Discrepancy" - a second gated thread, and the wiring it needs.

THE POOL ALONE WOULD HAVE DONE NOTHING. _dlgSay and _dlgAmbient both name
'reaction:king' literally; there is no generic "try the threads" step. Adding
reaction:discrepancy without a caller is 30 lines that parse, ship and never
fire - the same failure shape as writing Part 7 to PERSONAS. So the wiring is
part of this patch, not a follow-up.

NARROWER BY CONSTRUCTION, which is what the brief asks for. The King rumour is
wide - anyone can have an opinion about a royal visit. A discrepancy in a
specific moneylender's private books is not something most patrons would credibly
know about, so only the three the brief names can carry it: Corbin (owns the
story), Sparr (carries messages past it), Pell (in Corvus's orbit). One object to
extend if more should qualify.
AND IT IS DELIBERATELY NOT IN _dlgAmbient. Ambient is the room's talk with no
speaker attached; a private ledger matter having no mouth to come out of is
exactly the eligibility rule doing its job rather than being bypassed.

ELIGIBLE SPEAKERS PREFER IT TO THE KING. Placed before the King branch, so
Corbin/Sparr/Pell carry the ledger thread and everyone else carries the royal
one - two threads genuinely running in parallel through different mouths, rather
than one pool starving the other.

IT RESOLVES, WHERE THE KING DEFLATES. Tier 3 gates on heard() AND night_gte(4),
so the story actually ends. Two threads that both trail off would read as one
mechanism wearing different words.

THE BOOKKEEPING IS ALREADY THERE: _dlgSay records run._dlgHeard[row.t] for any
pool starting 'reaction:' and run._dlgHeard[row.tag] for any tagged row, so the
per-run no-repeat and the tier gate both work for this thread without a line of
new state - the same infrastructure the King gate uses, which P623 verified is
sound.
"""
import io, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the wiring, without which none of the content is reachable ───────────
sub(u"  var key=String(id).toLowerCase(),stage=run._dlgStage[key]||0;\n"
    u"  var row=_dlgPick('patron:'+key,stage,null);\n"
    u"  if(!row)row=_dlgPick('reaction:king',stage,run._dlgHeard);",
    u"  var key=String(id).toLowerCase(),stage=run._dlgStage[key]||0;\n"
    u"  var row=_dlgPick('patron:'+key,stage,null);\n"
    u"  /* P629: THE DISCREPANCY, for the few who could credibly know of it.\n"
    u"     A missing sum in Corvus's private books is not tavern-wide gossip the\n"
    u"     way a royal visit is, so eligibility is the thread's own shape rather\n"
    u"     than a setting: Corbin owns the story, Sparr carries messages past it,\n"
    u"     Pell is in Corvus's orbit. Extend the object to widen it.\n"
    u"     BEFORE the King branch on purpose - these three carry the ledger thread\n"
    u"     and everyone else carries the royal one, so the two run in parallel\n"
    u"     through different mouths instead of one starving the other.\n"
    u"     Deliberately absent from _dlgAmbient: the room at large has no business\n"
    u"     knowing this, and ambient talk has no speaker to qualify. */\n"
    u"  if(!row&&_DISCREPANCY_SPEAKERS[key])row=_dlgPick('reaction:discrepancy',stage,run._dlgHeard);\n"
    u"  if(!row)row=_dlgPick('reaction:king',stage,run._dlgHeard);",
    'P629 wire the thread into _dlgSay')

sub(u"function _dlgSay(id){",
    u"/* P629: who can credibly carry the Discrepancy. See the note in _dlgSay. */\n"
    u"var _DISCREPANCY_SPEAKERS={corbin:1,sparr:1,pell:1};\n"
    u"function _dlgSay(id){",
    'P629 eligibility list')

# ── the content ──────────────────────────────────────────────────────────
T1 = [
 "Corbin's been quieter than usual at the counting house. Something's off there.",
 "Heard the books didn't balance this month. First time in years, they say.",
 "Corvus is asking more questions than usual. Never a good sign, that.",
 "Something's not adding up in Corvus's ledgers. Literally, from what I hear.",
 "The counting house had its door locked longer than usual last week.",
 "Word is a sum's gone missing somewhere in Corvus's books.",
 "Corbin looked like he hadn't slept. Something's wrong over there.",
]
T2 = [
 "Wonder if someone's skimming. Wouldn't be the first.",
 "Corvus finding a shortfall would explain why he's been extra sharp lately.",
 "If Corbin's covering for someone, that's not like him at all.",
 "Bet it's nothing. Corvus finds these things eventually.",
 "Whoever's responsible better hope Corvus doesn't find them first.",
 "Corbin's too precise to make an error like that himself. Has to be someone else.",
 "Maybe it's not theft. Maybe just bad bookkeeping, for once.",
 "I'd hate to be whoever owes Corvus money right now, with him already on edge.",
 "Sparr's been carrying more messages than usual between the counting house and the Hall. Interesting timing.",
 "If it's a debtor covering their tracks, Corvus will find the thread eventually. He always does.",
 "Corbin's reputation's on the line if this doesn't get sorted quietly.",
 "Wonder how much is actually missing. Nobody's said a number.",
 "Could just be a clerical slip. Could also be something worse.",
 "Corvus doesn't miss much. Whoever did this picked the wrong ledger to touch.",
 "I heard it's not coin missing, just numbers that don't match. Different problem, maybe worse.",
]
T3 = [
 "Turned out to be an honest error. Corbin fixed it himself, mortified the whole time.",
 "Never did find out what really happened with Corvus's books. Some things stay buried.",
 "Corbin's back to his usual precise self. Whatever happened, it's handled.",
 "Heard Corvus quietly wrote it off. Strange, for him. Makes you wonder.",
]

rows = []
for t in T1:
    rows.append("  {p:'reaction:discrepancy',s:0,tag:'discrepancy_intro',g:'discrepancy-intro',t:%s}," % json.dumps(t))
for t in T2:
    rows.append("  {p:'reaction:discrepancy',s:0,c:['heard:discrepancy_intro'],g:'discrepancy-speculation',t:%s}," % json.dumps(t))
for t in T3:
    rows.append("  {p:'reaction:discrepancy',s:0,c:['heard:discrepancy_intro','night_gte:4'],g:'discrepancy-resolution',t:%s}," % json.dumps(t))

end = s.index('\n];', s.index('var PATRON_LINES=['))
block = (u",\n  /* \u2500\u2500 P629 (Part 8): THE DISCREPANCY \u2500\u2500 a second gated thread.\n"
         u"     Same three-tier machinery as the King: an untagged tier 1 that sets\n"
         u"     `discrepancy_intro`, a tier 2 gated on having heard it, and a tier 3\n"
         u"     gated on that AND night_gte:4. _dlgPick prefers MOST conditions, so\n"
         u"     once night 4 arrives the resolution outranks the speculation and the\n"
         u"     story ENDS - where the King's permanently deflates. Two threads that\n"
         u"     both trailed off would read as one mechanism in different words.\n"
         u"     The per-run no-repeat and the tag both come free: _dlgSay already\n"
         u"     records reaction:* lines and any tagged row. \u2500\u2500 */\n"
         + u"\n".join(rows).rstrip(',') + u"\n")
s = s[:end] + block + s[end:]

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d wiring edits + %d thread lines (%d/%d/%d per tier)'
      % (n, len(rows), len(T1), len(T2), len(T3)))
