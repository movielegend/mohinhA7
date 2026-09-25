import math
import numpy as np
import trimesh, manifold3d as mf
def rr(w,h,r,n=20):
 r=min(r,w/2,h/2);p=[]
 for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for t in np.linspace(a,a+90,n,endpoint=False):p.append((cx+r*np.cos(np.deg2rad(t)),cy+r*np.sin(np.deg2rad(t))))
 return np.array(p)

def prism(w, h, r, d, axis='z', pos=(0, 0, 0)):
    m = mf.CrossSection([rr(w, h, r)]).extrude(d).translate((0, 0, -d / 2))
    if axis == 'x':
        m = m.rotate((0, 90, 0))
    if axis == 'y':
        m = m.rotate((-90, 0, 0))
    return m.translate(pos)

def disc(rad, d, pos=(0, 0, 0), axis='z', inner=0, segments=64):
    m = mf.Manifold.cylinder(d, rad, rad, segments, True)
    if inner:
        m = m - mf.Manifold.cylinder(d + 2, inner, inner, segments, True)
    if axis == 'x':
        m = m.rotate((0, 90, 0))
    if axis == 'y':
        m = m.rotate((-90, 0, 0))
    return m.translate(pos)

def rounded_prism(w, h, r, d, b=1.5):
    b = min(b, d / 2 - 0.001)
    layers = []
    for t in np.linspace(0, math.pi / 2, 18):
        layers.append((-d / 2 + b * (1 - math.cos(t)), b * (1 - math.sin(t))))
    for t in np.linspace(math.pi / 2, 0, 18):
        layers.append((d / 2 - b * (1 - math.cos(t)), b * (1 - math.sin(t))))
    v = []
    f = []
    n = len(rr(w, h, r))
    for z, inset in layers:
        v.extend(((xx, yy, z) for xx, yy in rr(w - 2 * inset, h - 2 * inset, max(0.1, r - inset))))
    for k in range(len(layers) - 1):
        for i in range(n):
            j = (i + 1) % n
            a = k * n + i
            c = k * n + j
            f.extend([(a, c, c + n), (a, c + n, a + n)])
    v.extend([(0, 0, -d / 2), (0, 0, d / 2)])
    a = len(v) - 2
    b0 = len(v) - 1
    for i in range(n):
        j = (i + 1) % n
        f.extend([(a, j, i), (b0, (len(layers) - 1) * n + i, (len(layers) - 1) * n + j)])
    m = trimesh.Trimesh(v, f, process=True)
    m.fix_normals()
    return mf.Manifold(mf.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))

def lathe(profile, cx=0, cy=0, n=128):
    v = []
    f = []
    for radius, z in profile:
        v.extend(((cx + radius * math.cos(t), cy + radius * math.sin(t), z) for t in np.linspace(0, math.tau, n, endpoint=False)))
    for k in range(len(profile)):
        kk = (k + 1) % len(profile)
        for i in range(n):
            j = (i + 1) % n
            f.extend([(k * n + i, k * n + j, kk * n + j), (k * n + i, kk * n + j, kk * n + i)])
    m = trimesh.Trimesh(v, f, process=True)
    m.fix_normals()
    return m

def dome(cx, cy, r, z, depth):
    n = 128
    rings = 35
    v = [(cx, cy, z + depth)]
    f = []
    for k in range(1, rings + 1):
        rr0 = r * k / rings
        for t in np.linspace(0, math.tau, n, endpoint=False):
            v.append((cx + rr0 * math.cos(t), cy + rr0 * math.sin(t), z + depth * (1 - (rr0 / r) ** 2)))
    for i in range(n):
        f.append((0, i + 1, 1 + (i + 1) % n))
    for k in range(rings - 1):
        a = 1 + k * n
        b = a + n
        for i in range(n):
            j = (i + 1) % n
            f.extend([(a + i, b + i, b + j), (a + i, b + j, a + j)])
    return trimesh.Trimesh(v, f, process=False)