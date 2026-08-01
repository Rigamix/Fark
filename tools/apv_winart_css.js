const want=['.win-art','.win-art img','.win-bg','.win-banner','.win-hands','.win-panel',
            '#end-ov.win-art-on .win-art'];
const seen=new Set();
for(const sh of document.styleSheets){
  let rs=null;try{rs=sh.cssRules;}catch(e){continue;}
  const walk=r=>{for(const x of r){if(x.selectorText)seen.add(x.selectorText.trim());if(x.cssRules)walk(x.cssRules);}};
  walk(rs);
}
const el=document.querySelector('.win-art'), img=document.querySelector('.win-bg');
const box=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {w:Math.round(r.width),h:Math.round(r.height)};};
return {
  missing:want.filter(w=>!seen.has(w)),
  winArtBox:box(el), bgBox:box(img),
  winArtComputed:el?{position:getComputedStyle(el).position,inset:getComputedStyle(el).inset,
                     display:getComputedStyle(el).display,opacity:getComputedStyle(el).opacity}:null,
  bgComputed:img?{position:getComputedStyle(img).position,width:getComputedStyle(img).width,
                  height:getComputedStyle(img).height,natural:img.naturalWidth+'x'+img.naturalHeight}:null,
  parentOfArt:el?el.parentElement.id:null
};
