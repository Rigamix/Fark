# Missing artwork — tracking list

**Source of truth is `Art/`.** `assets/` holds the previous version's art and is
not what this list is about — an earlier version of this doc audited `assets/`
and produced 44 entries, 42 of which were legacy cards from a game that no
longer exists. Ignore that number; this is the corrected list.

Checked by listing `Art/Assets/**` against the ids the game actually defines.

---

## Family cards — DONE (was 2 missing)

`Art/Assets/Cards/<Family>/card_face_<id>.png`

- [x] **steady_hand** (Silver) — added 2026-07-31
- [x] **fair_trade** (Silver) — added 2026-07-31

**Every live family card now has art.** Verified against the game's own path
(`assets/cards/<id>.webp`) across all 31 FAM_LIVE ids; the only two without a
file are `anchor_f` and `bookends_f`, which are aliases onto `vanguard_f` and
need none.

Note the masters arrived camelCase (`card_face_steadyHand.png`,
`card_face_FairTrade.png`) where every other card is snake_case
(`card_face_ward.png`). Harmless, but any future script deriving a card id from
a filename will trip on those two.

Both are Silver, and the gap has an obvious cause: the rework RETIRED
Ward-the-card and Insurance-the-card and replaced them with these two.
`Art/Assets/Cards/Silver/` still holds `card_face_ward.png` and
`card_face_insurance.png` — art for the two cards that left — and nothing for
the two that arrived.

These are the only ones that visibly break. `famCardArt` has no `onerror`
fallback (unlike `_cardArtImg`, which removes its own `<img>` so the emoji
swatch shows), so today they paint a broken-image glyph. A code-side fallback is
in the current sweep; resolution 10 says do both, so the art is still wanted.

**Art that exists for cards no longer live** — not needed, just noting so they
aren't mistaken for current work: `tar_pit` (Amber), `cultivate` (Jade),
`insurance` + `ward` (Silver), `tamper` (Vagabond).

---

## Still on old art — flagged 2026-07-31

**The game's match table is the previous version's.** `fark_proto.html` renders
`assets/Environment_ART/match.png` — 1064x1920, dated 07-11 — while the current
master is `Art/Assets/Match/Commoner/Table_new.png` at 1080x2011 (07-27). The
props lab was pointed at `TableLit.png` (07-20) and is now on `Table_new.png`;
the game itself was not touched, because repointing it changes the look of every
match and that is a call rather than a fix.

## Everything else is complete

| | |
|---|---|
| Badges | 8/8 — including TheTippedScales |
| Enchant icons | 8/8, plus 8 store icons and the panel |
| Patron characters | 24 |
| Traits | 7 |
| Dice | Bone only, and that is correct — materials are skinned from `assets/models/dice/skins.js` and family colours, not per-family art files |

---

## Two naming mismatches worth knowing about

The card id and the art filename disagree for two live cards. They resolve today,
but anything that maps id → filename mechanically will miss them:

| card id | art filename |
|---|---|
| `fools_gold_f` | `card_face_fools_gold.png` |
| `vanguard_f` | `card_face_vanguard.png` |

Related: `anchor_f` and `bookends_f` look like artless cards in any id-based
audit. They are aliases onto `vanguard_f` (`_FAM_ALIAS`, the vanguard collapse),
so they need no art of their own.

---

## Note on the enchant icons

They ship as `.png` and never went through the optimize pass every other picture
gets — no `optimized/` webp copies at the top level of `Art/Assets/Enchants/`
(the `storeIcons/` subfolder does have one). Worth a pass.
