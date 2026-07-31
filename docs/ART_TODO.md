# Missing artwork — tracking list

**Source of truth is `Art/`.** `assets/` holds the previous version's art and is
not what this list is about — an earlier version of this doc audited `assets/`
and produced 44 entries, 42 of which were legacy cards from a game that no
longer exists. Ignore that number; this is the corrected list.

Checked by listing `Art/Assets/**` against the ids the game actually defines.

---

## Family cards — 2 missing

`Art/Assets/Cards/<Family>/card_face_<id>.png`

- [ ] **steady_hand** (Silver)
- [ ] **fair_trade** (Silver)

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
