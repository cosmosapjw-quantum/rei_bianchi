#!/usr/bin/env python3
"""R7: read fixed R5 enclosures and propagate their error, not the source IVP.

Subpartitions all cover the SAME original first cell. All incoming errors are
retained. B is fixed on the certified domain so four-component B*eN memory is
exact for this comparison; a different subsequent B requires the raw vector.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
import json, hashlib, time, argparse
from carry import advance
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/R5/BASS_HE_HE17_R5_20261014'
Z=Q(0); ONE=Q(1); S=[ONE,ONE,ONE,Q(32)]

def inv(a):
    n=len(a);m=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next(k for k in range(j,n) if m[k][j]);m[k],m[j]=m[j],m[k]
        d=m[j][j];m[j]=[x/d for x in m[j]]
        for k in range(n):
            if k!=j:
                d=m[k][j];m[k]=[x-d*y for x,y in zip(m[k],m[j])]
    return [row[n:] for row in m]
def mv(a,b):return [sum((x*y for x,y in zip(row,b)),Z) for row in a]
def plus(a,b):return [x+y for x,y in zip(a,b)]
def up(x,digits=80):
    n=10**digits
    return Q(-((-x.numerator*n)//x.denominator),n)
def dec(x,digits=35,upper=True):
    with localcontext() as c:
        c.prec=digits;c.rounding=ROUND_CEILING if upper else ROUND_FLOOR
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def iarr(a):return tuple(Q(x) for x in a)
def ia(a,b):return a[0]+b[0],a[1]+b[1]
def isc(a,s):return (a[0]*s,a[1]*s) if s>=0 else (a[1]*s,a[0]*s)
def ab(a):return max(abs(a[0]),abs(a[1]))
def poly_bounds(mid,whole):
    c0,c1,c2=map(iarr,mid[:3]);v=[]
    for i in range(16):
        a=Q(i,16)-Q(1,2);d=Q(1,16)
        y=ia(ia(c0,isc(c1,a)),isc(c2,a*a));yp=ia(c1,isc(c2,2*a))
        ctrl=[y,ia(y,isc(yp,d/2)),ia(ia(y,isc(yp,d)),isc(c2,d*d))]
        v.append(max(map(ab,ctrl)))
    return v,ab(iarr(whole[3]))
def remints(a,b):
    """Integral of |u-1/2|^3 and u|u-1/2|^3 on [a,b], exact."""
    lo=a-Q(1,2);hi=b-Q(1,2)
    def F(x):return (ONE if x>=0 else -ONE)*x**4/4
    def G(x):return abs(x)**5/5
    i=F(hi)-F(lo); j=G(hi)-G(lo)+i/2
    return i,j

def construct_envelopes(parent=PARENT):
    cert=json.loads((parent/'results/CERTIFICATE.json').read_text())
    detail=json.loads((parent/'results/RESIDUAL_COUPLING.json').read_text())
    mid=json.loads((parent/'results/mid_jets.json').read_text());whole=json.loads((parent/'results/whole_jets.json').read_text())
    h=Q(cert['cell_s'][1]); B=[list(map(Q,row)) for row in detail['B_scaled']];C=[list(map(Q,row)) for row in detail['C_scaled']]
    A=[[h*Q(x) for x in row] for row in cert['scaled_A']]
    K=[[h*h*Q(x) for x in row] for row in cert['scaled_BC']]
    gm=[];gr=[]
    for k in range(4):
        mu,r=poly_bounds(mid['gas'][k],whole['gas'][k]);gm.append([x/S[k] for x in mu]);gr.append(r/S[k])
    qm=[[Z]*4 for _ in range(16)];qr=[Z]*4;pr=[]
    for j in range(len(B)):
        mu,r=poly_bounds(mid['photon'][j],whole['photon'][j]);pr.append(sum(mu,Z)/16+r/32)
        assert pr[-1]<=Q(detail['photon'][j]['integral'])  # exact reassembly can be narrower than old iv rounding
        for k in range(4):
            if B[j][k]:
                hb=h*B[j][k];qr[k]+=hb*r
                for i in range(16):qm[i][k]+=hb*mu[i]
    env={'gas_mu':[[gm[k][i] for k in range(4)] for i in range(16)],'gas_rem':gr,'memory_mu':qm,'memory_rem':qr}
    return cert,h,B,C,A,K,pr,env,whole

def integrate_env(env,a,b):
    g=[Z]*4;q=[Z]*4;weighted=[Z]*4
    for i in range(16):
        l=max(a,Q(i,16));r=min(b,Q(i+1,16))
        if l>=r:continue
        for k in range(4):
            g[k]+=(r-l)*env['gas_mu'][i][k]
            q[k]+=(r-l)*env['memory_mu'][i][k]
            weighted[k]+=(r-l)*(b-(l+r)/2)*env['memory_mu'][i][k]
    ii,iu=remints(a,b)
    for k in range(4):
        g[k]+=env['gas_rem'][k]*ii;q[k]+=env['memory_rem'][k]*ii
        weighted[k]+=env['memory_rem'][k]*(b*ii-iu)
    return g,q,weighted

def solve_partition(parts,A,K,env,drop_memory=False):
    d=Q(1,parts);P=[[d*A[i][j]+d*d*K[i][j]/2 for j in range(4)] for i in range(4)]
    eta=max(sum(row,Z) for row in P)
    if eta>=1:raise ValueError('COMPARISON_GAIN_NOT_CLOSED')
    R=inv([[Q(i==j)-P[i][j] for j in range(4)] for i in range(4)])
    assert all(v>=0 for row in R for v in row)
    eg=[Z]*4;m=[Z]*4;acc=[Z]*4;qc=[Z]*4;records=[]
    for i in range(parts):
        a=Q(i,parts);b=Q(i+1,parts);dg,dq,dw=integrate_env(env,a,b)
        incoming=[Z]*4 if drop_memory else eg;im=[Z]*4 if drop_memory else m
        exact=advance(incoming,im,plus(dg,dw),R,d)
        D=[up(x) for x in exact]
        assert all(x>=y>=0 for x,y in zip(D,exact))
        acc=plus(acc,[d*x for x in D]);qc=plus(qc,dq);m=plus(mv(K,acc),qc);eg=D
        records.append({'a':str(a),'b':str(b),'gas_sup':[str(x) for x in D],
                        'incoming_gas':[str(x) for x in incoming], 'incoming_memory':[str(x) for x in im]})
    return {'parts':parts,'gain':eta,'gas_end':eg,'photon_memory_end':m,'integrated_gas_bound':acc,'records':records}

def main():
    t=time.perf_counter();cert,h,B,C,A,K,pr,env,whole=construct_envelopes()
    nh=Q(whole['env']['nh'][0][1]);weight=[ONE,Q(3,38),Q(6,38),Z]
    pref=Q(299792458)*10**6*h*nh
    runs=[]
    for n in [1,2,4,8,16,32,64]:
        r=solve_partition(n,A,K,env);rad=pref*sum((x*y for x,y in zip(weight,r['integrated_gas_bound'])),Z)
        r['column_radius']=rad;runs.append(r)
        print(n,dec(rad),flush=True)
    chosen=runs[-1]
    raw=[h*sum((x*y for x,y in zip(c,chosen['integrated_gas_bound'])),Z)+rr for c,rr in zip(C,pr)]
    direct=[h*sum((B[j][k]*raw[j] for j in range(len(B))),Z) for k in range(4)]
    assert direct==chosen['photon_memory_end']
    cref=list(map(Q,cert['reference_column_interval']));rad=chosen['column_radius']
    ci=[cref[0]-rad,cref[1]+rad];sig=Q('6.6524587051e-29');tau=[sig*x for x in ci]
    prob=[tau[0]-tau[0]**2/2,tau[1]-tau[1]**2/2+tau[1]**3/6]
    old=Q(cert['column_radius_m2_inv']['rational'])
    false=solve_partition(64,A,K,env,drop_memory=True)
    false_rad=pref*sum((x*y for x,y in zip(weight,false['integrated_gas_bound'])),Z)
    outcome={'stage':'R7','scope':'same original first cell; partitioned error comparison, not new source evolution',
      'original_cell_s':cert['cell_s'],'partition_rows':[{'parts':r['parts'],'gain_upper':dec(r['gain']),
         'radius_exact':str(r['column_radius']),'radius_upper':dec(r['column_radius']),
         'gas_end_upper':[dec(x*S[k]) for k,x in enumerate(r['gas_end'])]} for r in runs],
      'chosen_parts':64,'old_radius_exact':str(old),'chosen_radius_exact':str(rad),
      'radius_ratio_exact':str(rad/old),'relative_radius_reduction':dec(1-rad/old),
      'column_interval_exact':list(map(str,ci)), 'tau_interval_exact':list(map(str,tau)),
      'tau_outward':[dec(tau[0],35,False),dec(tau[1])],
      'conditional_probability_exact':list(map(str,prob)), 'conditional_probability_outward':[dec(prob[0],35,False),dec(prob[1])],
      'wrong_reset_radius_upper':dec(false_rad),'wrong_reset_status':'INTENTIONAL_INVALID_COMPARISON; NOT_A_BOUND',
      'compression_identity_verified':True,'rounding':'exact rational then outward ceiling to80decimal places per gas step',
      'parent_interval_coefficients_reused':True,'source_RHS_calls':0,'source_ODE_calls':0,
      'new_second_stored_cell_certificate':None,'seconds':time.perf_counter()-t}
    (ROOT/'results/R7_RESULT.json').write_text(json.dumps(outcome,indent=2))
    packet={'source_interval_s':cert['cell_s'],'fixed_reference_sha256':'7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be',
      'gas_scale':['1','1','1','32 eV/H'], 'gas_error_end_scaled':list(map(str,chosen['gas_end'])),
      'photon_error_end_raw_exact':list(map(str,raw)), 'photon_units':'original reference-volume cm^-3',
      'compressed_hB_error_exact':list(map(str,direct)),
      'compression_scope':'hB fixed first-cell majorant; new cell must use its actual B on the raw error vector',
      'next_reference_jump':None,'next_cell_majorants':None,'not_a_second_cell_certificate':True}
    (ROOT/'results/ENDPOINT_MEMORY.json').write_text(json.dumps(packet,indent=2))
    (ROOT/'results/SUBCELL_TRACE.json').write_text(json.dumps(chosen['records'],indent=2))
    print('R7_DONE',outcome['seconds'],flush=True)
if __name__=='__main__':main()
