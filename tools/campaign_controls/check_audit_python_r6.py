#!/usr/bin/env python3
"""Require the versions recorded for audit_r3; print what was actually imported."""
import json,platform,sys
import numpy,sympy,networkx,ripser
EXPECTED={'python':'3.11.17','numpy':'2.3.5','sympy':'1.14.0','networkx':'3.6.1','ripser':'0.6.12'}
observed={'python':platform.python_version(),'numpy':numpy.__version__,'sympy':sympy.__version__,'networkx':networkx.__version__,'ripser':ripser.__version__}
ok=observed==EXPECTED
print(json.dumps({'PASS':ok,'executable':sys.executable,'versions':observed,'expected':EXPECTED},sort_keys=True))
raise SystemExit(0 if ok else 1)
