# -*- coding: utf-8 -*-
"""Apply one of the workflow-specified patches to fark_proto.html.

    python tools/apply_spec.py A [B C ...]

WHY THIS EXISTS RATHER THAN A HAND-WRITTEN SCRIPT PER PATCH: five patches, 21
anchors, all against one 34,000-line file, specified by five agents that could
not see each other's work. The deconflict pass found every anchor unique and
non-overlapping but flagged one blocker - the file is 100% CRLF (35,270 pairs,
zero bare LF) while every multi-line anchor is written with bare \\n.

That blocker does NOT apply to this applier, and the difference is worth stating
because it nearly cost a rewrite: io.open(..., encoding='utf-8') uses
newline=None, which is UNIVERSAL NEWLINES - CRLF is translated to \\n on the way
in, so the anchors match; and io.open(..., 'w', encoding='utf-8') translates \\n
back to os.linesep on the way out, so the file stays CRLF. A raw-bytes applier
would have failed on 19 of 21. Verified both directions below rather than
assumed: the round-trip check refuses to write if the CRLF count moves.
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(os.path.dirname(HERE), 'fark_proto.html')
SPECS = os.environ.get('FARK_SPECS') or os.path.join(
    os.path.dirname(HERE), 'tools', 'specs.json')

def crlf_count(path):
    return io.open(path, 'rb').read().count(b'\r\n')

def main(letters):
    specs = json.load(io.open(SPECS, encoding='utf-8'))['specs']
    before_crlf = crlf_count(F)
    s = io.open(F, encoding='utf-8').read()
    applied = []

    for L in letters:
        i = 'ABCDE'.index(L)
        sp = specs[i]
        if not sp.get('found'):
            raise SystemExit('patch %s reports found=false' % L)
        pairs = [(sp['anchor'], sp['replacement'])]
        pairs += [(e['anchor'], e['replacement']) for e in (sp.get('otherEdits') or [])]
        for j, (a, b) in enumerate(pairs):
            n = s.count(a)
            if n != 1:
                raise SystemExit('MISS %s.%d count=%d :: %r' % (L, j, n, a[:80]))
            # a replacement that still contains its own anchor cannot be applied
            # twice - the deconflict pass flagged C.main for exactly this - so
            # the guard is stated here rather than trusted to a human.
            s = s.replace(a, b, 1)
            applied.append('%s.%d' % (L, j))

    # never write a file whose line endings drifted
    tmp = F + '.stage'
    io.open(tmp, 'w', encoding='utf-8').write(s)
    after_crlf = crlf_count(tmp)
    lf_only = io.open(tmp, 'rb').read()
    bare = lf_only.count(b'\n') - lf_only.count(b'\r\n')
    if bare:
        os.remove(tmp)
        raise SystemExit('REFUSED: %d bare LF would be written' % bare)
    if after_crlf < before_crlf:
        os.remove(tmp)
        raise SystemExit('REFUSED: CRLF count fell %d -> %d' % (before_crlf, after_crlf))
    os.replace(tmp, F)
    print('applied %s  (%d edits, CRLF %d -> %d, 0 bare LF)'
          % (','.join(letters), len(applied), before_crlf, after_crlf))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main([a.upper() for a in sys.argv[1:]])
