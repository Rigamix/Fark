/* Is _cfBlur() a SOUND feature test? Simulate an engine that never shipped
   CanvasRenderingContext2D.filter by deleting the prototype accessor, then
   re-run exactly the detection body from fark_proto.html. */
const out={};
const proto=CanvasRenderingContext2D.prototype;
out.hasFilterAccessor=('filter' in proto);
out.realDetect=_cfBlur();
out.D3X_cf=(typeof D3X!=='undefined')?D3X._cf:'n/a';

/* the detection body, verbatim in behaviour, but not cached */
function detect(){
  try{var c=document.createElement('canvas').getContext('2d');
      c.filter='blur(2px)';return (c.filter==='blur(2px)');}
  catch(e){return false;}
}
out.detectNow=detect();

const desc=Object.getOwnPropertyDescriptor(proto,'filter');
out.descFound=!!desc;
if(desc){
  delete proto.filter;
  out.afterDelete_inProto=('filter' in proto);
  out.afterDelete_detect=detect();      /* <-- iOS Safari < 18 answer */
  /* and does a blur actually happen without the accessor? */
  var c2=document.createElement('canvas');c2.width=64;c2.height=64;
  var g2=c2.getContext('2d');
  g2.filter='blur(8px)';
  g2.fillStyle='#fff';g2.fillRect(24,24,16,16);
  var d2=g2.getImageData(0,0,64,64).data;
  /* a real blur puts ink at (12,32); a no-op leaves it empty */
  out.afterDelete_blurRealFar=d2[((32*64)+12)*4+3];
  Object.defineProperty(proto,'filter',desc);
  out.restored=('filter' in proto);
}
/* control: with the accessor present, is the blur real? */
var c3=document.createElement('canvas');c3.width=64;c3.height=64;
var g3=c3.getContext('2d');
g3.filter='blur(8px)';g3.fillStyle='#fff';g3.fillRect(24,24,16,16);
out.control_blurAlphaFar=g3.getImageData(0,0,64,64).data[((32*64)+12)*4+3];
return out;
