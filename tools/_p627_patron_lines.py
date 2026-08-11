# -*- coding: utf-8 -*-
"""P627 (Part 6b): the brief's 23 patrons, placed against their real pools.

Flat pools, s:0, same shape as today - the brief is explicit there is no stage
split here. Every row carries `g` so P621's de-dup covers them.

DUPLICATES ARE REPORTED, NOT FATAL. If one of the brief's new lines is identical
to a line the patron already has, that is worth SEEING - it means the brief
rewrote something that already shipped - so those are skipped and listed rather
than aborting the run or silently doubling the line.

GOLGOTH IS THE DELIBERATE EXCEPTION and keeps it: three lines per outcome, no
sentiment groups, because his whole design is having almost nothing to say and
full volume would undo the joke. His existing 1+1 stays.

WHAT THIS DOES NOT DO: re-derive the voices. The brief locked them partly against
backstory lines that do not exist in this build (it assumed 6 per patron; there
are 3). The win/loss SHAPE it wrote to is correct, so placement is mechanical and
safe, but whether each voice is right is a reading pass for Denis - the diff is
the deliverable, not a claim that it is verified.
"""
import io, os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')

C = {}


def add(who, out, g, lines):
    C.setdefault((who, out), []).extend((g, l) for l in lines)


PLAIN = 'plain'

add('krox','win','quiet-acceptance',["Figured as much.","About what I expected.","Didn't need to watch closely to know that."])
add('krox','win','tanning-metaphor',["Leather doesn't rush, and neither did that.","Patient work wins out, same as always.","Slow and steady. Works on hides, works here too."])
add('krox','win',PLAIN,["There it is.","Right.","Yeah."])
add('krox','loss','mild-surprise',["Huh. Wasn't expecting that.","Didn't see that coming, and I usually do.","That one caught me still."])
add('krox','loss','unbothered',["Fair enough. Didn't see it coming.","No shame in it. Happens.","Outlasted me that round, fair play."])
add('krox','loss',PLAIN,["Alright.","Fine.","Huh."])

add('eira','win','letter-writer-callback',["Predictable. Could've written it down beforehand.","Noted, same as everything else I see.","I'll add that to what I already knew about you."])
add('eira','win','watchful-confidence',["Watched that coming three rolls back.","Told you I notice things. That's one of them.","No surprises. I don't get many, watching as close as I do."])
add('eira','win',PLAIN,["Noted.","There it is.","Fine."])
add('eira','loss','revising-notes',["Well. Revising my notes on you again.","That's going in the file, underlined.","I'll need a fresh page for you at this rate."])
add('eira','loss','rare-surprise',["Unexpected. I don't say that often.","Didn't see that written anywhere. My mistake.","You've surprised me. Doesn't happen twice a week."])
add('eira','loss',PLAIN,["Well.","Huh.","Alright."])

add('nebb','win','restless-triumph',["There we go. Sat still just long enough.","Told you I focus when it counts.","Quick as ever. Didn't even need to think about it."])
add('nebb','win','quick-confidence',["Course I did. Wasn't really in doubt.","Didn't need long for that one.","Done before you'd finished asking, near enough."])
add('nebb','win',PLAIN,["There we go.","Yeah.","Right then."])
add('nebb','loss','flustered',["Fark. Didn't see that coming.","Well, that's embarrassing.","Didn't sit still long enough to notice that one."])
add('nebb','loss','quick-recovery',["Won't happen twice. Onto the next.","Fine, fine, moving on already.","Already thinking about the next one, honestly."])
add('nebb','loss',PLAIN,["Huh.","Fine.","Alright then."])

add('regis','win','self-important',["As I predicted. I predict many things, you understand.","Precisely as I foresaw. I usually do.","I did call this. I call most things."])
add('regis','win','order-restored',["Order restored to this table, as it should be.","Standards upheld, same as always.","The table runs properly again. As I intended."])
add('regis','win',PLAIN,["As expected.","Naturally.","Indeed."])
add('regis','loss','grudging-permission',["An aberration. I shall permit it, this once.","I'll allow this. Once.","Unusual. I'm choosing to be gracious about it."])
add('regis','loss','surprised-pomposity',["Well played. Even I can be surprised, apparently.","Didn't foresee that. Rare, for me.","I'll admit it \u2014 you had me there."])
add('regis','loss',PLAIN,["Well.","Hm.","Fine, then."])

add('corbin','win','ledger-precision',["The numbers favored me. They usually do.","Balanced, same as every column before it.","Figures add up my way again."])
add('corbin','win','quiet-confidence',["Didn't need to check twice on that one.","Expected, and correctly so.","The sums were mine before we started."])
add('corbin','win',PLAIN,["As expected.","Noted.","Fine."])
add('corbin','loss','finding-the-error',["An error somewhere. I'll find it before I sleep.","Something didn't balance. I'll trace it back.","A miscalculation on my end. Embarrassing, but fixable."])
add('corbin','loss','discomfort-with-mess',["Unaccounted for. I don't care for that.","Messy result. I prefer tidy ones.","That doesn't sit right in the ledger. I'll deal with it."])
add('corbin','loss',PLAIN,["Hm.","Noted.","Well."])

add('sparr','win','speed-boast',["Ha, quick as ever.","Told you, I don't slow for anyone.","Fastest thing at this table tonight, and it wasn't the dice."])
add('sparr','win','on-the-move',["Already halfway to the next thing, honestly.","Didn't even need to sit down properly for that.","In and out, same as every delivery."])
add('sparr','win',PLAIN,["There we go.","Right.","Course."])
add('sparr','loss','rare-miss',["Didn't see that one coming, and I see most things coming.","Missed that. Doesn't happen often, to be fair.","Slower than me tonight, apparently. New feeling."])
add('sparr','loss','quick-recovery',["Fine, you're fast too. Noted, moving on.","Already onto the next stop, win or not.","No time to dwell on it. Never is."])
add('sparr','loss',PLAIN,["Huh.","Fair.","Alright."])

add('pell','win','arrow-craft',["Flew true. Same as always.","Straight as anything I've fletched.","No wobble in that one. Clean."])
add('pell','win','honest-work',["No surprises from an honest hand.","Nothing tricky about it. Just did the work.","Steady hand wins out, same as the trade."])
add('pell','win',PLAIN,["There it is.","Right.","Course."])
add('pell','loss','rare-miss',["Well. Even a good arrow misses sometimes.","Wobbled on that one. Happens.","Not every shaft flies true. Fair enough."])
add('pell','loss','fair-allowance',["Fair shot. I'll allow it.","Good aim, that. I'll say so.","Earned, not lucky. I can tell the difference in a shot."])
add('pell','loss',PLAIN,["Fair.","Hm.","Alright."])

add('osgood','win','old-hand-confidence',["Told you. Old hands still know a trick or two.","Experience wins out. Usually does, in my case.","Done this before. Longer than you've been alive, probably."])
add('osgood','win','gruff-deflection',["Don't read too much into it.","Wasn't luck. Wasn't magic either. Just done it before.","Nothing to make a story of. Just a win."])
add('osgood','win',PLAIN,["There it is.","Right.","Course."])
add('osgood','loss','fair-fight',["Hmph. Fair fight, that.","Well struck. Don't let it go to your head, mind.","No complaints. Won fair."])
add('osgood','loss','rilla-mention',["Rilla'll be pleased, at least.","She'll say I had it coming. She's not wrong, this time.","Won't hear the end of this from my niece, probably."])
add('osgood','loss',PLAIN,["Hmph.","Fine.","Alright."])

add('rilla','win','settled-and-moving-on',["There, that's settled then.","No hard feelings, I hope.","Good, that's done. Back to the stall for me."])
add('rilla','win','stall-practicality',["Can't stay long, the stall doesn't mind itself.","Told you I don't linger. Winning or not.","Good result. Now, back to actual work."])
add('rilla','win',PLAIN,["There now.","Right.","Good."])
add('rilla','loss','genuine-praise',["Oh! Well done, truly.","That's a good win, that is.","Proper good roll, that was."])
add('rilla','loss','warm-encouragement',["Don't be modest about it, go on.","You earned that, take the credit.","Enjoy it, you don't need my permission but you have it anyway."])
add('rilla','loss',PLAIN,["Well done.","Good for you.","There now."])

add('dunstan','win','forge-solid',["Solid work. Same as my forge.","No cracks in that outcome.","Held up fine. Good iron does that."])
add('dunstan','win','no-nonsense',["Simple result. Nothing complicated about it.","Didn't need to ask why. Just took it.","Straightforward. Like most good work."])
add('dunstan','win',PLAIN,["There it is.","Fine.","Good."])
add('dunstan','loss','weak-point-found',["Hm. Didn't see the weak point till it was too late.","Should've caught that earlier. Didn't.","There's always a flaw somewhere. Found mine tonight."])
add('dunstan','loss','taking-the-lesson',["Fair beating. I'll take the lesson.","Noted. Won't miss that again.","Good work, yours. I can respect good work."])
add('dunstan','loss',PLAIN,["Hm.","Fine.","Alright."])

add('rask','win','job-done',["That's the job done, then.","Nothing personal. Just work.","Finished clean. Same as always."])
add('rask','win','reliable-work',["Told you I'm reliable. That includes this table.","Didn't need to try hard. Wasn't much of a job.","Easy work tonight. Most of it is, honestly."])
add('rask','win',PLAIN,["Done.","Right.","Fine."])
add('rask','loss','grudging-acknowledgment',["Huh. Didn't expect that from you.","Didn't see that coming. Rare, for me.","You got the better of me. Noted."])
add('rask','loss','fair-pay',["Fine. You earned that one.","Fair's fair. That was earned.","Good work. I can respect that, even losing to it."])
add('rask','loss',PLAIN,["Huh.","Fine.","Alright."])

add('sil','win','no-curse-deflection',["No curse did that. Just good dice.","Wasn't magic. Was just a decent roll.","Nothing supernatural about it. Rarely is."])
add('sil','win','dry-diagnosis',["Nothing to fix here. You'll live.","You'll survive the loss. Probably.","Not fatal. Just a bad night for you."])
add('sil','win',PLAIN,["There it is.","Fine.","Right."])
add('sil','loss','self-deprecating',["Well. Bad luck and worse dice, this time mine.","Physician, heal thyself. Apparently not tonight.","Can't fix my own luck, turns out."])
add('sil','loss','rough-night',["Fair enough. I've had worse nights.","Not my best showing. Had better.","Long night. This didn't help."])
add('sil','loss',PLAIN,["Well.","Fine.","Huh."])

add('thorne','win','quiet-satisfaction',["Quiet win. Prefer it that way.","Didn't need to say much. The result speaks.","No noise needed. Just the outcome."])
add('thorne','win','result-speaks',["Don't need to explain it. It happened.","Speaks for itself, that.","Simple result. Simple as the woods, that way."])
add('thorne','win',PLAIN,["There it is.","Fine.","Good."])
add('thorne','loss','missed-it',["Hm. Missed that one.","Didn't track that coming. My mistake.","Lost the trail on that one, clearly."])
add('thorne','loss','rare-miss-hunter',["Fair. Even a good hunter misses sometimes.","Happens. Not often, but it happens.","Won't happen twice, probably. Probably."])
add('thorne','loss',PLAIN,["Hm.","Fair.","Alright."])

add('vess','win','good-for-business',["Good outcome for me. Better for my ledger.","Profitable night, this one.","Coin's coin. Tonight it's mine."])
add('vess','win','price-of-loss',["Everything has a price. Tonight, yours was steep.","You paid for that one. Fair terms, though.","Cost you something, that. Business is business."])
add('vess','win',PLAIN,["There it is.","Fine.","Good."])
add('vess','loss','absorbing-the-loss',["Well, that's a loss I'll have to absorb.","Cost me tonight. I'll recover it elsewhere.","Not every night's profitable. Tonight wasn't."])
add('vess','loss','fine-deal',["Fine deal, that. For you, anyway.","Good terms, on your end. I'll allow it.","You got the better price tonight. Rare."])
add('vess','loss',PLAIN,["Well.","Fine.","Alright."])

add('nell','win','cards-dont-lie',["Told you. Cards don't lie, and neither do I about my odds.","Read that from three moves out.","Not magic. Just paying attention."])
add('nell','win','watching-advantage',["Didn't need to cheat. Just watched close.","That's how it's done. Every time, near enough.","Told Squib the same thing. He still hasn't learned it."])
add('nell','win',PLAIN,["There it is.","Right.","Course."])
add('nell','loss','rare-miss',["Huh. Didn't see that coming, and I usually do.","Missed a read there. Doesn't happen often.","Slipped past me, that one."])
add('nell','loss','genuine-respect',["Well played. Genuinely.","That was earned, not lucky.","Good hand. I'll remember it."])
add('nell','loss',PLAIN,["Huh.","Fair.","Alright."])

add('squib','win','finally-not-nell',["HA! Finally! Someone besides Nell!","First time beating anyone that isn't my sister. Feels good.","Wait till Nell hears about this one."])
add('squib','win','proving-himself',["See, I'm not completely hopeless.","Told you I was getting better. Slowly, but still.","Practice is paying off. A little."])
add('squib','win',PLAIN,["There we go.","Yeah!","Right!"])
add('squib','loss','so-close',["Aw, come on. So close.","Nearly had it. Nearly.","One roll off. Story of my life, lately."])
add('squib','loss','grudging-fine',["Fine. FINE. You got me.","Alright, alright, you win this one.","Can't win 'em all. Wish I could, though."])
add('squib','loss',PLAIN,["Aw.","Fine.","Alright."])

add('tuck','win','bread-rising',["That's the bread rising, same as always.","Comes out right most nights. Tonight's one of them.","Good batch, this one. Same as the last few."])
add('tuck','win','feeding-everyone',["Good result. Good enough to celebrate with pie, maybe.","Feed you well either way, but tonight I'll add extra.","Winners eat the same as losers here. Just happier about it."])
add('tuck','win',PLAIN,["There it is.","Good.","Right."])
add('tuck','loss','bread-falls-flat',["Well, even good bread falls flat sometimes.","Doesn't always rise right. Tonight didn't.","Bad batch. Happens now and then."])
add('tuck','loss','feed-you-anyway',["Fair enough. Feed you extra next time, maybe.","Come by tomorrow, I'll make it up in stew. Or bread. Your choice.","Losing doesn't mean going hungry. Sit, I'll fix you a plate."])
add('tuck','loss',PLAIN,["Well.","Fine.","Alright."])

add('mudge','win','smooth-crossing',["Smooth crossing, that.","No surprises on the water tonight.","Calm current. Made for an easy trip."])
add('mudge','win','river-metaphor',["River was kind tonight. Not always the case.","Current favored me. Won't always.","Same as any good crossing. Steady, no surprises."])
add('mudge','win',PLAIN,["There it is.","Good.","Right."])
add('mudge','loss','rough-water',["Huh. Rough water, that.","Current turned on me. Happens out there too.","Choppier than I expected."])
add('mudge','loss','river-surprises',["Fair enough. Even the river surprises me sometimes.","Didn't see that current coming. Rare, for me.","The water's taught me humility more than once. Tonight again."])
add('mudge','loss',PLAIN,["Huh.","Fair.","Alright."])

add('nix','win','my-luck',["Told you. My luck, not yours.","Comes with me, this luck. Tonight it showed up.","Don't ask me to explain it. Just goes my way sometimes."])
add('nix','win','roller-favored',["The Roller favored me, this time.","She noticed me tonight, apparently.","Rare that it lands my way. Tonight it did."])
add('nix','win',PLAIN,["There it is.","Huh.","Right."])
add('nix','loss','luck-turned',["Ha! My own luck turned on me. Fitting, really.","Even my own luck doesn't always favor me. Ironic.","Turned on me tonight. Should've seen that coming, given the reputation."])
add('nix','loss','first-time',["Well, that's a first. Don't get used to it.","Doesn't happen often. Tonight it did.","Rare loss, that. Mark the occasion."])
add('nix','loss',PLAIN,["Well.","Huh.","Fine."])

add('poll','win','confidently-wrong',["Knew it'd go that way. Or something close to it.","Called it. Or I'm calling it now, works the same.","Told someone this would happen. Might've been you."])
add('poll','win','retroactive-telling',["Told everyone I'd win. Or I will, now.","By the time I tell this story, I'll have called it perfectly.","Ask me tomorrow, I'll remember predicting this exactly."])
add('poll','win',PLAIN,["There it is.","Right.","Course."])
add('poll','loss','hard-to-say',["Huh, didn't see that coming. Or maybe I did. Hard to say.","Might've called this too. Can't quite recall.","Saw it coming, probably. Details are fuzzy."])
add('poll','loss','straight-story',["Well, that's one story I'll tell straight, for once.","No need to embellish this one. Loss is a loss.","Won't need to change the details on this retelling."])
add('poll','loss',PLAIN,["Huh.","Well.","Fine."])

add('roan','win','job-done',["Job's done.","Simple as that.","Didn't need to think hard on it. Just did it."])
add('roan','win','simple-loyalty',["She'll be glad to hear it.","One more thing done right.","Don't need a reason to feel good about that."])
add('roan','win',PLAIN,["Done.","Right.","Good."])
add('roan','loss','mild-surprise',["Huh. Didn't expect that.","Wasn't looking for that outcome.","Caught me off guard, that one."])
add('roan','loss','back-to-work',["Fair enough. Back to my errands.","No time to dwell. Places to be.","Losing doesn't stop the work. Off I go."])
add('roan','loss',PLAIN,["Huh.","Fine.","Alright."])

add('remny','win','false-memory',["Knew I'd win. I remember it happening before, even.","Recall this exact outcome from last time. Or the time before. One of those.","Told you this would happen. I definitely told someone."])
add('remny','win','confident-mostly',["Course I won. I always do. Mostly.","Wasn't in doubt. Rarely is, in my memory of it.","Same as I remember every other time going."])
add('remny','win',PLAIN,["There it is.","Course.","Right."])
add('remny','loss','new-experience',["Well, that's new. Don't remember losing before.","Can't recall this happening. Must be a first.","Strange. Doesn't match anything I remember."])
add('remny','loss','remembering-wrong',["I'll remember this one, probably wrong, but I'll remember it.","Going in the memory, details subject to change.","By next time I'll recall this differently, probably better."])
add('remny','loss',PLAIN,["Well.","Huh.","Fine."])

# GOLGOTH: the deliberate exception - no groups, near-silence preserved
add('golgoth','win','golgoth',["...Yeah.","...Huh. Good.","...Fine, that."])
add('golgoth','loss','golgoth',["...Huh.","...Ah.","...Well."])

# ── emit ─────────────────────────────────────────────────────────────────
s = io.open(P, encoding='utf-8', newline='').read()
start = s.index('var PATRON_LINES=[')
end = s.index('\n];', start)
existing = set(re.findall(r"\{p:'([^']+)'[^}]*?t:\"(.*?)\"\}", s[start:end]))
pools_present = set(re.findall(r"\{p:'([^']+)'", s[start:end]))

rows, seen, skipped, missing = [], set(existing), [], []
for (who, out) in sorted(C):
    pool = 'patron:%s:%s' % (who, out)
    if pool not in pools_present:
        missing.append(pool)
    for g, t in C[(who, out)]:
        if (pool, t) in seen:
            skipped.append((pool, t))
            continue
        seen.add((pool, t))
        rows.append("  {p:'%s',s:0,g:'%s',t:%s}," % (pool, g, json.dumps(t)))

if missing:
    sys.exit('POOLS THAT DO NOT EXIST: %s' % ', '.join(missing))

block = (u",\n  /* \u2500\u2500 P627 (Part 6b): THE BRIEF'S 23 PATRONS \u2500\u2500\n"
         u"     Flat pools at s:0, the shape the brief specifies. Every row grouped\n"
         u"     for the de-dup. Golgoth keeps his deliberate near-silence: three\n"
         u"     lines an outcome and no sentiment split, because his whole design is\n"
         u"     having almost nothing to say.\n"
         u"     PLACEMENT is mechanical and safe - the pools were checked to exist\n"
         u"     first. Whether each VOICE is right is a reading pass, not a claim\n"
         u"     made here: the brief locked these voices partly against backstory\n"
         u"     lines this build does not have. \u2500\u2500 */\n"
         + u"\n".join(rows).rstrip(',') + u"\n")

io.open(P, 'w', encoding='utf-8', newline='').write(s[:end] + block + s[end:])
print('P627: %d lines added across %d pools' % (len(rows), len(C)))
if skipped:
    print('\nSKIPPED - identical to a line the patron already has (%d):' % len(skipped))
    for p, t in skipped:
        print('   %-22s %s' % (p, t))
