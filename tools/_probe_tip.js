const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(500);
gw();
/* make score tags exist (they carry inline styles - the reason P728 failed) */
E("G.pool[0].sel=true;G.pool[1].sel=true;try{_renderSelTags(G.pool.filter(function(d){return d.sel;}),450,true);}catch(e){}");
await sleep(300);
out.tagsBefore=W.document.querySelectorAll('.selTag,#selTotal').length;
E("G.pF=[{id:'honeytrap',tier:2,charges:2,state:{}}];famRenderRow()");
await sleep(300);
E("famCardTap(0)");
await sleep(500);
const tip=W.document.getElementById('cardFocusTip');
const card=W.document.querySelector('#famRowP .fcv');
out.tipW=tip?Math.round(tip.getBoundingClientRect().width):null;
out.screenW=Math.round(W.document.getElementById('screen-match').getBoundingClientRect().width);
out.widthPct=out.tipW&&out.screenW?Math.round(100*out.tipW/out.screenW):null;
const body=tip&&tip.querySelector('.cft-body');
out.justify=body?getComputedStyle(body).textAlign:null;
out.lastLine=body?getComputedStyle(body).textAlignLast:null;
const name=tip&&tip.querySelector('.cft-name');
out.titleStroke=name?getComputedStyle(name).webkitTextStrokeWidth:null;
/* the scores must be GONE while the tip is open */
const tag=W.document.querySelector('.selTag')||W.document.getElementById('selTotal');
out.tagOpacity=tag?getComputedStyle(tag).opacity:'no-tag';
out.tagVis=tag?getComputedStyle(tag).visibility:'no-tag';
/* and the tip must clear the card */
if(tip&&card){
  const t=tip.getBoundingClientRect(),c=card.getBoundingClientRect();
  out.gapPx=Math.round(c.top-t.bottom);
  out.overlapsCard=t.bottom>c.top;
}
out.verdict=out.widthPct>=55&&out.widthPct<=68&&out.justify==='justify'&&out.lastLine==='center'
  &&parseFloat(out.titleStroke)>0&&(out.tagOpacity==='0'||out.tagVis==='hidden')&&out.overlapsCard===false;
return out;
