#!/usr/bin/env python3
"""SymPy/Decimal fallback for R2B KKT and sampled nested sums."""
from __future__ import annotations
import argparse,csv,gzip,json,tempfile
from decimal import Decimal,getcontext
from pathlib import Path
from typing import Any
import sympy as sp
from validate_stage import resolve_logical_file

getcontext().prec=80
D=Decimal

def kkt_symbolic_identities()->dict[str,bool]:
    q,mu,lam,s,c=sp.symbols('q mu lam s c', positive=True, real=True)
    x=q*sp.exp(-mu-lam)
    stationarity=sp.simplify(x/(q*sp.exp(-mu-lam))-1)==0
    active_row=sp.simplify(s*sp.exp(-sp.log(s/c))-c)==0
    inactive_row=sp.simplify(s*sp.exp(0)-s)==0
    active_complementarity=sp.simplify(sp.log(s/c)*(c-s*sp.exp(-sp.log(s/c))))==0
    inactive_complementarity=sp.simplify(sp.Integer(0)*(c-s))==0
    return {
      'exponential_stationarity':bool(stationarity),
      'active_row_equals_capacity':bool(active_row),
      'inactive_row_unchanged':bool(inactive_row),
      'active_complementarity':bool(active_complementarity),
      'inactive_complementarity':bool(inactive_complementarity),
    }

def _rel(a:D,b:D)->D:
    scale=max(abs(a),abs(b),D('1e-999'))
    return abs(a-b)/scale

def decimal_sample_audit(repo:Path,stage:Path)->dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix='r2b_exact_') as td:
        workspace=Path(td)
        state=resolve_logical_file(stage/'data/node_state_lift.csv.gz',workspace)
        groups=resolve_logical_file(stage/'data/node_group_lift.csv.gz',workspace)
        with gzip.open(state,'rt',newline='') as sf, gzip.open(groups,'rt',newline='') as gf:
            sr=csv.DictReader(sf); gr=csv.DictReader(gf)
            first=next(sr); key=(first['shape_lane'],first['interval_index'],first['substep'],first['macro_index'])
            state_rows=[first]
            for row in sr:
                k=(row['shape_lane'],row['interval_index'],row['substep'],row['macro_index'])
                if k!=key: break
                state_rows.append(row)
            group_rows=[]
            for row in gr:
                k=(row['shape_lane'],row['interval_index'],row['substep'],row['macro_index'])
                if k!=key: break
                group_rows.append(row)
    r2a=repo/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data'
    with open(r2a/'macro_projection.csv',newline='') as f:
        target=next(r for r in csv.DictReader(f) if (r['shape_lane'],r['interval_index'],r['substep'],r['macro_index'])==key)
    with open(r2a/'global_moment_lock.csv',newline='') as f:
        global_target=next(r for r in csv.DictReader(f) if (r['interval_index'],r['substep'])==(key[1],key[2]))
    mass=sum((D(r['M_sink_H_node_cMpc3']) for r in state_rows),D(0))
    mass_x=sum((D(r['M_sink_H_node_cMpc3'])*D(r['xHII_lift']) for r in state_rows),D(0))
    mass_T=sum((D(r['M_sink_H_node_cMpc3'])*D(r['T_lift_K']) for r in state_rows),D(0))
    capacity=sum((D(r['cycling_capacity_node_s_inv_cMpc3']) for r in state_rows),D(0))
    transfer=sum((D(r['mass_transfer_net_H_s_inv_cMpc3']) for r in state_rows),D(0))
    sums={g:{'J':D(0),'kappa':D(0)} for g in ('G1','G2a')}
    max_gamma=D(0)
    for r in group_rows:
        g=r['group'];J=D(r['J_sink_node_s_inv_cMpc3']);k=D(r['kappa_sink_node_cMpc_inv']);phi=D(r['Phi_current_Gamma_s_inv_cMpc2'])
        sums[g]['J']+=J;sums[g]['kappa']+=k;max_gamma=max(max_gamma,_rel(J,k*phi))
    residuals={
      'mass_relative':_rel(mass,D(target['M_sink_H_cMpc3'])),
      'ionization_absolute':abs(mass_x/mass-D(global_target['x_HII_sink_global'])),
      'temperature_relative':_rel(mass_T/mass,D(global_target['T_sink_global_K'])),
      'capacity_relative':_rel(capacity,D(target['cycling_capacity_macro_s_inv_cMpc3'])),
      'transfer_relative':_rel(transfer,D(target['mass_transfer_rate_macro_H_s_inv_cMpc3'])),
      'J_G1_relative':_rel(sums['G1']['J'],D(target['J_sink_G1_s_inv_cMpc3'])),
      'J_G2a_relative':_rel(sums['G2a']['J'],D(target['J_sink_G2a_s_inv_cMpc3'])),
      'kappa_G1_relative':_rel(sums['G1']['kappa'],D(target['kappa_sink_G1_cMpc_inv'])),
      'kappa_G2a_relative':_rel(sums['G2a']['kappa'],D(target['kappa_sink_G2a_cMpc_inv'])),
      'pointwise_current_gamma_relative_max':max_gamma,
    }
    zero_rows=list(csv.DictReader(open(stage/'data/exact_zero_audit.csv',newline='')))
    zeros_exact=all(r['value'].strip()=='0' and r['exact_zero'].strip().lower()=='true' for r in zero_rows)
    status=all(v<=D('1e-11') for v in residuals.values()) and zeros_exact and all(kkt_symbolic_identities().values())
    return {
      'status':'PASS' if status else 'FAIL','precision_decimal_digits':getcontext().prec,
      'sample_key':{'shape_lane':key[0],'interval_index':int(key[1]),'substep':int(key[2]),'macro_index':int(key[3])},
      'sample_state_rows':len(state_rows),'sample_group_rows':len(group_rows),
      'symbolic_kkt':kkt_symbolic_identities(),
      'residuals':{k:str(v) for k,v in residuals.items()},
      'structural_zero_rows':len(zero_rows),'structural_zeros_exact':zeros_exact,
    }

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();r=decimal_sample_audit(a.repo,a.stage);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
if __name__=='__main__':main()
