#!/usr/bin/env python3
# checks the graph data from scratch: geometry, K4-freeness, colorings,
# cnf encoding and the deletion witnesses. usage: python3 verify.py <dir>
import json, sys, itertools
from collections import defaultdict

cert = sys.argv[1].rstrip('/')

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

# coordinates
pts = {}
with open(cert + "/coordinates_integer120.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"): continue
        t = list(map(int, line.split()))
        if len(t) != 7: fail("bad coord row: " + line)
        vid, rest = t[0], tuple(t[1:])
        if vid in pts: fail(f"duplicate id {vid}")
        pts[vid] = rest
n = len(pts)
if n != 108: fail(f"expected 108 vertices, got {n}")
if sorted(pts) != list(range(108)): fail("vertex ids not 0..107")
if len(set(pts.values())) != 108: fail("coordinate tuples not distinct")

# unit distances, exact
edges_geom = set()
for u, v in itertools.combinations(range(108), 2):
    a, b = pts[u], pts[v]
    P = 0; Q = 0
    for k in range(3):
        dA = a[2*k] - b[2*k]; dB = a[2*k+1] - b[2*k+1]
        P += dA*dA + 5*dB*dB
        Q += 2*dA*dB
    if Q == 0 and P == 14400:
        edges_geom.add((u, v))

edges_file = set()
with open(cert + "/edges_zero_based.txt") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        u, v = map(int, line.split())
        if u == v: fail("self loop")
        edges_file.add((min(u, v), max(u, v)))
if len(edges_file) != 590: fail(f"edge file has {len(edges_file)} edges")
if edges_file != edges_geom:
    fail(f"edge list mismatch: file-only={len(edges_file-edges_geom)}, geom-only={len(edges_geom-edges_file)}")
print(f"OK geometry: 108 distinct points, exactly {len(edges_geom)} unit pairs, edge list matches")

adj = defaultdict(set)
for u, v in edges_file:
    adj[u].add(v); adj[v].add(u)

# triangles and K4
tris = []
for u, v in sorted(edges_file):
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tris.append((u, v, w))
nk4 = 0
for u, v in sorted(edges_file):
    common = sorted(adj[u] & adj[v])
    for w, x in itertools.combinations(common, 2):
        if x in adj[w]:
            nk4 += 1
if nk4: fail(f"found {nk4} K4 witnesses")
print(f"OK clique structure: {len(tris)} triangles, zero K4")

# six coloring
with open(cert + "/six_coloring.txt") as f:
    col6 = list(map(int, f.read().split()))
if len(col6) != 108: fail("six coloring wrong length")
if not all(0 <= c <= 5 for c in col6): fail("six coloring colors out of range")
mono = [(u, v) for u, v in edges_file if col6[u] == col6[v]]
if mono: fail(f"six coloring improper on {len(mono)} edges")
print(f"OK six-coloring: proper, uses {len(set(col6))} colors")

# cnf soundness
clauses = []
nvars = None
with open(cert + "/proof/five.cnf") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("c"): continue
        if line.startswith("p"):
            parts = line.split()
            nvars = int(parts[2])
            continue
        lits = list(map(int, line.split()))
        if lits[-1] != 0: fail("clause missing terminator")
        clauses.append(tuple(lits[:-1]))
if nvars != 540: fail(f"expected 540 vars, got {nvars}")

def vc(lit):
    a = abs(lit) - 1
    return a // 5, a % 5  # vertex, color

alo = set(); units = []
n_amo = 0; n_edge = 0
edge_color_seen = set()
for cl in clauses:
    if len(cl) == 5 and all(l > 0 for l in cl):
        vs = {vc(l)[0] for l in cl}
        cs = {vc(l)[1] for l in cl}
        if len(vs) != 1 or cs != set(range(5)): fail(f"bad ALO clause {cl}")
        alo.add(vs.pop())
    elif len(cl) == 2 and all(l < 0 for l in cl):
        (u, cu), (v, cvv) = vc(cl[0]), vc(cl[1])
        if u == v and cu != cvv:
            n_amo += 1
        elif cu == cvv and (min(u, v), max(u, v)) in edges_file:
            n_edge += 1
            edge_color_seen.add((min(u, v), max(u, v), cu))
        else:
            fail(f"unsound binary clause {cl}: vertices {u},{v} colors {cu},{cvv}")
    elif len(cl) == 1:
        units.append(vc(cl[0]) if cl[0] > 0 else fail(f"negative unit {cl}"))
    else:
        fail(f"unexpected clause shape {cl}")
if alo != set(range(108)): fail("ALO clauses missing for some vertex")
# symmetry units must sit on a real triangle
if units:
    uverts = [u for u, c in units]; ucols = [c for u, c in units]
    if len(units) != 3 or len(set(uverts)) != 3 or len(set(ucols)) != 3:
        fail(f"unexpected unit clauses {units}")
    a, b_, c_ = sorted(uverts)
    if not ((a, b_) in edges_file and (a, c_) in edges_file and (b_, c_) in edges_file):
        fail("symmetry-breaking units are not on a triangle")
print(f"OK CNF: {len(clauses)} clauses all whitelisted "
      f"(ALO 108, AMO {n_amo}, edge {n_edge} covering {len({(u,v) for u,v,_ in edge_color_seen})} edges, "
      f"units {len(units)} on a genuine triangle with distinct colors)")

# deletion witnesses
with open(cert + "/vertex_deletion_witnesses.json") as f:
    wit = json.load(f)["witnesses"]
keys = {w["deleted_vertex"] for w in wit}
if keys != set(range(108)): fail(f"witnesses cover {len(keys)} vertices, not all 108")
for w in wit:
    k = w["deleted_vertex"]
    cm = w["five_coloring"]
    if len(cm) != 108: fail(f"witness for {k} wrong length")
    used = {cm[i] for i in range(108) if i != k}
    if not used <= set(range(5)): fail(f"witness for {k} uses colors {sorted(used)}")
    for u, v in edges_file:
        if u == k or v == k: continue
        if cm[u] == cm[v]:
            fail(f"witness for {k} improper on edge ({u},{v})")
print("OK vertex-criticality: all 108 single-deletion 5-colorings are proper")
print("ALL STRUCTURAL CHECKS PASSED")
