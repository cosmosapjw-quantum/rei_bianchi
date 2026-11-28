#!/usr/bin/env python3
"""Read-only saved-trajectory shear memory. Never launches an ODE or NCP task."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.integrate import simpson
from stress_memory import memory_budget,sector_observables

FIELDS=('H_per_s','S_h','P_m_h','P_r_h','b','p_m_J_m3','p_r_J_m3')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def write_csv(p,rows):
    with Path(p).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def pack_rei(root,out):
    """Pack original stored columns, preserving their float64 bytes; S_h is derived."""
    lanes=(('radiation_slice','matter_radiation_20261021/decomposition/cases'),
           ('new_matter_and_mixed','matter_radiation_20261021/results/new_sweep/cases'))
    cases=[];values=[];x=None;copied_values=0;workmax=0.
    for lane,rel in lanes:
        for p in sorted((root/rel).glob('*.npz')):
            with np.load(p,allow_pickle=False) as z:
                if x is None:x=z['x'].copy()
                if not np.array_equal(x,z['x']):raise ValueError('TIME_GRID_MISMATCH')
                v=np.stack([z['H_per_s'],np.sqrt(3)*z['s_over_H'],z['signed_Pi_m'],z['signed_Pi_r'],z['b'],z['p_m_J_m3'],z['p_r_J_m3']])
                for col,key in ((0,'H_per_s'),(2,'signed_Pi_m'),(3,'signed_Pi_r'),(4,'b'),(5,'p_m_J_m3'),(6,'p_r_J_m3')):
                    if v[col].tobytes()!=z[key].tobytes():raise ValueError('SELECTED_COLUMN_BYTE_MISMATCH')
                    copied_values+=len(x)
                for key,pressure in [('work_m_J_m3_per_x','p_m_J_m3'),('work_r_J_m3_per_x','p_r_J_m3')]:
                    predicted=-6*z['s_over_H']*z[pressure]
                    workmax=max(workmax,float(np.max(abs(predicted-z[key]))))
            values.append(v);cases.append({'id':p.stem,'lane':lane,'source_path':str(p.relative_to(root)),'source_sha256':sha(p)})
    if len(cases)!=1231:raise ValueError('EXPECTED_625_PLUS_606_UNIQUE_STORED_CASES')
    data=np.stack(values)
    np.savez_compressed(out/'long.npz',x=x,values=data,case_ids=np.array([r['id'] for r in cases]))
    return {'file':'long.npz','sha256':sha(out/'long.npz'),'fields':FIELDS,'cases':cases,'selected_raw_values_byte_matched':copied_values,
            'derived_field':'S_h=sqrt(3)*source.s_over_H','source_work_formula_max_abs':workmax,
            'scope':'REI198 collisionless LRS zbar20 to4; half-contraction inputs; not short C15'}

def pack_hh(root,out):
    p=root/'sector_split_20261021/data/SECTOR_HISTORY.csv';groups={}
    with p.open() as f:
        for row in csv.DictReader(f):groups.setdefault(row['case_id'],[]).append(row)
    vals=[];cases=[];x=None
    for cid,rows in sorted(groups.items()):
        rows=sorted(rows,key=lambda z:int(z['sample']))
        arr=lambda k:np.array([float(z[k]) for z in rows])
        xx=arr('x')
        if x is None:x=xx
        if not np.array_equal(x,xx):raise ValueError('HH_GRID_MISMATCH')
        v=np.stack([arr('H_per_s'),arr('Sigma_signed')/np.sqrt(2),arr('Pi_m_signed')/np.sqrt(2),arr('Pi_r_signed')/np.sqrt(2),
                    arr('pi_s_m_J_m3'),arr('pi_s_r_J_m3')])
        vals.append(v);cases.append({'id':cid,'lane':'HH74_CONTROL','b_available':False})
    if len(cases)!=63:raise ValueError('EXPECTED_63_STORED_HH_CONTROLS')
    # This source CSV has no b field: do not invent one.
    np.savez_compressed(out/'hh74.npz',x=x,values=np.stack(vals),case_ids=np.array([r['id'] for r in cases]))
    return {'file':'hh74.npz','sha256':sha(out/'hh74.npz'),'fields':('H_per_s','S_h','P_m_h','P_r_h','p_m_J_m3','p_r_J_m3'),'cases':cases,'source_csv_sha256':sha(p),
            'conversion':'signed full Frobenius inputs divided by sqrt(2); b is absent',
            'scope':'HH74 original 63 collisionless controls A_m=0, no independent matter sweep'}

def build_packet(rei,hh,out):
    out.mkdir(parents=True,exist_ok=False)
    index={'schema':'PHYS75_IMMUTABLE_SAVED_DATA_V1','datasets':{'long':pack_rei(rei,out),'hh74':pack_hh(hh,out)},
           'new_IVPs':0,'source_archives':{'long':'2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d',
                                        'hh74':'007b996201c770ef4b630adb7fde5355ef0ca19458046fd24f2c14c30f74566b'}}
    dump(out/'INDEX.json',index)

def analyze(packet,out):
    index=json.loads((packet/'INDEX.json').read_text());out.mkdir(parents=True,exist_ok=False)
    summary={'schema':'PHYS75_MEMORY_ANALYSIS_V1','new_IVPs':0,'benchmark_runs':0,'datasets':{}}
    for name,record in index['datasets'].items():
        p=packet/record['file']
        if sha(p)!=record['sha256']:raise ValueError('PACKET_HASH_MISMATCH:'+name)
        with np.load(p,allow_pickle=False) as z:x=z['x'];v=z['values'];ids=z['case_ids']
        H,S,Pm,Pr=[v[:,i,:] for i in range(4)]
        result=memory_budget(x,H,S,Pm,Pr);rows=[]
        oracle_max=0.
        for i,cid in enumerate(ids):
            kernel=np.exp(3*(x-x[-1]))*H[i]/H[i,-1]
            for k,P in [('matter_memory',Pm),('radiation_memory',Pr)]:
                oracle_max=max(oracle_max,abs(float(simpson(kernel*P[i],x=x))-float(result[k][i])))
            row={'case_id':str(cid),'source_lane':record['cases'][i]['lane'],
                 'initial_S_h':float(S[i,0]),'initial_P_m_h':float(Pm[i,0]),'initial_P_r_h':float(Pr[i,0]),
                 'final_S_h':float(S[i,-1]),'final_P_m_h':float(Pm[i,-1]),'final_P_r_h':float(Pr[i,-1])}
            for k,value in result.items():row[k]=bool(value[i]) if value.dtype==bool else float(value[i])
            for k in ('initial_memory','matter_memory','radiation_memory','predicted_signed_shear','observed_signed_shear','closure_defect'):
                row[k+'_F']=float(np.sqrt(2)*result[k][i])
            rows.append(row)
        write_csv(out/(name+'_memory.csv'),rows)
        summary['datasets'][name]={'cases':len(ids),'samples':int(H.size),'scope':record['scope'],
          'max_abs_closure_half':float(np.max(abs(result['closure_defect']))),
          'max_abs_closure_F':float(np.sqrt(2)*np.max(abs(result['closure_defect']))),
          'max_scaled_closure':float(np.max(result['closure_scaled_defect'])),
          'max_absolute_coarse_grid_difference':float(np.max(abs(result['total_halfgrid_difference']))),
          'independent_scipy_integral_max_abs_difference':float(oracle_max),
          'input_sha256':sha(p),'output_csv_sha256':sha(out/(name+'_memory.csv')),
          'mixed_cancellation_cases':[r for r in rows if r['case_id'].startswith('mixed_')]}
    summary['claim']='Saved-node quadrature and path attribution only, not a continuum trajectory error bound or species-removal experiment.'
    dump(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('pack');b.add_argument('--rei-root',type=Path,required=True);b.add_argument('--hh-root',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('analyze');a.add_argument('--packet',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    q=ap.parse_args()
    if q.cmd=='pack':build_packet(q.rei_root,q.hh_root,q.out)
    else:analyze(q.packet,q.out)
