#!/usr/bin/env python3
"""Independent, file-reloaded validation for the R2B node lift."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any
import pandas as pd

ACTIVE_GROUPS=("G1","G2a")
TOL_REL=1.0e-11
TOL_ABS_X=1.0e-11
TOL_CAP_REL=1.0e-12
TOL_KKT=1.0e-9


def _f(row:dict[str,str], key:str)->float:
    return float(row[key])

def _i(row:dict[str,str], key:str)->int:
    return int(row[key])

def _node_key(row:dict[str,str])->tuple[str,int,int,int,int]:
    return (row['shape_lane'],_i(row,'interval_index'),_i(row,'substep'),_i(row,'macro_index'),_i(row,'micro_index'))

def _macro_key(row:dict[str,str])->tuple[str,int,int,int]:
    return (row['shape_lane'],_i(row,'interval_index'),_i(row,'substep'),_i(row,'macro_index'))

def _new_macro()->dict[str,float]:
    d={
      'state_rows':0.0,'mass':0.0,'mass_x':0.0,'mass_T':0.0,'capacity':0.0,
      'transfer':0.0,'p_mass_sum':0.0,'w_micro_sum':0.0,
      'J_G1':0.0,'J_G2a':0.0,'kappa_G1':0.0,'kappa_G2a':0.0,
      'q_G1':0.0,'q_G2a':0.0,
      'phi_G1_min':math.inf,'phi_G1_max':-math.inf,
      'phi_G2a_min':math.inf,'phi_G2a_max':-math.inf,
    }
    return d

def stream_validate_node_outputs(state_path:Path, group_path:Path)->dict[str,Any]:
    """Read state and group files in lockstep and reconstruct all node moments."""
    macro:dict[tuple[str,int,int,int],dict[str,float]]=defaultdict(_new_macro)
    max_cap_rel=0.0; max_cap_abs=0.0; cap_rel_fail=0
    max_gamma_rel=0.0; max_slack_copy_rel=0.0; max_cap_copy_rel=0.0
    bounds_fail=0; order_fail=0; group_order_fail=0
    state_rows=0; group_rows=0; previous_node=None
    with gzip.open(state_path,'rt',newline='') as sf, gzip.open(group_path,'rt',newline='') as gf:
        sr=csv.DictReader(sf); gr=csv.DictReader(gf)
        for s in sr:
            state_rows += 1
            nk=_node_key(s)
            if previous_node is not None and nk <= previous_node:
                order_fail += 1
            previous_node=nk
            pair=[]
            for expected in ACTIVE_GROUPS:
                try: g=next(gr)
                except StopIteration as exc: raise ValueError('group file ended before state file') from exc
                group_rows += 1
                if _node_key(g)!=nk: raise ValueError(f'node key mismatch: state={nk}, group={_node_key(g)}')
                if g['group']!=expected: group_order_fail += 1
                pair.append(g)
            mk=_macro_key(s); a=macro[mk]
            mass=_f(s,'M_sink_H_node_cMpc3'); x=_f(s,'xHII_lift'); temp=_f(s,'T_lift_K')
            cap=_f(s,'cycling_capacity_node_s_inv_cMpc3')
            a['state_rows']+=1; a['mass']+=mass; a['mass_x']+=mass*x; a['mass_T']+=mass*temp
            a['capacity']+=cap; a['transfer']+=_f(s,'mass_transfer_net_H_s_inv_cMpc3')
            a['p_mass_sum']+=_f(s,'p_mass_conditional'); a['w_micro_sum']+=_f(s,'w_micro')
            if mass<0 or not (0.0<=x<=1.0) or temp<=0 or cap<0: bounds_fail += 1
            Jsum=0.0; slacks=[]
            for g in pair:
                group=g['group']; J=_f(g,'J_sink_node_s_inv_cMpc3'); kappa=_f(g,'kappa_sink_node_cMpc_inv'); phi=_f(g,'Phi_current_Gamma_s_inv_cMpc2')
                q=_f(g,'q_prior_conditional'); slack=_f(g,'capacity_slack_after_all_groups_s_inv_cMpc3')
                Jsum += J; slacks.append(slack)
                a[f'J_{group}']+=J; a[f'kappa_{group}']+=kappa; a[f'q_{group}']+=q
                a[f'phi_{group}_min']=min(a[f'phi_{group}_min'],phi); a[f'phi_{group}_max']=max(a[f'phi_{group}_max'],phi)
                expected=phi*kappa
                gamma_rel=abs(J-expected)/max(abs(J),abs(expected),1e-300)
                max_gamma_rel=max(max_gamma_rel,gamma_rel)
                if J<0 or kappa<0 or q<0: bounds_fail += 1
            slack_ref=slacks[0]
            max_slack_copy_rel=max(max_slack_copy_rel,abs(slacks[0]-slacks[1])/max(abs(slacks[0]),abs(slacks[1]),abs(cap),1e-300))
            reconstructed=Jsum+slack_ref
            max_cap_copy_rel=max(max_cap_copy_rel,abs(cap-reconstructed)/max(abs(cap),abs(reconstructed),1e-300))
            violation=max(Jsum-cap,0.0)
            rel=violation/max(abs(Jsum),abs(cap),1e-300)
            max_cap_abs=max(max_cap_abs,violation); max_cap_rel=max(max_cap_rel,rel)
            if rel>TOL_CAP_REL: cap_rel_fail += 1
        try:
            extra=next(gr)
        except StopIteration:
            extra=None
        if extra is not None: raise ValueError('group file has rows after state file ended')
    return {
      'state_rows':state_rows,'group_rows':group_rows,'macro_count':len(macro),'macro':dict(macro),
      'max_capacity_absolute_violation':max_cap_abs,'max_capacity_relative_violation':max_cap_rel,
      'capacity_relative_failure_count':cap_rel_fail,
      'max_current_gamma_relative_residual':max_gamma_rel,
      'max_duplicate_slack_relative_residual':max_slack_copy_rel,
      'max_state_capacity_reconstruction_relative_residual':max_cap_copy_rel,
      'physical_bound_failure_count':bounds_fail,'state_order_failure_count':order_fail,
      'group_order_failure_count':group_order_fail,
    }

def _rel(a:float,b:float)->float:
    return abs(a-b)/max(abs(a),abs(b),1e-300)

def files_identical(a: Path, b: Path) -> bool:
    """Return true only for byte-identical files."""
    if a.stat().st_size != b.stat().st_size:
        return False
    with a.open('rb') as fa, b.open('rb') as fb:
        while True:
            ba=fa.read(1024*1024); bb=fb.read(1024*1024)
            if ba != bb:
                return False
            if not ba:
                return True

def resolve_logical_file(logical: Path, workspace: Path) -> Path:
    """Return a logical file, reconstructing verified binary parts when needed."""
    if logical.exists():
        return logical
    parts_dir=Path(str(logical)+'.parts')
    manifest_path=parts_dir/'parts_manifest.json'
    if not manifest_path.exists():
        raise FileNotFoundError(f'missing logical file and parts manifest: {logical}')
    manifest=json.loads(manifest_path.read_text())
    if manifest.get('original_name') != logical.name:
        raise ValueError('parts manifest original_name mismatch')
    workspace.mkdir(parents=True,exist_ok=True)
    output=workspace/logical.name
    digest=hashlib.sha256(); total=0
    with output.open('wb') as dst:
        for entry in manifest['parts']:
            part=parts_dir/entry['name']; payload=part.read_bytes()
            if len(payload)!=int(entry['size_bytes']) or hashlib.sha256(payload).hexdigest()!=entry['sha256']:
                raise ValueError(f'part verification failed: {part}')
            dst.write(payload); digest.update(payload); total+=len(payload)
    if total!=int(manifest['size_bytes']) or digest.hexdigest()!=manifest['sha256']:
        raise ValueError(f'reconstructed logical-file verification failed: {logical}')
    return output

def validate_stage(repo:Path, stage:Path)->dict[str,Any]:
    data=stage/'data'
    with tempfile.TemporaryDirectory(prefix='r2b_validate_') as td:
        workspace=Path(td)
        state_path=resolve_logical_file(data/'node_state_lift.csv.gz',workspace)
        group_path=resolve_logical_file(data/'node_group_lift.csv.gz',workspace)
        streamed=stream_validate_node_outputs(state_path,group_path)
    r2a=repo/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK'/'data'
    macro_targets=pd.read_csv(r2a/'macro_projection.csv')
    global_targets=pd.read_csv(r2a/'global_moment_lock.csv')
    mt={(str(r.shape_lane),int(r.interval_index),int(r.substep),int(r.macro_index)):r for r in macro_targets.itertuples(index=False)}
    gt={(int(r.interval_index),int(r.substep)):r for r in global_targets.itertuples(index=False)}
    macro_max=defaultdict(float); macro_fail=0
    global_acc:dict[tuple[str,int,int],dict[str,float]]=defaultdict(lambda:defaultdict(float))
    for key,a in streamed['macro'].items():
        if key not in mt: raise ValueError(f'output macro absent from target: {key}')
        t=mt[key]; lane,ii,ss,_=key
        vals={
          'mass_relative':_rel(a['mass'],float(t.M_sink_H_cMpc3)),
          'ionization_absolute':abs(a['mass_x']/a['mass']-float(gt[(ii,ss)].x_HII_sink_global)),
          'temperature_relative':_rel(a['mass_T']/a['mass'],float(gt[(ii,ss)].T_sink_global_K)),
          'capacity_relative':_rel(a['capacity'],float(t.cycling_capacity_macro_s_inv_cMpc3)),
          'transfer_relative':_rel(a['transfer'],float(t.mass_transfer_rate_macro_H_s_inv_cMpc3)),
          'J_G1_relative':_rel(a['J_G1'],float(t.J_sink_G1_s_inv_cMpc3)),
          'J_G2a_relative':_rel(a['J_G2a'],float(t.J_sink_G2a_s_inv_cMpc3)),
          'kappa_G1_relative':_rel(a['kappa_G1'],float(t.kappa_sink_G1_cMpc_inv)),
          'kappa_G2a_relative':_rel(a['kappa_G2a'],float(t.kappa_sink_G2a_cMpc_inv)),
          'p_mass_sum_absolute':abs(a['p_mass_sum']-1.0),
          'w_micro_sum_absolute':abs(a['w_micro_sum']-1.0),
          'q_G1_sum_absolute':abs(a['q_G1']-1.0),
          'q_G2a_sum_absolute':abs(a['q_G2a']-1.0),
          'phi_G1_relative':max(_rel(a['phi_G1_min'],float(t.current_Gamma_flux_G1_s_inv_cMpc2)),_rel(a['phi_G1_max'],float(t.current_Gamma_flux_G1_s_inv_cMpc2))),
          'phi_G2a_relative':max(_rel(a['phi_G2a_min'],float(t.current_Gamma_flux_G2a_s_inv_cMpc2)),_rel(a['phi_G2a_max'],float(t.current_Gamma_flux_G2a_s_inv_cMpc2))),
        }
        for n,v in vals.items(): macro_max[n]=max(macro_max[n],float(v))
        if a['state_rows']!=2560 or any((v>TOL_ABS_X if 'absolute' in n else v>TOL_REL) for n,v in vals.items()): macro_fail+=1
        ga=global_acc[(lane,ii,ss)]
        for n in ('mass','mass_x','mass_T','capacity','transfer','J_G1','J_G2a','kappa_G1','kappa_G2a'): ga[n]+=a[n]
    if len(mt)!=len(streamed['macro']): raise ValueError(f'macro count mismatch output={len(streamed["macro"])} target={len(mt)}')
    global_max=defaultdict(float); global_fail=0
    for (lane,ii,ss),a in global_acc.items():
        t=gt[(ii,ss)]
        vals={
          'mass_relative':_rel(a['mass'],float(t.N_H_sink_global_cMpc3)),
          'ionization_absolute':abs(a['mass_x']/a['mass']-float(t.x_HII_sink_global)),
          'temperature_relative':_rel(a['mass_T']/a['mass'],float(t.T_sink_global_K)),
          'capacity_relative':_rel(a['capacity'],float(t.cycling_capacity_global_s_inv_cMpc3)),
          'transfer_relative':_rel(a['transfer'],float(t.diffuse_sink_mass_transfer_rate_H_s_inv_cMpc3)),
          'J_G1_relative':_rel(a['J_G1'],float(t.J_sink_G1_global_s_inv_cMpc3)),
          'J_G2a_relative':_rel(a['J_G2a'],float(t.J_sink_G2a_global_s_inv_cMpc3)),
          'kappa_G1_relative':_rel(a['kappa_G1'],float(t.kappa_sink_G1_global_cMpc_inv)),
          'kappa_G2a_relative':_rel(a['kappa_G2a'],float(t.kappa_sink_G2a_global_cMpc_inv)),
        }
        for n,v in vals.items(): global_max[n]=max(global_max[n],float(v))
        if any((v>TOL_ABS_X if 'absolute' in n else v>TOL_REL) for n,v in vals.items()): global_fail+=1
    # KKT certificates are independently reloaded.
    cert_count=0; max_stationarity=0.0; max_complementarity=0.0; max_column=0.0; cert_status_fail=0
    with open(data/'node_dual_kkt_certificates.jsonl') as f:
        for line in f:
            c=json.loads(line); cert_count+=1
            if c.get('status')!='PASS': cert_status_fail+=1
            max_stationarity=max(max_stationarity,float(c['max_stationarity_residual']))
            max_complementarity=max(max_complementarity,float(c['max_complementarity_residual']))
            max_column=max(max_column,float(c['max_column_relative_residual']))
    zeros=pd.read_csv(data/'exact_zero_audit.csv',dtype={'value':str})
    zero_fail=int(((zeros['value'].astype(str).str.strip()!='0')|(~zeros['exact_zero'].astype(bool))).sum())
    inherited_ok=files_identical(data/'finite_relaxation_inheritance.csv',r2a/'finite_relaxation_feasibility.csv')
    gates={
      'row_counts':streamed['state_rows']==1382400 and streamed['group_rows']==2764800,
      'macro_count':streamed['macro_count']==540 and len(global_acc)==30,
      'deterministic_order':streamed['state_order_failure_count']==0 and streamed['group_order_failure_count']==0,
      'physical_bounds':streamed['physical_bound_failure_count']==0,
      'capacity_relative':streamed['max_capacity_relative_violation']<=TOL_CAP_REL and streamed['capacity_relative_failure_count']==0,
      'capacity_copy':streamed['max_state_capacity_reconstruction_relative_residual']<=TOL_REL and streamed['max_duplicate_slack_relative_residual']<=TOL_REL,
      'current_gamma':streamed['max_current_gamma_relative_residual']<=TOL_REL,
      'macro_nested_moments':macro_fail==0,
      'global_nested_moments':global_fail==0,
      'kkt':cert_count==540 and cert_status_fail==0 and max_stationarity<=TOL_KKT and max_complementarity<=TOL_KKT and max_column<=TOL_REL,
      'structural_zeros':len(zeros)==150 and zero_fail==0,
      'finite_relaxation_inheritance':inherited_ok,
    }
    report={
      'status':'PASS' if all(gates.values()) else 'FAIL', 'gates':gates,
      'counts':{'state_rows':streamed['state_rows'],'group_rows':streamed['group_rows'],'macro_cases':streamed['macro_count'],'global_cases':len(global_acc),'certificate_count':cert_count,'exact_zero_rows':len(zeros)},
      'stream':{k:v for k,v in streamed.items() if k!='macro'},
      'macro_max_residuals':dict(macro_max),'global_max_residuals':dict(global_max),
      'macro_failure_count':macro_fail,'global_failure_count':global_fail,
      'kkt':{'max_stationarity':max_stationarity,'max_complementarity':max_complementarity,'max_column_relative_residual':max_column,'status_failure_count':cert_status_fail},
      'structural_zero_failure_count':zero_fail,
      'finite_relaxation_inheritance_exact':inherited_ok,
      'tolerances':{'relative':TOL_REL,'ionization_absolute':TOL_ABS_X,'capacity_relative':TOL_CAP_REL,'kkt':TOL_KKT},
    }
    return report

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--stage',type=Path,required=True); ap.add_argument('--output',type=Path)
    a=ap.parse_args(); report=validate_stage(a.repo,a.stage)
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(text)
    print(text,end='')
    raise SystemExit(0 if report['status']=='PASS' else 1)

if __name__=='__main__': main()
