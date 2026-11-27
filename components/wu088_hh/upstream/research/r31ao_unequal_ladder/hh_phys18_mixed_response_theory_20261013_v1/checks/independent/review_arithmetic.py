#!/usr/bin/env python3
"""PHYS18 independent exact-rational review of stored scientific inputs.
No candidate imports or physical source/root/history evaluations. The exact
interval primitives and determinant solver are reused from the independently
reviewed PHYS17 checker. Mixed photon products use a nilpotent polynomial
coefficient convolution, separate from the candidate mixed-dual class.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,pathlib,resource,struct,sys,time
from fractions import Fraction as F
class R:
    __slots__=("lo","hi")
    def __init__(self,a=0,b=None):
        if isinstance(a,R): self.lo,self.hi=a.lo,a.hi; return
        if isinstance(a,dict):
            if "exact" in a:
                a,b=(F(*map(int,a["exact"][z])) for z in ("lo","hi"))
            else: a,b=(bits(a[z]) for z in ("lo_bits","hi_bits"))
        self.lo,self.hi=F(a),F(a if b is None else b)
        assert self.lo<=self.hi
    def __add__(self,b): b=R(b); return R(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self): return R(-self.hi,-self.lo)
    def __sub__(self,b): return self+-R(b)
    def __rsub__(self,b): return R(b)+-self
    def __mul__(self,b):
        b=R(b); v=[a*c for a in (self.lo,self.hi) for c in (b.lo,b.hi)]
        return R(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=R(b); assert not b.lo<=0<=b.hi
        return self*R(1/b.hi,1/b.lo)
    def __rtruediv__(self,b): return R(b)/self
    def __pow__(self,n):
        assert n>=0 and isinstance(n,int)
        if n==0:return R(1)
        if n%2 and self.lo<=0<=self.hi:return R(self.lo**n,self.hi**n)
        if n%2==0 and self.lo<=0<=self.hi:return R(0,max(abs(self.lo),abs(self.hi))**n)
        a,b=self.lo**n,self.hi**n; return R(min(a,b),max(a,b))
    def meet(self,b):b=R(b);return R(max(self.lo,b.lo),min(self.hi,b.hi))
    def holds(self,b):b=R(b);return self.lo<=b.lo and b.hi<=self.hi
    def overlaps(self,b):b=R(b);return self.lo<=b.hi and b.lo<=self.hi
    def mag(self):return max(abs(self.lo),abs(self.hi))
    def point(self):assert self.lo==self.hi;return self.lo

def bits(s): return F(struct.unpack(">d",bytes.fromhex(s))[0])
def V(x):return [R(z) for z in x]
def M(x):return [V(z) for z in x]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),R())
def mv(a,b):return [dot(x,b) for x in a]
def add(a,b):return [x+y for x,y in zip(a,b)]
def tensor(h,a,b):return sum((R(h[j][k])*a[j]*b[k] for k in range(4) for j in range(4)),R())
def det(a):
    n=len(a);answer=F()
    for p in itertools.permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=F(sign)
        for i in range(n):term*=a[i][p[i]]
        answer+=term
    return answer
def cramer(a,b):
    denominator=det(a);assert denominator
    return [det([[b[i] if k==j else a[i][k] for k in range(4)] for i in range(4)])/denominator for j in range(4)]
def contain(a,b):assert all(R(x).holds(y) for x,y in zip(a,b))
def overlap(a,b):assert all(R(x).overlaps(y) for x,y in zip(a,b))
def report_interval(x):return {"lo":str(x.lo),"hi":str(x.hi),"display":[float(x.lo),float(x.hi)]}

def scl(s,v):return [s*z for z in v]
def jet(j):return {'v':R(j['value']),'g':V(j['gradient'][:4]),'h':[V(row[:4]) for row in j['signed_hessian'][:4]]}
def centered(a,c,d):
    return {'v':a['v'].meet(c['v']+dot(a['g'],d)),
            'g':[a['g'][i].meet(c['g'][i]+dot(a['h'][i],d)) for i in range(4)],'h':a['h']}

def main(args):
    tic=time.perf_counter();checks=[];identities=[]
    roots={name:getattr(args,name.lower()).resolve() for name in ('P15','P16','P17','P18')}
    def read(name,path):
        p=roots[name]/path;b=p.read_bytes()
        identities.append({'root':name,'path':path,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        return json.loads(b)
    def check(name,fn):
        try:checks.append({'id':name,'result':'PASS','detail':fn()})
        except Exception as e:checks.append({'id':name,'result':'FAIL','error_type':type(e).__name__,'error':str(e)})
    c=read('P18','checks/application/run02/results/MIXED_RESPONSE_RESULTS.json')
    u17=read('P17','checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json')
    e16=read('P16','checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json')
    v16=read('P16','checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json')
    ncp='inputs/phys14/inputs/ncp07/results/'
    full=read('P15',ncp+'full/SOURCE_BOX.json');half=read('P15',ncp+'first_half/SOURCE_BOX.json')
    comp=read('P15',ncp+'full/SOURCE_BOX_COMPONENTS.json');hcomp=read('P15',ncp+'first_half/SOURCE_BOX_COMPONENTS.json')
    centre=read('P15',ncp+'full/SOURCE_CENTRE.json');cc=read('P15',ncp+'full/SOURCE_CENTRE_COMPONENTS.json')
    native=read('P15',ncp+'full/NATIVE_CONSTANT_LEAVES.json')
    uniform=read('P15','inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json')
    p09=read('P15','inputs/phys14/inputs/phys09/PROJECTED_RESULTS.json')
    p11=read('P15','inputs/phys14/inputs/phys11/CARRY_RESULTS.json')
    p14=read('P15','inputs/phys14/results/advance01/ADVANCE_RESULTS.json')
    f=c['fixed_endpoint'];ft=c['fixed_transfer'];bs=c['bindings'];st=c['stage_increment']
    C=M(ft['C']);B=[[R(z).point() for z in row] for row in ft['B']];q=R(ft['q']).point();S=[R(z).point() for z in ft['S']]
    A=[[F(i==j)-B[i][j] for j in range(4)] for i in range(4)];EJ=M(ft['I_CJF']);JF=M(ft['JF'])
    h=R(bits(half['dt_bits']));n1=R(bits(half['nH_bits']));n2=R(bits(full['nH_bits']))
    f1=R(bits(half['nHe_stored_bits']))/n1;f2=R(bits(full['nHe_stored_bits']))/n2
    df=f1-f2;rn=n1/n2;H=R(bits(full['Hmean_bits']));clight=R(bits(native['c_bits']))
    CT=2*R(bits(native['ev_erg_bits']))/(3*R(bits(native['kb_bits'])))
    chi=R(bits(native['CHI_bits'][0]));hh=[R(1),R(),R(),-chi]
    le=[R(1),f2,2*f2,R()];le1=[R(1),f1,2*f1,R()]
    g1=V(f['g1']);y=V(f['g2']);gF=V(f['gF']);d=V(f['d']);du=V(f['d_lambda']);db=V(f['d_b'])
    U1,V1,W1=[V(bs['first_half'][k]) for k in ('U','V','W')]
    U,Vv,W=[V(bs['second_half'][k]) for k in ('U','V','W')]
    UF,VF,WF=[V(bs['full'][k]) for k in ('U_intersection','V_intersection','W')]
    s,su,sb,sW=[V(st[k]) for k in ('value','lambda','b','mixed_intersection')]
    gcentre=[R(F(z)) for z in uniform['center']]
    X=V(p14['root_certificate']['domain_X'])
    E=[R(bits(z)) for z in full['energy_bits']];heat=[R(bits(z[0])) for z in full['heat_bits']]
    npfull=[jet(z) for z in comp['nonphoto']];npcentre=[jet(z) for z in cc['nonphoto']]
    qfull=jet(full['q']);qcentre=jet(centre['q'])
    def sources(g):
        contain(X,g);delta=[x-z for x,z in zip(g,gcentre)]
        return [centered(a,b,delta) for a,b in zip(npfull,npcentre)],centered(qfull,qcentre,delta)
    def combined(g):
        np,qj=sources(g)
        jac=[[np[i]['g'][j]+R(0,1)*qj['g'][j]*hh[i] for j in range(4)] for i in range(4)]
        hs=[[[np[i]['h'][j][k]+R(0,1)*qj['h'][j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
        jac[3][3]-=2*H
        return jac,hs,qj
    Jy,Hy,qy=combined(y)
    seg12=[R(min(x.lo,z.lo),max(x.hi,z.hi)) for x,z in zip(g1,y)]
    _,H12,q12=combined(seg12)
    def core_identities():
        for x in c['input_identities']:
            root=roots[{'PHYS15':'P15','PHYS16':'P16','PHYS17':'P17'}[x['root']]]
            b=(root/x['path']).read_bytes()
            assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
        return {'identities':len(c['input_identities'])}
    check('original_input_identities',core_identities)
    def scalar_bindings():
        assert h.point()==625000000 and bits(full['dt_bits'])==2*h.point()
        assert half['Hmean_bits']==full['Hmean_bits']
        contain(f['le'],le);assert R(f['CT']).holds(CT)
        contain(f['d'],V(e16['endpoint_d_intersection']))
        for p,k in (('lambda','d_lambda'),('b','d_b')):contain(f[k],V(u17['responses'][p]['d_theta']))
        assert R(f['Pi2']).lo>0 and R(f['PiF']).lo>0
        assert R(f['Pi2']).holds(1+f2+dot(le,y))
        assert R(f['PiF']).holds(R(f['Pi2'])-dot(le,d))
        return {'native_constants':'exact binary64/ratios','same_Hmean':True,'positive_denominators':True}
    check('constants_and_endpoint_bindings',scalar_bindings)
    def carry():
        first=next(z for z in p09['stages'] if z['stage']=='first_half');fulls=next(z for z in p09['stages'] if z['stage']=='full')
        count=0
        for stage,orig in [('first_half',first),('second_half',p14['gas_response'])]:
            for k in ('U','V','W'):contain(bs[stage][k],V(orig[k]));count+=4
        for key,old in [('U_original','U'),('V_original','V'),('W','W')]:contain(bs['full'][key],V(fulls[old]));count+=4
        for new,g,dd,old in [(UF,U,du,bs['full']['U_original']),(VF,Vv,db,bs['full']['V_original'])]:
            contain(new,[R(z).meet(x-y0) for z,x,y0 in zip(old,g,dd)])
        contain(st['mixed_direct'],[z-z1 for z,z1 in zip(W,W1)])
        contain(st['mixed_intersection'],[R(a).meet(R(b)) for a,b in zip(st['mixed_direct'],st['mixed_from_stage'])])
        return {'original_gas_response_components':count,'mixed_derivative':'ordinary partial lambda b'}
    check('original_mixed_carry_and_intersections',carry)
    def fixed_inverse():
        for i in range(4):
            assert S[i]==F(uniform['radius'][i])
            for j in range(4):
                assert C[i][j].point()==F(uniform['fixed_C'][i][j])
                assert B[i][j]==R(uniform['B'][i][j]).hi
            assert sum(B[i][j]*S[j]/S[i] for j in range(4))<=q
        assert q==R(uniform['q']).hi and 0<q<1 and det(A)>0
        for i in range(4):
            for j in range(4):
                mean=R(centre['A_Gg'][i][j])+dot(V(full['G_gg'][i][j]),[gF[k]-gcentre[k] for k in range(4)])
                assert JF[i][j].holds(mean.meet(full['A_Gg'][i][j]))
                expected=(R(i==j)-dot(C[i],[JF[k][j] for k in range(4)])).meet(R(-B[i][j],B[i][j]))
                assert EJ[i][j].holds(expected)
        return {'q':float(q),'det_I_minus_B':str(det(A)),'unchanged_preconditioner':True}
    check('original_preconditioner_and_JF_inclusion',fixed_inverse)
    def slots():
        count=0
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    a,b=R(full['G_gg'][i][j][k]),R(full['G'][i]['signed_hessian'][j][k]);assert a.holds(b) and b.holds(a);count+=1
                for label,slot in [('G_g_lambda',4),('G_g_b',5)]:
                    a,b=R(full[label][i][j]),R(full['G'][i]['signed_hessian'][j][slot]);assert a.holds(b) and b.holds(a);count+=1
            assert R(full['G_lambdab'][i]).holds(R(full['G'][i]['signed_hessian'][4][5]))
            assert R(bs['H_lambdab_source_identity'][i]).point()==0
            assert R(full['G_lambdab'][i]).holds(0);count+=1
        return {'signed_export_slot_equalities':count,'gas_fixed_H_lambdab':0}
    check('original_Hessian_parameter_slots',slots)

    ell=[2*h*clight*n2*R(bits(z[0])) for z in full['sigma_bits']]+[R(),R()]
    Dy=[1+l*(1-y[0]) for l in ell];Df=[z+l*d[0] for z,l in zip(Dy,ell)]
    QF=V(v16['linked_factors']['QF']);birth=[R() for _ in range(35)];birth[24]=R(v16['linked_factors']['M'])
    def project(vec):return [sum(vec[:33],R()),R(),R(),dot(heat,vec[:33])]
    Hphoto=project([2*l*l*n/(den**3) for l,n,den in zip(ell,QF,Df)])
    _,HBf,qf=combined(gF)
    HF=[[[(-2*h*HBf[i][j][k]+(Hphoto[i] if j==k==0 else R())).meet(full['G_gg'][i][j][k]) for k in range(4)] for j in range(4)] for i in range(4)]
    Hgl=[[-2*h*hh[i]*qf['g'][j] for j in range(4)] for i in range(4)]
    Hgbvec=project([2*l*j/(den**2) for l,j,den in zip(ell,birth,Df)])
    Hgb=[[Hgbvec[i] if j==0 else R() for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4):Hgl[i][j]=Hgl[i][j].meet(full['G_g_lambda'][i][j]);Hgb[i][j]=Hgb[i][j].meet(full['G_g_b'][i][j])
    def reconstructed_derivatives():
        for i in range(4):
            contain(ft['Hg_lambdaF'][i],Hgl[i]);contain(ft['Hg_bF'][i],Hgb[i])
            for j in range(4):contain(ft['HggF'][i][j],HF[i][j])
        assert all(z.lo>0 for z in Df)
        return {'Hgg_entries':64,'Hgl_Hgb_entries':32,'Full_birth_derivative_factor':2}
    check('independent_original_source_and_HI_derivative_reconstruction',reconstructed_derivatives)
    HFs=ft['HggF'];Hgls=M(ft['Hg_lambdaF']);Hgbs=M(ft['Hg_bF'])
    def direct_equation():
        rhs0=add(add([tensor(HFs[i],UF,VF) for i in range(4)],mv(Hgls,VF)),mv(Hgbs,UF))
        rhs0=add(rhs0,V(bs['H_lambdab_source_identity']))
        contain(c['direct_forcing'],rhs0);contain(c['direct_rhs'],add(mv(JF,W),V(c['direct_forcing'])))
        return {'equation':'JF Wd = JF W + Hgg[UF,VF] + Hgl VF + Hgb UF','factorial_rescaling':False}
    check('M3_direct_mixed_forcing',direct_equation)
    npy,qjy=sources(y);npf,qjf=sources(gF)
    DHsource=[[[ -2*h*((npy[i]['h'][j][k]-npf[i]['h'][j][k])+R(0,1)*(qjy['h'][j][k]-qjf['h'][j][k])*hh[i]) for k in range(4)] for j in range(4)] for i in range(4)]
    DHphoto=project([2*l**3*n*d[0]*(df0**2+df0*dy0+dy0**2)/(dy0**3*df0**3) for l,n,df0,dy0 in zip(ell,QF,Df,Dy)])
    DHgb=project([2*l*l*j*d[0]*(df0+dy0)/(dy0**2*df0**2) for l,j,df0,dy0 in zip(ell,birth,Df,Dy)])
    segF=[R(min(x.lo,z.lo),max(x.hi,z.hi)) for x,z in zip(y,gF)];_,qs=sources(segF)
    def endpoint_sectors():
        expected={
        'endpoint_linear_movement':scl(-1,[tensor(full['G_gg'][i],d,W) for i in range(4)]),
        'endpoint_source_Hessian_difference':scl(-1,[tensor(DHsource[i],U,Vv) for i in range(4)]),
        'endpoint_photo_Hessian_difference':scl(-U[0]*Vv[0],DHphoto),
        'endpoint_lambda_defect':scl(-1,[tensor(HFs[i],du,Vv) for i in range(4)]),
        'endpoint_birth_defect':scl(-1,[tensor(HFs[i],UF,db) for i in range(4)]),
        'endpoint_HH_gradient_difference':scl(2*h*tensor(qs['h'],d,Vv),hh),
        'endpoint_HH_birth_defect':scl(-1,mv(Hgls,db)),
        'endpoint_birth_gradient_difference':scl(-U[0],DHgb),
        'endpoint_birth_lambda_defect':scl(-1,mv(Hgbs,du))}
        for name,z in expected.items():contain(c['endpoint_correction_sectors'][name],z)
        return {'sectors':len(expected),'C2_Hessian_difference':'signed range subtraction','HI_rational_small_defect':'exact'}
    check('M4_endpoint_correction_and_M5_M6_M7',endpoint_sectors)

    def residual_sums():
        for name,vec in c['photon_jets'].items():
            assert len(vec)==35
            for j in (33,34):assert R(vec[j]['W']).point()==0
            contain(c['mixed_residual_sectors'][name],project([R(z['W']) for z in vec]))
        contain(c['r_lambdab'],[sum((R(vec[i]) for vec in c['mixed_residual_sectors'].values()),R()) for i in range(4)])
        contain(c['correlated_rhs'],add(V(c['r_lambdab']),[sum((R(vec[i]) for vec in c['endpoint_correction_sectors'].values()),R()) for i in range(4)]))
        return {'photon_sectors':7,'gas_source_sectors':9,'endpoint_correction_sectors':9,'photon_slots':35}
    check('mixed_residual_and_correlated_rhs_assembly',residual_sums)
    def inverse_for(rhs,cert):
        cr=mv(C,V(rhs));contain(cert['C_rhs'],cr)
        crs=V(cert['C_rhs']);m=cramer(A,[x.mag() for x in crs]);assert all(x>=0 for x in m)
        tail=[sum(B[i][j]*m[j] for j in range(4)) for i in range(4)]
        contain(cert['absolute_majorant'],[R(x) for x in m]);contain(cert['tail'],[R(x) for x in tail])
        contain(cert['initial'],[crs[i]+R(-tail[i],tail[i]) for i in range(4)])
        z=V(cert['initial'])
        for _ in range(3):z=[x.meet(y0) for x,y0 in zip(z,add(crs,mv(EJ,z)))]
        return z
    for name in ('direct','correlated'):
        def inverse(name=name):
            z=inverse_for(c[name+'_rhs'],c[name+'_inverse_certificate']);contain(c['d_mixed_'+name],z)
            return {'method':'Cramer exact determinants versus candidate elimination','signed_fixed_point_refinements':3}
        check(name+'_independent_inverse_certificate',inverse)
    def endpoint_intersection():
        sub=[x-z for x,z in zip(W,WF)];contain(c['d_mixed_original_subtraction'],sub)
        meet=[R(a).meet(R(b)).meet(R(d0)) for a,b,d0 in zip(c['d_mixed_direct'],c['d_mixed_correlated'],c['d_mixed_original_subtraction'])]
        contain(c['d_mixed_intersection'],meet)
        return {'simultaneous_same_function_inclusions':3}
    check('three_mixed_endpoint_inclusions_and_final_intersection',endpoint_intersection)

    Pi2,PiF,T2,dT=[R(f[k]) for k in ('Pi2','PiF','T2','DeltaT_K')]
    Fu,Fb,T2u,T2b=[R(f[k]) for k in ('DeltaT_lambda_K','DeltaT_b_K','T2_lambda','T2_b')]
    de=dot(le,d);deu=dot(le,du);deb=dot(le,db)
    Pu=R(u17['responses']['lambda']['PiF_theta']);Pb=R(u17['responses']['b']['PiF_theta'])
    def finite_temperature():
        t2w=(CT*W[3]-T2*dot(le,W)-T2u*dot(le,Vv)-T2b*dot(le,U))/Pi2
        assert R(f['T2_lambdab']).holds(t2w)
        row=[(CT*R(i==3)-(T2-dT)*le[i])/PiF for i in range(4)];contain(f['common_goal_row'],row)
        parts={'second_endpoint_mixed_temperature':-R(f['T2_lambdab'])*de/PiF,'lambda_temperature_birth_electrons':-T2u*deb/PiF,
               'birth_temperature_lambda_electrons':-T2b*deu/PiF,'lambda_defect_birth_denominator':-Fu*Pb/PiF,
               'birth_defect_lambda_denominator':-Fb*Pu/PiF,'value_defect_mixed_denominator':-dT*dot(le,W)/PiF}
        for name,x in parts.items():assert R(c['temperature_geometry_parts_K'][name]).holds(x)
        assert R(c['temperature_geometry_K']).holds(sum((R(z) for z in c['temperature_geometry_parts_K'].values()),R()))
        for name in ('direct','correlated','original_subtraction','intersection'):
            got=dot(V(f['common_goal_row']),V(c['d_mixed_'+name]))+R(c['temperature_geometry_K'])
            assert R(c['DeltaT_mixed_'+name+'_K']).holds(got)
        return {'M16_second_endpoint':True,'M15_exact_geometry_parts':6,'same_positive_PiF':True}
    check('M15_M16_exact_finite_temperature',finite_temperature)
    def interaction_sign():
        z=R(c['DeltaT_mixed_intersection_K']);ii=R(c['four_corner_interaction_K']);prior=F('1.958485175177039e-9')
        assert R(c['interaction_previous_magnitude_bound_K']).holds(prior)
        assert z.hi<0 and R(c['DeltaT_mixed_direct_K']).hi<0
        assert ii.holds(z.meet(R(-prior,prior)))
        assert ii.lo<ii.hi<0
        return {'mixed_interval_K':report_interval(z),'interaction_interval_K':report_interval(ii),
                'strict_negative_margin_K':float(-ii.hi),'old_prior_to_new_magnitude_ratio':float(prior/ii.mag()),
                'quantifier':'fixed same alpha and all lambda,b in unit square'}
    check('uniform_negative_mixed_response_and_four_corner_integral',interaction_sign)

    readout=read('P18','checks/application/readout01/results/FINITE_MIXED_READOUT.json')
    def grouped_readout():
        parts={**c['mixed_residual_sectors'],**c['endpoint_correction_sectors']};used=[]
        for name,group in readout['grouped_attribution'].items():
            names=group['sector_names'];used.extend(names)
            rhs=[sum((R(parts[n][i]) for n in names),R()) for i in range(4)]
            contain(group['combined_rhs'],rhs)
            cr=mv(C,V(group['combined_rhs']));m=cramer(A,[x.mag() for x in cr])
            tail=[sum(B[i][j]*m[j] for j in range(4)) for i in range(4)]
            val=[cr[i]+R(-tail[i],tail[i]) for i in range(4)]
            for _ in range(3):val=[v.meet(cr[i]+dot(EJ[i],val)) for i,v in enumerate(val)]
            contain(group['d_mixed'],val)
            assert R(group['temperature_K']).holds(dot(V(f['common_goal_row']),V(group['d_mixed'])))
        assert len(used)==len(set(used))==len(parts) and set(used)==set(parts)
        expected=sum((R(g['temperature_K']) for g in readout['grouped_attribution'].values()),R())+R(readout['thermal_geometry_K'])
        assert R(readout['sum_of_group_enclosures_K']).holds(expected)
        return {'disjoint_sector_partition':len(used),'groups':3,'same_full_inverse_goal_row':True}
    check('three_group_common_inverse_attribution',grouped_readout)
    def finite_readout():
        z=R(c['DeltaT_mixed_intersection_K']);orig=R(c['DeltaT_mixed_original_subtraction_K']);direct=R(c['DeltaT_mixed_direct_K'])
        prior=R(c['interaction_previous_magnitude_bound_K'])
        assert R(readout['DeltaT_lambdab_K']).holds(z)
        assert R(readout['strict_negative_margin_K']).holds(-z.hi)
        for key,expected in [('magnitude_bound_improvement_factor',prior/R(z.mag())),
                             ('original_subtraction_width_improvement_factor',R(orig.hi-orig.lo)/R(z.hi-z.lo)),
                             ('direct_mixed_implicit_width_improvement_factor',R(direct.hi-direct.lo)/R(z.hi-z.lo))]:
            assert R(readout['comparison'][key]).holds(expected)
        for key in ('mixed_mean_per_unit_area_K','birth_change_of_lambda_response_K','lambda_change_of_birth_response_K'):
            assert R(readout[key]).holds(z)
        assert readout['actual_four_corner_root_evaluations']==0 and readout['source_calls']==readout['root_solves']==readout['history_replays']==0
        return {'finite_rectangle_area_scaling':'exact FTC identity','comparison_ratios':'independent exact endpoints','root_evaluations':0}
    check('finite_rectangle_readout_and_improvement_ratios',finite_readout)

    # The photon derivative review and density bridge checks are attached below.
    extra_checks(check,c,roots,full,half,hcomp,native,p09,p11,p14,v16,st,bs,le,le1,h,n1,n2,f1,f2,df,rn,hh,chi,sources,combined,project)
    result={'schema':'WU088_HH_PHYS18_INDEPENDENT_ARITHMETIC_V1','status':'PASS' if all(x['result']=='PASS' for x in checks) else 'FAIL',
            'method':'No candidate import; unrounded rational interval arithmetic; independent Cramer inverse; photon nilpotent coefficient convolution',
            'checks':checks,'inputs':identities,'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'physical_source_calls':0,'root_solves':0,'history_replays':0}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'pass':sum(x['result']=='PASS' for x in checks),'failures':[x for x in checks if x['result']=='FAIL'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 1

def extra_checks(check,c,roots,full,half,hcomp,native,p09,p11,p14,v16,st,bs,le,le1,h,n1,n2,f1,f2,df,rn,hh,chi,sources,combined,project):
    g1=V(c['fixed_endpoint']['g1']);y=V(c['fixed_endpoint']['g2'])
    U1,V1,W1=[V(bs['first_half'][k]) for k in ('U','V','W')]
    U,Vv,W=[V(bs['second_half'][k]) for k in ('U','V','W')]
    s,su,sb,sW=[V(st[k]) for k in ('value','lambda','b','mixed_intersection')]
    E=[R(bits(z)) for z in full['energy_bits']]
    clight=R(bits(native['c_bits']));aa1=[clight*n1*R(bits(z[0])) for z in full['sigma_bits']]+[R(),R()]
    aa2=[clight*n2*R(bits(z[0])) for z in full['sigma_bits']]+[R(),R()]
    rho=R(v16['linked_factors']['rho']);alpha=[R()]+[(1-rho)*E[j]/(E[j]-E[j-1]) for j in range(1,33)]
    birth=[R() for _ in range(35)];birth[24]=R(v16['linked_factors']['M'])
    def P(v=0,u=0,b=0,w=0):return tuple(R(z) for z in (v,u,b,w))
    def pa(a,b):return tuple(x+y for x,y in zip(a,b))
    def pn(a):return tuple(-x for x in a)
    def ps(a,b):return pa(a,pn(b))
    def pm(a,b):
        # Coefficients of R[e_lambda,e_b]/(e_lambda^2,e_b^2).
        return tuple(sum((a[i]*b[j] for i in range(4) for j in range(4) if i&j==0 and i|j==k),R()) for k in range(4))
    def pc(a,z):return tuple(x*z for x in a)
    def pmeet(a,raw):return tuple(x.meet(y0) for x,y0 in zip(a,raw))
    def psum(xs):return tuple(sum((x[k] for x in xs),R()) for k in range(4))
    def absorption(g,u,v,w,a):
        A=1/(1+h*a*(1-g))
        return P(A,h*a*A**2*u,h*a*A**2*v,h*a*A**2*w+2*(h*a)**2*A**3*u*v)
    A1=[absorption(g1[0],U1[0],V1[0],W1[0],a) for a in aa1]
    A2=[absorption(y[0],U[0],Vv[0],W[0],a) for a in aa2]
    AF=[absorption(y[0],U[0],Vv[0],W[0],2*a) for a in aa2]
    tau=[pc(P(1-y[0],-U[0],-Vv[0],-W[0]),h*a) for a in aa2]
    L=[pm(t,a) for t,a in zip(tau,A2)];LF=[pc(pm(t,a),2) for t,a in zip(tau,AF)]
    C1=[pm(pm(pm(t,a),a),af) for t,a,af in zip(tau,A2,AF)]
    C2=[pm(t,c1) for t,c1 in zip(tau,C1)]
    def remap(v):
        result=[P() for _ in range(35)]
        for j in range(1,33):
            result[j-1]=pa(result[j-1],pc(v[j],alpha[j]));result[j]=pa(result[j],pc(v[j],1-alpha[j]))
        result[33]=pa(v[33],v[0]);result[34]=pc(pa(v[34],pc(v[0],E[0])),rho)
        return result
    def rm_i(v):
        result=[P() for _ in range(35)];result[0]=pn(v[0]);result[33]=v[0]
        result[34]=pa(pc(v[0],rho*E[0]),pc(v[34],rho-1))
        for j in range(1,33):
            part=pc(v[j],alpha[j]);result[j-1]=pa(result[j-1],part);result[j]=ps(result[j],part)
        return result
    def dr(v):
        z=[P() for _ in range(35)]
        for j in range(2,33):
            r=(E[j-1]-E[j-2])/(E[j]-E[j-1]);p=pc(v[j],alpha[j]*alpha[j-1])
            z[j-2]=pa(z[j-2],p);z[j-1]=ps(z[j-1],pc(p,1+r));z[j]=pa(z[j],pc(p,r))
        z[1]=pa(z[1],pc(v[1],alpha[1]*(alpha[1]+rho-1)))
        z[0]=ps(z[0],pc(v[1],alpha[1]*(alpha[1]+rho)))
        z[33]=pa(z[33],pc(v[1],alpha[1]));z[34]=pa(z[34],pc(v[1],rho*E[0]*alpha[1]))
        return z
    Z0=[P(R(z)) for z in v16['linked_factors']['common_Z0']];bz=P(R(0,1),0,1,0)
    rz=remap(Z0);r2z=remap(rz);drz=dr(Z0)
    Q1=[pa(z,pc(bz,j)) for z,j in zip(rz,birth)];Z1=[pm(a,z) for a,z in zip(A1,Q1)]
    first=next(z for z in p11['stages'] if z['stage']=='first_half')
    for j in range(33):
        Q1[j]=pmeet(Q1[j],[R(first['groups'][j]['incoming'][k]) for k in ('value','U','V','W')])
        Z1[j]=pmeet(Z1[j],[R(first['groups'][j]['outgoing_joint'][k]) for k in ('value','U','V','W')])
    Q2=[pa(z,pc(bz,j)) for z,j in zip(remap(Z1),birth)]
    P1=[pm(ps(P(1),a),z) for a,z in zip(A1,Q1)]
    for j in range(33):
        Q2[j]=pmeet(Q2[j],[R(p14['photon_state']['incoming'][k][j]) for k in ('value','U','V','W')])
        P1[j]=pmeet(P1[j],[R(first['groups'][j]['absorbed'][k]) for k in ('value','U','V','W')])
    P2=[pm(l,z) for l,z in zip(L,Q2)];Z2=[pm(a,z) for a,z in zip(A2,Q2)]
    for j in range(33):
        P2[j]=pmeet(P2[j],[R(p14['photon_state']['absorbed'][k][j]) for k in ('value','U','V','W')])
        Z2[j]=pmeet(Z2[j],[R(p14['photon_state']['outgoing'][k][j]) for k in ('value','U','V','W')])
    for j,name in ((33,'number'),(34,'energy_eV_per_H')):
        Z2[j]=pmeet(Z2[j],[R(p14['photon_state']['guard'][k][name]) for k in ('value','U','V','W')])
    gd=P(y[0],U[0],Vv[0],W[0]);sd=P(s[0],su[0],sb[0],sW[0])
    zeta=[pc(ps(pc(ps(P(1),gd),clight*R(bits(full['sigma_bits'][j][0]))*(n2-n1)),pc(sd,aa1[j])),h) for j in range(33)]+[P(),P()]
    dA=[pm(pm(z,a1),a2) for z,a1,a2 in zip(zeta,A1,A2)];dAQ=[pm(a,z) for a,z in zip(dA,Q1)]
    commute=[P() for _ in range(35)]
    for j in range(1,33):
        commute[j-1]=pa(commute[j-1],pm(pm(pm(pc(ps(P(1),gd),alpha[j]*h*(aa2[j-1]-aa2[j])),A2[j-1]),A2[j]),Q1[j]))
    rj=rm_i([P(x) for x in birth])
    ph={
        'opacity_change':[ps(pm(l,r),z) for l,r,z in zip(L,remap(dAQ),dAQ)],
        'absorption_transport_commutator':[pm(l,z) for l,z in zip(L,commute)],
        'stock_intermediate_redshift':[pn(pm(l,z)) for l,z in zip(L,rm_i(rz))],
        'stock_backward_euler':[pm(a,z) for a,z in zip(C2,r2z)],
        'remap_composition':[pm(l,z) for l,z in zip(LF,drz)],
        'birth_redshift':[pm(pm(pm(bz,l),a),z) for l,a,z in zip(L,A2,rj)],
        'birth_backward_euler':[pn(pc(pm(bz,a),j)) for a,j in zip(C1,birth)]}
    def photon_checks():
        contained=overlapped=0
        for name,vec in ph.items():
            for j,p in enumerate(vec):
                for k,key in enumerate(('value','U','V','W')):
                    actual=R(c['photon_jets'][name][j][key]);assert actual.overlaps(p[k]),(name,j,key)
                    contained+=actual.holds(p[k]);overlapped+=1
        return {'sectors':7,'slots':35,'ordinary_jet_coefficients':4,'nonempty_independent_intersections':overlapped,
                'candidate_contains_independent_expression':contained,'alternate_primitive':'analytic absorption derivative and nilpotent coefficient convolution'}
    check('seven_photon_sectors_independent_mixed_polynomial_products',photon_checks)
    Jy,Hy,qy=combined(y)
    def stage_mixed():
        source=add(add(mv(Jy,W),[tensor(Hy[i],U,Vv) for i in range(4)]),scl(dot(qy['g'],Vv),hh))
        rhs=add(scl(h,source),project([p[3] for p in P2]))
        overlap(st['mixed_from_stage'],rhs)
        return {'M13_original_35_photon_carry':'nonempty independent enclosure intersection','gas_coordinate_count':4}
    check('M13_mixed_stage_increment',stage_mixed)
    def ledger():
        rFz=[ps(a,b) for a,b in zip(r2z,drz)];QF=[pa(z,pc(bz,2*j)) for z,j in zip(rFz,birth)]
        zhat=[pm(a,z) for a,z in zip(AF,QF)];delta=[ps(z,fz) for z,fz in zip(Z2,zhat)]
        pv=[psum([vec[j] for vec in ph.values()]) for j in range(35)]
        def number(v):return pa(psum(v[:33]),v[33])
        def energy(v):return pa(psum([pc(v[j],E[j]) for j in range(33)]),v[34])
        ln=pa(number(pv),number(delta))[3]
        lu=pa(ps(energy(pv),pc(energy(P1),1-rho)),energy(delta))[3]
        assert ln.lo<=0<=ln.hi and lu.lo<=0<=lu.hi
        assert R(c['photon_ledger']['number_zero_residual']).overlaps(ln)
        assert R(c['photon_ledger']['energy_zero_residual']).overlaps(lu)
        return {'mixed_number_guard_zero_contained':True,'mixed_energy_guard_zero_contained':True,'affine_birth_mixed_injection':0}
    check('mixed_photon_number_energy_ledgers',ledger)

    def bridge(v,label):
        saved=c['density_bridge'][label]
        sg=g1[1]+2*g1[2];e1=dot(le1,g1);e2=dot(le,g1);pi1=1+f1+e1
        pull=-g1[3]*df*(1+sg)/pi1
        pv=-df*(((1+sg)*v[3]+g1[3]*(v[1]+2*v[2]))/pi1-g1[3]*(1+sg)*dot(le1,v)/(pi1**2))
        gs=list(g1);gs[3]+=pull;vs=list(v);vs[3]+=pv
        seg=[R(min(z.lo,x.lo),max(z.hi,x.hi)) for z,x in zip(g1,gs)]
        ng,qg=sources(g1);ns,qs=sources(gs);nh,qh=sources(seg)
        rem=(rn-1)+rn*df*sg/e2;rv=rn*df*(e2*(v[1]+2*v[2])-sg*dot(le,v))/(e2**2)
        scalar=ns[3]['v']+chi*ns[0]['v'];sg1=[ns[3]['g'][j]+chi*ns[0]['g'][j] for j in range(4)]
        sg2=[[ns[3]['h'][j][k]+chi*ns[0]['h'][j][k] for k in range(4)] for j in range(4)]
        ee=dot(le,gs);pis=1+f2+ee;uu=scalar/(n2*ee)
        ug=[(sg1[j]/ee-scalar*le[j]/ee**2)/n2 for j in range(4)]
        uh=[[(sg2[j][k]/ee-(sg1[j]*le[k]+sg1[k]*le[j])/ee**2+2*scalar*le[j]*le[k]/ee**3)/n2 for k in range(4)] for j in range(4)]
        xi=[R(1),R(),R(),gs[3]/pis];xiv=[R(),R(),R(),vs[3]/pis-gs[3]*dot(le,vs)/pis**2]
        khe_id=(uu-gs[0]*dot(ug,xi))/f2;khe=khe_id.meet(v16['source_bridge']['kwHe'])
        dkhe=(dot(ug,vs)-vs[0]*dot(ug,xi)-gs[0]*(tensor(uh,vs,xi)+dot(ug,xiv)))/f2
        nv=[rem*dot(ng[i]['g'],v)+rv*ns[i]['v']+(1+rem)*pull*dot(nh[i]['h'][3],v)+(1+rem)*ns[i]['g'][3]*pv for i in range(4)]
        hev=n1*df*(dot(le1,v)*khe+e1*dkhe);nv[3]+=hev
        qv=(rn-1)*dot(qg['g'],v)+rn*pull*dot(qh['h'][3],v)+rn*qs['g'][3]*pv
        for key,value in [('pull_w',pull),('pull_w_theta',pv),('re_minus1',rem),('re_theta',rv),('kHe_identity',khe_id),('kHe',khe),('D_kHe',dkhe),('He_correction_theta_per_second',hev),('HH_time_theta_per_second',qv)]:
            assert R(saved[key]).holds(value),(label,key)
        contain(saved['gstar'],gs);contain(saved['vstar'],vs);contain(saved['nonphoto_time_theta_per_second'],nv)
        return scl(h,[nv[i]+R(0,1)*qv*hh[i] for i in range(4)]),qv
    bridge_results={}
    for label,v in [('W1',W1),('V1',V1)]:
        def check_bridge(label=label,v=v):
            bridge_results[label]=bridge(v,label)
            return {'direction':label,'analytic_He_projector':'C2 source Hessian only','same_original_domain':True}
        check(label+'_density_gradient_bridge_from_original_C2_source',check_bridge)
    def gas_mixed():
        assert 'W1' in bridge_results and 'V1' in bridge_results
        seg=[R(min(z.lo,x.lo),max(z.hi,x.hi)) for z,x in zip(g1,y)];_,Hs,qs=combined(seg)
        hnp=[jet(z) for z in hcomp['nonphoto']];hq=jet(half['q'])
        H1=[[[hnp[i]['h'][j][k]+R(0,1)*hq['h'][j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
        diff=[[[H1[i][j][k]-Hy[i][j][k] for k in range(4)] for j in range(4)] for i in range(4)]
        expected={'source_time_linear':bridge_results['W1'][0],
            'stage_mixed_increment':scl(-h,mv(Jy,sW)),
            'stage_linear_curvature':scl(-h,[tensor(Hs[i],s,W1) for i in range(4)]),
            'stage_Hessian_difference':scl(h,[tensor(diff[i],U1,V1) for i in range(4)]),
            'stage_lambda_increment':scl(-h,[tensor(Hy[i],su,V1) for i in range(4)]),
            'stage_birth_increment':scl(-h,[tensor(Hy[i],U,sb) for i in range(4)]),
            'HH_gradient_time':scl(h*bridge_results['V1'][1],hh),
            'HH_gradient_birth_increment':scl(-h*dot(qy['g'],sb),hh),
            'HH_gradient_movement':scl(-h*tensor(qs['h'],s,V1),hh)}
        for name,z in expected.items():contain(c['gas_mixed_residual_sectors'][name],z)
        return {'gas_sectors':9,'M8_M9_M10_M11':'all source pieces checked'}
    check('M8_M9_M10_M11_gas_mixed_residual',gas_mixed)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ('p15','p16','p17','p18'):ap.add_argument('--'+name,type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    raise SystemExit(main(ap.parse_args()))

