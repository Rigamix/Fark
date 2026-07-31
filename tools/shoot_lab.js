const p=document.getElementById('plate');
if(!p)return {err:'no #plate'};
await new Promise(r=>{ if(p.complete&&p.naturalWidth)return r(); p.onload=r; p.onerror=r; setTimeout(r,5000); });
return {src:p.getAttribute('src'), nat:p.naturalWidth+'x'+p.naturalHeight, broken:!p.naturalWidth};
