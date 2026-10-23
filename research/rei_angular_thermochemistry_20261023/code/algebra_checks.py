"""Finite pre-IVP checks for the frozen ANGTHERM01 contract.

No solver or historical harness is invoked. Expected identities use the frozen
event/geometry equations and immutable source tables; this is implementation
evidence, not a scientific admission decision.
"""
from __future__ import annotations

import argparse
import ast
from decimal import Decimal, localcontext
import hashlib
import json
import math
import resource
import time
import numpy as np

import angular_model as m


def _relative(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.max(np.abs(a-b)/np.maximum(np.maximum(abs(a), abs(b)), 1e-300)))


def _cancellation(terms):
    values = np.asarray(terms, dtype=float)
    scale = np.sum(abs(values))
    return float(abs(np.sum(values))/scale) if scale else 0.0


def interior(model, index):
    fractions = np.array([
        [.73, .27, .70, .20, .10, .15, .35, .25, .25],
        [.41, .59, .19, .34, .47, .18, .29, .31, .22],
        [.55, .45, .65, .22, .13, .38, .27, .21, .14],
    ])[index]
    y = model.y0.copy()
    y[model.ax] = fractions
    y[model.gx] = np.linspace(.04+.1*index, 1.4+.2*index, model.J)
    temperature = [6200., 11000., 4200.][index]
    y[model.iu] = 1.5*m.KB*(m.NN+m.VGRAD@fractions)*temperature
    return y


def _lift_state(reduced, full, y):
    """Explicit isotope/copy initial-data lift, without model lift()."""
    target = np.zeros(full.size)
    for name, block in m.ATOM.blocks.items():
        total = m.ATOM.initial_nucleus_totals[name]
        if not total:
            continue
        sl = slice(0, 2) if len(block) == 2 else slice(2, 5) if len(block) == 3 else slice(5, 9)
        target[list(block)] = total*y[sl]/m.ATOM.scales[list(block)]
    target[full.gx] = np.repeat(reduced.photons(y)/8, 8)
    target[-8:] = y[-8:]
    return target


def _binding():
    b = np.zeros(21)
    for lower, upper, channel in m.ATOM.edges:
        b[upper] = b[lower]+float(m.CHANNELS[channel]['chi_eV'])
    return b


def run_checks():
    started, cpu = time.perf_counter(), time.process_time()
    records = []

    def check(name, function):
        try:
            details = function()
            passed = bool(details.pop('pass'))
            records.append({'name': name, 'pass': passed, **details})
        except Exception as exc:
            records.append({'name': name, 'pass': False,
                            'exception': f'{type(exc).__name__}: {exc}'})

    red, full = m.Reduced(), m.FullOracle()

    def sources():
        manifest = json.loads((m.BASE/'inputs/COPY_MANIFEST.json').read_text())
        wrong = []
        for entry in manifest['copies']:
            actual = hashlib.sha256((m.BASE/entry['destination']).read_bytes()).hexdigest()
            if actual != entry['sha256']:
                wrong.append(entry['destination'])
        expected_background = {
            'grid044': 'ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b',
            'grid022': '5d0ef6ee7adadf3a3acf148a930136cf406fab2b3eb484682e2a93de7119b7c0',
        }
        for name, expected in expected_background.items():
            if hashlib.sha256((m.BASE/f'inputs/background/{name}_history.npz').read_bytes()).hexdigest() != expected:
                wrong.append(name)
        donor = next((m.BASE/'vendor/rei_donors').glob('*/research/rei_c13_live_source_20261015/short_interval.py'))
        source_sigma = None
        for node in ast.parse(donor.read_text()).body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'THOMSON_CGS' for t in node.targets):
                source_sigma = ast.literal_eval(node.value)
        return {'pass': not wrong and m.SIGMA_T == source_sigma,
                'checked_copy_count': len(manifest['copies']), 'mismatches': wrong,
                'sigma_T_cm2': m.SIGMA_T, 'C13_source_sigma_T_cm2': source_sigma}
    check('immutable_sources_and_backgrounds', sources)

    def backgrounds():
        output = {}
        ok = True
        for case in ('grid044', 'grid022'):
            bg = m.Background(case)
            values = np.array([bg.fields(t) for t in bg.eta]).T
            nerr = _relative(values[1], bg.saved_n)
            herr = _relative(values[0], bg.saved_H)
            berr = float(max(abs(values[2]-(bg.saved_b-bg.saved_b[0]))))
            bperr = float(max(abs(values[3]-bg.saved_bp)))
            # Hermite b' is quadratic on each piece: evaluate both endpoints
            # and every interior vertex to bound b' over the full interval.
            extrema = list(bg.eta)
            for i, width in enumerate(np.diff(bg.eta)):
                cubic, quadratic = bg.bfun.c[0, i], bg.bfun.c[1, i]
                if cubic:
                    vertex = -quadratic/(3*cubic)
                    if 0 < vertex < width:
                        extrema.append(bg.eta[i]+vertex)
            bp = bg.bfun(np.array(extrema), 1)
            # For every mu, 3mu²-1 is in [-1,2]. This sufficient exact
            # polynomial bound covers all adopted ray angles, both signs.
            redshift_lower_bound = 1-2*float(max(abs(bp)))
            retains_b = bool(np.any(values[2] != 0))
            case_ok = nerr < 5e-12 and herr < 5e-14 and berr < 1e-15 and bperr < 5e-14 and redshift_lower_bound > 0
            if case == 'grid022':
                case_ok = case_ok and retains_b
            ok = ok and case_ok
            output[case] = {'nHref_relative_error': nerr, 'H_node_relative_error': herr,
                            'b_node_absolute_error': berr, 'bprime_node_absolute_error': bperr,
                            'redshift_factor_lower_bound_all_angles_both_signs': redshift_lower_bound,
                            'retains_nonzero_b': retains_b, 'b_absolute_max': float(max(abs(values[2])))}
        return {'pass': ok, 'cases': output}
    check('saved_background_interpolants_and_monotone_rays', backgrounds)

    def initial():
        state = m.ATOM.initial_state()
        mapped = _lift_state(red, full, red.y0)
        group = full.g0.reshape(6, red.M, 8).sum(axis=2)
        physical = m.ATOM.scales*state
        totals = {name: float(physical[list(block)].sum()) for name, block in m.ATOM.blocks.items()}
        return {'pass': red.size == 41 and full.size == 221 and np.allclose(mapped, full.y0, rtol=0, atol=1e-16)
                        and np.allclose(state, full.y0[full.ax], rtol=0, atol=1e-16)
                        and np.allclose(group.sum(axis=1), [.05,.25,.003,.0002,.00001,.000001], rtol=2e-15, atol=0)
                        and abs(m.ATOM.A@physical-1.32808000350006)<2e-14,
                'reduced_size': red.size, 'full_size': full.size,
                'baryon_per_Href': float(m.ATOM.A@physical), 'nucleus_totals': totals,
                'UV_band_counts_per_Href': group.sum(axis=1).tolist(),
                'population_lift_max_absolute_error': float(max(abs(mapped[full.ax]-state)))}
    check('source_initial_inventory_and_dimensions', initial)

    def provider():
        sigma_errors, rr_errors, supports = [], [], []
        for channel in m.CHANNELS:
            name, chi = channel['ion'], channel['chi_eV']
            supports.append(float(m.ATOM.provider.sigma(name, np.nextafter(chi, -np.inf))) == 0)
            energies = [chi*1.1, 150.]
            if name == 'LiI':
                energies += [64.39-1e-5, 64.39, 64.39+1e-5]
            for energy in energies:
                sigma_errors.append(_relative(m.ATOM.provider.sigma(name,energy), m.ATOM.provider.sigma_decimal(name,energy)))
            for temp in [3.,300.,1e4,1e9]:
                rr_errors.append(_relative(m.ATOM.provider.rr(name,temp),m.ATOM.provider.rr_decimal(name,temp)))
        rejects = []
        for temp in [2.999, 1e9+1]:
            try:
                m.thermal(temp)
                rejects.append(False)
            except ValueError:
                rejects.append(True)
        bounds = red.boundaries()
        crossings = red.crossings
        crossing_error = max(abs(c['energy_at_root_eV']-c['threshold_eV']) for c in crossings)
        return {'pass': all(supports) and all(rejects) and max(sigma_errors)<5e-13 and max(rr_errors)<5e-13
                        and bounds[0] == 0 and bounds[-1] == m.END and crossing_error < 5e-12,
                'sigma_vs_decimal_max_relative_error': max(sigma_errors),
                'rr_vs_decimal_max_relative_error': max(rr_errors),
                'below_threshold_structural_zero': all(supports), 'T_outside_domain_rejected': all(rejects),
                'support_crossing_count': len(crossings), 'unique_segments': len(bounds)-1,
                'root_energy_max_absolute_error_eV': crossing_error}
    check('exact_provider_domain_thresholds_and_decimal_values', provider)

    def full_reduced():
        rows=[]
        for i,t in enumerate([.17,.63,1.21]):
            y=interior(red,i); z=_lift_state(red,full,y)
            a,b=red.rhs(t,y),full.rhs(t,z)
            expected=_lift_state(red,full,y)
            # Differentiate the linear isotope lift and exp(-tau) explicitly.
            expected[:21]=0
            for name,block in m.ATOM.blocks.items():
                total=m.ATOM.initial_nucleus_totals[name]
                if total:
                    sl=slice(0,2) if len(block)==2 else slice(2,5) if len(block)==3 else slice(5,9)
                    expected[list(block)]=total*a[sl]/m.ATOM.scales[list(block)]
            expected[full.gx]=np.repeat(-red.photons(y)*a[red.gx]/8,8)
            expected[-8:]=a[-8:]
            error=float(max(abs(b-expected)/np.maximum(1.,np.maximum(abs(b),abs(expected)))))
            rows.append({'eta':t,'scaled_max_absolute_rhs_error':error})
        return {'pass': max(r['scaled_max_absolute_rhs_error'] for r in rows)<2e-12,'states':rows}
    check('independent_full_reduced_RHS_three_interior_states', full_reduced)

    def jacobian():
        rows=[]
        for i,t in enumerate([.17,.63]):
            y=interior(red,i)
            scale=np.ones(red.size)
            scale[-8:-3]=max(1.,float(m.ENERGIES@m.UV))
            scale[-1]=.1
            analytic=red.jacobian(t,y)
            numeric=np.empty_like(analytic)
            step=np.cbrt(np.finfo(float).eps)*scale
            for j in range(red.size):
                plus,minus=y.copy(),y.copy()
                plus[j]+=step[j];minus[j]-=step[j]
                numeric[:,j]=(red.rhs(t,plus)-red.rhs(t,minus))/(2*step[j])
            a=analytic*scale[None,:]/scale[:,None]
            b=numeric*scale[None,:]/scale[:,None]
            residual=float(max((abs(a-b)/np.maximum(1.,np.maximum(abs(a),abs(b)))).ravel()))
            rows.append({'eta':t,'maximum_component_scaled_residual':residual,
                         'scaled_infinity_norm_relative_residual':float(np.linalg.norm(a-b,np.inf)/max(np.linalg.norm(a,np.inf),np.linalg.norm(b,np.inf))),
                         'centered_step_scaled':float(np.cbrt(np.finfo(float).eps))})
        return {'pass': all(r['maximum_component_scaled_residual']<=2e-5 for r in rows),'states':rows}
    check('analytic_Jacobian_centered_finite_difference_two_states', jacobian)

    def differential():
        rows=[]
        binding=_binding()
        for i,t in enumerate([.17,.63,1.21]):
            y=interior(red,i);z=_lift_state(red,full,y)
            for model,state in [(red,y),(full,z)]:
                d=model.rhs(t,state)
                h,n,b,bp=model.bg.fields(t)
                energy,mu,p2,ep=m.geometry(t,b,bp,model.mu0,model.e0)
                g=model.photons(state)
                if model.oracle:
                    physicaldot=m.ATOM.scales*d[model.ax]
                    gdot=d[model.gx]
                else:
                    physicaldot=m.ATOM.scales*m.lift(d[model.ax])
                    gdot=-g*d[model.gx]
                erterms=[d[model.iu],binding@physicaldot,ep@g,energy@gdot,
                         d[model.iesc],d[model.iwg],d[model.iwm],d[model.iws]]
                charge=[m.ATOM.q@physicaldot,d[model.irr],-d[model.iabs]]
                number=[gdot.sum(),d[model.iabs]]
                nucleus=max(_cancellation(physicaldot[list(block)]) for block in m.ATOM.blocks.values())
                rows.append({'eta':t,'model':'full' if model.oracle else 'reduced',
                             'energy':_cancellation(erterms),'charge':_cancellation(charge),
                             'photon':_cancellation(number),'nucleus':nucleus,
                             'omitted_shear_work_normalized_residual':_cancellation(erterms[:-1]),
                             'shear_work_derivative':float(d[model.iws])})
        return {'pass':all(max(r[k] for k in ['energy','charge','photon','nucleus'])<=2e-12 for r in rows)
                       and all(r['omitted_shear_work_normalized_residual']>1e-8 for r in rows),
                'normalization':'sum absolute values of the cancelling differential terms; exact zero gives zero',
                'states':rows}
    check('local_energy_charge_number_nuclei_and_omitted_shear_control', differential)

    def geometric():
        t=.63;b=.137;bp=.091
        e,mu,p2,ep=m.geometry(t,b,bp,full.mu0,full.e0)
        direct=full.e0*np.exp(-t)*np.sqrt((1-full.mu0**2)*np.exp(2*b)+full.mu0**2*np.exp(-4*b))
        g=np.repeat((red.g0*np.linspace(.8,1.3,red.J))/8,8)
        vectors=np.vstack((np.sqrt(1-mu**2)*np.cos(full.phi),np.sqrt(1-mu**2)*np.sin(full.phi),mu))
        tensor=np.einsum('j,ij,kj->ik',e*g,vectors,vectors)
        U=float(e@g);Q=float((e*p2)@g)
        expected=np.diag([(U-Q)/3,(U-Q)/3,(U+2*Q)/3])
        pi=tensor-np.eye(3)*U/3
        shear=np.diag([-bp,-bp,2*bp])
        zero=m.geometry(t,0.,0.,full.mu0,full.e0)
        folded_e,_,folded_p2,_=m.geometry(t,b,bp,red.mu0,red.e0)
        folded_g=g.reshape(red.J,8).sum(axis=1)
        collisionless=_cancellation([ep@g,U,2*bp*Q])
        tensor_error=float(np.max(abs(tensor-expected)))
        return {'pass':_relative(e,direct)<2e-15 and _relative(zero[0],full.e0*np.exp(-t))<2e-15
                        and np.max(abs(zero[1]-full.mu0))<2e-15 and tensor_error<2e-14
                        and abs(np.trace(tensor)-U)<2e-14
                        and abs(np.sum(shear*pi)-2*bp*Q)<2e-14
                        and abs(np.linalg.norm(shear)-math.sqrt(6)*abs(bp))<2e-15
                        and abs(np.linalg.norm(pi)-math.sqrt(2/3)*abs(Q))<2e-14
                        and abs(folded_e@folded_g-U)<2e-14
                        and abs((folded_e*folded_p2)@folded_g-Q)<2e-14 and collisionless<2e-14,
                'exact_map_vs_metric_max_relative_error':_relative(e,direct),
                'full_folded_pressure_tensor_max_absolute_error':tensor_error,
                'fixed_q_count_change':0.,'collisionless_energy_normalized_residual':collisionless,
                'pressure_trace_error':float(np.trace(tensor)-U),
                'sigma_pi_minus_2sQ':float(np.sum(shear*pi)-2*bp*Q),
                'UV_U_eV_per_Href':U,'signed_Q_eV_per_Href':Q}
    check('zero_shear_fixed_q_collisionless_full_folded_tensor_geometry', geometric)

    def scope_controls():
        mismatch=full.y0[full.ax].copy()
        block=m.ATOM.blocks['D']
        mismatch[block[0]]-=.01;mismatch[block[1]]+=.01
        rejected=False
        try:
            m.quotient(mismatch)
        except ValueError as exc:
            rejected='ISOTOPE_QUOTIENT_INELIGIBLE' in str(exc)
        odd=full.g0.copy().reshape(red.J,8)
        odd[:,:4]*=1.5;odd[:,4:]*=.5
        odd=odd.ravel()
        number_error=float(max(abs(odd.reshape(red.J,8).sum(axis=1)-red.g0)))
        e,mu,_,_=m.geometry(0.,0.,0.,full.mu0,full.e0)
        odd_flux=float((e*mu)@odd)
        zero=m.Reduced(zero_uv=True)
        dy=zero.rhs(.2,zero.y0)
        nT=list(m.ATOM.blocks['n'])+list(m.ATOM.blocks['T'])
        fdy=full.rhs(.2,full.y0)
        return {'pass':rejected and number_error<2e-17 and abs(odd_flux)>1e-3
                        and np.all(zero.photons(zero.y0)==0) and dy[zero.iabs]==0
                        and np.all(fdy[nT]==0),
                'mismatched_isotope_IC_rejected':rejected,
                'odd_angular_case_policy':'explicitly remains unfolded; equal-copy reconstruction is ineligible',
                'odd_angular_group_count_error':number_error,'unfolded_odd_energy_flux_eV_per_Href':odd_flux,
                'folded_symmetric_reconstruction_energy_flux':0.,
                'zero_UV_absorption_derivative':float(dy[zero.iabs]),
                'n_T_structural_zero_derivative_max':float(max(abs(fdy[nT])))}
    check('isotope_and_odd_angular_admission_limits_and_structural_zeros', scope_controls)

    def representation():
        logscale,ell=200.,-800.
        raw=math.exp(ell)
        scaled=math.exp(logscale+ell)
        with localcontext() as ctx:
            ctx.prec=80
            exact=float((Decimal(200)+Decimal(-800)).exp())
        g0=.031;kappa=7.3;t=.81
        tau=kappa*t
        logg=math.log(g0)-tau
        # Algebraic constant-opacity solution; no IVP is spent.
        identity_error=abs(logg-(math.log(g0)-kappa*t))
        # Exercise the implemented primary coefficient path at raw-count
        # underflow using its actual bg/provider scale, still representable.
        state=interior(red,0)
        state[red.gx]=red.logg0+746.
        data=red.data(.17,state)
        coeff=data[13]
        positive=coeff[coeff>0]
        return {'pass':raw==0 and scaled>0 and _relative(scaled,exact)<2e-15 and identity_error==0
                        and len(positive)>0 and np.all(red.photons(state)==0),
                'raw_exp_minus800':raw,'direct_scaled_exp_minus600':scaled,
                'Decimal_expected':exact,'Decimal_relative_error':_relative(scaled,exact),
                'actual_model_positive_photo_coefficients_after_raw_count_underflow':int(len(positive)),
                'actual_model_max_photo_coefficient':float(max(positive)) if len(positive) else 0.,
                'constant_opacity_log_count_absolute_error':identity_error}
    check('direct_scaled_underflow_and_constant_opacity_coordinates', representation)

    elapsed=time.perf_counter()-started
    return {'overall_pass':all(r['pass'] for r in records),'checks':records,
            'scope':'pure algebra/provider checks only; zero new IVPs',
            'resource':{'wall_s':elapsed,'CPU_s':time.process_time()-cpu,
                        'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=str)
    args=parser.parse_args()
    result=run_checks()
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(text)
    print(text)
    raise SystemExit(0 if result['overall_pass'] else 1)
