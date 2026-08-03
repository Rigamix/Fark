/* sim_power_d.js — LENS 2, part D: is the Break cost a TRAP or a TIMING READ,
 * does the power delta survive a change of agent, and is a worn badge a gain?
 *
 *  D1. Bea, unchanged, against Bea-with-one-rule-added: withhold the SKULL
 *      until no future turn remains (brief §4's timing read). Nothing else
 *      differs, so the gap is Break's timing and only that.
 *  D2. The night-1 → night-8 delta under four more agents.
 *  D3. Every badge, worn, on two builds: the branded "maxed" one and the
 *      unbranded one that actually wins most.
 *
 * Tail for tools/sim_run.js. fark_proto.html is NOT edited.
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:600;
var TIER=5;
var out={seed:seed,n:N,tier:TIER};
var N8=FSIM.GEAR.night8;

function gear(key,ench,badge,fcards,dice){
  return{key:key,dice:(dice||N8.dice).slice(),ench:ench,badge:badge||null,fcards:fcards||[]};
}
function w(k,n){return FSIM.ci95(k,n);}
function pairedCI(b,c,n){
  var d=(b-c)/n,v=(b+c-(b-c)*(b-c)/n)/(n*n),se=Math.sqrt(Math.max(v,0));
  return{d:+(100*d).toFixed(1),lo:+(100*(d-1.959963985*se)).toFixed(1),
         hi:+(100*(d+1.959963985*se)).toFixed(1),discordant:b+c};
}
function sweep(tier,gears,policies,n,boss){
  /* cells = gears x policies, all seeing the identical opponent sequence */
  var cells=[];
  gears.forEach(function(g){policies.forEach(function(p){
    cells.push({gear:g,pol:p,key:g.key+' | '+p.name,wins:[],
      bank:[],opp:[],turns:[],busts:0,turnsTot:0,icons:0,gold:[],cap:0,err:0});});});
  for(var i=0;i<n;i++){
    var s=(seed+i*7919)|0,first=(i%2===0);
    for(var c=0;c<cells.length;c++){
      var cell=cells[c];
      FSIM.installRng(s);
      var rung=boss?null:generatePatron(tier);
      var m=null;
      try{m=FSIM.simMatch(cell.pol,{tier:tier,boss:!!boss,gear:cell.gear,
        badge:cell.gear.badge||null,fcards:cell.gear.fcards||[],
        rung:rung,playerFirst:first});}catch(e){cell.err++;}
      if(!m){cell.wins.push(null);continue;}
      cell.wins.push(m.won?1:0);
      cell.bank.push(m.playerBank);cell.opp.push(m.oppBank);cell.turns.push(m.turns);
      cell.busts+=m.busts;cell.turnsTot+=m.turns;cell.icons+=m.icons;
      cell.gold.push(m.goldGained);if(m.capEnd)cell.cap++;
    }
  }
  cells.forEach(function(a){
    var k=0;a.wins.forEach(function(x){if(x)k++;});
    var ci=w(k,a.bank.length);
    a.row={key:a.key,win:+(100*ci.p).toFixed(1),
      ci:[+(100*ci.lo).toFixed(1),+(100*ci.hi).toFixed(1)],
      bank:+FSIM.ciMean(a.bank).mean.toFixed(0),
      oppBank:+FSIM.ciMean(a.opp).mean.toFixed(0),
      medTurns:FSIM.median(a.turns),
      bustPerTurn:+(100*a.busts/Math.max(1,a.turnsTot)).toFixed(1),
      icons:+(a.icons/Math.max(1,a.bank.length)).toFixed(2),
      goldPerMatch:+FSIM.ciMean(a.gold).mean.toFixed(1),
      capEndPct:+(100*a.cap/Math.max(1,a.bank.length)).toFixed(1),
      k:k,n:a.bank.length,errors:a.err};
  });
  function vs(i,j){
    var b=0,c=0,np=0;
    for(var q=0;q<n;q++){
      var x=cells[i].wins[q],y=cells[j].wins[q];
      if(x==null||y==null)continue;np++;if(x&&!y)b++;if(!x&&y)c++;
    }
    return pairedCI(b,c,Math.max(1,np));
  }
  return{cells:cells,rows:cells.map(function(c){return c.row;}),vs:vs};
}

/* BEA + one rule: hold the skull back until there is no future turn to lose.
   Everything else — threshold, keep preference, draft, lane plan — is Bea's
   own, taken by reference off the shipped policy object. */
var beaInformed=Object.assign({},FSIM.POLICIES.bea,{
  name:'BALANCED BEA (informed Break)',
  keep:function(f,c){
    var pool=c.keeps;
    if(!(c.state&&c.state.lastTurn)){
      var noSkull=c.keeps.filter(function(k){
        return !k.sel.some(function(d){return _dieIsIcon(d)&&d.ench&&d.ench.t==='break';});});
      if(noSkull.length)pool=noSkull;
    }
    var ic=pool.filter(function(k){return k.icons>0;});
    if(ic.length&&c.G.turnPts<400)pool=ic;
    var b=pool[0];
    for(var i=1;i<pool.length;i++)
      if(pool[i].pts>b.pts||(pool[i].pts===b.pts&&pool[i].left>b.left))b=pool[i];
    return b.sel;
  }});

/* ── D1. naive vs informed Break ──────────────────────────────────────── */
try{
  FSIM.quiet();
  var t0=performance.now();
  var brk=[null,null,null,null,null,null];brk[3]='break';
  var g1=[gear('n8_no_brand',[null,null,null,null,null,null]),
          gear('n8_break_only',brk),
          gear('n8_maxed_6brands',N8.ench.slice(),N8.badge,N8.fcards.slice())];
  var r1=sweep(TIER,g1,[FSIM.POLICIES.bea,beaInformed],N);
  /* cell order is gear-major: [g0/bea, g0/inf, g1/bea, g1/inf, g2/bea, g2/inf] */
  out.breakTiming={rows:r1.rows,
    breakOnly_informedVsNaive:r1.vs(3,2),
    maxed_informedVsNaive:r1.vs(5,4),
    noBrand_informedVsNaive:r1.vs(1,0),
    breakOnlyNaive_vs_noBrand:r1.vs(2,0),
    breakOnlyInformed_vs_noBrand:r1.vs(3,1)};
  out.msD1=Math.round(performance.now()-t0);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.breakTiming='ERR '+e.stack;}

/* ── D2. does the night-1 → night-8 delta survive a change of agent? ──── */
try{
  FSIM.quiet();
  var t1=performance.now();
  var g2=[{key:'night1',dice:['silver','bone','bone','bone','bone','bone'],
           ench:[null,null,null,null,null,null],badge:null,fcards:[]},
          gear('n8_maxed',N8.ench.slice(),N8.badge,N8.fcards.slice()),
          gear('n8_noBrand',[null,null,null,null,null,null],N8.badge,N8.fcards.slice())];
  var pols=[FSIM.POLICIES.carl,FSIM.POLICIES.ned,FSIM.POLICIES.otto,FSIM.POLICIES.greg_informed];
  var r2=sweep(TIER,g2,pols,Math.round(N*0.75));
  out.agents={rows:r2.rows,deltas:{}};
  /* cell index = gearIdx*pols.length + polIdx */
  pols.forEach(function(p,pi){
    out.agents.deltas[p.name]={
      maxedVsNight1:r2.vs(1*pols.length+pi,0*pols.length+pi),
      noBrandVsNight1:r2.vs(2*pols.length+pi,0*pols.length+pi),
      noBrandVsMaxed:r2.vs(2*pols.length+pi,1*pols.length+pi)};
  });
  out.msD2=Math.round(performance.now()-t1);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.agents='ERR '+e.stack;}

/* ── D3. every badge, worn, on both builds ────────────────────────────── */
try{
  FSIM.quiet();
  var t2=performance.now();
  var BADGES=[null,'last_call','kindred','still_waters','first_strike',
              'steeped','pickpocket','drill_order','reckoning'];
  var NAME={last_call:'ZERO HOUR',counterfeit:'KINDRED',confession:'STILL WATERS',
            in_arrears:'FIRST STRIKE',steeped:'STEEPED',pickpocket:'PICKPOCKET',
            drill_order:'DRILL ORDER',reckoning:'RECKONING'};
  function badgeSweep(label,ench){
    var gs=BADGES.map(function(b){
      return gear(label+'/'+(b?NAME[b]:'no badge'),ench.slice(),b,N8.fcards.slice());});
    var r=sweep(TIER,gs,[FSIM.POLICIES.bea],Math.round(N*0.7));
    return{rows:r.rows,vsNone:BADGES.map(function(b,ix){
      return ix?{badge:NAME[b],d:r.vs(ix,0)}:null;}).filter(Boolean)};
  }
  out.badges_branded=badgeSweep('6brands',N8.ench);
  out.badges_unbranded=badgeSweep('noBrand',[null,null,null,null,null,null]);
  out.msD3=Math.round(performance.now()-t2);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.badges_branded='ERR '+e.stack;}

FSIM.restoreRng();
return out;
