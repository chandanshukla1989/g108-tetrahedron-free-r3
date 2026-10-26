#!/usr/bin/env python3
# forward RUP check of a DRUP proof. deletions are ignored, which only
# strengthens propagation. usage: python3 rupcheck.py cnf proof
import sys

def parse_dimacs(path):
    clauses = []
    nvars = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in "c%":
                continue
            if line[0] == "p":
                nvars = int(line.split()[2]); continue
            lits = list(map(int, line.split()))
            assert lits[-1] == 0
            clauses.append(lits[:-1])
    return nvars, clauses

def main():
    cnf_path, drup_path = sys.argv[1], sys.argv[2]
    nvars, clauses = parse_dimacs(cnf_path)

    val = [0] * (nvars + 1)
    trail = []

    def lit_val(l):
        v = val[abs(l)]
        return v if l > 0 else -v

    watches = {}  # lit -> list of clauses (lists) watching it
    def watch(l, cl):
        watches.setdefault(l, []).append(cl)

    units0 = []
    db = []
    def add_clause(cl):
        if len(cl) == 1:
            units0.append(cl[0]); return
        watch(cl[0], cl); watch(cl[1], cl)
        db.append(cl)

    for cl in clauses:
        add_clause(cl)

    def enqueue(l):
        v = abs(l)
        cur = val[v]
        want = 1 if l > 0 else -1
        if cur == want:
            return True
        if cur == -want:
            return False  # conflict
        val[v] = want
        trail.append(v)
        return None  # newly assigned

    def propagate(queue):
        qi = 0
        while qi < len(queue):
            l = queue[qi]; qi += 1
            falsified = -l
            wl = watches.get(falsified)
            if not wl:
                continue
            new_wl = []
            for cl in wl:
                # make sure cl[1] is the falsified watch
                if cl[0] == falsified:
                    cl[0], cl[1] = cl[1], cl[0]
                # cl[1] == falsified
                if lit_val(cl[0]) == 1:
                    new_wl.append(cl); continue
                found = False
                for i in range(2, len(cl)):
                    if lit_val(cl[i]) != -1:
                        cl[1], cl[i] = cl[i], cl[1]
                        watch(cl[1], cl)
                        found = True
                        break
                if found:
                    continue
                new_wl.append(cl)
                r = enqueue(cl[0])
                if r is False:
                    idx = wl.index(cl)
                    watches[falsified] = new_wl + wl[idx+1:]
                    return False
                if r is None:
                    queue.append(cl[0])
            watches[falsified] = new_wl
        return True

    q = []
    for l in units0:
        r = enqueue(l)
        if r is False:
            print("ORIGINAL CNF propagates to conflict at top level"); return
        if r is None:
            q.append(l)
    if not propagate(q):
        print("ORIGINAL CNF propagates to conflict at top level"); return
    top = len(trail)

    def undo(to):
        while len(trail) > to:
            val[trail.pop()] = 0

    nadd = 0
    empty_ok = False
    with open(drup_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("d "):
                continue  # deletions ignored (sound)
            lits = list(map(int, line.split()))
            assert lits[-1] == 0
            lits = lits[:-1]
            nadd += 1
            if not lits:
                print(f"FAIL: empty clause not derivable by unit propagation (lemma {nadd})")
                return
            save = len(trail)
            q = []
            conflict = False
            for l in lits:
                r = enqueue(-l)
                if r is False:
                    conflict = True; break
                if r is None:
                    q.append(-l)
            if not conflict:
                conflict = not propagate(q)
            undo(save)
            if not conflict:
                print(f"FAIL: lemma {nadd} is not RUP: {lits}")
                return
            if len(lits) == 1:
                r = enqueue(lits[0])
                if r is False:
                    empty_ok = True
                    break
                if r is None:
                    if not propagate([lits[0]]):
                        empty_ok = True
                        break
                top = len(trail)
            else:
                lits.sort(key=lambda l: 0 if lit_val(l) != -1 else 1)
                watch(lits[0], lits); watch(lits[1], lits)
                db.append(lits)
    if not empty_ok:
        print(f"checked {nadd} lemmas; no top-level conflict reached — FAIL")
        return
    print(f"VERIFIED: UNSAT confirmed after {nadd} lemmas (forward RUP, deletions ignored)")

main()
