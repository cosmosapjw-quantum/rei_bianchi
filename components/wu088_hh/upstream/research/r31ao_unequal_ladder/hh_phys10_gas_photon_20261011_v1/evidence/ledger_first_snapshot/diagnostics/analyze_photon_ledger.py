"""PHYS10: new exact contractions of saved source Jets, no source/inverse replay."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exact_weighted import E, dot, bits, unbits
Z=E.point(0); O=E.point(1)
CHECKS=[]

def check(ok,label):
    CHECKS.append({'label':label,'pass':bool(ok)})
    if not ok:raise AssertionError(label)

def exact_input(obj):
    p=obj['exact']
    if set(p)!={'lo','hi'}:raise ValueError('EXACT_ENDPOINT_LAYOUT')
    z=E(Q(int(p['lo'][0]),int(p['lo'][1])),Q(int(p['hi'][0]),int(p['hi'][1])))
    s=z.serial()
    if any(s[k]!=obj[k] for k in ('lo_bits','hi_bits','sign')):raise ValueError('EXACT_DISPLAY_MISMATCH')
    if bits(float(obj['lo']))!=s['lo_bits'] or bits(float(obj['hi']))!=s['hi_bits']:raise ValueError('DISPLAY_BITS')
    return z

def jzero():return {'v':Z,'g':[Z]*7,'h':[[Z]*7 for _ in range(7)]}

def jread(obj):
    if len(obj['gradient'])!=7 or len(obj['signed_hessian'])!=7 or any(len(x)!=7 for x in obj['signed_hessian']):raise ValueError('JET_DIMENSION')
    return {'v':E.saved(obj['value']),'g':[E.saved(z)for z in obj['gradient']],'h':[[E.saved(z)for z in r]for r in obj['signed_hessian']]}

def jscale(j,a):return {'v':a*j['v'],'g':[a*x for x in j['g']],'h':[[a*x for x in r]for r in j['h']]}

def jadd(a,b):return {'v':a['v']+b['v'],'g':[x+y for x,y in zip(a['g'],b['g'],strict=True)],'h':[[x+y for x,y in zip(r,s,strict=True)]for r,s in zip(a['h'],b['h'],strict=True)]}

def jlinear(js,cs):
    out=jzero()
    for j,c in zip(js,cs,strict=True):out=jadd(out,jscale(j,c))
    return out

def bilinear(h,u,v):return sum((h[i][j]*u[i]*v[j]for i in range(4)for j in range(4)),Z)

def contract(j,u,v,w,d=O):
    if any(len(x)!=4 for x in (u,v,w)):raise ValueError('TANGENT_DIMENSION')
    terms={'feedback':d*dot(j['g'][:4],w),'hessian':d*bilinear(j['h'],u,v),
           'lambda_gradient_tail':d*dot([j['h'][i][4]for i in range(4)],v),
           'birth_gradient':d*dot([j['h'][i][5]for i in range(4)],u),
           'lambda_birth_tail':d*j['h'][4][5]}
    return sum(terms.values(),Z),terms

def intersect(a,b):
    if not a.overlap(b):raise ValueError('EMPTY_IDENTITY_INTERSECTION')
    return E(max(a.lo,b.lo),min(a.hi,b.hi))

def mag(x):return max(abs(x.lo),abs(x.hi))
def serial_terms(ts):return {k:z.serial()for k,z in ts.items()}

def semantic_cases():
    out=[]
    # Exact eliminated photon number identity at distinct positive denominators.
    for d,k,n in [(Q(1),Q(2),Q(3)),(Q(3,7),Q(2,5),Q(11,13)),(Q(1,8),Q(0),Q(0))]:
        ph=n/(1+d*k);rate=k*ph
        check(d*rate==n-ph,'toy exact eliminated photon number')
    out.append({'case':'eliminated_photon_number','samples':3})
    # N=(3+5b)/(3-lambda), E=7, gas x=lambda. Exact mixed FTC.
    rate=jzero();rate['h'][0][5]=rate['h'][5][0]=E(Q(-5,4),Q(-5,9))
    u=[O,Z,Z,Z];v=[Z]*4;w=[Z]*4
    rad,_=contract(jscale(rate,E.point(-7)),u,v,w)
    corner=lambda l,b:Q(7)*(3+5*b)/(3-l)
    finite=corner(1,1)-corner(1,0)-corner(0,1)+corner(0,0)
    check(finite==Q(35,6) and rad.contains(E.point(finite)) and rad.lo>0,'toy finite FTC photon sign')
    out.append({'case':'finite_photon_FTC','exact_interaction':E.point(finite).serial(),'uniform_mixed':rad.serial()})
    # General five-term chain rule, J=g0*g1+2*g0*lambda+3*g1*b+5*lambda*b.
    l=Q(1,3);b=Q(2,5);g0=l+b;g1=l*b
    j=jzero();j['g'][0]=E.point(g1+2*l);j['g'][1]=E.point(g0+3*b)
    j['h'][0][1]=j['h'][1][0]=O
    j['h'][0][4]=j['h'][4][0]=E.point(2)
    j['h'][1][5]=j['h'][5][1]=E.point(3)
    j['h'][4][5]=j['h'][5][4]=E.point(5)
    value,terms=contract(j,[O,E.point(b),Z,Z],[O,E.point(l),Z,Z],[Z,O,Z,Z])
    expected=2*l+8*b+7
    check(value==E.point(expected) and all(z.lo>0 for z in terms.values()),'all five observable chain-rule terms')
    out.append({'case':'full_observable_chain_rule','exact':E.point(expected).serial(),'terms':serial_terms(terms)})
    # Source capture error is a genuine nonzero rational, even when float heat=E.
    chi=Q(1,2**54);energy=Q(1);heat=Q(float(1-float(chi)))
    eps=heat+chi-energy
    check(eps==chi and eps>0,'captured heat defect retained exactly')
    out.append({'case':'nonzero_heat_capture_defect','epsilon':E.point(eps).serial()})
    tiny=Q(unbits('0000000000000001'));signed=E(-tiny,tiny)*E.point(Q(1,3))
    check(signed.lo<0<signed.hi and signed.serial()['lo_bits']=='8000000000000001' and signed.serial()['hi_bits']=='0000000000000001','signed subnormal exact propagation')
    out.append({'case':'signed_subnormal_not_clipped','interval':signed.serial()})
    # A broad interval sum cannot express a dependent cancellation; early identity can.
    a=E(1,2);wide=a+(-a);early=Z
    check(wide==E(-1,1) and wide.contains(early),'correlated ledger identity before projection')
    out.append({'case':'dependency_and_early_projection','direct':wide.serial(),'identity':early.serial()})
    bad=E.point(Q(1,3)).serial();bad['exact']['lo'][1]='0'
    rejected=[]
    for name,call in [('zero_exact_denominator',lambda:exact_input(bad)),('empty_identity',lambda:intersect(E(1,2),E(3,4))),('zero_divisor',lambda:O/E(-1,1)),('bad_tangent',lambda:contract(j,[O],v,w))]:
        try:call()
        except (ValueError,ZeroDivisionError):rejected.append(name)
    check(len(rejected)==4,'invalid input rejected without fallback')
    out.append({'case':'invalid_exact_or_identity_domain','rejected':rejected})
    return out

def stage(name,prior):
    base=ROOT/'inputs/ncp07/raw/results'/name
    src,comp,leaf,domain=[json.loads((base/n).read_text())for n in ('SOURCE_BOX.json','SOURCE_BOX_COMPONENTS.json','NATIVE_CONSTANT_LEAVES.json','C2_DOMAIN.json')]
    check(src['coordinate']=='thermal_w' and src['native_authority'] is False,name+': fixed source scope')
    check(domain['status']=='SOURCE_C2_EVIDENCED',name+': inherited C2 source chart')
    check(len(src['energy_bits'])==33 and len(comp['photo_rates'])==33 and all(len(row)==3 for row in comp['photo_rates']),name+': complete 33x3 channels')
    check(len(comp['nonphoto'])==4 and len(src['heat_bits'])==33 and all(len(row)==3 for row in src['heat_bits']),name+': nonphoto and heat layout')
    check(len(src['D'])==33 and all(E.saved(z).lo>0 for z in src['D']),name+': positive eliminated denominators')
    d=E.leaf(src['dt_bits']);f=E.leaf(src['fHe_bits']);H=E.leaf(src['Hmean_bits'])
    nh=E.leaf(src['nH_bits']);nhe=E.leaf(src['nHe_stored_bits'])
    chi=[E.leaf(x)for x in leaf['CHI_bits']];energies=[E.leaf(x)for x in src['energy_bits']]
    check(d.lo>0 and f.lo>0 and nh.lo>0 and nhe.lo>0 and H.lo>=0 and all(x.lo>0 for x in chi+energies),name+': dimensional leaf domains')
    expected_d=Q(1250000000 if name=='full'else 625000000)
    check(d==E.point(expected_d),name+': same original named stage d')
    u=[exact_input(x)for x in prior['U']];v=[exact_input(x)for x in prior['V']];w=[exact_input(x)for x in prior['W']]
    we=exact_input(prior['projected_energy'])
    check(we.hi<0,name+': reused conditional gas energy sign')
    rates=[[jread(j)for j in row]for row in comp['photo_rates']]
    nonphoto=[jread(j)for j in comp['nonphoto']]
    ell=[chi[0],f*chi[1],f*(chi[1]+chi[2]),O]
    np=jlinear(nonphoto,ell)
    wx=jzero();wx['v']=E.saved(domain['X'][3]);wx['g'][3]=O
    expansion=jscale(wx,-2*H)
    absorption=jzero();psi=jzero();eps_rows=[]
    for node,row in enumerate(rates):
        for absorber,rate in enumerate(row):
            heat=E.leaf(src['heat_bits'][node][absorber])
            epsilon=heat+chi[absorber]-energies[node]
            absorption=jadd(absorption,jscale(rate,energies[node]))
            psi=jadd(psi,jscale(rate,epsilon))
            eps_rows.append({'node':node,'absorber':absorber,'energy_bits':src['energy_bits'][node],'chi_bits':leaf['CHI_bits'][absorber],'heat_bits':src['heat_bits'][node][absorber],'epsilon':epsilon.serial()})
    open_source=jadd(jadd(np,expansion),psi)
    photon,photon_terms=contract(jscale(absorption,-O),u,v,w,d)
    total,total_terms=contract(open_source,u,v,w,d)
    parts={}
    for key,j in [('nonphoto',np),('expansion',expansion),('capture_defect',psi)]:
        val,ts=contract(j,u,v,w,d);parts[key]={'interval':val.serial(),'terms':serial_terms(ts)}
    # These are set consistency checks, not independent source-model verification.
    direct_total=we+photon
    check(direct_total.contains(total),name+': early total is inside preserved direct sum')
    photon_joint=intersect(photon,total-we)
    check(photon.contains(photon_joint) and (total-we).contains(photon_joint),name+': sound photon identity intersection')
    ratio=None;eta=mag(total)/(-we.hi)
    if photon_joint.lo>0:
        # Same-family pointwise relation, hence valid also for finite rectangle integrals.
        ratio=intersect(photon_joint/(-we),O+total/(-we))
        check(ratio.lo>0,name+': positive photon over negative gas ratio')
    totalsum=sum((exact_input(x['interval'])for x in parts.values()),Z)
    check(totalsum.contains(total),name+': linear source-part split encloses early total')
    summary={'stage':name,'units':'eV/H','same_COMMON_first_stage':True,
             'reused_gas_energy':we.serial(),'photon_energy_from_absorption':photon.serial(),
             'photon_energy_joint':photon_joint.serial(),'gas_plus_photon_direct_sum':direct_total.serial(),
             'gas_plus_photon_projected':total.serial(),'relative_imbalance_bound':E.point(eta).serial(),
             'photon_over_negative_gas_ratio':None if ratio is None else ratio.serial(),
             'finite_unit_rectangle_interaction':'same bounds by FTC in the same fixed C2 family',
             'native_authority':False,'actual_native_root_U_V_W_I':None}
    detail={'stage':name,'photon_terms':serial_terms(photon_terms),'total_terms':serial_terms(total_terms),
            'open_ledger_parts':parts,'capture_epsilon':eps_rows,
            'epsilon_nonzero_count':sum(x['epsilon']['sign']!='ZERO_CONTAINING'for x in eps_rows),
            'consumed_rate_Jets':99,'consumed_nonphoto_Jets':4,'consumed_source_interval_expressions':103*57,
            'reused_implicit_enclosures':'inputs/phys09/PROJECTED_RESULTS.json; no new inverse/root solve',
            'normalization':'photons/H and captured photon energy[eV]; no extra nH division',
            'normalization_correction':'stage f projection of original nonphoto already includes Jnorm; no extra term',
            'epsilon_definition':'exact(captured heat)+exact(CHI)-exact(node energy)'}
    return summary,detail

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='ledger_first');args=parser.parse_args()
    if not args.run_id.replace('_','').isalnum():raise ValueError('RUN_ID')
    out=ROOT/'results'/args.run_id;out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat()
    p=ROOT/'inputs/phys09/PROJECTED_RESULTS.json';data=p.read_bytes()
    check(hashlib.sha256(data).hexdigest()=='c6329fed8c411e1592bd1a0c63ebd9ca6151e81500ed1f46fb6b40f4b7758444','fixed PHYS09 result identity')
    old=json.loads(data);prior={s['stage']:s for s in old['stages']}
    check(set(prior)=={'full','first_half'},'two inherited first-stage records')
    cases=semantic_cases();summaries=[];details=[]
    for name in ('full','first_half'):
        s,d=stage(name,prior[name]);summaries.append(s);details.append(d)
    result={'schema':'WU088_HH_PHYS10_GAS_PHOTON_LEDGER_V1','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
            'stages':summaries,'details':details,'semantic_cases':cases,'checks':CHECKS,'assertions':len(CHECKS),'assertions_are_unique_tests':False,
            'new_source_callbacks':0,'new_inverse_solves':0,'new_native_root_calls':0,'historical_scientific_replays':0,'native_authority':False,
            'scope':'conditional fixed real-source family after PreBE, local absorption step; not global radiation/guard/escape/redshift conservation'}
    with (out/'LEDGER_RESULTS.json').open('x')as fp:json.dump(result,fp,indent=2);fp.write('\n')
    display=lambda x:None if x is None else [x['lo'],x['hi']]
    compact={'status':'PASS','assertions':len(CHECKS),'semantic_cases':len(cases),'stages':[{k:display(v) if isinstance(v,dict)and 'exact'in v else v for k,v in s.items()}for s in summaries]}
    with (out/'SUMMARY.json').open('x')as fp:json.dump(compact,fp,indent=2);fp.write('\n')
    print(json.dumps(compact,indent=2))

if __name__=='__main__':main()
