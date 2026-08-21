# Phase 5 — Observers. Measured: already built, now enforced.

The plan: *"Structurally enforces 'feats must never grant power' — currently a
rule we remember, afterwards a thing the architecture won't allow. Cheapest
phase, best ratio."*

**Both halves already held.** The gap was that nothing asserted them, so a
regression would have been silent. Rerun with `tools/p5_observers.py`; pinned by
`tools/apv_observers.js`.

## Feats — done

- **23 feat checks**, every one invoked as `f.check(_featView(G))` — **1 gated
  call site, 0 raw**.
- **0 checks read a field the view does not carry.** `_featView` copies 19
  fields plus a frozen `S.run`.
- The Proxy throws on set *and* delete, and nested objects are frozen — so
  `view.run.gold = -1` is a no-op rather than a write.

## Dialogue — already satisfied, by shape rather than by facade

`DLG` reads exactly **`G.rung`** and **`S.npcLedger`**, and **writes `G` zero
times**. It is **push-based**: 24 trigger names, all fired as
`DLG.trigger('NAME')` by game code that already detected the situation. It never
inspects state to decide, so there is nothing for a facade to protect.

`dlgFlags` is a save/restore snapshot (L10285 writes it, L31536 restores it),
not a live condition layer — worth noting because it looks like one.

## What was actually missing

**Nothing asserted either property.** A new feat check invoked with raw `G` would
have worked. A `DLG` method that started writing `G` would have worked. Both are
exactly the silent-regression shape this codebase keeps producing.

`apv_observers` pins six things, and the write test is **real rather than a
source scan** — it takes the actual view and tries to write through it, so a
Proxy quietly replaced by a plain object fails the check. A grep would not
notice.

| check | |
|---|---|
| `viewRefusesWrite` | the Proxy throws at runtime |
| `viewRefusesDelete` | so does delete |
| `nestedFrozen` | `run` is frozen, not just the top level |
| `allChecksGated` | 1 gated site, 0 raw |
| `dlgWritesNothing` | 0 `G` writes across every `DLG` method |
| `dlgIsPushBased` | `DLG.trigger` takes a name |

## Status

**Phase 5 is complete.** It was the plan's "cheapest phase, best ratio" and the
reason is now visible: the architecture had already grown the right shape, and
the work was measuring that honestly and pinning it before something drifted.
