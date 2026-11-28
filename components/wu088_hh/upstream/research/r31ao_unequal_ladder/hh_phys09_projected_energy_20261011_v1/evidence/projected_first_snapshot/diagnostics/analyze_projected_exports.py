"""PHYS09: one new exact arithmetic consumer of frozen NCP07 source Jets.

No source callbacks, nonlinear iteration, finite differences or native imports.
The original interval source inclusion is an explicit inherited premise.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from exact_weighted import E, bits, unbits, dot, validate_saved_intervals

ZERO = E.point(0)
ONE = E.point(1)
TERMS = 4
CHECKS = []
TSV = []


def check(ok, label):
    CHECKS.append({'label': label, 'pass': bool(ok)})
    if not ok:
        raise AssertionError(label)


def mag(z):
    return max(abs(z.lo), abs(z.hi))


def ser(z):
    return z.serial(exact=True)


def vec(v):
    return [ser(z) for z in v]


def matvec(a, v):
    return [dot(row, v) for row in a]


def matmul(a, b):
    return [[dot(row, [b[k][j] for k in range(4)]) for j in range(4)] for row in a]


def addv(a, b):
    return [x+y for x,y in zip(a,b,strict=True)]


def bilinear(h, u, v):
    return sum((h[i][j]*u[i]*v[j] for i in range(4) for j in range(4)), ZERO)


def det_point(a):
    check(all(x.lo==x.hi for row in a for x in row), 'fixed C point leaves')
    out=F(0)
    for perm in permutations(range(4)):
        inversions=sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
        term=F((-1)**inversions)
        for i,j in enumerate(perm):
            term*=a[i][j].lo
        out+=term
    return out


def inverse_action(k, c, rhs, radii, gamma):
    if gamma < 0 or gamma >= 1 or len(rhs)!=4 or any(r<=0 for r in radii):
        raise ValueError('INVALID_CONTRACTION_DOMAIN')
    cs=matvec(c,rhs)
    norm=max(mag(z)/r for z,r in zip(cs,radii,strict=True))
    tail=gamma**TERMS*norm/(1-gamma)
    term=list(cs)
    total=list(cs)
    for _ in range(1,TERMS):
        term=matvec(k,term)
        total=addv(total,term)
    result=[z+E(-r*tail,r*tail) for z,r in zip(total,radii,strict=True)]
    return result, {'terms':TERMS,'rhs_weighted_norm':ser(E.point(norm)),
                    'tail_weighted_norm':ser(E.point(tail)),
                    'component_tail_radius':vec([E.point(r*tail)for r in radii]),
                    'formula':'gamma^4 * ||C rhs||_radius / (1-gamma)'}


def jzero():
    return {'v':ZERO,'g':[ZERO]*7,'h':[[ZERO]*7 for _ in range(7)]}


def jread(obj):
    if len(obj['gradient'])!=7 or len(obj['signed_hessian'])!=7 or any(len(r)!=7 for r in obj['signed_hessian']):
        raise ValueError('JET_DIMENSION')
    return {'v':E.saved(obj['value']), 'g':[E.saved(z)for z in obj['gradient']],
            'h':[[E.saved(z)for z in row]for row in obj['signed_hessian']]}


def jscale(j, a):
    return {'v':a*j['v'],'g':[a*z for z in j['g']],
            'h':[[a*z for z in row]for row in j['h']]}


def jadd(a,b):
    return {'v':a['v']+b['v'],'g':addv(a['g'],b['g']),
            'h':[addv(x,y)for x,y in zip(a['h'],b['h'],strict=True)]}


def jlinear(js, cs):
    out=jzero()
    for j,c in zip(js,cs,strict=True):
        out=jadd(out,jscale(j,c))
    return out


def jser(j):
    return {'value':ser(j['v']),'gradient':vec(j['g']),
            'signed_hessian':[vec(r)for r in j['h']]}


def append_interval(stage,key,z):
    # Fixture inputs must be original binary64 endpoints, never a derived result.
    lo,hi=float(z.lo),float(z.hi)
    if F(lo)!=z.lo or F(hi)!=z.hi:
        raise ValueError('NON_BINARY64_GATE_INPUT')
    TSV.append((stage,key,bits(lo),bits(hi)))


def append_jet(stage,key,j):
    append_interval(stage,key+'.v',j['v'])
    for k in range(7):
        append_interval(stage,f'{key}.g.{k}',j['g'][k])
        for l in range(7):
            append_interval(stage,f'{key}.h.{k}.{l}',j['h'][k][l])


def stage_analysis(name):
    base=ROOT/'inputs/ncp07/raw/results'/name
    names=['SOURCE_BOX.json','SOURCE_BOX_COMPONENTS.json','SOURCE_CENTRE.json',
           'UNIFORM_ARITHMETIC.json','C2_DOMAIN.json','NATIVE_CONSTANT_LEAVES.json']
    paths=[base/n for n in names]
    src,comp,ctr,uniform,domain,leaves=[json.loads(p.read_text())for p in paths]
    endpoint_count=sum(validate_saved_intervals(x)for x in (src,comp,ctr,uniform,domain,leaves))
    check(src['coordinate']=='thermal_w' and src['native_authority'] is False,name+': thermal-w source scope')
    check(domain['status']=='SOURCE_C2_EVIDENCED',name+': inherited open C2 witness')
    check(uniform['status']=='CONDITIONAL_ROOT_ARITHMETIC_PASS',name+': saved conditional arithmetic evidence')
    check(len(src['G'])==4 and len(comp['nonphoto'])==4,name+': gas layout')
    check(len(comp['photo_rates'])==33 and all(len(r)==3 for r in comp['photo_rates']),name+': all 33 by 3 signed photo channels')
    check(len(src['heat_bits'])==33 and all(len(r)==3 for r in src['heat_bits']),name+': heat layout')
    g=[jread(j)for j in src['G']]
    np=[jread(j)for j in comp['nonphoto']]
    rates=[[jread(j)for j in row]for row in comp['photo_rates']]
    q=jread(src['q'])
    heat=[[E.leaf(z)for z in row]for row in src['heat_bits']]
    chi=[E.leaf(z)for z in leaves['CHI_bits']]
    d=E.leaf(src['dt_bits']); f=E.leaf(src['fHe_bits'])
    nh=E.leaf(src['nH_bits']); nhe=E.leaf(src['nHe_stored_bits'])
    hmean=E.leaf(src['Hmean_bits']); kb=E.leaf(leaves['kb_bits']); ev=E.leaf(leaves['ev_erg_bits'])
    check(all(z.lo>0 for z in [d,f,nh,nhe,kb,ev]+chi),name+': positive captured dimensional leaves')
    check(hmean.lo>=0,name+': nonnegative expansion leaf')
    x=[E.saved(z)for z in domain['X']]
    center=[E.point(v)for v in uniform['center']]
    radius=[F(v)for v in uniform['radius']]
    check(all(r>0 for r in radius),name+': strictly positive radius')
    check(all(xx.contains(cc+E(-r,r)) for xx,cc,r in zip(x,center,radius,strict=True)),name+': closed Banach ball Y inside native X')
    check(all(E.saved(z).lo>0 for z in src['D']),name+': original positive photon denominators')
    check(all(xx.lo>0 for xx in x) and x[0].hi<1 and (x[1]+x[2]).hi<1,name+': strict gas chart')
    c=[[E.point(v)for v in row]for row in uniform['fixed_C']]
    det=det_point(c)
    check(det!=0,name+': fixed C nonsingular exact determinant')
    a=[j['g'][:4]for j in g]
    ca=matmul(c,a)
    k=[[E.point(int(i==j))-ca[i][j]for j in range(4)]for i in range(4)]
    rows=[sum(mag(k[i][j])*radius[j]for j in range(4))for i in range(4)]
    gamma=max(z/r for z,r in zip(rows,radius,strict=True))
    gc=[E.saved(j['value'])for j in ctr['G']]
    cgc=matvec(c,gc)
    beta=[mag(z)for z in cgc]
    margins=[r-b-z for r,b,z in zip(radius,beta,rows,strict=True)]
    check(gamma<1 and all(z>0 for z in margins),name+': exact strict whole-family Banach inequalities')
    u,ut=inverse_action(k,c,[-j['g'][4]for j in g],radius,gamma)
    v,vt=inverse_action(k,c,[-j['g'][5]for j in g],radius,gamma)
    rhs_terms=[]
    mixed=[]
    for j in g:
        pieces={'lambda_birth':j['h'][4][5],
                'gas_lambda_V':dot([j['h'][i][4]for i in range(4)],v),
                'gas_birth_U':dot([j['h'][i][5]for i in range(4)],u),
                'gas_hessian_UV':bilinear(j['h'],u,v)}
        rhs_terms.append({key:ser(z)for key,z in pieces.items()})
        mixed.append(-sum(pieces.values(),ZERO))
    w,wt=inverse_action(k,c,mixed,radius,gamma)
    ell=[chi[0],f*chi[1],f*(chi[1]+chi[2]),ONE]
    # Exact algebra projects a coherent reaction vector before interval evaluation.
    energy_np=jlinear(np,ell)
    energy_photo=jzero()
    for jj,row in enumerate(rates):
        for aa,rate in enumerate(row):
            energy_photo=jadd(energy_photo,jscale(rate,heat[jj][aa]+chi[aa]))
    wjet=jzero(); wjet['v']=x[3]; wjet['g'][3]=ONE
    expansion=jscale(wjet,-2*hmean)
    energy=jadd(jadd(energy_np,energy_photo),expansion)
    e_terms={'feedback':d*dot(energy['g'][:4],w),
             'hessian':d*bilinear(energy['h'],u,v),
             'lambda_gradient_tail':d*dot([energy['h'][i][4]for i in range(4)],v),
             'birth_gradient':d*dot([energy['h'][i][5]for i in range(4)],u),
             'lambda_birth_tail':d*energy['h'][4][5]}
    projected=sum(e_terms.values(),ZERO)
    direct=dot(ell,w)
    # Both contain the same observable by separate identities; intersection is sound.
    check(direct.overlap(projected),name+': two energy identities have compatible enclosures (diagnostic)')
    common=E(max(direct.lo,projected.lo),min(direct.hi,projected.hi))
    H=[q['v'],ZERO,ZERO,-chi[0]*q['v']]
    leading=d*d*dot([energy['h'][i][5]for i in range(4)],H)
    ia=[[E.point(int(i==j))-a[i][j]for j in range(4)]for i in range(4)]
    u_feedback=matvec(ia,u)
    birth_remainder=d*dot([energy['h'][i][5]for i in range(4)],u_feedback)
    remainder=e_terms['feedback']+e_terms['hessian']+e_terms['lambda_gradient_tail']+e_terms['lambda_birth_tail']+birth_remainder
    leading_remainder=leading+remainder
    check(projected.overlap(leading_remainder),name+': finite source leading/remainder identity compatible (diagnostic)')
    # Temperature is an observable chain rule on the same thermal-w domain.
    fhat=nhe/nh; cp=2*ev/(3*kb)
    p=ONE+fhat+x[0]+fhat*(x[1]+2*x[2])
    check(p.lo>0,name+': positive particle factor')
    alpha=[ONE,fhat,2*fhat]
    tg=[-cp*x[3]*aa/(p*p)for aa in alpha]+[cp/p]
    th=[[ZERO]*4 for _ in range(4)]
    for i in range(3):
        for j in range(3): th[i][j]=2*cp*x[3]*alpha[i]*alpha[j]/(p*p*p)
        th[i][3]=-cp*alpha[i]/(p*p);th[3][i]=th[i][3]
    wt_temp=dot(tg,w)+bilinear(th,u,v)
    stagesummary={'stage':name,'gamma':ser(E.point(gamma)),
                  'margins':vec([E.point(z)for z in margins]),'det_C':ser(E.point(det)),
                  'U':vec(u),'V':vec(v),'W':vec(w),'direct_energy':ser(direct),
                  'projected_energy':ser(projected),'energy_terms':{key:ser(z)for key,z in e_terms.items()}}
    first=len(TSV)
    scalars={'dt':d,'fHe':f,'nH':nh,'nHe':nhe,'kb':kb,'ev':ev,'hmean':hmean}
    scalars.update({f'chi.{i}':z for i,z in enumerate(chi)})
    for key,z in scalars.items(): append_interval(name,key,z)
    for i in range(4):
        for key,z in [(f'X.{i}',x[i]),(f'center.{i}',center[i]),(f'radius.{i}',E.point(radius[i])),(f'gc.{i}',gc[i])]:append_interval(name,key,z)
        for j in range(4):append_interval(name,f'C.{i}.{j}',c[i][j])
        append_jet(name,f'G.{i}',g[i]);append_jet(name,f'NP.{i}',np[i])
    for j in range(33):
        for aa in range(3):
            append_jet(name,f'RATE.{j}.{aa}',rates[j][aa]);append_interval(name,f'HEAT.{j}.{aa}',heat[j][aa])
    append_jet(name,'HHQ',q)
    expected=10+16+16+(4+4+33*3+1)*(1+7+7*7)+33*3
    check(len(TSV)-first==expected,name+': complete fixed gate input layout')
    check(len({row[1]for row in TSV[first:]})==expected,name+': unique gate input keys')
    detail={'stage':name,'input_exports':[{'path':str(z.relative_to(ROOT)),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest()}for z in paths],
            'validated_saved_intervals':endpoint_count,'same_COMMON_first_stage':True,
            'thermal_X':vec(x),'Banach_ball_center':vec(center),'radius':vec([E.point(r)for r in radius]),
            'banach_beta':vec([E.point(z)for z in beta]),'banach_absK_radius':vec([E.point(z)for z in rows]),
            'linear_tail':{'U':ut,'V':vt,'W':wt},'mixed_residual_terms':rhs_terms,
            'energy_source_Jet':jser(energy),
            'energy_source_parts':{'nonphoto':jser(energy_np),'photo':jser(energy_photo),'expansion':jser(expansion)},
            'direct_projected_intersection':ser(common),'temperature_mixed_K':ser(wt_temp),
            'source_leading_energy':ser(leading),'finite_remainder_energy':ser(remainder),
            'birth_feedback_remainder':ser(birth_remainder),'leading_plus_remainder_energy':ser(leading_remainder),
            'remainder_abs_over_leading_strict_margin':None if leading.hi>=0 else ser(E.point(mag(remainder)/(-leading.hi))),
            'finite_unit_square_interaction':{'gas':vec(w),'energy':ser(projected),'temperature':ser(wt_temp),
                 'identity':'double integral of mixed derivative over the same unit parameter rectangle',
                 'corner_roots_evaluated':0},
            'source_inclusion_premise':'original NCP07 fixed-coefficient real-source Jet inclusion and open C2 evidence; no new proof of native interval kernel',
            'native_authority':False,'actual_native':{'root':None,'U':None,'V':None,'W':None,'I':None}}
    return stagesummary,detail


def semantic_checks():
    results=[]
    ident=[[E.point(int(i==j))for j in range(4)]for i in range(4)]
    k=[[E.point(F(1,4) if i==j else 0)for j in range(4)]for i in range(4)]
    ans,tail=inverse_action(k,ident,[ONE]*4,[F(1)]*4,F(1,4))
    check(all(z.contains(E.point(F(4,3)))for z in ans),'semantic: nontrivial Neumann tail includes exact inverse')
    results.append({'case':'nontrivial_inverse_tail','exact_solution':ser(E.point(F(4,3))),'enclosure':vec(ans),'tail':tail})
    chi=E.point(5);q=E(1,2)
    naive=chi*q-chi*q
    check(naive.lo<0<naive.hi,'semantic: independent component cancellation loses dependence')
    results.append({'case':'reaction_vector_cancellation','naive_interval':ser(naive),'structural_identity':ser(ZERO)})
    for label,terms,expected in [('negative',[E(-2,-1),E(F(-1,8),F(1,8))],'STRICT_NEGATIVE'),
                                  ('positive',[E(1,2),E(F(-1,8),F(1,8))],'STRICT_POSITIVE'),
                                  ('zero_touch',[E(-1,0)],'ZERO_CONTAINING')]:
        total=sum(terms,ZERO)
        check(total.sign()==expected,'semantic: scalar term '+label)
        results.append({'case':'scalar_'+label,'sum':ser(total)})
    tiny=E.leaf('0000000000000001'); signed=E(-tiny.hi,tiny.hi)
    check((signed+ZERO)==signed,'semantic: signed minsubnormal is retained exactly')
    results.append({'case':'signed_minsubnormal','interval':ser(signed)})
    # Analytically solvable dimensionless two-coordinate model:
    # F=lambda*q*(1,-chi)+b*(r-s*x)*(1,a).
    d=F(1,4);qq=F(2);cc=F(5);aa=F(1,2);ss=F(1);rr=F(2);x0=F(1,4);w0=F(3)
    def toy(lam,b):
        x=(x0+d*lam*qq+d*b*rr)/(1+d*b*ss)
        w=w0-d*cc*lam*qq+d*b*aa*(rr-ss*x)
        return cc*x+w
    finite=toy(1,1)-toy(1,0)-toy(0,1)+toy(0,0)
    exact=-d*d*qq*ss*(cc+aa)/(1+d*ss)
    uniform=E(-d*d*qq*ss*(cc+aa),-d*d*qq*ss*(cc+aa)/(1+d*ss)**2)
    check(finite==exact and uniform.contains(E.point(finite)) and uniform.hi<0,'semantic: analytic finite interaction agrees with integrated mixed bound')
    results.append({'case':'analytic_HH_photo_finite_identity','finite_exact':ser(E.point(exact)),'uniform_mixed':ser(uniform),'point_root_solver_calls':0})
    rejected=[]
    for label,gamma,rad in [('gamma_one',F(1),[F(1)]*4),('negative_radius',F(1,4),[F(-1)]+[F(1)]*3)]:
        try:inverse_action(k,ident,[ONE]*4,rad,gamma)
        except ValueError:rejected.append(label)
        else:raise AssertionError('did not reject '+label)
    check(len(rejected)==2,'semantic: invalid inverse domains rejected')
    results.append({'case':'invalid_inverse_domains','rejected':rejected})
    return results


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='projected_first');args=parser.parse_args()
    if not args.run_id.replace('_','').isalnum():raise ValueError('RUN_ID')
    out=ROOT/'results'/args.run_id;out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat()
    semantic=semantic_checks()
    stages=[];details=[]
    for name in ('full','first_half'):
        s,dd=stage_analysis(name);stages.append(s);details.append(dd)
    fixture=out/'GATE_INPUTS.tsv'
    fixture.write_text('stage\tkey\tlo_bits\thi_bits\n'+''.join('\t'.join(row)+'\n'for row in TSV))
    oracle={'schema':'PHYS09_PROJECTED_ENERGY_ORACLE_V1','stages':stages,
            'gate_input':{'path':str(fixture.relative_to(ROOT)),'rows':len(TSV),'bytes':fixture.stat().st_size,'sha256':hashlib.sha256(fixture.read_bytes()).hexdigest()},
            'comparison_rule':'Rust enclosure contains exact rational oracle; endpoint signs checked separately',
            'native_authority':False}
    result={'schema':'WU088_HH_PHYS09_PROJECTED_FINITE_ENERGY_V1','started_utc':started,
            'finished_utc':datetime.now(timezone.utc).isoformat(),'stages':stages,'details':details,
            'semantic_cases':semantic,'checks':CHECKS,'assertions':len(CHECKS),'assertions_are_unique_tests':False,
            'new_native_source_callbacks':0,'nonlinear_root_iterations':0,'native_solver_calls':0,
            'new_transcendental_source_evaluations':0,'historical_scientific_replays':0,
            'scope':'mathematical family of captured NCP07 fixed-leaf source, conditional on original source inclusion; no native issuer authority'}
    for filename,obj in [('GOLDEN_ORACLE.json',oracle),('PROJECTED_RESULTS.json',result)]:
        with (out/filename).open('x')as fp:json.dump(obj,fp,indent=2);fp.write('\n')
    print(json.dumps({'status':'PASS','assertions':len(CHECKS),'semantic_cases':len(semantic),'gate_input_rows':len(TSV),
         'stages':[{'stage':s['stage'],'gamma':[s['gamma']['lo'],s['gamma']['hi']],
                    'W':[[z['lo'],z['hi']]for z in s['W']],
                    'energy_direct':[s['direct_energy']['lo'],s['direct_energy']['hi']],
                    'energy_projected':[s['projected_energy']['lo'],s['projected_energy']['hi']],
                    'energy_terms':{k:[z['lo'],z['hi']]for k,z in s['energy_terms'].items()},
                    'temperature_mixed':[dd['temperature_mixed_K']['lo'],dd['temperature_mixed_K']['hi']],
                    'leading':[dd['source_leading_energy']['lo'],dd['source_leading_energy']['hi']],
                    'remainder':[dd['finite_remainder_energy']['lo'],dd['finite_remainder_energy']['hi']]}
                   for s,dd in zip(stages,details,strict=True)]},indent=2))


if __name__=='__main__':main()
