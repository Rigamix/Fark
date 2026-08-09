# -*- coding: utf-8 -*-
"""Read a .glb and say what is actually in it.

No gltf library is installed and there is no Blender on PATH, so this parses
the container directly. GLB is small and documented: a 12-byte header
(magic 'glTF', version, total length) followed by chunks, each a 8-byte header
(length, type) then payload. Chunk type 0x4E4F534A is the JSON, 0x004E4942 the
binary buffer.

Read-only. It never writes to Art/ - those are Denis's source files.
"""
import sys, json, struct, os

ACC_TYPE_N = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16}
COMP = {5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}


def load(path):
    raw = open(path, 'rb').read()
    magic, ver, total = struct.unpack('<4sII', raw[:12])
    if magic != b'glTF':
        raise SystemExit('not a GLB: magic is %r' % magic)
    js, binc, off = None, None, 12
    while off < len(raw):
        clen, ctype = struct.unpack('<II', raw[off:off+8])
        body = raw[off+8:off+8+clen]
        if ctype == 0x4E4F534A:
            js = json.loads(body.decode('utf-8'))
        elif ctype == 0x004E4942:
            binc = body
        off += 8 + clen + ((4 - (clen % 4)) % 4 if clen % 4 else 0)
    return js, binc, ver, total


def accessor_data(g, binc, idx):
    """Return a flat list of numbers for accessor idx. Handles byteStride."""
    a = g['accessors'][idx]
    n = ACC_TYPE_N[a['type']]
    fmt, size = COMP[a['componentType']]
    count = a['count']
    if 'bufferView' not in a:
        return [0] * (count * n)
    bv = g['bufferViews'][a['bufferView']]
    base = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride') or (size * n)
    out = []
    for i in range(count):
        s = base + i * stride
        out.extend(struct.unpack_from('<' + fmt * n, binc, s))
    return out


def main(path):
    g, binc, ver, total = load(path)
    print('file      : %s' % os.path.basename(path))
    print('size      : %d bytes   glTF version %d' % (total, ver))
    print('generator : %s' % g.get('asset', {}).get('generator', '-'))
    print('bin chunk : %d bytes' % (len(binc) if binc else 0))
    print()
    print('meshes    : %d   materials: %d   images: %d   textures: %d   nodes: %d'
          % (len(g.get('meshes', [])), len(g.get('materials', [])),
             len(g.get('images', [])), len(g.get('textures', [])),
             len(g.get('nodes', []))))
    for mi, m in enumerate(g.get('meshes', [])):
        print()
        print('mesh %d: %r  (%d primitive%s)'
              % (mi, m.get('name', '-'), len(m['primitives']),
                 '' if len(m['primitives']) == 1 else 's'))
        for pi, p in enumerate(m['primitives']):
            attrs = p.get('attributes', {})
            vcount = g['accessors'][attrs['POSITION']]['count'] if 'POSITION' in attrs else 0
            icount = g['accessors'][p['indices']]['count'] if 'indices' in p else 0
            print('  prim %d: mode %s  verts %d  indices %d  tris %d'
                  % (pi, p.get('mode', 4), vcount, icount, icount // 3 if icount else vcount // 3))
            print('     attributes : %s' % ', '.join(sorted(attrs.keys())))
            print('     HAS UVs    : %s' % ('YES' if 'TEXCOORD_0' in attrs else 'NO'))
            if 'material' in p:
                mat = g['materials'][p['material']]
                pbr = mat.get('pbrMetallicRoughness', {})
                print('     material   : %r  baseColorTexture=%s'
                      % (mat.get('name', '-'), 'yes' if 'baseColorTexture' in pbr else 'no'))
            if 'POSITION' in attrs:
                acc = g['accessors'][attrs['POSITION']]
                if 'min' in acc and 'max' in acc:
                    mn, mx = acc['min'], acc['max']
                    print('     bounds     : min %s' % ['%.4f' % v for v in mn])
                    print('                  max %s' % ['%.4f' % v for v in mx])
                    print('     size       : %s' % ['%.4f' % (mx[i]-mn[i]) for i in range(3)])
            if 'NORMAL' in attrs and 'POSITION' in attrs:
                nrm = accessor_data(g, binc, attrs['NORMAL'])
                # how many distinct normal directions? a hard-edged cube has 6
                buckets = {}
                for i in range(0, len(nrm), 3):
                    key = tuple(round(nrm[i+k], 2) for k in range(3))
                    buckets[key] = buckets.get(key, 0) + 1
                axis = [k for k in buckets if sorted(abs(c) for c in k)[:2] == [0.0, 0.0]]
                print('     distinct normals: %d   (axis-aligned: %d)'
                      % (len(buckets), len(axis)))
                top = sorted(buckets.items(), key=lambda kv: -kv[1])[:8]
                for k, v in top:
                    print('        %-22s %d verts' % (str(k), v))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'die_new.glb')
