"""Generated fixed-manifest worker; no arbitrary command arguments."""
import hashlib, importlib.util, pathlib, sys
sys.dont_write_bytecode = True
p = pathlib.Path('/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder/native_execution_20261001_v1/mpi_native_tasks/worker.py')
if hashlib.sha256(p.read_bytes()).hexdigest() != 'b4225733844df0971a197172e531c13313b17404c170542d4a6f25db4fa77398':
    raise SystemExit('CORE_WORKER_CHANGED')
spec = importlib.util.spec_from_file_location('_bound_native_worker', p)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
raise SystemExit(worker.main('515fa639abb69b5f07cafc0ca21cd5b8b520c97a784ca5b5380063bd6e195167', '/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder/native_execution_20261001_v1/mpi_native_tasks/readback_bundle_baseline_strict/MANIFEST.json'))
