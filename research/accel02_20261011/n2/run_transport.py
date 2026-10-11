#!/usr/bin/env python3
"""Whole-interval HM12 radiation diagnostic in explicitly prescribed ion bath.

The bath fractions are not evolved: this diagnoses photon chronology, not a
reionization solution. Atomic values use the exact pinned Verner formula. Gas
feedback acceptance is evaluated separately by the coupled integration owner.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
from characteristics import make_grid, geometry_nodes, source_reference, exponential_step

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PIN=REPO/'research/physical_provider_20261010'
sys.path.insert(0,str(PIN))
from background import BianchiBackground
from hm12_data import load_hm12
C=29979245800.
CHI=np.array([13.598434599702,24.587389011,54.41776])


def sigma(energy):
    """Literal vector translation of native AtomicProvider::cross_section.

    Above50keV cells are inactive storage with exactly zero N,S in this closed
    band model. This routine does not extend Verner's supported cross section.
    """
    result=np.zeros((len(energy),3))
    params=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),
            (24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
            (54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
    for j,(eth,e0,s0,ya,p,yw,y0,y1) in enumerate(params):
        active=(energy>=eth)&(energy<=50000.)
        x=energy[active]/e0-y0; y=np.sqrt(x*x+y1*y1)
        result[active,j]=s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18
    return result


def execute(r,nt,ne,nmu):
    start=time.perf_counter()
    bg=BianchiBackground(r=r,z_i=15.9,t_max=1e17)
    tf=bg.time_of_redshift(4.)
    final=bg.at(tf)
    qmax=50000*max(final['scale_rel'])
    q,m,w=make_grid(ne,nmu,qmax)
    tables=load_hm12()
    init=np.zeros(len(q)); keep=q<=50000
    init[keep]=tables['uvb'].photon_number_log(q[keep],15.9)*w[keep]
    n=init.copy(); source_sum=absorbed=source_energy=abs_energy=work=0.
    absorbed_species=np.zeros(3)
    x=np.linspace(0,np.log(16.9/5),nt+1)
    zz=16.9/np.exp(x)-1; zz[0]=15.9; zz[-1]=4.
    ts=np.array([bg.time_of_redshift(float(z)) for z in zz])
    times={}; rows=[]
    initial_energy=float(np.dot(n,q))
    def measure(t):
        g=bg.at(t); e,mu,_=geometry_nodes(q,m,g); sig=sigma(e)
        photons=n/g['a_rel']**3
        gam=C*np.sum(sig*photons[:,None],axis=0)
        photoheat=C*np.sum(sig*photons[:,None]*np.maximum(e[:,None]-CHI,0),axis=0)
        nn=float(n.sum()); ee=float(np.dot(n,e))
        rows.append(dict(t_s=t,z=g['z'],photon_reference=nn,energy_reference_eV=ee,
            Gamma=gam.tolist(),heat_per_target_eV_s=photoheat.tolist(),
            active_number_reference=[float(n[e>=threshold].sum()) for threshold in [13.60,24.59,54.42]],
            source_reference=source_sum,absorbed_reference=absorbed,
            absorbed_species_reference=absorbed_species.tolist(),
            photon_ledger=(nn+absorbed-init.sum()-source_sum)/max(init.sum()+source_sum,1e-100),
            energy_ledger=(ee+abs_energy+work-initial_energy-source_energy)/max(initial_energy+source_energy,1e-100)))
    measure(0.)
    maxstage=0.
    for i in range(nt):
        t0,t1=ts[i:i+2]; tm=.5*(t0+t1); dt=t1-t0
        g0,gm,g1=bg.at(float(t0)),bg.at(float(tm)),bg.at(float(t1))
        e0,_,_=geometry_nodes(q,m,g0); em,_,_=geometry_nodes(q,m,gm); e1,_,_=geometry_nodes(q,m,g1)
        s=source_reference(q,m,w,gm,tables['emissivity'])
        if np.any((em>50000)&((n!=0)|(s!=0))): raise ValueError('UNSUPPORTED_OCCUPIED_ENERGY')
        # External prescribed bath, fixed ion fractions (.1,.1,0), expanding n.
        lower=np.array([.9*gm['nH'],.9*gm['nHe'],.1*gm['nHe']])
        opacity=C*sigma(em)*lower
        step=exponential_step(n,s,opacity,dt)
        new=step['number']; an=step['absorbed_by_species']
        sn=float(step['source_added'].sum()); aa=float(an.sum())
        maxstage=max(maxstage,abs(new.sum()+aa-n.sum()-sn)/max(n.sum()+sn,1e-100))
        work+=float(np.dot(n,e0-em)+np.dot(new,em-e1))
        source_energy+=float(np.dot(step['source_added'],em));abs_energy+=float(np.dot(an.sum(axis=1),em))
        source_sum+=sn;absorbed+=aa;absorbed_species+=an.sum(axis=0);n=new
        if (i+1)%(nt//64)==0: measure(float(t1))
    return dict(r=r,nsteps=nt,n_energy=ne,n_mu=nmu,n_nodes=len(q),q_band=[10,qmax],
        elapsed_s=time.perf_counter()-start,max_stage_ledger=maxstage,history=rows,
        status='EXECUTED_DIAGNOSTIC_NOT_CHEMISTRY',
        source_sha=tables['emissivity'].source_sha256,uvb_sha=tables['uvb'].source_sha256,
        background_sha=hashlib.sha256((PIN/'background.py').read_bytes()).hexdigest())


def compare(a,b):
    errors={}
    for key in ['photon_reference','energy_reference_eV','Gamma','heat_per_target_eV_s',
                'active_number_reference','source_reference','absorbed_reference','absorbed_species_reference']:
        aa=np.array([r[key] for r in a['history']]); bb=np.array([r[key] for r in b['history']])
        scale=np.max(np.abs(bb),axis=0)
        errors[key]=float(np.max(np.abs(aa-bb)/np.where(scale>0,scale,1.)))
    return errors


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--steps',type=int,default=2048);p.add_argument('--energy',type=int,default=512)
    p.add_argument('--summarize-existing',action='store_true')
    args=p.parse_args()
    if not args.summarize_existing: args.output.mkdir(parents=True,exist_ok=False)
    results=[]
    for r in [0.,.05]:
        cases=[(args.steps,args.energy,4),(2*args.steps,args.energy,4),
               (2*args.steps,2*args.energy,8)]
        group=[]
        for nt,ne,nmu in cases:
            path=args.output/f'r{r}_t{nt}_e{ne}_m{nmu}.json'
            case=json.loads(path.read_text()) if args.summarize_existing else execute(r,nt,ne,nmu)
            group.append(case)
            if not args.summarize_existing:
                path.write_text(json.dumps(case,indent=2)+'\n')
                print(json.dumps({k:v for k,v in case.items() if k!='history'}),flush=True)
        temporal=compare(group[0],group[1]);spectral=compare(group[1],group[2])
        ledger=float(max(abs(row[k]) for case in group for row in case['history'] for k in ['photon_ledger','energy_ledger']))
        results.append(dict(r=r,temporal=temporal,spectral_angular=spectral,max_ledger=ledger,
            temporal_pass=max(temporal.values())<=2e-6,spectral_pass=max(spectral.values())<=1e-3,
            ledger_pass=ledger<=1e-10))
    passed=all(x['temporal_pass'] and x['spectral_pass'] and x['ledger_pass'] for x in results)
    report=dict(status='PASS_DIAGNOSTIC' if passed else 'FAIL_REFINEMENT',results=results,
                coupled_gas_status='NOT_EVALUATED_BY_THIS_DIAGNOSTIC')
    (args.output/'COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()
