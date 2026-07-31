const st=document.getElementById('stage');
const R={};
function ratio(){const r=st.getBoundingClientRect();return {w:Math.round(r.width),h:Math.round(r.height),ar:+(r.height/r.width).toFixed(3)};}
R.viewport=innerWidth+'x'+innerHeight;
R.default=ratio();                       /* game 319:691 -> 2.166 */
R.note=document.getElementById('arNote').textContent;
R.buttons=[...document.querySelectorAll('#arBtns button')].map(b=>b.textContent);
/* flick to 9:16 and confirm the stage really reshapes */
const b916=[...document.querySelectorAll('#arBtns button')].find(b=>b.textContent==='9:16');
b916.click(); await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
R.at916=ratio();                          /* -> 1.778 */
/* and back */
document.querySelectorAll('#arBtns button')[0].click();
await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
R.backToGame=ratio();
R.plateStillFits=(()=>{const p=document.getElementById('plate').getBoundingClientRect(),s=st.getBoundingClientRect();
  return Math.abs(p.width-s.width)<1&&Math.abs(p.height-s.height)<1;})();
return R;
