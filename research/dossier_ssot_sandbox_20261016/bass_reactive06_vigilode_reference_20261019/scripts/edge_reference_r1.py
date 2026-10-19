#!/usr/bin/env python3
"""Fresh recovery R1 manufactured near-edge controls on actual BASS geometry."""
import argparse
import datetime
import json
from pathlib import Path
import time
import numpy as np
from independent_birth_reference import Fixture,PathGrid,EDGES,EV_J,VERSION,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);start=time.perf_counter();rows=[]
    for case in ('SIGNED_MINUS','SIGNED_PLUS'):
        f=Fixture(a.parent,case);aa=f.geometry.at(np.array([0.,.5,1.]))[0]
        for mu in (0.,1/np.sqrt(3.),1.):
            n=np.array([np.sqrt(1-mu*mu),0.,mu])
            mid_ratio=np.sqrt(np.sum((aa[0]*n/aa[1])**2))
            for gate in EDGES:
                energy=gate/mid_ratio;K=(aa[0]*energy*n)[None,:]
                results=[]
                for degree in (32,64):
                    left=PathGrid(f,np.array([0.]),degree,16,np.array([.5])).evaluate(K)
                    right=PathGrid(f,np.array([.5]),degree,16,np.array([1.])).evaluate(K)
                    P=left['P'][0]*right['P'][0]
                    events=left['events'][0]+left['P'][0]*right['events'][0]
                    heat=left['heat'][0]+left['P'][0]*right['heat'][0]
                    absorbed=left['absorbed_energy'][0]+left['P'][0]*right['absorbed_energy'][0]
                    work=left['work'][0]+left['P'][0]*right['work'][0]
                    nr=P+np.sum(events)-1
                    er=(P*right['end_energy_ev'][0]*EV_J+absorbed-energy*EV_J-work)/(energy*EV_J)
                    if np.any(events<0) or np.any(heat<0):raise ValueError('negative edge event/heat')
                    results.append({'event_degree':degree,'survival':float(P),'events':events.tolist(),'heat':heat.tolist(),
                       'absorbed_j':float(absorbed),'work_j':float(work),'number_residual':float(nr),'energy_residual_relative':float(er)})
                mid_energy=np.sqrt(np.sum((K[0]/aa[1])**2))
                rows.append({'case':case,'mu':float(mu),'gate_ev':float(gate),'birth_energy_ev':float(energy),
                  'manufactured_cut_q':.5,'midpoint_gate_difference_ev':float(mid_energy-gate),
                  'event_refinement_max_absolute':float(np.max(np.abs(np.array(results[1]['events'])-results[0]['events']))),
                  'results':results})
    receipt={'version':VERSION,'status':'COMPLETED_FRESH_RECOVERY_EXECUTION','historical_pass_inherited':False,
      'scope':'24 manufactured redshift-exit witnesses on actual expanding BASS +/- geometries; not native threshold dominance or blueshift admission',
      'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':sha(__file__),
      'integrator_source_sha256':sha(Path(__file__).with_name('independent_birth_reference.py')),
      'cases':len(rows),'wall_s':time.perf_counter()-start,'rows':rows,
      'max_number_residual':max(abs(v['number_residual']) for r in rows for v in r['results']),
      'max_energy_residual_relative':max(abs(v['energy_residual_relative']) for r in rows for v in r['results']),
      'max_event_refinement_absolute':max(r['event_refinement_max_absolute'] for r in rows)}
    out=a.output/'EDGE_REFERENCE.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rows'}))


if __name__=='__main__':main()
