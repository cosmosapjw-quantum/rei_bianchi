#!/usr/bin/env python3
"""Compute frozen trajectory source tangency and chemical energy bridge.

Source: immutable exact PR298 full archive. No IVP, no new physical rate owner.
"""
from __future__ import annotations
from pathlib import Path
import zipfile, io, json, csv, hashlib, numpy as np
from scipy.integrate import simpson, cumulative_trapezoid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WORK=Path(__file__).resolve().parents[1]
MASTER = WORK/'source'/'PR298_FULL.zip'
SHA = '012635501cc5d9717ae775e9482b351b239003aa6c7db4dd2035ffa4760b7f2d'
TOP='REI_F4_HYBRID_FJ_WEAK_THERMAL_20261031/'
OUT=WORK/'results'
EV_ERG=1.602176634e-12
KB_ERG=1.380649e-16
CHI_REI=(13.598434599702,24.587389011,54.41776)

def locked_inputs():
    if hashlib.sha256(MASTER.read_bytes()).hexdigest()!=SHA:
        raise ValueError('PR298_MASTER_IDENTITY_FAIL')
    with zipfile.ZipFile(MASTER) as z:
        if z.testzip() is not None:raise ValueError('ZIP_CRC_FAIL')
        arr=np.load(io.BytesIO(z.read(TOP+'results/HYBRID_FULL21_193.npz')),allow_pickle=False)
        arrays={k:arr[k].copy() for k in arr.files};arr.close()
        rows=list(csv.DictReader(io.StringIO(z.read(TOP+'results/HYBRID_FJ_THERMAL_193.csv').decode())))
    return arrays,rows

def compute():
    a,rr=locked_inputs();N=193
    assert len(rr)==N
    col=lambda name:np.array([float(r[name]) for r in rr],dtype=float)
    t=col('elapsed_s');x=col('x');z=col('z');h=col('H_s');temp=col('T_K')
    nb_cm=col('nb_m3')/1e6; CV=col('REI_common_Cv21_erg_cm3_K')
    q=a['q21'];A=a['A21'];Y=a['Y_BASS193'];FB=a['F_BASS'];FH=a['F_hybrid'];JB=a['J_BASS'];JH=a['J_hybrid']
    assert Y.shape==(N,21) and np.all(np.diff(t)>0) and np.all(np.diff(x)>0)
    assert np.allclose(a['source_x'],x,rtol=0,atol=1e-13)
    DF=FH-FB
    # exact algebraic mismatch: any identical trajectory would require DF=0.
    dYe=np.gradient(Y,t,axis=0,edge_order=2)
    RB=dYe-FB;RH=dYe-FH
    assert np.max(np.abs(RH-RB+DF))<8e-31
    xeDot=DF@q
    # Number per baryon; use physical REI ionization thresholds for all channels.
    dfhii=DF[:,2]
    dfheii=DF[:,11]
    dfheiii=DF[:,12]
    bind_ev_rate=CHI_REI[0]*dfhii+CHI_REI[1]*(dfheii+dfheiii)+CHI_REI[2]*dfheiii
    DeltaBinding=nb_cm*EV_ERG*bind_ev_rate
    DeltaElectron=nb_cm*xeDot
    nTherm=CV/(1.5*KB_ERG)
    thermalComp=-DeltaBinding
    tempQonly=thermalComp/CV
    tempLoading=-temp*DeltaElectron/nTherm
    tempFormal=tempQonly+tempLoading
    # Canonical source histories remain unchanged, no opacity or heat integration.
    AJ=np.einsum('j,ijk->ik',A,JH);AF=FH@A
    timeHmid=(np.diff(t)*.5*(h[:-1]+h[1:]))/(np.diff(x))
    local_diff=np.max(abs(DF),axis=1)
    eps=1e-70
    rows=[]
    cumul_e=np.concatenate(([0.], cumulative_trapezoid(xeDot,t)))
    cumul_bind=np.concatenate(([0.], cumulative_trapezoid(DeltaBinding/nb_cm,t)))
    for i in range(N):
        rows.append(dict(epoch=i,z=z[i],x=x[i],t_elapsed_s=t[i],H_per_s=h[i],T_K=temp[i],nb_cm3=nb_cm[i],nHref_over_nb=col('nHref_over_nb')[i],
          delta_F_HII_per_baryon_s=dfhii[i],delta_F_HeII_per_baryon_s=dfheii[i],delta_F_HeIII_per_baryon_s=dfheiii[i],
          delta_F_full21_max_per_baryon_s=local_diff[i],delta_F_full21_max_per_Hubble=local_diff[i]/h[i],
          derivative_BASS_residual_max_per_baryon_s=np.max(np.abs(RB[i])),derivative_hybrid_residual_max_per_baryon_s=np.max(np.abs(RH[i])),
          derivative_BASS_residual_max_per_Hubble=np.max(np.abs(RB[i]))/h[i],derivative_hybrid_residual_max_per_Hubble=np.max(np.abs(RH[i]))/h[i],
          delta_electron_source_per_baryon_s=xeDot[i],delta_electron_source_per_Hubble=xeDot[i]/h[i],cumulative_delta_electron_source_trap_per_baryon=cumul_e[i],
          delta_chemical_binding_erg_cm3_s=DeltaBinding[i],delta_binding_energy_per_baryon_s_ev=bind_ev_rate[i],
          cumulative_delta_binding_erg_per_baryon_trap=cumul_bind[i],
          required_opposite_energy_port_erg_cm3_s=thermalComp[i],
          formal_Q_over_Cv_K_s=tempQonly[i],formal_number_loading_K_s=tempLoading[i],formal_total_Tdot_bridge_K_s=tempFormal[i],
          max_baryon_A_F_hybrid_per_s=abs(AF[i]),max_baryon_A_J_hybrid_per_s=np.max(np.abs(AJ[i])),
          clock_midpoint_H_dt_dx_ratio=(1. if i==0 else timeHmid[i-1]),
          scope='FROZEN_REPLACEMENT_SOURCE_DIAGNOSTIC_NOT_A_SOLVED_TEMPERATURE'))
    stats=dict(schema='REI_F4_FROZEN_TANGENCY_V1',source_PR=298,source_sha256=SHA,epochs=N,
       max_delta_F_per_baryon_s=float(np.max(abs(DF))),max_delta_F_per_Hubble=float(np.max(local_diff/h)),
       source_defect_nonzero_epochs=int(np.count_nonzero(local_diff>0)),
       max_delta_electron_source_per_baryon_s=float(np.max(abs(xeDot))),
       simpson_delta_electron_source_per_baryon=float(simpson(xeDot,x=t)),
       simpson_signed_chemical_binding_erg_per_baryon=float(simpson(DeltaBinding/nb_cm,x=t)),
       max_abs_chemical_binding_source_erg_cm3_s=float(np.max(abs(DeltaBinding))),
       max_formal_Tdot_bridge_K_s=float(np.max(abs(tempFormal))),
       max_saved_trajectory_BASS_derivative_residual=float(np.max(abs(RB))),
       max_saved_trajectory_HYBRID_derivative_residual=float(np.max(abs(RH))),
       max_A_F_hybrid=float(np.max(abs(AF))),max_A_J_hybrid=float(np.max(abs(AJ))),
       midpoint_H_dt_dx_rel_error_max=float(np.max(abs(timeHmid-1))),
       no_new_ivp=True,actual_thermal_evolution=False,not_new_physical_source_owner=True,
       canonical={'working':'33/88','central':'28/88','physical_fast':'4/7','delta':0},
       production='HOLD',distinct_author_review='NOT_RUN')
    return rows,stats,(Y,FB,FH,DF,RB,RH),dict(z=z,h=h,xeDot=xeDot,DeltaBinding=DeltaBinding,comp=thermalComp,tempQ=tempQonly,tempLoad=tempLoading,tempFormal=tempFormal,cv=CV,t=t,clock=timeHmid,AJ=AJ)

def figures(info,rows):
    z=info['z'];h=info['h'];t=info['t'];zmid=.5*(z[:-1]+z[1:]);
    data={key:np.array([v[key] for v in rows],float) for key in rows[0] if key not in ['scope']}
    def plot(name,curves,ylabel,title,log=False,scalar=1):
        fig,ax=plt.subplots(figsize=(8.2,4.8))
        for label,axis,values in curves:
            vals=np.asarray(values,float)*scalar
            if log:
                vals=np.where(np.abs(vals)>1e-250,np.abs(vals),np.nan)
                ax.semilogy(axis,vals,label=label)
            else:ax.plot(axis,vals,label=label)
        ax.set_xlabel('Original BASS redshift z (frozen trajectory)')
        ax.set_ylabel(ylabel);ax.set_title(title);ax.grid(alpha=.24)
        ax.legend(loc='best',fontsize=8);fig.tight_layout()
        fig.savefig(OUT/name,dpi=160);plt.close(fig)
    plot('PLOT01_HHE_SOURCE_DEFECT.png',[(n,z,data['delta_F_'+n+'_per_baryon_s']/h) for n in ('HII','HeII','HeIII')],r'Rate per Hubble, baryon$^{-1}$', 'H/He source replacement on BASS193',log=False)
    plot('PLOT02_SOURCE_TANGENCY_RESIDUAL.png', [('Original BASS sampled-derivative residual',z,data['derivative_BASS_residual_max_per_Hubble']),('Hybrid sampled-derivative residual',z,data['derivative_hybrid_residual_max_per_Hubble']),('Exact source mismatch |Delta F|/H',z,data['delta_F_full21_max_per_Hubble'])],r'Max component per Hubble', 'Trajectory tangency vs source replacement (sample derivative)',log=True)
    plot('PLOT03_ELECTRON_SOURCE_HISTORY.png', [('Electron source mismatch per Hubble',z,data['delta_electron_source_per_Hubble'])],r'Delta electron per baryon / Hubble', 'Full-21 charge bath source defect')
    plot('PLOT04_CHEMICAL_ENERGY_PORT.png', [('Binding-source change',z,data['delta_chemical_binding_erg_cm3_s']),('Opposite required energy port',z,data['required_opposite_energy_port_erg_cm3_s'])],r'Energy source [erg cm$^{-3}$ s$^{-1}$]', 'Chemical energy accounting under fixed external reservoirs')
    plot('PLOT05_FORMAL_TEMPERATURE_OPERATORS.png', [('Formal Q/Cv',z,data['formal_Q_over_Cv_K_s']/h),('Electron-number loading',z,data['formal_number_loading_K_s']/h),('Sum, not actual Delta T',z,data['formal_total_Tdot_bridge_K_s']/h)],'Diagnostic K per Hubble','Conditional heat/number compensation, not evolved temperature')
    plot('PLOT06_CLOCK_AND_BARYON_J.png',[('Midpoint H dt/dx -1',zmid,info['clock']-1)],'Dimensionless clock discrepancy','Original saved clock and mean expansion H',False)
    return 6

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    rows,stats,arrays,info=compute()
    with (OUT/'FROZEN_SOURCE_TANGENCY_193.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    np.savez_compressed(OUT/'FROZEN_SOURCE_RESIDUAL_193.npz',Y=arrays[0],F_BASS=arrays[1],F_hybrid=arrays[2],Delta_F=arrays[3],Residual_BASS=arrays[4],Residual_HYBRID=arrays[5],z=info['z'],t=info['t'])
    figures(info,rows)
    (OUT/'RESULTS.json').write_text(json.dumps(stats,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps(stats,indent=2,ensure_ascii=False));return stats

if __name__=='__main__':run()
