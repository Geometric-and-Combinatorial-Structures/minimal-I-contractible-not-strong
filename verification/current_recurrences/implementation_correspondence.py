#!/usr/bin/env python3
"""Bounded correspondence check: actual C functions vs independent recurrences.

The source is included without edits, with only its executable main renamed.
All labelled graphs of orders 0..5 and all induced masks are compared. This
is a finite regression check, not a proof of the general program or a census.
"""
from pathlib import Path
from functools import lru_cache
from itertools import combinations
import argparse
import hashlib
import json
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "v2/src/atascadas_v2.c"



def restrict(graph, vertices):
    vs = tuple(vertices)
    return tuple(sum(1 << j for j, v in enumerate(vs) if graph[u] >> v & 1) for u in vs)


def remove_edge(graph, u, v):
    out = list(graph)
    out[u] ^= 1 << v
    out[v] ^= 1 << u
    return tuple(out)


def neighbours(graph, v):
    return tuple(u for u in range(len(graph)) if graph[v] >> u & 1)


@lru_cache(None)
def strong(graph):
    if not graph:
        return False
    if len(graph) == 1:
        return True
    for v in range(len(graph)):
        if strong(restrict(graph, neighbours(graph, v))) and strong(restrict(graph, (u for u in range(len(graph)) if u != v))):
            return True
    for u, v in combinations(range(len(graph)), 2):
        if graph[u] >> v & 1:
            common = (w for w in range(len(graph)) if (graph[u] & graph[v]) >> w & 1)
            if strong(restrict(graph, common)) and strong(remove_edge(graph, u, v)):
                return True
    return False


@lru_cache(None)
def vertex_strong(graph):
    if not graph:
        return False
    if len(graph) == 1:
        return True
    return any(vertex_strong(restrict(graph, neighbours(graph, v))) and
               vertex_strong(restrict(graph, (u for u in range(len(graph)) if u != v)))
               for v in range(len(graph)))


def cone(graph):
    return bool(graph) and any(row.bit_count() == len(graph) - 1 for row in graph)


@lru_cache(None)
def dismantlable(graph, level):
    if level == -1:
        return cone(graph)
    if not graph:
        return False
    if len(graph) == 1:
        return True
    return any(dismantlable(restrict(graph, neighbours(graph, v)), level - 1) and
               dismantlable(restrict(graph, (u for u in range(len(graph)) if u != v)), level)
               for v in range(len(graph)))


@lru_cache(None)
def topology(graph):
    if not graph:
        return False, 0, False
    faces = [list(vs for vs in combinations(range(len(graph)), size)
                  if all(graph[u] >> v & 1 for u, v in combinations(vs, 2)))
             for size in range(1, len(graph) + 1)]
    ranks = [1]
    for dimension in range(1, len(faces)):
        row_index = {face: i for i, face in enumerate(faces[dimension - 1])}
        pivots = {}
        for face in faces[dimension]:
            column = sum(1 << row_index[face[:j] + face[j + 1:]] for j in range(len(face)))
            while column:
                pivot = column.bit_length() - 1
                if pivot in pivots:
                    column ^= pivots[pivot]
                else:
                    pivots[pivot] = column
                    break
        ranks.append(len(pivots))
    ranks.append(0)
    betti = [len(faces[d]) - ranks[d] - ranks[d + 1] for d in range(len(faces))]
    return not any(betti), sum((-1)**d * len(fs) for d, fs in enumerate(faces)), betti[0] == 0


def check(output_dir, compiler):
    started = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    harness = HERE / "implementation_correspondence.c"
    binary = output_dir / "implementation_correspondence.bin"
    compile_command = [compiler, "-O2", "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror", str(harness), "-o", str(binary)]
    compiled = subprocess.run(compile_command, capture_output=True, text=True, check=True)
    run = subprocess.run([str(binary)], capture_output=True, text=True, check=True, timeout=60)
    (output_dir / "implementation_correspondence.stdout").write_text(run.stdout)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
    counts = {n: {"labelled_graphs": 0, "masked_states": 0, "empty_masks": 0,
                  "singleton_masks": 0, "successful_vertex_first_choices": 0,
                  "successful_edge_first_choices": 0} for n in range(6)}
    mismatch = []
    seen = set()
    for line in run.stdout.splitlines():
        n, code, mask, *actual = map(int, line.split())
        assert (n, code, mask) not in seen
        seen.add((n, code, mask))
        graph = [0] * n
        pairs = [(u, v) for v in range(1, n) for u in range(v)]
        for bit, (u, v) in enumerate(pairs):
            if code >> bit & 1:
                graph[u] |= 1 << v
                graph[v] |= 1 << u
        vertices = tuple(v for v in range(n) if mask >> v & 1)
        sub = restrict(graph, vertices)
        acyclic, chi, connected = topology(sub)
        vfirst = sum(1 << v for v in vertices
                     if strong(restrict(graph, (u for u in vertices if graph[v] >> u & 1))) and
                     strong(restrict(graph, (u for u in vertices if u != v))))
        efirst = 0
        for bit, (u, v) in enumerate(pairs):
            if u in vertices and v in vertices and graph[u] >> v & 1:
                common = (w for w in vertices if (graph[u] & graph[v]) >> w & 1)
                if strong(restrict(graph, common)) and strong(restrict(remove_edge(graph, u, v), vertices)):
                    efirst |= 1 << bit
        expected = list(map(int, [strong(sub), vertex_strong(sub), cone(sub)] +
                            [dismantlable(sub, k) for k in range(4)] +
                            [acyclic, acyclic, chi, connected, vfirst, efirst]))
        if actual != expected:
            mismatch.append({"n": n, "edge_code": code, "mask": mask, "actual": actual, "expected": expected})
        c = counts[n]
        c["labelled_graphs"] += mask == 0
        c["masked_states"] += 1
        c["empty_masks"] += len(vertices) == 0
        c["singleton_masks"] += len(vertices) == 1
        c["successful_vertex_first_choices"] += vfirst.bit_count()
        c["successful_edge_first_choices"] += efirst.bit_count()
    for n, c in counts.items():
        assert c["labelled_graphs"] == 2**(n*(n-1)//2)
        assert c["masked_states"] == c["labelled_graphs"] * 2**n
    report = {"status": "FAIL" if mismatch else "PASS", "scope": "all labelled graphs n=0..5; all induced masks; all candidate first vertex and edge deletions",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": source_hash,
              "comparison_fields": ["IS", "ISV", "cone", "0Dis", "1Dis", "2Dis", "3Dis", "F2_acyclic_full", "F2_acyclic_prefilter", "Euler", "connected", "successful_vertex_first_mask", "successful_edge_first_mask"],
              "counts": counts, "mismatches": mismatch, "compile_command": compile_command,
              "compile_stderr": compiled.stderr, "run_stderr": run.stderr,
              "compile_exit": compiled.returncode, "run_exit": run.returncode,
              "seconds": time.monotonic() - started,
              "artifacts_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), harness, binary, output_dir / "implementation_correspondence.stdout")},
              "limitations": ["The executable parser rejects order zero; the empty mathematical state is checked by calling the original internal functions.", "No census above order five was run.", "This independent recurrence was written after inspecting the C and the manuscript; it is not a pre-registered clean-room implementation.", "Small graphs do not test the high-order separation IS versus ISV or k-levels; existing witness certificates cover those examples."]}
    (output_dir / "implementation_correspondence.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "labelled_graphs": sum(c["labelled_graphs"] for c in counts.values()), "masked_states": len(seen), "mismatches": len(mismatch), "seconds": report["seconds"]}, indent=2))
    assert not mismatch


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run without -O: this checker requires assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", default="cc", help="C compiler executable (default: cc)")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build/current_recurrences",
                        help="Directory for binary, raw output, and report")
    args = parser.parse_args()
    check(args.output_dir.resolve(), args.cc)
