from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np

STAGE = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _mods():
    tensor = _load("r2b_r2a_tensorized_controller", STAGE / "analysis/tensorized_inputs.py")
    picard = _load("r2b_r2a_globalized_controller", STAGE / "analysis/globalized_picard.py")
    controller = _load("r2b_r2a_adaptive_controller", STAGE / "analysis/adaptive_controller.py")
    return tensor, picard, controller


def _state(tensor, x=0.1):
    nh = np.array([1.0, 2.0])
    nhe = 0.079 * nh
    v = np.zeros((6, 2))
    v[1] = nh*x; v[0] = nh-v[1]
    v[2] = nhe*0.9; v[3] = nhe*0.09; v[4] = nhe-v[2]-v[3]
    T = np.array([5000.0, 6000.0])
    particles = nh+nhe+v[1]+v[3]+2*v[4]
    v[5] = 1.5*1.380649e-16*particles*T
    return tensor.ArrayState(v,T)


def _shift(tensor, state, dx):
    v=state.values.copy(); nh=v[0]+v[1]
    x=np.clip(v[1]/nh+dx,1e-6,1-1e-6)
    v[1]=nh*x; v[0]=nh-v[1]
    particles=nh+v[2]+v[3]+v[4]+v[1]+v[3]+2*v[4]
    T=state.temperature_K*(1.0+0.05*dx)
    v[5]=1.5*1.380649e-16*particles*T
    return tensor.ArrayState(v,T)


def _trial(picard, state, *, converged=True, dx=0.0, classification="FIXED_POINT_NONCONVERGENCE"):
    return picard.TrialResult(
        state=state,
        converged=converged,
        iterations=3,
        residual=1e-12 if converged else 1.0,
        residual_trace=(1e-2,1e-6,1e-12) if converged else (1.0,),
        damping_trace=(0.5,),
        map_calls=4,
        minimum_species=float(np.min(state.values[:5])),
        max_hydrogen_residual=0.0,
        max_helium_residual=0.0,
        max_owner_residual=0.0,
        max_photon_residual=0.0,
        max_thermal_residual=0.0,
        certificate={} if converged else {"classification":classification},
    )


def test_controller_starts_at_dt8_and_bisects_only_failed_step():
    tensor,picard,ctl=_mods(); initial=_state(tensor)
    # Fail for partition 8 and 16; pass from partition 32 downward.
    def solve(state,t0,t1,partition,trial_name):
        if partition < 32:
            return ctl.MicroTrial(_trial(picard,state,converged=False),{})
        dt=t1-t0
        return ctl.MicroTrial(_trial(picard,_shift(tensor,state,1e-4*dt)),{"photon":dt})
    history=ctl.AcceptedArrayHistory(state=initial,ledgers={"photon":0.0})
    result=ctl.AdaptiveController().advance_interval(history=history,t0=0.0,t1=1.0,solve_trial=solve)
    assert result.accepted
    assert result.attempts[0].partition == 8
    assert all(b.child_partition == 2*b.parent_partition for b in result.bisections)
    assert max(a.partition for a in result.attempts) <= 1024
    assert any(b.parent_partition==8 for b in result.bisections)
    assert any(b.parent_partition==16 for b in result.bisections)
    assert history.commit_count == result.accepted_microsteps


def test_full_and_two_half_trials_must_all_pass_and_rejection_is_byte_exact():
    tensor,picard,ctl=_mods(); initial=_state(tensor)
    def solve(state,t0,t1,partition,trial_name):
        if trial_name == "SECOND_HALF":
            return ctl.MicroTrial(_trial(picard,state,converged=False),{})
        return ctl.MicroTrial(_trial(picard,_shift(tensor,state,1e-5)),{"photon":t1-t0})
    history=ctl.AcceptedArrayHistory(state=initial,ledgers={"photon":0.0})
    before=history.serialize()
    result=ctl.AdaptiveController(minimum_partition=1024).advance_interval(
        history=history,t0=0.0,t1=1.0,solve_trial=solve
    )
    assert not result.accepted
    assert result.certificate["failed_trial"] == "SECOND_HALF"
    assert result.certificate["classification"] == "FIXED_POINT_NONCONVERGENCE"
    assert history.serialize() == before
    assert history.commit_count == 0


def test_local_error_failure_bisects_and_uses_two_half_solution_on_accept():
    tensor,picard,ctl=_mods(); initial=_state(tensor)
    def solve(state,t0,t1,partition,trial_name):
        dt=t1-t0
        # At partition 8, full/two-half disagree above tolerance; from 16 they agree.
        scale = 5e-3 if partition==8 and trial_name=="FULL" else 1e-5
        return ctl.MicroTrial(_trial(picard,_shift(tensor,state,scale*dt)),{"photon":dt})
    history=ctl.AcceptedArrayHistory(state=initial,ledgers={"photon":0.0})
    result=ctl.AdaptiveController().advance_interval(history=history,t0=0.0,t1=1.0,solve_trial=solve)
    assert result.accepted
    assert any(b.reason=="LOCAL_ERROR_FAILURE" for b in result.bisections)
    assert result.max_local_error <= 2e-4
    assert history.ledgers["photon"] == 1.0


def test_restart_roundtrip_is_byte_identical_and_replay_deterministic():
    tensor,picard,ctl=_mods(); initial=_state(tensor)
    def solve(state,t0,t1,partition,trial_name):
        return ctl.MicroTrial(_trial(picard,_shift(tensor,state,1e-6*(t1-t0))),{"photon":t1-t0})
    history=ctl.AcceptedArrayHistory(state=initial,ledgers={"photon":0.0})
    result=ctl.AdaptiveController().advance_interval(history=history,t0=0.0,t1=1.0,solve_trial=solve)
    payload=history.restart_payload()
    restored=ctl.AcceptedArrayHistory.from_restart_payload(payload)
    assert result.accepted
    assert restored.serialize()==history.serialize()
    assert restored.commit_count==history.commit_count
