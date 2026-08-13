# -*- coding: utf-8 -*-
"""P693: launching over a pending match resumes it - no question asked.

Denis, seeing P692's confirm: "Can you bring me to the match automatically
rather than ask?" So the guard stops being a question: tap any seat while a
match is waiting and you are simply back at that table. Abandoning stays a
deliberate act (Settings -> ABANDON MATCH, or fleeing in-match) - which is
the right place for the destructive path anyway. The modal helper goes with
its only callers; the heart-charge enforcement in initMatchScreen stays for
whatever other route ever reaches it.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# the modal helper goes; the seat guard resumes instead
i = s.index(u"function _confirmDiscardPending(onYes){")
j = s.index(u"\n}\n", i) + 3
s = s[:i] + u"/* P693: _confirmDiscardPending removed - launching over a pending match\n   RESUMES it now, per Denis. Abandoning is Settings' job. */\n" + s[j:]
n += 1
print('  ok  P693 modal helper removed')

sub(u"function launchSeat(seatIdx){\n"
    u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){\n"
    u"    _confirmDiscardPending(function(){window._fkDiscardOk=true;try{launchSeat(seatIdx);}finally{window._fkDiscardOk=false;}});\n"
    u"    return;\n"
    u"  }",
    u"function launchSeat(seatIdx){\n"
    u"  /* P693: a waiting match takes precedence - straight back to the table,\n"
    u"     no modal (Denis: \"bring me to the match automatically\"). Probes and\n"
    u"     the deliberate-abandon path can set _fkDiscardOk to launch anyway. */\n"
    u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){resumeMatch();return;}",
    'P693 seat launch resumes')

sub(u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){\n"
    u"    _confirmDiscardPending(function(){window._fkDiscardOk=true;try{launchBossMatch();}finally{window._fkDiscardOk=false;}});\n"
    u"    return;\n"
    u"  }",
    u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){resumeMatch();return;}/* P693 */",
    'P693 boss launch resumes')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
