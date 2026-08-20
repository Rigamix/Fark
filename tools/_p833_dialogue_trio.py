# -*- coding: utf-8 -*-
"""P833: the dialogue rulings - boss :open pool, the additive resolver
with the growth lines wired, and DLG.triggerCard deleted.

Denis's rulings (2026-08-20 batch):
 - First-meeting boss lines: BUILD THE POOL; he writes the eight
   greetings later. The slot: original getLine, after the ledger
   branch misses - for bosses _orig always runs (P818: art stays
   null), for patrons the personal layer answers first, so the branch
   is boss-reachable and patron-inert by construction. Pool key form
   proven by _bossKey: the lowercased rung NAME (boss:grog:open).
 - Band lines must be GENUINELY ADDITIVE (his brief's explicit word).
   The resolver's most-conditions rule is a deliberate override
   pattern elsewhere (the Discrepancy thread ends a story with it), so
   rather than change its meaning, rows tagged add:1 JOIN the pool
   whenever their conditions pass without entering the specificity
   contest. Band-4/band-7 rows for the 22 covered patrons wire in from
   docs/PATRON_GROWTH_LINES.md (Golgoth: recognition only, by design);
   recognition rows land as patron:<art>:recog pools for the beat that
   arrives with the persona registry.
 - DLG.triggerCard: DELETE the call sites, don't revive - trait
   reactions + hesitation already cover event reactions. 24 sites + the
   method; the global triggerCard() banner (~210 sites) is a different
   function and untouched.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1) the boss :open slot ──
sub("""        }catch(e){}
      }
      /* PATRON class flavour: on a match open, ~60% chance to use a
         persona-specific intro (from PATRON_CLASS_LINES) instead of the
         generic patron pool, so the patron's 'class' comes through. */""",
    """        }catch(e){}
      }
      /* P833: FIRST-EVER MEETING (Denis). The ledger greeting needs
         history; with none, a boss draws its own :open pool
         (boss:<name>:open - _bossKey's key family, the lowercased rung
         name). Rows are Denis's to write; an empty pool falls through
         silently. Covers MATCH_START and the rematch redirect alike.
         Boss-reachable and patron-inert by construction: for bosses the
         wrapper always reaches this original (art is null, P818); for
         patrons the personal layer answers MATCH_START first. */
      if((cat==='MATCH_START'||cat==='REMATCH_START')&&typeof G!=='undefined'&&G&&G._isBoss){
        try{
          var _lg0=(typeof S!=='undefined')&&S&&S.npcLedger&&S.npcLedger[this.portraitKey];
          if(!(_lg0&&_lg0.nights>0)&&typeof _dlgPick==='function'){
            var _bo=_dlgPick('boss:'+String(this.oppKey||'').toLowerCase()+':open',0,null);
            if(_bo)return _bo.t;
          }
        }catch(e){}
      }
      /* PATRON class flavour: on a match open, ~60% chance to use a
         persona-specific intro (from PATRON_CLASS_LINES) instead of the
         generic patron pool, so the patron's 'class' comes through. */""",
    'the boss :open slot')

# ── 2) the additive resolver ──
sub("""  if(!live.length)return null;
  var spec=Math.max.apply(null,live.map(function(r){return (r.c||[]).length;}));
  live=live.filter(function(r){return (r.c||[]).length===spec;});
  var flo=Math.max.apply(null,live.map(function(r){return r.s||0;}));
  live=live.filter(function(r){return (r.s||0)===flo;});""",
    """  if(!live.length)return null;
  /* P833: ADDITIVE ROWS (add:1) join the pool whenever their conditions
     pass, WITHOUT entering the specificity contest - the band-growth
     lines are additive by the brief's explicit word ("the baseline
     stays the baseline"). The most-conditions rule below keeps its
     meaning for everything untagged - the Discrepancy thread's
     deliberate story-ending override depends on it. */
  var _addR=live.filter(function(r){return r.add;});
  live=live.filter(function(r){return !r.add;});
  if(live.length){
    var spec=Math.max.apply(null,live.map(function(r){return (r.c||[]).length;}));
    live=live.filter(function(r){return (r.c||[]).length===spec;});
    var flo=Math.max.apply(null,live.map(function(r){return r.s||0;}));
    live=live.filter(function(r){return (r.s||0)===flo;});
  }
  live=live.concat(_addR);""",
    'the additive resolver')

# ── 3) the growth lines, parsed from the doc ──
doc = io.open(os.path.join(ROOT, 'docs', 'PATRON_GROWTH_LINES.md'), encoding='utf-8').read()
rows = []
pat = re.compile(r'^\*\*([A-Z]+)\*\* \u2014 band-4: "(.+?)" \u2014 band-7: "(.+?)" \u2014 recognition: "(.+?)"', re.M)
found = pat.findall(doc)
if len(found) != 22:
    sys.exit('expected 22 full patron lines, parsed %d' % len(found))
def js(t):
    return '"' + t.replace('\\', '\\\\').replace('"', '\\"') + '"'
for name, b4, b7, recog in found:
    art = name.lower()
    rows.append("  {p:'patron:%s',s:0,g:'b4',add:1,c:['night_gte:4'],t:%s}," % (art, js(b4)))
    rows.append("  {p:'patron:%s',s:0,g:'b7',add:1,c:['night_gte:7'],t:%s}," % (art, js(b7)))
    rows.append("  {p:'patron:%s:recog',s:0,t:%s}," % (art, js(recog)))
# Golgoth: recognition only, by explicit design
rows.append("  {p:'patron:golgoth:recog',s:0,t:\"...Still here.\"},")

sub("""  {p:'reaction:discrepancy',s:0,c:['heard:discrepancy_intro','night_gte:4'],g:'discrepancy-resolution',t:"Heard Corvus quietly wrote it off. Strange, for him. Makes you wonder."}

];""",
    """  {p:'reaction:discrepancy',s:0,c:['heard:discrepancy_intro','night_gte:4'],g:'discrepancy-resolution',t:"Heard Corvus quietly wrote it off. Strange, for him. Makes you wonder."},

  /* P833: THE GROWTH LINES (docs/PATRON_GROWTH_LINES.md, Denis's own
     content pass). band-4/band-7 rows are add:1 - additive with the
     baseline pool from their night on, never replacing it. The :recog
     pools hold the rare "first meeting since the band changed" beat,
     drawn once the persona registry lands (P838). Golgoth: recognition
     only, his silence is the design. */
""" + "\n".join(rows) + """
];""",
    'the growth lines wired (22 patrons + golgoth recog)')

# ── 4) DLG.triggerCard: the guarded bust block first ──
sub("""    /* Patron dialogue for the most impactful bust-triggered card (just one to avoid stacking) */
    if(_pendingBustTriggers.length&&window.DLG){
      var _firstBT=_pendingBustTriggers[0];
      setTimeout(function(){DLG.triggerCard(_firstBT.cid,false);},900);
    }""",
    """    /* P833: the DLG.triggerCard bust bark went with the feature - its
       pools were deleted with OPP_DIALOGUE and Denis ruled the call
       sites out rather than revived (trait reactions cover the beat). */""",
    'bust-trigger bark deleted')

# then every remaining call site, FRAGMENT-surgically: several sites share
# their line with live code (last_stand's return, high_roller's +400, the
# closing brace of an if-block) - a line sweep amputated them once already.
_before = s.count('DLG.triggerCard(')
# IIFE-wrapped forms first (their wrapper must go whole)
s = re.sub(r"\(function\(_cid\)\{setTimeout\(function\(\)\{if\(window\.DLG\)DLG\.triggerCard\(_cid,false\);\},(?:_oppDelay\(\d+\)|\d+)\);\}\)\(cid\);", '', s)
# try-wrapped (iron_gate)
s = re.sub(r"try\{if\(window\.DLG\)setTimeout\(function\(\)\{DLG\.triggerCard\('[a-z_]+',(?:true|false)\);\},\d+\);\}catch\(e\)\{\}", '', s)
# guard-outside and guard-inside plain forms
s = re.sub(r"if\(window\.DLG\)setTimeout\(function\(\)\{DLG\.triggerCard\([^)]*\);\},(?:_oppDelay\(\d+\)|\d+)\);", '', s)
s = re.sub(r"setTimeout\(function\(\)\{if\(window\.DLG\)DLG\.triggerCard\([^)]*\);\},(?:_oppDelay\(\d+\)|\d+)\);", '', s)
s = re.sub(r"setTimeout\(function\(\)\{DLG\.triggerCard\([^)]*\);\},(?:_oppDelay\(\d+\)|\d+)\);", '', s)
_after = s.count('DLG.triggerCard(')
edits.append('%d call fragments removed' % (_before - _after))
# now-empty statements left behind are harmless; the parse gate is the judge

# then the method itself (with its doc comment)
mi = s.find('    /* triggerCard: patron reacts to a specific card firing.')
me = s.find("      this.show(line);this.lastTime=Date.now();},", mi)
if mi < 0 or me < 0:
    sys.exit('triggerCard method anchors missing')
me = s.find('\n', me) + 1
s = s[:mi] + """    /* P833: DLG.triggerCard is DELETED (Denis's ruling) - its card-bark
       pools were removed with OPP_DIALOGUE and the ~24 call sites fired
       into nothing; trait reactions + hesitation cover event reactions.
       The GLOBAL triggerCard() banner is a different function, alive. */
""" + s[me:]
edits.append('the method deleted')

_rest = [m.start() for m in re.finditer(r'DLG\.triggerCard\(', s)]
if _rest:
    ctx = [s[i-70:i+90].replace('\n', '\\n') for i in _rest[:4]]
    sys.exit('DLG.triggerCard survives the sweep at: ' + ' ||| '.join(ctx))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %s' % ', '.join(edits))
