#!/usr/bin/env python3
"""Check the finite scope and tables used by the mathematical supplement."""
from pathlib import Path
from collections import Counter
from itertools import combinations
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from finite_isomorphism import pairwise_nonisomorphic, unique_inclusions
sys.path.insert(0, str(ROOT / "finite/certificates"))
from finite_checks import decode, encode, edge, cliques


def rows(name):
    with (ROOT / "finite/data" / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    seeds = rows("stuck_14_K4free.tsv")
    strict = rows("strictly_2dis_12.tsv")
    all_closure = rows("acyclic_not_strong_14_closure.tsv")
    positive = rows("I_not_strong_14_closure.tsv")
    seed_strings = {r["graph6"] for r in seeds}
    assert len(seed_strings) == 51
    unique_inclusions(sorted(seed_strings), [r["graph6"] for r in all_closure])
    empty_paths = [r for r in all_closure if json.loads(r["added_edges"]) == []]
    assert len(empty_paths) == 51
    assert {r["graph6"] for r in empty_paths} == seed_strings
    assert all(r["graph6"] == r["seed_graph6"] for r in empty_paths)
    assert all(r["seed_graph6"] in seed_strings for r in all_closure)
    assert len((ROOT / "data/census/F4_positive.g6").read_text().splitlines()) == 8
    assert len((ROOT / "data/census/F4_residual.g6").read_text().splitlines()) == 625
    unfoldings = json.loads((ROOT / "finite/data/unfolding_components.json").read_text())
    assert len(unfoldings) == 51 and {r["row"] for r in unfoldings} == set(range(1,52))
    for record in unfoldings:
        for component in record["components"]:
            assert sorted(map(len, component["boundary_words"])) == sorted(component["boundary_lengths"])
        if record["row"] in (48,49):
            assert [(c["type"], sorted(c["boundary_lengths"])) for c in record["components"]] == [("annulus", [4,12])]
        if record["row"] == 51:
            assert sorted((c["type"], sorted(c["boundary_lengths"])) for c in record["components"]) == [("annulus", [8,12]), ("disc", [4])]
    report = {}
    for name, table in [("seeds", seeds), ("strict12", strict), ("closures51", all_closure)]:
        report[name] = pairwise_nonisomorphic([r["graph6"] for r in table])
    types = Counter((r["H1_Z"], r["unfolding"]) for r in seeds)
    assert types == {("trivial", "disc"): 3, ("Z/3", "disc"): 45,
                     ("Z/3", "annulus"): 2, ("Z/3", "annulus + disc"): 1}
    for row in seeds:
        graph = decode(row["graph6"])
        triangles = cliques(graph, 3)
        covered = {tuple(e) for t in triangles for e in combinations(t, 2)}
        assert covered == set(cliques(graph, 2))
        assert len(graph) - len(cliques(graph, 2)) + len(triangles) == 1
        assert not cliques(graph, 4)
    assert Counter(r["I_contractible"] for r in all_closure) == {"0": 2242, "1": 29}
    assert Counter(int(r["K4_count"]) == 0 for r in positive) == {True: 8, False: 21}
    restricted = [r["graph6"] for r in all_closure if r["K4_count"] == "0"]
    exceptional = ((ROOT / "data/census/F4_residual.g6").read_text().splitlines() +
                   (ROOT / "data/census/F4_positive.g6").read_text().splitlines())
    assert len(exceptional) == len(set(exceptional)) == 633
    report["exceptional_nonisomorphism"] = pairwise_nonisomorphic(exceptional)
    comparison = unique_inclusions(restricted, exceptional)
    missing = sorted(set(exceptional) - {r["target"] for r in comparison})
    assert len(restricted) == 277 and len(missing) == 356
    assert missing[0] == "M?B@`jIja{J}jy{]?"
    restricted_I = [r["graph6"] for r in all_closure if r["K4_count"] == "0" and r["I_contractible"] == "1"]
    restricted_torsion = [r["graph6"] for r in all_closure if r["K4_count"] == "0" and r["I_contractible"] == "0"]
    assert len(restricted_I) == 8 and len(restricted_torsion) == 269
    assert all(json.loads(r["H1_torsion"]) == ([3] if r["I_contractible"] == "0" else []) for r in all_closure)
    unique_inclusions(restricted_I, (ROOT / "data/census/F4_positive.g6").read_text().splitlines())
    unique_inclusions(restricted_torsion, (ROOT / "data/census/F4_residual.g6").read_text().splitlines())
    small = json.loads((ROOT / "finite/data/small_closure_certificates.json").read_text())["closures"]
    assert {name: sum(not state["strong"] and not cliques(decode(state["graph6"]), 4)
                      for state in record["states"]) for name, record in small.items()} == {"G14a": 4, "G14b": 3, "G14c": 1}
    sources = [s["graph6"] for record in small.values() for s in record["states"] if not s["strong"]]
    # Union: two isomorphic overlaps across seeds must not be counted twice.
    target = [r["graph6"] for r in positive]
    matched = {unique_inclusions([s], target)[0]["target"] for s in sources}
    assert matched == set(target)
    report["unfolding_types_by_H1"] = {" / ".join(k): v for k, v in sorted(types.items())}
    report["closure_partition"] = {"I": 29, "H1_Z3": 2242, "K4_free_I": 8}
    report["restricted_comparison"] = {"closure_classes": 277, "torsion": 269,
        "exceptional_classes": len(exceptional), "outside_closure": len(missing), "example_outside": missing[0]}
    streams = {"stuck_14_K4free.g6": [r["graph6"] for r in seeds],
               "strictly_2dis_12.g6": [r["graph6"] for r in strict],
               "acyclic_not_strong_13.g6": (ROOT / "data/census/F2_13_residual.g6").read_text().splitlines()}
    disc = json.loads((ROOT / "finite/certificates/disc_hypotheses.json").read_text())
    streams["dunce_hat_15.g6"] = [r["graph6"] for r in disc if r["graph"] == "D15"]
    streams["dunce_hat_15.g6"].append(encode(edge(decode(streams["dunce_hat_15.g6"][0]), 9, 12, True)))
    for name, catalog in streams.items():
        graphs = [line.split()[0] for line in (ROOT / "data" / name).read_text().splitlines()
                  if line.strip() and not line.startswith("#")]
        assert len(graphs) == len(catalog)
        matches = unique_inclusions(graphs, catalog)
        assert len({r["target"] for r in matches}) == len(catalog)
    report["labelled_regression_streams_matched"] = len(streams)
    published = json.loads((ROOT / "finite/data/D15_published_triangles.json").read_text())
    assert published["graph6"] == next(r["graph6"] for r in disc if r["graph"] == "D15")
    replay = json.loads((ROOT / "finite/certificates/certificate_replay.json").read_text())
    assert replay[-1]["g6"] == published["graph6"]
    labels = published["graph6_to_published"]
    assert labels == [1,4,13,12,11,3,14,15,10,5,2,6,7,8,9]
    assert sorted(labels) == list(range(1,16))
    graph = decode(published["graph6"])
    published_edges = {tuple(sorted(e)) for t in published["published_triangles"] for e in combinations(t,2)}
    assert {tuple(sorted(labels[v] for v in e)) for e in cliques(graph,2)} == published_edges
    assert {tuple(sorted(labels[v] for v in t)) for t in cliques(graph,3)} == {tuple(sorted(t)) for t in published["published_triangles"]}
    report["D15_published_edges_and_triangles"] = [len(published_edges), len(published["published_triangles"])]
    print(json.dumps(report, indent=2))


if not __debug__:
    raise RuntimeError("Run without -O; the checks require assertions")
if __name__ == "__main__":
    main()
