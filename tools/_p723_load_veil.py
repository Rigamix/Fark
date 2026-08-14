# -*- coding: utf-8 -*-
"""P723: the load veil - a screen change goes black until its art is ready.

Denis: "put a black frame over everything that fades off once all assets
are loaded... so I don't see objects loading one after the other."

showScreen is the one navigation funnel, so the veil lives there: an
instant black cover on every REAL screen change (re-renders of the current
screen - the room's chips re-call showScreen('gauntlet') - never flash),
released by watching every <img> the arriving screen holds: the fade
starts when the last one loads or errors, with a 2.5s cap so a stalled
fetch can never wedge the game behind the veil. A token guards rapid
double-navigations. Boot keeps its veil too: black into the title is the
same promise. Overlay surfaces that bypass showScreen (shelf, shop sheet,
Last Orders) are out of scope here by design - they are already light.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"let _currentScreen = 'menu';\n"
    u"function showScreen(name, data) {\n"
    u"  document.querySelectorAll('.screen.active').forEach(s => s.classList.remove('active'));\n"
    u"  document.getElementById('screen-' + name).classList.add('active');\n"
    u"  _currentScreen = name;",
    u"let _currentScreen = 'menu';\n"
    u"/* P723: THE LOAD VEIL. A screen change goes black instantly and fades\n"
    u"   back once every image the arriving screen holds has loaded or errored\n"
    u"   - art never pops in piece by piece (Denis). Inline styles on purpose:\n"
    u"   they read back reliably and no cascade can fight them. */\n"
    u"var _veilEl=null,_veilTok=0;\n"
    u"function _loadVeilShow(){\n"
    u"  if(!_veilEl){\n"
    u"    _veilEl=document.createElement('div');_veilEl.id='loadVeil';\n"
    u"    _veilEl.style.cssText='position:fixed;inset:0;background:#000;z-index:2147480000;display:none;opacity:0';\n"
    u"    document.body.appendChild(_veilEl);\n"
    u"  }\n"
    u"  _veilEl.style.transition='none';\n"
    u"  _veilEl.style.opacity='1';\n"
    u"  _veilEl.style.display='block';\n"
    u"  _veilEl.style.pointerEvents='auto';\n"
    u"}\n"
    u"function _loadVeilRelease(scope){\n"
    u"  var tok=++_veilTok;\n"
    u"  /* one beat so the arriving screen's init has injected its DOM */\n"
    u"  setTimeout(function(){\n"
    u"    if(tok!==_veilTok)return;\n"
    u"    var imgs=[];\n"
    u"    try{imgs=[].slice.call((scope||document).querySelectorAll('img'))\n"
    u"      .filter(function(i){return i.src&&!i.complete;});}catch(e){}\n"
    u"    var left=imgs.length,done=false;\n"
    u"    function go(){\n"
    u"      if(done||tok!==_veilTok)return;done=true;\n"
    u"      requestAnimationFrame(function(){\n"
    u"        if(!_veilEl||tok!==_veilTok)return;\n"
    u"        _veilEl.style.transition='opacity .3s ease';\n"
    u"        _veilEl.style.opacity='0';\n"
    u"        _veilEl.style.pointerEvents='none';\n"
    u"        setTimeout(function(){if(tok===_veilTok&&_veilEl)_veilEl.style.display='none';},380);\n"
    u"      });\n"
    u"    }\n"
    u"    function one(){if(--left<=0)go();}\n"
    u"    if(!left){go();return;}\n"
    u"    imgs.forEach(function(i){\n"
    u"      i.addEventListener('load',one,{once:true});\n"
    u"      i.addEventListener('error',one,{once:true});\n"
    u"    });\n"
    u"    /* the cap: a 404 or stalled fetch must never wedge the game */\n"
    u"    setTimeout(go,2500);\n"
    u"  },60);\n"
    u"}\n"
    u"var _veilFirstNav=true;/* boot's first showScreen veils too - black into the title */\n"
    u"function showScreen(name, data) {\n"
    u"  var _veilOn=(_currentScreen!==name)||_veilFirstNav;\n"
    u"  _veilFirstNav=false;\n"
    u"  if(_veilOn)_loadVeilShow();\n"
    u"  document.querySelectorAll('.screen.active').forEach(s => s.classList.remove('active'));\n"
    u"  document.getElementById('screen-' + name).classList.add('active');\n"
    u"  _currentScreen = name;",
    'P723 veil plumbing + show at switch')

sub(u"    case 'match': initMatchScreen(data); break;\n"
    u"    case 'gameover': initGameOverScreen(); break;\n"
    u"  }\n"
    u"}",
    u"    case 'match': initMatchScreen(data); break;\n"
    u"    case 'gameover': initGameOverScreen(); break;\n"
    u"  }\n"
    u"  if(_veilOn)_loadVeilRelease(document.getElementById('screen-'+name));/* P723 */\n"
    u"}",
    'P723 release after init')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
