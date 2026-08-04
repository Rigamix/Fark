/* SUITE: exclude — measurement, and the one the cleanup depends on.
 *
 * apv_asset_404 found five declared font families reporting `unloaded` after a
 * six-screen sweep, and it would be easy to read that as "58 dead CSS refs,
 * delete them". It is not sufficient evidence. `unloaded` means THE BROWSER
 * NEVER ASKED, and it never asks for a font no rendered text resolved to — on
 * the screens that were visited. Shop, gauntlet and game over were not.
 *
 * Deleting a font declaration that paints on an unvisited screen is a visible
 * regression that no probe would catch afterwards, because the reference would
 * be gone. So this walks EVERY screen the game has and, more importantly, asks
 * a different question than "did it load":
 *
 *   WHICH ELEMENTS ACTUALLY COMPUTE TO EACH FAMILY AS THEIR FIRST CHOICE?
 *
 * getComputedStyle resolves the whole font-family stack, so an element whose
 * CSS says `font-family:'IM Fell English', serif` reports the full list
 * whether or not the face loaded. That is the honest test of "is this
 * reference reachable" — independent of load timing, and it works on a screen
 * that is built but never painted. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};

const FAMS=['IM Fell English','Uncial Antiqua','Macondo','Jacquard 24','Metamorphous',
            'MedievalSharp','Alagard','Press Start 2P','JMH Beda','Enchanted Land'];
const out={perScreen:{},reach:{},loaded:{},samples:{}};
FAMS.forEach(f=>{out.reach[f]=0;out.samples[f]=[];});

/* Count every element in the DOM whose resolved font stack names the family,
   and record WHERE — a count with no example is unactionable. Walks the whole
   document, not just visible nodes: a built-but-hidden screen still carries
   its styling, and that is precisely the case that would be missed. */
function scan(where){
  const hit={};
  const all=document.querySelectorAll('*');
  for(const el of all){
    let ff='';
    try{ ff=getComputedStyle(el).fontFamily||''; }catch(e){ continue; }
    if(!ff)continue;
    for(const f of FAMS){
      if(ff.indexOf(f)<0)continue;
      /* FIRST in the stack is a real use; later is only a fallback, which is
         a much weaker claim and should not block deleting the @font-face. */
      const first=ff.split(',')[0].replace(/['"]/g,'').trim();
      const isPrimary=(first===f);
      hit[f]=(hit[f]||0)+1;
      if(isPrimary){
        out.reach[f]++;
        if(out.samples[f].length<3)
          out.samples[f].push(where+': '+(el.id?('#'+el.id):(el.className&&typeof el.className==='string'?('.'+el.className.split(' ')[0]):el.tagName)));
      }
    }
  }
  out.perScreen[where]=hit;
}

await sleep(1000); scan('menu');
try{ showScreen('shop'); }catch(e){ out.shopErr=String(e); }
await sleep(1400); scan('shop');
try{ showScreen('gauntlet'); }catch(e){ out.gauntErr=String(e); }
await sleep(1400); scan('gauntlet');
try{ showScreen('gameover'); }catch(e){ out.goErr=String(e); }
await sleep(1400); scan('gameover');
try{ showScreen('menu'); }catch(e){}
await sleep(600);

/* the loadout and the enchant store, which are overlays rather than screens */
try{ famLoadoutShow(); }catch(e){ out.loErr=String(e); }
await until(()=>document.getElementById('gbLoadout'),6000); await sleep(900);
scan('loadout');
try{ document.getElementById('gbLoadout').remove(); }catch(e){}

/* then a real run, for the screens that only exist mid-play */
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
scan('new run');
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(()=>[...document.querySelectorAll('.ptcard')].filter(vis).length>0,9000);
await sleep(800); scan('patron select');
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0]; if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
await sleep(800); scan('match');
try{ dbgWin(); }catch(e){}
await until(()=>vis(document.getElementById('end-ov')),9000);
/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather
   than throwing, so discarding this result meant every assertion below
   ran against a state that may never have arrived - and reported the
   result as a verdict about the game. Three probes were fixed one at a
   time for exactly this before it was swept for. */
const _pre = await until(()=>document.querySelector('.fo-offer'),12000);
if (!_pre) return { skip: 'precondition never arrived: apv_font_reach had nothing to measure' };
await sleep(1000); scan('win');

try{ await document.fonts.ready; FAMS.forEach(f=>{out.loaded[f]=document.fonts.check('16px "'+f+'"');}); }catch(e){}

out.unreachable=FAMS.filter(f=>out.reach[f]===0);
out.verdict={
  measuredEveryScreen: Object.keys(out.perScreen).length>=9,
  gameFontReachable:   out.reach['JMH Beda']>0
};
return out;
