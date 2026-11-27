"""One new source-aligned PHYS11 joint group/ledger calculation; no source replay."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exact_weighted import E,dot
from joint_carry import (Z,O,KEYS,exact_input,jzero,jread,jscale,jadd,jlinear,carry,
                        cscale,cadd,csub,cmul,cquotient,total,intersect,cintersect,cserial,mag)

CHECKS=[]
def check(ok,label):
    CHECKS.append({'label':label,'pass':bool(ok)})
    if not ok:raise AssertionError(label)
def load(p):return json.loads(p.read_text())
def display(x):return [x.serial()['lo'],x.serial()['hi']]
def csum(cs):
    r=carry()
    for c in cs:r=cadd(r,c)
    return r

def semantic_cases():
    cases=[]
    # Closed two-stage rational function: x1=lambda, P1=1+b, N2=P1/(2-x1).
    l=Q(1,3);b=Q(2,5)
    incoming=carry(E.point(1+b),Z,O,Z)
    denominator=carry(E.point(2-l),-O,Z,Z)
    result=cquotient(incoming,denominator)
    expected=carry(E.point(Q(21,25)),E.point(Q(63,125)),E.point(Q(3,5)),E.point(Q(9,25)))
    check(result==expected,'two-stage rational carry closed-form derivatives')
    corner=lambda x,y:(1+Q(y))/(2-Q(x))
    finite=corner(1,1)-corner(1,0)-corner(0,1)+corner(0,0)
    check(finite==Q(1,2),'two-stage exact finite interaction')
    check(cquotient(carry(incoming['value']),denominator)['W']==Z and
          cquotient(incoming,carry(denominator['value']))['W']==Z,'resetting either incoming first derivative destroys interaction')
    cases.append({'case':'two_stage_cross_carry','carry':cserial(result),'exact_finite_interaction':E.point(finite).serial()})
    # Sum commutes with quotient only with the same ray denominator.
    a=carry(E.point(2),E.point(3),E.point(5),E.point(7))
    b2=carry(E.point(11),E.point(13),E.point(17),E.point(19))
    den=carry(E.point(23),E.point(2),E.point(3),E.point(5))
    check(cadd(cquotient(a,den),cquotient(b2,den))==cquotient(cadd(a,b2),den),'common-denominator ray lift four components')
    wrong=cadd(cquotient(a,den),cquotient(b2,carry(E.point(29),E.point(2),E.point(3),E.point(5))))
    check(wrong!=cquotient(cadd(a,b2),den),'unequal ray denominator counterexample')
    cases.append({'case':'ray_lift_and_unequal_denominator_counterexample'})
    forcing=carry(Z,Z,O,E.point(Q(2,3)))
    check(cquotient(forcing,carry(O))==forcing,'zero-stock forcing and transparent node preserved')
    cases.append({'case':'transparent_zero_stock_signed_forcing','carry':cserial(forcing)})
    # Same group sum does not determine a later ray-dependent redshift energy.
    p=(Q(1),Q(3));q=(Q(3),Q(1));weights=(Q(1,2),Q(3,4))
    check(sum(p)==sum(q) and sum(x*y for x,y in zip(p,weights))!=sum(x*y for x,y in zip(q,weights)),
          'group-only next-transport ambiguity')
    cases.append({'case':'angular_information_counterexample','equal_group':4,'later_weighted_values':['11/4','9/4']})
    # q=lambda*b has both direct partials; lambda*q=lambda^2*b has mixed 2lambda.
    qcarry=carry(E.point(l*b),E.point(b),E.point(l),O)
    hh=cmul(carry(E.point(l),O,Z,Z),qcarry)
    check(hh['W']==E.point(2*l) and hh['U']==E.point(2*l*b),'HH product retains all direct parameter terms')
    cases.append({'case':'HH_product_with_parameter_dependent_q','carry':cserial(hh)})
    # The source-derived balance observable includes a threshold graph difference.
    chi,tau,ci,rr,kin=map(Q,(2,3,5,7,11))
    derived_escape=-(chi*(ci-rr)-tau*ci-kin)
    check(derived_escape==chi*rr+kin+(tau-chi)*ci==30,'escape definition preserves possible threshold-graph mismatch')
    cases.append({'case':'escape_definition_with_threshold_difference','exact_escape':30,'threshold_difference_contribution':5})
    u=Q(1,2**53);gamma2=2*u/(1-2*u);tau=Q(3,7)
    perturb=-gamma2*tau
    actual=abs((1+tau)/(1+tau+perturb)-1)
    bound=gamma2*tau/(1+(1-gamma2)*tau)
    check(actual==bound and gamma2>0,'conditional coefficient perturbation worst endpoint')
    cases.append({'case':'conditional_value_perturbation_bound','bound':E.point(bound).serial()})
    rejected=[]
    for label,fn in [('bad_denominator',lambda:cquotient(incoming,carry(E(-1,1)))),
                     ('inconsistent_identity',lambda:intersect(E(1,2),E(3,4))),
                     ('bad_gas_layout',lambda:total(jzero(),[O],[O],[O]))]:
        try:fn()
        except ValueError:rejected.append(label)
    check(len(rejected)==3,'invalid carry domains rejected without fallback')
    cases.append({'case':'invalid_carry_domain','rejected':rejected})
    return cases

def stage(name,gasprior,ledgerprior):
    base=ROOT/'inputs/ncp07/raw/results'/name
    src,comp,leaf,domain,pre,common=[load(base/n) for n in
      ('SOURCE_BOX.json','SOURCE_BOX_COMPONENTS.json','NATIVE_CONSTANT_LEAVES.json','C2_DOMAIN.json','PREBE.json','COMMON_INPUT_SCOPE.json')]
    check(src['native_authority'] is False and src['coordinate']=='thermal_w',name+': source scope')
    check(domain['status']=='SOURCE_C2_EVIDENCED' and pre['same_object_validator'],name+': inherited source/C2 scope')
    check(len(pre['groups'])==len(src['photons'])==len(src['D'])==len(comp['photo_rates'])==33 and
          all(len(r)==3 for r in comp['photo_rates']),name+': all33 groups and99 rates')
    check(len(comp['nonphoto'])==4 and len(pre['source_weights'])==128,name+': nonphoto and angular weight layout')
    u,v,w=([exact_input(x) for x in gasprior[k]] for k in ('U','V','W'))
    we=exact_input(gasprior['projected_energy'])
    x=[E.saved(s) for s in domain['X']]
    oldgas=[E.saved(s) for s in common['old_gas']]
    d,f,H,nh,nhe=[E.leaf(src[k]) for k in ('dt_bits','fHe_bits','Hmean_bits','nH_bits','nHe_stored_bits')]
    fhat=nhe/nh
    c=E.leaf(leaf['c_bits']);chi=[E.leaf(s) for s in leaf['CHI_bits']]
    energies=[E.leaf(s) for s in src['energy_bits']]
    ell=[chi[0],f*chi[1],f*(chi[1]+chi[2]),O]
    ellhat=[chi[0],fhat*chi[1],fhat*(chi[1]+chi[2]),O]
    check(d==E.point(1250000000 if name=='full' else 625000000),name+': original named first-stage dt')
    lower=[O-x[0],f*(O-x[1]-x[2]),f*x[1]]
    check(all(z.lo>=0 for z in lower) and nh.lo>0 and f.lo>0 and d.lo>0,name+': physical opacity domain')
    in_jets=[jread(z) for z in pre['groups']]
    rates=[[jread(z) for z in row] for row in comp['photo_rates']]
    groups=[];absorbed_species=[jzero() for _ in range(3)]
    in_energy=jzero();out_energy=carry();psi=jzero();epsilon=[]
    gamma2=E.point(Q(2,2**53-2))
    gamma_bounds=[];intersection_count=0
    for node,(incoming_j,row) in enumerate(zip(in_jets,rates,strict=True)):
        incoming=total(incoming_j,u,v,w)
        rate=jlinear(row,[O]*3)
        absorption=cscale(total(rate,u,v,w),d)
        by_absorption=csub(incoming,absorption)
        coeff=[c*nh*E.leaf(z) for z in src['sigma_bits'][node]]
        k=dot(coeff,lower)
        kg=[-coeff[0],f*(-coeff[1]+coeff[2]),-f*coeff[1],Z]
        d_value=intersect(O+d*k,E.saved(src['D'][node]))
        den=carry(d_value,d*dot(kg,u),d*dot(kg,v),d*dot(kg,w))
        by_quotient=cquotient(incoming,den)
        joint=cintersect(by_absorption,by_quotient)
        joint['value']=intersect(joint['value'],E.saved(src['photons'][node]))
        intersection_count+=5
        check(all(by_absorption[t].contains(joint[t]) and by_quotient[t].contains(joint[t]) for t in KEYS),
              name+': node'+str(node)+' same-family carry intersection')
        # Source-generated exact values are nonnegative. Derivatives remain signed.
        check(joint['value'].hi>=0,name+': node'+str(node)+' value has physical support')
        for a in range(3):
            absorbed_species[a]=jadd(absorbed_species[a],row[a])
            eps=E.leaf(src['heat_bits'][node][a])+chi[a]-energies[node]
            psi=jadd(psi,jscale(row[a],eps))
            if eps!=Z:epsilon.append({'node':node,'absorber':a,'epsilon':eps.serial()})
        in_energy=jadd(in_energy,jscale(incoming_j,energies[node]))
        # Aggregate the absorption expression; do not add33 unrelated rational quotient denominators.
        # This remains a sound exact interval for the same complete outgoing spectrum.
        out_energy=cadd(out_energy,cscale(by_absorption,energies[node]))
        tau_max=(d*k).hi
        perturb=gamma2*E.point(tau_max)/(O+(O-gamma2)*E.point(tau_max))
        gamma_bounds.append(perturb)
        groups.append({'node':node,'energy_bits':src['energy_bits'][node],
                       'incoming':cserial(incoming),'absorbed':cserial(absorption),
                       'outgoing_by_absorption':cserial(by_absorption),
                       'outgoing_by_quotient':cserial(by_quotient),'outgoing_joint':cserial(joint),
                       'source_denominator':cserial(den),'conditional_native_value_relative_bound':perturb.serial()})
    absorbed=[cscale(total(j,u,v,w),d) for j in absorbed_species]
    thermal=cscale(carry(x[3],u[3],v[3],w[3]),2*d*H)
    source_n=total(jread(pre['source_n']),u,v,w)
    source_u=total(jread(pre['source_u']),u,v,w)
    q=total(jread(src['q']),u,v,w)
    hh=cscale(cmul(carry(E(0,1),O,Z,Z),q),d)
    nonphoto=[jread(z) for z in comp['nonphoto']]
    escape=cscale(total(jlinear(nonphoto,ellhat),u,v,w),-d)
    norm=jlinear(nonphoto,[a-b for a,b in zip(ell,ellhat,strict=True)])
    augmented=cscale(total(jadd(norm,psi),u,v,w),d)
    normcarry=cscale(total(norm,u,v,w),d)
    psic=cscale(total(psi,u,v,w),d)
    delta_gas=carry(dot(ell,[a-b for a,b in zip(x,oldgas,strict=True)]),dot(ell,u),dot(ell,v),we)
    incoming_energy=total(in_energy,u,v,w)
    direct=cadd(cadd(cadd(delta_gas,csub(out_energy,incoming_energy)),escape),thermal)
    joint_aug=cintersect(direct,augmented)
    check(all(direct[t].contains(augmented[t]) for t in KEYS),name+': early augmented identity inside raw direct sum')
    check(all(cadd(normcarry,psic)[t].contains(augmented[t]) for t in KEYS),name+': normalization/capture split encloses early identity')
    # Same source-family PHYS10 result reused; no previous diagnostic executed.
    p10sum=exact_input(ledgerprior['gas_plus_photon_projected'])
    p10aug=p10sum+escape['W']+thermal['W']
    check(p10aug.contains(augmented['W']),name+': augmented mixed result consistent with reused PHYS10 total')
    source_slope=E.leaf(pre['fl_dt_SOURCE_bits'])
    check(source_n['V'].contains(source_slope) and source_n['W'].lo<=0<=source_n['W'].hi,
          name+': affine source slope and exact-zero mixed contained without clipping raw tails')
    # Source_n is scalar birth ledger; do not assert independent angular intervals sum to exact1.
    weights=sum((E.saved(z) for z in pre['source_weights']),Z)
    relative=E.point(mag(augmented['W'])/(-we.hi))
    p10relative=exact_input(ledgerprior['relative_imbalance_bound'])
    reduction=E.point(mag(p10sum)/mag(augmented['W'])) if mag(augmented['W'])>0 else None
    summary={'stage':name,'units_energy':'eV/H','dt_s':float(d.lo),
             'groups_completed':33,'carry_intersections':intersection_count,
             'outgoing_group_W_sign_counts':{sgn:sum(g['outgoing_joint']['W']['sign']==sgn for g in groups)
                                           for sgn in ('STRICT_POSITIVE','STRICT_NEGATIVE','ZERO_CONTAINING')},
             'augmented_mixed_residual':display(augmented['W']),
             'derived_escape_mixed':display(escape['W']),'thermal_work_mixed':display(thermal['W']),
             'HH_events_mixed':display(hh['W']),
             'absorbed_number_mixed':display(csum(absorbed)['W']),
             'source_number_mixed_raw':display(source_n['W']),
             'source_energy_mixed_raw':display(source_u['W']),
             'normalization_mixed':display(normcarry['W']),'capture_defect_mixed':display(psic['W']),
             'relative_augmented_residual_bound':display(relative),
             'PHYS10_relative_residual_reused':display(p10relative),
             'residual_bound_reduction_vs_PHYS10':None if reduction is None else display(reduction),
             'conditional_native_value_relative_bound_max':display(E.point(max(z.hi for z in gamma_bounds))),
             'native_authority':False,'actual_native_root_U_V_W_I':None}
    detail={'stage':name,'groups':groups,
            'ledgers':{'absorbed_by_species':[cserial(a) for a in absorbed],
                       'absorbed_total':cserial(csum(absorbed)),
                       'source_number':cserial(source_n),'source_energy':cserial(source_u),
                       'HH_events':cserial(hh),'HH_threshold_heat':cserial(cscale(hh,-chi[0])),
                       'thermal_work':cserial(thermal),'source_derived_escape_star':cserial(escape)},
            'energy':{'gas_increment':cserial(delta_gas),'incoming_photons':cserial(incoming_energy),
                      'outgoing_photons_from_complete_absorption_sum':cserial(out_energy),
                      'augmented_direct_sum':cserial(direct),'augmented_early_projection':cserial(augmented),
                      'augmented_identity_intersection':cserial(joint_aug),'normalization_defect':cserial(normcarry),
                      'capture_defect':cserial(psic),'PHYS10_reused_plus_new_escape_thermal_mixed':p10aug.serial(),
                      'relative_augmented_residual_bound':relative.serial()},
            'physical_leaves':{'f':f.serial(),'fhat':fhat.serial(),'f_minus_fhat':(f-fhat).serial(),
                               'source_slope':source_slope.serial(),'source_weight_sum_interval':weights.serial(),
                               'nonzero_captured_epsilon':epsilon},
            'historical_primal_preserved':{k:common[k] for k in ('historical_HH_and_compensation','primal_ledger_comp','primal_energy_comp')},
            'coverage':{'consumed_incoming_full_Jets':33,'consumed_photo_rate_full_Jets':99,
                        'consumed_nonphoto_full_Jets':4,'consumed_source_full_Jets':2,'consumed_q_full_Jets':1,
                        'saved_signed_tails_retained':True,'saved_Hessian_symmetrization':False,
                        'structural_first_stage_incoming_lambda_mixed':'exact zero by source affine theorem; raw contraction retained',
                        'guard_and_redshift_future_derivatives':'structural zero at these first stages; actual primal arrays absent',
                        'scalar_birth_equals_grid_birth':'requires coherent normalized geometry weights; not inferred from interval sum',
                        'native_distribution_coefficient_equivalence':False,'native_value_bound_assumption':'two normal IEEE binary64 nearest multiplications without reassociation; value only',
                        'native_escape_Jet_export':False,'escape_star':'defined by -ell_fhat Fnp; no native escape authority',
                        'finite_unit_rectangle_interaction':'same early mixed interval, inherited C2 and same fixed source tuple',
                        'actual_carried_second_half':False}}
    return summary,detail

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id',default='carry_first');a=p.parse_args()
    if not a.run_id.replace('_','').isalnum():raise ValueError('RUN_ID')
    out=ROOT/'results'/a.run_id;out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat()
    p9=ROOT/'inputs/phys09/PROJECTED_RESULTS.json';p10=ROOT/'inputs/phys10/LEDGER_RESULTS.json'
    check(hashlib.sha256(p9.read_bytes()).hexdigest()=='c6329fed8c411e1592bd1a0c63ebd9ca6151e81500ed1f46fb6b40f4b7758444','fixed PHYS09 result identity')
    check(hashlib.sha256(p10.read_bytes()).hexdigest()=='5c80682180650f4c98bff6a0cec699cb04b9a52c680a019b1e522f0bb598a7cc','fixed PHYS10 result identity')
    gas={s['stage']:s for s in load(p9)['stages']};ledger={s['stage']:s for s in load(p10)['stages']}
    check(set(gas)==set(ledger)=={'full','first_half'},'same two inherited first-stage records')
    cases=semantic_cases();summaries=[];details=[]
    for name in ('full','first_half'):
        s,d=stage(name,gas[name],ledger[name]);summaries.append(s);details.append(d)
    result={'schema':'WU088_HH_PHYS11_JOINT_CARRY_V1','started_utc':started,
            'finished_utc':datetime.now(timezone.utc).isoformat(),'stages':details,
            'semantic_cases':cases,'checks':CHECKS,'assertions':len(CHECKS),'assertions_are_unique_tests':False,
            'new_source_callbacks':0,'new_inverse_solves':0,'new_native_root_calls':0,
            'historical_scientific_replays':0,'native_authority':False,
            'actual_native_root':None,'actual_native_U':None,'actual_native_V':None,'actual_native_W':None,'actual_native_I':None,
            'scope':'conditional source-aligned first-stage33group plus future ledger carry; no actual native joint state or second stage'}
    compact={'status':'PASS','assertions':len(CHECKS),'semantic_cases':len(cases),
             'stages':summaries,'new_source_callbacks':0,'new_inverse_solves':0,'new_native_root_calls':0,
             'historical_scientific_replays':0,'native_authority':False}
    for name,data in [('CARRY_RESULTS.json',result),('SUMMARY.json',compact)]:
        with (out/name).open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    print(json.dumps(compact,indent=2))

if __name__=='__main__':main()
