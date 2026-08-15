/* SUITE: exclude. Does a REAL bust reach the scatter and the red? The
 * P733 probe called _bustImpact() directly - which proves the function,
 * not the route (prove-the-hook lesson). This drives doBust. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(600);
gw();
E("window.__impact=0;var _oi=_bustImpact;_bustImpact=function(){window.__impact++;return _oi.apply(this,arguments);};");
E("window.__scatterN=0;var _os=D3X.scatterRow.bind(D3X);D3X.scatterRow=function(s){var n=_os(s);window.__scatterN=n;return n;};");
E("window.__flare=0;var _of=D3X.bustFlare.bind(D3X);D3X.bustFlare=function(){window.__flare++;return _of();};");
/* a REAL bust: no scoring dice, then the game's own doBust */
E("G.pool.forEach(function(d){d.committed=false;d.sel=false;d.val=3;});G.pool[0].val=2;G.pool[1].val=4;G.pool[2].val=6;G.pool[3].val=2;G.pool[4].val=3;G.pool[5].val=4;");
E("G.phase='choosing';doBust()");
await sleep(300);
out.impactCalled=E('window.__impact');
out.scatterKicked=E('window.__scatterN');
out.flareCalled=E('window.__flare');
const red=W.document.getElementById('matchBustRed');
out.redExists=!!red;
out.redOnNow=red&&red.classList.contains('on');
out.redOpacity=red?getComputedStyle(red).opacity:null;
out.kicksLive=E("D3X.dice.filter(function(d){return d.match&&d.kick;}).length");
out.verdict=out.impactCalled>0&&out.scatterKicked>0&&out.flareCalled>0&&!!out.redOnNow;
return out;
