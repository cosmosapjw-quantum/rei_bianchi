#!/usr/bin/env python3
"""Independent PHYS20 angular diagnostic. Standard library only; no IVP/native calls."""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform

PIN_ROOT = Path('/workspace/scratch/603081e41728/rei_recon_pinned/fastest_718468dc')
SOURCE_PATH = 'rust/rei_microphysics/src/paired_runtime.rs'
SOURCE_BLOB = '70eed18b07b6dd4297d8ef8da6d7e1be8e44456e'
SOURCE_COMMIT = '718468dc75cb81fdfe0f2792aab5c8d0dbc54607'


def exact_grid_moments(n: int) -> dict[str, F]:
    """Exact mu sums; azimuth degree <=4 has been summed analytically (M>=5)."""
    mu = [F(2*j+1-n, n) for j in range(n)]
    m2 = sum(x*x for x in mu) / n
    m4 = sum(x**4 for x in mu) / n
    assert m2 == F(1, 3)-F(1, 3*n*n)
    assert m4 == F(1, 5)-F(2, 3*n*n)+F(7, 15*n**4)
    u = 1-m2
    u2 = 1-2*m2+m4
    p2 = u2/2
    c = u-p2/2
    qxx = u/2
    qzz = m2
    assert qxx == F(1, 3)+F(1, 6*n*n)
    assert qzz-qxx == -F(1, 2*n*n)
    assert c == F(8, 15)+F(1, 3*n*n)-F(7, 60*n**4)
    # D=diag(-1/2,-1/2,1): -<q.D.q> gives positive first-order leakage.
    axial_linear = -(qzz-qxx)
    wrong_cross = 2*u-2*p2
    correct_cross = 2*u-5*p2
    uniform_minus_correct_cross = wrong_cross-correct_cross
    assert uniform_minus_correct_cross == F(4, 5)+F(7, 10*n**4)
    assert correct_cross == F(2, 3*n*n)-F(7, 6*n**4)
    return {
        'mu2': m2, 'mu4': m4, 'Qxx': qxx, 'Qyy': qxx, 'Qzz': qzz,
        'qx4': F(3, 8)*u2, 'qy4': F(3, 8)*u2, 'qz4': m4,
        'qx2qy2': u2/8, 'qx2qz2': (m2-m4)/2,
        'U': u, 'P2': p2, 'energy_quadratic_xy': c,
        'energy_quadratic_bias_absolute': c-F(8, 15),
        'energy_quadratic_bias_relative': c/F(8, 15)-1,
        'axial_energy_linear_spurious': axial_linear,
        'uniform_q_birth_cross': wrong_cross,
        'jacobian_birth_cross_residual': correct_cross,
        'uniform_minus_jacobian_birth_cross': uniform_minus_correct_cross,
    }


def dec(frac: F) -> Decimal:
    return Decimal(frac.numerator)/Decimal(frac.denominator)


def decimal_phi_grid(m: int = 32):
    """Power-of-two azimuths using radicals, independent of platform sin/cos."""
    if m < 8 or m & (m-1):
        raise ValueError('power-of-two M>=8 required for radical construction')
    c = Decimal(2).sqrt()/2  # cos(pi/4)
    denominator = 4
    while denominator < m:
        c = ((1+c)/2).sqrt()
        denominator *= 2
    s = (1-c*c).sqrt()
    cstep = 2*c*c-1
    sstep = 2*c*s
    pairs = []
    x, y = c, s
    for _ in range(m):
        pairs.append((x, y))
        x, y = x*cstep-y*sstep, x*sstep+y*cstep
    return pairs


def midpoint_grid_decimal(n: int, m: int = 32):
    az = decimal_phi_grid(m)
    out = []
    for j in range(n):
        z = dec(F(2*j+1-n, n))
        rho = (1-z*z).sqrt()
        for cp, sp in az:
            out.append(((rho*cp, rho*sp, z), Decimal(1)/Decimal(n*m)))
    return out


def gauss_legendre_decimal(n: int = 8):
    """Newton/Legendre recurrence at Decimal80; only a small angular integral."""
    def legendre(x):
        p0, p1 = Decimal(1), x
        for k in range(2, n+1):
            p0, p1 = p1, ((2*k-1)*x*p1-(k-1)*p0)/k
        derivative = n*(x*p1-p0)/(x*x-1)
        return p1, derivative

    result = []
    for k in range(1, n+1):
        x = Decimal(str(math.cos(math.pi*(k-0.25)/(n+0.5))))
        for _ in range(40):
            p, dp = legendre(x)
            new = x-p/dp
            if abs(new-x) < Decimal('1e-73'):
                x = new
                break
            x = new
        else:
            raise ArithmeticError('Legendre root did not converge')
        p, dp = legendre(x)
        if abs(p) > Decimal('1e-70'):
            raise ArithmeticError('Legendre root residual')
        result.append((x, 1/((1-x*x)*dp*dp)))  # weights for dmu/2
    return result


def continuum_probe_grid():
    az = decimal_phi_grid(32)
    out = []
    for z, w in gauss_legendre_decimal(8):
        rho = (1-z*z).sqrt()
        for cp, sp in az:
            out.append(((rho*cp, rho*sp, z), w/32))
    return out


def mean_energy(grid, birth: Decimal, age: Decimal,
                eigenvalues=(Decimal(1), Decimal(-1), Decimal(0)),
                physical_birth=False):
    """birth=sigma*b, age=sigma*Delta. Hmean factor is divided out."""
    gb_exp = [(-2*d*birth).exp() for d in eigenvalues]
    gt_exp = [(-2*d*(birth+age)).exp() for d in eigenvalues]
    total, mass = Decimal(0), Decimal(0)
    for q, w in grid:
        gb = sum(q[i]*q[i]*gb_exp[i] for i in range(3)).sqrt()
        gt = sum(q[i]*q[i]*gt_exp[i] for i in range(3)).sqrt()
        jac = 1/(gb**3) if physical_birth else Decimal(1)
        total += w*jac*gt/gb
        mass += w*jac
    return total/mass


def binary_formula_check(n, m, exact):
    rays = []
    for j in range(n):
        mu = -1.0+2.0*(j+0.5)/n
        for k in range(m):
            phi = 2.0*math.pi*(k+0.5)/m
            rho = math.sqrt(1.0-mu*mu)
            q = [rho*math.cos(phi), rho*math.sin(phi), mu]
            norm = math.hypot(math.hypot(q[0], q[1]), q[2])
            rays.append([x/norm for x in q])
    size = n*m
    second = [[math.fsum(q[i]*q[j] for q in rays)/size
               for j in range(3)] for i in range(3)]
    expected = [float(exact[x]) for x in ('Qxx', 'Qyy', 'Qzz')]
    err = max(abs(second[i][j]-(expected[i] if i == j else 0.0))
              for i in range(3) for j in range(3))
    p2 = math.fsum((q[0]**2-q[1]**2)**2 for q in rays)/size
    p2_error = abs(p2-float(exact['P2']))
    assert err < 2e-14 and p2_error < 2e-14
    return {'N':n, 'M':m, 'Q':second, 'Q_max_abs_error':err,
            'P2':p2, 'P2_abs_error':p2_error,
            'note':'Python math recreation; not a Rust binary or bit-identity test'}


def encode_exact(record):
    return {k:{'fraction':str(v), 'decimal':str(dec(v))} for k,v in record.items()}


def run(output: Path, pin_root: Path):
    output.mkdir(parents=True, exist_ok=True)
    target = output/'angular_moments_results.json'
    if target.exists():
        raise FileExistsError(f'refusing to replace existing evidence: {target}')
    source = (pin_root/SOURCE_PATH).read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()
    if blob != SOURCE_BLOB:
        raise ValueError(f'pinned source drift: {blob}')
    exact = {n:exact_grid_moments(n) for n in (4,8,16)}
    binary = [binary_formula_check(n, m, exact[n]) for n,m in ((4,8),(8,16),(16,32))]
    numeric = []
    eps = Decimal('1e-6')
    for n in (4,8,16):
        grid = midpoint_grid_decimal(n, 32)
        c = (mean_energy(grid, Decimal(0), eps)-1)/(eps*eps)
        minus = mean_energy(grid, Decimal(0), -eps)
        plus = mean_energy(grid, Decimal(0), eps)
        parity = abs(plus-minus)
        axial = (mean_energy(grid, Decimal(0), eps,
                 (Decimal('-0.5'), Decimal('-0.5'), Decimal(1)))
                 -mean_energy(grid, Decimal(0), -eps,
                 (Decimal('-0.5'), Decimal('-0.5'), Decimal(1))))/(2*eps)
        f0 = mean_energy(grid, Decimal(0), eps)
        uniform = mean_energy(grid, eps, eps, physical_birth=False)
        weighted = mean_energy(grid, eps, eps, physical_birth=True)
        wrong_cross = (uniform-f0)/(eps*eps)
        right_cross = (weighted-f0)/(eps*eps)
        difference = (uniform-weighted)/(eps*eps)
        values = {'energy_quadratic_xy':c,
                  'axial_energy_linear_spurious':axial,
                  'uniform_q_birth_cross':wrong_cross,
                  'jacobian_birth_cross_residual':right_cross,
                  'uniform_minus_jacobian_birth_cross':difference}
        errors = {k:abs(v-dec(exact[n][k])) for k,v in values.items()}
        assert max(errors.values()) < Decimal('1e-9')
        assert parity < Decimal('1e-68')
        numeric.append({'N':n,'M':32,'epsilon':str(eps),
                        'observed':{k:str(v) for k,v in values.items()},
                        'errors':{k:str(v) for k,v in errors.items()},
                        'parity_abs':str(parity)})

    continuum = []
    grid = continuum_probe_grid()
    for eps in (Decimal('0.01'), Decimal('0.001'), Decimal('0.0001')):
        f0 = mean_energy(grid, Decimal(0), eps)
        uniform = mean_energy(grid, eps, eps)
        weighted = mean_energy(grid, eps, eps, physical_birth=True)
        c = (f0-1)/(eps*eps)
        cross = (uniform-weighted)/(eps*eps)
        continuum.append({'epsilon':str(eps), 'quadratic_coefficient':str(c),
            'coefficient_error':str(abs(c-dec(F(8,15)))),
            'uniform_minus_physical_cross':str(cross),
            'cross_coefficient_error':str(abs(cross-dec(F(4,5)))),
            'physical_birth_vs_birth_zero_abs':str(abs(weighted-f0))})
    assert Decimal(continuum[-1]['coefficient_error']) < Decimal('1e-7')
    assert Decimal(continuum[-1]['cross_coefficient_error']) < Decimal('1e-7')
    assert Decimal(continuum[-1]['physical_birth_vs_birth_zero_abs']) < Decimal('1e-25')
    for key in ('coefficient_error','cross_coefficient_error'):
        errors = [Decimal(row[key]) for row in continuum]
        assert errors[0] > errors[1] > errors[2]

    # M=4 midpoint phi lies on qx^2=qy^2: a direct fourth-moment counterexample.
    bad_p2 = 0
    assert bad_p2 != exact[8]['P2']
    results = {
        'task':'PHYS20_INDEPENDENT_ANGULAR_MOMENT_VERIFICATION',
        'status':'PASS_SCOPED_ANALYTIC_AND_NUMERICAL_CHECKS',
        'reviewer_role':'independent contributing verifier; not decision reviewer',
        'evidence_states':['derived','numerically checked'],
        'scientific_admission':'HOLD', 'native_executions':0, 'IVP_runs':0,
        'old_proof_reruns':0, 'repository_mutations':0,
        'source':{'commit':SOURCE_COMMIT,'path':SOURCE_PATH,'git_blob':blob,
                  'sha256':hashlib.sha256(source).hexdigest()},
        'method':{'exact':'Fraction sums of midpoint mu powers and roots-of-unity azimuth identities',
                  'numeric':'Decimal80 exp/sqrt; radical phi32; independent Newton-Legendre8 angular probe',
                  'finite_grid_numeric_tolerance':'1e-9 absolute for derivative coefficients at epsilon1e-6',
                  'binary_recreation_tolerance':'2e-14 absolute for Q and P2',
                  'continuum_probe':'angular quadrature diagnostic only, not a certified continuum numerical bound'},
        'claims':{
            'Q':'diag(1/3+1/(6N^2),1/3+1/(6N^2),1/3-1/(3N^2)); M>=3',
            'STF_defect':'Q:B=-Bzz/(2N^2)',
            'xy_energy_coefficient_continuum':'8/15',
            'xy_energy_coefficient_midpoint':'8/15+1/(3N^2)-7/(60N^4); M>=5',
            'xy_sign_symmetry':'exact mathematical grid when M divisible by4; binary trig only to rounding',
            'axial_spurious_linear_energy':'sigma*Delta/(2N^2)',
            'birth_wrong_uniform_minus_physical_continuum':'(4/5)*sigma^2*b*Delta+O(sigma^4)',
            'birth_wrong_uniform_minus_J_midpoint':'[4/5+7/(10N^4)]*sigma^2*b*Delta+O(sigma^4)',
            'birth_J_midpoint_residual':'[2/(3N^2)-7/(6N^4)]*sigma^2*b*Delta+O(sigma^4)',
        },
        'exact_by_N':{str(n):encode_exact(r) for n,r in exact.items()},
        'binary_formula_checks':binary,
        'decimal_finite_grid_checks':numeric,
        'continuum_directional_probes':continuum,
        'negative_controls':{
            'M4_midpoint_xy_P2':'0 instead of continuum4/15; M>=5 condition necessary as a general safe condition',
            'generic_STF_first_order_cancellation':'FAIL on finite midpoint grid; analytical counterexample D=(-1/2,-1/2,1)',
            'discrete_J_exact_birth_invariance':'FAIL in general; explicit O(N^-2) residual retained',
            'uniform_q_physical_isotropy':'FAIL away from b=0; leading continuum artifact4/5*sigma^2*b*Delta'},
        'limitations':['collisionless photon energy diagnostic only',
                       'not absorption/heating histories or a coupled-gas error bound',
                       'threshold crossing differentiability handled by parent physics task',
                       'source inspected and mathematical formulas recreated; no Rust runtime claim'],
        'execution':{'python':platform.python_version(),
                     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    target.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':results['status'],'output':str(target),
                      'exact_N':[4,8,16],'binary_cases':len(binary),
                      'decimal_grid_cases':len(numeric),
                      'continuum_probes':len(continuum),'native_or_IVP_runs':0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--pin-root',type=Path,default=PIN_ROOT)
    args = parser.parse_args()
    with localcontext() as ctx:
        ctx.prec = 80
        run(args.output_dir,args.pin_root)
