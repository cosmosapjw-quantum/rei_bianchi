"""New finite shell analysis with independent mpmath80 formulas and quadrature."""
import json
import math
from pathlib import Path
import mpmath as mp
import shell

UNIT = Path(__file__).resolve().parents[1]


def rel(a, b):
    return float(abs(mp.mpf(a)-b)/abs(b)) if b else float(abs(mp.mpf(a)-b))


def mp_parameters(E0, B, M):
    E0, B, M = map(lambda x: mp.mpf(str(x)), (E0, B, M))
    mu = M/(M+1); nu = (M+1)/(M+2)
    return E0, B, M, mu, nu, nu*E0-B


def independent_radial(E0, B, M, pA, direction):
    """Raw lab energy quadratic, independent of primary coefficient helpers."""
    e, bind, mass = map(lambda x: mp.mpf(str(x)), (E0, B, M))
    a = [mp.mpf(str(x)) for x in pA]
    n = [mp.mpf(str(x)) for x in direction]
    length = mp.sqrt(sum(x*x for x in n)); n = [x/length for x in n]
    P = [mp.mpf(0), mp.mpf(0), mp.sqrt(2*e)]
    r = [P[i]-a[i] for i in range(3)]
    A = (1+1/mass)/2
    Bcoef = -sum(r[i]*n[i] for i in range(3))/mass
    C = sum(x*x for x in a)/2+sum(x*x for x in r)/(2*mass)-(e-bind)
    disc = Bcoef*Bcoef-4*A*C
    if disc < 0: return [], mp.mpf(0), disc
    roots = sorted(x for x in [(-Bcoef-mp.sqrt(disc))/(2*A),
                                (-Bcoef+mp.sqrt(disc))/(2*A)] if x > 0)
    if disc == 0: return roots, None, disc
    weight = mp.sqrt(sum(x*x for x in a))*sum(x*x/mp.sqrt(disc) for x in roots)
    return roots, weight, disc


def main():
    mp.mp.dps = 80
    errors = []
    def require(value, tolerance, label):
        if not math.isfinite(value) or value > tolerance:
            errors.append({'label': label, 'error': value, 'tolerance': tolerance})
    fixtures = []
    mass = shell.PROTON_ELECTRON_MASS_RATIO
    for eV in (20, 54.4, 413.6):
        E0 = eV/shell.NOMINAL_EV_PER_HARTREE
        for mode in ('fixed0.5', 'mu/2'):
            B = 0.5 if mode == 'fixed0.5' else mass/(mass+1)/2
            e = mp.mpf(str(eV))/mp.mpf('27.2'); m = mp.mpf('1836.152673426')
            mu, nu = m/(m+1), (m+1)/(m+2)
            b = mp.mpf('0.5') if mode == 'fixed0.5' else mu/2
            eps = nu*e-b
            # Independent one-dimensional shell integral. q=qmax*sin(t)
            # removes the square-root endpoint; no primary volume call here.
            qmax = mp.sqrt(2*nu*eps)
            integral = mp.quad(lambda t: qmax**3*mp.sqrt(eps)*mp.sin(t)**2*mp.cos(t)**2,
                               [0, mp.pi/2])
            volume_quad = 16*mp.pi**2*mu*mp.sqrt(2*mu)*integral
            volume_exact = 4*mp.pi**3*(mu*nu)**mp.mpf('1.5')*eps**2
            quad_error = float(abs(volume_quad-volume_exact)/volume_exact)
            primary_volume = shell.phase_space_volume(E0, B, mass)
            volume_error = rel(primary_volume, volume_quad)
            require(quad_error, 1e-50, f'{eV}/{mode}:mp80_volume_quadrature')
            require(volume_error, 1e-11, f'{eV}/{mode}:binary64_volume')
            analytic = shell.constant_weight_moments(E0, B, mass)
            z = shell.parameters(E0, B, mass); samples = []
            max_energy = max_momentum = 0.0
            for node, weight in shell.sphere76_nodes():
                q = [math.sqrt(2*z['nu']*z['epsilon'])*x for x in node[:3]]
                k = [math.sqrt(2*z['mu']*z['epsilon'])*x for x in node[3:]]
                lab = shell.from_jacobi(E0, mass, q, k)
                # Direct lab energies and momentum, independent of shell_state.
                a, bb, Q = lab['p_A'], lab['p_B'], lab['Q']
                EA, EB, ER = sum(x*x for x in a)/2, sum(x*x for x in bb)/2, sum(x*x for x in Q)/(2*mass)
                max_energy = max(max_energy, abs(E0-B-EA-EB-ER)/max(1, E0))
                max_momentum = max(max_momentum, *(abs(a[i]+bb[i]+Q[i]-z['P'][i])/max(1, math.sqrt(2*E0)) for i in range(3)))
                samples.append((weight, a, bb, Q, EA, EB, ER))
            means = {n: math.fsum(row[0]*row[j] for row in samples) for n, j in [('EA', 4), ('EB', 5), ('ER', 6)]}
            momentum_means = {n: [math.fsum(row[0]*row[j][i] for row in samples) for i in range(3)]
                              for n, j in [('p_A', 1), ('p_B', 2), ('Q', 3)]}
            var = math.fsum(row[0]*(row[6]-means['ER'])**2 for row in samples)
            moment_errors = {n: abs(means[n]-analytic['means'][n])/max(1, abs(analytic['means'][n])) for n in means}
            moment_errors['ER_variance'] = abs(var-analytic['recoil_energy_variance'])/max(1, abs(analytic['recoil_energy_variance']))
            for n in momentum_means:
                moment_errors[n] = max(abs(momentum_means[n][i]-analytic['means'][n][i])/max(1,abs(analytic['means'][n][i])) for i in range(3))
            require(max_energy, 1e-11, f'{eV}/{mode}:energy')
            require(max_momentum, 1e-11, f'{eV}/{mode}:momentum')
            for n, error in moment_errors.items(): require(error, 1e-11, f'{eV}/{mode}:moment_{n}')
            fixtures.append({'nominal_eV': eV, 'E0_au_binary64': E0, 'binding_mode': mode,
                             'B_au_binary64': B, 'M': mass, 'epsilon_binary64': z['epsilon'],
                             'phase_volume_binary64': primary_volume,
                             'phase_volume_mp80_quadrature': mp.nstr(volume_quad, 82),
                             'phase_volume_mp80_closed': mp.nstr(volume_exact, 82),
                             'mp80_quadrature_relative_error': quad_error,
                             'binary64_volume_relative_error': volume_error,
                             'constant_weight_analytic': analytic,
                             'positive76_means': means, 'positive76_momentum_means': momentum_means,
                             'positive76_recoil_variance': var, 'moment_scaled_errors': moment_errors,
                             'max_node_energy_scaled_residual': max_energy,
                             'max_node_momentum_scaled_residual': max_momentum})
    root_cases = []
    for M, E0, B in [(1.0, 1.0, 0.5)]+[(mass, eV/27.2, 0.5) for eV in (20, 54.4, 413.6)]:
        pA = (0, 0, math.sqrt(2*E0)/4)
        for angle in (0, 20, 45, 50):
            rad = math.radians(angle); n = (math.sin(rad), 0, math.cos(rad))
            primary = shell.solve_radial(E0, B, M, pA, n)
            reference, weight, disc = independent_radial(E0, B, M, pA, n)
            if primary['status'] == 'NEAR_CAUSTIC_UNRESOLVED':
                root_cases.append({'M': M, 'E0': E0, 'theta_deg': angle, 'status': primary['status'], 'rawD': primary['raw_discriminant']})
                continue
            if len(primary['positive_roots']) != len(reference):
                errors.append({'label':'positive_root_count','M':M,'E0':E0,'angle':angle})
            root_errors = [float(abs(mp.mpf(p)-q)/max(1,abs(q))) for p,q in zip(primary['positive_roots'],reference)]
            for error in root_errors: require(error, 1e-10, 'ordinary_radial_root')
            jac_error = rel(primary['density_dEA_dOmegaA_dOmegaB'], weight) if weight else abs(primary['density_dEA_dOmegaA_dOmegaB'])
            require(jac_error, 1e-10, 'ordinary_radial_jacobian')
            root_cases.append({'M':M,'E0':E0,'theta_deg':angle,'status':primary['status'],
                               'binary64_roots':primary['positive_roots'],
                               'mp80_roots':[mp.nstr(p,82) for p in reference],
                               'root_scaled_errors':root_errors,'jacobian_relative_or_absolute_zero_error':jac_error,
                               'rawD':primary['raw_discriminant'],'mp80_discriminant':mp.nstr(disc,82)})
    # Synthetic outside-origin conditional sphere: sum both ray roots and
    # integrate after h substitution. The integrand never calls shell helpers.
    alpha = mp.mpf(2); c = 3*mp.sqrt(2)/8; rho = mp.sqrt(10)/8
    delta = c*c-rho*rho
    def folded(h):
        center_projection = mp.sqrt(h*h+delta)
        pp, pm = center_projection+h, center_projection-h
        return 2*mp.pi*(pp*pp+pm*pm)/(alpha*c*center_projection)
    fold_integral = mp.quad(folded, [0,rho])
    sphere_integral = 4*mp.pi*rho/alpha
    fold_error = float(abs(fold_integral-sphere_integral)/sphere_integral)
    require(fold_error, 1e-50, 'two_root_fold_angular_quadrature')
    fold_grid = []
    for i in range(281):
        theta = i/4; t = math.radians(theta)
        out = shell.solve_radial(1,0.5,1,(0,0,math.sqrt(2)/4),(math.sin(t),0,math.cos(t)))
        roots = out['positive_roots']
        fold_grid.append({'theta_deg':theta,'p_minus':roots[0] if len(roots)==2 else None,
                          'p_plus':roots[-1] if roots else None,
                          'radial_weight_sum':out['radial_weight_sum'],'status':out['status']})
    ratio_curves = []
    for eV in (20,54.4,413.6):
        E0=eV/27.2; infinite=4*math.pi**3*(E0-0.5)**2
        for mode in ('fixed0.5','mu/2'):
            rows=[]
            for i in range(101):
                M=10**(i/20);B=0.5 if mode=='fixed0.5' else M/(M+1)/2
                rows.append({'M':M,'ratio_to_Bhalf_infinite_mass':shell.phase_space_volume(E0,B,M)/infinite})
            ratio_curves.append({'nominal_eV':eV,'binding_mode':mode,'rows':rows})
    report={'unit':'HE-ANG-FINITEMASS-SHELL','status':'PASS' if not errors else 'FAIL',
            'precision_reference_decimal':80,'acceptance':'Frozen unchanged; binary64 is not outward certified',
            'fixtures':fixtures,'ordinary_root_reference_cases':root_cases,
            'fold':{'fixture':'M1/B0.5/E01/pA=P/4','theta_critical_deg':math.degrees(math.acos(2/3)),
                    'mp80_two_root_angular_integral':mp.nstr(fold_integral,82),
                    'mp80_regular_sphere_4pi_rho_over_alpha':mp.nstr(sphere_integral,82),
                    'relative_error':fold_error,'plot_grid':fold_grid},
            'volume_ratio_curves':ratio_curves,'errors':errors,
            'scope':'Kinematic constant-weight measure only; no amplitude/flux/spin/count prefactor/event sigma',
            'old_suite_replays':0,'physical_provider_admitted':False,'global_event_sigma':False}
    path=UNIT/'results/ANALYSIS.json';path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise RuntimeError('preserve existing analysis; no automatic replay')
    path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'fixtures':len(fixtures),'root_cases':len(root_cases),
                      'mp80_fold_relative_error':fold_error,'errors':errors}))
    return 0 if not errors else 1


if __name__=='__main__':raise SystemExit(main())
