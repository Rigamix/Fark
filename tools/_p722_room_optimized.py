# -*- coding: utf-8 -*-
"""P722: the room screen joins the optimized world.

Denis: "check this is not happening anywhere else - everything should use
optimized assets." The sweep found the biggest one still standing: the pt
room fetched ~5MB of RAW painting per visit - Grog's env BG (2.5MB) + a
foreground stage (2.3-2.5MB) - while all four optimized webps sat beside
them unreferenced (the P712/P721 bug class, third sighting). Every other
night 404'd onto the raw mockup pair bg3+fg3 (2.7MB+2.2MB); those now have
optimized copies too (197KB+134KB, generated this pass). And the room /
shelf / shop hearts drew raw mockup pngs while Art/Assets/Hearts/optimized
existed and was already used by Last Orders - the three sites join it.
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


sub(u"  var envBg=bossDir+nice+'_env_BG.png';\n"
    u"  var envFg=bossDir+nice+'_env_Foreground_'+bossStage+'.png';",
    u"  /* P722: the optimized copies existed beside the masters, unreferenced -\n"
    u"     the room fetched ~5MB of raw painting per visit (the P712/P721 bug\n"
    u"     class, third sighting). */\n"
    u"  var envBg=bossDir+'optimized/'+nice+'_env_BG_opt.webp';\n"
    u"  var envFg=bossDir+'optimized/'+nice+'_env_Foreground_'+bossStage+'_opt.webp';",
    'env layers -> optimized')

sub(u"onerror=\"this.onerror=null;this.src=PT_A+\\'bg3.png\\'\"",
    u"onerror=\"this.onerror=null;this.src=PT_A+\\'optimized/bg3_opt.webp\\'\"",
    'bg fallback -> optimized')

sub(u"onerror=\"this.onerror=null;this.src=PT_A+\\'fg3.png\\'\"",
    u"onerror=\"this.onerror=null;this.src=PT_A+\\'optimized/fg3_opt.webp\\'\"",
    'fg fallback -> optimized')

sub(u"hearts+='<img src=\"'+PT_A+(hi<(S.run.coins||0)?'heart_full':'heart_empty')+'.png\" alt=\"\">';",
    u"hearts+='<img src=\"Art/Assets/Hearts/optimized/'+(hi<(S.run.coins||0)?'heart_full_opt':'heart_empty_opt')+'.webp\" alt=\"\">';/* P722: the Hearts set Last Orders already uses */",
    'hearts -> optimized (x3)', count=3)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
