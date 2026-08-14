# -*- coding: utf-8 -*-
"""P719: the lucky-die TAKE retires; the grudge survives, better placed.

Denis on the lucky trophy: "I don't know, I think we could retire it as
well." Scoped by census: the lucky die itself STAYS - it is every patron's
first die (brief section 2), rolled in every match, named in the peek. What
retires is the invisible collecting: it is no longer a For Keeps option,
and luckyNames + the three_lucky grant (its only reader) go with it.

The grudge loop ("they remember you" - a later patron of the archetype
returns angrier) had the lucky take as its ONLY trigger, so retiring the
take would have silently retired the grudge too. It moves to the act that
deserves it: SEATING any die you took at For Keeps. You kept his die; the
archetype remembers.
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


# ── the offer: the lucky die is no longer on the table ──
sub(u"    var _fkDice=(G.rung&&G.rung.dice)||[];\n"
    u"    var _fkName=(G.rung&&G.rung.lucky&&G.rung.lucky.name)||'their lucky die';",
    u"    /* P719: the lucky die is the patron's own - it stays in their hand.\n"
    u"       Only the mundane five are on the table at For Keeps. */\n"
    u"    var _fkDice=((G.rung&&G.rung.dice)||[]).filter(function(m){return m!=='lucky';});",
    'P719 lucky off the For Keeps table')

sub(u"    _fkDice.forEach(function(m,i){\n"
    u"      var nm=m==='lucky'?('✦ '+_fkName):getDie(m).name;\n"
    u"      fkh+='<div onclick=\"famFkTake('+i+')\" style=\"cursor:pointer;width:64px;height:64px;background:#191919;'\n"
    u"        +'border:2px solid '+(m==='lucky'?'#dd6':'#777')+';display:flex;align-items:center;justify-content:center;'\n"
    u"        +'font-size:9px;color:#ddd;text-align:center\">'+nm+'</div>';\n"
    u"    });\n"
    u"    fkh+='</div></div>';\n"
    u"    window._fkPool=_fkDice.slice();window._fkLucky=_fkName;window._fkPersona=G.rung&&G.rung.persona;",
    u"    _fkDice.forEach(function(m,i){\n"
    u"      fkh+='<div onclick=\"famFkTake('+i+')\" style=\"cursor:pointer;width:64px;height:64px;background:#191919;'\n"
    u"        +'border:2px solid #777;display:flex;align-items:center;justify-content:center;'\n"
    u"        +'font-size:9px;color:#ddd;text-align:center\">'+getDie(m).name+'</div>';\n"
    u"    });\n"
    u"    fkh+='</div></div>';\n"
    u"    window._fkPool=_fkDice.slice();window._fkPersona=G.rung&&G.rung.persona;",
    'P719 offer renders without the lucky branch')

# ── the take: no lucky branch; the persona rides to the seat ──
sub(u"  _getS();_enchInit();\n"
    u"  /* P718: THE PRIZE SEATS IMMEDIATELY. The invisible reserve retired with\n"
    u"     Fair Trade (Denis: only the six exist) - a real die now asks which\n"
    u"     seat it takes; the lucky die stays a trophy (names + grudges), it was\n"
    u"     never a playable material. */\n"
    u"  if(m==='lucky'){\n"
    u"    S.run.luckyNames=S.run.luckyNames||[];S.run.luckyNames.push(window._fkLucky);\n"
    u"    S.run._grudges=S.run._grudges||{};\n"
    u"    if(window._fkPersona)S.run._grudges[window._fkPersona]=true;/* the archetype remembers */\n"
    u"    window._fkPool=null;save();\n"
    u"    var rc=document.querySelector('#end-ov .res-card');\n"
    u"    if(rc)rc.innerHTML='<div style=\"font-family:'+\"'JMH Beda'\"+',serif;font-size:15px;color:#3a2812;padding:30px 12px;text-align:center;line-height:1.5\">'\n"
    u"      +'✦ '+window._fkLucky+' IS YOURS — ITS OWNER WILL REMEMBER</div>';\n"
    u"    _famEndReady();\n"
    u"    return;\n"
    u"  }\n"
    u"  window._fkTaken={mat:m};\n"
    u"  window._fkPool=null;save();\n"
    u"  _fkSeatOffer();",
    u"  _getS();_enchInit();\n"
    u"  /* P718/P719: THE PRIZE SEATS IMMEDIATELY. The invisible reserve retired\n"
    u"     with Fair Trade; the lucky-die take retired with luckyNames (Denis) -\n"
    u"     the pool only ever holds real materials now, and the persona rides to\n"
    u"     the seat so the grudge lands on the act of KEEPING his die. */\n"
    u"  window._fkTaken={mat:m,persona:window._fkPersona||null};\n"
    u"  window._fkPool=null;save();\n"
    u"  _fkSeatOffer();",
    'P719 take without the lucky branch')

# ── the grudge lands where it belongs ──
sub(u"  S.run.dice[si]=t.mat;S.run.dieEnch[si]=null;\n"
    u"  window._fkTaken=null;save();",
    u"  S.run.dice[si]=t.mat;S.run.dieEnch[si]=null;\n"
    u"  /* P719: you KEPT his die - the archetype remembers. The grudge's old\n"
    u"     only trigger was the retired lucky take; this is the act it was\n"
    u"     always about. */\n"
    u"  if(t.persona){S.run._grudges=S.run._grudges||{};S.run._grudges[t.persona]=true;}\n"
    u"  window._fkTaken=null;save();",
    'P719 grudge on the kept die')

sub(u"    +getDie(t.mat).name.toUpperCase()+' TAKES THE SEAT — '+getDie(out).name.toUpperCase()+' RETIRES'\n"
    u"    +(outE?'<div style=\"font-size:11px;color:#8a4a18;margin-top:6px\">its brand goes with it</div>':'')+'</div>';",
    u"    +getDie(t.mat).name.toUpperCase()+' TAKES THE SEAT — '+getDie(out).name.toUpperCase()+' RETIRES'\n"
    u"    +(outE?'<div style=\"font-size:11px;color:#8a4a18;margin-top:6px\">its brand goes with it</div>':'')\n"
    u"    +(t.persona?'<div style=\"font-size:11px;color:#6a5238;margin-top:6px\">its owner will remember</div>':'')+'</div>';",
    'P719 the memory is said out loud')

# ── the invisible ledger and its one reader go ──
sub(u"  if((S.run.luckyNames||[]).length>=3)grant('three_lucky','THREE LUCKY DICE IN ONE RUN',25);\n",
    u"  /* P719: three_lucky retired with the lucky-die take - luckyNames has no\n"
    u"     writer any more. */\n",
    'P719 three_lucky grant retired')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
