"""Generated fixed-manifest worker; no arbitrary command arguments."""
import hashlib, importlib.util, pathlib, sys
sys.dont_write_bytecode = True
p = pathlib.Path('/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder/native_execution_20261001_v1/mpi_native_tasks/worker.py')
if hashlib.sha256(p.read_bytes()).hexdigest() != '64d8d91a0cb624dd2eda8b4df0d75ff5627cf2e872f459fc9fb40c2dfb3f0ba6':
    raise SystemExit('CORE_WORKER_CHANGED')
spec = importlib.util.spec_from_file_location('_bound_native_worker', p)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
raise SystemExit(worker.main('5d31112d2a23e5c833395db372a7b6a7d352c31a0120185de349f3e30567dea6', '/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder/native_execution_20261001_v1/mpi_native_tasks/readback_bundle_baseline/MANIFEST.json'))
