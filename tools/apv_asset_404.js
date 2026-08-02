/* PHASE 5 — DOES EVERY PICTURE THE GAME ASKS FOR ACTUALLY ARRIVE?
 *
 * The static inventory (tools/asset_inventory.js) proves every path SPELLED OUT
 * in the source resolves on disk. It cannot check the other half: 54 of the
 * file's asset paths are built at runtime from a prefix constant plus a name —
 * `PT_CHAR + persona + '.webp'`, `'Art/Assets/Feats/' + FEAT_ART[id] + '.png'`.
 * Those are exactly where a 404 hides, because the bug is in the JOIN, not in
 * either half. `Death&Taxes.png` needs URL-encoding at one call site and not
 * another; nothing but a live load would ever tell you.
 *
 * So this drives the real screens and asks the browser, not the filesystem:
 * every <img> that got a src must have decoded. naturalWidth === 0 on a
 * connected, non-empty src IS the 404 — it is what the player sees as a hole.
 *
 * THE FONT CHECK IS HERE FOR A REASON. 'JMH Beda' loads from
 * assets/_mockups/new_main/, inside the PREVIOUS game's tree, and the standing
 * project note said that tree was dead. Following that note would have deleted
 * the game's font. document.fonts.check is the measurement that settles it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};

const out={screens:[],dead:[],fonts:{}};
const seen=new Set();

function sweep(where){
  let n=0;
  for(const img of document.images){
    const src=img.getAttribute('src')||'';
    if(!src||src.startsWith('data:'))continue;
    n++;
    /* complete && naturalWidth===0 is the browser saying "I finished, and there
       was nothing there". Still-loading images (complete false) are skipped —
       reporting those would make the probe a race. */
    if(img.complete&&img.naturalWidth===0){
      const key=src.split('?')[0];
      if(!seen.has(key)){seen.add(key);out.dead.push({src:key,screen:where});}
    }
  }
  out.screens.push({screen:where,imgs:n});
}

/* ── home ── */
await sleep(1200); sweep('home');

/* ── new run → patron select ── */
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
sweep('new run');
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(()=>[...document.querySelectorAll('.ptcard')].filter(vis).length>0,9000);
await sleep(900); sweep('patron select');

/* ── the loadout, which is where the feats wall and the dice case live ── */
try{ famLoadoutShow(); }catch(e){ out.loadoutErr=String(e); }
await until(()=>document.getElementById('gbLoadout'),6000);
await sleep(1200); sweep('loadout');
try{ document.getElementById('gbLoadout').remove(); }catch(e){}

/* ── match ── */
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0]; if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
await sleep(900); sweep('match');

/* ── the win overlay and its draft ── */
try{ dbgWin(); }catch(e){ out.winErr=String(e); }
await until(()=>vis(document.getElementById('end-ov')),9000);
await until(()=>document.querySelector('.fo-offer'),12000);
await sleep(1200); sweep('win');

/* ── the fonts, measured rather than assumed ── */
try{
  await document.fonts.ready;
  ['JMH Beda','Alagard','Press Start 2P','IM Fell English','MedievalSharp'].forEach(f=>{
    out.fonts[f]=document.fonts.check('16px "'+f+'"');
  });
}catch(e){ out.fontErr=String(e); }

out.totalImgsSeen=out.screens.reduce((a,s)=>a+s.imgs,0);

out.verdict={
  noDeadImages:  out.dead.length===0,
  gameFontLoaded: out.fonts['JMH Beda']===true
};
return out;
