#!/usr/bin/env python3
"""Independent PHYS19 certificate/readout audit; never imports application code.

Uses fractions.Fraction with exact rational interval operations. The checks
reconstruct inverse proofs, selected pure product rules, quotient formulae,
and finite-response claims from frozen inputs and outputs.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, struct, time, math, resource, signal, sys
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q

class IV:
    def __init__(self,a=0,b=None):
        if isinstance(a,IV): self.a,self.b=a.a,a.b; return
        self.a,self.b=Q(a),Q(a if b is None else b)
        assert self.a<=self.b
    def __add__(self,z):
        z=IV(z); return IV(self.a+z.a,self.b+z.b)
    __radd__=__add__
    def __neg__(self):return IV(-self.b,-self.a)
    def __sub__(self,z):return self+-IV(z)
    def __rsub__(self,z):return IV(z)+-self
    def __mul__(self,z):
        z=IV(z); a=[self.a*z.a,self.a*z.b,self.b*z.a,self.b*z.b]
        return IV(min(a),max(a))
    __rmul__=__mul__
    def __truediv__(self,z):
        z=IV(z); assert not z.a<=0<=z.b
        return self*IV(1/z.b,1/z.a)
    def __rtruediv__(self,z):return IV(z)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        if n==0:return IV(1)
        if n%2:return IV(self.a**n,self.b**n)
        return IV(0 if self.a<=0<=self.b else min(self.a**n,self.b**n),max(self.a**n,self.b**n))
    def meet(self,z):z=IV(z);return IV(max(self.a,z.a),min(self.b,z.b))
    def inside(self,z):z=IV(z);return z.a<=self.a and self.b<=z.b
    def same(self,z):z=IV(z);return self.a==z.a and self.b==z.b
    def zero(self):return self.a<=0<=self.b
    def mag(self):return max(abs(self.a),abs(self.b))
    def midpoint(self):return (self.a+self.b)/2
    def radius(self):return (self.b-self.a)/2

def bits(x):return Q(struct.unpack('>d',bytes.fromhex(x))[0])
def raw(x):
    if 'exact' in x:return IV(Q(*map(int,x['exact']['lo'])),Q(*map(int,x['exact']['hi'])))
    return IV(bits(x['lo_bits']),bits(x['hi_bits']))
def vec(x):return [raw(z) for z in x]
def mat(x):return [vec(z) for z in x]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),IV(0))
def mv(a,b):return [dot(z,b) for z in a]
def tensor(a,u,v):return sum((a[j][k]*u[j]*v[k] for j in range(4) for k in range(4)),IV(0))

class Pure:
    """Independent ordinary derivative jet using binomial convolution."""
    def __init__(self,value=0,first=0,second=0):
        self.d=list(value.d) if isinstance(value,Pure) else [IV(value),IV(first),IV(second)]
    def __add__(self,z):
        z=Pure(z);return Pure(*[a+b for a,b in zip(self.d,z.d)])
    __radd__=__add__
    def __neg__(self):return Pure(*[-a for a in self.d])
    def __sub__(self,z):return self+-Pure(z)
    def __rsub__(self,z):return Pure(z)+-self
    def __mul__(self,z):
        z=Pure(z)
        return Pure(*[sum((math.comb(n,k)*self.d[k]*z.d[n-k] for k in range(n+1)),IV(0)) for n in range(3)])
    __rmul__=__mul__
    def reciprocal(self):
        a,b,c=self.d;t=1/a
        return Pure(t,-b*t**2,2*b**2*t**3-c*t**2)
    def __truediv__(self,z):return self*Pure(z).reciprocal()
    def __rtruediv__(self,z):return Pure(z)*self.reciprocal()
    def meet(self,*bounds):
        return Pure(*[v if z is None else v.meet(z) for v,z in zip(self.d,list(bounds)+[None]*(3-len(bounds)))])

def jet(z):return {'v':raw(z['value']),'g':vec(z['gradient'][:4]),'h':mat([a[:4] for a in z['signed_hessian'][:4]])}
def hull(a,b):return IV(min(a.a,b.a),max(a.b,b.b))
def plus(a,b):return [x+y for x,y in zip(a,b)]
def times(a,v):return [a*x for x in v]
def dec(x,mode):
    with localcontext() as c:
        c.prec=16;c.rounding=mode
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def output(x):
    if isinstance(x,IV):return {'exact':{'lo':[str(x.a.numerator),str(x.a.denominator)],'hi':[str(x.b.numerator),str(x.b.denominator)]},'decimal':[dec(x.a,ROUND_FLOOR),dec(x.b,ROUND_CEILING)]}
    if isinstance(x,Q):return output(IV(x))
    if isinstance(x,dict):return {k:output(v) for k,v in x.items()}
    if isinstance(x,list):return [output(v) for v in x]
    return x
def solve(A,b):
    # Fraction Gaussian elimination with independent pivot normalization.
    n=len(b);a=[list(row)+[v] for row,v in zip(A,b)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if a[i][j])
        a[j],a[pivot]=a[pivot],a[j]
        for i in range(j+1,n):
            fac=a[i][j]/a[j][j]
            for k in range(j,n+1):a[i][k]-=fac*a[j][k]
    v=[Q(0) for _ in range(n)]
    for j in reversed(range(n)):v[j]=(a[j][n]-sum(a[j][k]*v[k] for k in range(j+1,n)))/a[j][j]
    return v

def main(base,outdir):
    start=time.perf_counter();checks=[];ids=[]
    sys.set_int_max_str_digits(0)
    outdir.mkdir(parents=True,exist_ok=False)
    def load(p):
        data=p.read_bytes();ids.append({'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        return json.loads(data)
    def check(name,ok,detail=None):
        checks.append({'name':name,'pass':bool(ok),'detail':detail})
        if not ok:
            (outdir/'FAILURE.json').write_text(json.dumps(output({'checks':checks,'elapsed_seconds':time.perf_counter()-start}),indent=2)+'\n')
            raise AssertionError(name)
    comparisons=[]
    def enclosure(name,expected,record):
        vals=expected if isinstance(expected,list) else [expected]
        refs=record if isinstance(expected,list) else [record]
        ok=len(vals)==len(refs) and all(a.inside(raw(b)) for a,b in zip(vals,refs))
        differences=[{'lower_margin':a.a-raw(b).a,'upper_margin':raw(b).b-a.b} for a,b in zip(vals,refs)]
        comparisons.append({'name':name,'count':len(vals),'contained':ok,
            'exact_match_count':sum(a.same(raw(b)) for a,b in zip(vals,refs)),
            'minimum_lower_margin_decimal':dec(min(z['lower_margin'] for z in differences),ROUND_FLOOR),
            'minimum_upper_margin_decimal':dec(min(z['upper_margin'] for z in differences),ROUND_FLOOR),
            'comparison_arithmetic':'exact Fraction endpoint inequalities'})
        check(name,ok, None if ok else {'independent':vals,'reported':refs,'margins':differences})
    p19=base/'HH_PHYS19_THEORY_20261013_v1';p15=base/'HH_PHYS15_THEORY_20261012_v1'
    r=load(p19/'checks/application/run01/results/CURVATURE_RESULTS.json')
    geo=load(p19/'checks/application/readout02/results/CURVATURE_GEOMETRY.json')
    mix=load(base/'HH_PHYS18_THEORY_20261013_v1/checks/application/run02/results/MIXED_RESPONSE_RESULTS.json')
    p17=load(base/'HH_PHYS17_THEORY_20261013_v1/checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json')
    p16=load(base/'HH_PHYS16_THEORY_20261013_v1/checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json')
    src=p15/'inputs/phys14/inputs/ncp07/results'
    first=load(src/'first_half/SOURCE_BOX.json');full=load(src/'full/SOURCE_BOX.json')
    native=load(src/'full/NATIVE_CONSTANT_LEAVES.json')
    p14=load(p15/'inputs/phys14/results/advance01/ADVANCE_RESULTS.json')
    uniform=load(p15/'inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json')
    preflight=load(base/'HH_PHYS18_THEORY_20261013_v1/theory/CURVATURE_INPUT_PREFLIGHT.json')
    centre=load(src/'full/SOURCE_CENTRE.json')
    components=load(src/'full/SOURCE_BOX_COMPONENTS.json')
    centre_components=load(src/'full/SOURCE_CENTRE_COMPONENTS.json')
    first_components=load(src/'first_half/SOURCE_BOX_COMPONENTS.json')
    carry=load(p15/'inputs/phys14/inputs/phys11/CARRY_RESULTS.json')
    projected=load(p15/'inputs/phys14/inputs/phys09/PROJECTED_RESULTS.json')
    contract=load(p19/'contracts/ADOPTED_CURVATURE_CONTRACT.json')
    for binding in contract['input_bindings']:
        path=base/binding['path'];data=path.read_bytes()
        check('contract_binding:'+binding['path'],len(data)==binding['bytes'] and hashlib.sha256(data).hexdigest()==binding['sha256'])
    source_identities=[]
    for rel in ['src/curvature_application.py','checks/application/run01/EXECUTED_CODE.py','checks/application/run01/PRE_RUN.json','checks/application/run01/RUN.json','src/curvature_geometry.py','checks/application/readout02/EXECUTED_CODE.py','checks/application/readout02/PRE_RUN.json','checks/application/readout02/RUN.json']:
        path=p19/rel;data=path.read_bytes();source_identities.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    check('producer_executed_code_identity',source_identities[0]['sha256']==source_identities[1]['sha256'])
    check('geometry_executed_code_identity',source_identities[4]['sha256']==source_identities[5]['sha256'])
    check('geometry_curvature_input_sha',geo['input']['sha256']==hashlib.sha256((p19/'checks/application/run01/results/CURVATURE_RESULTS.json').read_bytes()).hexdigest())
    check('geometry_mixed_input_sha',geo['mixed_input']['sha256']==hashlib.sha256((base/'HH_PHYS18_THEORY_20261013_v1/checks/application/run02/results/MIXED_RESPONSE_RESULTS.json').read_bytes()).hexdigest())
    inv=r['inverse_bindings'];fixed=r['fixed_endpoint']
    inverses={}
    for stage in ['first_half','full','second_half']:
        z=inv[stage];B=[[raw(v).b for v in row] for row in z['B']]
        S=[raw(v).a for v in z['S']];q=raw(z['q']).b
        ee=mat(z['I_CJF'] if stage=='full' else z['E'])
        check(stage+'_majorant_nonnegative',all(x>=0 for row in B for x in row))
        check(stage+'_scale_positive',all(x>0 for x in S))
        check(stage+'_E_within_B',all(ee[i][j].mag()<=B[i][j] for i in range(4) for j in range(4)))
        rows=[sum(B[i][j]*S[j]/S[i] for j in range(4)) for i in range(4)]
        check(stage+'_q_contract',max(rows)<=q<1,{'row_bounds':rows,'q':q})
        inverses[stage]=(B,ee)
    check('first_half_J_input_identity',all(raw(inv['first_half']['J'][i][j]).same(raw(first['A_Gg'][i][j])) for i in range(4) for j in range(4)))
    check('first_half_E_is_I_minus_J',all((IV(i==j)-raw(first['A_Gg'][i][j])).same(raw(inv['first_half']['E'][i][j])) for i in range(4) for j in range(4)))
    check('second_half_E_input_identity',all(raw(inv['second_half']['E'][i][j]).same(raw(p14['linear_certificates']['L_hFg'][i][j])) for i in range(4) for j in range(4)))
    C=mat(inv['full']['C']);JF=mat(inv['full']['JF']);BF=inverses['full'][0]
    check('Full_C_original_identity',all(C[i][j].same(Q(uniform['fixed_C'][i][j])) for i in range(4) for j in range(4)))
    check('Full_B_original_identity',all(BF[i][j]==raw(uniform['B'][i][j]).b for i in range(4) for j in range(4)))
    check('Full_scale_original_identity',all(raw(v).same(Q(w)) for v,w in zip(inv['full']['S'],uniform['radius'])))
    check('Full_q_original_identity',raw(inv['full']['q']).same(raw(uniform['q']).b))
    check('first_half_B_preflight_identity',all(inverses['first_half'][0][i][j]==Q(*map(int,preflight['B1_exact'][i][j])) for i in range(4) for j in range(4)))
    check('first_half_scale_preflight_identity',all(raw(v).same(Q(*map(int,w))) for v,w in zip(inv['first_half']['S'],preflight['S1_exact'])))
    check('first_half_q_preflight_identity',raw(inv['first_half']['q']).same(Q(*map(int,preflight['q1_exact']))))
    check('second_half_scale_original_identity',all(raw(v).same(raw(w).a) for v,w in zip(inv['second_half']['S'],p14['root_certificate']['scaled_inf_scales'])))
    check('second_half_q_original_identity',raw(inv['second_half']['q']).same(raw(p14['root_certificate']['refined_contraction_upper']).b))
    for i in range(4):
        for j in range(4):
            e=(IV(i==j)-dot(C[i],[JF[k][j] for k in range(4)])).meet(IV(-BF[i][j],BF[i][j]))
            enclosure('full_E_intersection_'+str(i)+'_'+str(j),e,inv['full']['I_CJF'][i][j])
    check('source_residual_Hessian_symmetry_compatible',all(raw(s['G_gg'][i][j][k]).meet(raw(s['G_gg'][i][k][j])) is not None for s in [first,full] for i in range(4) for j in range(4) for k in range(4)))
    cert_records=[]
    def certificate(name,stage,cert,reported,rhs):
        B,ee=inverses[stage]
        cr=vec(cert['C_rhs'] if 'C_rhs' in cert else cert['rhs'])
        enclosure(name+'_rhs_binding',mv(C,rhs) if stage=='full' else rhs,cert['C_rhs'] if stage=='full' else cert['rhs'])
        m=solve([[Q(i==j)-B[i][j] for j in range(4)] for i in range(4)],[v.mag() for v in cr])
        tail=[sum(B[i][j]*m[j] for j in range(4)) for i in range(4)]
        check(name+'_exact_majorant_identity',all(m[i]>=0 and m[i]-tail[i]==cr[i].mag() for i in range(4)))
        enclosure(name+'_stored_majorant',[IV(x) for x in m],cert['absolute_majorant'])
        enclosure(name+'_stored_tail',[IV(x) for x in tail],cert['tail'])
        vv=[x+IV(-t,t) for x,t in zip(cr,tail)]
        enclosure(name+'_initial',vv,cert['initial'])
        for _ in range(3):vv=[x.meet(y+z) for x,y,z in zip(vv,cr,mv(ee,vv))]
        enclosure(name+'_refined',vv,reported)
        cert_records.append({'name':name,'stage':stage,'reconstructed_inclusion':vv})

    h=bits(first['dt_bits']);c=bits(native['c_bits']);n1=bits(first['nH_bits']);n2=bits(full['nH_bits'])
    check('stage_duration_exact',h==625000000 and bits(full['dt_bits'])==2*h)
    energy=[IV(bits(z)) for z in full['energy_bits']]
    a1=[c*n1*bits(z[0]) for z in full['sigma_bits']]+[Q(0),Q(0)]
    a2=[c*n2*bits(z[0]) for z in full['sigma_bits']]+[Q(0),Q(0)]
    rho=raw(p16['linked_factors']['rho']);birth=raw(p16['linked_factors']['M'])
    alpha=[IV(0)]+[(1-rho)*energy[j]/(energy[j]-energy[j-1]) for j in range(1,33)]
    def remap(v):
        u=[IV(0) for _ in range(35)];u[33]=v[33]+v[0];u[34]=rho*(v[34]+energy[0]*v[0])
        for j in range(1,33):u[j-1]+=alpha[j]*v[j];u[j]+=(1-alpha[j])*v[j]
        return u
    CT,Pi2,PiF,T2=[raw(fixed[k]) for k in ['CT','Pi2','PiF','T2']]
    le=vec(fixed['le']);d=vec(fixed['d']);de=dot(le,d);F=raw(fixed['DeltaT_K']);goal=vec(fixed['goal_row'])
    check('temperature_denominators_positive',Pi2.a>0 and PiF.a>0)
    CT_exact=2*bits(native['ev_erg_bits'])/(3*bits(native['kb_bits']))
    f2=bits(full['nHe_stored_bits'])/n2
    enclosure('temperature_constant_from_exact_binary_leaves',IV(CT_exact),fixed['CT'])
    enclosure('electron_row_exact_ratio',[IV(1),IV(f2),IV(2*f2),IV(0)],fixed['le'])
    enclosure('Pi2_exact_quotient_denominator',1+f2+dot(le,vec(fixed['g2'])),fixed['Pi2'])
    enclosure('PiF_common_endpoint_denominator',Pi2-de,fixed['PiF'])
    enclosure('goal_row_exact_finite_quotient',[(CT*int(i==3)-(T2-F)*le[i])/PiF for i in range(4)],fixed['goal_row'])
    g1=vec(fixed['g1']);g2=vec(fixed['g2']);gF=vec(fixed['gF']);gc=[IV(Q(z)) for z in uniform['center']]
    X=vec(p14['root_certificate']['domain_X']);chi=IV(bits(native['CHI_bits'][0]));hh=[IV(1),IV(0),IV(0),-chi]
    np=[jet(z) for z in components['nonphoto']];npc=[jet(z) for z in centre_components['nonphoto']]
    qbox=jet(full['q']);qcentre=jet(centre['q']);parameter=IV(0,1)
    Hexp=IV(bits(full['Hmean_bits']))
    def local(g):
        assert all(a.inside(b) for a,b in zip(g,X))
        delta=[a-b for a,b in zip(g,gc)]
        def tay(a,b):
            return {'v':a['v'].meet(b['v']+dot(a['g'],delta)),
                    'g':[u.meet(v+dot(row,delta)) for u,v,row in zip(a['g'],b['g'],a['h'])], 'h':a['h']}
        return [tay(a,b) for a,b in zip(np,npc)],tay(qbox,qcentre)
    def source(g):
        n,q=local(g)
        J=[[n[i]['g'][j]+parameter*q['g'][j]*hh[i] for j in range(4)] for i in range(4)]
        H=[[[n[i]['h'][j][k]+parameter*q['h'][j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
        J[3][3]-=2*Hexp
        return J,H,q
    Jy,Hy,qy=source(g2);JFsource,HFsource,qf=source(gF)
    Ggg=[mat(z) for z in full['G_gg']]
    reconstructed_JF=[[raw(full['A_Gg'][i][j]).meet(raw(centre['A_Gg'][i][j])+dot(Ggg[i][j],[gF[k]-gc[k] for k in range(4)])) for j in range(4)] for i in range(4)]
    for i in range(4):enclosure('Full_JF_source_center_binding_row_'+str(i),reconstructed_JF[i],inv['full']['JF'][i])
    heat=[IV(bits(z[0])) for z in full['heat_bits']]
    def project(v):return [sum(v[:33],IV(0)),IV(0),IV(0),dot(heat,v[:33])]
    ell=[2*h*a for a in a2];Dy=[1+e*(1-g2[0]) for e in ell];Df=[a+e*d[0] for a,e in zip(Dy,ell)]
    check('Full_photo_denominators_positive',all(z.a>0 for z in Df))
    QF=vec(p16['linked_factors']['QF']);Jbirth=[birth if j==24 else IV(0) for j in range(35)]
    Hph=project([2*e**2*v/z**3 for e,v,z in zip(ell,QF,Df)])
    HF=[[[( -2*h*HFsource[i][j][k]+(Hph[i] if j==k==0 else IV(0))).meet(Ggg[i][j][k]) for k in range(4)] for j in range(4)] for i in range(4)]
    Hgl=[[(-2*h*hh[i]*qf['g'][j]).meet(raw(full['G_g_lambda'][i][j])) for j in range(4)] for i in range(4)]
    Hgbvec=project([2*e*v/z**2 for e,v,z in zip(ell,Jbirth,Df)])
    Hgb=[[(Hgbvec[i] if j==0 else IV(0)).meet(raw(full['G_g_b'][i][j])) for j in range(4)] for i in range(4)]
    first_proj=next(s for s in projected['stages'] if s['stage']=='first_half')
    full_proj=next(s for s in projected['stages'] if s['stage']=='full')
    first_carry=next(s for s in carry['stages'] if s['stage']=='first_half')
    # Directional derivative of the inherited density bridge, independently
    # evaluated from frozen source value/gradient/Hessian data.
    f1=bits(first['nHe_stored_bits'])/n1;df=IV(f1-f2);rn=IV(n1/n2);le1=[IV(1),IV(f1),IV(2*f1),IV(0)]
    check('same_stage_expansion_leaf',first['Hmean_bits']==full['Hmean_bits'])
    def bridge(v):
        sg=g1[1]+2*g1[2];eg1=dot(le1,g1);eg2=dot(le,g1);pi1=1+f1+eg1
        pull=-g1[3]*df*(1+sg)/pi1
        pullv=-df*(((1+sg)*v[3]+g1[3]*(v[1]+2*v[2]))/pi1-g1[3]*(1+sg)*dot(le1,v)/pi1**2)
        gs=list(g1);gs[3]+=pull;vs=list(v);vs[3]+=pullv
        ng,qg=local(g1);ns,qs=local(gs);nh,qh=local([hull(a,b) for a,b in zip(g1,gs)])
        rem=rn-1+rn*df*sg/eg2;re=1+rem
        rev=rn*df*(eg2*(v[1]+2*v[2])-sg*dot(le,v))/eg2**2
        sc=ns[3]['v']+chi*ns[0]['v'];sc1=[ns[3]['g'][j]+chi*ns[0]['g'][j] for j in range(4)]
        sc2=[[ns[3]['h'][j][k]+chi*ns[0]['h'][j][k] for k in range(4)] for j in range(4)]
        es=dot(le,gs);pis=1+f2+es;U=sc/(n2*es)
        Ug=[(sc1[j]/es-sc*le[j]/es**2)/n2 for j in range(4)]
        Ugg=[[(sc2[j][k]/es-(sc1[j]*le[k]+sc1[k]*le[j])/es**2+2*sc*le[j]*le[k]/es**3)/n2 for k in range(4)] for j in range(4)]
        u=[IV(1),IV(0),IV(0),gs[3]/pis];du=[IV(0),IV(0),IV(0),vs[3]/pis-gs[3]*dot(le,vs)/pis**2]
        identity=(U-gs[0]*dot(Ug,u))/f2;kh=identity.meet(raw(p16['source_bridge']['kwHe']))
        dkh=(dot(Ug,vs)-vs[0]*dot(Ug,u)-gs[0]*(tensor(Ugg,vs,u)+dot(Ug,du)))/f2
        npv=[rem*dot(ng[i]['g'],v)+rev*ns[i]['v']+re*pull*dot(nh[i]['h'][3],v)+re*ns[i]['g'][3]*pullv for i in range(4)]
        he=n1*df*(dot(le1,v)*kh+eg1*dkh);npv[3]+=he
        qv=(rn-1)*dot(qg['g'],v)+rn*pull*dot(qh['h'][3],v)+rn*qs['g'][3]*pullv
        total=[h*(npv[i]+parameter*qv*hh[i]) for i in range(4)]
        return total,{'gstar':gs,'vstar':vs,'pull_w':pull,'pull_w_theta':pullv,'re_minus1':rem,'re_theta':rev,
            'kHe_identity':identity,'kHe':kh,'D_kHe':dkh,'He_correction_theta_per_second':he,
            'nonphoto_time_theta_per_second':npv,'HH_time_theta_per_second':qv}
    photon_formula_checks={};ledger_checks={}
    for theta in ['lambda','b']:
        z=r['responses'][theta];binding=z['bindings'];p1=vec(binding['p1']);p2=vec(binding['p2']);pF=vec(binding['pF']);dp=vec(binding['d_theta'])
        slot='U' if theta=='lambda' else 'V';dl=int(theta=='lambda');db=int(theta=='b')
        enclosure(theta+'_first_tangent_original_inclusion',vec(first_proj[slot]),binding['p1'])
        enclosure(theta+'_second_tangent_original_inclusion',vec(p14['gas_response'][slot]),binding['p2'])
        enclosure(theta+'_defect_tangent_original_inclusion',vec(p17['responses'][theta]['d_theta']),binding['d_theta'])
        enclosure(theta+'_Full_original_tangent_inclusion',vec(full_proj[slot]),binding['pF_original'])
        enclosure(theta+'_Full_tangent_intersection',[raw(b).meet(c-e) for b,c,e in zip(binding['pF_original'],p2,dp)],binding['pF'])
        K1=vec(z['first_half']['K']);K2=vec(z['second_half']['K']);KF=vec(z['full']['K'])
        H1=[mat(v) for v in first['G_gg']];H1theta=mat(first['G_g_'+theta])
        rhs1=[-tensor(H1[i],p1,p1)-2*dot(H1theta[i],p1) for i in range(4)]
        enclosure(theta+'_first_pure_rhs_factor2',rhs1,z['first_half']['rhs'])
        forceF=[tensor(HF[i],pF,pF)+2*dot((Hgl if dl else Hgb)[i],pF) for i in range(4)]
        enclosure(theta+'_Full_residual_source_forcing',forceF,z['full']['forcing'])
        srhs=[h*(tensor(Hy[i],p2,p2)+2*dl*dot(qy['g'],p2)*hh[i]) for i in range(4)]
        enclosure(theta+'_second_source_Hessian_time_and_HH_factor2',srhs,z['second_half']['source_rhs'])
        certificate(theta+'_K1','first_half',z['first_half']['inverse_certificate'],z['first_half']['K'],vec(z['first_half']['rhs']))
        certificate(theta+'_KF','full',z['full']['inverse_certificate'],z['full']['K'],times(-1,vec(z['full']['forcing'])))
        certificate(theta+'_K2','second_half',z['second_half']['inverse_certificate'],z['second_half']['K'],vec(z['second_half']['rhs']))
        certificate(theta+'_Kd_direct','full',z['direct_inverse_certificate'],z['d_pure_direct'],vec(z['direct_rhs']))
        certificate(theta+'_Kd_correlated','full',z['correlated_inverse_certificate'],z['d_pure_correlated'],vec(z['correlated_rhs']))
        expected=[a+b+c0 for a,b,c0 in zip(K1,vec(z['second_half']['source_rhs']),vec(z['second_half']['photo_rhs_excluding_linear_K2']))]
        enclosure(theta+'_second_RHS_component_sum',expected,z['second_half']['rhs'])
        expected=[x+y for x,y in zip(mv(JF,K2),vec(z['full']['forcing']))]
        enclosure(theta+'_same_Full_direct_RHS',expected,z['direct_rhs'])
        expected=[sum((raw(s[i]) for s in z['residual_sectors'].values()),IV(0)) for i in range(4)]
        enclosure(theta+'_residual_sector_sum',expected,z['r_theta_theta'])
        expected=[raw(z['r_theta_theta'][i])+sum((raw(s[i]) for s in z['endpoint_correction_sectors'].values()),IV(0)) for i in range(4)]
        enclosure(theta+'_correlated_endpoint_sum',expected,z['correlated_rhs'])
        enclosure(theta+'_K_endpoint_difference',[a-b for a,b in zip(K2,KF)],z['d_pure_endpoint_subtraction'])
        dk=[a.meet(b).meet(cc) for a,b,cc in zip(vec(z['d_pure_direct']),vec(z['d_pure_correlated']),vec(z['d_pure_endpoint_subtraction']))]
        check(theta+'_three_way_Kd_intersection',all(a.same(raw(b)) for a,b in zip(dk,z['d_pure_intersection'])))
        jets=z['photon_jets'];check(theta+'_35_photon_slots',all(len(v)==35 for v in jets.values()))
        q2pure=remap([raw(a['theta_theta']) for a in jets['Z1']])
        enclosure(theta+'_carried_Q2_pure_linear_remap',q2pure,[a['theta_theta'] for a in jets['Q2']])
        check(theta+'_absorption_guards_exact_zero',all(raw(jets[k][j]['theta_theta']).same(0) for k in ['P1','P2'] for j in [33,34]))
        def rjet(v):
            u=[Pure(0) for _ in range(35)];u[33]=v[33]+v[0];u[34]=(v[34]+v[0]*energy[0])*rho
            for j in range(1,33):u[j-1]+=v[j]*alpha[j];u[j]+=v[j]*(1-alpha[j])
            return u
        def rmjet(v):
            u=[Pure(0) for _ in range(35)];u[0]=-v[0];u[33]=v[0]
            u[34]=v[0]*(rho*energy[0])+v[34]*(rho-1)
            for j in range(1,33):u[j-1]+=v[j]*alpha[j];u[j]-=v[j]*alpha[j]
            return u
        def drjet(v):
            u=[Pure(0) for _ in range(35)]
            for j in range(2,33):
                ratio=(energy[j-1]-energy[j-2])/(energy[j]-energy[j-1]);pref=v[j]*(alpha[j]*alpha[j-1])
                u[j-2]+=pref;u[j-1]-=pref*(1+ratio);u[j]+=pref*ratio
            u[1]+=v[1]*(alpha[1]*(alpha[1]+rho-1));u[0]-=v[1]*(alpha[1]*(alpha[1]+rho))
            u[33]+=v[1]*alpha[1];u[34]+=v[1]*(rho*energy[0]*alpha[1])
            return u
        bp=Pure(parameter,db,0);x1=Pure(g1[0],p1[0],K1[0]);x2=Pure(g2[0],p2[0],K2[0]);x20=Pure(g2[0],p2[0],0)
        z0=[Pure(v) for v in vec(p16['linked_factors']['common_Z0'])]
        rz0=rjet(z0);rrz0=rjet(rz0);drz0=drjet(z0)
        q1=[v+bp*j for v,j in zip(rz0,Jbirth)]
        a1j=[1/(1+(1-x1)*(h*a)) for a in a1]
        z1=[a*v for a,v in zip(a1j,q1)]
        for j in range(33):
            q1[j]=q1[j].meet(raw(first_carry['groups'][j]['incoming']['value']),raw(first_carry['groups'][j]['incoming'][slot]))
            z1[j]=z1[j].meet(raw(first_carry['groups'][j]['outgoing_joint']['value']),raw(first_carry['groups'][j]['outgoing_joint'][slot]))
        q2=[v+bp*j for v,j in zip(rjet(z1),Jbirth)]
        for j in range(33):q2[j]=q2[j].meet(raw(p14['photon_state']['incoming']['value'][j]),raw(p14['photon_state']['incoming'][slot][j]))
        for name,vv in [('Q1',q1),('Z1',z1),('Q2',q2)]:
            for k,key in enumerate(['value','theta','theta_theta']):enclosure(theta+'_independent_jet_'+name+'_'+key,[v.d[k] for v in vv],[v[key] for v in jets[name]])
        # Original producer clips only value/first slots, never the new pure slot.
        tau0=[(1-x20)*(h*a) for a in a2];lz=[t/(1+t) for t in tau0]
        photo0=project([(u*v).d[2] for u,v in zip(lz,q2)])
        enclosure(theta+'_carried_photo_forcing_excludes_linear_K2',photo0,z['second_half']['photo_rhs_excluding_linear_K2'])
        tau=[(1-x2)*(h*a) for a in a2]
        aa=[1/(1+t) for t in tau];af=[1/(1+2*t) for t in tau]
        ll=[t/(1+t) for t in tau];lf=[2*t/(1+2*t) for t in tau]
        c1=[t*a*a*f for t,a,f in zip(tau,aa,af)];c2=[t*v for t,v in zip(tau,c1)]
        p1j=[(1-a)*v for a,v in zip(a1j,q1)];p2j=[a*v for a,v in zip(ll,q2)];z2j=[a*v for a,v in zip(aa,q2)]
        for name,vv in [('P1',p1j),('P2',p2j),('Z2',z2j)]:enclosure(theta+'_actual_'+name+'_restores_linear_K2',[v.d[2] for v in vv],[v['theta_theta'] for v in jets[name]])
        sp=vec(binding['stage_increment_theta']);ss=vec(p16['linked_factors']['stage_increment'])
        sK=vec(z['stage_increment']['pure_intersection']);sx=Pure(ss[0],sp[0],sK[0])
        sk_rhs=plus(times(h,plus(plus(mv(Jy,K2),[tensor(Hy[i],p2,p2) for i in range(4)]),times(2*dl*dot(qy['g'],p2),hh))),project([raw(v['theta_theta']) for v in jets['P2']]))
        enclosure(theta+'_stage_increment_source_identity',sk_rhs,z['stage_increment']['pure_from_stage'])
        check(theta+'_stage_increment_intersection',all(v.same((a-b).meet(raw(w))) for v,a,b,w in zip(sK,K2,K1,z['stage_increment']['pure_from_stage'])))
        zeta=[((1-x2)*(c*bits(full['sigma_bits'][j][0])*(n2-n1))-sx*a1[j])*h for j in range(33)]+[Pure(0),Pure(0)]
        da=[z*a*b for z,a,b in zip(zeta,a1j,aa)];daq=[a*q for a,q in zip(da,q1)]
        comm=[Pure(0) for _ in range(35)]
        for j in range(1,33):comm[j-1]+=(1-x2)*(alpha[j]*h*(a2[j-1]-a2[j]))*aa[j-1]*aa[j]*q1[j]
        rmJ=rmjet([Pure(v) for v in Jbirth])
        photon={
            'opacity_change':[-u+l*v for u,l,v in zip(daq,ll,rjet(daq))],
            'absorption_transport_commutator':[l*v for l,v in zip(ll,comm)],
            'stock_intermediate_redshift':[-l*v for l,v in zip(ll,rmjet(rz0))],
            'stock_backward_euler':[u*v for u,v in zip(c2,rrz0)],
            'remap_composition':[u*v for u,v in zip(lf,drz0)],
            'birth_redshift':[bp*l*a*v for l,a,v in zip(ll,aa,rmJ)],
            'birth_backward_euler':[-bp*u*v for u,v in zip(c1,Jbirth)]}
        for name,vv in photon.items():enclosure(theta+'_seven_sector_'+name,[v.d[2] for v in vv],z['photon_sector_pure'][name])
        for name,vv in z['photon_sector_pure'].items():enclosure(theta+'_photon_gas_projection_'+name,project(vec(vv)),z['residual_sectors'][name])
        for name in ['opacity_change','birth_redshift','birth_backward_euler']:
            check(theta+'_'+name+'_guards_zero',all(v.d[2].same(0) for v in photon[name][33:]))
        timeK,bK=bridge(K1);_,bp1=bridge(p1)
        for direction,bdata in [('K1',bK),('p1',bp1)]:
            for name,value in bdata.items():enclosure(theta+'_C2_density_bridge_'+direction+'_'+name,value,z['density_bridge'][direction][name])
        _,H12,q12=source([hull(a,b) for a,b in zip(g1,g2)])
        hn=[jet(v)['h'] for v in first_components['nonphoto']];hq=jet(first['q'])['h']
        hsource1=[[[hn[i][j][k]+parameter*hq[j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
        dh12=[[[hsource1[i][j][k]-Hy[i][j][k] for k in range(4)] for j in range(4)] for i in range(4)]
        gas={
            'source_time_linear':timeK,
            'stage_pure_increment':times(-h,mv(Jy,sK)),
            'stage_linear_curvature':times(-h,[tensor(H12[i],ss,K1) for i in range(4)]),
            'stage_Hessian_difference':times(h,[tensor(dh12[i],p1,p1) for i in range(4)]),
            'stage_tangent_change':times(-2*h,[tensor(Hy[i],sp,times(IV(Q(1,2)),plus(p2,p1))) for i in range(4)]),
            'HH_gradient_time':times(2*dl*h*bp1['HH_time_theta_per_second'],hh),
            'HH_gradient_increment':times(-2*dl*h*dot(qy['g'],sp),hh),
            'HH_gradient_movement':times(-2*dl*h*tensor(q12['h'],ss,p1),hh)}
        for name,v in gas.items():enclosure(theta+'_gas_residual_'+name,v,z['gas_residual_sectors'][name])
        ny,qny=local(g2);nf,qnf=local(gF)
        dhsource=[[[ -2*h*((ny[i]['h'][j][k]-nf[i]['h'][j][k])+parameter*(qny['h'][j][k]-qnf['h'][j][k])*hh[i]) for k in range(4)] for j in range(4)] for i in range(4)]
        dhphoto=project([2*e**3*v*d[0]*(dfi**2+dfi*dyi+dyi**2)/(dyi**3*dfi**3) for e,v,dfi,dyi in zip(ell,QF,Df,Dy)])
        dhgb=project([2*e**2*v*d[0]*(dfi+dyi)/(dyi**2*dfi**2) for e,v,dfi,dyi in zip(ell,Jbirth,Df,Dy)])
        _,qseg=local([hull(a,b) for a,b in zip(g2,gF)])
        balance=[a-b/2 for a,b in zip(p2,dp)]
        endpoints={
            'endpoint_linear_movement':times(-1,[tensor(Ggg[i],d,K2) for i in range(4)]),
            'endpoint_source_Hessian_difference':times(-1,[tensor(dhsource[i],p2,p2) for i in range(4)]),
            'endpoint_photo_Hessian_difference':times(-p2[0]**2,dhphoto),
            'endpoint_tangent_defect':times(-2,[tensor(HF[i],dp,balance) for i in range(4)]),
            'endpoint_HH_gradient_difference':times(4*dl*h*tensor(qseg['h'],d,p2),hh),
            'endpoint_HH_gradient_defect':times(-2*dl,mv(Hgl,dp)),
            'endpoint_birth_gradient_difference':times(-2*db*p2[0],dhgb),
            'endpoint_birth_gradient_defect':times(-2*db,mv(Hgb,dp))}
        for name,v in endpoints.items():enclosure(theta+'_C2_endpoint_'+name,v,z['endpoint_correction_sectors'][name])
        g1=vec(fixed['g1']);g2=vec(fixed['g2']);db=int(theta=='b');photo_compare=[]
        for j in range(35):
            t1=h*a1[j];A=1/(1+t1*(1-g1[0]));Au=t1*A**2*p1[0];Auu=t1*A**2*K1[0]+2*t1**2*A**3*p1[0]**2
            J=birth if j==24 else IV(0)
            calc=Auu*raw(jets['Q1'][j]['value'])+2*db*Au*J
            record=raw(jets['Z1'][j]['theta_theta'])
            # The algebraically factored formula can have a different interval width.
            calc.meet(record);photo_compare.append(calc.inside(record))
        photon_formula_checks[theta]={'35_pure_product_intersections':True,'factored_enclosure_contained_count':sum(photo_compare),'total':35}
        Ft=raw(p17['responses'][theta]['DeltaT_theta_K']);Tt=raw(p17['responses'][theta]['T2_theta_K']);Pt=raw(p17['responses'][theta]['PiF_theta'])
        tpp=(CT*K2[3]-T2*dot(le,K2)-2*Tt*dot(le,p2))/Pi2
        enclosure(theta+'_finite_T2_quotient_factor2',tpp,z['T2_pure_K'])
        tfpp=(CT*KF[3]-(T2-F)*dot(le,KF)-2*(Tt-Ft)*dot(le,pF))/PiF
        enclosure(theta+'_finite_Full_quotient_factor2',tfpp,z['TF_pure_K'])
        geo_parts={'second_endpoint_pure_temperature':-raw(z['T2_pure_K'])*de/PiF,'temperature_electron_cross':-2*Tt*dot(le,dp)/PiF,'defect_denominator_cross':-2*Ft*Pt/PiF,'value_defect_pure_denominator':-F*dot(le,K2)/PiF}
        for k,v in geo_parts.items():enclosure(theta+'_geometry_'+k,v,z['temperature_geometry_parts_K'][k])
        enclosure(theta+'_geometry_sum',sum(vec(list(z['temperature_geometry_parts_K'].values())),IV(0)),z['temperature_geometry_K'])
        fpp=(dot(goal,dk)+raw(z['temperature_geometry_K'])).meet(raw(z['F_pure_temperature_subtraction_K']))
        enclosure(theta+'_finite_correlated_F_quotient',fpp,z['F_pure_K'])
        check(theta+'_pure_sign',raw(z['F_pure_K']).b<0)
        # Independently reconstruct the conserved rows from stored pure photons.
        QF=vec(p16['linked_factors']['QF']);zhat=[]
        for j in range(35):
            ell=2*h*a2[j];A=1/(1+ell*(1-g2[0]));Au=ell*A**2*p2[0];Auu=ell*A**2*K2[0]+2*ell**2*A**3*p2[0]**2
            J=birth if j==24 else IV(0);zhat.append(Auu*QF[j]+4*db*Au*J)
        dz=[raw(v['theta_theta'])-w for v,w in zip(jets['Z2'],zhat)]
        ps=[sum((raw(v[j]) for v in z['photon_sector_pure'].values()),IV(0)) for j in range(35)]
        num=lambda v:sum(v[:33],IV(0))+v[33]
        eng=lambda v:dot(energy,v[:33])+v[34]
        p1pure=[raw(v['theta_theta']) for v in jets['P1']]
        ln=num(ps)+num(dz);lu=eng(ps)-(1-rho)*eng(p1pure)+eng(dz)
        check(theta+'_independent_number_ledger_contains_zero',ln.zero())
        check(theta+'_independent_energy_ledger_contains_zero',lu.zero())
        ledger_checks[theta]={'number_residual':ln,'energy_residual':lu,'meaning':'interval consistency of exact pure conservation identities'}

    fin=r['finite_response'];a=raw(fin['F_lambda_lambda_K']);b=raw(fin['F_b_b_K']);m=raw(mix['DeltaT_mixed_intersection_K']);interaction=raw(mix['four_corner_interaction_K'])
    det=a*b-m**2;direction=a-m/12+b/576
    check('strict_saddle_Hessian',det.b<0,det)
    check('fixed_countervariation_positive',direction.a>0,direction)
    enclosure('geometry_pointwise_mixed_binding',m,geo['hessian']['lambda_b_K'])
    check('interaction_distinct_source_field',geo['mixed_input']['hessian_field']=='DeltaT_mixed_intersection_K' and geo['mixed_input']['corner_coefficient_field']=='four_corner_interaction_K')
    check('geometry_determinant_exact',det.same(raw(geo['hessian']['determinant_K2'])))
    check('geometry_countervariation_exact',direction.same(raw(geo['hessian']['countervariation_curvature_K'])))
    bil=(a.mag()+b.mag())/8;corr=(a.radius()+b.radius())/8
    enclosure('bilinear_error_1_over_8',IV(bil),fin['bilinear_uniform_abs_error_bound_K'])
    enclosure('quadratic_centered_error_1_over_8',IV(corr),fin['quadratic_corrected_uniform_abs_error_bound_K'])
    check('geometry_error_ratio_exact',IV(bil/corr).same(raw(geo['interpolation']['improvement_factor'])))
    for k,v in [('lambda_lambda',a),('b_b',b)]:
        enclosure('pure_midpoint_'+k,IV(v.midpoint()),fin['pure_midpoints_K'][k]);enclosure('pure_radius_'+k,IV(v.radius()),fin['pure_radii_K'][k])
    globalF=raw(fin['anchor_F00_K']);al=raw(fin['chord_a_lambda_K']);ab=raw(fin['chord_a_b_K'])
    anchor=globalF.meet(globalF-al).meet(globalF-ab).meet(globalF-al-ab-interaction)
    check('corner_consistent_anchor_exact',anchor.same(raw(geo['coefficient_resolution']['corner_consistent_F00_K'])))
    cA=Q('-3.797385260416e-14');cB=Q('-4.681380466304e-11')
    fixedcorr=(max(abs(a.a-cA),abs(a.b-cA))+max(abs(b.a-cB),abs(b.b-cB)))/8
    total=anchor.radius()+al.radius()+ab.radius()+interaction.radius()+fixedcorr
    check('deterministic_surrogate_total_upper_bound_exact',IV(total).same(raw(geo['coefficient_resolution']['deterministic_midpoint_model_uniform_error_bound_K'])))
    path_slope=al-ab/24;check('countervariation_first_slope_negative',path_slope.b<0,path_slope)
    enclosure('displayed_decimal_midpoint_extra_rounding',IV(fixedcorr),geo['interpolation']['fixed_decimal_correction_abs_bound_K'])
    enclosure('geometry_bilinear_exact',IV(bil),geo['interpolation']['bilinear_abs_bound_K'])
    enclosure('geometry_midpoint_exact',IV(corr),geo['interpolation']['pure_midpoint_abs_bound_K'])
    check('axis_first_derivatives_resolved',al.b<0 and ab.a>0)
    decimal_count=0
    def check_decimals(z):
        nonlocal decimal_count
        if isinstance(z,dict):
            if 'exact' in z and 'outward_decimal' in z:
                v=raw(z);a,b=map(Q,z['outward_decimal']);assert a<=v.a<=v.b<=b;decimal_count+=1
            else:
                for v in z.values():check_decimals(v)
        elif isinstance(z,list):
            for v in z:check_decimals(v)
    check_decimals(r);check_decimals(geo);check('all_published_decimals_outward',True,{'intervals_checked':decimal_count})
    result={'schema':'WU088_HH_PHYS19_INDEPENDENT_FRACTION_AUDIT_V2','status':'pass_scoped',
        'method':'Independent Fraction interval class without dyadic rounding; separate binomial pure-jet graph; Gaussian elimination; no production imports or main replay',
        'scope':'Frozen same-COMMON fixed-alpha C2 family on shared [0,1]^2; 4 gas and 35 photon slots',
        'input_identities':ids,'producer_source_and_run_identities':source_identities,'checks':checks,'check_count':len(checks),
        'exact_endpoint_comparisons':comparisons,'comparison_count':len(comparisons),
        'scalar_comparison_count':sum(z['count'] for z in comparisons),'inverse_reconstruction':cert_records,
        'photon_product_rules':photon_formula_checks,'ledger_consistency':ledger_checks,
        'derived_readout':{'F_lambda_lambda_K':a,'F_b_b_K':b,'mixed_pointwise_K':m,
            'determinant_K2':det,'countervariation_curvature_K':direction,'countervariation_first_derivative_K':path_slope,
            'bilinear_bound_K':IV(bil),'quadratic_corrected_bound_K':IV(corr),
            'finite_decimal_corrected_bound_K':IV(fixedcorr),'shape_error_improvement_factor':IV(bil/corr),
            'corner_consistent_anchor_K':anchor,'deterministic_midpoint_uniform_upper_bound_K':IV(total)},
        'new_source_calls':0,'new_root_solves':0,'history_replays':0,
        'executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (outdir/'INDEPENDENT_FRACTION_AUDIT.json').write_text(json.dumps(output(result),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'comparisons':len(comparisons),
        'scalar_comparisons':result['scalar_comparison_count'],'elapsed_seconds':result['elapsed_seconds'],
        'peak_rss_kib':result['peak_rss_kib'],
        'derived_readout_decimal':{k:output(v)['decimal'] for k,v in result['derived_readout'].items()}},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();main(a.base,a.output)
