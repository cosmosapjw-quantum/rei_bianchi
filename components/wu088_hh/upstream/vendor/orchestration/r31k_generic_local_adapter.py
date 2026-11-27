"""Path-only adapter for the frozen R30 wide-H source on a nested local runtime.

No scientific formulas or provider admission are changed here.  Unlike the older
R31A local adapter, this file deliberately does NOT import the z=8-only R31A
provider bridge.  It binds the exact frozen R30 driver to the runtime root named
by R31K_RUNTIME_ROOT so the original |z|<=64 source domain can be exercised.
"""
from __future__ import annotations
import hashlib, importlib.util, os, sys
from pathlib import Path

RUNTIME = Path(os.environ['R31K_RUNTIME_ROOT']).resolve()
HERE = RUNTIME / 'r31a'
MIXED = RUNTIME / 'completion/mixed_h'
sys.path.insert(0, str(MIXED))

source = HERE / 'wide_hybrid_run.py'
spec = importlib.util.spec_from_file_location('r31k_frozen_wide_hybrid_run', source)
if spec is None or spec.loader is None:
    raise RuntimeError(f'cannot load frozen wide-H source: {source}')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
base.ROOT = RUNTIME
base.MIXED = MIXED

ROOT = RUNTIME
provider_gate = base.provider_gate
Hybrid12 = base.Hybrid12
folder_for = base.folder_for
configuration = base.configuration
init = base.init
pair = base.pair
assemble = base.assemble
sha = base.sha

def build_identity_for_orchestrator(args, h, d, t, W, gs, gw, length):
    ah = lambda x: hashlib.sha256(x.tobytes()).hexdigest()
    return {
      'producer':'wide_hybrid12_R30_v1',
      'n':args.n,'g':args.g,'z':float(args.z),'z_hex':float(args.z).hex(),
      'gamma_scale':args.gamma_scale,'gamma_scale_length':length,
      'model_sha256':sha(ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'),
      'native':h.identity,
      'driver':sha(source),
      'assembler':sha(MIXED/'run.py'),
      'grid_source':sha(MIXED/'native.py'),
      'weights_source':sha(ROOT/'exact_weights/exact_laplace_weights.py'),
      'grid_sha256':{k:ah(v) for k,v in dict(t=t,W=W,gs=gs,gw=gw).items()},
      'sumabs_semantics':'triangle/L1 upper diagnostic, no outward rounding',
      'claim_ceiling':'H source computation only; requires B160/B192 convergence and later O/D/JVP/ionic full-matrix admission.',
      'runtime_binding_adapter':'R31K_GENERIC_PATH_ONLY_NO_R31A_Z8_AUTHORITY'
    }
