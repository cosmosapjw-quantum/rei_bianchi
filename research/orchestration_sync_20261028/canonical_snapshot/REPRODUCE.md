# Saved-only structural validation

From this package directory, the following reads the saved package and calls the same structural validator. It does not stage sources, rebuild the graph, run compiler fixtures, import scientific code or reproduce historical calculations.

```sh
python3 - <<'PY'
import importlib.util
import json
from pathlib import Path
package = Path('.').resolve()
spec = importlib.util.spec_from_file_location('assembly_checker', package / 'assembly/assemble.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
result = checker.validate(json.loads((package / 'DAG.json').read_text()), package)
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['valid'] else 1)
PY
```

The validator checks source pointers, historical identities, dependency topology and the explicit future-execution metadata guards. It does not independently admit physical domains, assign new budgets or assert other nodes runnable. The original assembler's staging command requires the private working intake and is unnecessary for validating this standalone package.
