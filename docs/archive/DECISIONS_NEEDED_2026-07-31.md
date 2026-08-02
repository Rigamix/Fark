# Decisions — answered 2026-07-31, and what is genuinely still open

Denis answered by revising `FARK_MASTER_BRIEF.md` and
`FARK_ENCHANT_BADGE_REWORK.md` rather than by replying, so **the briefs are the
ruling** and both are now in `docs/briefs/`. This file is kept as the record of
what was asked and what came back.

---

## ANSWERED — all seven

| # | Question | Ruling |
|---|---|---|
| 1 | Amber's Break turn never has to end | **One bust, not the whole turn.** Rec A taken. The brief now says the old wording was "an unbounded row in a table of otherwise single, bounded, one-time effects, which is structurally why it broke this badly. Now a one-shot like its five siblings." |
| 2 | Fair Trade → Break costs no die | **A borrowed die is an illegal Break target, full stop.** Rec A taken. This also STRIKES section 4b's "the lane persists, benched die returns immediately, stay at 6" ruling. Natural shatter of a borrowed die is explicitly unchanged. |
| 3 | The six briefed brands are a net downgrade | **Deferred to a pricing pass, not dismissed.** Open item 3: "All seven new enchant gold prices are placeholders, need a dedicated pricing pass." Section 4's Break timing finding is re-stated as protected: do not average the two numbers, do not make Break net-positive across a match — that would destroy the skill expression. |
| 4 | The loadout costs more than the game pays out | **Partly** — same pricing pass. The brand-refund-on-die-purchase half was not addressed; still open below. |
| 5 | Still Waters isn't the counter the brief claims | **Hush by material family, not by `d.ench`.** Rec A taken, and my re-opening of it is explicitly overruled: "DECISIONS_NEEDED separately re-opened this as an unmade choice — it isn't one." Break's guaranteed family trigger must be suppressed too, relics included. |
| 6 | Difficulty stops climbing after tier 3 | **Not addressed** in this revision. Still open below. |
| 7 | Starstone's flat +500 — *the one this list missed* | **Gate it on the Starstone die being part of the kept and scored selection.** Rec A taken. The brief calls it "the single most severe finding across the whole sim pass — it stopped mattering who was playing", and notes the fix makes it suppressible by Still Waters for the first time. |

### Also closed, unasked

- **PRECEDENCE IS NOW STATED**, which was section 9 of `FEEL_2026-07-31.md` and
  upstream of several arguments. The master brief is foundational, not final;
  five later documents win on any topic they cover. It also admits plainly that
  the line-by-line pass to strike the stale text this implies is **not done**,
  and flags it as owed work rather than assuming it complete.
- **Kindred's "double strength" is defined per enchant** — Ward two-thirds
  instead of a half; Snare halves twice on the same shot; Snuff and Fog extend
  to two turns; Break and Trade never double. Open item 1 closed.
- **Cursed seat, not sealed seat** — the lore brief's purple smoke wins, and
  the master brief is patched to match. No wax, no ribbons, no badge object.
  The Tankard is retired from that role and survives as tavern flavour.
- **Silver's regression target is a ratio** (~0.55× bone), not the brittle
  ~26% absolute — matching what the wider sweep measured.

---

## STILL OPEN

1. **Refund the brand when its die is replaced.** Buying a die silently deletes
   that slot's brand with no refund, so the correct purchase order is
   dice-then-brands — the order that guarantees brands never get bought. In
   practice a dedicated shopper reaches 2.0 of 6. Worth doing independently of
   the pricing pass.
2. **Difficulty is flat from tier 3 to tier 7** (30.8 / 33.0 / 36.4 / 33.9 /
   32.3). Late matches aren't harder, they're longer: cap-decided endings go
   0.3% → 85.5% because targets climb 5,000 → 9,500 while opponent bank barely
   moves. The master brief's own instruction is "Tune TARGETS down before
   inflating player scoring."
3. **First Strike — the brief asks for a decision and does not make one.**
   "This is weaker and less interesting than the original race concept — worth
   a real decision on whether it's still worth keeping in this reduced form or
   should retire back toward something else, rather than quietly shipping a
   downgrade nobody signed off on."
4. **Corvus's lost economy tax.** In Arrears was the only gold-drain in the
   roster; nothing taxes gold now. Flagged as needing a new home if missed.
5. **The enchant pricing pass** (open item 3), which items 3 and 4 above both
   feed into.
6. **The stale-text pass on the master brief**, which the brief itself flags as
   owed: the old enchant menu, old Silver pricing, Renown's mechanical perks,
   dead boss-tell UI references, and the BOOKKEEPER feat — which still awards
   for "Bookends pays three times in one match" although Bookends was collapsed
   into Vanguard, so it is unreachable.

---

## Not a decision — a harness bug, now fixed

`tools/sim_harness.js` wrote `_enchTradeV=2` where the shipped migration guard
is `!==1`, so it tripped the guard instead of satisfying it: every `{t:'trade'}`
brand was nulled and refunded 350g before a match ran. It was also
order-dependent — `_wardOwned` calls `_enchInit`, so the migration fired
mid-loop and ate only the Trade brands sitting before the first Ward in the
spec. Fixed, and `buildLoadout` now reports `lost` beside `refused` so a
silently-emptied lane can never be measured again. **Anything Trade-flavoured
in `SIM_RESULTS_2026-07-31.md` still needs re-running.**
