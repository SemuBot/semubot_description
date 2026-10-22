#!/usr/bin/env python3
"""Turn the Onshape URDF export of the V2 wheelbase into the two meshes used by
urdf/semubot_v2.urdf.xacro, and print the geometry the xacro needs.

  python3 scripts/onshape_v2_meshes.py <export>/urdf/base_frames_vNN.urdf meshes/v2

The export is one rigid link with ~600 glTF parts. This keeps the visible parts
(no bearings, screws, washers, pins), decimates them (CELL) and merges them into
  base_frame.stl - everything that does not rotate, in base_link coordinates
  omni_ball.stl  - one omni-ball, centred, drive axle along x
Only numpy is needed. Frame "forward" is the battery side: the bisector of the
two wheels the battery sits between.
"""
import base64
import json
import math
import os
import struct
import sys
import xml.etree.ElementTree as ET

import numpy as np

CELL = 0.003  # m, vertex-clustering grid; vendor motor models are ~300k triangles each
SKIP = ('bearing', 'Screw', 'washer', 'spirol', 'Nut', 'diaphragm')
BALL = ('Omni_ball_', 'shell_v2', 'roller_shell', 'roller_core')


def rpy_matrix(r, p, y):
    cr, sr, cp, sp, cy, sy = (math.cos(r), math.sin(r), math.cos(p), math.sin(p),
                              math.cos(y), math.sin(y))
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def rot_z(a):
    return rpy_matrix(0.0, 0.0, a)


def read_gltf(path):
    """Return (vertices Nx3, triangles Mx3). Onshape puts all geometry at the root node."""
    g = json.load(open(path))
    bufs = [base64.b64decode(b['uri'].split(',', 1)[1]) if b['uri'].startswith('data:')
            else open(os.path.join(os.path.dirname(path), b['uri']), 'rb').read()
            for b in g['buffers']]

    def accessor(i, ncomp, dtype):
        acc = g['accessors'][i]
        bv = g['bufferViews'][acc['bufferView']]
        item = np.dtype(dtype).itemsize * ncomp
        stride = bv.get('byteStride', item)
        raw = np.frombuffer(bufs[bv['buffer']], np.uint8, stride * (acc['count'] - 1) + item,
                            bv.get('byteOffset', 0) + acc.get('byteOffset', 0))
        rows = np.lib.stride_tricks.as_strided(raw, (acc['count'], item), (stride, 1))
        return rows.copy().view(dtype).reshape(acc['count'], ncomp)

    verts, tris = [], []
    for mesh in g['meshes']:
        for prim in mesh['primitives']:
            assert prim.get('mode', 4) == 4, 'only triangle lists supported'
            v = accessor(prim['attributes']['POSITION'], 3, np.float32)
            idx_type = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32}[
                g['accessors'][prim['indices']]['componentType']]
            t = accessor(prim['indices'], 1, idx_type).reshape(-1, 3).astype(np.int64)
            tris.append(t + sum(len(x) for x in verts))
            verts.append(v.astype(float))
    return np.vstack(verts), np.vstack(tris)


def decimate(v, t, cell=CELL):
    """Vertex clustering: snap vertices to a grid, drop collapsed triangles."""
    _, inv = np.unique(np.round(v / cell).astype(np.int64), axis=0, return_inverse=True)
    inv = inv.ravel()
    nv = np.zeros((inv.max() + 1, 3))
    np.add.at(nv, inv, v)
    nv /= np.bincount(inv)[:, None]
    nt = inv[t]
    keep = (nt[:, 0] != nt[:, 1]) & (nt[:, 1] != nt[:, 2]) & (nt[:, 0] != nt[:, 2])
    return nv, nt[keep]


def write_stl(path, parts):
    tri = np.vstack([v[t] for v, t in parts]).astype(np.float32)
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(tri), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'], rec['v'] = normals, tri
    with open(path, 'wb') as f:
        f.write(b'semubot v2'.ljust(80, b' ') + struct.pack('<I', len(tri)) + rec.tobytes())
    return len(tri)


def main(urdf, out_dir):
    mesh_dir = os.path.join(os.path.dirname(urdf), '..', 'meshes')
    parts = []  # (name, vertices in CAD frame, triangles)
    for vis in ET.parse(urdf).getroot().iter('visual'):
        name = vis.find('geometry/mesh').get('filename').split('/')[-1]
        if any(s in name for s in SKIP):
            continue
        o = vis.find('origin')
        v, t = read_gltf(os.path.join(mesh_dir, name))
        R = rpy_matrix(*map(float, o.get('rpy').split()))
        v = v @ R.T + np.array(list(map(float, o.get('xyz').split())))
        parts.append((name, v, t))  # full detail here: geometry below is measured from it

    # Ball centres and drive axles from the ball cores (smallest-variance axis = axle)
    cores = [v for n, v, _ in parts if n.startswith('Omni_ball_core')]
    assert len(cores) == 3, 'expected three Omni_ball_core parts'
    centres = np.array([c.mean(0) for c in cores])
    axles = [np.linalg.eigh(np.cov((c - c.mean(0)).T))[1][:, 0] for c in cores]
    floor_z = min(v[:, 2].min() for n, v, _ in parts if n.startswith(BALL))
    ball_radius = centres[0, 2] - floor_z

    # Forward = bisector of the two wheels the battery is between
    battery = next(v for n, v, _ in parts if n.startswith('Battery')).mean(0)
    ang = np.arctan2(centres[:, 1], centres[:, 0])
    rear = int(np.argmax(np.cos(ang - math.atan2(battery[1], battery[0]) - math.pi)))
    front = [i for i in range(3) if i != rear]
    fwd = math.atan2(*np.sin(ang[front]).sum(keepdims=True), *np.cos(ang[front]).sum(keepdims=True))
    yaw = -fwd  # CAD -> base_link rotation

    def to_base(p):
        return (p - [0, 0, floor_z]) @ rot_z(yaw).T

    os.makedirs(out_dir, exist_ok=True)
    frame, balls = [], [[] for _ in centres]
    for name, v, t in parts:
        if not name.startswith(BALL):
            frame.append(decimate(to_base(v), t))
            continue
        d = np.linalg.norm(centres - v.mean(0), axis=1)
        i = int(np.argmin(d))
        if d[i] > ball_radius:
            print(f'WARNING: {name} is {d[i]:.3f} m from the nearest ball centre, '
                  'misplaced in the CAD? skipped')
            continue
        balls[i].append((v, t))
    # One ball is enough: take a complete one, move it to the origin, axle -> x
    i = max(range(3), key=lambda k: len(balls[k]))
    a = math.atan2(axles[i][1], axles[i][0])
    ball = [decimate((v - centres[i]) @ rot_z(-a).T, t) for v, t in balls[i]]
    print('base_frame.stl triangles:', write_stl(os.path.join(out_dir, 'base_frame.stl'), frame))
    print('omni_ball.stl  triangles:', write_stl(os.path.join(out_dir, 'omni_ball.stl'), ball))

    print(f'\nball radius / centre height: {ball_radius:.4f} m')
    order = sorted(front, key=lambda i: -math.sin(ang[i] + yaw)) + [rear]  # left, right, rear
    for n, i in enumerate(order, 1):
        c = to_base(centres[i])
        a = math.atan2(axles[i][1], axles[i][0]) + yaw
        print(f'omni_ball_{n}: xyz=({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}) '
              f'angle={math.degrees(math.atan2(c[1], c[0])):.2f} deg '
              f'axle_yaw={math.degrees(a) % 180:.2f} deg')


if __name__ == '__main__':
    main(*sys.argv[1:3])
