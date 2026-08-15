const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
await sleep(300);
/* every live card has a short line, and each is shorter than the long one */
out.cov=E(`(function(){var miss=[],longer=[];Object.keys(FAM_LIVE).forEach(function(id){
 var d=famDef(id);if(!d)return;var sh=FAM_SHORT[id];
 if(!sh){miss.push(id);return;}
 if(sh.length>=d.text[0].length)longer.push(id+' '+sh.length+'>='+d.text[0].length);});
 return {miss:miss,longer:longer};})()`);
out.avg=E(`(function(){var L=0,S=0,n=0;Object.keys(FAM_SHORT).forEach(function(id){
 var d=famDef(id);if(!d)return;L+=d.text[0].length;S+=FAM_SHORT[id].length;n++;});
 return {longAvg:Math.round(L/n),shortAvg:Math.round(S/n),n:n};})()`);
/* the MATCH focus shows the short one... */
E("G.pF=[{id:'honeytrap',tier:2,charges:2,state:{}}];famRenderRow()");
await sleep(250);E("famCardTap(0)");await sleep(400);
gw();
const body=W.document.querySelector('#cardFocusTip .cft-body');
out.matchText=body?body.textContent.trim().slice(0,60):null;
out.usesShort=!!(out.matchText&&/next roll pulls a die/i.test(out.matchText));
/* ...and the OTHER screens still read the authored text */
out.shelfHtml=E("famCardHtml('honeytrap',2,{}).indexOf('Tap a kept pair')>=0||(function(){var d=famDef('honeytrap');return d.text[1].indexOf('Tap a kept pair')>=0;})()");
out.verdict=out.cov.miss.length===0&&out.cov.longer.length===0&&out.usesShort&&out.shelfHtml===true;
return out;
