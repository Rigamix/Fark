/* SUITE: exclude. C16: every live card resolves a recipe; famUse plays
 * it; a brand plays its family. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
await sleep(400);
/* coverage: every FAM_LIVE card resolves */
out.coverage=E(`(function(){var live=Object.keys(FAM_LIVE),miss=[];
 live.forEach(function(id){if(!FKFX.resolve(id))miss.push(id);});
 return {n:live.length,missing:miss};})()`);
out.enchCoverage=E(`['tithe','ward','snare','trade','snuff','quicksilver']
 .filter(function(k){return !FKFX.resolve('ench:'+k);})`);
out.commonsSilent=E(`['bone','iron','flint','lead'].every(function(m){return !FKFX.resolve('mat:'+m);})`);
/* famUse plays it: count spray calls during a real cast */
E(`window.__sprayN=0;var _os=_fxSpray;_fxSpray=function(){window.__sprayN++;return _os.apply(this,arguments);};`);
E(`window.__toneN=0;var _ot=SFX._tone.bind(SFX);SFX._tone=function(){window.__toneN++;return _ot.apply(null,arguments);};`);
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
E("G.pF=[{id:'powder_keg',tier:2,charges:2,state:{}}]");E("famRenderRow()");
await sleep(300);
E("window.__sprayN=0;window.__toneN=0");
E("famUse(0)");
await sleep(900);
out.castSprays=E('window.__sprayN');
out.castTones=E('window.__toneN');
/* ARM (powder keg) is a pulse and a drum with NO particles by design -
   so the spray families get their own check */
E("window.__sprayN=0");
E("FKFX.play('preserve',document.querySelector('#famRowP .fcv'))");
await sleep(400);
out.setSprays=E('window.__sprayN');
E("window.__sprayN=0");
E("FKFX.play('sacrifice',document.querySelector('#famRowP .fcv'))");
await sleep(400);
out.breakSprays=E('window.__sprayN');
/* a brand fires its family (tithe = COIN: two triangle blips) */
E("window.__toneN=0");
E(`(function(){var d=G.pool.filter(function(x){return !x.committed;})[0];
 if(!d)return;d.ench={t:'tithe',face:d.val};_iconFire(d,'p');})()`);
await sleep(500);
out.brandTones=E('window.__toneN');
out.verdict=out.coverage&&out.coverage.missing.length===0&&out.enchCoverage.length===0
  &&out.commonsSilent&&out.castTones>0&&out.brandTones>0
  &&out.setSprays>0&&out.breakSprays>0;
return out;
