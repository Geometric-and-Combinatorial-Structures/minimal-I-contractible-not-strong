# Checking partitioned enumerations

These scripts check residue receipts, completion state, aggregation attempts and comparisons between enumerations. `finalize_campaign_r6.py` combines the checks. They operate on existing run directories and do not submit jobs or transfer data. The [full reproduction guide](../../docs/full-reproduction.md) describes the input universes and the required stages; each script's `--help` gives its interface.

`check_audit_python_r6.py` checks the optional homology environment: NumPy, SymPy, NetworkX and Ripser. The standard-library finite route does not require these packages.

Historical filenames retain the source identities used in the enumeration records. Complete historical run directories are not distributed; the selected records and their scope are described in [`finite/provenance/`](../../finite/provenance/).
