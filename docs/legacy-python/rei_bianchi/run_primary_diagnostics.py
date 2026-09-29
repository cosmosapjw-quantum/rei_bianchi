from __future__ import annotations
import argparse,json,time,traceback
from pathlib import Path
import pandas as pd
import node_resolved_joint_history as M

def main(r1,b0a,b0c,out):
 out.mkdir(parents=True,exist_ok=True)
 hist,forcings,macro_template,micro,node_table,mapping=M.load_inputs(r1,b0a,b0c)
 rh=pd.read_csv(b0c/'data/primary_joint_history.csv');rl=pd.read_csv(b0c/'data/primary_joint_ledger.csv');first=rh.iloc[0];fl=rl.iloc[0]
 initial={'N_sink':float(first.N_sink),'x_sink':float(first.x_sink),'T_sink':float(first.T_sink),'nH_cm3':float(fl.cloud_density_cm3),'radius_cm':float(fl.cloud_radius_proper_pc)*3.085677581491367e18}
 status=[]
 for ns in [1,2,4]:
  t=time.perf_counter()
  try:
   ep,g,l,s=M.run_lane(f'PRIMARY_DIAGNOSTIC_DT_OVER_{ns}','LOCAL_NEUTRAL_HAZARD_PRIMARY','BASELINE','DETERMINISTIC',hist,forcings,macro_template,micro,mapping,ns,initial,save_nodes=False)
   elapsed=time.perf_counter()-t
   g.to_csv(out/f'primary_dt_over_{ns}_global.csv',index=False);l.to_csv(out/f'primary_dt_over_{ns}_ledger.csv',index=False);s.to_csv(out/f'primary_dt_over_{ns}_sink.csv.gz',index=False,compression='gzip')
   status.append({'substeps':ns,'success':True,'elapsed_seconds':elapsed,'completed_intervals':len(g),'sink_H_fraction_final':float(g.iloc[-1].sink_H_fraction),'max_sink_H_fraction':float(g.sink_H_fraction.max()),'max_reaction_limiter':float(l.reaction_limiter_weighted.max()),'max_energy_limiter':float(l.energy_limiter_weighted.max()),'max_sink_volume_filling':float(l.sink_volume_filling_max.max()),'max_macro_redistribution_TV':float(l.macro_sink_redistribution_TV.max()),'max_sink_opacity_fraction':float(l.sink_opacity_fraction_max.max())})
  except Exception as exc:
   elapsed=time.perf_counter()-t
   status.append({'substeps':ns,'success':False,'elapsed_seconds':elapsed,'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc()})
   # Stop finer refinements once a coarser accepted sequence fails.
   if ns>=2: break
 pd.DataFrame(status).to_csv(out/'primary_diagnostic_status.csv',index=False)
 (out/'primary_diagnostic_status.json').write_text(json.dumps(status,indent=2))
 print(json.dumps(status,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--r1',type=Path,required=True);p.add_argument('--b0a',type=Path,required=True);p.add_argument('--b0c',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.r1,a.b0a,a.b0c,a.output)
