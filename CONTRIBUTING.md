# Maintaining the mathematical companion

A change to a result should identify its mathematical statement, hypotheses, proof or enumeration, and corresponding data. Preserve graph labels across the article, certificates, figures and notebook. Auxiliary results belong with their proofs in the supplement.

## Source records

[`docs/provenance/article-r01.json`](docs/provenance/article-r01.json) identifies the article's source inputs and PDF. If those inputs are replaced, update the identity record and the checks that refer to it. [`selection-migration.json`](docs/provenance/selection-migration.json) records the relation to imported files; [`migration-inventory.tsv`](docs/provenance/migration-inventory.tsv) records the earlier repository tree. Maintain these correspondences when editing an imported file.

After reviewing a change, regenerate the affected tables or figures, update the inventories and run:

```bash
python3 tools/integrity.py --write
python3 reproduce.py --extended --cc gcc
```

Files under `finite/data/`, `finite/certificates/` and `finite/provenance/`, together with the TSV dictionaries under `finite/figures/`, also belong to `finite/integrity_manifest.json`; changes there require updating that manifest and `finite/integrity_manifest.sha256`. The file inventories record the selected bytes. Mathematical checks and proofs establish the properties of the represented objects.

For a new count, retain the input universe, generation and classification procedures, complete execution record and exceptional graphs. Resolve every residual by a positive certificate or a mathematical obstruction: failure of a bounded certificate search leaves membership undecided.

Compile documents in temporary copies as described in [the document guide](ARTICLE.md#build-the-documents), examine the logs and inspect the pages. For graph drawings, keep edges separate from coordinates, compare the emitted edge set with the graph data and retain the mathematical label style.

## Checks and output directories

`reproduce.py` runs the eleven finite checks, followed by the repository, table, interface, certificate and notebook checks. Its `--timeout` is applied to each finite stage; the finite driver receives twelve times that limit overall. Each other required stage receives one limit, and interface subprocesses inherit it. On POSIX systems, timeout handling terminates the process group and retains its output.

Generated outputs inside the repository belong under root `results/` or `build/`. The inventory also excludes root Git metadata, `.venv/`, Python bytecode, notebook checkpoints, LaTeX intermediates, `.DS_Store`, `v2/build/`, `v2/tests/results/`, `src/atascadas` and `quick-verification.json`. Identically named directories nested inside the data remain part of the input inventory.

For interactive work, use the notebook copy created by `python3 tools/copy_notebook.py`; the distributed notebook remains an input. The [regression guide](v2/README.md#regression-suite) describes the classifier and partition-driver tests. Complete enumerations follow [full reproduction](docs/full-reproduction.md).
