"""One new arithmetic analysis of frozen source exports; no source evaluation.

Reference-only Banach/Neumann inequalities and source directional witnesses.
There is no nonlinear point iteration, native callback, or certificate issuer.
"""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from certified_interval import I
from hh_source_box import (family_from_json, parse_interval as pi,
                           interval_json as ij, CHI, SOURCE_PER_H_S)

TERMS = 4
OUT = ROOT/'results/SOURCE_ANALYSIS.json'
checks = []


def check(condition, label):
    checks.append({'label': label, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(label)


def dot(a, b):
    return sum((x*y for x,y in zip(a,b,strict=True)), I(0))


def matvec(a, v):
    return [dot(row, v) for row in a]


def add(a, b):
    return [x+y for x,y in zip(a,b,strict=True)]


def intervals(xs):
    return [ij(x) for x in xs]


def load_jet(j):
    return {'v': pi(j['value']), 'g': [pi(z) for z in j['gradient']],
            'h': [[pi(z) for z in row] for row in j['hessian']]}


def enclosed_linear_solution(Q, s, radii, gamma):
    """A^-1 s = sum(k=0..3) Q^k s + tail, ||tail||r <= gamma^4 ||s||r/(1-gamma)."""
    norm = max(z.mag()/r for z,r in zip(s,radii,strict=True))
    tail_norm = gamma**TERMS * norm/(1-gamma)
    term = list(s)
    total = list(s)
    for _ in range(1, TERMS):
        term = matvec(Q, term)
        total = add(total, term)
    ans = [z+I(-r*tail_norm, r*tail_norm) for z,r in zip(total,radii,strict=True)]
    return ans, {'terms': TERMS, 'rhs_weighted_norm_upper': ij(I(norm)),
                 'tail_weighted_norm_upper': ij(I(tail_norm)),
                 'tail_formula': 'gamma^4 * norm_r(rhs) / (1-gamma)'}


def stage_analysis(name):
    base = ROOT/'results'/name
    paths = [base/n for n in ('family.json','source_box.json','source_centre.json','run_summary.json')]
    family_data, data, centre, run = [json.loads(p.read_text()) for p in paths]
    family = family_from_json(family_data)
    x = [pi(z) for z in data['gas_box']]
    radii = [(z.hi-z.lo)/2 for z in x]
    source = [load_jet(z) for z in data['residual']]
    temp = load_jet(data['temperature_K'])
    particles = load_jet(data['particle_factor'])['v']
    q = load_jet(data['HH_events_per_H_s'])
    photo = [load_jet(z) for z in data['photo_rhs']]
    st = family.stage
    check(st.n_h.lo == st.n_h.hi and st.n_he_stored.lo == st.n_he_stored.hi,
          name+': point stage density leaves')
    fhat = st.n_he_stored.lo/st.n_h.lo
    ctemp = 2*st.ev.lo/(3*st.kb.lo)
    f = st.f_he.lo
    eps = F(1, 2**52)
    # Actual paired_runtime scalar endpoints: fl(FHE * (1 +- 8 eps)).
    blanket = I(F.from_float(float(f*(1-8*eps))), F.from_float(float(f*(1+8*eps))))
    check(blanket.contains(I(fhat)), name+': stored density ratio inside paired blanket')
    check(F('0.082') <= fhat <= F('0.084') and 7700 < ctemp < 7800,
          name+': outer C2 leaf conditions')
    outer = [I('0.899','0.931'),I('0.289','0.311'),I('0.589','0.611'),I('12.9','14.1')]
    p_outer = I(1)+I(fhat)+outer[0]+I(fhat)*(outer[1]+2*outer[2])
    check(F('2.10') < p_outer.lo and p_outer.hi < F('2.15'), name+': outer particle margin')
    check(outer[0].hi<1 and outer[1].hi+outer[2].hi<1 and all(z.lo>0 for z in outer),
          name+': strict outer simplex and thermal domain')
    outer_t = I(ctemp)*outer[3]/p_outer
    check(outer_t.lo>46200 and outer_t.hi<52372, name+': explicit outer temperature bounds')
    pminus = 1+fhat+x[0].lo+fhat*(x[1].lo+2*x[2].lo)
    pplus = 1+fhat+x[0].hi+fhat*(x[1].hi+2*x[2].hi)
    exact_t = I(ctemp*x[3].lo/pplus, ctemp*x[3].hi/pminus)
    check(temp['v'].contains(exact_t), name+': exported T contains independent corner extrema')
    check(all(pi(z).lo>=1 for z in data['photon_denominators']), name+': all D >= 1')
    check(all(row[1]==I(0) and row[2]==I(0) for row in family.sigma), name+': HI-only photo grid')
    active=[]
    for j,(e,sig,nb,bb) in enumerate(zip(family.energies,family.sigma,family.nbar,family.birth,strict=True)):
        if nb.hi>0 or bb.hi>0:
            check(e<=13.7, name+f': positive stock support node {j}')
        if sig[0].hi>0 and (nb.hi>0 or bb.hi>0):
            heat = F.from_float(float(e)-CHI[0])
            check(heat==F.from_float(e)-F.from_float(CHI[0]), name+f': exact active heat subtraction {j}')
            check(0<heat<F('0.102'), name+f': active low excess energy {j}')
            active.append((j,heat))
    check(bool(active), name+': nonempty active HI stock')
    threshold = x[3]/particles
    maximum_heat = max(z[1] for z in active)
    check(threshold.lo>6 and threshold.lo>maximum_heat, name+': photon temperature decrease condition')
    check(q['v'].lo>0 and all(q['g'][i].hi<0 for i in range(3)) and q['g'][3].lo>0,
          name+': HH gas derivative signs')
    H=[q['v'],I(0),I(0),-I(CHI[0])*q['v']]
    dtH=dot(temp['g'][:4],H)
    dtphoto=dot(temp['g'][:4],[z['v'] for z in photo])
    check(dtH.hi<0 and dtphoto.hi<0 and photo[3]['v'].lo>0,
          name+': HH and photo cool temperature while photo heats w')
    check(all(z['h'][4][5]==I(0) for z in source), name+': fixed gas G_lambdab = 0')

    # Finite-stage rate is exactly the stored birth amount divided by d.
    # It is not silently equated with the unrounded mathematical S_*.
    d=I(family.dt)
    rates=[z/d for z in family.birth]
    u=I(1)-x[0]
    nu=I(1.2)+I(157800)/temp['v']
    hp=I(0); ph=I(0); ph_energy=I(0)
    xis=[]
    for j,rate in enumerate(rates):
        if rate==I(0):
            continue
        a=st.c*st.n_h*family.sigma[j][0]
        heat=I(float(family.energies[j])-CHI[0])
        den=pi(data['photon_denominators'][j])
        xi=u*nu/particles*(I(1)-heat*particles/x[3])
        check(xi.lo>0, name+f': positive HH thermal factor at birth node {j}')
        common=q['v']*a*rate
        hp=hp-common/den*(2+xi)
        ph=ph-common/den**2
        ph_energy=ph_energy-I(family.energies[j])*common/den**2
        xis.append({'node':j,'Xi':ij(xi),'B_d_rate':ij(rate),
                     'stored_birth_minus_exact_dS':ij(family.birth[j]-d*I(SOURCE_PER_H_S))})
    hp_ad=dot(q['g'][:4],[z['g'][5]/d for z in photo])
    ph_ad=dot([photo[0]['h'][i][5]/d for i in range(4)],H)
    check(hp.hi<0 and ph.hi<0 and ph_energy.hi<0 and hp_ad.hi<0 and ph_ad.hi<0,
          name+': both closed-form and exported AD source interaction witnesses negative')
    check(max(hp.lo,hp_ad.lo)<=min(hp.hi,hp_ad.hi) and max(ph.lo,ph_ad.lo)<=min(ph.hi,ph_ad.hi),
          name+': independent witness expression enclosures overlap (diagnostic only)')

    A=[z['g'][:4] for z in source]
    Q=[[I(int(i==j))-A[i][j] for j in range(4)] for i in range(4)]
    row_bounds=[sum(Q[i][j].mag()*radii[j] for j in range(4)) for i in range(4)]
    gamma=max(z/r for z,r in zip(row_bounds,radii,strict=True))
    beta=[pi(z['value']).mag() for z in centre['residual']]
    margins=[r-b-qb for r,b,qb in zip(radii,beta,row_bounds,strict=True)]
    check(gamma<1 and all(z>0 for z in margins), name+': strict uniform Banach inequalities')
    U,utail=enclosed_linear_solution(Q,[-z['g'][4] for z in source],radii,gamma)
    V,vtail=enclosed_linear_solution(Q,[-z['g'][5] for z in source],radii,gamma)
    mixed=[]
    for z in source:
        forcing=z['h'][4][5]
        forcing=forcing+dot([z['h'][i][4] for i in range(4)],V)
        forcing=forcing+dot([z['h'][i][5] for i in range(4)],U)
        forcing=forcing+sum((z['h'][i][j]*U[i]*V[j] for i in range(4) for j in range(4)),I(0))
        mixed.append(-forcing)
    W,wtail=enclosed_linear_solution(Q,mixed,radii,gamma)
    ell=[I(CHI[0]),st.f_he*I(CHI[1]),st.f_he*(I(CHI[1])+I(CHI[2])),I(1)]
    energyW=dot(ell,W)
    TW=dot(temp['g'][:4],W)+sum((temp['h'][i][j]*U[i]*V[j] for i in range(4) for j in range(4)),I(0))
    return {
        'stage':name,'dt_s':family.dt,
        'input_exports':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in paths],
        'domain':{'fhat':ij(I(fhat)),'fhat_minus_stage_f':ij(I(fhat-f)),
                  'paired_blanket':ij(blanket),'C_temperature':ij(I(ctemp)),
                  'source_T_K':ij(temp['v']),'exact_corner_T_K':ij(exact_t),
                  'open_witness_closure':intervals(outer),'outer_T_K':ij(outer_t),
                  'lower_HH_temperature_margin_K':ij(I(exact_t.lo-35000)),
                  'upper_HH_temperature_margin_K':ij(I(60000-exact_t.hi))},
        'mechanism':{'active_stock_nodes':[z[0] for z in active],
                     'maximum_heat_ev':ij(I(maximum_heat)),'w_over_p_ev':ij(threshold),
                     'DT_HH_K_per_s':ij(dtH),'DT_photo_K_per_s':ij(dtphoto),
                     'photo_w_ev_per_H_s':ij(photo[3]['v']),
                     'birth_thermal_factors':xis,
                     'H_g_PBd_x':ij(hp),'PBd_g_H_x':ij(ph),'ell_PBd_g_H':ij(ph_energy),
                     'exported_AD_H_g_PBd_x':ij(hp_ad),'exported_AD_PBd_g_H_x':ij(ph_ad),
                     'source_witness_is_actual_W':False},
        'reference_uniform_root':{'status':'STRICT_BANACH_INCLUSION_FOR_DECLARED_REFERENCE_ONLY',
            'preconditioner':'identity','radius':intervals([I(z)for z in radii]),
            'beta_component':intervals([I(z)for z in beta]),'Q_radius_component':intervals([I(z)for z in row_bounds]),
            'strict_component_margins':intervals([I(z)for z in margins]),
            'gamma_weighted_infinity_upper':ij(I(gamma)),
            'uniqueness_scope':'inside X only, for every theta and the fixed declared analytic-remap coefficient vector',
            'parameter_coverage':{'lambda':[0,1],'b':[0,1]},
            'source_C2_open_witness':'theory/SOURCE_C2_DOMAIN_KO.md plus domain checks above',
            'nonlinear_point_iterations':0,'native_root_certified':False},
        'reference_root_derivatives':{'U_dlambda':intervals(U),'V_db':intervals(V),'W_dlambdadb':intervals(W),
            'W_energy_ev_per_H':ij(energyW),'W_temperature_K':ij(TW),
            'linear_Neumann_tails':{'U':utail,'V':vtail,'W':wtail},
            'W_HII_strict_negative':W[0].hi<0,'W_energy_strict_negative':energyW.hi<0,
            'W_temperature_strict_negative':TW.hi<0,
            'finite_unit_rectangle_interaction_enclosure':intervals(W),
            'finite_energy_interaction_enclosure_ev_per_H':ij(energyW),
            'finite_temperature_interaction_enclosure_K':ij(TW),
            'finite_identity':'I = g(1,1)-g(1,0)-g(0,1)+g(0,0) = integral_0^1 integral_0^1 W dlambda db',
            'corners_or_nonlinear_roots_evaluated':0,
            'not_second_half_carried_family':True},
        'actual_native':{'source_tuple_bound':False,'root':None,'U':None,'V':None,'W':None,
                         'finite_interaction':None,'full_two_half_defect':None,'IVP':None}
    }


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    started=datetime.now(timezone.utc).isoformat()
    result=[stage_analysis(name) for name in ('full','first_half')]
    obj={'schema':'WU088_HH_PHYS07_SOURCE_DOMAIN_AND_REFERENCE_ROOT_ANALYSIS_V1',
         'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
         'stages':result,'checks':checks,'assertions':len(checks),
         'new_source_callback_evaluations':0,'new_transcendental_evaluations':0,
         'native_calls':0,'nonlinear_point_iterations':0,'old_suite_replays':0,
         'scope':'mathematical reference first-stage family; native and carried second-half remain open'}
    with OUT.open('x') as stream:
        json.dump(obj,stream,indent=2,ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({'status':'PASS','assertions':len(checks),'output':str(OUT.relative_to(ROOT)),
          'stages':[{'name':s['stage'],'gamma':s['reference_uniform_root']['gamma_weighted_infinity_upper']['display_float'],
                     'margins':[z['display_float']for z in s['reference_uniform_root']['strict_component_margins']],
                     'W':[z['display_float']for z in s['reference_root_derivatives']['W_dlambdadb']],
                     'W_energy':s['reference_root_derivatives']['W_energy_ev_per_H']['display_float'],
                     'W_T':s['reference_root_derivatives']['W_temperature_K']['display_float']}for s in result]},indent=2))


if __name__=='__main__':
    main()
