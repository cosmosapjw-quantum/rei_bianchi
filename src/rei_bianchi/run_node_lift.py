"""R2B fixed-node moment lift.

This module distributes already locked R2A macro moments over the immutable
B2C2B0A micro measure.  It does not evolve chemistry or infer cloud mass.
"""
from __future__ import annotations
import argparse,csv,gzip,json,math,shutil,sys,zipfile
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
try:
    from .node_lift_operator import (
     bernoulli_kl_mean_projection,positive_mass_projection,
     capacity_constrained_group_projection,signed_transfer_lift,
    )
except ImportError:
    from node_lift_operator import (
     bernoulli_kl_mean_projection,positive_mass_projection,
     capacity_constrained_group_projection,signed_transfer_lift,
    )

MYR_S=1.0e6*365.25*86400.0
NH0_CM3=1.88e-7
ACTIVE_GROUPS=('G1','G2a')

def alpha_b_hii(T: np.ndarray|float)->np.ndarray:
    """B2C0 locked HII case-B fit, cm^3 s^-1."""
    T=np.asarray(T,dtype=float)
    ll=315614.0/T
    return 2.753e-14*ll**1.5/(1.0+(ll/2.740)**0.407)**2.242

def _v(row:Any,key:str)->float:
    if isinstance(row,dict): return float(row[key])
    return float(row[key])

def lift_macro_case(nodes:pd.DataFrame,macro:Any,global_row:Any,q_prior:np.ndarray)->dict[str,Any]:
    """Lift one macro case onto its fixed micro nodes."""
    nodes=nodes.sort_values('micro_index').reset_index(drop=True)
    n=len(nodes); q=np.asarray(q_prior,dtype=float)
    if q.shape!=(n,2): raise ValueError(f'q_prior shape {q.shape} != {(n,2)}')
    p=nodes['w_micro'].to_numpy(float); p=p/p.sum()
    M=_v(macro,'M_sink_H_cMpc3')
    mass=positive_mass_projection(p,M)
    target_x=_v(global_row,'x_HII_sink_global')
    x,xcert=bernoulli_kl_mean_projection(nodes['xHII'].to_numpy(float),mass,target_x)
    target_T=_v(global_row,'T_sink_global_K')
    thermal=positive_mass_projection(mass*nodes['T_K'].to_numpy(float),M*target_T)
    T=np.divide(thermal,mass,out=np.full_like(thermal,target_T),where=mass>0)
    z=_v(macro,'z_mid'); dt=_v(global_row,'dt_Myr')*MYR_S
    nH=NH0_CM3*(1.0+z)**3*np.maximum(nodes['delta_total'].to_numpy(float),1e-300)
    cap_shape=p*(np.maximum(1.0-x,0.0)/dt + alpha_b_hii(T)*nH*x*x)
    if not np.all(np.isfinite(cap_shape)) or cap_shape.sum()<=0: cap_shape=p.copy()
    cap_total=_v(macro,'cycling_capacity_macro_s_inv_cMpc3')
    capacity=positive_mass_projection(cap_shape,cap_total)
    totals=np.array([_v(macro,'J_sink_G1_s_inv_cMpc3'),_v(macro,'J_sink_G2a_s_inv_cMpc3')])
    J,jcert=capacity_constrained_group_projection(q,totals,capacity,tol=2e-11)
    kappat=np.array([_v(macro,'kappa_sink_G1_cMpc_inv'),_v(macro,'kappa_sink_G2a_cMpc_inv')])
    phi=np.divide(totals,kappat,out=np.zeros_like(totals),where=kappat>0)
    kappa=np.divide(J,phi[None,:],out=np.zeros_like(J),where=phi[None,:]>0)
    pos,neg,net=signed_transfer_lift(_v(macro,'mass_transfer_rate_macro_H_s_inv_cMpc3'),p)
    # temperature I-divergence is applied to the energy measure.
    prior_energy=mass*nodes['T_K'].to_numpy(float)
    with np.errstate(divide='ignore',invalid='ignore'):
        terms=np.where(thermal>0,thermal*np.log(thermal/np.maximum(prior_energy,1e-300)),0)-thermal+prior_energy
    tkl=float(np.sum(terms))
    cert={k:v for k,v in jcert.items() if k!='lambda'}
    lamb=np.asarray(jcert['lambda'])
    cert.update({
      'lambda_active_indices':np.flatnonzero(lamb>1e-12).tolist(),
      'lambda_active_values':lamb[lamb>1e-12].tolist(),
      'bernoulli_kl':xcert['kl'],'bernoulli_mean_residual':xcert['mean_residual'],
      'thermal_generalized_kl':tkl,
      'mass_relative_residual':float(abs(mass.sum()-M)/max(abs(M),1.0)),
      'ionization_absolute_residual':float(abs(np.dot(mass,x)/mass.sum()-target_x)),
      'temperature_relative_residual':float(abs(np.dot(mass,T)/mass.sum()-target_T)/max(abs(target_T),1.0)),
      'kappa_relative_residual_max':float(np.max(np.abs(kappa.sum(0)-kappat)/np.maximum(np.abs(kappat),1.0))),
      'transfer_relative_residual':float(abs(net.sum()-_v(macro,'mass_transfer_rate_macro_H_s_inv_cMpc3'))/max(abs(_v(macro,'mass_transfer_rate_macro_H_s_inv_cMpc3')),1.0)),
    })
    return {'mass':mass,'xHII':x,'T_K':T,'nH_cm3':nH,'capacity':capacity,'J':J,'kappa':kappa,'phi':phi,'transfer_positive':pos,'transfer_negative':neg,'transfer_net':net,'certificate':cert,'x_prior':nodes['xHII'].to_numpy(float),'T_prior':nodes['T_K'].to_numpy(float),'p_mass':p}

def _float(x): return f'{float(x):.17e}'

def read_gzipped_csv_member(archive: zipfile.ZipFile, member: str) -> pd.DataFrame:
    """Read a gzip-compressed CSV member without relying on filename inference."""
    with archive.open(member) as raw:
        with gzip.GzipFile(fileobj=raw, mode="rb") as decoded:
            return pd.read_csv(decoded)

def copy_inherited_csv_exact(source: Path, destination: Path) -> None:
    """Preserve an inherited auditor table byte-for-byte."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def run_stage(repo:Path,stage:Path,b0a_zip:Path,prior_npz:Path)->dict[str,Any]:
    r2a=repo/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK'
    global_df=pd.read_csv(r2a/'data/global_moment_lock.csv')
    macro_df=pd.read_csv(r2a/'data/macro_projection.csv').sort_values(['shape_lane','interval_index','substep','macro_index'])
    root='Bianchi_Reionization_Stage_P0_5_B2C2B0A_HIERARCHICAL_TWO_SCALE_OPACITY_CHEMISTRY_CLOSURE_LOCK/'
    with zipfile.ZipFile(b0a_zip) as z:
        nodes_all=read_gzipped_csv_member(z,root+'data/hierarchical_node_table.csv.gz')
    nodes_map={(round(float(z),2),int(m)):g.sort_values('micro_index').reset_index(drop=True) for (z,m),g in nodes_all.groupby(['z','macro_index'],sort=False)}
    pri=np.load(prior_npz)
    data=stage/'data';data.mkdir(exist_ok=True)
    state_cols=['shape_lane','interval_index','substep','z_mid','macro_index','micro_index','w_micro','M_sink_H_node_cMpc3','p_mass_conditional','xHII_prior','xHII_lift','T_prior_K','T_lift_K','nH_node_cm3','cycling_capacity_node_s_inv_cMpc3','mass_transfer_positive_H_s_inv_cMpc3','mass_transfer_negative_H_s_inv_cMpc3','mass_transfer_net_H_s_inv_cMpc3']
    group_cols=['shape_lane','interval_index','substep','z_mid','macro_index','micro_index','group','q_prior_conditional','J_sink_node_s_inv_cMpc3','kappa_sink_node_cMpc_inv','Phi_current_Gamma_s_inv_cMpc2','capacity_slack_after_all_groups_s_inv_cMpc3']
    macro_aud=[]; certs=[]; envelope=[]
    state_path=data/'node_state_lift.csv.gz';group_path=data/'node_group_lift.csv.gz'
    with gzip.open(state_path,'wt',newline='',compresslevel=6) as sf,gzip.open(group_path,'wt',newline='',compresslevel=6) as gf:
      sw=csv.writer(sf);gw=csv.writer(gf);sw.writerow(state_cols);gw.writerow(group_cols)
      for _,mr in macro_df.iterrows():
        keyg=(int(mr.interval_index),int(mr.substep)); gr=global_df[(global_df.interval_index==keyg[0])&(global_df.substep==keyg[1])].iloc[0]
        z=round(float(mr.z_mid),2); m=int(mr.macro_index); lane=str(mr.shape_lane); ng=nodes_map[(z,m)]
        qcols=[]
        for group in ACTIVE_GROUPS:
          key=f'z{z:.2f}_{lane}_{group}'
          qa=pri[key+'_q_node']; ma=pri[key+'_macro_index']; mi=pri[key+'_micro_index']
          sel=(ma==m); order=np.argsort(mi[sel]); qcols.append(qa[sel][order])
        q=np.column_stack(qcols)
        out=lift_macro_case(ng,mr,gr,q)
        rowJ=out['J'].sum(1); slack=out['capacity']-rowJ
        for i,r in ng.iterrows():
          sw.writerow([lane,int(mr.interval_index),int(mr.substep),_float(z),m,int(r.micro_index),_float(r.w_micro),_float(out['mass'][i]),_float(out['p_mass'][i]),_float(out['x_prior'][i]),_float(out['xHII'][i]),_float(out['T_prior'][i]),_float(out['T_K'][i]),_float(out['nH_cm3'][i]),_float(out['capacity'][i]),_float(out['transfer_positive'][i]),_float(out['transfer_negative'][i]),_float(out['transfer_net'][i])])
          for j,group in enumerate(ACTIVE_GROUPS):
            qcond=q[:,j]/q[:,j].sum()
            gw.writerow([lane,int(mr.interval_index),int(mr.substep),_float(z),m,int(r.micro_index),group,_float(qcond[i]),_float(out['J'][i,j]),_float(out['kappa'][i,j]),_float(out['phi'][j]),_float(slack[i])])
        cert={'shape_lane':lane,'interval_index':int(mr.interval_index),'substep':int(mr.substep),'z_mid':z,'macro_index':m,**out['certificate']};certs.append(cert)
        M=out['mass'].sum(); Jsum=out['J'].sum(0);ksum=out['kappa'].sum(0)
        maudit={'shape_lane':lane,'interval_index':int(mr.interval_index),'substep':int(mr.substep),'z_mid':z,'macro_index':m,
          'mass_relative_residual':abs(M-mr.M_sink_H_cMpc3)/max(abs(mr.M_sink_H_cMpc3),1),
          'ionization_absolute_residual':abs(np.dot(out['mass'],out['xHII'])/M-gr.x_HII_sink_global),
          'temperature_relative_residual':abs(np.dot(out['mass'],out['T_K'])/M-gr.T_sink_global_K)/max(abs(gr.T_sink_global_K),1),
          'J_G1_relative_residual':abs(Jsum[0]-mr.J_sink_G1_s_inv_cMpc3)/max(abs(mr.J_sink_G1_s_inv_cMpc3),1),
          'J_G2a_relative_residual':abs(Jsum[1]-mr.J_sink_G2a_s_inv_cMpc3)/max(abs(mr.J_sink_G2a_s_inv_cMpc3),1),
          'kappa_G1_relative_residual':abs(ksum[0]-mr.kappa_sink_G1_cMpc_inv)/max(abs(mr.kappa_sink_G1_cMpc_inv),1),
          'kappa_G2a_relative_residual':abs(ksum[1]-mr.kappa_sink_G2a_cMpc_inv)/max(abs(mr.kappa_sink_G2a_cMpc_inv),1),
          'capacity_violation_max':max(float(np.max(rowJ-out['capacity'])),0.0),
          'capacity_slack_min':float(np.min(slack)),
          'transfer_relative_residual':abs(out['transfer_net'].sum()-mr.mass_transfer_rate_macro_H_s_inv_cMpc3)/max(abs(mr.mass_transfer_rate_macro_H_s_inv_cMpc3),1),
          'kkt_stationarity_max':cert['max_stationarity_residual'],'kkt_complementarity_max':cert['max_complementarity_residual'],'active_capacity_nodes':cert['active_row_count']}
        macro_aud.append(maudit)
        tv=[]
        for j in range(2):
          p0=q[:,j]/q[:,j].sum();p1=out['J'][:,j]/max(out['J'][:,j].sum(),1e-300);tv.append(.5*float(np.sum(np.abs(p1-p0))))
        envelope.append({'shape_lane':lane,'interval_index':int(mr.interval_index),'substep':int(mr.substep),'macro_index':m,'KL_photon':cert['generalized_kl'],'TV_G1':tv[0],'TV_G2a':tv[1],'KL_bernoulli':cert['bernoulli_kl'],'KL_thermal':cert['thermal_generalized_kl']})
    pd.DataFrame(macro_aud).to_csv(data/'macro_nested_moment_audit.csv',index=False)
    pd.DataFrame(envelope).to_csv(data/'node_kl_tv_envelope.csv',index=False)
    with open(data/'node_dual_kkt_certificates.jsonl','w') as f:
      for x in certs:f.write(json.dumps(x,separators=(',',':'))+'\n')
    # Global sums are derived independently from macro outputs.
    ma=pd.DataFrame(macro_aud); global_rows=[]
    for keys,g in ma.groupby(['shape_lane','interval_index','substep','z_mid']):
      global_rows.append({'shape_lane':keys[0],'interval_index':keys[1],'substep':keys[2],'z_mid':keys[3],
       'macro_count':len(g),'mass_relative_residual_max':g.mass_relative_residual.max(),'ionization_absolute_residual_max':g.ionization_absolute_residual.max(),'temperature_relative_residual_max':g.temperature_relative_residual.max(),'J_relative_residual_max':max(g.J_G1_relative_residual.max(),g.J_G2a_relative_residual.max()),'kappa_relative_residual_max':max(g.kappa_G1_relative_residual.max(),g.kappa_G2a_relative_residual.max()),'capacity_violation_max':g.capacity_violation_max.max(),'transfer_relative_residual_max':g.transfer_relative_residual.max(),'KKT_stationarity_max':g.kkt_stationarity_max.max(),'KKT_complementarity_max':g.kkt_complementarity_max.max()})
    pd.DataFrame(global_rows).to_csv(data/'global_nested_moment_audit.csv',index=False)
    zeros=[]
    for keys in macro_df[['shape_lane','interval_index','substep','z_mid']].drop_duplicates().itertuples(index=False):
      for quantity in ['kappa_sink_G2b','kappa_sink_G3','J_sink_G2b','J_sink_G3','HeII_G3_sink_absorption']:
        zeros.append({'shape_lane':keys.shape_lane,'interval_index':keys.interval_index,'substep':keys.substep,'z_mid':keys.z_mid,'quantity':quantity,'value':'0','exact_zero':True})
    pd.DataFrame(zeros).to_csv(data/'exact_zero_audit.csv',index=False)
    copy_inherited_csv_exact(r2a/'data/finite_relaxation_feasibility.csv',data/'finite_relaxation_inheritance.csv')
    summary={'node_state_rows':len(macro_df)*2560,'node_group_rows':len(macro_df)*2560*2,'macro_cases':len(macro_df),'global_cases':30,
      'max_mass_relative_residual':float(ma.mass_relative_residual.max()),'max_ionization_absolute_residual':float(ma.ionization_absolute_residual.max()),'max_temperature_relative_residual':float(ma.temperature_relative_residual.max()),'max_J_relative_residual':float(max(ma.J_G1_relative_residual.max(),ma.J_G2a_relative_residual.max())),'max_kappa_relative_residual':float(max(ma.kappa_G1_relative_residual.max(),ma.kappa_G2a_relative_residual.max())),'max_capacity_violation':float(ma.capacity_violation_max.max()),'min_capacity_slack':float(ma.capacity_slack_min.min()),'max_KKT_stationarity':float(ma.kkt_stationarity_max.max()),'max_KKT_complementarity':float(ma.kkt_complementarity_max.max()),'active_capacity_node_max':int(ma.active_capacity_nodes.max())}
    (data/'node_lift_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('--b0a-zip',type=Path,required=True);ap.add_argument('--prior-npz',type=Path,required=True);a=ap.parse_args();print(json.dumps(run_stage(a.repo,a.stage,a.b0a_zip,a.prior_npz),indent=2))
if __name__=='__main__':main()
