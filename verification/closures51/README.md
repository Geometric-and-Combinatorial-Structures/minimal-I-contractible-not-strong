# Finite regeneration of the 51-seed closure

The committed `run.json` is the saved `report.json` from the documented local invocation. It records a successful local regeneration with the unmodified current C classifier and nauty `labelg`. The 8,084 labelled non-strong outputs give 2,271 isomorphism classes, exactly the deposited class set. Every seed was processed, the process exited zero, and input hashes were unchanged. This calculation starts from the supplied 51 seeds; seed completeness is established by the enumeration and reduction lemmas described in the [verification map](../../docs/verification-scope.md).

Run from the repository root with a C11 compiler and nauty `labelg`:

```bash
python3 tools/reproduce_closures.py --cc gcc --labelg /path/to/labelg --output results/closures51
```

The output directory must be new. Raw closure output, canonicalized lists, logs and a report are written there. The compact committed report retains their hashes; those large generated streams are not distributed. A different canonical labeller build can change canonical strings while preserving the comparison within its own run.

The default finite route separately checks every deposited path, non-strong status, first homology group and isomorphism class. It regenerates the three small positive-seed closures using its own Python recursion and isomorphism backtracking. The finite route also checks that the 277 K4-free closure members lie among the 633 row-14 exceptions.
