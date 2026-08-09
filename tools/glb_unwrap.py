# -*- coding: utf-8 -*-
"""Box-unwrap the die and write a new GLB: centred, scaled to match, seams on
the bevel centres.

die_new.glb arrived with NO UVs - 438 verts, 576 tris, one fallback material.
Nothing can be painted on it until it has an unwrap.

DENIS'S THREE REQUIREMENTS, each handled explicitly:

  CENTRED. The source is not: X and Y straddle zero but Z runs 0.23 to 29.54,
  so the model sits on the origin instead of around it. Every vertex is moved
  by the bounding-box centre. A die that spins about a point off its own centre
  wobbles, and the physics box in the lab is centred on the body.

  SCALE MATCHED. The source is ~29.7 units across; the die the game actually
  uses (die.glb) is 0.0295. Scaled to the same longest-axis size so the new
  mesh is a drop-in rather than something every consumer has to renormalise.

  SEAMS ON THE BEVEL CENTRES, not where the bevel meets the flat face. Two
  parts to that, and only doing one of them looks right but is not:

    1. which island a triangle belongs to - by dominant face normal, so a bevel
       triangle goes to whichever face it leans toward and the boundary falls
       along the 45-degree line, which IS the bevel centre.
    2. WHERE that boundary lands in UV space - the island is projected to span
       flat_half + halfBevel, so the bevel centre maps exactly onto the cell
       edge. Projecting the whole silhouette instead would put the seam at the
       cell edge but the bevel centre somewhere inside it, and the painted seam
       would not sit where the geometric one does.

  So each cell is: the flat face in the middle, half a bevel of gutter all
  round, and the cut exactly on the ridge line. Bilinear filtering then blends
  across the least visible part of the die instead of across a pip.

LAYOUT - a 3x2 atlas ordered by PIP NUMBER, using the convention
die3d_lab.html already encodes (MAP = {1:'py',6:'ny',2:'px',5:'nx',3:'pz',4:'nz'}),
so opposite faces sum to seven and a texture painted here lands on the face the
game already believes it is. Read out of the lab rather than invented.

    +--------+--------+--------+
    |   1    |   2    |   3    |
    +--------+--------+--------+
    |   4    |   5    |   6    |
    +--------+--------+--------+

Vertices are split per (vertex, face slot): a bevel vertex is shared by
triangles of different faces and one vertex carries one UV, so it must become
several. Inherent to a box unwrap, and cheap at this size.

WRITES A NEW FILE, never the input. Art/ is Denis's.
"""
import sys, json, struct, os

ACC_TYPE_N = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
COMP = {5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}

PIP_AXIS = {1:'py', 2:'px', 3:'pz', 4:'nz', 5:'nx', 6:'ny'}
AXIS_VEC = {'px':(1,0,0),'nx':(-1,0,0),'py':(0,1,0),'ny':(0,-1,0),'pz':(0,0,1),'nz':(0,0,-1)}
# A 3x2 grid inside a SQUARE image gives cells of 341x512 - every face
# stretched 1.5x vertically. Cells must be square IN PIXELS, and the only
# arrangement of six that is square and leaves both image dimensions a power of
# two is 4x2 in 2048x1024: cells of 512x512, six used, one spare column.
# NPOT would have worked on WebGL2 and gone black on WebGL1 with mipmaps, and
# the lab does not guarantee which it gets.
CELL = {1:(0,0), 2:(1,0), 3:(2,0), 4:(0,1), 5:(1,1), 6:(2,1)}
COLS, ROWS = 4, 2
# in-plane axes per face, and sign flips so a painted square is not mirrored
# (u axis, v axis, u sign, v sign) with v measured UPWARD in the cell.
# A face reads correctly from outside when U x Vdown == -N. py and ny were
# both mirrored - the digits came out backwards on the top and bottom faces -
# and the check below now runs on every build so it cannot regress.
PLANE = {'px':(2,1,-1, 1), 'nx':(2,1, 1, 1),
         'py':(0,2, 1,-1), 'ny':(0,2, 1, 1),
         'pz':(0,1, 1, 1), 'nz':(0,1,-1, 1)}


def _check_handedness():
    def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    bad = []
    for k,(ua,va,us,vs) in PLANE.items():
        U=[0,0,0]; U[ua]=us
        Vup=[0,0,0]; Vup[va]=vs
        Vd=tuple(-c for c in Vup)
        if cross(tuple(U),Vd) != tuple(-x for x in AXIS_VEC[k]):
            bad.append(k)
    if bad:
        raise SystemExit('GATE FAILED: these faces are mirrored: %s' % ', '.join(sorted(bad)))
    return True
TARGET_SIZE = 0.0295           # die.glb's longest axis - the in-game scale


def load(path):
    raw = open(path,'rb').read()
    if raw[:4] != b'glTF':
        raise SystemExit('not a GLB')
    js = binc = None; off = 12
    while off < len(raw):
        clen, ctype = struct.unpack('<II', raw[off:off+8])
        body = raw[off+8:off+8+clen]
        if ctype == 0x4E4F534A: js = json.loads(body.decode('utf-8').rstrip('\x00 '))
        elif ctype == 0x004E4942: binc = body
        off += 8 + clen + ((4 - (clen % 4)) % 4 if clen % 4 else 0)
    return js, binc


def acc(g, binc, idx):
    a = g['accessors'][idx]; n = ACC_TYPE_N[a['type']]
    fmt, size = COMP[a['componentType']]
    bv = g['bufferViews'][a['bufferView']]
    base = bv.get('byteOffset',0) + a.get('byteOffset',0)
    stride = bv.get('byteStride') or (size*n)
    return [struct.unpack_from('<'+fmt*n, binc, base+i*stride) for i in range(a['count'])]


def dominant_axis(nx, ny, nz):
    best, key = -2.0, 'px'
    for k, v in AXIS_VEC.items():
        d = nx*v[0]+ny*v[1]+nz*v[2]
        if d > best: best, key = d, k
    return key


def main(src, dst):
    _check_handedness()   # every face reads correctly from outside, or stop
    g, binc = load(src)
    prim = g['meshes'][0]['primitives'][0]
    pos = [list(p) for p in acc(g, binc, prim['attributes']['POSITION'])]
    nrm = acc(g, binc, prim['attributes']['NORMAL'])
    idx = [t[0] for t in acc(g, binc, prim['indices'])]

    # ---- CENTRE, then SCALE to the in-game die ---------------------------
    mn = [min(p[i] for p in pos) for i in range(3)]
    mx = [max(p[i] for p in pos) for i in range(3)]
    ctr = [(mn[i]+mx[i])/2.0 for i in range(3)]
    src_size = max(mx[i]-mn[i] for i in range(3))
    s = TARGET_SIZE / src_size
    print('source bounds : min %s' % ['%.3f'%v for v in mn])
    print('                max %s' % ['%.3f'%v for v in mx])
    print('centre offset : %s' % ['%.3f'%-v for v in ctr])
    print('scale         : %.6f   (%.3f -> %.4f, matching die.glb)'
          % (s, src_size, TARGET_SIZE))
    pos = [[(p[i]-ctr[i])*s for i in range(3)] for p in pos]

    # ---- per-face flat extent and bevel half-width -----------------------
    # the flat face is the vertices whose normal IS the axis; the silhouette is
    # everything assigned to that face. The island spans flat + halfBevel so the
    # bevel CENTRE lands exactly on the cell edge.
    face_verts = {k: [] for k in AXIS_VEC}
    for vi, n in enumerate(nrm):
        for k, v in AXIS_VEC.items():
            if n[0]*v[0]+n[1]*v[1]+n[2]*v[2] > 0.999:
                face_verts[k].append(vi)

    tri_slot = []
    slot_verts = {k: set() for k in AXIS_VEC}
    for t in range(0, len(idx), 3):
        tri = idx[t:t+3]
        ax = sum(nrm[v][0] for v in tri); ay = sum(nrm[v][1] for v in tri); az = sum(nrm[v][2] for v in tri)
        k = dominant_axis(ax, ay, az)
        tri_slot.append(k)
        for v in tri: slot_verts[k].add(v)

    island = {}
    print()
    print('per face: flat extent, silhouette extent, island (flat + half bevel)')
    for k in AXIS_VEC:
        ua, va, us, vs = PLANE[k]
        flat = face_verts[k]; sil = slot_verts[k]
        if not flat:
            raise SystemExit('no flat face found for %s - is this a rounded cube?' % k)
        halves = []
        for axis in (ua, va):
            fh = max(abs(pos[v][axis]) for v in flat)
            sh = max(abs(pos[v][axis]) for v in sil)
            halves.append((fh + sh) / 2.0)   # the bevel centre
        island[k] = halves
        print('  %s: flat %.5f/%.5f  sil %.5f/%.5f  island %.5f/%.5f'
              % (k,
                 max(abs(pos[v][ua]) for v in flat), max(abs(pos[v][va]) for v in flat),
                 max(abs(pos[v][ua]) for v in sil),  max(abs(pos[v][va]) for v in sil),
                 halves[0], halves[1]))

    axis_of_pip = {v:k for k,v in PIP_AXIS.items()}
    newpos, newnrm, newuv, newidx = [], [], [], []
    remap = {}
    clamped = 0

    for ti in range(len(tri_slot)):
        tri = idx[ti*3:ti*3+3]
        k = tri_slot[ti]
        pip = axis_of_pip[k]
        col, row = CELL[pip]
        u0, v0 = col/float(COLS), row/float(ROWS)
        cw, ch = 1.0/COLS, 1.0/ROWS
        ua, va, us, vs = PLANE[k]
        hu, hv = island[k]
        for vi in tri:
            key = (vi, k)
            if key not in remap:
                p = pos[vi]
                fu = 0.5 + (p[ua]/(2.0*hu))*us
                fv = 0.5 + (p[va]/(2.0*hv))*vs
                if fu < 0 or fu > 1 or fv < 0 or fv > 1: clamped += 1
                fu = min(1.0, max(0.0, fu)); fv = min(1.0, max(0.0, fv))
                remap[key] = len(newpos)
                newpos.append(p); newnrm.append(list(nrm[vi]))
                # glTF UV origin is top-left, so v is flipped into the cell
                newuv.append((u0 + fu*cw, v0 + (1.0-fv)*ch))
            newidx.append(remap[key])

    print()
    print('verts %d -> %d   tris %d' % (len(pos), len(newpos), len(idx)//3))
    print('UVs clamped to their cell: %d  (the outer half of each bevel, by design)' % clamped)

    # ---- pack ------------------------------------------------------------
    def pad(b, fill): return b + fill * ((4 - len(b) % 4) % 4)
    b_pos = b''.join(struct.pack('<3f', *p) for p in newpos)
    b_nrm = b''.join(struct.pack('<3f', *n) for n in newnrm)
    b_uv  = b''.join(struct.pack('<2f', *u) for u in newuv)
    use32 = len(newpos) > 65535
    b_idx = b''.join(struct.pack('<I' if use32 else '<H', i) for i in newidx)
    blob = pad(b_pos, b'\x00') + pad(b_nrm, b'\x00') + pad(b_uv, b'\x00') + pad(b_idx, b'\x00')
    o_nrm = len(pad(b_pos, b'\x00')); o_uv = o_nrm + len(pad(b_nrm, b'\x00'))
    o_idx = o_uv + len(pad(b_uv, b'\x00'))

    out = {
      'asset':{'version':'2.0','generator':'fark glb_unwrap.py - centred, scaled, seams on bevel centres'},
      'scene':0,'scenes':[{'nodes':[0]}],
      'nodes':[{'mesh':0,'name':'die_new_uv'}],
      'meshes':[{'name':'die_new_uv','primitives':[{
          'attributes':{'POSITION':0,'NORMAL':1,'TEXCOORD_0':2},
          'indices':3,'material':0,'mode':4}]}],
      'materials':[{'name':'die_uv','doubleSided':False,
          'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],
                                  'metallicFactor':0.0,'roughnessFactor':0.75}}],
      'buffers':[{'byteLength':len(blob)}],
      'bufferViews':[
          {'buffer':0,'byteOffset':0,    'byteLength':len(b_pos),'target':34962},
          {'buffer':0,'byteOffset':o_nrm,'byteLength':len(b_nrm),'target':34962},
          {'buffer':0,'byteOffset':o_uv, 'byteLength':len(b_uv), 'target':34962},
          {'buffer':0,'byteOffset':o_idx,'byteLength':len(b_idx),'target':34963}],
      'accessors':[
          {'bufferView':0,'componentType':5126,'count':len(newpos),'type':'VEC3',
           'min':[min(p[i] for p in newpos) for i in range(3)],
           'max':[max(p[i] for p in newpos) for i in range(3)]},
          {'bufferView':1,'componentType':5126,'count':len(newnrm),'type':'VEC3'},
          {'bufferView':2,'componentType':5126,'count':len(newuv),'type':'VEC2'},
          {'bufferView':3,'componentType':5125 if use32 else 5123,
           'count':len(newidx),'type':'SCALAR'}],
    }
    # THE JSON CHUNK PADS WITH SPACES, NOT NULs. The first version of this
    # writer padded with \x00 and produced a file whose JSON chunk would not
    # parse - caught by re-inspecting the output rather than by trusting it.
    js = pad(json.dumps(out, separators=(',',':')).encode('utf-8'), b' ')
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(dst,'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(blob), 0x004E4942)); f.write(blob)

    nb = [min(p[i] for p in newpos) for i in range(3)]
    xb = [max(p[i] for p in newpos) for i in range(3)]
    print()
    print('wrote  : %s  (%d bytes)' % (dst, total))
    print('bounds : min %s' % ['%.5f'%v for v in nb])
    print('         max %s' % ['%.5f'%v for v in xb])
    print('centre : %s   (want ~0,0,0)' % ['%+.6f'%((nb[i]+xb[i])/2) for i in range(3)])
    print('size   : %s   (want ~%.4f)' % (['%.5f'%(xb[i]-nb[i]) for i in range(3)], TARGET_SIZE))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'die_new_uv.glb'))
