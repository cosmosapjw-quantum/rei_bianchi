"""Previously approved targeted clean-directory smoke; no IVP."""
from pathlib import Path
import sys,json,bounded
unit=Path(__file__).resolve().parents[1];clean=unit/'results/launcher_smoke_workspace_capfixed'
if clean.exists():raise RuntimeError('SMOKE_WORKSPACE_EXISTS')
(clean/'code').mkdir(parents=True);(clean/'code/harmless.py').write_text('print("CLEAN_DIRECTORY_SMOKE_NO_IVP")\n')
bounded.BASE=clean;sys.argv=['bounded.py','harmless','harmless.py'];rc=bounded.main()
passed=rc==0 and (clean/'results/harmless_stdout.log').read_text().strip()=='CLEAN_DIRECTORY_SMOKE_NO_IVP'
(unit/'results/launcher_smoke.json').write_text(json.dumps({'pass':passed,'new_IVPs':0})+'\n')
raise SystemExit(0 if passed else 1)

