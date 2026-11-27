"""Whole-cell Taylor/Bernstein bounds and a source-derived positive comparison.
Reads computed interval jets; never calls an ODE solver or imports native code.
"""
from warm_interval import *
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import hashlib

def fromrec(a):return bound(Q(a[0]),Q(a[1]))
def display(q,digits=35,up=True):
    with localcontext() as c:
        c.prec=digits;c.rounding=ROUND_CEILING if up else ROUND_FLOOR
        return str(Decimal(q.numerator)/Decimal(q.denominator))
def pack(q):return {'rational':str(q),'upper_display':display(q)}
def residual_bounds(mid,whole,parts=16):
    c=[fromrec(mid[k]) for k in range(3)];a3=absup(fromrec(whole[3]));gmax=Q(0);integ=Q(0);weighted=Q(0)
    for i in range(parts):
        aa=Q(i,parts)-Q(1,2);bb=Q(i+1,parts)-Q(1,2);d=bb-aa
        y=c[0]+c[1]*V(aa)+c[2]*V(aa*aa);yp=c[1]+2*c[2]*V(aa)
        ctrl=[y,y+yp*V(d/2),y+yp*V(d)+c[2]*V(d*d)]
        mx=max(map(absup,ctrl));gmax=max(gmax,mx);integ+=d*mx;weighted+=d*(Q(1,2)-(aa+bb)/2)*mx
    return {'sup':gmax+a3/8,'integral':integ+a3/32,'weighted_integral':weighted+a3/64,'third_coeff':a3,'polynomial_sup':gmax}

def inverse(m):
    n=len(m);a=[r[:]+[Q(i==j) for j in range(n)] for i,r in enumerate(m)]
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]);a[j],a[k]=a[k],a[j]
        p=a[j][j];a[j]=[v/p for v in a[j]]
        for k in range(n):
            if k!=j:
                p=a[k][j];a[k]=[x-p*y for x,y in zip(a[k],a[j])]
    return [r[n:] for r in a]

def main():
    ts=time.perf_counter();s=WarmSource();mid=json.loads((ROOT/'results/mid_jets.json').read_text());whole=json.loads((ROOT/'results/whole_jets.json').read_text())
    with np.load(ROOT/'inputs/P01_STATE.npz',allow_pickle=False) as archived_state:
        left_state=archived_state['states'][:s.n,1]
        right_state=archived_state['states'][:s.n,2]
        exact_left_right=all(s.coeff[i][0]==Q.from_float(float(left_state[i])) and
                              sum(s.coeff[i])==Q.from_float(float(right_state[i])) for i in range(s.n))
    assert exact_left_right, 'SECOND_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
    scale=[Q(1),Q(1),Q(1),Q(32)];h=s.hq
    rg=[residual_bounds(a,b) for a,b in zip(mid['gas'],whole['gas'])]
    rp=[residual_bounds(a,b) for a,b in zip(mid['photon'],whole['photon'])]
    inputs=json.load(open(ROOT/'inputs/HH_P01_COMPARISON.json'));g0=list(map(Q,inputs['gas_initial_exact']));rad=list(map(Q,inputs['gas_radii']))
    incoming=json.loads((ROOT/'inputs/ENDPOINT_MEMORY_R7.json').read_text())
    ep=[Q(x) for x in incoming['photon_error_end_raw_exact']]
    eg=[Q(x) for x in incoming['gas_error_end_scaled']]
    assert len(ep)==2904 and len(eg)==4 and all(x>=0 for x in ep+eg)
    box=[bound(x-r,x+r) for x,r in zip(g0,rad)];x,y,z,w=box
    nh=fromrec(whole['env']['nh'][0]);vr=fromrec(whole['env']['vr'][0]);HH=fromrec(whole['env']['H'][0]);cf=C/vr
    B=[];Cg=[];GM=[V(0)]*3;QM=[V(0)]*3;Gref=[V(0)]*3;Qref=[V(0)]*3;Ntrue=[];Nref=[];transparent=0
    for j,node in enumerate(whole['nodes']):
        E=fromrec(node['E']);sig=list(map(fromrec,node['sigma']));src=fromrec(node['source'])
        if all(hi(a)==0 and lo(a)==0 for a in sig):transparent+=1
        nr=max(s.controls[4+j]);nl=min(s.controls[4+j]);assert nl>=0
        # Positivity and diagonal nonnegative absorption give this exact true-history envelope.
        nt=s.coeff[4+j][0]+ep[j]+h*max(Q(0),hi(src));Ntrue.append(nt);Nref.append(nr)
        for a in range(3):
            GM[a]=GM[a]+cf*sig[a]*V(nt);QM[a]=QM[a]+cf*sig[a]*V(nt)*(E-CHI[a])
            Gref[a]=Gref[a]+cf*sig[a]*V(nr);Qref[a]=Qref[a]+cf*sig[a]*V(nr)*(E-CHI[a])
        bc=[cf*(1-x)*sig[0],cf*((1-y-z)*sig[1]-y*sig[2]),cf*y*sig[2],
            cf*((1-x)*sig[0]*(E-CHI[0])+FF*(1-y-z)*sig[1]*(E-CHI[1])+FF*y*sig[2]*(E-CHI[2]))]
        B.append([absup(bc[i])/scale[i] for i in range(4)])
        cg=[-C*nh*sig[0],C*nh*FF*(sig[2]-sig[1]),-C*nh*FF*sig[1],V(0)]
        Cg.append([absup(cg[i])*nr*scale[i] for i in range(4)])
    # Independent direct A over the old gas box and a NEW positive photon envelope.
    # This removes any unverified dependence on old photon moment-domain claims.
    gamma=[bound(0,hi(a)) for a in GM];qphoto=[bound(0,hi(a)) for a in QM]
    AA=[[Q(0)]*4 for _ in range(4)]
    for k in range(4):
        g=[Jet([box[i],1 if i==k else 0]) for i in range(4)]
        f=s.gas(g,Jet.constant(nh,1),Jet.constant(HH,1),[Jet.constant(a,1) for a in gamma],[Jet.constant(a,1) for a in qphoto])
        for i in range(4):AA[i][k]=absup(f[i].c[1])*scale[k]/scale[i]
    BC=[[sum((B[j][i]*Cg[j][k] for j in range(len(B))),Q(0)) for k in range(4)] for i in range(4)]
    PP=[[h*AA[i][k]+h*h*BC[i][k]/2 for k in range(4)] for i in range(4)]
    eta=max(sum(r,Q(0)) for r in PP);assert eta<1
    forcG=[rg[i]['integral']/scale[i] for i in range(4)]
    forcP=[h*sum((B[j][i]*rp[j]['weighted_integral'] for j in range(len(B))),Q(0)) for i in range(4)]
    carried_photon=[h*sum((B[j][i]*ep[j] for j in range(len(B))),Q(0)) for i in range(4)]
    dd=[a+b+eg[i]+carried_photon[i] for i,(a,b) in enumerate(zip(forcG,forcP))]
    inv=inverse([[Q(i==k)-PP[i][k] for k in range(4)] for i in range(4)]);assert all(v>=0 for r in inv for v in r)
    errors=[sum((inv[i][k]*dd[k] for k in range(4)),Q(0)) for i in range(4)]
    egas=[errors[i]*scale[i] for i in range(4)]
    chierr=egas[0]+Q(3,38)*(egas[1]+2*egas[2])
    colrad=Q(299792458)*10**6*h*hi(nh)*chierr
    CT=2*EV/(3*KB);Pibox=1+FF+x+FF*(y+2*z);Tbox=CT*w/Pibox
    Terr=hi((CT*V(egas[3])+Tbox*V(chierr))/Pibox)
    # The joint reference's exact column, analytically integrated Taylor polynomial plus derivative remainder.
    def coljet(z):
        ng=s.volume(z).reciprocal()*s.nh0
        gg=[polynomial(s.coeff[i],z) for i in range(3)];chi=gg[0]+(gg[1]+2*gg[2])*FF
        return ng*chi*(V(299792458)*10**6*s.h)
    jc=coljet(Jet.variable(V('.5'),7));jw=coljet(Jet.variable(bound(0,1),7))
    center=sum((jc.c[k]/((k+1)*2**k) for k in range(0,7,2)),V(0));rem=absup(jw.c[7])/(8*2**7)
    cref=center+bound(-rem,rem);cfull=cref+bound(-colrad,colrad)
    sigma=V('6.6524587051e-29');tau=cfull*sigma
    tl,tu=endpoints(tau);assert 0<tl<tu<1
    prlo=tl-tl*tl/2;prhi=tu-tu*tu/2+tu**3/6
    rows=json.load(open(ROOT/'inputs/P01_INTERVAL.json'))['history'];old=Q(299792458)*10**6*h*(Q.from_float(rows[1]['ne_cm3'])+Q.from_float(rows[2]['ne_cm3']))/2
    bias=cref-V(old)
    residual_detail={'incoming_gas_scaled':list(map(str,eg)), 'incoming_photon_scaled_force':list(map(str,carried_photon)),'gas':[{k:str(v) for k,v in d.items()} for d in rg], 'photon':[{k:str(v) for k,v in d.items()} for d in rp], 'B_scaled':[[str(x) for x in r] for r in B], 'C_scaled':[[str(x) for x in r] for r in Cg], 'true_photon_upper_raw':list(map(str,Ntrue)),'reference_photon_upper_raw':list(map(str,Nref))}
    (ROOT/'results/RESIDUAL_COUPLING.json').write_text(json.dumps(residual_detail))
    summary={'stage':'HE18_C3','cell_s':[str(h),str(2*h)],'reference':'second-cell FIXED_REFERENCE.npz exact dyadic coefficients', 'incoming_gas_scaled':list(map(str,eg)), 'incoming_photon_to_gas_scaled':list(map(str,carried_photon)),
      'arithmetic':'mpmath.iv 70dps; exact rational endpoint extraction/assembly',
      'method':'degree2 midpoint residual + whole-cell third derivative Taylor remainder;16Bernstein subintervals',
      'gas_sup_per_s':[display(rg[i]['sup']/h/scale[i]) for i in range(4)],
      'gas_integral_scaled':list(map(pack,forcG)),'photon_forcing_scaled':list(map(pack,forcP)),
      'gain':pack(eta),'gain_amplification':pack(1/(1-eta)),'scaled_A':[[str(v) for v in r] for r in AA],
      'scaled_BC':[[str(v) for v in r] for r in BC],'scaled_P':[[str(v) for v in r] for r in PP],
      'gas_error_components':list(map(pack,egas)), 'electron_perH_error':pack(chierr),'temperature_error_K':pack(Terr),
      'column_radius_m2_inv':pack(colrad),'reference_column_interval':record(cref),'reference_column_integration_remainder':pack(rem),
      'true_column_interval':record(cfull),'true_depth_interval':record(tau),'true_probability_interval':[str(prlo),str(prhi)],
      'column_display':[display(lo(cfull),up=False),display(hi(cfull))],
      'tau_display':[display(tl,up=False),display(tu)],'probability_display':[display(prlo,up=False),display(prhi)],
      'reference_bias_to_old_ne_PL':record(bias),'bias_display':[display(lo(bias),up=False),display(hi(bias))],
      'transparent_count':transparent,'first_initial_match':exact_left_right,'next_physical_cell_incoming_included':True,
      'A_domain':'direct full warm gas Jacobian over original entire-tube gas box and nonnegative true photon envelope P(t1)+incoming_etaN+h*Sbar; no inherited numerical photon moments needed',
      'BC_domain':'direct B and kappa-g derivative times fixed-reference Bernstein photon maximum; not factorization of inherited BC',
      'photon_moment_upper_true_Gamma':list(map(record,GM)),'photon_moment_upper_ref_Gamma':list(map(record,Gref)),
      'A_derivative_evaluations':4,'nonlinear_source_IVP_calls':0,'whole_history_fine_certificate':None,
      'inherited_global_coarse_preserved':True,'seconds_assembly':time.perf_counter()-ts}
    (ROOT/'results/CERTIFICATE.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:summary[k] for k in ['gas_sup_per_s','gain','gas_error_components','column_radius_m2_inv','tau_display','probability_display','bias_display','seconds_assembly']},indent=2))
if __name__=='__main__':main()
