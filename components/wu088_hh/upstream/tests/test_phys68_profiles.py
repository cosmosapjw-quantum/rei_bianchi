"""Independent exact manufactured solutions and fail-closed runner contracts."""
from dataclasses import replace
from fractions import Fraction as F
import json
from pathlib import Path

from flint import acb, arb, ctx
import pytest

import wu088_hh.phys68_profiles as p
from wu088_hh.phys68_taylor import TaylorDisk, rational_ball


def small_request(**kwargs):
    base = p.ProfileRequest(max_ell=2, ell=2, ellprime=1, outer="28", degree=32,
                            precision_bits=256, coefficient_bits=512,
                            d1_absolute_goal="1e-10", d2_absolute_goal="1e-10")
    return replace(base, **kwargs)


@pytest.fixture
def constant_model(monkeypatch):
    # Constant symmetric V with all intermediate channels nonzero. F_j=1 is
    # a manufactured analytic model; no original-physics execution is claimed.
    def h(ell, center, degree, radius, bits):
        return TaylorDisk(F(center), F(radius), (acb(1),)+(acb(0),)*degree,
                          arb(1), bits, ell, "manufactured F=1")
    def v(a, b, center, degree, *args):
        return (acb((a+1)*(b+1)),)+(acb(0),)*degree
    monkeypatch.setattr(p, "coulomb_taylor", h)
    monkeypatch.setattr(p, "angular_taylor_coefficients", v)
    monkeypatch.setattr(p, "angular_complex_disk_bound", lambda *args: arb(9))
    monkeypatch.setattr(p, "local_coulomb_majorant", lambda *args: arb(1))
    return lambda a,b: F((a+1)*(b+1))


def test_polynomial_integral_exact_rational():
    with ctx.workprec(256):
        got=p.polynomial_integral((acb(3),acb(4),acb(5)),F(-1,4),F(1,4))
        assert got.contains(rational_ball(F(149,96)))
        odd=p.polynomial_integral((acb(0),acb(4),acb(0),acb(7)),F(-1,4),F(1,4))
        assert odd.is_zero()


def test_manufactured_volterra_profiles_full_sum(constant_model):
    req=small_request()
    q={pair:acb(0) for pair in req.pairs}
    total=acb(0)
    with ctx.workprec(256):
        for c in (F(111,4),F(109,4)):
            panel=p.build_panel(req,c,q)
            # Independent closed form q_ab(r)=V_ab*(28-r).
            for pair in req.pairs:
                for offset in (F(-1,4),F(0),F(1,4)):
                    truth=constant_model(*pair)*(28-c-offset)
                    assert panel.evaluate_first_born(*pair,offset).contains(rational_ball(truth))
            total+=panel.second_born_increment
            q=panel.q_left
        # Integral from27to28 of (28-r)^2 sum_j V_2j V_1j = 28.
        exact=sum((constant_model(2,j)*constant_model(1,j) for j in range(3)),F(0))/3
        assert exact==28
        assert total.contains(28)
        assert p.norm_radius_l1(total)<F(1,10**5)


def test_missing_intermediate_pair_refused(constant_model):
    req=small_request()
    q={pair:acb(0) for pair in req.pairs}
    q.pop(next(iter(q)))
    with pytest.raises(ValueError,match="every requested"):
        p.build_panel(req,F(111,4),q)


def test_complex_bilinear_not_hermitian(monkeypatch,constant_model):
    req=small_request(max_ell=0,ell=0,ellprime=0)
    monkeypatch.setattr(p,"angular_taylor_coefficients",lambda a,b,c,n,*args:(acb(0,1),)+(acb(0),)*n)
    q={pair:acb(0) for pair in req.pairs}
    with ctx.workprec(256):
        total=acb(0)
        for c in (F(111,4),F(109,4)):
            panel=p.build_panel(req,c,q);q=panel.q_left;total+=panel.second_born_increment
        assert total.contains(rational_ball(F(-1,3)))
        assert not total.contains(rational_ball(F(1,3)))


def test_zero_free_failure_is_explicit(monkeypatch,constant_model):
    def bad(ell,c,n,r,bits):
        return TaylorDisk(F(c),F(r),(acb(0),acb(1))+(acb(0),)*(n-1),arb(10),bits,ell)
    monkeypatch.setattr(p,"coulomb_taylor",bad)
    req=small_request()
    with pytest.raises(p.ProfileEnclosureFailure,match="UNRESOLVED_ZERO_FREE_BOUND"):
        p.build_panel(req,F(111,4),{pair:acb(0) for pair in req.pairs})


@pytest.mark.parametrize("kwargs",[
    {"max_ell":True},{"max_ell":65},{"ell":29},{"outer":65.0},
    {"half_width":"3/10"},{"zero_free_radius":"1/4"},{"majorant_radius":"27"},
    {"d1_absolute_goal":"0"},{"degree":1},{"coefficient_bits":128},
])
def test_invalid_request_refused(kwargs):
    with pytest.raises((ValueError,TypeError)):
        replace(p.ProfileRequest(),**kwargs).validate()


def test_full_pair_coverage():
    r=p.ProfileRequest().validate()
    assert len(r.pairs)==57
    assert r.panel_count==76
    assert all(p.pair_key(a,j) in r.pairs for a in(21,20) for j in range(29))


def test_cap_and_precision_restored(constant_model):
    req=small_request()
    before=(ctx.prec,ctx.cap)
    p.build_panel(req,F(111,4),{pair:acb(0) for pair in req.pairs})
    assert (ctx.prec,ctx.cap)==before


def test_resume_verifies_then_reuses_without_recomputation(tmp_path,monkeypatch,constant_model):
    req=small_request()
    monkeypatch.setattr(p,"radial_certificate",lambda *a:{"terms":[{"radial_cutoff_bound":F(0)},{"radial_cutoff_bound":F(0)}]})
    first=p.run_profiles("manufactured",tmp_path,req,max_new_panels=1)
    assert first["status"]=="PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE"
    assert first["panels_computed_this_call"]==1
    second=p.run_profiles("manufactured",tmp_path,req,resume=True)
    assert second["panels_reused_this_call"]==1 and second["panels_computed_this_call"]==1
    old=p.build_panel
    monkeypatch.setattr(p,"build_panel",lambda *a:pytest.fail("completed panel repeated"))
    third=p.run_profiles("manufactured",tmp_path,req,resume=True)
    assert third["panels_reused_this_call"]==2 and third["panels_computed_this_call"]==0
    saved=json.loads((tmp_path/"panel_0000.json").read_text())
    saved["payload"]["center"]="99"
    (tmp_path/"panel_0000.json").write_text(json.dumps(saved))
    with pytest.raises(ValueError,match="payload hash"):
        p.run_profiles("manufactured",tmp_path,req,resume=True)


def test_request_mismatch_and_existing_directory_refused(tmp_path,monkeypatch,constant_model):
    req=small_request()
    monkeypatch.setattr(p,"radial_certificate",lambda *a:{"terms":[{"radial_cutoff_bound":F(0)},{"radial_cutoff_bound":F(0)}]})
    p.run_profiles("manufactured",tmp_path,req,max_new_panels=0)
    with pytest.raises(FileExistsError):p.run_profiles("manufactured",tmp_path,req)
    with pytest.raises(ValueError,match="fingerprint"):
        p.run_profiles("manufactured",tmp_path,replace(req,degree=33),resume=True)


def test_saved_profile_loader_never_reintegrates(tmp_path,monkeypatch,constant_model):
    req=small_request()
    monkeypatch.setattr(p,"radial_certificate",lambda *a:{"terms":[{"radial_cutoff_bound":F(0)},{"radial_cutoff_bound":F(0)}]})
    p.run_profiles("manufactured",tmp_path,req)
    monkeypatch.setattr(p,"build_panel",lambda *a:pytest.fail("profile loader reintegrated"))
    monkeypatch.setattr(p,"polynomial_integral",lambda *a:pytest.fail("profile loader reintegrated"))
    panel=p.load_profile_panel("manufactured",tmp_path,1)
    with ctx.workprec(256):
        for pair in req.pairs:
            assert panel.evaluate_first_born(*pair,F(1,8)).contains(
                rational_ball(constant_model(*pair)*F(5,8)))
    saved=json.loads((tmp_path/"CERTIFICATE.json").read_text())
    saved["panels"][1]["payload_sha256"]="0"*64
    (tmp_path/"CERTIFICATE.json").write_text(json.dumps(saved))
    with pytest.raises(ValueError,match="manifest"):
        p.load_profile_panel("manufactured",tmp_path,1)


def test_odd_radius_roundtrip_is_containing_not_byte_identical():
    # This actual Arb magnitude exposed the real two-panel resume failure.
    from wu088_hh.phys67_coulomb_certificate import restore_complex_ball,complex_ball_record
    component={"midpoint":{"mantissa":"0","exponent2":0},
               "radius":{"mantissa":"583153041","exponent2":-446},"display":"not hashed as a float"}
    original={"real":component,"imag":component}
    with ctx.workprec(384):
        restored=complex_ball_record(restore_complex_ball(original))
    assert restored["real"]["radius"]!=original["real"]["radius"]
    assert p._serialized_box_contains(restored,original)
    assert not p._serialized_box_contains(original,restored)


def test_saved_boundary_carry_requires_containment():
    from wu088_hh.phys67_coulomb_certificate import complex_ball_record
    with ctx.workprec(384):
        zero=complex_ball_record(acb(0));one=complex_ball_record(acb(1))
    state={"0,0":one}
    payload={"pairs":[{"pair":[0,0],"q_right":zero,"q_left":zero}]}
    with pytest.raises(ValueError,match="does not enclose"):
        p._verify_boundary_carry(payload,state,((0,0),))
