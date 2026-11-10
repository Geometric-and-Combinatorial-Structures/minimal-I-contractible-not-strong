#!/usr/bin/env python3
"""Generate the supplement's mathematical tables from the deposited records."""
from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / "finite/data" / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def line(values):
    return " & ".join(map(str, values)) + r" \\" + "\n"


def longtable(spec, caption, label, headings, body):
    return (r"\begingroup\small" + "\n" +
            r"\setlength{\tabcolsep}{3pt}" + "\n" +
            r"\begin{longtable}{" + spec + "}\n" +
            r"\caption{" + caption + r"}\label{" + label + r"}\\" + "\n" +
            r"\toprule" + "\n" + line(headings) + r"\midrule\endfirsthead" + "\n" +
            r"\toprule" + "\n" + line(headings) + r"\midrule\endhead" + "\n" +
            r"\midrule\multicolumn{" + str(len(headings)) + r"}{r}{Continued on the next page}\\" + "\n" +
            r"\endfoot\bottomrule\endlastfoot" + "\n" + "".join(line(row) for row in body) +
            r"\end{longtable}\endgroup" + "\n")


def contents():
    seeds = []
    seed_rows = rows("stuck_14_K4free.tsv")
    assert len(seed_rows) == 51
    assert [r["unfolding"] for r in seed_rows] == ["annulus" if i in (48, 49) else "annulus + disc" if i == 51 else "disc" for i in range(1,52)]
    for i, row in enumerate(seed_rows, 1):
        seeds.append([i, r"\verb+" + row["graph6"] + "+", row["edges"], row["triangles"],
                      row["automorphism_order"], {"trivial": "$0$", "Z/3": r"$\ZZ/3$"}[row["H1_Z"]],
                      row["boundary_component_lengths"].replace("+", ",")])
    strict = []
    for i, row in enumerate(rows("strictly_2dis_12.tsv"), 1):
        strict.append([i, r"\verb+" + row["graph6"] + "+", row["edges"], row["triangles"],
                       row["K4_count"], row["clique_number"],
                       row["minimum_degree"], row["maximum_degree"], row["automorphism_order"]])
    record = json.loads((ROOT / "finite/certificates/certificate_replay.json").read_text())[-1]
    disc = json.loads((ROOT / "finite/certificates/disc_hypotheses.json").read_text())
    assert record["g6"] == next(row["graph6"] for row in disc if row["graph"] == "D15")
    assert record["added_edge"] == [9, 12]
    steps = []
    for step in record["steps"]:
        element = [step["element"]] if step["kind"] == "vertex" else step["element"]
        operation = ("v" if step["kind"] == "vertex" else "e") + r"_{\{" + ",".join(map(str, element)) + r"\}}"
        link = ",".join(map(str, step["link_vertices"]))
        sequence = ",".join(str(op[1]) for op in step["link_certificate"])
        survivor = set(step["link_vertices"]) - {op[1] for op in step["link_certificate"]}
        if len(survivor) != 1:
            raise ValueError("Link reduction must have one survivor")
        steps.append([step["step"], "$" + operation + "$", r"$\{" + link + r"\}$",
                      "$" + sequence + r"\ ;\ [" + str(next(iter(survivor))) + "]$"])
    return {
        "seeds.tex": longtable("rlrrrrl",
            r"The 51 stuck $K_4$-free seeds of order 14. Here $m$ counts edges, "
            r"$t$ triangles, and $a=|\operatorname{Aut}(G)|$. The final column gives "
            r"all boundary lengths of the natural unfolding. Rows 48 and 49 are annuli; "
            r"row 51 is a disc together with an annulus; the other rows are discs.",
            "tab:seeds", ["No.", "Encoding", "$m$", "$t$", "$a$", "$H_1$", "Boundary"], seeds),
        "strict12.tex": longtable("rlrrrrrrr",
            r"The 20 graphs of order 12 in $2$-Dis outside $1$-Dis. The columns give "
            r"edges $m$, triangles $t$, four-cliques $q$, clique number $\omega$, "
            r"degrees $\delta,\Delta$, and automorphism-group order $a$.",
            "tab:strict", ["No.", "Encoding", "$m$", "$t$", "$q$", r"$\omega$", r"$\delta$", r"$\Delta$", "$a$"], strict),
        "d15.tex": longtable("rlll",
            r"A strong reduction of $\Dunce+\{9,12\}$. The symbols $v$ and $e$ "
            r"indicate vertex and edge deletions. The last column lists vertex "
            r"deletions in the tested neighbourhood, followed by its surviving vertex "
            r"in brackets. The main reduction ends at vertex $" + str(record["last_vertex"]) + "$.",
            "tab:d15", ["Step", "Delete", "Current neighbourhood", "Link reduction"], steps)
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare without modifying files")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "supplement/tables")
    args = parser.parse_args()
    generated = contents()
    if args.check:
        for name, text in generated.items():
            if (args.output_dir / name).read_text(encoding="utf-8") != text:
                parser.exit(1, "Supplement table differs: " + name + "\n")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, text in generated.items():
            (args.output_dir / name).write_text(text, encoding="utf-8")
    print(json.dumps({"tables": len(generated), "checked": args.check}))


if not __debug__:
    raise RuntimeError("Run without -O")
if __name__ == "__main__":
    main()
