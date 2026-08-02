# Feats — the art and the code are two different rosters

Counted off `Art/Assets/Feats/` and the shipped `FEATS` array, not reasoned.
Self-contained; paste it on its own.

**24 paintings. 32 shipped feats. 12 mapped — and most of those 12 are mapped to
the wrong thing.**

---

## 1. The mapped twelve are mostly MISMATCHED IN MEANING

This is the part that matters most, and it isn't a gap — it's twelve paintings
already on screen illustrating something the feat doesn't award for. `FEAT_ART`
maps id → filename, and nothing ever checked that the picture and the condition
agree.

| Painting | Brief says it means | Mapped to | Which actually awards for | |
|---|---|---|---|---|
| `Death&Taxes` | **Beat Ambrose** | `beat_corvus` | Beating **Corvus** | ✗ wrong boss |
| `Teetotaller` | **Never bank under 500** | `beat_grog` | Beating **Grog** | ✗ unrelated |
| `Bookkeeper` | **Bookends pays 3× in a match** | `five_banker` | Five banks in a match | ✗ unrelated |
| `CleanNight` | **Clear a night, zero seat losses** | `no_busts` | Win without busting | ✗ different scope |
| `TheCollector` | **Hold four badges at once** | `card_collector` | A full hand of cards | ✗ badges vs cards |
| `ThreeTorches` | **Win a night with 3 obsidian dice** | `hot_storm` | Hot Storm | ✗ unrelated |
| `LastManSitting` | **Win a sudden-death turn** | `survivor` | Survivor | ? plausible |
| `LongRoad` | **Win from 2,000+ behind** | `persistent` | On a Roll | ? plausible |
| `SecondWind` | **Win the night after LAST ORDERS** | `comeback` | Comeback | ? plausible |
| `Barehands` | **Beat a boss with all-bone dice** | `naked_run` | Naked Run | ✓ |
| `FirstBlood` | **First boss badge taken** | `first_blood` | First Blood | ✓ |
| `HighRoller` | **A single bank of 2,500+** | `high_roller` | High Roller | ✓ |

**Three clean, three plausible, six wrong.** `Death&Taxes` on Corvus is the
clearest: the painting is Ambrose's, and Ambrose is the final boss.

## 2. Twelve paintings with no feat at all

These are the brief's §8 list. The art exists; the code has no such id.

`ForKeeps` · `FullBloom` · `GreenThumb` · `HisOwnMedecine` · `NoClaim` ·
`OmensTrue` · `OwnTheNight` · `PowderMonkey` · `SlowBoiled` · `StickyFingers` ·
`TwiceSaved` · `WishGranted`

From the brief: GREEN THUMB (bank a straight completed by a jade wild), FULL
BLOOM (Bloom fires three times), SLOW BOILED (a turn of six or more rolls),
STICKY FINGERS (win with Tar Pit on the opponent twice), TWICE SAVED (two
bust-saves then win), NO CLAIM (win holding Insurance, never busting), POWDER
MONKEY (bank a shatter's +1000), WISH GRANTED (chain two Falling Star extra
turns), OMENS TRUE (win on a correct Ill Omen call), FOR KEEPS (win a dice
stake), HIS OWN MEDICINE (beat a boss on rematch wearing his badge), OWN THE
NIGHT (win the run).

**Note:** several depend on content that has since moved — NO CLAIM needs
Insurance-the-card (retired), BOOKKEEPER needs Bookends (collapsed into
Vanguard). So a few can't be restored as written even if the roster is chosen.

## 3. Twenty shipped feats with no painting

`crushing_win` · `lightning_round` · `big_turn` · `no_actives` · `full_straight` ·
`boss_slayer` · `hot_hand` · `one_turn_wonder` · `tempting_fate` ·
`brinksman_feat` · `boss_crusher` · `two_bosses` · `quick_climb` · `five_bosses` ·
`beat_mabel` · `beat_finnick` · `beat_brutus` · `beat_aldric` · `beat_whisper` ·
`beat_ambrose`

Six of those are per-boss feats — and the art set contains only one boss-specific
painting (`Death&Taxes`, Ambrose's), currently pointed at Corvus.

## RULED — Option 1, the brief's 24

Denis, and the reasoning corrects my framing: **this was never a coin flip
between three even options.** The 24 was the original authored scope — 24
achievement pins, two sheets of 12, planned early. **The 32 in code is drift, not
a deliberate expansion anyone decided on.** Feats are permanently
non-power-granting wall decoration, so there is no gameplay argument for a bigger
number, only an art-budget one, and the art budget already said 24.

**The six mismatched mappings resolve as a side effect, not as a separate fix.**
They only exist because the current twelve are guesses against the wrong list.
Restore the list and Death&Taxes is naturally Ambrose's condition, Teetotaller is
naturally the bank-threshold one. Fix the roster, the mappings follow.

### Three things that ride along

1. **BOOKKEEPER is already retired**, ruled earlier this session — Bookends'
   collapse into Vanguard was a deliberate simplification and is not being
   reversed. This document treated it as open because it predates that ruling.
   **That leaves 23 usable conditions and one orphaned painting** with no natural
   home under current mechanics. Small residual, not a blocker.
2. **NO CLAIM gets its condition rewritten, not cut.** It references
   Insurance-the-card, which is gone, but what it rewarded — defensive,
   bust-averse play — still exists via Ward. Rewrite against Ward; exact wording
   is a follow-up.
3. **The six per-boss `beat_<boss>` feats are cut**, and that is real content
   loss worth naming rather than hiding inside "rewriting 20 conditions". If
   dedicated per-boss recognition matters, it wants its own future category with
   its own art ask — not a reason to keep the drifted 32.

### The work, sized

- Replace `FEATS` (32 rows) with the brief's list (23 live + 1 parked).
- Remap `FEAT_ART` — which becomes near-total by construction, since the
  paintings and the roster finally describe the same set.
- Rewrite NO CLAIM against Ward.
- Rerun `apv_table_totality.js`: `FEAT_ART` should go from 12/32 to 23/23, and
  the baseline will prove it.

**Not started in the session that recorded this ruling** — it is a content change
across the whole feat list, and beginning it without room to finish is how a
half-migration happens.

## (superseded by the ruling above) What this needs from you

Not an engineering fix — **a decision about which roster is real.**

1. **The brief's 24** — restore the feat list to §8 and every painting has a
   home. Costs: rewriting 20 shipped conditions, and a few reference retired
   content.
2. **The shipped 32** — commission ~20 paintings, retire 12 existing ones.
3. **The intersection** — keep only feats that have art and a working condition;
   smallest list, no waste, but drops most of the shipped roster.

**Regardless of which:** the six mismatched mappings in §1 are wrong under *any*
of the three and should be corrected or unmapped now. A painting of Ambrose
awarded for beating Corvus is wrong in every world.

## How this was missed

`FEAT_ART` maps id → filename and nothing verified the pair meant the same
thing. Phase 2's totality assertion caught that the table was *incomplete*; it
cannot catch that an entry is *wrong*, because both sides exist. Totality is not
correctness — noted as a limit in the Phase 2 report, and this is what that limit
looks like in practice.
