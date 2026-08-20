# -*- coding: utf-8 -*-
"""P841: the greeting router dissolves into the resolver (Denis's
ruling on the architecture audit's one fold candidate: "three
_DLG_COND predicates over bespoke if/else... dissolve it now, while
it's small and fresh").

- Three predicates join _DLG_COND: boss_unmet, boss_wins:N,
  boss_wins_gte:N - each reads the CURRENT boss's ledger (rung.key,
  npcLedger's own key) and is false outside a boss match.
- The 80 greeting rows move from four state pools into ONE pool per
  boss (boss:<name>:greet), each row carrying exactly one condition:
  open -> boss_unmet; undefeated -> boss_wins:0 (met is implied - the
  predicate requires nights>0); firstloss -> boss_wins:1; beaten ->
  boss_wins_gte:2. The conditions are mutually exclusive, so plain
  condition filtering does ALL the state selection - no reliance on
  the specificity contest, and a fifth history state someday is one
  more predicate + rows, not another branch.
- The router in getLine collapses to a single _dlgPick call. The 65%
  ledger record-greeting upstream is untouched - the layering Denis
  called out stays exactly as it was.
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
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# 1) the predicates
sub("""  boss_beaten:function(a){try{return (S.run.bossesBeaten||[]).indexOf(a)>=0;}catch(e){return false;}},""",
    """  boss_beaten:function(a){try{return (S.run.bossesBeaten||[]).indexOf(a)>=0;}catch(e){return false;}},
  /* P841: the greeting router's states, as conditions. Each reads the
     CURRENT boss's ledger (rung.key - npcLedger's own key) and is
     false outside a boss match. boss_wins requires nights>0, so
     wins:0 (undefeated) can never match a first-ever meeting. */
  boss_unmet:function(){try{var k=(typeof G!=='undefined'&&G&&G._isBoss&&G.rung)?G.rung.key:null;if(!k)return false;var l=S.npcLedger&&S.npcLedger[k];return !(l&&l.nights>0);}catch(e){return false;}},
  boss_wins:function(a){try{var k=(typeof G!=='undefined'&&G&&G._isBoss&&G.rung)?G.rung.key:null;if(!k)return false;var l=S.npcLedger&&S.npcLedger[k];return !!(l&&l.nights>0)&&((l.w||0)===+a);}catch(e){return false;}},
  boss_wins_gte:function(a){try{var k=(typeof G!=='undefined'&&G&&G._isBoss&&G.rung)?G.rung.key:null;if(!k)return false;var l=S.npcLedger&&S.npcLedger[k];return !!(l&&l.nights>0)&&((l.w||0)>=+a);}catch(e){return false;}},""",
    'the three predicates')

# 2) the router collapses
sub("""      if((cat==='MATCH_START'||cat==='REMATCH_START')&&typeof G!=='undefined'&&G&&G._isBoss){
        /* P839: the STATE ROUTER (Denis's greeting set). No history ->
           :open. With history - once the 65% ledger record-greeting
           above has passed - the relationship picks the pool: the boss
           undefeated (:undefeated), the first sit-down since the
           player's first win (:firstloss), beaten more than once
           (:beaten). w counts PLAYER wins, the ledger's own convention. */
        try{
          if(typeof _dlgPick==='function'){
            var _lg0=(typeof S!=='undefined')&&S&&S.npcLedger&&S.npcLedger[this.portraitKey];
            var _bk0='boss:'+String(this.oppKey||'').toLowerCase();
            var _bPool;
            if(!(_lg0&&_lg0.nights>0))_bPool=_bk0+':open';
            else{
              var _bw=_lg0.w||0;
              _bPool=_bk0+(_bw===0?':undefeated':(_bw===1?':firstloss':':beaten'));
            }
            var _bo=_dlgPick(_bPool,0,null);
            if(_bo)return _bo.t;
          }
        }catch(e){}
      }""",
    """      if((cat==='MATCH_START'||cat==='REMATCH_START')&&typeof G!=='undefined'&&G&&G._isBoss){
        /* P841 (the audit's fold, Denis's ruling): the history states
           are CONDITIONS on rows in one pool, not a router. The
           boss_unmet / boss_wins:N / boss_wins_gte:2 predicates are
           mutually exclusive, so plain condition filtering does all
           the selection - a fifth state someday is a predicate + rows,
           not another branch. The 65% ledger record-greeting upstream
           layers over this exactly as before. */
        try{
          if(typeof _dlgPick==='function'){
            var _bo=_dlgPick('boss:'+String(this.oppKey||'').toLowerCase()+':greet',0,null);
            if(_bo)return _bo.t;
          }
        }catch(e){}
      }""",
    'the router collapses')

# 3) the rows regenerate into one pool per boss
doc = io.open(os.path.join(ROOT, 'docs', 'FARK_BOSS_GREETING_LINES.md'), encoding='utf-8').read()
rows = []
count = 0
def js(t):
    return '"' + t.replace('\\', '\\\\').replace('"', '\\"') + '"'
STATE_COND = {'open': "c:['boss_unmet']",
              'undefeated': "c:['boss_wins:0']",
              'firstloss': "c:['boss_wins:1']",
              'beaten': "c:['boss_wins_gte:2']"}
for m in re.finditer(r'^## ([A-Z]+)\n(.*?)(?=^## |\Z)', doc, re.M | re.S):
    boss = m.group(1).lower()
    body = m.group(2)
    if boss == 'total':
        continue
    fm = re.search(r'\*\*First meeting:\*\* "(.+?)"', body)
    rows.append("  {p:'boss:%s:greet',s:0,%s,t:%s}," % (boss, STATE_COND['open'], js(fm.group(1))))
    count += 1
    for state, pool in [('Undefeated', 'undefeated'), ('First loss', 'firstloss'), ('Repeated losses', 'beaten')]:
        sm = re.search(r'\*\*%s:\*\* (.+?)$' % state, body, re.M)
        lines = re.findall(r'"(.+?)"', sm.group(1))
        for gi, t in enumerate(lines):
            rows.append("  {p:'boss:%s:greet',s:0,g:'v%d',%s,t:%s}," % (boss, gi, STATE_COND[pool], js(t)))
            count += 1
if count != 80:
    sys.exit('expected 80 rows, built %d' % count)

# replace the old block: from its header comment to the closing ];
hi = s.find("""  /* P839: THE BOSS GREETINGS (docs/FARK_BOSS_GREETING_LINES.md,""")
if hi < 0:
    sys.exit('old greeting block header missing')
he = s.find('\n];', hi)
if he < 0:
    sys.exit('array close missing')
s = s[:hi] + """  /* P841: THE BOSS GREETINGS (docs/FARK_BOSS_GREETING_LINES.md,
     Denis's content) - ONE pool per boss, the history state carried
     as a condition per row (the audit's fold: the router dissolved
     into the resolver's own vocabulary). */
""" + "\n".join(rows) + s[he:]
edits.append('80 rows in one pool per boss')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
