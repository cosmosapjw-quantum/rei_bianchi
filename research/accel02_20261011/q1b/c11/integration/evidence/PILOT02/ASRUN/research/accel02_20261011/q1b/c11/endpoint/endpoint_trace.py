"""C11 explicit native one-sided value traces; no endpoint-cell admission.

The exact existing native SIGMA is evaluated at the declared binary64 energy,
never at a shifted energy. At a threshold, the source's strict less-than branch
proves a zero LEFT limit; its active analytic fit proves the RIGHT value equals
SIGMA(threshold). Caller must establish physical endpoint/side provenance.
This module deliberately provides no moment conversion or endpoint Jacobian.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import math
import sys

HERE=Path(__file__).resolve().parent
Q1B=HERE.parent.parent
REPO=Q1B.parents[2]
sys.path.insert(0,str(Q1B))
from opacity_native import NativeOpacity,EXPECTED_BINARY_SHA256,THRESHOLDS_EV

SOURCE_PINS={
    'rust/rei_microphysics/src/atomic_provider.rs':'b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3',
    'research/accel02_20261011/n1/native/src/main.rs':'239a08b0fdbe171f21112c128602be3ad9bbaae596ada1b6791fda482e8aeb76',
    'research/accel02_20261011/q1b/opacity_native.py':'6818b100e7a5331f9f244c2788813ea5ba3a746ad6c801b02e7fd1943706e9b1',
}

class TraceContractError(ValueError):
    pass

@dataclass(frozen=True)
class NativeValueTrace:
    energy_ev: float
    side: str
    sigma_cm2: tuple
    trace_branch: tuple
    input_energy_hex: str
    native_evaluation_energy_hex: str
    native_binary_sha256: str
    source_pins: tuple
    actual_native_calls: int
    claim: str='EXPLICIT_ENERGY_ONE_SIDED_VALUE_ONLY'
    admits_rounded_endpoint: bool=False
    supplies_endpoint_jacobian: bool=False


def native_trace(opacity,energy_ev,side):
    """Value of lim(E -> energy_ev from side) sigma(E), cm^2, HI/HeI/HeII.

    ``energy_ev`` is an explicitly identified binary64 endpoint in eV; this
    interface does not claim that a rounded R*q equals the physical endpoint.
    Caller must retain exact endpoint/threshold-side metadata or fail closed.
    At the hard 50keV domain maximum only the interior LEFT limit exists.
    """
    if not isinstance(opacity,NativeOpacity) or opacity.binary_sha256!=EXPECTED_BINARY_SHA256:
        raise TraceContractError('ACTUAL_PINNED_NATIVE_OPACITY_REQUIRED')
    energy=float(energy_ev)
    if side not in ('left','right'):
        raise TraceContractError('EXPLICIT_LEFT_OR_RIGHT_REQUIRED')
    if not math.isfinite(energy) or not 0.<energy<=50000.:
        raise TraceContractError('TRACE_ENERGY_PROVIDER_DOMAIN')
    if energy==50000. and side=='right':
        raise TraceContractError('RIGHT_TRACE_OUTSIDE_PROVIDER_DOMAIN')
    for name,expected in SOURCE_PINS.items():
        if hashlib.sha256((REPO/name).read_bytes()).hexdigest()!=expected:
            raise TraceContractError('TRACE_SOURCE_IDENTITY_CHANGED:'+name)
    before=opacity.native_calls
    values=opacity.sigma([energy])[0]
    branches=[]
    for k,threshold in enumerate(THRESHOLDS_EV):
        if energy<threshold or (energy==threshold and side=='left'):
            # This is the exact source-defined zero branch, not a sample and
            # not a clipped fit. Other species remain actual native values.
            values[k]=0.
            branches.append('BELOW_THRESHOLD_ANALYTIC_ZERO')
        else:
            branches.append('CONTINUOUS_ACTIVE_NATIVE_VALUE')
    return NativeValueTrace(energy,side,tuple(map(float,values)),tuple(branches),
        energy.hex(),energy.hex(),opacity.binary_sha256,tuple(SOURCE_PINS.items()),
        opacity.native_calls-before)
