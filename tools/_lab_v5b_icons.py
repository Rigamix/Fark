# -*- coding: utf-8 -*-
"""Lab v5b: at-a-glance glyphs on every sequencer node - motions,
visuals, sounds, text. Tiny inline SVGs, one stroke style, so a step
chain reads like a sentence of pictograms."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_lab.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


sub(u"""  .chip{display:block;padding:6px 9px;margin:3px 0;border-radius:5px;font-size:11px;
    background:#241a0e;border:1px solid #5a4626;cursor:grab;user-select:none}""",
    u"""  .chip{display:block;padding:6px 9px;margin:3px 0;border-radius:5px;font-size:11px;
    background:#241a0e;border:1px solid #5a4626;cursor:grab;user-select:none}
  .chip svg,.step svg{vertical-align:-3px;margin-right:5px;flex:none}
  .step .st-fx{display:flex;align-items:center}""",
    'icon CSS')

ICONS_JS = u"""
/* ═══ v5b: pictograms - one 16px stroke style, every node type ═══ */
var _IC={};
(function(){
  var w=function(body){return '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'+body+'</svg>';};
  /* motion */
  _IC['motion:pop']=w('<circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.5 1.5M13 3l-1.5 1.5M3 13l1.5-1.5M13 13l-1.5-1.5"/>');
  _IC['motion:shake']=w('<path d="M4 3l-2 2 2 2M12 3l2 2-2 2"/><rect x="5.5" y="5" width="5" height="6" rx="1"/><path d="M4 13h8"/>');
  _IC['motion:spin']=w('<path d="M13 8a5 5 0 1 1-2-4"/><path d="M13 2v3h-3"/>');
  _IC['motion:rise']=w('<path d="M8 13V4M4 8l4-4 4 4"/><path d="M3 14h10"/>');
  _IC['motion:sink']=w('<path d="M8 3v9M4 8l4 4 4-4"/><path d="M3 2h10"/>');
  _IC['motion:fade']=w('<circle cx="5" cy="8" r="3"/><circle cx="11" cy="8" r="3" stroke-dasharray="2 2" opacity=".6"/>');
  _IC['motion:snap']=w('<path d="M3 4l4 4-4 4M13 4l-4 4 4 4"/>');
  /* visual */
  _IC.spray=w('<circle cx="4" cy="12" r="1.4"/><path d="M6 9l2-3M8 11l3-2M7 13h3M9 5l1-2M12 7l2-1" opacity=".9"/>');
  _IC.glow=w('<circle cx="8" cy="8" r="2.6"/><path d="M8 2v1.6M8 12.4V14M2 8h1.6M12.4 8H14M4 4l1.1 1.1M12 4l-1.1 1.1M4 12l1.1-1.1M12 12l-1.1-1.1" opacity=".8"/>');
  _IC.flash=w('<path d="M9 1L4 9h3l-1 6 6-8H9l1-6z"/>');
  _IC.beam=w('<path d="M6 14V5M10 14V5" opacity=".9"/><path d="M4 14V8M12 14V8" opacity=".5"/><path d="M3 14h10"/>');
  _IC.ghost=w('<rect x="2.5" y="2.5" width="8" height="8" rx="1.5" opacity=".5"/><rect x="5.5" y="5.5" width="8" height="8" rx="1.5"/>');
  _IC.amberShell=w('<rect x="2.5" y="2.5" width="11" height="11" rx="3.5"/><circle cx="8" cy="8" r="1.3" fill="currentColor"/>');
  _IC.clearShell=w('<rect x="2.5" y="2.5" width="11" height="11" rx="3.5" opacity=".6"/><path d="M3 13L13 3"/>');
  _IC['break']=w('<rect x="3" y="3" width="10" height="10" rx="1.5"/><path d="M8 3L6.5 7l3 1.5L7 13"/>');
  _IC.shield=w('<path d="M8 1.5l5 2v4c0 3.5-2 6-5 7-3-1-5-3.5-5-7v-4l5-2z"/>');
  _IC.candle=w('<path d="M8 6c1.6-1.8.6-3.4 0-4.5C7.4 2.6 6.4 4.2 8 6z"/><rect x="6" y="7" width="4" height="7" rx="1"/>');
  _IC.announce=w('<path d="M2.5 3.5h11v6h-6l-3 3v-3h-2v-6z"/>');
  /* sound families */
  _IC['sound:chime']=w('<path d="M5 12V4l6-1.4V10"/><circle cx="3.6" cy="12" r="1.6"/><circle cx="9.6" cy="10.6" r="1.6"/>');
  _IC['sound:coin']=w('<circle cx="8" cy="8" r="5.5"/><path d="M8 5v6M6.3 6.2h2.5a1.3 1.3 0 0 1 0 2.6H6.8a1.3 1.3 0 0 0 0 2.6h2.9"/>');
  _IC['sound:thud']=w('<path d="M8 2v6M5 5l3 3 3-3"/><path d="M2.5 12.5h11" stroke-width="2.2"/>');
  _IC['sound:crack']=w('<path d="M8 1.5L6 6l3 1.5-2.5 4L8 14.5"/><path d="M4 4L2.5 6M12 4l1.5 2" opacity=".7"/>');
  _IC['sound:set']=w('<path d="M2.5 4c2 0 3 1.5 3 4s-1 4-3 4M13.5 4c-2 0-3 1.5-3 4s1 4 3 4"/><circle cx="8" cy="8" r="1.2" fill="currentColor"/>');
  _IC['sound:shimmer']=w('<path d="M5 3l.7 1.8L7.5 5.5 5.7 6.2 5 8l-.7-1.8L2.5 5.5l1.8-.7L5 3zM11 8l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z"/>');
  _IC['sound:bell']=w('<path d="M8 2a4 4 0 0 1 4 4c0 3 .8 4 1.5 4.6H2.5C3.2 10 4 9 4 6a4 4 0 0 1 4-4z"/><path d="M6.7 13a1.4 1.4 0 0 0 2.6 0"/>');
  _IC['sound:drum']=w('<ellipse cx="8" cy="5" rx="5.5" ry="2.2"/><path d="M2.5 5v6c0 1.2 2.5 2.2 5.5 2.2s5.5-1 5.5-2.2V5"/>');
  _IC['sound:scratch']=w('<path d="M2.5 12.5c2-1 2.5-6 5-6s2 5 4.5 4 1.5-4 1.5-4" opacity=".9"/><path d="M11.5 2.5l2 2-6 6-2.6.6.6-2.6 6-6z"/>');
})();
function ic(name){
  if(_IC[name])return _IC[name];
  if(name&&name.slice(0,6)==='sound:')return _IC['sound:chime'];
  if(name&&name.slice(0,7)==='motion:')return _IC['motion:pop'];
  return '';
}
"""

sub(u"var _MOTIONS={",
    ICONS_JS + u"var _MOTIONS={",
    'icon set')

sub(u"""  var mk=function(cls,name){return '<span class="chip '+cls+'" draggable="true" ondragstart="palDrag(event,&quot;'+name+'&quot;)">'+name+'</span>';};""",
    u"""  var mk=function(cls,name){
    var label=name.replace(/^(motion|sound):/,'');
    return '<span class="chip '+cls+'" draggable="true" ondragstart="palDrag(event,&quot;'+name+'&quot;)">'+ic(name)+label+'</span>';};""",
    'palette chips get glyphs')

sub(u"""    h+='<div class="step" onclick="showTab(2)"><span class="st-fx">\\u21bb '+mn+'</span>'""",
    u"""    h+='<div class="step" onclick="showTab(2)"><span class="st-fx">'+ic('motion:'+mn)+mn+'</span>'""",
    'motion step glyph')

sub(u"""    h+='<div class="step'+(i===_selStep?' on':'')+'" onclick="stepPick('+i+')">'
      +'<span class="st-fx">'+f.fx+'</span><div class="st-sub">'+sub+'</div>'""",
    u"""    var _icn=f.fx==='sound'?ic('sound:'+(f.p.snd||'chime')):ic(f.fx);
    h+='<div class="step'+(i===_selStep?' on':'')+'" onclick="stepPick('+i+')">'
      +'<span class="st-fx">'+_icn+(f.fx==='sound'?(f.p.snd||'sound'):f.fx)+'</span><div class="st-sub">'+sub+'</div>'""",
    'fx step glyphs')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
