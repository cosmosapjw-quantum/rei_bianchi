#!/usr/bin/env python3
"""Build the state-derived dynamic-opacity measure and conditional RN lift."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd

GROUPS=("G1","G2a","G2b","G3")
SPECIES=("HI","HeI","HeII")
SUPPORT={"HI":{"G1","G2a","G2b","G3"},"HeI":{"G2a","G2b","G3"},"HeII":{"G3"}}
H=0.68
KPC_CM=3.0856775814913673e21


def load_b0a(path:Path):
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location('r1b_r1_hierarchy',path)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def sha_array(a:np.ndarray)->str:
    b=np.ascontiguousarray(a,dtype='<f8').tobytes(); return hashlib.sha256(b).hexdigest()


def tv(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float); a=a/a.sum(); b=b/b.sum(); return 0.5*float(np.abs(a-b).sum())


def shared_rn_lift(measure:np.ndarray,kappa_total:float,current_total:float):
    h=np.asarray(measure,float)
    if np.any(h<0) or not np.all(np.isfinite(h)): raise ValueError('invalid absorption measure')
    if h.sum()<=0:
        q=np.zeros_like(h)
        if kappa_total!=0 or current_total!=0: raise ValueError('zero support with nonzero target')
    else:
        q=h/h.sum()
        # One closure correction on q, shared by kappa and current.
        q[-1]+=1.0-q.sum()
    k=kappa_total*q
    phi=current_total/kappa_total if kappa_total>0 else 0.0
    j=phi*k
    return q,k,j,phi


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--inputs',type=Path,required=True); ap.add_argument('--forcing',type=Path,required=True); ap.add_argument('--atomic',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    root=a.inputs
    b0=root/'Bianchi_Reionization_Stage_P0_5_B2C2B0A_HIERARCHICAL_TWO_SCALE_OPACITY_CHEMISTRY_CLOSURE_LOCK'
    p04=root/'Bianchi_Reionization_Stage_P0_4_PAPER_CODE_CHECKPOINT_REGRESSION'
    r2b=root/'Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2B_MOMENT_CONSTRAINED_NODE_LIFT_HISTORY'
    mod=load_b0a(b0/'src/hierarchical_two_scale_closure.py')
    forcing=pd.read_csv(a.forcing)
    atomic=pd.read_csv(a.atomic/'verner_gray_and_limit_moments.csv')
    sig={(r.species,r.group):float(r.gray_sigma_cm2) for r in atomic.itertuples()}
    micro_npz=np.load(b0/'data/fixed_micro_parcel_template_z6.npz')
    fixed_micro=mod.FixedMicroTemplate(n_delta=len(micro_npz['w_delta']),n_t=micro_npz['w_temperature'].shape[1],w_delta=micro_npz['w_delta'],w_temperature=micro_npz['w_temperature'],u_delta=micro_npz['u_delta'],u_temperature=micro_npz['u_temperature'],weight_lock_redshift=6.0)
    macro_template=pd.read_csv(b0/'data/fixed_macro_parcel_template_z6.csv')
    mapping=pd.read_csv(p04/'data/density_mapping_colossus_1_3_10_port.csv')
    prior=np.load(r2b/'data/b0a_full_node_priors.npz')
    macro_rows=[]; hash_rows=[]; audit_rows=[]; hierarchy_rows=[]; tv_rows=[]
    prior_lanes=['LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR']
    for rec in forcing.sort_values(['interval_index','node_index']).itertuples(index=False):
        frac=float(rec.fraction); z_eval=float(rec.z_start+frac*(rec.z_end-rec.z_start))
        hs=mod.B2C0.HistoryState(z=z_eval,x_hii=float(rec.xHII),x_heii=float(rec.xHeII),x_heiii=float(rec.xHeIII),temperature=float(rec.T_K),gamma_hi=float(getattr(rec,'Gamma_HI_s_1',getattr(rec,'Gamma_HI_s-1',0.0))))
        # pandas sanitizes invalid identifier names; retrieve by column position instead.
        gamma_hi=float(pd.Series(rec._asdict()).get('Gamma_HI_s-1', forcing.loc[(forcing.interval_index==rec.interval_index)&(forcing.node_index==rec.node_index),'Gamma_HI_s-1'].iloc[0]))
        hs=mod.B2C0.HistoryState(z=z_eval,x_hii=float(rec.xHII),x_heii=float(rec.xHeII),x_heiii=float(rec.xHeIII),temperature=float(rec.T_K),gamma_hi=gamma_hi)
        macro=mod.macro_measure(z_eval,mapping,macro_template)
        nodes,means,diag=mod.construct_hierarchy(hs,macro,fixed_micro,'BASELINE')
        W=nodes.W_node.to_numpy(float); delta=nodes.delta_total.to_numpy(float)
        nH=mod.NH0*(1+z_eval)**3*delta; nHe=mod.YHE*nH
        densities={'HI':nH*(1-nodes.xHII.to_numpy(float)),'HeI':nHe*nodes.xHeI.to_numpy(float),'HeII':nHe*nodes.xHeII.to_numpy(float)}
        Lproper=(2.0/H)*KPC_CM/(1+z_eval)
        hierarchy_rows.append({'interval_index':int(rec.interval_index),'node_index':int(rec.node_index),'fraction':frac,'z_eval':z_eval,'weight_sum':float(W.sum()),'mass_density_sum':float(diag['mass_density_sum']),'mass_xHII':float(diag['mass_xHII']),'target_xHII':float(rec.xHII),'mass_xHeII':float(diag['mass_xHeII']),'target_xHeII':float(rec.xHeII),'mass_xHeIII':float(diag['mass_xHeIII']),'target_xHeIII':float(rec.xHeIII),'temperature_weighted_mean':float(diag['temperature_weighted_mean']),'target_T_K':float(rec.T_K)})
        for g in GROUPS:
            tau_species={s:(densities[s]*sig[(s,g)]*Lproper if g in SUPPORT[s] else np.zeros_like(W)) for s in SPECIES}
            tau=sum(tau_species.values())
            h=W*tau
            finite=W*(-np.expm1(-np.clip(tau,0,745)))
            kappa_total=float(forcing.loc[(forcing.interval_index==rec.interval_index)&(forcing.node_index==rec.node_index),f'kappa_{g}_cMpc-1'].iloc[0])
            current_total=float(forcing.loc[(forcing.interval_index==rec.interval_index)&(forcing.node_index==rec.node_index),f'absorption_{g}_s-1_cMpc-3'].iloc[0])
            q,k,j,phi=shared_rn_lift(h,kappa_total,current_total)
            qfinite=finite/finite.sum() if finite.sum()>0 else np.zeros_like(finite)
            common=np.divide(j,k,out=np.full_like(j,phi),where=k>0)
            support_mask=h>0
            common_res=float(np.max(np.abs(common[support_mask]-phi))/max(abs(phi),1.0)) if np.any(support_mask) else 0.0
            audit_rows.append({'interval_index':int(rec.interval_index),'node_index':int(rec.node_index),'fraction':frac,'z_eval':z_eval,'group':g,'global_kappa_cMpc_inv':kappa_total,'global_current_s_inv_cMpc3':current_total,'incident_flux_s_inv_cMpc2':phi,'q_sum_residual':abs(q.sum()-(1.0 if h.sum()>0 else 0.0)),'kappa_moment_relative_residual':abs(k.sum()-kappa_total)/max(abs(kappa_total),1.0),'current_moment_relative_residual':abs(j.sum()-current_total)/max(abs(current_total),1.0),'common_flux_relative_residual':common_res,'negative_measure_count':int(np.count_nonzero(h<0)),'zero_support_nonzero_allocation_count':int(np.count_nonzero((h==0)&(q!=0))),'differential_vs_finite_TV':tv(q,qfinite) if q.sum()>0 and qfinite.sum()>0 else 0.0,'tau_min':float(tau.min()),'tau_max':float(tau.max()),'tau_weighted_mean':float(np.dot(W,tau)),'proper_cell_length_cm':Lproper})
            hash_rows.append({'interval_index':int(rec.interval_index),'node_index':int(rec.node_index),'fraction':frac,'z_eval':z_eval,'group':g,'node_count':len(q),'q_sha256':sha_array(q),'tau_sha256':sha_array(tau),'q_min':float(q.min()),'q_max':float(q.max()),'q_sum':float(q.sum())})
            mi=nodes.macro_index.to_numpy(int)
            for macro_index in range(18):
                sel=mi==macro_index
                macro_rows.append({'interval_index':int(rec.interval_index),'node_index':int(rec.node_index),'fraction':frac,'z_eval':z_eval,'group':g,'macro_index':macro_index,'q_macro':float(q[sel].sum()),'kappa_macro_cMpc_inv':float(k[sel].sum()),'current_macro_s_inv_cMpc3':float(j[sel].sum()),'tau_weighted_macro':float(np.dot(W[sel],tau[sel]))})
            # Compare only at interval midpoint, where inherited priors are defined.
            if abs(frac-0.5)<1e-12 and g in {'G1','G2a'}:
                zlabel=f"z{float(rec.z_mid):.2f}"
                for lane in prior_lanes:
                    key=f"{zlabel}_{lane}_{g}_q_node"
                    if key in prior:
                        tv_rows.append({'interval_index':int(rec.interval_index),'z_mid':float(rec.z_mid),'group':g,'shape_lane':lane,'state_measure_vs_inherited_shape_TV':tv(q,prior[key])})
        print(f"completed interval={int(rec.interval_index)} node={int(rec.node_index)} fraction={frac:.8f}", flush=True)
    pd.DataFrame(macro_rows).to_csv(a.output/'dynamic_macro_disintegration.csv',index=False)
    pd.DataFrame(hash_rows).to_csv(a.output/'dynamic_node_measure_hashes.csv',index=False)
    adf=pd.DataFrame(audit_rows); adf.to_csv(a.output/'dynamic_global_moment_audit.csv',index=False)
    hdf=pd.DataFrame(hierarchy_rows); hdf.to_csv(a.output/'hierarchy_state_moment_audit.csv',index=False)
    tdf=pd.DataFrame(tv_rows); tdf.to_csv(a.output/'state_measure_vs_shape_prior_TV.csv',index=False)
    summary={'classification':'DYNAMIC_OPACITY_PARTITION_SUMMARY','selected_time_rows':int(len(forcing)),'dynamic_node_equivalents':int(len(forcing)*46080),'group_cases':int(len(adf)),'macro_group_cases':int(len(macro_rows)),'max_q_sum_residual':float(adf.q_sum_residual.max()),'max_kappa_moment_relative_residual':float(adf.kappa_moment_relative_residual.max()),'max_current_moment_relative_residual':float(adf.current_moment_relative_residual.max()),'max_common_flux_relative_residual':float(adf.common_flux_relative_residual.max()),'negative_measure_count_total':int(adf.negative_measure_count.sum()),'zero_support_nonzero_allocation_count_total':int(adf.zero_support_nonzero_allocation_count.sum()),'differential_vs_finite_TV_range':[float(adf.differential_vs_finite_TV.min()),float(adf.differential_vs_finite_TV.max())],'tau_range':[float(adf.tau_min.min()),float(adf.tau_max.max())],'max_hierarchy_weight_residual':float((hdf.weight_sum-1).abs().max()),'max_hierarchy_mass_density_residual':float((hdf.mass_density_sum-1).abs().max()),'max_H_fraction_residual':float((hdf.mass_xHII-hdf.target_xHII).abs().max()),'max_HeII_fraction_residual':float((hdf.mass_xHeII-hdf.target_xHeII).abs().max()),'max_HeIII_fraction_residual':float((hdf.mass_xHeIII-hdf.target_xHeIII).abs().max()),'max_temperature_relative_residual':float(np.max(np.abs(hdf.temperature_weighted_mean-hdf.target_T_K)/hdf.target_T_K)),'shape_prior_TV_range':[float(tdf.state_measure_vs_inherited_shape_TV.min()),float(tdf.state_measure_vs_inherited_shape_TV.max())] if len(tdf) else None,'partition_policy':'CONDITIONAL_UNIQUE_SHARED_RADON_NIKODYM_DENSITY_ON_STATE_DERIVED_ABSORPTION_MEASURE'}
    (a.output/'dynamic_opacity_partition_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
