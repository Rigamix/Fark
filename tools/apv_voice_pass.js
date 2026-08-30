/* P874 - the voice pass, driven through the real doors.
 *
 * The brief's section 5 names one check that has to be MEASURED rather than
 * read, because it is the ask Denis actually made ("low chance of getting the
 * same dialogue line again and again") and the words alone do not deliver it:
 *
 *   "Twenty busts against one patron, count distinct lines. Before the fix the
 *    ceiling is the pool size and the floor is a fair coin. After it the first
 *    N busts must return N distinct lines, then wrap. Assert the distinct
 *    count, not that a line appeared."
 *
 * So this drives _dlgEvent - the door the game uses - rather than _dlgPick.
 */
const out={};
if(typeof _dlgEvent!=='function')return {err:'no _dlgEvent'};
if(typeof _dlgResetGroups!=='function')return {err:'no _dlgResetGroups'};
_getS();

/* ── 1. the soft de-dup: N busts, N distinct lines ────────────────── */
function runOf(art,moment,n){
  window._lastSeatArt=art;window._lastSeatTrait=null;
  _dlgResetGroups();                       /* fresh match */
  const got=[];
  for(let i=0;i<n;i++){const l=_dlgEvent(moment);got.push(l);}
  return got;
}
const nell=runOf('Nell','yourBust',20);
/* THE REACHABLE pool, not every row. Nell's yourBust has three rows and one
   is gated on a warned tag - unavailable in a run with no push - so counting
   it made the target 3 when only 2 could ever be returned. The de-dup was
   right and the assert was wrong. */
const nellPool=PATRON_LINES.filter(r=>r.p==='patron:nell:yourBust'&&!(r.c&&r.c.length)).length;
const nellDistinctFirstN=new Set(nell.slice(0,nellPool)).size;
out.dedup={pool:nellPool,first20:nell,
  distinctInFirstPoolWorth:nellDistinctFirstN,
  distinctOverall:new Set(nell.filter(Boolean)).size,
  neverWentSilent:nell.every(Boolean)};

/* the CONTROL: without the skip map the same twenty repeat early. Proves the
   measurement can see a difference at all, rather than the pool being so big
   that any method looks good. */
window._lastSeatArt='Nell';
const raw=[];for(let i=0;i<20;i++){const r=_dlgPick('patron:nell:yourBust',0,null);raw.push(r&&r.t);}
out.dedup.controlDistinct=new Set(raw.filter(Boolean)).size;

/* ── 2. the said: gate ────────────────────────────────────────────── */
function gateTest(art,gatedText){
  window._lastSeatArt=art;window._lastSeatTrait=null;
  _dlgResetGroups();
  /* before the warning, the gated line must be unreachable */
  const before=[];for(let i=0;i<40;i++)before.push(_dlgEvent('yourBust'));
  _dlgResetGroups();
  _dlgEvent('push');                       /* this is what tags said:warned */
  const flagged=!!_dlgSaid['said:warned'];
  const after=[];for(let i=0;i<40;i++)after.push(_dlgEvent('yourBust'));
  return {flagged,
    beforeHasGated:before.indexOf(gatedText)>=0,
    afterHasGated:after.indexOf(gatedText)>=0};
}
out.gate={
  nell:gateTest('Nell',"I did say, love."),
  ferrand:gateTest('Ferrand',"I FARKIN' TOLD YOU! HAH!"),
  krox:gateTest('Krox',"I said bide. You thrashed."),
};

/* ── 3. Peck has a voice at all ───────────────────────────────────── */
window._lastSeatArt='Peck';_dlgResetGroups();
out.peck={rows:PATRON_LINES.filter(r=>/^patron:peck:/.test(r.p)).length,
  saysSomething:!!_dlgEvent('yourBust')};

/* ── 4. REACHABILITY: which moments in the table nothing can fire ─── */
const moments=new Set();
PATRON_LINES.forEach(r=>{const m=/^patron:[a-z]+:([a-zA-Z]+)$/.exec(r.p);if(m)moments.add(m[1]);});
/* _DLG_MOMENT is ONE door. win/loss reach through _dlgOutcome at match end
   and recog through the P837 recognition beat, so a census against
   _DLG_MOMENT alone reports them stranded when they are not. Those two doors
   fire once per match, which is also why the per-match de-dup is deliberately
   NOT applied there - it could not do anything. */
const OTHER_DOORS=['win','loss','recog'];
const fireable=new Set(Object.keys(_DLG_MOMENT).map(k=>_DLG_MOMENT[k]).concat(OTHER_DOORS));
out.reachability={
  momentsInTable:[...moments].sort(),
  momentsTheGameCanFire:[...fireable].sort(),
  unreachable:[...moments].filter(m=>!fireable.has(m)).sort(),
  rowsStranded:PATRON_LINES.filter(r=>{
    const m=/^patron:[a-z]+:([a-zA-Z]+)$/.exec(r.p);
    return m&&!fireable.has(m[1]);}).length,
};

/* ── 5. the struck-word list, over the rows only ──────────────────── */
const STRUCK=['acceptable','adequate','respectable','statistically','variance',
  'investment','strategic','composure','precisely','correct decision','expected'];
const offenders=[];
PATRON_LINES.forEach(r=>{
  /* EVERY row, not just the new ones - the brief says the final TABLES, and a
     pass that greps only its own diff cannot find what it missed. */
  const low=String(r.t||'').toLowerCase();
  STRUCK.forEach(w=>{if(low.indexOf(w)>=0)offenders.push(r.p+' :: '+r.t);});
});
out.struckWordSurvivors=offenders;

/* ── 6. the register ladder: who swears ───────────────────────────── */
const HIGH=['regis','rask','remny','vess','dunstan','eira','ollis','golgoth'];
const swears=[];
PATRON_LINES.forEach(r=>{
  const m=/^patron:([a-z]+):/.exec(r.p||'');if(!m)return;
  if(/fark/i.test(String(r.t||'')))swears.push(m[1]+' :: '+r.t);
});
out.oaths=swears;
out.highVoicesThatSwear=[...new Set(swears.map(x=>x.split(' :: ')[0]))].filter(n=>HIGH.indexOf(n)>=0);

out.VERDICT={
  dedupGivesDistinctLines: out.dedup.distinctInFirstPoolWorth===nellPool,
  dedupNeverSilent:        out.dedup.neverWentSilent===true,
  dedupBeatsTheControl:    out.dedup.distinctOverall>=out.dedup.controlDistinct,
  saidGateFlagsOnPush:     out.gate.nell.flagged&&out.gate.ferrand.flagged&&out.gate.krox.flagged,
  gatedLineHiddenBefore:   !out.gate.nell.beforeHasGated&&!out.gate.ferrand.beforeHasGated&&!out.gate.krox.beforeHasGated,
  gatedLineWinsAfter:      out.gate.nell.afterHasGated&&out.gate.ferrand.afterHasGated&&out.gate.krox.afterHasGated,
  peckHasAVoice:           out.peck.rows>0&&out.peck.saysSomething,
  noStruckWords:           offenders.length===0,
  onlyRaskSwearsAmongHigh: out.highVoicesThatSwear.length===1&&out.highVoicesThatSwear[0]==='rask',
  /* WAS "exactly preroll,waiting". P875 built those two triggers, so the
     stranded set is now empty and the assertion tightens to match: any moment
     the tables use must be one the game can fire. This is the verdict going
     from "these two are known-dead" to "nothing is dead", which is the whole
     point of having written it as a named set rather than a count. */
  nothingStranded: out.reachability.unreachable.length===0,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
