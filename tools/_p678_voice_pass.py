# -*- coding: utf-8 -*-
"""P678: the dialogue voice pass - FARK_DIALOGUE_VOICE_PASS.md applied in full.

Denis: "rewrite all dialogues to match this doc. You can see the vibe, creative
guideline and examples but you need to do a COMPLETE pass on all dialogues."

WHAT THE DOC CORRECTS, in its own words: backstory was "reflective statements
about a trait" and should be "a complaint, a family detail, a small thing that
happened"; reactions were "composed sentences with rhetorical shape" and should
be "short, blurted... genuinely no longer than" a 'you suck' or 'awww shucks'.

WHAT THIS REPLACES, counted before touching:
  - trait:* - 36 pools, 108 lines: the doc's text VERBATIM (its BULLISH is the
    file's `strong`, per the existing note at the table head).
  - patron:<name> backstory - 29 pools: the doc's 23 verbatim (Golgoth down to
    his single "...Fine." - the doc is explicit that three lines would undo
    him; Remny up from 2 to the doc's 3), plus SIX the doc scopes out (Twill,
    Fenn, Ferrand, Odo, Ollis, Tam) written here by the doc's own method -
    from their real existing lines (Fenn's chipping bone dice, Ferrand's boot
    and Bruiser, Ollis's shield fund and the trapper debt, Odo's traplines,
    Tam and Tuck's kitchen rivalry, Twill's weaving) in the doc's formula:
    complaint / family detail / small thing that happened.
  - patron:<name>:win|:loss - the end-of-match barks, 5+5 per patron (Golgoth
    2+2), rewritten as blurts in each voice. The old pools carried lines like
    "Leather doesn't rush, and neither did that." - exactly the composed
    register the doc retires.

WHAT THIS DOES NOT TOUCH, deliberately: the two bespoke overrides
(patron:sil:bust, patron:regis:bank - already blurt-length and in voice), the
boss pools (16 pools, 274 lines - heavy established characters the doc does
not cover; rewriting them ungrounded is the exact "invented-voice problem" the
doc warns it corrected once already), and gossip:town (already concrete
complaints in the doc's register). The boss question goes to OPEN.md.

SLANG, per the doc's own note: sparing. "Fark!" once (the doc's BULLISH bust),
Roller/bust-hand/born-rolling-ones only where the doc placed them plus two
voice-fitting spots in the barks - not spread evenly, which would make it a
tic.

Rows keep the table's shape: flat s:0, and every line gets its own `g` slug so
P621's no-repeat rule keeps two consecutive picks different.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

# ── the new material ────────────────────────────────────────────────────
TRAITS = {
 'steady': {
  'bust':     ["Ah, well.", "That's that, then.", "Meh. Happens."],
  'yourBust': ["Aww, hard luck.", "Oh dear.", "Better luck next time."],
  'bank':     ["There we go.", "Nice and steady.", "Told you."],
  'yourBank': ["Huh. Nice one.", "Alright, alright.", "Fair play."],
  'push':     ["Hm. One more?", "Let me think.", "Careful, now."],
  'banksafe': ["Might be more here.", "Small bank's still a bank.", "Hm. Tempting."]},
 'strong': {  # the doc's BULLISH
  'bust':     ["Fark! Should've stopped.", "Ah, damn it.", "One more would've done it."],
  'yourBust': ["Ha! Knew it.", "Told you so!", "Bust-hand!"],
  'bank':     ["That's how it's done.", "Beat that.", "Watch and learn."],
  'yourBank': ["Huh. Not bad.", "Okay, fine, that one's good.", "Lucky."],
  'push':     ["One more. Just one.", "Fine, let me think for once.", "...go again. Probably."],
  'banksafe': ["Feels small to stop at.", "Banking's boring.", "Ugh. Fine. Maybe."]},
 'orderly': {
  'bust':     ["Miscalculated that.", "Hm. Noted.", "Off by one roll."],
  'yourBust': ["Predictable.", "Math doesn't lie.", "As expected."],
  'bank':     ["Exactly as planned.", "Precise.", "As projected."],
  'yourBank': ["An outlier.", "Statistically unlikely.", "Huh. Noted."],
  'push':     ["Recalculating.", "Give me a second.", "The numbers are close here."],
  'banksafe': ["Checking the odds.", "Close call, this one.", "One moment."]},
 'reckless': {
  'bust':     ["Worth it though.", "Roller take it.", "Should've pushed further, honestly."],
  'yourBust': ["Ha! Greedy!", "Told you to stop!", "Classic."],
  'bank':     ["That's the way!", "Now we're talking!", "See? Worth the risk."],
  'yourBank': ["Okay, that was good.", "Nice risk.", "Huh. Bold."],
  'push':     ["...actually thinking about this one.", "Huh. Even I pause sometimes.", "That's a lot on the table."],
  'banksafe': ["Banking feels wrong.", "Every instinct says push.", "Fighting myself here."]},
 'greedy': {
  'bust':     ["My coin!", "Ow. That hurt.", "There goes the profit."],
  'yourBust': ["My coin now.", "Ha. Your loss, my gain.", "Couldn't resist, could you."],
  'bank':     ["Now we're talking.", "Coin's coin.", "Lovely."],
  'yourBank': ["Huh. Nice haul.", "Not bad, for you.", "Fine, fine."],
  'push':     ["That's real coin sitting there.", "Could double it. Could lose it.", "Hm. Tempting."],
  'banksafe': ["Feels small to walk away with.", "Bird in hand, though.", "Weighing it."]},
 'cunning': {
  'bust':     ["Mm. Saw that coming.", "As expected.", "Huh."],
  'yourBust': ["Mm. Knew it.", "Predictable, that.", "Saw that coming."],
  'bank':     ["As planned.", "Mm. Nice.", "There we go."],
  'yourBank': ["Huh. Interesting.", "Born rolling ones, you.", "Noted."],
  'push':     ["Calculating something.", "Worth a moment, this.", "Hm."],
  'banksafe': ["Might know something you don't.", "Weighing it.", "A pause, here."]},
}

BACKSTORY = {
 'krox':    ["Smell doesn't wash out. Wife hates it.",
             "Dropped a whole hide in the river last week. Still not over it.",
             "Regis talks enough for both of us."],
 'eira':    ["Wrote three love letters this week. None of them mine.",
             "Nebb keeps getting mistaken for me. We don't even look alike.",
             "Charge extra if you make me spell it out twice."],
 'nebb':    ["Sat still for a whole minute once. Nearly died.",
             "Everyone thinks I'm Eira. We don't even look alike.",
             "Got three jobs done before breakfast. Bored already."],
 'regis':   ["Someone has to announce things properly around here.",
             "Wife says I talk too much. She's probably right.",
             "Grog never thanks me for keeping order. Rude, honestly."],
 'corbin':  ["Back hurts from all this bending over ledgers.",
             "Corvus docked my pay for a miscount once. Never again.",
             "Son wants to be a clerk too. Talked him out of it."],
 'sparr':   ["Ran here from the other side of town. Barely out of breath.",
             "Boots wore through again. Third pair this year.",
             "Dog waits for me by the gate every evening."],
 'pell':    ["Cut my thumb again. Happens every week.",
             "Sold an arrow to a man who couldn't even draw a bow.",
             "Daughter wants to learn the trade. Good, someone should."],
 'osgood':  ["Rilla fusses over me like I'm made of glass.",
             "Knees ache when it rains. Every time.",
             "Tell people I fought in a war. Mostly true."],
 'rilla':   ["Uncle won't admit his knees hurt. Stubborn old man.",
             "Stall made good coin today. Enough for a new shawl.",
             "Told him to see a healer. He won't listen."],
 'dunstan': ["Burned my sleeve again. Third shirt this month.",
             "Nobody thanks a smith till something breaks.",
             "Son's too small for the hammer yet. Give it time."],
 'rask':    ["Shoulder's been aching since that job last week.",
             "Got paid in chickens once. Never again.",
             "Mother still thinks I'm a farmhand."],
 'sil':     ["Ran out of the good bandages again.",
             "Everyone thinks I can cure a hangover. I can't.",
             "Cat knocked over my whole shelf this morning."],
 'thorne':  ["Town's too loud for my taste.",
             "Tracked a deer for three days. Lost it anyway.",
             "Dog's better company than most people here."],
 'vess':    ["Sold rope to a man who owned a ship. Still laughing about that.",
             "Daughter haggles better than I do already.",
             "Everything's got a price. Even silence, sometimes."],
 'nell':    ["Squib still hasn't learned to bluff.",
             "Won my first hand at six years old. Never stopped.",
             "Half this town's bust-hands. I just don't say it to their face."],
 'squib':   ["Nell never lets me win. Not once.",
             "Practicing every night. Getting better, I swear.",
             "Owe half the tavern money. Don't tell Nell."],
 'tuck':    ["Bread didn't rise right this morning. Annoying.",
             "Tam's stew isn't that good. Don't tell her I said so.",
             "Fed three generations of this family. Still going."],
 'mudge':   ["River nearly took my hat again.",
             "Carried the same gossip twice this week. Different story each time, though.",
             "Wife says I smell like fish. I do."],
 'nix':     ["Blamed for every bad hand at this table.",
             "Didn't ask for this reputation. Roller's own luck, apparently.",
             "Cat won't even come near me anymore."],
 'poll':    ["Told someone the wrong name again today.",
             "Peck says I get his stories backwards. Probably true.",
             "Wife corrects me mid-sentence. Every time."],
 'roan':    ["Ran four errands before noon. Legs hurt.",
             "Innkeep forgot to pay me again. Third time this month.",
             "Dog follows me on every errand now."],
 'golgoth': ["...Fine."],
 'remny':   ["Remember you from Tuesday. Or someone like you.",
             "Owe me a drink. Or I owe you one. Not sure.",
             "Never forget a face. Get the details wrong, though."],
 # the six the doc scopes out - written by its method, from their real lines
 'twill':   ["Snapped a warp thread this morning. Whole row wasted.",
             "Mother wove for the old lord. Never lets anyone forget it.",
             "Sold a bolt with a crooked seam once. Still think about it."],
 'fenn':    ["Chipped another bone die last night. Third this month.",
             "Brother says I baby them. He plays iron, what does he know.",
             "Traded two good hides for this set. Worth it. Mostly."],
 'ferrand': ["Bruiser's had my boot a week now. A week.",
             "Wife says let it go. It's the principle of the thing.",
             "Won that boot fair at this very table. Ask anyone."],
 'odo':     ["Line froze over twice this week. Twice.",
             "Sister keeps asking when I'll move to town. Never, is when.",
             "Fox got into the bait store again. Clever thing. Hate it."],
 'ollis':   ["Shield fund's nearly there. Don't ask the number.",
             "Father never owned a shield his whole life. First in the family, me.",
             "Counted my coin three times last night. Same number. Still checked."],
 'tam':     ["Pot boiled over the second I sat down. Typical.",
             "Tuck thinks his bread carries the kitchen. Sweet of him.",
             "Someone sent back my stew once. Once."],
}

# end-of-match barks: win = the patron beat you, loss = you beat them.
# Blurts, in each voice. Golgoth stays nearly silent by design.
BARKS = {
 'krox':    (["Figured.", "There it is.", "Mm.", "No fuss, that.", "Right."],
             ["Huh.", "Fair enough.", "Caught me still.", "Well. That happened.", "Yours, then."]),
 'eira':    (["Signed and sealed.", "Read you easily.", "Knew the ending early.", "Filed away.", "Predictable post."],
             ["Well. Revising my notes.", "Didn't see that line coming.", "Hm. New ink needed.", "Yours. This once.", "Huh."]),
 'nebb':    (["Ha! Quick hands.", "Done and done.", "Next game?", "Easy. What else?", "That all?"],
             ["Ugh. Sat still too long.", "Again. Now.", "Fluke!", "Fine. Rematch.", "Bah."]),
 'regis':   (["As announced.", "Order prevails.", "Naturally.", "The table thanks me.", "Noted for the record."],
             ["Unannounced, that.", "The record will show... hm.", "Disorderly result.", "I demand a recount.", "Well."]),
 'corbin':  (["Balanced.", "The ledger agrees.", "Accounted for.", "Sum checks out.", "Filed."],
             ["An error somewhere.", "Doesn't balance.", "I'll find the miscount.", "Hm. Audit later.", "Unfiled, that."]),
 'sparr':   (["Beat you to it.", "Quick one, that.", "Done. Where next?", "No contest.", "Ran that one clean."],
             ["Caught me flat.", "Ah, well. Can't win 'em all.", "You're quicker than you look.", "Fine run.", "Huh."]),
 'pell':    (["Flew true.", "Clean shot.", "Straight to the mark.", "Feathers good, that one.", "There it is."],
             ["Wide of the mark.", "Bad feathers tonight.", "Missed clean.", "Hm. Warped shaft.", "Yours."]),
 'osgood':  (["Old tricks hold.", "Still got it.", "That's how we did it back when.", "Ha. Not dead yet.", "There now."],
             ["Ah, the knees of it.", "You'd have lost to me once.", "Hm. Age, that is.", "Fair fight.", "Rilla won't hear of this."]),
 'rilla':   (["There now.", "Good coin, that.", "Stall's buying the next round.", "Ha. Easy.", "Sweet enough."],
             ["Oh, fine.", "Uncle will laugh at this.", "Well played, then.", "Hmph. Sweetly done.", "This once."]),
 'dunstan': (["Held.", "Good iron, that.", "Forged well.", "Solid.", "That's the temper."],
             ["Cracked.", "Back to the forge.", "Soft metal tonight.", "Hm. Brittle.", "Yours, fair."]),
 'rask':    (["Job's done.", "Paid in full.", "Easy work.", "That's the shift.", "Done clean."],
             ["Hm. Rough shift.", "No pay for that one.", "Chickens again, then.", "Fair hit.", "Ow."]),
 'sil':     (["Prognosis: mine.", "Healthy result.", "No cure for that.", "Take two of those.", "Clean bill."],
             ["That stung.", "Physician, heal thyself, aye.", "No bandage for pride.", "Well struck.", "Hm."]),
 'thorne':  (["Tracked. Taken.", "Quiet does it.", "Clean kill.", "Mm.", "Done."],
             ["Lost the trail.", "Missed my mark.", "Loud in here. My excuse.", "Well hunted.", "Hm."]),
 'vess':    (["Profit.", "Sold high.", "The ledger smiles.", "Good trade, for me.", "Ka-ching, as they say."],
             ["A loss. It happens. Rarely.", "Bad investment, that.", "Hm. Market turned.", "Well bargained.", "Costly."]),
 'nell':    (["Read you three rolls back.", "Never bluff a bluffer.", "House rules: I win.", "Sharp, me.", "Mm. Easy table."],
             ["Ha. Well played.", "Didn't see the hand for once.", "Squib will never let this go.", "Sharp of you.", "Hm. Rare, that."]),
 'squib':   (["I WON? I won!", "Wait till Nell hears!", "Practice pays!", "Ha! Finally!", "That's one for me!"],
             ["Aw, come on.", "Every time.", "Nell's fault. Somehow.", "One day. One day.", "Ugh."]),
 'tuck':    (["Proofed and baked.", "Rose nicely, that.", "Fresh out the oven.", "Done to a turn.", "There's the crust."],
             ["Flat loaf, that.", "Oven's off tonight.", "Burnt it.", "Hm. Needs salt.", "Yours."]),
 'mudge':   (["Current carried me.", "Smooth crossing.", "Both banks, no trouble.", "Ferry's paid.", "There's the shore."],
             ["Choppy, that.", "Took on water.", "Current turned.", "Lost my hat AND the game.", "Hm."]),
 'nix':     (["Luck's mine tonight. For once.", "Don't blame me. Oh wait.", "Huh. It works for me too.", "The one kind of luck.", "There it is."],
             ["Of course.", "Typical.", "The usual luck, then.", "Blame me. Everyone does.", "Roller's little joke."]),
 'poll':    (["I won! ...I did win?", "That went how I said. Roughly.", "Ha! Or wait. Yes, ha!", "Good... game? Good game.", "There we... are?"],
             ["Lost? Thought I was winning.", "That's not how I heard it goes.", "Backwards again, then.", "Hm. Or did I?", "Ah well. Probably."]),
 'roan':    (["Job done.", "Quick, that.", "Back before dark, too.", "Easy run.", "Done and dusted."],
             ["Ah well. Still got legs.", "Slow tonight.", "Tripped at the line.", "Fair race.", "Hm."]),
 'golgoth': (["...Good.", "...Fine, that."],
             ["...Well.", "...Huh."]),
 'remny':   (["Knew I'd win. Remember it clearly.", "Same as Tuesday. I think.", "Told you this would happen. Didn't I?", "Familiar, this.", "Ha. Again."],
             ["Lost? Sure it was you who lost.", "Different from Tuesday, then.", "I remember this going better.", "Huh. New memory, that.", "If you say so."]),
 'twill':   (["Clean selvage.", "Thread held.", "Counted right.", "Neat work.", "There's the pattern."],
             ["Dropped a stitch.", "Crooked seam, that.", "Thread snapped.", "Hm. Unpicked.", "Yours, fair."]),
 'fenn':    (["Bones came through.", "No chips tonight.", "Good set, this.", "Rolled sweet.", "There they sing."],
             ["Chipped my luck.", "Bones went quiet.", "Iron would've done no better.", "Hm. Cold dice.", "Ah well."]),
 'ferrand': (["The boot comes home!", "That's for Bruiser.", "Principle wins.", "Ha! Justice.", "Mine, as it should be."],
             ["The boot stays lost.", "Bruiser will hear of this. Unfortunately.", "Not the principle of it!", "Hmph.", "This town, honestly."]),
 'odo':     (["Trap sprung.", "Patience, see.", "Caught clean.", "Good line tonight.", "That's the catch."],
             ["Slipped the trap.", "Clever thing, you.", "Bait's off.", "Hm. Like that fox.", "Fair catch."]),
 'ollis':   (["Coin for the shield!", "Fund grows!", "Closer now. Closer.", "Every coin counts.", "Ha! Saving's done it."],
             ["The fund weeps.", "Shield's further off now.", "Trapper gets paid last again.", "Ow. My savings.", "Counted wrong somewhere."]),
 'tam':     (["Seasoned right.", "Stew wins again.", "Simmered you slow.", "Taste that? Victory.", "Kitchen's still mine."],
             ["Oversalted that one.", "Pot got away from me.", "Tuck saw. Wonderful.", "Hm. Needs work.", "Cold serving, that."]),
}

# ── build the replacement block ─────────────────────────────────────────
def row(pool, g, t):
    t = t.replace('"', '\\"')
    return '  {p:\'%s\',s:0,g:\'%s\',t:"%s"},' % (pool, g, t)

out = []
out.append("  /* ═══ P678: THE VOICE PASS - FARK_DIALOGUE_VOICE_PASS.md applied in full.")
out.append("     Backstory: a complaint, a family detail, a small thing that happened.")
out.append("     Reactions and hesitation: short and blurted - talking, not writing.")
out.append("     The doc's 23 backstories verbatim; the six it scopes out (Twill, Fenn,")
out.append("     Ferrand, Odo, Ollis, Tam) written by its method from their real lines.")
out.append("     Barks are blurts in each voice, 5+5 (Golgoth 2+2 - near-silence IS his")
out.append("     design). Slang sparing, per the doc: Fark! once, Roller/bust-hand/")
out.append("     born-rolling-ones only where a trait or theme earns them. ═══ */")
for tr, moments in TRAITS.items():
    for mo, lines_ in moments.items():
        for i, t in enumerate(lines_):
            out.append(row('trait:%s:%s' % (tr, mo), 'v%d' % i, t))
for name, lines_ in BACKSTORY.items():
    for i, t in enumerate(lines_):
        out.append(row('patron:%s' % name, 'b%d' % i, t))
for name, (win, loss) in BARKS.items():
    for i, t in enumerate(win):
        out.append(row('patron:%s:win' % name, 'w%d' % i, t))
    for i, t in enumerate(loss):
        out.append(row('patron:%s:loss' % name, 'l%d' % i, t))
NEW = '\n'.join(out)

# ── remove the old rows ─────────────────────────────────────────────────
# Kept untouched: the two bespoke overrides, and every CONDITIONAL row
# (c:['heard:...'] / c:['boss_beaten:...']) - those are the King-arc and
# story callbacks, a separate mechanism the doc does not cover, and their
# lines are already blurt-length and in voice.
KEEP = ("{p:'patron:sil:bust'", "{p:'patron:regis:bank'", ",c:[")
pat = re.compile(r"^\s*\{p:'(?:trait:|patron:)[^']*'.*\},?\s*$")
lines = s.split('\n')
removed_trait = removed_patron = 0
kept = []
for l in lines:
    if pat.match(l) and not any(k in l for k in KEEP):
        if "{p:'trait:" in l:
            removed_trait += 1
        else:
            removed_patron += 1
        continue
    kept.append(l)
print('removed: %d trait rows, %d patron rows' % (removed_trait, removed_patron))
if removed_trait != 108:
    sys.exit('expected 108 trait rows, removed %d' % removed_trait)
if removed_patron != 600:
    sys.exit('expected 600 patron rows (602 minus 2 bespokes), removed %d' % removed_patron)
s = '\n'.join(kept)

# ── insert the new block after the bespoke overrides ────────────────────
anchor = "  {p:'patron:regis:bank',s:0,t:\"As I predicted. I predict many things.\"},"
c = s.count(anchor)
if c != 1:
    sys.exit('bespoke anchor x%d' % c)
s = s.replace(anchor, anchor + '\n\n' + NEW)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
n_new = len([l for l in out if l.lstrip().startswith('{p:')])
print('inserted %d rows' % n_new)
