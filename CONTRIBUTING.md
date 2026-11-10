# Updating the companion

Keep graph labels, mathematical scope and provenance explicit. The article's r01 source inputs and PDF are fixed by `docs/provenance/article-r01.json`; a later article version should have its own identity record. Auxiliary results belong in the supplement with a proof and a corresponding finite check.

After an intentional source change, review the diff and regenerate only the affected derived tables or figures. Record changes to imported files in `docs/provenance/selection-migration.json`. Then update the byte inventory and run the required checks:

```bash
python3 tools/integrity.py --write
python3 reproduce.py --extended --cc gcc
```

Rebuilding the inventory does not validate a scientific change. Semantic checks, source comparisons and mathematical arguments must remain valid. A new count needs its universe, algorithm, complete execution record and finite exceptions; a bounded search failure is not a negative membership decision.

For documents, compile temporary copies as described in `ARTICLE.md`, check the logs and inspect the pages. For graph drawings, keep adjacency data separate from coordinates, check every emitted edge and preserve the mathematical label style.

Default tests do not launch a census. Large enumerations follow `docs/full-reproduction.md`; their resource requirements are separate from the development route.
