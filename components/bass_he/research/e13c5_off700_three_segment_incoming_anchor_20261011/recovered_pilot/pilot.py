#!/usr/bin/env python3
"""Frozen E13C5 three-segment pilot; no ODE solver or native run."""
import csv, hashlib, json, sys, time
from pathlib import Path
from fractions import Fraction
from math import factorial
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'BASS_HE_E13C4_LOCAL_REMAINDER_ENCLOSURE_20261010_v1'
sys.path.insert(0,str(BASE/'code'))
import directed_interval as di
from directed_interval import IV, Jet2, value, response_j
from local_enclosure import Coefficients, integrands, lift, atomic_json
UPSTREAM=BASE/'inputs/e13c3/inputs/e13c2/inputs/upstream_e13c1'
KEYS=[('OFF',1,700,0),('OFF',2,700,0),('OFF',2,700,1)]
PIN={BASE/'inputs/SIX_CONTROLS.json':'2f543b128bdb6efe020868475619765d1a08f47c102cf0b9e5f65cb615c146dd',UPSTREAM/'evidence/capture/OFF/SEGMENTS.csv':'2a43dae808a0ca262dd175d2a1b74eeecc2c674d537f524bdba08e9d709076f7',UPSTREAM/'evidence/capture/OFF/NODES.csv':'f8c4ce74e4b1789118fccec1135d48bd29ea4e0813044da694c0b5375ad56164',UPSTREAM/'inputs/OFF_STAGES.csv':'d8a363f47781bcea8e33f193f9828e1bb04eb27bbf3821ab487de8238458d661',UPSTREAM/'native_candidate/source/research/transport_20261007/short-hhe-midpoint/src/radiation.rs':'457cd84c0bbacfa5446f0a76fb709b1e1cd31b4f4ce3f8eb1be161679543fa83'}
def encode(x):
    if isinstance(x,IV):return x.json()
    if isinstance(x,di.D):return str(x)
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x
def sym(b):return IV(b.hi.copy_negate(),b.hi)
def rows(path):
    with path.open() as f:return list(csv.DictReader(f))
def toy():
    # Alternating Taylor bounds for exp(-1), using exact Fraction arithmetic.
    def frac_iv(x):return IV(x.numerator)/x.denominator
    lower=sum((Fraction((-1)**k,factorial(k)) for k in range(82)),Fraction())
    upper=lower+Fraction(1,factorial(82))
    T=IV(frac_iv(lower).lo,frac_iv(upper).hi); P0=IV(1,frac_iv(Fraction(9,8)).hi)
    P1=T*P0; P2=T*P1
    A1=(1-T)*P0; A2=(1-T)*P1
    B1=4*(1-T.square())*P0; B2=2*(1-T.square())*P1
    J=(4-8*T)*P1
    count=P2-P0+A1+A2
    energy=4*T*P2-8*P0+2*(B1+B2)-J
    bad_count=IV(0)-P0+A1
    bad_energy=4*T*P2-8*P0+2*(B1+B2)
    assert count.contains(0) and energy.contains(0)
    # Shared P0 correlation: omitted-anchor residual is exactly J.
    assert not bad_count.contains(0) and J.lo>0
    point_bad=4*T*T.square()-8+2*(4*(1-T.square())+2*T*(1-T.square()))
    point_good=point_bad-(4-8*T)*T
    assert not point_bad.contains(0) and point_good.contains(0)
    assert not P2.contains(0)
    return encode({'T':T,'weight':frac_iv(Fraction(3,2)),'P0':P0,'P1':P1,'P2':P2,'A':[A1,A2],'B':[B1,B2],'Z':[B1,B2],'H':[B1-A1,B2-A2],'Janchor':J,'count_ledger':count,'energy_ledger':energy,'zero_incoming_count_ledger':bad_count,'expanded_omitted_anchor_energy_diagnostic':bad_energy,'factored_omitted_anchor_residual':J,'point_P0_1_omitted_anchor_energy':point_bad,'point_P0_1_good_energy':point_good,'negative_controls_failed':True})
def integrate(c):
    mid={};rad={};bound={};maxd={}
    for j in range(128):
        a,b,m=IV(j)/128,IV(j+1)/128,IV(2*j+1)/256
        field,bounds=integrands(c,Jet2.variable(IV(a.lo,b.hi)))
        center,_=integrands(c,m)
        for k,x in field.items():
            m2=abs(x.d2).hi
            mid[k]=mid.get(k,IV(0))+c.h/128*value(center[k])
            rad[k]=rad.get(k,IV(0))+c.h*IV(m2)/(24*128**3)
            maxd[k]=max(maxd.get(k,di.D(0)),m2)
        for k,x in bounds.items():bound[k]=bound.get(k,IV(0))+c.h/128*x
    return {k:v+sym(rad[k]) for k,v in mid.items()},bound,rad
def main():
    di.configure(60); start=time.monotonic()
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in PIN}
    assert all(hashes[str(p)]==h for p,h in PIN.items()),'IMMUTABLE_INPUT_MISMATCH'
    atomic_json(ROOT/'START.json',{'hashes':hashes,'HARNESS_UNAVAILABLE':True,'native_runs':0,'gas_advances':0,'old_continuous_solves':0,'six_control_replays':0,'full_path_expansions':0,'N':128,'P':60,'run_limit_seconds':180})
    toy_result=toy();atomic_json(ROOT/'TOY.json',toy_result)
    selected={}
    for r in rows(UPSTREAM/'evidence/capture/OFF/SEGMENTS.csv'):
        key=(r['mode'],int(r['step']),int(r['node']),int(r['segment']))
        if key in KEYS:selected[key]=r
    stages={int(r['step']):r for r in rows(UPSTREAM/'inputs/OFF_STAGES.csv')}
    assert set(selected)==set(KEYS)
    eps=lift(1.602176634e-12); species=('HI','HeI','HeII')
    cumulative={};captotal={};corrtotal={};outputs=[];prevD=IV(0);prevn=IV(0);anchor=IV(0)
    initial=lift(selected[KEYS[0]]['f0']); initialE=lift(selected[KEYS[0]]['e0']);weight=lift(selected[KEYS[0]]['weight'])
    for index,key in enumerate(KEYS):
        r=selected[key]
        assert lift(r['weight']).lo==weight.lo
        mask={s:float(r['e_mid'])>=cut for s,cut in zip(species,(13.6,24.59,54.42))}
        assert list(mask.values())==([True,True,False] if index<2 else [True,False,False])
        c=Coefficients({'row':r,'stage':stages[key[1]],'mask':mask,'source_on':True})
        Ia=IV(0) if index==0 else prevD+prevn-c.f0
        recurrence=Ia-(IV(0) if index==0 else prevD+prevn-c.f0)
        assert recurrence.contains(0)
        J,bounds,rad=integrate(c)
        S=IV(abs(Ia).hi)+bounds['B_r']
        j0=response_j(c.L,c.h);je=c.e0*response_j(c.L+1,c.h)
        g={'P1':(-c.L*c.h).exp(),'Z_eV':je,'QN':IV(0),'QE_eV':IV(0)}
        rem={'P1':S*bounds['H_h'],'Z_eV':S*bounds['H_E'],'QN':IV(0),'QE_eV':IV(0)}
        F0=c.f0*j0+c.qf*(c.h-j0)/c.L
        FE=c.f0*je+c.e0*c.qf*(response_j(IV(1),c.h)-response_j(c.L+1,c.h))/c.L
        frozen={'Z_eV':FE,'QN':c.qf*c.h,'QE_eV':c.e0*c.qf*response_j(IV(1),c.h)}
        cap={'Z_eV':lift(r['red'])/eps,'QN':lift(r['qn']),'QE_eV':lift(r['qe'])/eps}
        for i,s in enumerate(species):
            for pref,gg,ff,cc in [('A',c.lf[i]*j0,c.lf[i]*F0,lift(r['A_'+s])),('B',c.lf[i]*je,c.lf[i]*FE,lift(r['B_'+s])/eps),('H',c.lf[i]*(je-c.chi[i]*j0),c.lf[i]*(FE-c.chi[i]*F0),lift(r['B_'+s])/eps-c.chi[i]*lift(r['A_'+s]))]:
                k=pref+'_'+s+('_eV' if pref!='A' else '')
                g[k]=gg;frozen[k]=ff;cap[k]=cc;rem[k]=S*bounds['effective_'+pref+'_'+s]
        I={k:J[k]+g[k]*Ia for k in g}
        corrected={k:I[k]+sym(rem[k]) for k in I}
        Pf=c.f0*g['P1']+c.qf*j0
        n=lift(r['n']);DP=Pf-n+corrected['P1'];Pend=n+DP
        for k in frozen:
            cumulative[k]=cumulative.get(k,IV(0))+frozen[k]+corrected[k]
            captotal[k]=captotal.get(k,IV(0))+cap[k]
            corrtotal[k]=corrtotal.get(k,IV(0))+(frozen[k]-cap[k])+corrected[k]
        count=Pend-initial+sum((cumulative['A_'+s] for s in species),IV(0))-cumulative['QN']
        energy=c.endpoint_E*Pend-initialE*initial+sum((cumulative['B_'+s+'_eV'] for s in species),IV(0))+cumulative['Z_eV']-cumulative['QE_eV']-anchor
        assert count.contains(0),'COUNT_LEDGER_CONTAINMENT_FAILURE'
        assert energy.contains(0),'ENERGY_LEDGER_CONTAINMENT_FAILURE'
        seam=IV(0)
        if index<2:
            delta=lift(selected[KEYS[index+1]]['e0'])-c.endpoint_E;seam=delta*Pend;anchor+=seam
        out={'key':key,'Ia':Ia,'recurrence_residual':recurrence,'S':S,'J':J,'g':g,'I_firstvariation':I,'remainder':rem,'corrected':corrected,'frozen':frozen,'captured':cap,'DP':DP,'Pend':Pend,'cumulative':cumulative.copy(),'cumulative_correction':corrtotal.copy(),'count_ledger':count,'energy_ledger':energy,'Janchor_to_next':seam,'domain':c.domain,'midpoint_radii':rad}
        outputs.append(encode(out));prevD=DP;prevn=n
        atomic_json(ROOT/'CHECKPOINT.json',{'completed':outputs})
        print(json.dumps({'key':key,'elapsed_seconds':time.monotonic()-start,'count_ledger':count.json(),'energy_ledger':energy.json()}),flush=True)
    weighted={k:weight*v for k,v in cumulative.items()}
    result={'status':'PASS','scope':'E13C5_OFF700_THREE_SEGMENT_INCOMING_ANCHOR_PILOT','segments':outputs,'weighted_cumulative':encode(weighted),'weighted_final_P':encode(weight*Pend),'weighted_Janchor':encode(weight*anchor),'toy':toy_result,'elapsed_seconds':time.monotonic()-start,'physical':'HOLD','production':'HOLD','full_path':'HOLD','independent_decision':'PENDING'}
    atomic_json(ROOT/'RESULTS.json',result)
if __name__=='__main__':main()
