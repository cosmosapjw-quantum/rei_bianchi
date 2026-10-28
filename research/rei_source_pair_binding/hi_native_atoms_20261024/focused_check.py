"""One planned fixture group. Execution requires root release via runner."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback
import native_source as ns

HERE = Path(__file__).resolve().parent


# Independent integer-dyadic oracle: no Fraction arithmetic inside accumulator.
def dyadic(value):
    numerator, denominator = float(value).as_integer_ratio()
    return numerator, denominator.bit_length()-1


def dadd(left, right):
    a, ea = left; b, eb = right
    exponent = max(ea, eb)
    return (a << (exponent-ea)) + (b << (exponent-eb)), exponent


def dmul(left, right):
    a, ea = left; b, eb = right
    return a*b, ea+eb


def integer_oracle(atoms, chi):
    A = K = P = (0, 0)
    c = dyadic(chi)
    for k, w in atoms:
        kd, wd = dyadic(k), dyadic(w)
        A = dadd(A, wd)
        K = dadd(K, dmul(kd, wd))
        P = dadd(P, dmul(wd, dadd(kd, c)))
    return {'A': A, 'K': K, 'B': dmul(c, A), 'P': P}


def verify_oracle(moment, oracle):
    for name, (numerator, exponent) in oracle.items():
        actual = getattr(moment, name)
        assert actual.numerator*(1 << exponent) == numerator*actual.denominator, name


def verify_source(source):
    assert source.energy.exact_sum == 0
    assert source.nuclei_residual_exact == source.charge_residual_exact == 0
    for vector in (source.energy, source.particles):
        assert vector.rounded_sum_exact-vector.exact_sum == sum(vector.errors, Fraction(0))
        assert all(abs(error) <= bound for error,bound in zip(vector.errors,vector.error_bounds))
    assert abs(source.energy.rounded_sum_exact) <= source.energy.rounding_budget
    n = source.particles
    for indices in (((0,1),(1,1)), ((1,1),(2,-1),(3,-1))):
        residual = sum((sign*Fraction(n.rounded[i]) for i,sign in indices), Fraction(0))
        budget = sum((n.error_bounds[i] for i,sign in indices), Fraction(0))
        assert abs(residual) <= budget


def refuses(call):
    try:
        call()
    except (ValueError, OverflowError):
        return
    raise AssertionError('expected invalid-input refusal')


def main():
    atoms = ns.load_selected_atoms()
    summary_bytes = (HERE/'inputs/source_card.json').read_bytes()
    assert hashlib.sha256(summary_bytes).hexdigest() == ns.SUMMARY_SHA256
    summary = json.loads(summary_bytes)
    moment = ns.native_moments(atoms)
    assert len(atoms) == moment.atom_count == 4368
    assert all(k >= 0 and w > 0 and k+ns.CHI <= 50000 for k,w in atoms)
    assert 0 <= moment.K <= moment.maximum_kinetic*moment.A
    assert moment.P == moment.B+moment.K
    oracle = integer_oracle(atoms, ns.CHI)
    verify_oracle(moment, oracle)
    comparison = ns.rounding_decomposition(atoms, summary, moment=moment)
    assert all(value == 0 for value in comparison['identity_residuals'].values())
    assert comparison['delta_r_E_identity'] == comparison['delta_r_B_identity'] == 0
    assert all(comparison['finite_fsum_ulp_certificates'].values())
    assert comparison['saved_provider_scalars_agree']
    assert comparison['donor_residual_saved'] == comparison['donor_residual_recomputed']
    assert comparison['donor_residual_saved'] < 0
    assert sum(b['row_count'] for b in comparison['bins']) == 4368
    assert sum((b['A_exact'] for b in comparison['bins']), Fraction(0)) == moment.A
    assert sum((b['K_exact'] for b in comparison['bins']), Fraction(0)) == moment.K
    assert all(b['provider_scalar_agreement'] for b in comparison['bins'])
    # Explicit boundary selectors: exactly10 and exactly9937.21 enter upper bins.
    from bisect import bisect_right
    assert [bisect_right((10.0,9937.21), value) for value in
            (math.nextafter(10.0,-math.inf),10.0,math.nextafter(9937.21,-math.inf),9937.21)] == [0,1,1,2]
    hand = ns.native_moments(((0,1),(2,3)), threshold_eV=4)
    assert (hand.A,hand.K,hand.B,hand.P) == (4,6,16,22)
    verify_oracle(hand, integer_oracle(((0,1),(2,3)),4))
    hand_source = ns.source_per_href_native(hand, Fraction(1,4), a=2)
    assert hand_source.energy.exact == (0,8,-11,0,0,3)
    assert hand_source.particles.exact == (-2,2,2,0,-2)
    native_source = ns.source_per_href_native(moment, Fraction(3,7), a=Fraction(2,5))
    assert native_source.normalization == Fraction(6,35)
    jvp = ns.source_jvp_native(moment, 3, -5, a=2, da=1)
    assert jvp.normalization == -7
    assert jvp.energy.exact[1] == -7*moment.B
    zero = ns.source_per_href_native(moment,0,a=7)
    assert all(v == 0 for v in zero.energy.exact+zero.particles.exact)
    tiny = ns.source_per_href_native(hand,Fraction(1,1 << 1200))
    assert any(tag == 'final_underflow_to_zero' for tag in tiny.energy.tags)
    subnormal = ns.source_per_href_native(hand,Fraction(1,1 << 1070))
    assert any(tag == 'subnormal' for tag in subnormal.energy.tags)
    exact_scaling = ns.source_per_href_native(hand,Fraction(1,1 << 1100),a=1 << 1100)
    assert exact_scaling.normalization == 1
    for source in (hand_source,native_source,jvp,zero,tiny,subnormal,exact_scaling):
        verify_source(source)
    for bad in (True, float('nan'), float('inf'), -1):
        refuses(lambda bad=bad: ns.source_per_href_native(hand,bad))
        refuses(lambda bad=bad: ns.source_per_href_native(hand,1,a=bad))
        refuses(lambda bad=bad: ns.native_moments(((bad,1),),threshold_eV=4))
        refuses(lambda bad=bad: ns.native_moments(((1,bad),),threshold_eV=4))
    for bad in (True,float('nan'),float('inf')):
        refuses(lambda bad=bad: ns.source_jvp_native(hand,1,bad))
        refuses(lambda bad=bad: ns.source_jvp_native(hand,1,1,da=bad))
    refuses(lambda: ns.native_moments(((1,0),)))
    refuses(lambda: ns.native_moments(((50000,1),)))
    refuses(lambda: ns.native_moments(()))
    refuses(lambda: ns.load_selected_atoms(channel='HeI'))
    refuses(lambda: ns.load_selected_atoms(redshift=2.316))
    refuses(lambda: ns.load_selected_atoms(redshift=True))
    refuses(lambda: ns.source_per_href_native(hand,1 << 2000))
    print(json.dumps(ns.jsonable({'schema':'REI_HI_NATIVE_ATOMS_FIXTURE_V1',
          'fixture_groups':1,'observed_status':'PASS_IMPLEMENTATION_CONTROLS_ROOT_REVIEW_REQUIRED',
          'actual_primary_rows':len(atoms),'moments':moment,
          'integer_dyadic_oracle':{key:{'numerator':str(n),'denominator_power2':e} for key,(n,e) in oracle.items()},
          'comparison':comparison,'source':native_source,'signed_JVP':jvp,
          'hand_source':hand_source,'tiny_source':tiny,'subnormal_source':subnormal,
          'control_groups':['actual_atoms','integer_dyadic_oracle','four_delta_identities',
             'provider_rounding','bins','hand_case','normalization_once','signed_JVP',
             'zero','tiny_underflow','subnormal','exact_intermediate_scaling','input_guards'],
          'scientific_admission':'ROOT_DECISION_REQUIRED'}),sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
