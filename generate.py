#!/usr/bin/env python3
"""Export a witness in the labels used by the manuscript and certificates."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def witness(name, extended=False):
    records = json.loads((ROOT / "finite/certificates/disc_hypotheses.json").read_text(encoding="utf-8"))
    record = next(row for row in records if row["graph"] == name)
    code = record["graph6"]
    n = ord(code[0]) - 63
    bits = [int(bool((ord(c) - 63) & (1 << b))) for c in code[1:] for b in range(5, -1, -1)]
    edges = [(u, v) for bit, (u, v) in zip(bits, ((u, v) for v in range(1, n) for u in range(v))) if bit]
    extension = {"G14a": (0, 1), "G14b": (0, 3), "G14c": (2, 3), "D15": (9, 12)}
    if extended:
        if name not in extension:
            raise ValueError("--extension applies to G14a, G14b, G14c and D15")
        if extension[name] in edges:
            raise ValueError("The certifying edge is already present")
        edges.append(extension[name])
    edges.sort()
    return n, edges


def graph6(n, edges):
    present = set(edges)
    bits = [int((u, v) in present) for v in range(1, n) for u in range(v)]
    bits.extend([0] * ((-len(bits)) % 6))
    return chr(n + 63) + "".join(chr(63 + sum(bits[i + j] << (5 - j) for j in range(6))) for i in range(0, len(bits), 6))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True, choices=["G13", "G14a", "G14b", "G14c", "D15"])
    parser.add_argument("--extension", action="store_true", help="add the certifying edge to a contractible witness")
    parser.add_argument("--format", choices=["graph6", "json", "edges"], default="graph6")
    args = parser.parse_args()
    try:
        n, edges = witness(args.graph, args.extension)
    except ValueError as error:
        parser.error(str(error))
    if args.format == "graph6":
        print(graph6(n, edges))
    elif args.format == "edges":
        print("u\tv")
        for u, v in edges:
            print(str(u) + "\t" + str(v))
    else:
        print(json.dumps({"name": args.graph, "extension": args.extension, "n": n,
                          "m": len(edges), "vertices": list(range(n)), "edges": edges,
                          "graph6": graph6(n, edges)}, indent=2))


if __name__ == "__main__":
    main()
