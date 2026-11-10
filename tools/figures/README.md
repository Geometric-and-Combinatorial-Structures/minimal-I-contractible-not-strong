# Witness figures and printed finite data

`witness_data.json` freezes the exact graph edges, reduction data, coordinate
maps and source digests from the previous delivery. The graph encodings are
retained here only as provenance and as an independent comparison input.

From this directory, run:

```sh
python3 make_witness_figures.py --check
python3 make_witness_tables.py --check
python3 verify_witnesses.py
```

The first two commands require only Python's standard library. The verifier
requires NetworkX and SymPy. It computes homology via a spanning-tree cycle
basis, replays all reductions, and checks the disc by successive triangle
attachments. It does not repeat any graph census.

The generators write three figure sources and four mathematical tables under
`build/generated-paper/`, then compare them byte for byte with the frozen article
when `--check` is supplied. Local check results go under
`build/verification/witnesses/`. Compile the manuscript without resizing
the TikZ panels. They have 8pt mathematical labels and minimum node diameter
5.8mm. The drawing styles are the author's `jfef-mis-grafos` styles, loaded
in the manuscript preamble; Euler in the surrounding text is not changed.

The three scientific panels contain respectively 48,40 and45 edges. The
last count includes the dashed edge added to the44-edge graph Ga. The
generator checks each emitted edge set, not only its cardinality.

The optional verification environment is pinned in `requirements.txt` and was tested with Python 3.13. Install it in an isolated environment before running the verifier. The figure CI job regenerates the drawings and tables, checks the witnesses, and requires the distributed source hashes to remain unchanged.
