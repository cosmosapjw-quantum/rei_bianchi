#!/usr/bin/env python3
"""Independent PHYS13 decision checks; never imports or executes candidate code."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import struct
import sys
import time

sys.set_int_max_str_digits(0)
ROOT = Path('/workspace/scratch/b826cbaab54f/HH_PHYS13_20261012_v1')
OUT = Path(__file__).resolve().parent
checks = []

def ok(name, test):
    if not test:
        raise AssertionError(name)
    checks.append(name)

def atom(x):
    return x if isinstance(x, tuple) else (F(x), F(x))

def add(*xs):
    xs = [atom(x) for x in xs]
    return sum((x[0] for x in xs), F(0)), sum((x[1] for x in xs), F(0))

def neg(x):
    x = atom(x)
    return -x[1], -x[0]

def sub(x, y):
    return add(x, neg(y))

def mul(*xs):
    ans = (F(1), F(1))
    for x in xs:
        x = atom(x)
        ends = [a * b for a in ans for b in x]
        ans = min(ends), max(ends)
    return ans

def div(x, y):
    y = atom(y)
    assert y[1] < 0 or y[0] > 0
    return mul(x, (1 / y[1], 1 / y[0]))

def sq(x):
    x = atom(x)
    if x[0] >= 0:
        return x[0] ** 2, x[1] ** 2
    if x[1] <= 0:
        return x[1] ** 2, x[0] ** 2
    return F(0), max(x[0] ** 2, x[1] ** 2)

def cap(x, y):
    a = max(x[0], y[0]), min(x[1], y[1])
    assert a[0] <= a[1]
    return a

def lift(h):
    return F.from_float(struct.unpack('>d', bytes.fromhex(h))[0])

def unpack(x):
    if 'exact' in x:
        return tuple(F(int(x['exact'][edge][0]), int(x['exact'][edge][1])) for edge in ['lo', 'hi'])
    return lift(x['lo_bits']), lift(x['hi_bits'])

def eq(name, actual, stored):
    ok(name, actual == unpack(stored))

def sdisp(x):
    return [float(x[0]), float(x[1])]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def invariant_decimals(tree, prefix=''):
    if isinstance(tree, dict):
        if 'exact' in tree and 'outward_decimal' in tree:
            a = unpack(tree)
            dec = list(map(F, tree['outward_decimal']))
            ok(prefix + ': decimal enclosure', dec[0] <= a[0] <= a[1] <= dec[1])
        for k, v in tree.items():
            invariant_decimals(v, prefix + '/' + k)
    elif isinstance(tree, list):
        for j, v in enumerate(tree):
            invariant_decimals(v, prefix + '/' + str(j))

started = time.perf_counter()
inp = json.loads((ROOT / 'inputs/phys09/PROJECTED_RESULTS.json').read_text())
result = json.loads((ROOT / 'results/thermo_v2/THERMO_RESULTS.json').read_text())
leaves_path = ROOT / 'inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json'
leaves = json.loads(leaves_path.read_text())
ok('candidate source hash frozen', sha(ROOT / 'src/thermo_response.py') == '45c6b076ce4e90b5a00a26c39503bbcbe862f814ba960782248a8737787dfeaa')
ok('projected input hash', result['source_projected_sha256'] == sha(ROOT / 'inputs/phys09/PROJECTED_RESULTS.json'))
invariant_decimals(result)
details = {d['stage']: d for d in inp['details']}
by_stage = {d['stage']: d for d in result['rows']}
review_values = {}
for source in inp['stages']:
    name = source['stage']
    d, r = details[name], by_stage[name]
    srcpath = ROOT / f'inputs/ncp07/results/{name}/SOURCE_BOX.json'
    captured = json.loads(srcpath.read_text())
    for suffix, path in [('/SOURCE_BOX.json', srcpath), ('/NATIVE_CONSTANT_LEAVES.json', leaves_path)]:
        known = next(v for v in d['input_exports'] if v['path'].endswith(suffix))
        ok(name + ': inherited source identity ' + suffix, sha(path) == known['sha256'])
    ok(name + ': inherited first-stage flag', d['same_COMMON_first_stage'] is True)
    f = lift(captured['fHe_bits'])
    nh = lift(captured['nH_bits'])
    nhe = lift(captured['nHe_stored_bits'])
    fh = nhe / nh
    dt = lift(captured['dt_bits'])
    ok(name + ': duration', dt == {'full': 1250000000, 'first_half': 625000000}[name])
    ok(name + ': distinct normalizations retained', f != fh)
    C = 2 * lift(leaves['ev_erg_bits']) / (3 * lift(leaves['kb_bits']))
    chi, ch1, ch2 = map(lift, leaves['CHI_bits'])
    u, v, wmix = [[unpack(a) for a in source[k]] for k in ['U', 'V', 'W']]
    root = []
    for i in range(4):
        c, radius, beta, kr, X = [unpack(d[k][i]) for k in ['Banach_ball_center', 'radius', 'banach_beta', 'banach_absK_radius', 'thermal_X']]
        ok(f'{name}: centre and radius points {i}', c[0] == c[1] and radius[0] == radius[1])
        m = add(beta, kr)[1]
        ok(f'{name}: strict self-map margin {i}', m < radius[0] and m > 0)
        gi = cap((c[0] - m, c[1] + m), X)
        ok(f'{name}: Banach image inside Y {i}', c[0] - radius[1] <= gi[0] <= gi[1] <= c[1] + radius[1])
        eq(f'{name}: root image endpoint {i}', gi, r['root_image']['intervals'][i])
        root.append(gi)
    x, y1, y2, energy = root
    e = add(x, mul(fh, add(y1, mul(2, y2))))
    particles = add(1, fh, e)
    ue = add(u[0], mul(fh, add(u[1], mul(2, u[2]))))
    ve = add(v[0], mul(fh, add(v[1], mul(2, v[2]))))
    we = add(wmix[0], mul(fh, add(wmix[1], mul(2, wmix[2]))))
    thermal = div(mul(C, u[3]), particles)
    particle = neg(div(mul(C, energy, ue), sq(particles)))
    temp_direct = add(thermal, particle)
    grad = list(map(unpack, d['energy_source_Jet']['gradient']))
    projection = mul(dt, add(grad[4], *(mul(grad[j], u[j]) for j in range(4))))
    direct_energy = add(mul(chi, u[0]), mul(f * ch1, u[1]), mul(f * (ch1 + ch2), u[2]), u[3])
    gas_energy = cap(projection, direct_energy)
    remainder = add(gas_energy, mul(chi * fh - f * ch1, u[1]), mul(2 * chi * fh - f * (ch1 + ch2), u[2]))
    eff = cap(sub(chi, div(remainder, ue)), div(neg(u[3]), ue))
    temp_projected = mul(div(C, particles), sub(remainder, mul(add(chi, div(energy, particles)), ue)))
    temp = cap(temp_direct, temp_projected)
    thermal_p = mul(div(C, particles), sub(remainder, mul(chi, ue)))
    thermal = cap(thermal, thermal_p)
    share = energy[0] / (eff[1] * particles[1] + energy[0]), energy[1] / (eff[0] * particles[0] + energy[1])
    finite = r['finite_HH_response']
    for key, val in {'electron_fraction': ue, 'electron_density_cm3': mul(nh, ue), 'temperature_K': temp,
                     'thermal_part_K': thermal, 'particle_part_K': particle,
                     'particle_fraction_of_cooling': share, 'thermal_fraction_of_cooling': sub(1, share),
                     'effective_energy_eV_per_electron': eff, 'gas_energy_eV_per_H': gas_energy,
                     'pressure_per_nH_eV': mul(F(2, 3), u[3])}.items():
        eq(name + ': exact ' + key, val, finite[key])
    eq(name + ': first energy projection', projection, r['energy_correlation']['projected_first_energy'])
    eq(name + ': residual heat/electron identity', remainder, r['energy_correlation']['Uw_plus_chi_Ue'])
    eq(name + ': direct energy projection', direct_energy, r['energy_correlation']['direct_first_energy'])
    ok(name + ': all new signs', ue[0] > 0 and temp[1] < 0 and gas_energy[1] < 0 and eff[0] > chi and we[1] < 0)
    wt = unpack(d['temperature_mixed_K'])
    eq(name + ': mixed T reused unchanged', wt, r['birth_and_mixed']['temperature_mixed_K_REUSED_PHYS09'])
    eq(name + ': mixed electron', we, r['birth_and_mixed']['electron_mixed_NEW_LINEAR_READOUT'])
    eq(name + ': b0 temperature', sub(temp, wt), finite['temperature_b0_K'])
    suppression = div(wt, neg(temp))
    eta = suppression[0] / (1 + suppression[0]), suppression[1] / (1 + suppression[1])
    eq(name + ': suppression b1', suppression, r['birth_and_mixed']['temperature_suppression_relative_to_b1'])
    eq(name + ': suppression b0', eta, r['birth_and_mixed']['temperature_suppression_relative_to_b0'])
    vt = sub(div(mul(C, v[3]), particles), div(mul(C, energy, ve), sq(particles)))
    birth_e = div(v[3], ve)
    mean_e = div(energy, particles)
    for key, val in {'birth_only_electron_response': ve, 'birth_only_temperature_response_K': vt,
                     'birth_only_thermal_energy_response': v[3], 'birth_energy_per_extra_electron': birth_e,
                     'mean_thermal_energy_per_particle': mean_e}.items():
        eq(name + ': ' + key, val, r['birth_and_mixed'][key])
    ok(name + ': birth adds energy while cooling', v[3][0] > 0 and ve[0] > 0 and birth_e[1] < mean_e[0] and vt[1] < 0)
    Z = add(1, y1, mul(2, y2))
    uz = add(u[1], mul(2, u[2]))
    pf = add(1, x, mul(f, Z))
    ph = add(1, x, mul(fh, Z))
    dp_f = add(u[0], mul(f, uz))
    dp_h = add(u[0], mul(fh, uz))
    den = mul(pf, ph)
    offset = div(mul(-C * (f - fh), energy, Z), den)
    derivative = mul(-C * (f - fh), sub(div(add(mul(u[3], Z), mul(energy, uz)), den),
                    div(mul(energy, Z, add(mul(dp_f, ph), mul(pf, dp_h))), sq(den))))
    bridge = r['normalization_readout_bridge']
    eq(name + ': factored temperature offset', offset, bridge['pointwise_temperature_offset_K'])
    eq(name + ': factored finite response bridge', derivative, bridge['finite_HH_temperature_difference_K'])
    eq(name + ': electron response bridge', mul(f - fh, uz), bridge['finite_electron_readout_difference'])
    eq(name + ': finite response absolute bound', atom(max(abs(derivative[0]), abs(derivative[1]))), bridge['finite_HH_temperature_abs_bound_K'])
    review_values[name] = {'temperature_K': sdisp(temp), 'electron_fraction': sdisp(ue),
                           'gas_energy_eV_per_H': sdisp(gas_energy), 'chi_eff_eV': sdisp(eff),
                           'particle_share': sdisp(share), 'birth_energy_eV': sdisp(birth_e),
                           'mean_thermal_energy_eV': sdisp(mean_e), 'bridge_abs_K': float(max(map(abs, derivative)))}

# Independent exact analytic cases use a four-slot algebraic Jet. This differs
# from the candidate's explicit readout derivative implementation and needs no CAS.
def jc(x):
    return F(x), F(0), F(0), F(0)

def ja(*js):
    return tuple(sum((j[k] for j in js), F(0)) for k in range(4))

def jm(a, b):
    return (a[0]*b[0], a[1]*b[0]+a[0]*b[1], a[2]*b[0]+a[0]*b[2],
            a[3]*b[0]+a[1]*b[2]+a[2]*b[1]+a[0]*b[3])

def ji(a):
    return 1/a[0], -a[1]/a[0]**2, -a[2]/a[0]**2, 2*a[1]*a[2]/a[0]**3-a[3]/a[0]**2

def jd(a, b):
    return jm(a, ji(b))

P, uu, aa, vv, w0, cc = F(7,3), F(2,5), F(1,7), F(3,11), F(14), F(7,2)
l, b = F(2,7), F(3,11)
part = P + uu*l
Tj = jm(jc(cc), jd((w0-aa*l+vv*b, -aa, vv, F(0)), (part, uu, F(0), F(0))))
ok('mixed T requires Hessian cross term', Tj[3] == -cc*uu*vv/part**2)
def tf(l, b):
    return cc*(w0-aa*l+vv*b)/(P+uu*l)
ok('mixed finite T exact formula', tf(1,1)-tf(1,0)-tf(0,1)+tf(0,0) == -cc*uu*vv/(P*(P+uu)))
ok('He-response counterexample finite sign', F(999,1240)-F(25,32) == F(121,4960))
ok('four gas signs do not fix mixed T sign', F(184,107)-F(35,32)-F(100,37)+F(20,11) == -F(360439,1393568))
K = F(11,3)
energyj = jd(jc(K), (part, uu, F(0), F(0)))
A, B = -cc*energyj[1]/part, cc*energyj[0]*uu/part**2
ok('nonconstant cooling family has exact half share', A == B and B > 0)
gj = [(F(9,10), F(1,100), F(3,100), F(-1,900)),
      (F(3,10), F(-1,1000), F(1,100), F(1,2000)),
      (F(3,5), F(1,2000), F(-1,500), F(-1,4000)),
      (F(27,2), F(-3,20), F(1,20), F(1,10000))]
ff, fh = F(83,1000), F(829,10000)
zj = ja(jc(1), gj[1], jm(jc(2), gj[2]))
ppfj = ja(jc(1), gj[0], jm(jc(ff), zj))
pphj = ja(jc(1), gj[0], jm(jc(fh), zj))
diffj = ja(jm(jc(cc), jd(gj[3], ppfj)), jm(jc(-cc), jd(gj[3], pphj)))
factoredj = jm(jc(-cc*(ff-fh)), jd(jm(gj[3], zj), jm(ppfj, pphj)))
ok('normalization bridge equality through mixed derivative', diffj == factoredj)
w, uw, z, uz, ppf, pph, upf, uph = gj[3][0], gj[3][1], zj[0], zj[1], ppfj[0], pphj[0], ppfj[1], pphj[1]
manual = -cc*(ff-fh)*((uw*z+w*uz)/(ppf*pph)-w*z*(upf*pph+ppf*uph)/(ppf*pph)**2)
ok('normalization lambda bridge differentiation', diffj[1] == manual)
Tj = jm(jc(cc), jd(gj[3], pphj))
ue, ve, we = pphj[1], pphj[2], pphj[3]
expected_mixed = cc*(gj[3][3]/pph-w*we/pph**2-(uw*ve+gj[3][2]*ue)/pph**2+2*w*ue*ve/pph**3)
ok('temperature full mixed derivative formula', Tj[3] == expected_mixed)

receipt = {'schema': 'WU088_HH_PHYS13_INDEPENDENT_ARITHMETIC_V1', 'status': 'PASS',
           'candidate_imported_or_executed': False, 'historical_source_or_solver_rerun': False,
           'checks_count': len(checks), 'checks': checks, 'independent_values_binary64_display_only': review_values,
           'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in [ROOT / 'SCIENTIFIC_CONTRACT.md', ROOT / 'src/thermo_response.py',
                           ROOT / 'inputs/phys09/PROJECTED_RESULTS.json', ROOT / 'results/thermo_v2/THERMO_RESULTS.json',
                           ROOT / 'results/thermo_v2/SUMMARY.json', ROOT / 'evidence/thermo_v2/EXECUTION.json', leaves_path,
                           ROOT / 'inputs/ncp07/results/full/SOURCE_BOX.json', ROOT / 'inputs/ncp07/results/first_half/SOURCE_BOX.json']},
           'script_sha256': sha(Path(__file__)), 'elapsed_wall_s': time.perf_counter() - started}
(OUT / 'INDEPENDENT_ARITHMETIC.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': receipt['status'], 'checks_count': len(checks), 'values': review_values,
                  'elapsed_wall_s': receipt['elapsed_wall_s']}, indent=2))
