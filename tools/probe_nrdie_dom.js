const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.settings=S.settings||{};
try{startNewRun();}catch(e){}
try{famRunDraftShow();}catch(e){return{error:'famRunDraftShow threw '+e.message};}
if(!(await until(()=>document.getElementById('famRunDraft'),8000)))return{error:'no draft overlay'};
await sleep(3000);
const host=document.querySelector('#nrDice .d3host');
if(!host)return{error:'no d3host'};
const kids=[...host.children].map(c=>({tag:c.tagName,cls:c.className,id:c.id,
  childCount:c.children.length,
  style:(c.getAttribute('style')||'').slice(0,160)}));
/* what is D3 doing - did WebGL actually come up? */
const d3={exists:typeof D3!=='undefined',
  fail:(typeof D3!=='undefined')?!!D3.fail:null,
  loading:(typeof D3!=='undefined')?!!D3.loading:null,
  diceCount:(typeof D3!=='undefined'&&D3.dice)?D3.dice.length:null,
  hasTHREE:typeof THREE!=='undefined'};
const canvases=document.querySelectorAll('#famRunDraft canvas').length;
/* every descendant that uses a 3D transform = the CSS-cube signature */
let pre=0,tz=0;const samples=[];
host.querySelectorAll('*').forEach(el=>{
  const cs=getComputedStyle(el);
  if(cs.transformStyle==='preserve-3d')pre++;
  if(/matrix3d|translateZ/.test(cs.transform)){tz++;if(samples.length<8)
    samples.push({cls:el.className,tag:el.tagName,tr:cs.transform.slice(0,70)});}
});
return {hostHTML:host.innerHTML.slice(0,700),
  hostChildren:kids, d3, canvasesInOverlay:canvases,
  preserve3dCount:pre, transform3dCount:tz, transformSamples:samples,
  totalDescendants:host.querySelectorAll('*').length};
