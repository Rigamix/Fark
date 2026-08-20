# Boss greeting lines — full set, all history states

First-ever-meeting lines from earlier are included for completeness.
Three new states per boss, three lines each: undefeated (boss has won
every meeting so far), first loss (this is the first sit-down since
the player's first win), repeated losses (player has beaten them more
than once). Same voice-consistency standard as the win/loss expansion
— every line pulled from that boss's already-established register,
not invented fresh.

---

## GROG

**First meeting:** "Haven't seen you at my table before. Sit down, then. Let's see what you've got."

**Undefeated:** "Back again? Suit yourself. Table's always warm for you." / "Still trying, are you. Respect that, actually." / "Hah. Same face, same table. Sit."

**First loss:** "So. Beat me once. Don't let it go to your head." / "Huh. Wasn't expecting that. Sit, we'll see if it was luck." / "Well, well. Look who's got some nerve now."

**Repeated losses:** "You again. Starting to think I'm the easy night." / "At this rate you'll own the place. Sit down." / "Fine, fine. Let's see if tonight's different."

## MABEL

**First meeting:** "New face. Don't get many of those. Sit, dear — I don't bite, the dice might."

**Undefeated:** "Back again, dear? I do worry about you." / "Oh, you're persistent. Sit, I'll get you something warm." / "Still coming back for more. Bless you."

**First loss:** "Well! Look who's feeling proud of themselves. Sit anyway." / "So you've got some fight in you after all. Good. Sit." / "My, my. Didn't see that coming from you."

**Repeated losses:** "You again, and still winning. I'm almost proud." / "At this point I ought to start taking you seriously." / "Back to try your luck again? Sit, dear."

## FINNICK

**First meeting:** "Don't think we've played. Good. Means you don't know my tricks yet."

**Undefeated:** "Back for more? Suit yourself." / "Same trick, same table. Sit down." / "Still trying. Respect the persistence, honestly."

**First loss:** "Huh. Got the better of me once. Don't get used to it." / "Well, that's new. Sit, let's see if it sticks." / "So you've got some skill after all. Noted."

**Repeated losses:** "You're becoming a genuine problem for my business. Sit." / "At this rate I'll need a new trick. Or a new table." / "Back again. Guess I'm paying you tonight too."

## CORVUS

**First meeting:** "No record of you here. Let's start one, then."

**Undefeated:** "Another entry, same column. Sit." / "The numbers haven't favored you yet. Sit anyway." / "Predictable. Sit, let's continue the pattern."

**First loss:** "An anomaly. I'll be recalculating. Sit." / "Unexpected. Noted. Sit, we'll see if it repeats." / "My figures needed adjusting after last time. Sit."

**Repeated losses:** "You're becoming difficult to price. Sit anyway." / "I've revised my estimate of you twice now. Sit." / "An anomaly, still. A persistent one. Sit."

## BRUTUS

**First meeting:** "New recruit. Sit. We'll see what you're made of."

**Undefeated:** "Back for more drilling? Good. Sit." / "Still haven't learned the count. Sit, we'll try again." / "Soldier, you're persistent. Sit down."

**First loss:** "Fair fight, soldier. Sit, let's see if it holds." / "Earned that one. Don't let it go to your head. Sit." / "Hm. Noted. Sit, soldier."

**Repeated losses:** "You're drilling well. Sit, I'll allow this once more." / "Reassessing your training. Sit down." / "Still winning, are you. Sit. We'll fix that."

## ALDRIC

**First meeting:** "Thou art unknown to me. Sit, and we shall remedy that."

**Undefeated:** "Thou returnest, still unconfessed. Sit." / "Persistence is its own small virtue. Sit." / "The same lesson awaits thee. Sit."

**First loss:** "Well struck. I confess it plainly. Sit." / "A worthy match, that. Sit, let's see if it repeats." / "Thy cleverness surprised me. Sit."

**Repeated losses:** "Thy cleverness wants no further quieting from me. Sit." / "I begin to look forward to these. Sit." / "Twice bested. Sit, let's make it thrice."

## WHISPER

**First meeting:** "A new face. How rare. Let's see if you're worth remembering."

**Undefeated:** "Back again. I do love a repeat performance. Sit." / "Predictable. Sit, I usually am right." / "Same result, different night. Sit."

**First loss:** "Oh. Well played. I'll remember that. Sit." / "Unexpected. I do enjoy being surprised. Sit." / "Huh. You've got my attention now. Sit."

**Repeated losses:** "You're becoming genuinely interesting to me. Sit." / "I'm starting to take you seriously. Dangerous, that. Sit." / "Careful. I'm watching you closer now. Sit."

## AMBROSE

**First meeting:** "The house doesn't know your name yet. Sit. We'll see if it should."

**Undefeated:** "The house remembers your name. Sit." / "Back to be reckoned with again. Sit." / "The house has seen your face enough times now. Sit."

**First loss:** "A fair reckoning. I'll not pretend otherwise. Sit." / "The table turned. Noted. Sit." / "Earned, that. Sit, we'll see if it holds."

**Repeated losses:** "The house is taking notice of you now. Sit." / "You're no longer a name I'll forget by morning. Sit." / "Twice bested my table. Sit. Let's make it thrice."

---

## Total

8 bosses × (1 first-meeting + 3 states × 3 lines) = 80 lines. Same
resolver mechanism as everything else tonight handles selection
within each state — no new plumbing needed beyond wiring these into
the boss `:open` pool with the appropriate history condition per
state, same pattern P833 already built for the first-meeting case.
