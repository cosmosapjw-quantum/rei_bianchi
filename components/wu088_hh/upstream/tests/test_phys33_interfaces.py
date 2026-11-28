"""PHYS38: all exact radial interfaces and rigorous H^-1 delta estimate."""
from fractions import Fraction as F
from pathlib import Path
import json

import numpy as np
import pytest

import wu088_hh.phys33_interfaces as module
from wu088_hh.phys33_interfaces import all_interface_certificate

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
RESULT=ROOT/"research/hh_phys38_20261015/results/INTERFACE_HMINUS1.json"


def test_all_five_actual_binary64_interfaces_hminus1():
    z=all_interface_certificate(SOURCE)
    assert z["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert len(z["interfaces"])==5
    assert all(t["field_value_jump_exact_zero"] for t in z["interfaces"])
    assert F(z["full_broken_Laplacian_distribution_Hminus1_upper"])<F(2,10**13)
    assert F(z["Schrodinger_minus_Delta_over_two_distribution_Hminus1_upper"])<F(1,10**13)
    ref=json.loads(RESULT.read_text())
    for k in ("interfaces","input_sha256",
              "full_broken_Laplacian_distribution_Hminus1_upper",
              "Schrodinger_minus_Delta_over_two_distribution_Hminus1_upper"):
        assert z[k]==ref[k]


@pytest.mark.parametrize("b,w",[(F(1,10),F(1,40)),
                                (F(7,10),F(1,10)),
                                (F(10),F(1,2))])
def test_radial_trace_constant_is_conservative_for_manufactured_test(b,w):
    # Pair a manufactured u(r)=1+r, and confirm the 1-sided inequality
    # before converting it into a weighted physical H1 norm.
    r0=b-w
    u_at=(1+b)**2
    analytic_int_u=w+ b*b*w + b*w*w + w*w*w/F(3) + 2*b*w-w*w
    # Independent exact polynomial integration of (1+r)^2.
    analytic_int_u=((1+b)**3-(1+r0)**3)/3
    analytic_int_du=w
    bound=2/w*analytic_int_u+2*w*analytic_int_du
    assert bound>=u_at


def test_refuse_hminus1_claim_for_nonzero_frozen_value_jump(monkeypatch):
    real=module.load_frozen
    def adulterated(fn,pinned=True):
        radial,u,digest=real(fn,pinned)
        u=u.copy()
        # Modify only the right panel first node. The test deliberately
        # bypasses the provenance pin to hit the mathematical guard.
        u[0,2,0] += 0.0001
        return radial,u,digest
    monkeypatch.setattr(module,"load_frozen",adulterated)
    with pytest.raises(ArithmeticError,match="nonzero field-value jump"):
        all_interface_certificate(SOURCE)


def test_unsafe_precision_rejected():
    with pytest.raises(ValueError):
        all_interface_certificate(SOURCE,4)
