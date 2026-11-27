"""Opt-in R31M tuned adapter for the frozen R30 H source.

H0, grid, assembler and provider authority remain frozen R30.  Only the foreign
kernel is replaced by the separately-built R31M candidate after host/profile/
science-regression identity checks.  The scientific runtime is never mutated.
"""
from __future__ import annotations
import ctypes, hashlib, importlib.util, json, os, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO_ROOT/'src'))
from wu088_hh.autotune import validate_tuning_profile
from wu088_hh.hardware import inspect_host
from wu088_hh.promotion import validate_science_regression

RUNTIME=Path(os.environ['R31K_RUNTIME_ROOT']).resolve()
HERE=RUNTIME/'r31a'; MIXED=RUNTIME/'completion/mixed_h'
sys.path.insert(0,str(MIXED))
source=HERE/'wide_hybrid_run.py'
spec=importlib.util.spec_from_file_location('r31m_frozen_wide_hybrid_run',source)
if spec is None or spec.loader is None: raise RuntimeError(f'cannot load frozen source: {source}')
base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
base.ROOT=RUNTIME;base.MIXED=MIXED

PROFILE_PATH=Path(os.environ['WU088_R31M_TUNING_PROFILE']).resolve()
REGRESSION_PATH=Path(os.environ['WU088_R31M_REGRESSION']).resolve()
CANDIDATE_SO=Path(os.environ['WU088_R31M_CANDIDATE_SO']).resolve()
BUILD_KEY=os.environ['WU088_R31M_BUILD_KEY']
PROFILE=json.loads(PROFILE_PATH.read_text());REGRESSION=json.loads(REGRESSION_PATH.read_text())
HOST=inspect_host(use_smt=bool(PROFILE['selected'].get('use_smt',False)),
                  requested_workers=int(PROFILE['selected']['processes']),
                  kernel_threads=int(PROFILE['selected']['kernel_threads']))
validate_tuning_profile(PROFILE,HOST,BUILD_KEY)
PROMOTION=validate_science_regression(REGRESSION,
    profile_sha256=hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),build_key=BUILD_KEY)
KERNEL_THREADS=int(PROMOTION['kernel_threads'])

ROOT=RUNTIME
provider_gate=base.provider_gate
folder_for=base.folder_for
configuration=base.configuration
assemble=base.assemble
sha=base.sha

class Hybrid12(base.Hybrid12):
    def __init__(self):
        self.ref=base.WideReference()
        self.lib=ctypes.CDLL(str(CANDIDATE_SO))
        self.lib.precision_bits.restype=ctypes.c_int
        if self.lib.precision_bits()!=base.np.finfo(base.np.longdouble).nmant+1:
            raise RuntimeError('candidate long-double ABI mismatch')
        self.lib.hh_set_num_threads.argtypes=[ctypes.c_int];self.lib.hh_set_num_threads.restype=ctypes.c_int
        self.lib.hh_last_team_size.restype=ctypes.c_int
        if self.lib.hh_set_num_threads(KERNEL_THREADS): raise RuntimeError('candidate thread configuration rejected')
        self.fn=self.lib.mh_wide_foreign
        self.fn.argtypes=[ctypes.c_size_t,ctypes.c_size_t,base.DP,base.DP,base.DP,base.DP,base.DP,base.LP,base.LP]
        self.fn.restype=ctypes.c_int
        self.identity={
          'reference':self.ref.identity,
          'R31M_candidate_binary_sha256':sha(CANDIDATE_SO),
          'R31M_candidate_source_sha256':sha(REPO_ROOT/'native/candidate/r31a/hybrid12_wide_h_v2.cpp'),
          'R31M_build_key':BUILD_KEY,
          'R31M_tuning_profile_sha256':sha(PROFILE_PATH),
          'R31M_science_regression_sha256':sha(REGRESSION_PATH),
          'R31M_scoped_promotion':PROMOTION,
          **base.provider_gate(),
        }

def init(n,g,z,scale):
    base.STATE=(Hybrid12(),*base.configuration(n,g,z,scale),z)

def tuned_init(n,g,z,scale,groups,counter,lock,barrier):
    with lock:
        idx=counter.value;counter.value+=1
    if idx>=len(groups): raise RuntimeError('worker affinity index overflow')
    os.sched_setaffinity(0,set(groups[idx]))
    init(n,g,z,scale)
    barrier.wait()

pair=base.pair

def build_identity_for_orchestrator(args,h,d,t,W,gs,gw,length):
    ah=lambda x:hashlib.sha256(x.tobytes()).hexdigest()
    return {
      'producer':'wide_hybrid12_R31M_tuned_foreign_v1',
      'n':args.n,'g':args.g,'z':float(args.z),'z_hex':float(args.z).hex(),
      'gamma_scale':args.gamma_scale,'gamma_scale_length':length,
      'model_sha256':sha(ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'),
      'native':h.identity,'driver':sha(source),'assembler':sha(MIXED/'run.py'),'grid_source':sha(MIXED/'native.py'),
      'weights_source':sha(ROOT/'exact_weights/exact_laplace_weights.py'),
      'grid_sha256':{k:ah(v) for k,v in dict(t=t,W=W,gs=gs,gw=gw).items()},
      'sumabs_semantics':'triangle/L1 upper diagnostic, no outward rounding',
      'claim_ceiling':'H source only; R31M foreign-kernel execution promotion does not admit quadrature/full49/trajectory/production.',
      'runtime_binding_adapter':'R31M_TUNED_SIDECAR_NO_RUNTIME_MUTATION'
    }
