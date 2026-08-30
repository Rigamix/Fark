# -*- coding: utf-8 -*-
u"""P874 (VOICE PASS brief): the tavern stops talking like a costume drama.
Engine and words in one commit, because the brief is right that they cannot
ship apart.

WHAT THE BRIEF GOT RIGHT, ALL VERIFIED BEFORE A WORD WAS TYPED:
  * _dlgLastG really is keyed BY POOL, so a `g:'warned'` tag on a push line
    would have been invisible to a yourBust line and the seven best rows in
    the pass would have been silently dead. `say:` with its own store is the
    fix, and _DLG_COND.said must exist in the same commit or _dlgCondOk drops
    every gated row without a word.
  * Both patron doors really do pass null where the skip map goes - _dlgEvent
    and _dlgSay alike - so every bark has been drawn from the full pool every
    time. That is most of why they feel canned, and no amount of writing
    fixes it.
  * Peck really does have ZERO rows. Counted: 28 of 30 names carry 10-12,
    Golgoth 5, Peck none. The string does not occur in the file. He has been
    the one patron with no voice, falling through to trait:* forever.

WHAT THE BRIEF ASSUMES AND THE BUILD DOES NOT HAVE - and this is the one
thing to read before judging the result. The line tables use eight moments.
_DLG_MOMENT maps exactly seven categories, and only SIX of the eight are
among them:

    live now  bust  yourBust  bank  yourBank  push  banksafe
    no trigger        preroll   waiting

Nothing in the file fires a "patron is about to roll" or "player is taking
too long" event; there is no DLG category for either, so ~90 of these rows
cannot be reached today. They are shipped ANYWAY, complete and unedited,
because the brief says the engine changes live in FARK_DIALOGUE_BUILD.md
Part One and "stand unchanged" - I do not have that document, and inventing
the triggers would mean inventing a nag cadence, which is a design call and
Denis's. The moment Part One lands they are live with no further writing.
What must not happen is shipping them silently: the marker below, the entry
in docs/OPEN.md and the handover all name it.

`nv:1` on Golgoth's rows has no reader in this build either. Kept as written
- it is inert, not harmful, and it is clearly meant for a future non-verbal
styling - but his breathing renders as ordinary speech text today.

THE DE-DUP IS SOFT AND IT IS APPLIED AT THREE DOORS, not the brief's two.
_dlgAmbient passes null for gossip:town in exactly the same way, and the
gossip table is being rewritten in this same patch - fixing two of three
doors while rewriting the third's content would leave the new gossip
repeating for the same reason the old did. The guard never returns NO line:
it falls back to the full pool, because a de-dup that can empty the pool
turns a repeat into silence, which is worse. It stays OUT of _dlgPick, which
is shared - the story pools want the hard drop.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ══ 1. the `say:` store ═══════════════════════════════════════════════
sub(u"""var _dlgLastG={};
function _dlgResetGroups(){_dlgLastG={};}""",
    u"""var _dlgLastG={};
/* P874: WHAT WAS ACTUALLY SAID THIS MATCH. Module state beside _dlgLastG and
   cleared by the same reset, because it answers the same question - "did this
   happen in this match" - for two callers:
     keys that are line TEXT      -> the soft anti-repeat at the call sites
     keys that are 'said:<tag>'   -> what a later line may refer back to
   ONE map, not two. A second store for the second use is the defect this
   subsystem keeps growing. run._dlgHeard is the per-RUN, save()-backed set for
   story tags and is untouched by any of this.
   THE FIELD IS say:, NOT g:. `g` is the anti-repeat GROUP key above, and it is
   keyed by pool - so a g:'warned' on a push line would write under
   patron:krox:push and be invisible to a line reading patron:krox:yourBust.
   The gate would never open and nothing would error. */
var _dlgSaid={};
function _dlgResetGroups(){_dlgLastG={};_dlgSaid={};}""",
    '1 the said store')

# ══ 2. the condition. MUST land with the first gated row ══════════════
sub(u"""  heard:function(a){try{return !!(S.run._dlgHeard&&S.run._dlgHeard[a]);}catch(e){return false;}}""",
    u"""  heard:function(a){try{return !!(S.run._dlgHeard&&S.run._dlgHeard[a]);}catch(e){return false;}},
  /* P874: did this speaker say the tagged thing earlier THIS MATCH. Ships in
     the same commit as the first row that uses it, and that is not tidiness -
     _dlgCondOk drops a row whose condition name it does not recognise without
     erroring, so a gated line landing one commit early is permanently
     unpickable and silent about it. */
  said:function(a){return !!_dlgSaid['said:'+a];}""",
    '2 the said condition')

# ══ 3. the soft de-dup, at all three doors ════════════════════════════
sub(u"""    if(art)r=_dlgPick('patron:'+String(art).toLowerCase()+':'+moment,0,null);""",
    u"""    /* P874: PREFER SOMETHING NOT YET SAID THIS MATCH, but never return NO
       line - the fallback re-asks the full pool. A de-dup that can empty the
       pool turns a repeat into silence, which is worse, and it is the rule
       _dlgPick already applies to its own group exclusion. Kept OUT of
       _dlgPick because that is shared: the story pools want the hard drop. */
    if(art){var _pp='patron:'+String(art).toLowerCase()+':'+moment;
      r=_dlgPick(_pp,0,_dlgSaid)||_dlgPick(_pp,0,null);
      if(r){_dlgSaid[r.t]=1;if(r.say)_dlgSaid['said:'+r.say]=1;}}""",
    '3a dedup on the event door')

sub(u"""  if(!row)row=_dlgPick('patron:'+key,stage,null);""",
    u"""  /* P874: same soft de-dup as the event door, same reason. */
  if(!row){row=_dlgPick('patron:'+key,stage,_dlgSaid)||_dlgPick('patron:'+key,stage,null);
    if(row){_dlgSaid[row.t]=1;if(row.say)_dlgSaid['said:'+row.say]=1;}}""",
    '3b dedup on the say door')

sub(u"""    if(!row)row=_dlgPick('gossip:town',0,null);""",
    u"""    /* P874: THE THIRD DOOR, which the brief did not name. _dlgAmbient passes
       null for gossip in exactly the way the other two did, and this patch is
       rewriting the gossip table - fixing two doors while replacing the third's
       words would leave the new lines repeating for the old reason. */
    if(!row){row=_dlgPick('gossip:town',0,_dlgSaid)||_dlgPick('gossip:town',0,null);
      if(row)_dlgSaid[row.t]=1;}""",
    '3c dedup on the ambient door')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d engine edits (%s)' % (len(edits), ', '.join(edits)))
