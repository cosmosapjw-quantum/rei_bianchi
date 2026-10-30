#!/usr/bin/env python3
"""Matched source (not performance) test: spectral Gauss order and cell subdivision."""
import csv,json,pathlib,sys,numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import causal_firstflight as cc
ROOT=cc.ROOT
INDICES=[0,16,48,80,96,112,128,144,160,176,191,192]

def run():
    metrics=['mean_absorptions_per_pair','P2','absorbed_H_I','absorbed_He_I','absorbed_He_II',
        'absorbed_primary_electron_eV','absorbed_binding_eV','cosmological_redshift_work_eV','survivor_eV_at_z2']
    rows=[]
    with cc.owner() as m:
        data,H,nb,epochs,bins,net=m.load_original();x=data['x'];Y=data['Y'];m._z_source=data['z']
        for k in INDICES:
            grades={}
            for o,s in [(8,4),(16,4),(32,8)]:
                val,*_=cc.lightcone(m,net,x,H,nb,Y,k,order=o,substeps=s)
                grades[(o,s)]=val
            for key in metrics:
                a=grades[(8,4)][key];b=grades[(16,4)][key];c=grades[(32,8)][key]
                rows.append({'epoch':k,'z':float(data['z'][k]),'quantity':key,
                   'order8_sub4':a,'order16_sub4':b,'order32_sub8':c,
                   'abs_delta_16to32':abs(b-c),
                   'relative_delta_16to32':abs(b-c)/max(abs(c),1e-8)})
    result={'epochs':len(INDICES),'rows':len(rows),'order16_32_max_abs':max(r['abs_delta_16to32'] for r in rows),
            'order16_32_max_relative_floor1e-8':max(r['relative_delta_16to32'] for r in rows)}
    path=ROOT/'results/CONVERGENCE_108.csv'
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (ROOT/'results/CONVERGENCE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result
if __name__=='__main__':run()
