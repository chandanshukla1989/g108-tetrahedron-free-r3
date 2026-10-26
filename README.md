# A 108-vertex tetrahedron-free 6-chromatic unit-distance graph in R³

**Chandan Shukla, October 2026**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23653148.svg)](https://doi.org/10.5281/zenodo.23653148)

This repository contains a unit-distance graph in three-dimensional Euclidean
space with **108 vertices and 590 edges** that is **6-chromatic** (five colours
are impossible) and **tetrahedron-free** (it contains no K₄), together with
machine-checkable certificates for every claim. It is also **vertex-critical**:
deleting any single vertex leaves a 5-colourable graph.

All coordinates lie in Q(√5)³. Row `id Ax Bx Ay By Az Bz` in
`coordinates_integer120.txt` encodes the coordinate `(A + B·√5)/120` per axis.
`edges_zero_based.txt` lists every vertex pair at exact distance 1. The edge
list is complete, verified in exact rational arithmetic over all 5,778 pairs.

## Files

| File | Contents |
|---|---|
| `coordinates_integer120.txt` | exact coordinates (integer form, /120) |
| `edges_zero_based.txt` | all 590 unit-distance edges |
| `six_coloring.txt` | an explicit proper 6-colouring |
| `graph_exact.json` | the same data in JSON |
| `proof/five.cnf` | 5-colourability CNF (standard encoding + one symmetry-breaking triangle) |
| `proof/five.drup` | UNSAT proof (DRUP) |
| `vertex_deletion_witnesses.json` | a proper 5-colouring of G−v for every vertex v |
| `verify.py` | standalone structural verifier (python3, stdlib only) |
| `rupcheck.py` | standalone forward-RUP proof checker (python3, stdlib only) |
| `external_checker/drat-trim.c` | third-party DRAT checker (Heule et al., see LICENSE) |

## Verify everything

```bash
# geometry, K4-freeness, 6-colouring, CNF soundness, criticality witnesses
python3 verify.py .

# replay the 5-colour UNSAT proof (pure python)
python3 rupcheck.py proof/five.cnf proof/five.drup

# or with the external checker
gcc -O2 external_checker/drat-trim.c -o drat-trim
./drat-trim proof/five.cnf proof/five.drup -t 180   # expect: s VERIFIED
```

## Context

This continues the line of work on small 6-chromatic unit-distance graphs in
R³ started by A. de Grey and A. Haugstrup, "Two small 6-chromatic
unit-distance graphs in R³", Geombinatorics XXXI(3), 2022
(https://geombina.uccs.edu/past-issues/volume-xxxi). Those graphs, like the
other small constructions in this family, contain unit tetrahedra. The
previously described tetrahedron-free 6-chromatic construction, due to
Haugstrup, has 21,217 vertices (described Dec 2025,
https://dustingmixon.wordpress.com/2021/02/01/polymath16-seventeenth-thread-declaring-victory/).
The present graph extends that work with a tetrahedron-free example on 108
vertices. Global minimality is not claimed.

## License

Data and scripts: CC BY 4.0. `external_checker/` retains its own license.
