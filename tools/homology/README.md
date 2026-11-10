# Homology adjudication

`independent_homology_r2.py` is the exact integer boundary-matrix and Smith implementation whose SHA-256 appears in the F4 adjudication record:
`ffe667447460d5b5b9e56148f8c6c569f80f63da1caf1968c262b329ba188e29`.
It can be imported without running the historical comparison helpers.

`adjudicate_inventory_r2.py` accepts a validated campaign directory and creates a new output directory with all residual adjudications. It checks integer reduced homology in every dimension and compares the coefficient formulas with Ripser over F2 and F3 through dimension two. It requires NumPy and Ripser. It does not certify campaign completeness, authenticate old receipts or check the positive I certificates; those are separate obligations.

`archive/verificacion_independiente_F4.py` preserves the historical additional check with independent graph decoding, modular elimination over F2/F3/F5/F7 and SymPy Smith reduction. It also compares three historical versions of the counts and graph sets. It expects the original four-directory layout documented in its header and writes into that supplied verification layout. Those full historical inputs are not redistributed here, so it is archived source, not part of the quick command. The present finite verifier recomputes H1 by a separate cycle-lattice implementation.
