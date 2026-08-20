# -*- coding: utf-8 -*-
"""P839: LAST CALL judges the PRE-take amount; the eighty boss
greeting lines land with their history-state router.

THE RULING (Denis): "LAST CALL's threshold should see what the player
actually earned before any opponent card touches it - a bank that
cleared the floor on its own terms shouldn't retroactively fail
because of a tax applied after the fact. The skim still gets its cut
regardless." Found live by the P836 probe: a 1,000 bank was skimmed to
700 and then voided wholesale by the 800 floor.
Mechanically: the judged amount is captured AFTER the player's own
bonus stack (what the player earned) and BEFORE the opponent-card
docks; the refusal tests that. On a genuine sub-floor bank the void
still zeroes the post-take remainder and the taker keeps its cut -
per the ruling's own words.

THE GREETINGS (docs/FARK_BOSS_GREETING_LINES.md, Denis's content):
8 bosses x (first-meeting + three history states x 3 lines). The P833
:open slot becomes a state ROUTER: nights===0 -> :open; else - when
the 65% ledger record-greeting has passed - w===0 -> :undefeated,
w===1 -> :firstloss, w>=2 -> :beaten. Same resolver, rows as data.
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


# ── 1) the pre-take capture ──
sub("""  var _bankAborted=false;""",
    """  var _bankAborted=false;
  /* P839 (Denis): what the player ACTUALLY EARNED - after their own
     bonus stack, before any opponent card's cut. LAST CALL judges
     this, not the taxed remainder (a skim pushed a cleared bank under
     the floor and the house voided the whole thing - the badge's
     promise failing to an unrelated mechanic). */
  var _preTakeTotal=total;""",
    'the pre-take capture')

# ── 2) the refusal judges it ──
sub("""    if(_ruleActive('last_call','p')&&total>0&&total<_lcT){
      total=0;bonusMsg=' LAST CALL — BANK <'+_lcT;""",
    """    if(_ruleActive('last_call','p')&&_preTakeTotal>0&&_preTakeTotal<_lcT){
      /* P839: judged on the PRE-take amount. A bank that cleared the
         floor on its own terms pays its post-take remainder; a genuine
         sub-floor bank still voids, and any cut already taken stays
         with the taker - the ruling's own words. */
      total=0;bonusMsg=' LAST CALL — BANK <'+_lcT;""",
    'the refusal judges pre-take')

# ── 3) the state router replaces the :open-only slot ──
sub("""      if((cat==='MATCH_START'||cat==='REMATCH_START')&&typeof G!=='undefined'&&G&&G._isBoss){
        try{
          var _lg0=(typeof S!=='undefined')&&S&&S.npcLedger&&S.npcLedger[this.portraitKey];
          if(!(_lg0&&_lg0.nights>0)&&typeof _dlgPick==='function'){
            var _bo=_dlgPick('boss:'+String(this.oppKey||'').toLowerCase()+':open',0,null);
            if(_bo)return _bo.t;
          }
        }catch(e){}
      }""",
    """      if((cat==='MATCH_START'||cat==='REMATCH_START')&&typeof G!=='undefined'&&G&&G._isBoss){
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
    'the state router')

# ── 4) the eighty lines, parsed from Denis's doc ──
doc = io.open(os.path.join(ROOT, 'docs', 'FARK_BOSS_GREETING_LINES.md'), encoding='utf-8').read()
rows = []
count = 0
def js(t):
    return '"' + t.replace('\\', '\\\\').replace('"', '\\"') + '"'
for m in re.finditer(r'^## ([A-Z]+)\n(.*?)(?=^## |\Z)', doc, re.M | re.S):
    boss = m.group(1).lower()
    body = m.group(2)
    if boss == 'total':
        continue
    fm = re.search(r'\*\*First meeting:\*\* "(.+?)"', body)
    if fm:
        rows.append("  {p:'boss:%s:open',s:0,t:%s}," % (boss, js(fm.group(1))))
        count += 1
    for state, pool in [('Undefeated', 'undefeated'), ('First loss', 'firstloss'), ('Repeated losses', 'beaten')]:
        sm = re.search(r'\*\*%s:\*\* (.+?)$' % state, body, re.M)
        if not sm:
            sys.exit('missing %s for %s' % (state, boss))
        lines = re.findall(r'"(.+?)"', sm.group(1))
        if len(lines) != 3:
            sys.exit('%s %s: %d lines' % (boss, state, len(lines)))
        for gi, t in enumerate(lines):
            rows.append("  {p:'boss:%s:%s',s:0,g:'v%d',t:%s}," % (boss, pool, gi, js(t)))
            count += 1
if count != 80:
    sys.exit('expected 80 lines, wired %d' % count)

sub("""  {p:'patron:golgoth:recog',s:0,t:"...Still here."},
];""",
    """  {p:'patron:golgoth:recog',s:0,t:"...Still here."},
  /* P839: THE BOSS GREETINGS (docs/FARK_BOSS_GREETING_LINES.md,
     Denis's content) - first meeting plus three history states per
     boss, drawn by the state router in getLine. */
""" + "\n".join(rows) + """
];""",
    'the eighty lines wired')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits, %d lines (%s)' % (len(edits), count, ', '.join(edits)))
