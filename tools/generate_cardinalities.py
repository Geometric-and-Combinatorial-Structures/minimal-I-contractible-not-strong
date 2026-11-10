#!/usr/bin/env python3
"""Render the two mathematical table panels from the selected CSV.

This formats retained and mathematically adjudicated results; it does not
repeat the census. Run from any working directory. Inputs are explicit and
the output can be placed in a disposable build directory for comparison.
"""
from pathlib import Path
import argparse
import csv


def render(csv_path):
    fields = ["connected", "chi1", "acyclic_F2", "acyclic_Z", "I", "I_S",
              "I_SV", "3_Dis", "2_Dis", "1_Dis", "0_Dis", "cones"]
    with csv_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if [int(row["n"]) for row in rows] != list(range(3, 15)):
        raise ValueError("Expected each order 3 through 14 exactly once, in order")
    for row in rows:
        expected_universe = "connected_K4_free" if int(row["n"]) == 14 else "connected"
        if row["universe"] != expected_universe:
            raise ValueError(f"Unexpected universe at order {row['n']}")
        for field in fields:
            if int(row[field]) < 0:
                raise ValueError("Cardinalities must be nonnegative integers")
    panels = [
        (fields[:6], r"$n$ & connected & $\chi=1$ & $\mathcal A_{\mathbb F_2}$ & $\mathcal A_{\ZZ}$ & $\I$ & $\IS$"),
        (fields[6:], r"$n$ & $\ISV$ & $3$-Dis & $2$-Dis & $1$-Dis & $0$-Dis & $(-1)$-Dis"),
    ]
    head = r"""% Thirteen logical columns, including n; twelve counts in two panels.
\begingroup
\footnotesize
\setlength{\tabcolsep}{2pt}
\sisetup{group-separator={,}}
\renewcommand{\arraystretch}{1.12}
"""
    output = []
    for columns, header in panels:
        lines = [r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}rrrrrrr@{}}",
                 r"\toprule", header + r" \\", r"\midrule"]
        for row in rows:
            n = int(row["n"])
            label = str(n) + (r"$^{\dagger}$" if n == 14 else "")
            cells = [r"\num{" + str(int(row[field])) + "}" for field in columns]
            lines.append(label + " & " + " & ".join(cells) + r" \\")
        lines += [r"\bottomrule", r"\end{tabular*}"]
        output.append("\n".join(lines))
    return head + "\n\\par\\medskip\n".join(output) + "\n\\endgroup\n"


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path,
                        default=root / "data/cardinalities.csv")
    parser.add_argument("--output", type=Path,
                        default=root / "paper/tables/cardinalities.tex")
    parser.add_argument("--check", action="store_true",
                        help="Compare with the existing output without writing")
    args = parser.parse_args()
    content = render(args.csv)
    if args.check:
        if args.output.read_text(encoding="utf-8") != content:
            raise SystemExit("Table differs from CSV rendering")
        print("PASS: table exactly matches CSV rendering")
    else:
        args.output.write_text(content, encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
