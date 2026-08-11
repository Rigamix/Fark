# -*- coding: utf-8 -*-
"""P622 (Part 5): all eight bosses' stage-1 pools, grouped for the de-dup.

Stage 0 is left exactly as it is - the brief is explicit that the fires-once
lines are unchanged. Everything here is s:1, which is the "second time onward"
pool _dlgOutcome selects once run._dlgWL has advanced.

EVERY ROW CARRIES `g`. That label is the whole point of P621: without it the
resolver cannot tell that "Hm. As expected." and "Noted. Moving on." are the
same beat wearing different words, which is exactly the failure a 20-line pool
introduces and a 2-line pool could not.

KEYS VERIFIED AGAINST THE BUILD, not taken from the brief: _bossKey returns
aldric/ambrose/brutus/corvus/finnick/grog/mabel/whisper, and boss:<key>:<win|loss>
pools already exist for all eight. Content written to a name the game does not
use would parse, ship, and never fire.
"""
import io, os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')

B = {}


def add(boss, outcome, group, lines):
    B.setdefault((boss, outcome), []).extend((group, l) for l in lines)


# ── CORVUS ────────────────────────────────────────────────────────────────
add('corvus', 'win', 'cold-arithmetic', [
    "The numbers agreed with me again. They usually do.",
    "Arithmetic doesn't lie. Yours, apparently, does.",
    "Simple sums, tonight. They favored the house.",
    "Knew this before the first roll. Didn't even need to sit down for it."])
add('corvus', 'win', 'ledger-callback', [
    "Another entry, same column as the last one.",
    "I've stopped needing to check the book. I already know where this lands.",
    "My ledger's getting thick with your name in it.",
    "Filed, same as always. I'll copy it fresh into the new book come spring."])
add('corvus', 'win', 'prediction-confirmed', [
    "Exactly as calculated. I don't often need to revise.",
    "Same result as last time. I wrote it down then, too.",
    "I'd have wagered on this outcome. I did, in fact, before you sat down.",
    "Expected. I find that comforting, oddly."])
add('corvus', 'win', 'player-as-asset', [
    "You're a reliable line item at this point. I mean that as a compliment, in my way.",
    "Consistent losses make for a tidy account. Yours especially.",
    "I could set a clock by how this goes with you."])
add('corvus', 'win', 'cold-dismissal', [
    "Hm. As expected.", "Noted. Moving on.", "That's settled, then. Next."])
add('corvus', 'win', 'plain-acknowledgment', [
    "Fine.", "Very well.", "As expected, I suppose."])

add('corvus', 'loss', 'recalculating', [
    "Revising my figures. Again. This is becoming a pattern.",
    "My estimate of you needs adjusting. Upward, apparently.",
    "Didn't account for that. I'll fix the figures tonight, over supper.",
    "Recalculating. Give me a moment, this doesn't happen often."])
add('corvus', 'loss', 'anomaly-discomfort', [
    "You're becoming difficult to price. I don't care for that.",
    "An anomaly, still. A persistent one, now.",
    "You're the reason I'll be re-reading old pages tonight instead of sleeping.",
    "I'll be thinking about this over supper. Don't take that as flattery."])
add('corvus', 'loss', 'cost-tracking', [
    "That's coin I'll need to recover. I always do, eventually.",
    "Noted as a loss. I intend to balance it elsewhere.",
    "You've cost me again. I'm keeping a tally, don't worry."])
add('corvus', 'loss', 'grudging-cold-respect', [
    "Competent. I don't say that often, or lightly.",
    "You're better than the average. I've updated the file accordingly.",
    "Fine. That was earned, not lucky. I can tell the difference."])
add('corvus', 'loss', 'dismissive-irritation', [
    "Hm. Irritating, but noted.", "Unwelcome. I'll move past it.",
    "Fine. Fine. Onto the next figure."])
add('corvus', 'loss', 'plain-acknowledgment', [
    "Well.", "So be it.", "Noted, I suppose."])

# ── GROG ──────────────────────────────────────────────────────────────────
add('grog', 'win', 'gruff-dismissal', [
    "Hmph. Same as always.", "There it is again.", "Right, that's done."])
add('grog', 'win', 'losing-streak-callout', [
    "That's, what, three in a row now? Losing count.",
    "You keep sitting back down. I keep taking your coin. Fine by me.",
    "Some folk learn. You're taking your time about it."])
add('grog', 'win', 'tavern-business', [
    "Pour you an ale on the house. Won't fix the losing, but it'll help.",
    "Table's mine tonight. Same as most nights, with you.",
    "Coin's good either way. Keep 'em coming."])
add('grog', 'win', 'backhanded-needling', [
    "You're good company, if nothing else.",
    "At least you're not boring about it.",
    "Keep coming back, I'll keep letting you."])
add('grog', 'win', 'plain-acknowledgment', [
    "Great.", "There we are.", "Right, then."])

add('grog', 'loss', 'grudging-acceptance', [
    "Fine. Again. Don't let it go to your head.",
    "Alright, alright. You've got my measure tonight.",
    "Hmph. Same as last time, then."])
add('grog', 'loss', 'coin-focused', [
    "That's coin out of my pocket again. Lucky I like you.",
    "Costing me a fair bit lately, you are.",
    "Good thing I water down the ale, or I'd be in trouble."])
add('grog', 'loss', 'reluctant-respect', [
    "You're not bad at this. Don't tell the others I said that.",
    "Alright. Earned that one fair.",
    "Not luck this time. I'll give you that much."])
add('grog', 'loss', 'plain-acknowledgment', [
    "Very well then.", "Fair enough.", "So be it."])

# ── MABEL ─────────────────────────────────────────────────────────────────
add('mabel', 'win', 'motherly-worry', [
    "Oh, you again. I do worry, dear, I really do.",
    "Back so soon. Are you eating enough, at least?",
    "There, there. Happens to the best of us, now and again."])
add('mabel', 'win', 'food-focused', [
    "Sit down, I'll bring you something warm. Won't fix the run of luck, but it helps.",
    "You look like you need a proper meal more than a win, if I'm honest.",
    "I've got stew on. Have some, you'll feel better either way."])
add('mabel', 'win', 'gentle-teasing', [
    "Persistent little thing, aren't you.",
    "Same result as always. Bless you for trying, though.",
    "You do keep coming back. I admire that, sort of."])
add('mabel', 'win', 'plain-acknowledgment', [
    "There now.", "Well, alright then.", "There we go."])

add('mabel', 'loss', 'warm-surprise', [
    "Well! You again. And winning, this time.",
    "Goodness. Twice now, is it?",
    "Aren't you full of surprises tonight."])
add('mabel', 'loss', 'motherly-pride', [
    "I am a little proud, dear. Don't tell the others.",
    "Look at you. Someone's been practicing.",
    "Alright, alright. You've earned a proper compliment this time."])
add('mabel', 'loss', 'food-focused', [
    "Well, you've earned a proper meal tonight, at least.",
    "Winning AND hungry, I'd wager. Sit, I'll fix that second part.",
    "Good result. Have a bit extra on the house, go on."])
add('mabel', 'loss', 'plain-acknowledgment', [
    "Well done.", "There now.", "Good for you."])

# ── FINNICK ───────────────────────────────────────────────────────────────
add('finnick', 'win', 'trick-of-the-trade', [
    "Same trick, works every time. Not my fault you keep falling for it.",
    "Palm's quicker than your eye. Always has been.",
    "Told you, I don't need a new trick if the old one's still working."])
add('finnick', 'win', 'unbothered-shrug', [
    "Didn't even have to try tonight.", "Easy one. Onto the next.",
    "Suits me fine, either way it goes."])
add('finnick', 'win', 'light-teasing', [
    "You're making this too easy on me, you know.",
    "Almost feel bad. Almost. Then I remember the coin's mine now.",
    "Keep coming back. I like the company, honestly."])
add('finnick', 'win', 'plain-acknowledgment', [
    "There we go.", "Same as always.", "Alright then."])

add('finnick', 'loss', 'grudging-business-concern', [
    "You're bad for business, you know that?",
    "Word gets around if I keep losing to the same face. Not good for me.",
    "Can't keep letting this happen. Bad for the reputation."])
add('finnick', 'loss', 'new-trick-needed', [
    "Need a new approach for you, clearly. The old one's worn out.",
    "You've seen through it twice now. Time to learn something new.",
    "Back to the drawing board with you, apparently."])
add('finnick', 'loss', 'casual-respect', [
    "Alright, you're good. I'll say it once.",
    "Fair play. Didn't see that one.", "Not bad. Not bad at all."])
add('finnick', 'loss', 'plain-acknowledgment', [
    "Fine.", "There you go.", "Alright then."])

# ── BRUTUS ────────────────────────────────────────────────────────────────
add('brutus', 'win', 'drilling-metaphor', [
    "Drill's not done till it's done right. Back to it.",
    "Repetition's how you learn. We'll keep repeating, then.",
    "Still counting wrong. We'll fix that eventually."])
add('brutus', 'win', 'soldier-address', [
    "Soldier, you're not listening. Try again.",
    "Same lesson, different night. Pay attention this time.",
    "You're slow to learn, but you keep showing up. That counts for something."])
add('brutus', 'win', 'plain-military', [
    "As expected.", "Discipline holds.", "Noted. Next round."])
add('brutus', 'win', 'plain-acknowledgment', ["Good.", "Fine.", "Right."])

add('brutus', 'loss', 'grudging-training-update', [
    "Reassessing your training again. You're improving, soldier.",
    "Twice now. I'll need to adjust the drills.",
    "You're learning faster than most. Noted."])
add('brutus', 'loss', 'fair-acknowledgment', [
    "Fair fight. I don't begrudge a fair loss.",
    "Earned, that. I'll say so plainly.",
    "Good work. Don't let it go to your head."])
add('brutus', 'loss', 'plain-military', ["Noted.", "Acceptable.", "So be it."])
add('brutus', 'loss', 'plain-acknowledgment', ["Fine.", "Alright.", "Very well."])

# ── ALDRIC ────────────────────────────────────────────────────────────────
add('aldric', 'win', 'formal-judgment', [
    "The verdict stands the same as it did last time.",
    "Judgment rendered, same as always.",
    "The lesson repeats. Perhaps it will take, eventually."])
add('aldric', 'win', 'quiet-lesson', [
    "Another quiet lesson. Take it home with thee this time.",
    "Thou'rt slow to learn this one. No matter. I've the patience.",
    "The same confession awaits thee. Best get it over with."])
add('aldric', 'win', 'concrete-detail', [
    "Sit, and I'll pour thee something for the walk home.",
    "Same seat, same result. I'll have it noted before thou'st risen.",
    "The candle's near out. Confess quickly, and we're both to bed sooner."])
add('aldric', 'win', 'plain-acknowledgment', ["So it stands.", "As before.", "Very well."])

add('aldric', 'loss', 'formal-concession', [
    "I confess it, as is only fair.",
    "Bested twice. I'll not pretend otherwise.",
    "The lesson was mine to receive, this time."])
add('aldric', 'loss', 'growing-respect', [
    "Thy cleverness wants no further quieting from me, it seems.",
    "A worthy match, this. I'll say so plainly.",
    "I begin to look forward to these, truth be told."])
add('aldric', 'loss', 'concrete-detail', [
    "Pour thyself a cup. Thou'st earned it tonight.",
    "Sit a moment longer. The win's earned a proper pause.",
    "I'll mark this one in ink, not chalk. It deserves it."])
add('aldric', 'loss', 'plain-acknowledgment', ["So be it.", "Fair enough.", "Very well."])

# ── WHISPER ───────────────────────────────────────────────────────────────
add('whisper', 'win', 'knowing-amusement', [
    "Knew how this would go before you sat down.",
    "Mm. As I expected. I usually am.",
    "Predictable. I do enjoy being right about people."])
add('whisper', 'win', 'secretive-detail', [
    "I noticed something in your hands tonight. Won't say what.",
    "There's a tell in how you hold those dice. I'll keep it to myself, for now.",
    "You gave something away that round. I'm not telling you what."])
add('whisper', 'win', 'detached-observation', [
    "Same result, different night. Comfortable, in its way.",
    "Watched this coming three rolls back.",
    "Nothing surprising here. A shame, honestly."])
add('whisper', 'win', 'plain-acknowledgment', ["There we are.", "As expected.", "Mm. Fine."])

add('whisper', 'loss', 'genuine-interest', [
    "Twice now. You're becoming genuinely interesting to me.",
    "I don't often get surprised. Noted, and appreciated.",
    "You're worth watching more closely now. I intend to."])
add('whisper', 'loss', 'cautious-respect', [
    "Careful. I'm starting to take you seriously.",
    "Well played, twice over. I'll remember your face.",
    "Dangerous, you turning out to be good at this."])
add('whisper', 'loss', 'detached-observation', [
    "Unexpected, again. Rare, that.",
    "Didn't see that one coming. Refreshing, actually.",
    "Mm. Surprised me. Doesn't happen often."])
add('whisper', 'loss', 'plain-acknowledgment', ["Well played.", "Noted.", "Fine, then."])

# ── AMBROSE ───────────────────────────────────────────────────────────────
add('ambrose', 'win', 'the-house-remembers', [
    "The house remembers this table. You're becoming a fixture of it.",
    "Another name added to a long list. The house keeps good count.",
    "The house has seen your face enough times now to know it well."])
add('ambrose', 'win', 'grave-formal', [
    "As it was, so it is again.",
    "The reckoning holds the same shape tonight.",
    "Noted, and recorded, same as every time."])
add('ambrose', 'win', 'concrete-detail', [
    "Light a candle on your way out. It's tradition, for the losing side.",
    "The wine's poured already. Have a cup before you go.",
    "Same seat next time, if you're returning. It suits you."])
add('ambrose', 'win', 'plain-acknowledgment', ["So it stands.", "Noted.", "Very well."])

add('ambrose', 'loss', 'the-house-notices', [
    "The house is taking notice of you now. That's not nothing.",
    "Twice bested. Your name travels further than it did.",
    "Not forgotten by morning, this one. Rare, that."])
add('ambrose', 'loss', 'grave-acknowledgment', [
    "A fair reckoning. I'll not dispute it.",
    "The table turned. I accept it as given.",
    "Earned, that. I don't say it lightly."])
add('ambrose', 'loss', 'concrete-detail', [
    "Pour yourself the good wine tonight. You've earned the better bottle.",
    "Take the seat by the fire on your way out. Small comfort, but real.",
    "I'll light the candle myself, this time."])
add('ambrose', 'loss', 'plain-acknowledgment', ["So be it.", "Noted.", "Fair enough."])

# ── emit ──────────────────────────────────────────────────────────────────
s = io.open(P, encoding='utf-8', newline='').read()
start = s.index('var PATRON_LINES=[')
end = s.index('\n];', start)

# every key must already exist as a pool, or the content is unreachable
existing = set(re.findall(r"\{p:'([^']+)'", s[start:end]))
rows, seen = [], set()
for (boss, outcome) in sorted(B):
    pool = 'boss:%s:%s' % (boss, outcome)
    if pool not in existing:
        sys.exit('POOL DOES NOT EXIST: %s' % pool)
    for g, t in B[(boss, outcome)]:
        if (pool, t) in seen:
            sys.exit('DUPLICATE LINE in %s: %r' % (pool, t))
        seen.add((pool, t))
        rows.append("  {p:'%s',s:1,g:'%s',t:%s}," % (pool, g, json.dumps(t)))

# THE SEAM NEEDS A LEADING COMMA: the row this block follows does not carry
# a trailing one, so without this the array gets two entries side by side.
block = (u",\n  /* ── P622 (Part 5): BOSS STAGE-1 POOLS ──────────────────────────\n"
         u"     Stage 0 is untouched; these are the \"second time onward\" lines\n"
         u"     _dlgOutcome reaches once run._dlgWL has advanced for that boss and\n"
         u"     that direction. Every row carries `g`, the sentiment group P621's\n"
         u"     resolver uses to stop two lines that mean the same thing landing\n"
         u"     back to back - which a 2-line pool never needed and a 20-line one\n"
         u"     does. Pool names checked against the pools that already exist, so\n"
         u"     none of this can be written to a key the game never asks for. ── */\n"
         + u"\n".join(rows) + u"\n")

io.open(P, 'w', encoding='utf-8', newline='').write(s[:end] + block + s[end:])
print('P622: %d boss lines added across %d pools' % (len(rows), len(B)))
