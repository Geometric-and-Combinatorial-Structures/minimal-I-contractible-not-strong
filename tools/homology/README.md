# Classifying residual graphs by homology

The table classifier can leave acyclic graphs outside the strong class without a contractibility certificate. For each such **residual**, this stage computes reduced integral homology in every degree and checks the coefficient formulas over $\mathbb F_2$ and $\mathbb F_3$. Nonzero integral homology excludes I-contractibility. The [full reproduction guide](../../docs/full-reproduction.md#required-adjudication-of-every-residual) gives the command and the conditions for completing the classification.

`independent_homology_r2.py` implements integer boundary matrices and Smith reduction. `adjudicate_inventory_r2.py` reads an aggregated enumeration, runs that calculation on each residual and compares its field-homology predictions with Ripser through dimension two. It requires NumPy and Ripser and writes to a new directory outside the input run. Enumeration coverage and positive contractibility certificates are checked by the other stages of the full route.

## Historical comparison

`archive/verificacion_independiente_F4.py` preserves an additional comparison using separate graph decoding, elimination over $\mathbb F_2,\mathbb F_3,\mathbb F_5,\mathbb F_7$ and SymPy Smith reduction. It expects the four-directory layout documented in its header; those complete historical inputs are not included here. The [finite verifier](../../finite/README.md) instead recomputes first homology of the supplied residuals by a cycle-lattice presentation proved in the supplement.
