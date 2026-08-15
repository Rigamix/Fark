/* SUITE: exclude. C14: scatter variance + the red flinch. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),15000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(600);
gw();
/* fire the impact directly - a real bust needs a losing roll */
const lightsBefore=(()=>{const dx=E('window.D3X');let c=null;
  dx.scene.traverse(o=>{if(!c&&o.isLight)c=o.color.getHex();});return c;})();
E('_bustImpact()');
await sleep(120);
const dx=E('window.D3X');
const kicks=dx.dice.filter(d=>d.match&&d.kick).map(d=>({
  vx:+d.kick.vx.toFixed(2),vz:+d.kick.vz.toFixed(2),sp:+d.kick.sp.toFixed(2)}));
out.kicked=kicks.length;
/* CHAOS: directions must not be one-sided-by-sign, magnitudes must vary */
const mags=kicks.map(k=>Math.hypot(k.vx,k.vz));
out.magSpread=+(Math.max(...mags)-Math.min(...mags)).toFixed(2);
out.angles=kicks.map(k=>Math.round(Math.atan2(k.vz,k.vx)*180/Math.PI));
out.distinctAngles=new Set(out.angles.map(a=>Math.round(a/30))).size;
out.hardHits=mags.filter(m=>m>1.5*1.5*0.9).length;
/* the flinch */
const red=W.document.getElementById('matchBustRed');
out.redOn=red&&red.classList.contains('on');
const lightsDuring=(()=>{let c=null;dx.scene.traverse(o=>{if(!c&&o.isLight)c=o.color.getHex();});return c;})();
out.lightShifted=lightsDuring!==lightsBefore;
await sleep(1700);
const lightsAfter=(()=>{let c=null;dx.scene.traverse(o=>{if(!c&&o.isLight)c=o.color.getHex();});return c;})();
out.lightRestored=lightsAfter===lightsBefore;
out.redOff=red&&!red.classList.contains('on');
out.verdict=out.kicked>=3&&out.magSpread>0.4&&out.distinctAngles>=3
  &&out.redOn&&out.lightShifted&&out.lightRestored&&out.redOff;
return out;
