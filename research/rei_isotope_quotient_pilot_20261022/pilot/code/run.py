"""Portable source-pinned isotope quotient pilot. Run --help for finite commands."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import csv
import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import c, k as KB
from atomic_quotient import AtomicQuotient, OFFSETS, ISOTOPES, CHARGE_NAMES, EV, thermal_uv
from compact_transport import (CompactTransport, source, unit_matter_pi,
                               KAPPA_T, SQRT6, GAMMA_PER_NE, verify_vendor)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
XEND=math.log(7.)
ATOL=2e-11
RTOL=2e-8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_sources():
    verify_vendor()
    assert sha(ROOT/'code/compact_transport.py')=='0fa826025836a0126fac580de98e3b45c9dcc750e1e243afe933c249ae8e4b6c'
    assert sha(ROOT.parent/'INHERITED_PHYSICAL_CONTRACT.md')=='dd3950150be8718d1bb60eed4f1ba3f4cd7447b377adc92476abf28ba8369dee'
    expected={'verner_photo_Z1_Z2_Z3.dat':'fc2b5e4e32c1b601d011efed62f4d4d5f8202654061bc63734ffb0c0ecc510eb',
              'verner_ferland_rr_table1_original.dat':'2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091'}
    for filename,digest in expected.items():assert sha(ROOT/'data'/filename)==digest


def amplitudes_to_axes(sigma,am,ar,orientation=1):
    src=source()
    q0=orientation*sigma/math.sqrt(6-sigma*sigma)
    hinit=src.href*math.sqrt(1+q0*q0)
    mass_pref=src.omega_m*.1/src.aref**3
    pm=KAPPA_T*SQRT6*src.rhocrit_j_m3*mass_pref*unit_matter_pi()/hinit**2*am
    fr=src.h0**2*src.omega_r/(src.aref**4*src.href**2)
    pr=SQRT6*fr/(5*(1+q0*q0))*ar
    return pm,pr


class Coupled:
    def __init__(self,sigma=0.,am=0.,ar=0.,orientation=1,reference=False,ellmax=16,
                 rtol=RTOL,atol=ATOL,deadline=120.):
        pm,pr=amplitudes_to_axes(sigma,am,ar,orientation)
        self.transport=CompactTransport(sigma,pm,pr,ellmax=ellmax,orientation=orientation)
        self.atomic=AtomicQuotient(self.transport.source)
        self.reference=reference
        self.sizechem=18 if reference else 9
        self.ntrans=self.transport.size
        self.y0=np.r_[self.transport.initial_state(),
                       self.atomic.reference_initial() if reference else self.atomic.y0,0.]
        self.target=(orientation*sigma,pm,pr)
        self.rtol=rtol;self.atol=atol
        self.deadline=deadline
        self.started=time.monotonic()
        self.calls=0;self.jcalls=0

    def details(self,x,y):
        t=self.transport
        a=t.source.aref*math.exp(x)
        f=y[self.ntrans:-1]
        nb=self.atomic.nb_cm3(a)
        if self.reference:
            ne=self.atomic.reference_electron(f,nb)
        else:
            w=nb*self.atomic.w_element*self.atomic.q
            ne=float(w@f)
        dt,geom=t.rhs(x,y[:self.ntrans],ne,with_geometry=True)
        h=geom[1]
        if self.reference:
            _,df=self.atomic.reference_point(x,f,a,h)
            point=self.atomic.point(x,self.atomic.reference_reduce(f),a,h)
            point['ne_cm3']=ne
        else:
            point=self.atomic.point(x,f,a,h)
            df=point['F']
        return dt,df,geom,point

    def rhs(self,x,y):
        self.calls+=1
        if time.monotonic()-self.started>self.deadline:
            raise TimeoutError('case wall bound 120 s')
        dt,df,geom,point=self.details(x,y)
        return np.r_[dt,df,GAMMA_PER_NE*point['ne_cm3']/geom[1]]

    def jac(self,x,y):
        """Analytic chemistry/cross blocks; central differences only in transport geometry."""
        self.jcalls+=1
        if self.reference:
            raise RuntimeError('reference uses solver numerical Jacobian')
        n=self.ntrans;dt,df,geom,p=self.details(x,y)
        H=geom[1]
        J=np.zeros((n+10,n+10))
        step=np.finfo(float).eps**(1/3)
        for j in range(n):
            hj=step*max(1,abs(y[j]))
            plus=y.copy();minus=y.copy()
            plus[j]+=hj;minus[j]-=hj
            dp,gp=self.transport.rhs(x,plus[:n],p['ne_cm3'],with_geometry=True)
            dm,gm=self.transport.rhs(x,minus[:n],p['ne_cm3'],with_geometry=True)
            J[:n,j]=(dp-dm)/(2*hj)
            hp=gp[1]
            hm=gm[1]
            logH=(hp-hm)/(2*hj*H)
            J[n:n+9,j]=-df*logH
            J[-1,j]=-GAMMA_PER_NE*p['ne_cm3']/H*logH
        w=p['w'];tower=y[3:n].reshape(4,self.transport.n)
        for i in (0,1):
            start=3+i*self.transport.n
            J[start:start+self.transport.n,n:n+9]=-(GAMMA_PER_NE/H)*np.outer(
                self.transport.damp*tower[i],w)
        J[n:n+9,n:n+9]=p['Jff']
        J[-1,n:n+9]=GAMMA_PER_NE*w/H
        return J

    def diagnostics(self,x,y):
        n=self.ntrans
        a,H,s,pm,pg,pn,tower,m=self.transport.geometry(x,y[:n])
        f=self.atomic.reference_reduce(y[n:-1]) if self.reference else y[n:-1]
        p=self.atomic.point(x,f,a,H)
        if self.reference:
            p['ne_cm3']=self.atomic.reference_electron(y[n:-1],p['nb_cm3'])
        obs=self.transport.observables(x,y[:n],p['ne_cm3'],y[-1])
        bind,photo,uv,uv_number=self.atomic.photo_energy_ledger(p,f)
        nb=p['nb_cm3']*1e6
        ne=p['ne_cm3']*1e6
        nheavy=nb*sum(self.atomic.Y.values())
        npart=nheavy+ne
        if self.reference:
            _,df=self.atomic.reference_point(x,y[n:-1],a,H)
            ydot=np.r_[np.repeat(self.atomic.Y['H1'],2)*[0,1],
                       np.repeat(self.atomic.Y['D'],2)*[0,1],
                       np.repeat(self.atomic.Y['He3'],3)*[0,1,2],
                       np.repeat(self.atomic.Y['He4'],3)*[0,1,2],
                       np.repeat(self.atomic.Y['Li6'],4)*[0,1,2,3],
                       np.repeat(self.atomic.Y['Li7'],4)*[0,1,2,3]]
            Se=nb*float(ydot@df)*H
        else:
            Se=nb*float((self.atomic.w_element*self.atomic.q)@p['F'])*H
        thermal=1.5*KB*npart*H*p['dTdx']+1.5*KB*p['T']*Se+3*H*KB*p['T']*npart
        energy=3*H*H/KAPPA_T
        return dict(obs,T_K=p['T'],nB_m3=nb,ne_m3=ne,n_part_m3=npart,
                    U_thermal_J_m3=1.5*KB*p['T']*npart,
                    U_binding_J_m3=nb*float((self.atomic.w_element*self.atomic.charge_energy)@f),
                    U_UV_J_m3=uv,UV_number_m3=uv_number,
                    Q_thermal_required_W_m3=thermal,Q_binding_W_m3=bind,
                    Q_gas_required_W_m3=thermal+bind,P_photo_W_m3=photo,
                    bath_minus_escape_W_m3=thermal+bind-photo,
                    background_J_m3=energy,
                    electron_source_m3_s=Se,
                    N_gamma_0=tower[1,0],N_nu_0=tower[3,0],
                    min_angular_257=self.transport.brightness_min(y[:n],257))


def atomic_save(path,writer):
    if path.exists():
        raise FileExistsError(path)
    temp=path.with_name(path.stem+f'.{os.getpid()}.tmp'+path.suffix)
    writer(temp)
    os.replace(temp,path)


def case_id(model):
    return ('reference' if model.reference else 'quotient')+'_L'+str(model.transport.ellmax)+\
           '_S'+format(model.target[0],'.3g')+'_Am'+format(model.transport.am,'.3g')+\
           '_Ar'+format(model.transport.ar,'.3g')


def case_configurations():
    cases=[]
    for sigma in (0.,.01,.05,.2,.6):
        for am in (-.8,0.,1.6):
            for ar in (-.8,-.4,0.,.4,1.6):
                cases.append(dict(sigma=sigma,am=am,ar=ar,orientation=1,
                                  reference=False,ellmax=16))
    for am in (1.6,-.8):
        pm,_=amplitudes_to_axes(0.,am,0.)
        _,pr_unit=amplitudes_to_axes(0.,0.,1.)
        ar=-pm/pr_unit
        if not -1<=ar<=2:raise ValueError('cancellation outside positive W')
        cases.append(dict(sigma=0.,am=am,ar=ar,orientation=1,
                          reference=False,ellmax=16))
    for am,ar in ((0.,0.),(1.6,-.8)):
        cases.append(dict(sigma=.6,am=am,ar=ar,orientation=-1,
                          reference=False,ellmax=16))
    assert len(cases)==79
    controls=[]
    for choice in (cases[7],next(q for q in cases if q['sigma']==.6 and q['am']==1.6 and q['ar']==-.8),
                   cases[75]):
        controls.append(dict(choice,ellmax=24,rtol=2e-9,atol=2e-12))
    # Isotropic zero-stress index is Am=0,Ar=0 (index7).
    assert cases[7]['am']==cases[7]['ar']==0
    return cases,controls


def execute_config(config):
    return run_case(Coupled(**config,deadline=120.))


def verify_existing_case(config):
    name=case_id(Coupled(**config))
    receipt=json.loads((OUT/(name+'.json')).read_text())
    requested=Coupled(**config)
    expected=dict(Sigma_F0=requested.target[0],A_m=requested.transport.am,
                  A_r=requested.transport.ar,ellmax=requested.transport.ellmax,
                  reference=requested.reference,rtol=requested.rtol,
                  atol=requested.atol,max_step=.04,samples=257)
    if receipt['status']!='PASS' or receipt['model']!=expected:
        raise RuntimeError('existing config/result mismatch: '+name)
    for path in ('code/compact_transport.py','data/verner_photo_Z1_Z2_Z3.dat',
                 'data/verner_ferland_rr_table1_original.dat'):
        if receipt['source_hashes'][path]!=sha(ROOT/path):
            raise RuntimeError('existing source mismatch: '+name+' '+path)
    current=sha(ROOT/'code/atomic_quotient.py')
    older=receipt['source_hashes']['code/atomic_quotient.py']
    if current!=older:
        # Frozen isotope/charge equations were unchanged by diagnostics/Jacobian
        # repair. The immutable raw pair was reanalyzed against all 18 states.
        evidence=OUT/'profile_existing_reanalysis.json'
        profile_name='quotient_L16_S0_Am0_Ar0'
        if name!=profile_name or older!='ce4b8d7aa69651559a4c45a4d40195d85600b6f6bb11591e717e9f68ffa1bae1'\
                or not evidence.exists() or json.loads(evidence.read_text())['status']!='PASS':
            raise RuntimeError('existing atomic source mismatch: '+name)
    path=OUT/(name+'.npz')
    if sha(path)!=receipt['npz_sha256']:
        raise RuntimeError('existing case hash mismatch: '+name)
    return receipt


def run_stage(configurations,workers,stage):
    check=json.loads((OUT/'point_checks_v2.json').read_text())
    pair=json.loads((OUT/'profile_pair.json').read_text())
    if not check['passed'] or pair['status']!='PASS':
        raise RuntimeError('checks/profile must pass before sweep')
    if workers<1 or workers>4:raise ValueError('workers range 1..4')
    start=time.monotonic()
    existing=[p for p in OUT.glob('*.json') if p.name.startswith(('quotient_','reference_'))]
    cpu_total=sum(json.loads(p.read_text())['cpu_s'] for p in existing)
    wall_prior=sum(json.loads(p.read_text())['wall_s'] for p in existing)
    attempts=len(existing)
    pending=[]
    for config in configurations:
        name=case_id(Coupled(**config))
        rec=OUT/(name+'.json')
        if rec.exists():
            verify_existing_case(config)
        else:pending.append(config)
    outcomes=[]
    unlaunched=[]
    reason=None
    with ProcessPoolExecutor(max_workers=workers) as pool:
        inflight={}
        while pending or inflight:
            while pending and len(inflight)<workers and attempts<90 and\
                    cpu_total<2400 and wall_prior+time.monotonic()-start<900:
                config=pending.pop(0)
                future=pool.submit(execute_config,config)
                inflight[future]=config
                attempts+=1
            if not inflight:break
            done,_=wait(inflight,return_when=FIRST_COMPLETED)
            for future in done:
                config=inflight.pop(future)
                result=future.result()
                outcomes.append(result)
                cpu_total+=result['cpu_s']
                if result['status']!='PASS':
                    reason='FAILED_CASE'
                    unlaunched.extend(case_id(Coupled(**v)) for v in pending)
                    pending.clear()  # Preserve failure; no silent repair/admission.
            if wall_prior+time.monotonic()-start>=900 or cpu_total>=2400:
                reason=reason or 'RESOURCE_LIMIT'
                unlaunched.extend(case_id(Coupled(**v)) for v in pending)
                pending.clear()
    if attempts>=90 and pending:
        reason='ATTEMPT_LIMIT';unlaunched.extend(case_id(Coupled(**v)) for v in pending)
    result=dict(status='PASS' if not reason and not unlaunched and
                all(v['status']=='PASS' for v in outcomes) else 'PARTIAL_OR_FAILED',
                stop_reason=reason,stage=stage,new_cases=len(outcomes),
                attempts_total=attempts,cpu_total_s=cpu_total,
                wall_s=time.monotonic()-start,wall_cumulative_upper_s=wall_prior+time.monotonic()-start,
                unlaunched=unlaunched,
                statuses={v['case']:v['status'] for v in outcomes})
    atomic_save(OUT/(stage+'_receipt.json'),lambda p:p.write_text(json.dumps(result,indent=2)+'\n'))
    return result


def controls_stage(workers=4):
    cases,controls=case_configurations()
    strong=next(c for c in cases if c['sigma']==.6 and c['am']==1.6 and c['ar']==-.8)
    configurations=[strong,cases[75],*controls]
    return run_stage(configurations,workers,'controls_stage')


def sweep(workers=4):
    cases,controls=case_configurations()
    return run_stage(cases+controls,workers,'sweep')


def summarize():
    """Generate CSV, scoped controls, and data-backed scientific figures without IVPs."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cases,controls=case_configurations()
    configs=cases+controls
    records=[];data={}
    for config in configs:
        name=case_id(Coupled(**config))
        rpath=OUT/(name+'.json');path=OUT/(name+'.npz')
        if not rpath.exists():continue
        receipt=json.loads(rpath.read_text())
        if receipt['status']!='PASS' or not path.exists() or sha(path)!=receipt['npz_sha256']:
            continue
        with np.load(path,allow_pickle=True) as z:
            data[name]={k:z[k] for k in ('x','z','conditional','census','diagnostics','diagnostic_names')}
        records.append(receipt)
    figdir=ROOT/'figures';figdir.mkdir(exist_ok=True)
    with (ROOT/'summary.csv').open('w',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['case','L','A_m','A_r','S_initial','P_m_initial','P_r_initial',
                         'S_final','P_m_final','P_r_final','tau_final','wall_s','cpu_s','nfev','njev','nlu'])
        for r in records:
            c=r['model'];writer.writerow([r['case'],c['ellmax'],c['A_m'],c['A_r'],
                   *r['initial_axes'],*r['final_axes'],r['final_tau'],r['wall_s'],
                   r['cpu_s'],r['nfev'],r['njev'],r['nlu']])
    def series(case,key):
        row=data[case];names=row['diagnostic_names'].tolist()
        return row['diagnostics'][:,names.index(key)]
    def plot(name,selection,keys):
        fig,ax=plt.subplots(figsize=(7,4.2))
        for label,cname in selection:
            if cname not in data:continue
            z=data[cname]['z']
            for k in keys:ax.plot(z,series(cname,k),label=label+' '+k)
        ax.invert_xaxis();ax.set_xlabel('redshift z');ax.legend(fontsize=7,ncol=2)
        fig.tight_layout();fig.savefig(figdir/(name+'.png'),dpi=160);plt.close(fig)
    iso=case_id(Coupled(**cases[7]))
    strong=case_id(Coupled(**next(c for c in cases if c['sigma']==.6 and c['am']==1.6 and c['ar']==-.8)))
    canc=[case_id(Coupled(**c)) for c in cases[75:77]]
    negative=[case_id(Coupled(**c)) for c in cases[77:79]]
    plot('stress_histories',[('isotropic',iso),('strong',strong)],
         ('Sigma_F','Pi_m','Pi_r','Pi_total'))
    plot('photon_neutrino',[('strong',strong)],('P_gamma','P_nu'))
    plot('cancellation_orientation',[(s,s) for s in canc+negative],
         ('signed_Sigma','P_m','P_r'))
    fig,ax=plt.subplots(figsize=(7,5))
    for r in records:
        if r['model']['ellmax']!=16 or r['model']['Sigma_F0']!=.6:continue
        ax.scatter(r['initial_axes'][1],r['initial_axes'][2],c=r['final_axes'][0],
                   vmin=-.6,vmax=.6,cmap='coolwarm',s=60,edgecolor='k',linewidth=.25)
    ax.set_xlabel('realized signed initial P_m');ax.set_ylabel('realized signed initial P_r')
    fig.tight_layout();fig.savefig(figdir/'signed_final_sweep.png',dpi=160);plt.close(fig)
    if strong in data:
        fig,axes=plt.subplots(3,1,figsize=(8,8),sharex=True)
        z=data[strong]['z'];f=data[strong]['conditional']
        for ax,(element,sl) in zip(axes,OFFSETS.items()):
            for q,j in enumerate(range(sl.start,sl.stop)):
                ax.plot(z,f[:,j],label=f'{element} q={q}')
            ax.set_ylabel('charge fraction');ax.legend(fontsize=8,ncol=4)
        axes[-1].invert_xaxis();axes[-1].set_xlabel('redshift z')
        fig.tight_layout();fig.savefig(figdir/'charge_fractions.png',dpi=160);plt.close(fig)
        plot('energy_ledger',[('strong',strong)],
             ('Q_gas_required_W_m3','P_photo_W_m3','bath_minus_escape_W_m3'))
    differences={}
    for config in controls:
        high=case_id(Coupled(**config))
        low=case_id(Coupled(**dict(config,ellmax=16,rtol=RTOL,atol=ATOL)))
        if high not in data or low not in data:continue
        axes={k:float(np.max(abs(series(high,k)-series(low,k)))) for k in
              ('signed_Sigma','P_m','P_r')}
        fraction=float(np.max(abs(data[high]['conditional']-data[low]['conditional'])))
        differences[high]=dict(reference=low,axes=axes,fraction=fraction,
                               passed=max(fraction,*axes.values())<=2e-5)
    result=dict(completed=len(records),expected=len(configs),controls=differences,
                preliminary_all_cases=all(r['status']=='PASS' for r in records) and len(records)==len(configs),
                figures=sorted(p.name for p in figdir.glob('*.png')))
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def run_case(model,output=OUT):
    output.mkdir(parents=True,exist_ok=True)
    ident=case_id(model)
    path=output/(ident+'.npz')
    receipt=output/(ident+'.json')
    if path.exists() or receipt.exists():
        raise FileExistsError('immutable case already exists '+ident)
    started=time.monotonic();cpu0=time.process_time()
    record=dict(case=ident,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in
                [ROOT/'code/compact_transport.py',ROOT/'code/atomic_quotient.py',
                 ROOT/'data/verner_photo_Z1_Z2_Z3.dat',ROOT/'data/verner_ferland_rr_table1_original.dat']},
                model=dict(Sigma_F0=model.target[0],A_m=model.transport.am,A_r=model.transport.ar,
                           ellmax=model.transport.ellmax,reference=model.reference,
                           rtol=model.rtol,atol=model.atol,max_step=.04,samples=257))
    try:
        x=np.linspace(0,XEND,257)
        sol=solve_ivp(model.rhs,(0,XEND),model.y0,method='Radau',
                      jac=None if model.reference else model.jac,
                      rtol=model.rtol,atol=model.atol,max_step=.04,t_eval=x)
        if not sol.success or sol.y.shape!=(len(model.y0),257):
            raise RuntimeError('integration '+sol.message)
        rows=[model.diagnostics(float(xi),sol.y[:,i]) for i,xi in enumerate(x)]
        names=list(rows[0]);diag=np.array([[v[k] for k in names] for v in rows],dtype=float)
        f=sol.y[model.ntrans:-1].T
        reduced=np.array([model.atomic.reference_reduce(v) for v in f]) if model.reference else f
        census=np.array([model.atomic.lift(v) for v in reduced])
        pidx={k:i for i,k in enumerate(names)}
        conservation={el:float(np.max(abs(np.sum(reduced[:,sl],axis=1)-1)))
                      for el,sl in OFFSETS.items()}
        initial=np.array([rows[0][k] for k in ('signed_Sigma','P_m','P_r')])
        initial_error=float(np.max(abs(initial-np.array(model.target))))
        number_drift=float(max(abs(sol.y[3+model.transport.n, :]-1).max(),
                               abs(sol.y[3+3*model.transport.n,:]-1).max()))
        mass_numbers=diag[:,pidx['matter_number_comoving']]
        massive_drift=float(np.max(abs(mass_numbers/mass_numbers[0]-1)))
        min_brightness=float(np.min(diag[:,pidx['min_angular_257']]))
        min_cell=float(np.min(diag[:,pidx['min_canonical_cell']]))
        bounds=dict(endpoint=bool(sol.t[-1]==XEND),finite=bool(np.isfinite(sol.y).all() and
                    np.isfinite(diag).all()),min_fraction=float(np.min(f))>=-2e-9,
                    isotope_sum=max(conservation.values())<=2e-9,
                    initial_axis=initial_error<=2e-10,number_drift=number_drift<=2e-9,
                    massive_number_drift=massive_drift<=2e-9,
                    canonical_cells=min_cell>=0,angular_257=min_brightness>=-2e-8)
        record.update(status='PASS' if all(bounds.values()) else 'FAILED',gates=bounds,
                      isotope_sum_errors=conservation,initial_error=initial_error,
                      number_drift=number_drift,massive_number_drift=massive_drift,
                      min_fraction=float(np.min(f)),
                      min_brightness=min_brightness,min_cell=min_cell,
                      nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,rhs_calls=model.calls,
                      jac_calls=model.jcalls,initial_axes=initial.tolist(),
                      final_axes=[rows[-1][k] for k in ('signed_Sigma','P_m','P_r')],
                      final_tau=rows[-1]['tau_T'])
        atomic_save(path,lambda tmp:np.savez_compressed(tmp,x=x,z=21*np.exp(-x)-1,
                    state=sol.y.T,conditional=reduced,census=census,
                    census_names=np.array(CHARGE_NAMES),abundances=np.array(list(model.atomic.Y.items()),dtype=object),
                    diagnostics=diag,diagnostic_names=np.array(names)))
        record['npz_sha256']=sha(path)
    except Exception as exc:
        record.update(status='FAILED',error=str(exc),traceback=traceback.format_exc())
    record['wall_s']=time.monotonic()-started
    record['cpu_s']=time.process_time()-cpu0
    record['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    atomic_save(receipt,lambda tmp:tmp.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n'))
    return record


def point_checks():
    verify_sources()
    atomic=AtomicQuotient(source())
    result=dict(photo_rel_64_128=atomic.spectral_rel_error,
                uv_integral_rel_analytic_vs_gl64=atomic.uv_integral_error,rr_rows={},
                points=[],jacobian={})
    for name,row in atomic.rr.items():
        result['rr_rows'][name]={str(T):[atomic.rr_scalar(row,T),
            row[0]/(math.sqrt(T/row[2])*(1+math.sqrt(T/row[2]))**(1-row[1])*
                    (1+math.sqrt(T/row[3]))**(1+row[1]))]
                              for T in (100,1000,10000)}
    for x in (0.,XEND/2,XEND):
      for sigma in (0.,.6):
       for am in (-.8,1.6):
        for ar in (-.8,1.6):
            model=Coupled(sigma,am,ar,deadline=120.)
            y=model.y0.copy();f=np.array([.61,.39,.29,.44,.27,.19,.25,.31,.25]);y[model.ntrans:-1]=f
            a=model.transport.source.aref*math.exp(x)
            dt,df,geom,p=model.details(x,y)
            g=np.r_[f[:2],f[:2],f[2:5],f[2:5],f[5:],f[5:]]
            ne_ref,df_ref=atomic.reference_point(x,g,a,geom[1])
            lifted=np.r_[df[:2],df[:2],df[2:5],df[2:5],df[5:],df[5:]]
            scaled=(lifted-df_ref)/np.maximum(1,abs(df_ref))
            mismatch=float(np.max(abs(scaled)))
            col=float(max(abs(p['G'].sum(axis=0))))
            min_off=float(np.min(p['G']-np.diag(np.diag(p['G']))))
            obs=model.transport.observables(x,y[:model.ntrans],p['ne_cm3'])
            result['points'].append(dict(x=x,Sigma0=sigma,Am=am,Ar=ar,
                rhs_error=mismatch,rhs_scaled_residual=scaled.tolist(),
                full_conditional=g.tolist(),quotient_conditional=f.tolist(),
                full_rhs=df_ref.tolist(),lifted_rhs=lifted.tolist(),
                electron_quotient_cm3=p['ne_cm3'],electron_reference_cm3=ne_ref,
                electron_rel=(abs(p['ne_cm3']-ne_ref)/abs(ne_ref) if ne_ref!=0 else
                              (0. if p['ne_cm3']==0 else float('inf'))),
                generator_column_error=col,offdiagonal_min=min_off,
                initial_axis_error=float(np.max(abs(np.array([obs[k] for k in
                    ('signed_Sigma','P_m','P_r')])-np.array(model.target)))) if x==0 else None,
                signed_shear=obs['signed_Sigma'],signed_matter=obs['P_m'],
                signed_radiation=obs['P_r']))
    model=Coupled(.6,1.6,-.8)
    x=XEND/2;y=model.y0.copy();n=model.ntrans
    y[n:-1]=[.61,.39,.29,.44,.27,.19,.25,.31,.25]
    J=model.jac(x,y)
    numerical=np.zeros((len(y),len(y)-1))
    for i in range(len(y)-1):
        h=1e-6*max(1,abs(y[i]));yp=y.copy();ym=y.copy()
        yp[i]+=h;ym[i]-=h
        numerical[:,i]=(model.rhs(x,yp)-model.rhs(x,ym))/(2*h)
    delta=abs(J[:,:-1]-numerical)/(1+abs(numerical))
    result['jacobian']=dict(full_cross_mixed_max=float(np.max(delta)),
                            atomic_max=float(np.max(delta[n:n+9,n:])),
                            photon_max=float(np.max(delta[3:3+2*model.transport.n,n:])),
                            tau_max=float(np.max(delta[-1,n:])),
                            atomic_geometry_max=float(np.max(delta[n:n+9,:n])),
                            tau_geometry_max=float(np.max(delta[-1,:n])),
                            full_residual_matrix=delta.tolist())
    result['passed']=bool(result['photo_rel_64_128']<=2e-8 and
       max(p['rhs_error'] for p in result['points'])<=5e-13 and
       max(p['electron_rel'] for p in result['points'])<=5e-14 and
       max(p['generator_column_error'] for p in result['points'])<=5e-15 and
       min(p['offdiagonal_min'] for p in result['points'])>=0 and
       max(p['initial_axis_error'] for p in result['points'] if p['initial_axis_error'] is not None)<=2e-10 and
       result['jacobian']['full_cross_mixed_max']<=2e-6)
    OUT.mkdir(parents=True,exist_ok=True)
    atomic_save(OUT/'point_checks_v2.json',lambda p:p.write_text(json.dumps(result,indent=2)+'\n'))
    return result


def profile():
    checks=OUT/'point_checks_v2.json'
    if not checks.exists() or not json.loads(checks.read_text())['passed']:
        raise RuntimeError('point checks must pass before IVP')
    start=time.monotonic();cpu=time.process_time()
    reduced=run_case(Coupled(0.,0.,0.))
    if reduced['status']!='PASS' or time.monotonic()-start>120 or time.process_time()-cpu>240:
        return {'status':'STOP_AFTER_REDUCED','reduced':reduced}
    reference=run_case(Coupled(0.,0.,0.,reference=True))
    if reference['status']!='PASS':return {'status':'STOP_AFTER_REFERENCE','reference':reference}
    files=[OUT/(r['case']+'.npz') for r in (reduced,reference)]
    with np.load(files[0]) as a,np.load(files[1]) as b:
        fq=a['conditional'];fr=b['state'][:,39:-1]
        target=np.concatenate([fq[:,:2],fq[:,:2],fq[:,2:5],fq[:,2:5],
                               fq[:,5:],fq[:,5:]],axis=1)
        f=float(np.max(abs(target-fr)))
        names=a['diagnostic_names'].tolist()
        axes={k:float(np.max(abs(a['diagnostics'][:,names.index(k)]-
                            b['diagnostics'][:,names.index(k)]))) for k in
              ('signed_Sigma','P_m','P_r','tau_T')}
    result=dict(status='PASS' if max(f,*axes.values())<=2e-7 else 'FAILED',
                max_charge_difference=f,axes_difference=axes,
                pair_wall_s=time.monotonic()-start,pair_cpu_s=time.process_time()-cpu,
                reduced_receipt=reduced['case']+'.json',reference_receipt=reference['case']+'.json')
    atomic_save(OUT/'profile_pair.json',lambda p:p.write_text(json.dumps(result,indent=2)+'\n'))
    return result


def reanalyze_existing_profile():
    """Read old immutable raw pair; no IVPs and no correction of old diagnostics."""
    short=OUT/'quotient_L16_S0_Am0_Ar0.npz'
    full=OUT/'reference_L16_S0_Am0_Ar0.npz'
    with np.load(short,allow_pickle=True) as a,np.load(full,allow_pickle=True) as b:
        fq=a['conditional'];fr=b['state'][:,39:-1]
        target=np.concatenate([fq[:,:2],fq[:,:2],fq[:,2:5],fq[:,2:5],
                               fq[:,5:],fq[:,5:]],axis=1)
        names=a['diagnostic_names'].tolist()
        def col(z,key):return z['diagnostics'][:,names.index(key)]
        mass=[float(np.max(abs(col(z,'matter_number_comoving')/
                       col(z,'matter_number_comoving')[0]-1))) for z in (a,b)]
        Y=AtomicQuotient(source())
        g=fr
        nb=col(b,'nB_m3')/1e6
        actual=np.array([Y.reference_electron(g[i],nb[i]) for i in range(len(nb))])
        saved=col(b,'ne_cm3')
        result=dict(status='PASS' if np.max(abs(target-fr))<=2e-7 and max(mass)<=2e-9
                    else 'FAILED',max_all18_fraction_difference=float(np.max(abs(target-fr))),
                    each18_fraction_difference=np.max(abs(target-fr),axis=0).tolist(),
                    duplicate_isotope_difference=float(max(np.max(abs(fr[:,0:2]-fr[:,2:4])),
                        np.max(abs(fr[:,4:7]-fr[:,7:10])),np.max(abs(fr[:,10:14]-fr[:,14:18])))),
                    massive_number_relative_drift_quotient=mass[0],
                    massive_number_relative_drift_reference=mass[1],
                    reference_stored_electron_vs_full18_cm3=float(np.max(abs(saved-actual))),
                    previous_diagnostic_electron_computed_from_representative=True,
                    source_npz_sha256={short.name:sha(short),full.name:sha(full)})
    atomic_save(OUT/'profile_existing_reanalysis.json',
                lambda p:p.write_text(json.dumps(result,indent=2)+'\n'))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('checks','profile','reanalyze-profile','controls','sweep','summarize','audit-existing'))
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args()
    if a.action=='checks':r=point_checks()
    elif a.action=='profile':r=profile()
    elif a.action=='reanalyze-profile':r=reanalyze_existing_profile()
    elif a.action=='controls':r=controls_stage(a.workers)
    elif a.action=='sweep':r=sweep(a.workers)
    elif a.action=='summarize':r=summarize()
    else:
        verify_sources()
        receipts=[json.loads(p.read_text()) for p in OUT.glob('*.json') if
                  p.name.startswith(('quotient_','reference_'))]
        r={'receipts':len(receipts),'statuses':{x['case']:x['status'] for x in receipts},
           'files_valid':all(sha(OUT/(x['case']+'.npz'))==x['npz_sha256'] for x in receipts
                             if 'npz_sha256' in x)}
    print(json.dumps(r,indent=2))

if __name__=='__main__':main()
