"""Source-owned BASS21 193 epoch event ledger and P19 counterfactual.

Inputs MUST be extracted from the immutable VIGILODE PR121 source ZIP.
No IVP, no time stepping, no external physical source mutation.
All units: Y per baryon; event intensity per baryon per proper second,
proper nb, ne in m^-3; Jacobian in s^-1.
"""
from __future__ import annotations
import argparse, csv, json, hashlib, math, sys
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from scipy.integrate import cumulative_simpson, cumulative_trapezoid

ROOT=Path(__file__).resolve().parents[1]
DONOR=ROOT/'donor'
sys.path.insert(0,str(DONOR/'rei_pr269'/'code'))
import native_full_rate as src

SOURCE_SHA256='37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
PR121_ZIP_SHA256='19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907'
ORIGINAL_BASS='cc602e209e7deeb511ab2a1f3b2268d55206c43c'
SAVED_N=193
GAMMA_TOL_REL=5e-13

@dataclass(frozen=True)
class Event:
    kind:str
    source:int
    target:int
    kname:str
    def label(self,names):return f'{self.kind}:{names[self.source]}->{names[self.target]}'
    @property
    def electron_dependent(self):return self.kind in ('rr','dr')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def owner_events(net):
    photo=[Event('photo',int(i),int(i)+1,'photo_s') for i in net.photo_indices]
    rr=[Event('rr',int(i),int(i)-1,'rr_m3_s') for i in net.recombination_indices]
    dr=[Event('dr',int(i),int(i)-1,'dr_m3_s') for i in net._dr_indices]
    weak=[Event('weak',i,j,typ) for i,j,typ in ((0,2,'n'),(5,8,'T'),(6,9,'T'))]
    return photo+rr+dr+weak

def event_coefficient(event,rates,net):
    if event.kind=='weak':
        return net.neutron_lambda_s if event.kname=='n' else net.tritium_lambda_s
    return float(rates[event.kname][event.source])

def evaluate_event_F_J(net,y,rates,nb):
    """All 35 owner events, complete electron feedback; temperature/UV are prescribed."""
    y=np.asarray(y,dtype=np.float64).copy(order='C')
    q=np.asarray(net.q,float); ne=float(nb*float(q@y))
    events=owner_events(net)
    F=np.zeros(21);J=np.zeros((21,21));per_s=[]
    for e in events:
        k=event_coefficient(e,rates,net)
        nfac=ne if e.electron_dependent else 1.
        value=k*nfac*y[e.source]
        grad=(k*nfac)*(np.arange(21)==e.source).astype(float)
        if e.electron_dependent: grad+=k*nb*y[e.source]*q
        F[e.source]-=value;F[e.target]+=value
        J[e.source,:]-=grad;J[e.target,:]+=grad
        per_s.append(value)
    return F,J,np.asarray(per_s),ne

def saved():
    p=DONOR/'original'/'trajectory.npz'
    if sha(p)!=SOURCE_SHA256:raise ValueError('SAVED_TRAJECTORY_SHA_INVALID')
    manifest=src.source_manifest_check()
    with np.load(p,allow_pickle=False) as f: a={k:f[k].copy() for k in f.files}
    if a['Y'].shape!=(193,21) or a['diagnostics'].shape!=(193,25):raise ValueError('BAD_SOURCE_DIMENSIONS')
    if not np.all(np.diff(a['x'])>0) or not np.all(np.diff(a['z'])<0):raise ValueError('BAD_TIME_ORDER')
    if np.min(a['Y'])<0 or not np.isfinite(a['Y']).all():raise ValueError('NEGATIVE_OR_NONFINITE_OWNER_STATE')
    return a,manifest

def generate(write=True):
    a,manifest=saved(); net=src.new_native_network();evs=owner_events(net)
    names=tuple(str(x) for x in a['species_names']);assert len(evs)==35,len(evs)
    diag_names=[str(x) for x in a['diagnostic_names']];d={name:a['diagnostics'][:,k] for k,name in enumerate(diag_names)}
    q=np.asarray(net.q,float);A=np.asarray(net.A,float)
    Y=a['Y'];xx=a['x'];zz=a['z'];nb=d['nb_m3'];H=d['H']; temp=d['T_K'];uv=d['uv_scale']
    if not (np.all(nb>0) and np.all(H>0) and np.all(temp>=100) and np.all(uv>=0)):raise ValueError('BAD_DOMAIN')
    F=np.empty((SAVED_N,21));J=np.empty((SAVED_N,21,21));rates_all=np.empty((SAVED_N,len(evs)))
    max_relF=max_relJ=0.;max_absF=max_absJ=0.
    max_source_charge=max_Af=max_Aj=0.; max_li6_rel=0.;native_electron_rel=0.
    event_rows=[]; epoch_rows=[];p19_rows=[]
    li6_tot=float(np.sum(net.initial_Y[13:17]));li7_tot=float(np.sum(net.initial_Y[17:21]));gamma=li6_tot/li7_tot
    for i in range(SAVED_N):
        y=Y[i].copy(order='C'); x=float(xx[i]);z=float(zz[i]);b=float(nb[i]);h=float(H[i]);t=float(temp[i]);u=float(uv[i]);r=net.rates(t,u);native=net.evaluate(y,t,u,b)
        f,j,event_rates,ne=evaluate_event_F_J(net,y,r,b)
        F[i]=f;J[i]=j;rates_all[i]=event_rates
        fn=native['dY_dt'];jn=native['jac'];max_absF=max(max_absF,float(np.max(np.abs(f-fn))));max_absJ=max(max_absJ,float(np.max(np.abs(j-jn))))
        max_relF=max(max_relF,float(np.max(np.abs(f-fn)))/max(float(np.max(np.abs(fn))),1e-100))
        max_relJ=max(max_relJ,float(np.max(np.abs(j-jn)))/max(float(np.max(np.abs(jn))),1e-100))
        max_source_charge=max(max_source_charge,abs(float(q@f)-float(q@fn)))
        max_Af=max(max_Af,abs(float(A@f)));max_Aj=max(max_Aj,float(np.max(np.abs(A@j))))
        native_electron_rel=max(native_electron_rel,abs(ne-native['ne'])/max(native['ne'],1e-100))
        delta=y[13:17]-gamma*y[17:21];li_rel=np.linalg.norm(delta,ord=1)/li6_tot
        max_li6_rel=max(max_li6_rel,li_rel)
        for k,e in enumerate(evs):
            rate=float(event_rates[k]);
            if rate<-1e-70:raise AssertionError(f'NEGATIVE_EVENT_{i}_{e.label(names)}')
            event_rows.append(dict(epoch=i,x=x,z=z,elapsed_s=float(d['elapsed_s'][i]),T_K=t,UV=u,
                                   event_id=k,channel=e.kind,src_index=e.source,dst_index=e.target,
                                   src_name=names[e.source],dst_name=names[e.target],rate_per_baryon_s=rate,
                                   rate_per_m3_s=rate*b,charge_delta=int(q[e.target]-q[e.source]),
                                   event_integrand_dx=rate/h,physical_owner='BASS21_PR118_SAVED193'))
        li_up=[float(r['photo_s'][k]) for k in (13,14,15)]
        li_down=[ne*(float(r['rr_m3_s'][k])+float(r['dr_m3_s'][k])) for k in (14,15,16)]
        M=np.zeros((4,4))
        for k,v in enumerate(li_up):M[k,k]-=v;M[k+1,k]+=v
        for k,v in enumerate(li_down,start=1):M[k,k]-=v;M[k-1,k]+=v
        eig=np.linalg.eigvals(M)
        # Four-state tridiagonal Markov birth-death generator; no time-global decay inference.
        eig_sorted=sorted(eig,key=lambda x:x.real,reverse=True)
        # use nonzero eigenvalues' real parts, excluding the conservation mode
        gap=float(max(0,-eig_sorted[1].real))
        charge_q6=float(np.dot([0,1,2,3],y[13:17]));charge_q7=float(np.dot([0,1,2,3],y[17:21]))
        base_row=dict(epoch=i,x=x,z=z,elapsed_s=float(d['elapsed_s'][i]),H_s=h,nb_m3=b,ne_m3=ne,
                     T_K=t,uv_scale=u,xe=float(q@y),li6_charge_per_baryon=charge_q6,
                     li7_charge_per_baryon=charge_q7,li_isotope_delta_charge=charge_q6-gamma*charge_q7,
                     li_transverse_l1_over_nu6=li_rel,li_frozen_gap_s=gap,
                     li_frozen_gap_inverse_Myr=(1/gap)/(1e6*365.25*86400) if gap>0 else float('nan'),
                     photo_event_per_baryon_s=float(event_rates[:13].sum()),
                     rr_event_per_baryon_s=float(event_rates[13:26].sum()),
                     dr_event_per_baryon_s=float(event_rates[26:32].sum()),
                     weak_event_per_baryon_s=float(event_rates[32:].sum()),
                     electron_source_per_baryon_s=float(q@f),
                     absorbed_W_m3=float(native['photo_absorbed_power_W_m3']),
                     primary_W_m3=float(native['primary_kinetic_power_W_m3']),
                     unresolved_core_W_m3=float(native['unresolved_core_power_W_m3']))
        epoch_rows.append(base_row)
        if 2.4<=z<=4.75:
            src_indices=(1,3,5,7,8,10,11);dest_indices=(2,4,6,8,9,11,12);family=(0,0,0,1,2,1,2)
            rates_B=np.array([r['photo_s'][1],r['photo_s'][7],r['photo_s'][8]])
            rates_P=src.p19_nominal_gamma(z,beta=0.,kappa=0.)
            rates_Pnom=src.p19_nominal_gamma(z)
            for tag,photo_p in (('P19_D1_FIDUCIAL_13_KNOT_LOG_INTERP',rates_P),('P19_GLS_NOMINAL',rates_Pnom)):
                pv_B=np.asarray([y[s]*rates_B[family[k]] for k,s in enumerate(src_indices)])
                pv_P=np.asarray([y[s]*photo_p[family[k]] for k,s in enumerate(src_indices)])
                differential=pv_B-pv_P
                source_F=np.zeros(21)
                for k,(s,dst) in enumerate(zip(src_indices,dest_indices)):
                    source_F[s]-=differential[k];source_F[dst]+=differential[k]
                p19_rows.append(dict(epoch=i,z=z,x=x,tag=tag,temperature_K=t,ne_m3=ne,
                                     B_gamma_HI=float(rates_B[0]),B_gamma_HeI=float(rates_B[1]),B_gamma_HeII=float(rates_B[2]),
                                     P_gamma_HI=float(photo_p[0]),P_gamma_HeI=float(photo_p[1]),P_gamma_HeII=float(photo_p[2]),
                                     B_HHe_photo_electrons_per_baryon_s=float(pv_B.sum()),
                                     P_HHe_photo_electrons_per_baryon_s=float(pv_P.sum()),
                                     source_difference_electrons_per_baryon_s=float(differential.sum()),
                                     source_difference_F_l1_s=float(np.sum(np.abs(source_F))),
                                     charge_identity_residual=float(q@source_F-differential.sum()),
                                     baryon_identity_residual=float(A@source_F)))
    integrated_rates={}
    for k,e in enumerate(evs):
        val=cumulative_simpson(rates_all[:,k]/H,x=xx,initial=0.)[-1]
        valT=cumulative_trapezoid(rates_all[:,k]/H,x=xx,initial=0.)[-1]
        integrated_rates[e.label(names)]=dict(simpson=float(val),trapezoid=float(valT))
    channel_totals={s:float(sum(v['simpson'] for k,v in integrated_rates.items() if k.startswith(s+':')))
                    for s in ('photo','rr','dr','weak')}
    li6charge=np.array([v['li6_charge_per_baryon'] for v in epoch_rows]);
    jac_event=J
    # retain output as source-on-history, not IVP solution
    result=dict(schema='REI_F4_BASS193_NATIVE_EVENT_LEDGER_V1',status='SOURCE_OWNED_SAVED_HISTORY_DIAGNOSTIC',
        canonical_dag=dict(working='33/88',central='28/88',physical_fast='4/7',physical_delta=0),
        parent_pr=274,original_bass_commit=ORIGINAL_BASS,
        sources=dict(VigilODE_PR121_zip_sha=PR121_ZIP_SHA256,
                     trajectory_sha=SOURCE_SHA256,coefficients='129/129 source-projected numeric, raw original coefficient table SHA not locally checked',
                     atomic_network_sha=manifest['BASS_ATOMIC_NETWORK.py'],
                     P19='original PR269 13 knots from Puchwein et al 2019 D1, same-owner identification false'),
        counts=dict(epochs=193,event_types=len(evs),event_rows=len(event_rows),P19_comparison_rows=len(p19_rows),new_IVP=0),
        validation=dict(native_event_F_max_abs_s=max_absF,native_event_F_scaled_max=max_relF,
                        native_event_J_max_abs_s=max_absJ,native_event_J_scaled_max=max_relJ,
                        max_A_F_s=max_Af,max_A_J_s=max_Aj,max_source_charge_s=max_source_charge,
                        max_electron_pool_relative=native_electron_rel,max_Li_l1_rel_nu6=max_li6_rel),
        path_exposure_simpson_per_baryon=channel_totals,
        path_exposure_definition='postprocessed ∫(event_per_baryon_s)/H dx over saved BASS x grid; not new IVP or certified event-count',
        local_spectral_gap_min_s=min(v['li_frozen_gap_s'] for v in epoch_rows),
        local_spectral_gap_max_s=max(v['li_frozen_gap_s'] for v in epoch_rows),
        physical_claim='same-BASS source chemistry at saved epochs only',
        counterfactual_claim='P19 fiducial/nominal photon rates replace BASS H-He photo rates on the SAME frozen BASS populations; NOT a P19 history, REI RHS or observer tau',
        no_more_IVPs=True,independent_R6='NOT_RUN',independent_C9='NOT_RUN',full_physical_F4='PARTIAL',L4=False,production='HOLD')
    if write:
        out=ROOT/'results';out.mkdir(exist_ok=True)
        def csvwrite(path,rows):
            if not rows:return
            with path.open('w',newline='') as h:
                w=csv.DictWriter(h,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
        csvwrite(out/'BASS193_NATIVE_EVENT_6755_ROWS.csv',event_rows)
        csvwrite(out/'BASS193_EPOCH_CHEM_PHYSICS.csv',epoch_rows)
        csvwrite(out/'P19_ON_BASS193_COUNTERFACTUAL.csv',p19_rows)
        (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        (out/'EVENT_EXPOSURES.json').write_text(json.dumps(integrated_rates,indent=2)+'\n')
        np.savez_compressed(out/'NATIVE_193_EVENT_VECTOR_AND_JACOBIAN.npz',x=xx,z=zz,F_21=F,J_21x21=jac_event,event_rates_193x35=rates_all)
    return result,epoch_rows,event_rows,p19_rows

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--dry',action='store_true');arg=parser.parse_args();
    print(json.dumps(generate(not arg.dry)[0],indent=2))
