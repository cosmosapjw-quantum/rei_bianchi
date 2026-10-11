"""Only exact attempt66 failed-cell SIGMA quadrature, no gas/full maps."""
from pathlib import Path
import json,sys,math,hashlib,shutil
import numpy as np
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2]
for path in (Q1B,Q1B/'c10',Q1B/'c11/endpoint'):sys.path.insert(0,str(path))
import positive_absorption as old
from reconstruction import reconstruct
from opacity_native import NativeOpacity,THRESHOLDS_EV

def main():
    output=HERE/'evidence/ORDERS66';output.mkdir(exist_ok=False)
    shutil.copy2(__file__,output/'ASRUN_diagnose_orders.py')
    entry=json.loads((HERE/'evidence/EXTRACT66/RESULT.json').read_text());cell=reconstruct(**entry['parameters'])
    splits=[float(E/cell.R) for E in THRESHOLDS_EV if cell.a<E/cell.R<cell.b]
    rows=[];response={}
    with NativeOpacity() as opacity:
        for order in (64,128,256):
            measure=old._measure(cell,opacity,order,splits)
            k0,ke=old._kernels(measure.q,measure.P,measure.sigma,cell.R)
            direct=old._direct_heat(measure.q,measure.P,measure.sigma,cell.R)
            vector=old._components(old._sum(measure.P),cell.R*old._sum(measure.q*measure.P),k0,ke,direct)
            response[order]=vector
            rows.append(dict(order=order,diagnostics=measure.diagnostics,response=vector.tolist(),native_energy_min=float(min(cell.R*measure.q)),native_energy_max=float(max(cell.R*measure.q)),threshold_min_distance_ev=float(min(abs(cell.R*measure.q-54.42)))))
            np.savez_compressed(output/f'MEASURE_{order}.npz',q=measure.q,P=measure.P,sigma=measure.sigma,response=vector)
        metrics=[]
        for lo,hi in ((64,128),(128,256),(64,256)):
            coarse,fine=response[lo],response[hi];delta=abs(coarse-fine);scale=abs(fine)
            error=np.divide(delta,scale,out=np.zeros_like(delta),where=scale>0)
            metrics.append(dict(orders=[lo,hi],errors=error.tolist(),max_error=float(max(error)),pass_original_1e7=bool(np.all(error<=1e-7) and np.all(delta[scale==0]==0))))
        result=dict(schema='rei.c12.opacity.failure66.orders.v1',case=entry['parameters'],splits_q=splits,rows=rows,component_names=old.RESPONSE_COMPONENTS,comparisons=metrics,native_sigma_calls=opacity.native_calls,sigma_energy_evaluations=opacity.energy_evaluations,native_gas_calls=0,whole_maps=0)
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
