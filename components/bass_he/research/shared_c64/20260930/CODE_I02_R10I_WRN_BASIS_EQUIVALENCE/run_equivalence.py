"""R10I fixed query manifest rotation-only audit. No geometry or Delta imports."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, platform, sys, traceback
from collections import defaultdict
import numpy as np
from reduced_parity import reduced_rotation_batch
from bass_he.rotation import rotation_batch
from eta_rotation import eta_rotation_batch

HERE=pathlib.Path(__file__).resolve().parent

def atomic(path, obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(str(path.parent),os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def run(out):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((HERE/'QUERY_MANIFEST.json').read_text())
    raw=json.dumps(manifest['active_queries'],separators=(',',':'),allow_nan=False).encode()
    assert hashlib.sha256(raw).hexdigest()==manifest['active_query_identity_sha256']
    assert manifest['active_query_count']==len(manifest['active_queries'])==3270
    groups=defaultdict(list)
    for i,q in enumerate(manifest['active_queries']):groups[tuple(q[:5])].append((i,q[5]))
    assert len(groups)==24
    records=[None]*len(manifest['active_queries']);stats=[]
    max_auth_step=max_clean_step=max_red_unit=max_clean_unit=max_red_stoch=max_clean_stoch=max_collapse=0.
    worst=None;worst_value=-1.
    for gi,(key,pairs) in enumerate(groups.items()):
        trajectory,cutoff,E,N,l=key
        r=np.array([float.fromhex(h) for _,h in pairs])
        cut=((l+.5)**2-(.5 if cutoff=='CPC' else 0))/3
        low,high=(64,128) if trajectory=='STRAIGHT' else (256,512)
        red_lo=reduced_rotation_batch(N,l,E,r,trajectory=trajectory,cutoff=cutoff,steps=low)
        red_hi=reduced_rotation_batch(N,l,E,r,trajectory=trajectory,cutoff=cutoff,steps=high)
        solver=rotation_batch if trajectory=='STRAIGHT' else eta_rotation_batch
        clean_lo=solver(N,l,E,r,R_cut=cut,steps=low)
        clean_hi=solver(N,l,E,r,R_cut=cut,steps=high)
        assert np.all(red_hi['entered']) and np.all(clean_hi['entered'])
        auth_step=np.max(abs(red_lo['P']-red_hi['P']),axis=(1,2))
        clean_step=np.max(abs(clean_lo['P_abs']-clean_hi['P_abs']),axis=(1,2))
        diff=red_hi['P']-clean_hi['P_abs']
        per_max=np.max(abs(diff),axis=(1,2))
        per_frob=np.sqrt(np.sum(diff*diff,axis=(1,2)))
        collapse=np.max(abs(red_hi['P_collapsed']-clean_hi['P_abs']),axis=(1,2))
        clean_unit=float(np.max(abs(clean_hi['U_z'].conj().swapaxes(-1,-2)@clean_hi['U_z']-np.eye(2*l+1))))
        clean_stoch=float(np.max(abs(clean_hi['P_abs'].sum(1)-1)))
        max_auth_step=max(max_auth_step,float(np.max(auth_step)))
        max_clean_step=max(max_clean_step,float(np.max(clean_step)))
        max_red_unit=max(max_red_unit,red_hi['unitarity_defect'])
        max_clean_unit=max(max_clean_unit,clean_unit)
        max_red_stoch=max(max_red_stoch,red_hi['stochasticity_defect'])
        max_clean_stoch=max(max_clean_stoch,clean_stoch)
        max_collapse=max(max_collapse,float(np.max(collapse)))
        for j,(original_index,hx) in enumerate(pairs):
            row,col=np.unravel_index(int(np.argmax(abs(diff[j]))),diff[j].shape)
            rec={'trajectory':trajectory,'cutoff':cutoff,'energy_keV_u':E,'N':N,'l':l,'rho_hex':hx,
                 'author_reduced_probability':red_hi['P'][j].tolist(),
                 'clean_collapsed_probability':clean_hi['P_abs'][j].tolist(),
                 'parity_reassembled_probability':red_hi['P_collapsed'][j].tolist(),
                 'max_probability_difference':float(per_max[j]),'frobenius_difference':float(per_frob[j]),
                 'worst_final_m':int(row),'worst_initial_m':int(col),
                 'author_step_difference':float(auth_step[j]),'clean_step_difference':float(clean_step[j]),
                 'parity_reassembly_difference':float(collapse[j])}
            records[original_index]=rec
            if per_max[j]>worst_value:
                worst_value=float(per_max[j]);worst=rec
        stats.append({'group':list(key),'active_queries':len(r),'author_max_low_high':float(np.max(auth_step)),
                      'clean_max_low_high':float(np.max(clean_step)),'max_basis_difference':float(np.max(per_max)),
                      'max_parity_reassembly_difference':float(np.max(collapse)),
                      'author_unitarity_defect':red_hi['unitarity_defect'],'clean_unitarity_defect':clean_unit,
                      'author_stochasticity_defect':red_hi['stochasticity_defect'],'clean_stochasticity_defect':clean_stoch})
        atomic(out/'PROGRESS.json',{'status':'RUNNING','groups_completed':gi+1,'groups_total':24,
                                    'queries_completed':sum(x['active_queries'] for x in stats),'worst_difference_so_far':worst_value})
    assert all(x is not None for x in records)
    numeric_pass=(max_auth_step<=1e-8 and max_clean_step<=1e-8 and
                  max_red_unit<=5e-13 and max_clean_unit<=5e-13 and
                  max_red_stoch<=5e-13 and max_clean_stoch<=5e-13 and max_collapse<=1e-8)
    verdict='WRN_BASIS_NUMERICALLY_EQUIVALENT' if worst_value<=1e-8 else 'WRN_BASIS_NOT_EQUIVALENT'
    summary={'schema':'bass_he.r10i.rotation_equivalence.v1','status':'COMPLETE','verdict':verdict,
             'numeric_gate':'PASS' if numeric_pass else 'FAIL','query_count':len(records),'group_count':len(groups),
             'rho_count':300,'max_probability_difference':worst_value,
             'max_author_low_high':max_auth_step,'max_clean_low_high':max_clean_step,
             'max_author_unitarity_defect':max_red_unit,'max_clean_unitarity_defect':max_clean_unit,
             'max_author_stochasticity_defect':max_red_stoch,'max_clean_stochasticity_defect':max_clean_stoch,
             'max_parity_reassembly_difference':max_collapse,'worst_query':{k:v for k,v in worst.items() if not k.endswith('_probability')},
             'groups':stats,'query_manifest_sha256':sha(HERE/'QUERY_MANIFEST.json'),
             'r10g_delta_calls':0,'python':platform.python_version(),'numpy':np.__version__}
    atomic(out/'ROTATION_RESULTS.json',{'schema':'bass_he.r10i.rotation_results.v1','records':records})
    atomic(out/'ROTATION_SUMMARY.json',summary)
    atomic(out/'PROGRESS.json',{'status':'COMPLETE','groups_completed':24,'queries_completed':len(records)})
    print(json.dumps({k:summary[k] for k in ('verdict','numeric_gate','query_count','max_probability_difference',
          'max_author_low_high','max_clean_low_high','max_author_unitarity_defect','max_clean_unitarity_defect',
          'max_parity_reassembly_difference')},indent=2))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    try:run(args.out)
    except Exception:
        atomic(pathlib.Path(args.out)/'FAILURE.json',{'status':'R10I_ROTATION_FAILED','traceback':traceback.format_exc()})
        raise
