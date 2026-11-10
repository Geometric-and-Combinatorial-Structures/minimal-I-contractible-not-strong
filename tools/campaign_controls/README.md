# Production controls

These scripts retain their historical filenames. They verify receipt metadata, state, approved aggregate attempts and per-residue comparisons; `finalize_campaign_r6.py` assembles these checks. They were selected from the controls used with the exact classifier. Read each `--help` before use with a fresh campaign directory. They do not submit jobs or transfer data.

`check_audit_python_r6.py` checks the optional independent homology environment (`numpy`, `sympy`, `networkx`, `ripser`). That environment is not required by the standard-library quick verification route. The large production directories to which these controls applied are not included here, and these historical control runs have not been reexecuted in preparing this selection.
