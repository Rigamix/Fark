# -*- coding: utf-8 -*-
"""P626 (Part 6a): win/loss pools for the six patrons the brief never covered.

Twill plus the five who are DEALABLE AS OPPONENTS AND SILENT AT OUTCOME TIME -
fenn, ferrand, odo, ollis, tam have no patron:<key>:win or :loss pool at all, so
_dlgOutcome returns null for them and the caller falls back to a generic bark.
That is a content type the brief never checked existed.

WRITTEN FROM THEIR REAL LINES, which is the method the brief intended and did not
have available - each voice below is locked to what is actually in the build:
  TWILL    weaver. Seams, threads, patience-as-trade. "Patience isn't a virtue in
           my trade. It's the whole trade."
  ODO      trapper. Lives rough, dry about it, out of practice talking. "Talking's
           a skill I'm a bit rusty at, if it's not obvious."
  OLLIS    saving for a shield, in debt TO ODO, and refuses to hear the odds.
           "Don't tell me the odds, I don't want to hear them."
  FERRAND  bruiser. Owed things, unimpressed by rank. "Boot's mine. Bruiser owes
           me that much and worse besides."
  FENN     ONE existing line, about his dice chipping. Thin.
  TAM      ONE existing line, about the stew being worth the losing. Thin.

FENN AND TAM GET LESS, DELIBERATELY. Two groups per outcome instead of three,
because a single existing line is not enough to lock a voice from and writing
eighteen would be inventing a character rather than extending one. Flagged
rather than quietly padded.

OLLIS'S DEBT IS TO ODO - that link is already in the build ("Owe the trapper a
little still") and his loss pool uses it, so the two read as connected rather
than as two strangers who happen to share a table.
"""
import io, os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')

C = {}


def add(who, outcome, group, lines):
    C.setdefault((who, outcome), []).extend((group, l) for l in lines)


add('twill', 'win', 'even-seams', [
    "Even work. Nothing crooked in it.",
    "Straight through, start to finish. It shows.",
    "No pulled threads there. I'd have seen one."])
add('twill', 'win', 'patience-pays', [
    "Patience, that's all it was. Told you it's the whole trade.",
    "Took my time. Usually enough.",
    "No rushing it. There never is."])
add('twill', 'win', 'plain', ["There.", "Right.", "Good."])
add('twill', 'loss', 'dropped-stitch', [
    "A stitch went somewhere. I'll find where.",
    "Something pulled crooked. My hand, not yours.",
    "Missed a thread. It happens, even to careful people."])
add('twill', 'loss', 'unpick-and-learn', [
    "I'll unpick it tonight and learn the shape of it.",
    "Worth doing twice to get right. I'll take that.",
    "Noted. The next bolt comes out better."])
add('twill', 'loss', 'plain', ["Fair.", "Hm.", "Right."])

add('odo', 'win', 'trapline-patience', [
    "Traps teach you waiting. Same thing at a table.",
    "Set it, leave it, come back to it. Worked tonight.",
    "Out on the lines you wait days. This was quick by comparison."])
add('odo', 'win', 'gruff-dry', [
    "Aye. That'll do.",
    "Didn't need to say much for that one.",
    "Talking's still not my strength. This part I manage."])
add('odo', 'win', 'plain', ["Aye.", "Right.", "There."])
add('odo', 'loss', 'sprung-empty', [
    "Empty trap. Happens more than you'd think.",
    "Set it wrong somewhere. My doing.",
    "Walked back to nothing. Familiar enough feeling."])
add('odo', 'loss', 'unbothered-rough', [
    "No matter. I've had worse nights out there, and colder.",
    "Fair. Costs me less than a bad week on the lines.",
    "You'll not hear me complain about one night."])
add('odo', 'loss', 'plain', ["Aye.", "Hm.", "Fine."])

add('ollis', 'win', 'closer-to-the-shield', [
    "That's a bit more toward the shield.",
    "Closer now. Don't tell me how much closer.",
    "Every coin counts twice with me. That one counted twice over."])
add('ollis', 'win', 'debt-relief', [
    "Might pay the trapper back sooner than he expects.",
    "That's a little less owed. I hate owing.",
    "One thing settled. He'll not have forgotten, mind."])
add('ollis', 'win', 'plain', ["Right.", "Good.", "There."])
add('ollis', 'loss', 'shield-further-off', [
    "Shield's further off than it was this morning.",
    "That's coin I'd already counted twice.",
    "Further away now. I know. I know."])
add('ollis', 'loss', 'refusing-the-odds', [
    "Don't tell me the odds. I've asked you not to.",
    "I'd rather not hear what that one cost me.",
    "Fine. Doesn't change what I'm saving for."])
add('ollis', 'loss', 'plain', ["Fine.", "Hm.", "Alright."])

add('ferrand', 'win', 'fighter-plain', [
    "Went how it usually goes.",
    "No trouble in that one.",
    "Same as a fight. You land it or you don't."])
add('ferrand', 'win', 'what-im-owed', [
    "That's mine, then. I'll take what's owed.",
    "Good. I'm still owed elsewhere, mind.",
    "One thing settled. Plenty isn't."])
add('ferrand', 'win', 'plain', ["Right.", "Aye.", "There."])
add('ferrand', 'loss', 'took-the-hit', [
    "Took that one. Fine.",
    "Landed on me instead. Happens.",
    "Not the first hit I've taken. Won't be the last."])
add('ferrand', 'loss', 'no-grudge', [
    "Fair. I don't hold it against you.",
    "Clean enough. I'll allow it.",
    "You earned it. That's the whole of it."])
add('ferrand', 'loss', 'plain', ["Fine.", "Aye.", "Hm."])

# ── the two thin voices: two groups, not three ───────────────────────────
add('fenn', 'win', 'careful-with-them', [
    "Careful with them, that's all it takes.",
    "Treat them right and they'll treat you right.",
    "Mine are in good order. That helps more than luck."])
add('fenn', 'win', 'plain', ["There.", "Good.", "Right."])
add('fenn', 'loss', 'chipped-somewhere', [
    "One of them's chipped, I'd wager. I'll check tonight.",
    "Something's off in the set. Always is, when I lose.",
    "I'll look them over before I sleep."])
add('fenn', 'loss', 'plain', ["Hm.", "Fine.", "Alright."])

add('tam', 'win', 'staying-for-the-stew', [
    "Good. Still staying for the stew, mind.",
    "Won and fed. Can't ask much more of an evening.",
    "That's the night made, near enough."])
add('tam', 'win', 'plain', ["There we go.", "Good.", "Right."])
add('tam', 'loss', 'worth-the-losing', [
    "Worth the losing, like I said. Don't tell her I said it.",
    "Lost, but the stew's still on. Fair trade.",
    "I'll be back for the food regardless."])
add('tam', 'loss', 'plain', ["Ah well.", "Fine.", "Right."])

# ── emit, deduping against everything already in the table ───────────────
s = io.open(P, encoding='utf-8', newline='').read()
start = s.index('var PATRON_LINES=[')
end = s.index('\n];', start)
existing = set(re.findall(r"\{p:'([^']+)'[^}]*?t:\"(.*?)\"\}", s[start:end]))

rows, seen = [], set(existing)
for (who, outcome) in sorted(C):
    pool = 'patron:%s:%s' % (who, outcome)
    for g, t in C[(who, outcome)]:
        if (pool, t) in seen:
            sys.exit('DUPLICATE against the existing table: %s / %r' % (pool, t))
        seen.add((pool, t))
        rows.append("  {p:'%s',s:0,g:'%s',t:%s}," % (pool, g, json.dumps(t)))

block = (u",\n  /* \u2500\u2500 P626 (Part 6a): THE SIX THE BRIEF DID NOT COVER \u2500\u2500\n"
         u"     Twill, plus five who could already be dealt as opponents and had\n"
         u"     NO win/loss pool at all - _dlgOutcome returned null and the caller\n"
         u"     fell back to a generic bark. Voices locked to their real existing\n"
         u"     lines, not to a document. Fenn and Tam get two groups instead of\n"
         u"     three: one existing line each is not enough to write eighteen from,\n"
         u"     and padding them would be inventing a character. \u2500\u2500 */\n"
         + u"\n".join(rows).rstrip(',') + u"\n")

io.open(P, 'w', encoding='utf-8', newline='').write(s[:end] + block + s[end:])
print('P626: %d lines across %d new pools' % (len(rows), len(C)))
