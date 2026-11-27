"""Single bounded PHYS08 reference run; never imports or executes native code."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from exact_weighted import E, bits, unbits, outward, weighted, dot, validate_saved_intervals

checks = []
fixtures = []
fixture_rows = []


def require(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def write_new(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')


def fixture(case_id, role, p, w, fhat, v, t, expected=None):
    # The Rust gate receives outward binary64 enclosures, not hidden rationals.
    args = [p,w,fhat,*v,t]
    bb = [a.binary_enclosure() for a in args]
    p0,w0,f0,*rest = bb
    vv,tt = rest[:4],rest[4]
    ans = weighted(p0,w0,f0,vv,tt)
    if expected is not None:
        require(ans['B'].sign()==expected,case_id+'_exact_expected_sign')
    words=[]
    for a in bb:
        s=a.serial(False)
        words.extend((s['lo_bits'],s['hi_bits']))
    fixture_rows.append(' '.join([case_id,role,*words]))
    fixtures.append({'case_id':case_id,'role':role,'input_endpoint_bits':words,
                     'oracle_B':ans['B'].serial(),'oracle_DT':ans['DT'].serial(),
                     'expected_balance_sign':ans['B'].sign(),
                     'expected_dt_sign':ans['DT'].sign(),
                     'strict_match_required':case_id!='minsubnormal_signed'})


def aggregate(rates, f, heat, selector, nodes=None):
    ids=range(len(rates)) if nodes is None else nodes
    values=[(j,[E.saved(selector(rates[j][a])) for a in range(3)]) for j in ids]
    s=[sum((v[a] for _,v in values),E.point(0)) for a in range(3)]
    return [s[0],(s[1]-s[2])/f,s[2]/f,
            sum((heat[j][a]*v[a] for j,v in values for a in range(3)),E.point(0))]


def stage_result(stage):
    base=ROOT/'inputs/ncp07/raw/results'/stage
    names=['SOURCE_BOX.json','SOURCE_BOX_COMPONENTS.json','C2_DOMAIN.json',
           'NATIVE_CONSTANT_LEAVES.json','DIRECTIONAL_VECTORS.json','PREBE.json',
           'SOURCE_DIRECTIONAL_WITNESS.json']
    docs={n:json.loads((base/n).read_text()) for n in names}
    counts={n:validate_saved_intervals(d) for n,d in docs.items()}
    identities=[{'path':str((base/n).relative_to(ROOT)),'bytes':(base/n).stat().st_size,
                 'sha256':hashlib.sha256((base/n).read_bytes()).hexdigest()} for n in names]
    s=docs['SOURCE_BOX.json']; comp=docs['SOURCE_BOX_COMPONENTS.json']
    c2=docs['C2_DOMAIN.json']; leaves=docs['NATIVE_CONSTANT_LEAVES.json']
    old=docs['DIRECTIONAL_VECTORS.json']; pre=docs['PREBE.json']
    rates=comp['photo_rates']
    require(len(rates)==33 and all(len(r)==3 for r in rates),stage+'_all_33x3_rates')
    for row in rates:
        for r in row:
            require(len(r['gradient'])==7 and len(r['signed_hessian'])==7 and
                    all(len(x)==7 for x in r['signed_hessian']),stage+'_signed_Jet_shape')
    x=[E.saved(d) for d in c2['X']]
    f=E.leaf(s['fHe_bits']); fhat=E.leaf(s['nHe_stored_bits'])/E.leaf(s['nH_bits'])
    p=1+fhat+x[0]+fhat*(x[1]+2*x[2])
    C=2*E.leaf(leaves['ev_erg_bits'])/(3*E.leaf(leaves['kb_bits']))
    t=C*x[3]/p
    require(E.saved(c2['fhat']).contains(fhat),stage+'_saved_fhat_contains_leaf_ratio')
    require(E.saved(c2['particles']).contains(p),stage+'_saved_particles_contains_exact')
    require(E.saved(c2['temperature']).contains(t),stage+'_saved_temperature_contains_exact')
    heat=[[E.leaf(a) for a in row] for row in s['heat_bits']]
    q=E.saved(s['q']['value'])
    qg=[E.saved(a) for a in s['q']['gradient'][:4]]
    chi=[E.leaf(a) for a in leaves['CHI_bits']]
    H=[q,E.point(0),E.point(0),-chi[0]*q]
    ell=[chi[0],f*chi[1],f*(chi[1]+chi[2]),E.point(1)]
    D=[E.saved(a) for a in s['D']]
    c=E.leaf(leaves['c_bits']); nH=E.leaf(s['nH_bits'])
    sig=[[E.leaf(a) for a in row] for row in s['sigma_bits']]
    require(all(row[1].lo==row[1].hi==row[2].lo==row[2].hi==0 for row in sig),stage+'_fixed_He_cross_sections_zero')
    require(q.lo>0 and (1-x[0]).lo>0,stage+'_positive_HH_domain')
    roles={}
    for role in ('P_N','P_M'):
        select=(lambda r:r['value']) if role=='P_N' else (lambda r:r['gradient'][5])
        v=aggregate(rates,f,heat,select)
        pg=[]
        for k in range(4):
            dsel=(lambda r,k=k:r['gradient'][k]) if role=='P_N' else (lambda r,k=k:r['signed_hessian'][k][5])
            pg.append(aggregate(rates,f,heat,dsel))
        # pg is stored by gas-direction column; contract into H retaining all tails.
        pgH=[sum((pg[k][a]*H[k] for k in range(4)),E.point(0)) for a in range(4)]
        hp_x=dot(qg,v)
        balance=weighted(p,x[3],fhat,v,t)
        dtC=C*balance['B']/(p*p)
        dt_grad=dot([-t/p,-fhat*t/p,-2*fhat*t/p,t/x[3]],v)
        nu=E.point(Q(1.2))+157800/t
        hp_closed=q*(-2*v[0]/(1-x[0])+nu*dtC/t)
        amount=[E.saved(g['value'] if role=='P_N' else g['gradient'][5]) for g in pre['groups']]
        ph_closed=-q*sum((c*nH*sig[j][0]*amount[j]/(D[j]*D[j]) for j in range(33)),E.point(0))
        energy_closed=-q*sum(((heat[j][0]+chi[0])*c*nH*sig[j][0]*amount[j]/(D[j]*D[j]) for j in range(33)),E.point(0))
        ell_pgH=dot(ell,pgH)
        for key,val in [('Px',v[0]),('Pw',v[3])]:
            require(val.lo>0,stage+'_'+role+'_'+key+'_strict_positive')
        for key,val in [('B',balance['B']),('DT_C',dtC),('DT_Twp',balance['DT']),
                        ('DT_gradient',dt_grad),('HgP_x_saved_Jet',hp_x),('HgP_x_formula',hp_closed),
                        ('PgH_x_saved_Jet',pgH[0]),('PgH_x_formula',ph_closed),
                        ('ell_PgH_saved_Jet',ell_pgH),('ell_PgH_formula',energy_closed)]:
            require(val.hi<0,stage+'_'+role+'_'+key+'_strict_negative')
        require(hp_x.overlap(hp_closed),stage+'_'+role+'_HgP_overlap_diagnostic_only')
        require(pgH[0].overlap(ph_closed),stage+'_'+role+'_PgH_overlap_diagnostic_only')
        require(ell_pgH.overlap(energy_closed),stage+'_'+role+'_ellPgH_overlap_diagnostic_only')
        oldmatch=None
        if role=='P_M':
            oldmatch=[E.saved(a).contains(b) for a,b in zip(old['P_M'],v)]
            require(all(oldmatch),stage+'_saved_PM_contains_exact_aggregate')
        tail32=aggregate(rates,f,heat,select,[32])
        tailB=weighted(p,x[3],fhat,tail32)['B']
        group_dpart=balance['dparts']
        weighted_heat=v[3]/group_dpart
        all_other=aggregate(rates,f,heat,select,[j for j in range(33) if j!=24])
        otherB=weighted(p,x[3],fhat,all_other)['B']
        roles[role]={
            'role':role,'source_mapping':'photo_rates.value' if role=='P_N' else 'photo_rates.gradient[5]',
            'Pg_mapping':'photo_rates.gradient[k]' if role=='P_N' else 'photo_rates.signed_hessian[k][5]',
            'P':[a.serial() for a in v], 'dparticles':group_dpart.serial(),
            'B':balance['B'].serial(), 'DT_C_B_over_p2':dtC.serial(),
            'DT_T_B_over_wp':balance['DT'].serial(),'DT_gradient_dot':dt_grad.serial(),
            'weighted_energy_per_added_particle':weighted_heat.serial(),'w_over_p':(x[3]/p).serial(),
            'HgP_x_saved_Jet':hp_x.serial(),'HgP_x_closed_formula':hp_closed.serial(),
            'PgH_saved_Jet':[a.serial() for a in pgH], 'PgH_x_closed_formula':ph_closed.serial(),
            'ell_PgH_saved_Jet':ell_pgH.serial(),'ell_PgH_closed_formula':energy_closed.serial(),
            'ell_HgP_exact':{'value':0,'basis':'ell dot (1,0,0,-CHI_H)=0 for identical exact coefficient leaves'},
            'node32_contribution_B':tailB.serial(),'all_nodes_except24_contribution_B':otherB.serial(),
            'node32_absolute_B_bound_over_strict_total_margin':(E.point(max(abs(tailB.lo),abs(tailB.hi)))/E.point(-balance['B'].hi)).serial(),
            'saved_PM_contains_exact_aggregate':oldmatch,
            'overlap_status':'DIAGNOSTIC_ONLY_NOT_IDENTITY_PROOF',
            'strict_source_direction_cooling':True,'native_implicit_authority':False}
        fixture(stage+'_'+role,role,p,x[3],fhat,v,t,'STRICT_NEGATIVE')
    node32M=E.saved(pre['groups'][32]['gradient'][5])
    require(node32M.lo<0<node32M.hi,stage+'_original_node32_signed_M_retained')
    require((heat[32][0]*p).hi >= x[3].lo,stage+'_old_per_node_heat_test_still_not_satisfied')
    return {'stage':stage,'source_input_identities':identities,'validated_intervals_by_file':counts,
            'actual_domain_X':[a.serial() for a in x],'f_stage':f.serial(),'fhat_ratio':fhat.serial(),
            'p':p.serial(),'T_K':t.serial(),'HH_q':q.serial(),'roles':roles,
            'old_node32_witness':'PRESERVED_OPEN','all_signed_rate_channels_retained':True,
            'native_authority':False}


def semantic_cases():
    p,w,f,t=map(E.point,(2,10,0,100))
    z=E.point(0)
    # Exact decimal thought experiments, then separately enclose as binary64 fixtures.
    small=[E.point(Q(101,100)),z,z,E.point(2)]
    large=[E.point(2),z,z,E.point(101)]
    require(weighted(p,w,f,small,t)['B']==E.point(Q(-61,10)),'small_hot_tail_exact_B_minus_6_1')
    require(weighted(p,w,f,large,t)['B']==E.point(182),'large_hot_tail_exact_B_182')
    require((E.point(100)*p).lo>w.hi,'hot_node_individually_fails')
    fixture('small_hot_tail','SIGNED_VECTOR',p,w,f,small,t,'STRICT_NEGATIVE')
    fixture('large_hot_tail','SIGNED_VECTOR',p,w,f,large,t,'STRICT_POSITIVE')
    fixture('zero','SIGNED_VECTOR',p,w,f,[z,z,z,z],t,'ZERO_CONTAINING')
    fixture('touch_zero','SIGNED_VECTOR',p,w,f,[E.point(1),z,z,E(4,5)],t,'ZERO_CONTAINING')
    # A signed He component is indispensable: deleting it reverses the answer.
    hevec=[E.point(1),E.point(-3),z,z]
    require(weighted(p,w,E.point(1),hevec,t)['B'].lo>0,'signed_He_component_changes_sign')
    require(weighted(p,w,E.point(1),[hevec[0],z,z,z],t)['B'].hi<0,'dropping_He_would_give_false_cooling')
    fixture('signed_He_changes_sign','SIGNED_VECTOR',p,w,E.point(1),hevec,t,'STRICT_POSITIVE')
    scaled=[a*8 for a in small]
    require(weighted(p,w,f,scaled,t)['B']==weighted(p,w,f,small,t)['B']*8,'exact_positive_scaling')
    fixture('positive_scaling','SIGNED_VECTOR',p,w,f,scaled,t,'STRICT_NEGATIVE')
    tiny=E.leaf('0000000000000001')
    fixture('minsubnormal_signed','SIGNED_VECTOR',p,w,E.point(1),[tiny,-tiny,tiny,z],t,'STRICT_NEGATIVE')
    errors=[]
    actions=[('reversed',lambda:E(2,1)),('nonfinite',lambda:unbits('7ff0000000000000')),
             ('nan',lambda:unbits('7ff8000000000001')),('p_zero',lambda:weighted(z,w,f,small,t)),
             ('w_zero',lambda:weighted(p,z,f,small,t)),('f_negative',lambda:weighted(p,w,E.point(-1),small,t)),
             ('T_zero',lambda:weighted(p,w,f,small,z)),('zero_divisor',lambda:p/E(-1,1)),
             ('display_overflow',lambda:E.point(2**2000).serial())]
    for name,fn in actions:
        try:
            fn()
        except (ValueError,OverflowError) as exc:
            errors.append({'case':name,'exception':type(exc).__name__,'reason':str(exc)})
        else:
            raise AssertionError('expected rejection: '+name)
    require(len(errors)==len(actions),'explicit_invalid_inputs_rejected')
    return errors


def main():
    out=ROOT/'results/weighted_first'
    out.mkdir(parents=True,exist_ok=False)
    stages=[stage_result(s) for s in ('full','first_half')]
    errors=semantic_cases()
    result={'schema':'WU088_HH_PHYS08_EXACT_WEIGHTED_SOURCE_V1','created_utc':datetime.now(timezone.utc).isoformat(),
            'arithmetic':'exact Fraction interval operations on captured binary64 bits; displays outward rounded',
            'source_stages':stages,'semantic_expected_rejections':errors,
            'checks':checks,'check_assertions':len(checks),'fixture_cases':len(fixtures),
            'execution_counts':{'new_Python_reference_runs':1,'native_bindings_present':False,
                                'fresh_PreBE':0,'fresh_residual':0,'fresh_FT03':0,'fresh_HH':0,'fresh_provider':0,
                                'fresh_root':0,'fresh_IVP':0,'historical_science_replays':0,'Rust_builds':0,'Rust_runs':0},
            'measurement_basis':'This offline Python program does not import native routines; inherited uninstrumented counters not reclassified.',
            'rust_status':'NOT_BUILT_NOT_RUN_TOOLCHAIN_ABSENT',
            'conclusion':'Both saved source roles in both first stages satisfy weighted cooling and source-level mutual HH/photo suppression.',
            'open':['native root authority','native U/V/W/I','finite gas-energy interaction','carried second-half',
                    'full/two-half defect','time and continuum remainder','full49','production']}
    write_new(out/'WEIGHTED_RESULTS.json',result)
    write_new(out/'GOLDEN_ORACLE.json',{'schema':'PHYS08_RUST_SAVED_FIXTURE_ORACLE_V1','fixtures':fixtures,
              'comparison':'Rust enclosure must contain exact rational oracle interval; compare signs separately. No equality or overlap-only pass.'})
    with (out/'GATE_INPUTS.tsv').open('x') as f:
        f.write('# case_id role p_lo p_hi w_lo w_hi fhat_lo fhat_hi vx_lo vx_hi vy1_lo vy1_hi vy2_lo vy2_hi vw_lo vw_hi T_lo T_hi\n')
        f.write('\n'.join(fixture_rows)+'\n')
    print(json.dumps({'status':'PASS','assertions':len(checks),'stages':len(stages),'fixtures':len(fixtures),
                      'source_results':[{'stage':s['stage'],'roles':{k:{'B':v['B']['hi'],'DT_hi':v['DT_C_B_over_p2']['hi'],
                            'HgP_hi':v['HgP_x_saved_Jet']['hi'],'PgH_hi':v['PgH_saved_Jet'][0]['hi']}
                            for k,v in s['roles'].items()}} for s in stages]},indent=2))


if __name__=='__main__':
    main()
