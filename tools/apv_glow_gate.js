/* THE GATE THAT KEPT THE iOS GLOW UNREACHABLE.
 * _cfBlur is script-scoped, so this cannot call it directly. Instead it runs
 * BOTH algorithms - the old string test and the new behavioural one - against
 * two worlds: this engine as it is, and this engine with the
 * CanvasRenderingContext2D.filter accessor deleted, which is what an iPhone
 * before Safari 18 looks like.
 * The claim under test: the old test cannot tell those two worlds apart. */
function oldTest(){
  try{
    var c=document.createElement('canvas').getContext('2d');
    c.filter='blur(2px)';
    return c.filter==='blur(2px)';
  }catch(e){return false;}
}
function newTest(){
  try{
    var c=document.createElement('canvas');c.width=64;c.height=64;
    var x=c.getContext('2d');
    x.filter='blur(8px)';
    x.fillStyle='#fff';x.fillRect(24,24,16,16);
    x.filter='none';
    return x.getImageData(12,32,1,1).data[3]>2;
  }catch(e){return false;}
}
/* how much light actually lands 12px clear of the square - the ground truth
   both tests are trying to predict */
function bleed(){
  try{
    var c=document.createElement('canvas');c.width=64;c.height=64;
    var x=c.getContext('2d');
    x.filter='blur(8px)';
    x.fillStyle='#fff';x.fillRect(24,24,16,16);
    x.filter='none';
    return x.getImageData(12,32,1,1).data[3];
  }catch(e){return -1;}
}

const out={};
const P=CanvasRenderingContext2D.prototype;
const desc=Object.getOwnPropertyDescriptor(P,'filter');
out.engineHasFilter=!!desc;

out.realEngine={old:oldTest(), neu:newTest(), alphaAt12px:bleed()};

/* now simulate the iPhone this bug lives on */
if(desc){
  delete P.filter;
  out.noFilterEngine={old:oldTest(), neu:newTest(), alphaAt12px:bleed()};
  Object.defineProperty(P,'filter',desc);      /* put it back */
  out.restored=!!Object.getOwnPropertyDescriptor(P,'filter');
}

out.verdict={
  /* the bug: the old test says "filter works" on an engine where it does not */
  oldTestIsFooled: out.noFilterEngine ? out.noFilterEngine.old===true : null,
  /* the fix: the new test tells the two worlds apart */
  newTestIsHonest: out.noFilterEngine
    ? (out.realEngine.neu===true && out.noFilterEngine.neu===false) : null,
  /* and it agrees with reality where reality is measurable */
  newTestMatchesPixels: out.realEngine.neu===(out.realEngine.alphaAt12px>2)
};
/* what the shipped build cached for itself on this engine */
out.shippedCache=window.__cfBlur;
return out;
