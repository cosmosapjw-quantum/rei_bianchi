#!/usr/bin/env python3
"""Frozen data-only D8 sample-bracket analysis. Never calls or imports an ODE solver."""
import argparse, hashlib, json, math, pathlib, sys, tarfile
import numpy as np
ARCHIVE_SHA256="7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251"
ROOT="repo_payload/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021"
IDS={"a":"d58d4df366eadd417f7fbbd20b5906f51265660fb6bff81dec830d4bf16965e8","b":"6a9c9e40b8da9297509128b11f9ae5714c554a3e7df978f3a9268facf1749825","c":"1c39be4e6a5b7a7862d97efda76ea24b5b88a07db2696ffe76fe4b6cbf9c2e91","d":"d98e5a31e6765c37b80a1ffaf007ff83042482a1b0a6be3dbe67fbc86d56a272"}
EXPECTED={"a":{"Sigma_F_i":0.003,"P_m_i":-0.0003,"P_r_i":-0.001},"b":{"Sigma_F_i":0.003,"P_m_i":-0.0001,"P_r_i":-0.001},"c":{"Sigma_F_i":0.003,"Pi_F_signed_i":-0.001},"d":{"Sigma_F_i":0.003,"P_m_i":0.0001,"P_r_i":-0.001}}
B2_MANIFEST=ROOT+"/results/MANIFEST.json"; Z2_MANIFEST=ROOT+"/z2_extension/results/MANIFEST.json"
def sha(b): return hashlib.sha256(b).hexdigest()
def read_member(tf,n):
    m=tf.getmember(n)
    if not m.isfile(): raise RuntimeError("not a regular archive member: "+n)
    return tf.extractfile(m).read()
def dump(path,obj): path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--archive',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    archive=pathlib.Path(args.archive); out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    ah=sha(archive.read_bytes())
    if ah!=ARCHIVE_SHA256: raise RuntimeError("archive SHA mismatch: "+ah)
    extracted=out/'extracted'; case_dir=extracted/'cases'; case_dir.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive,'r:gz') as tf:
        b2_bytes=read_member(tf,B2_MANIFEST); z2_bytes=read_member(tf,Z2_MANIFEST)
        b2=json.loads(b2_bytes); z2=json.loads(z2_bytes)
        b2e={x['id']:x for x in b2['cases']}; z2e={x['id']:x for x in z2['cases']}
        if (b2.get('nominal_cases'),b2.get('guard_cases'))!=(91,3): raise RuntimeError('historical B2 91+3 manifest mismatch')
        if IDS['c'] not in b2e or 'P_m_i' in b2e[IDS['c']]['config']: raise RuntimeError('case c lacks requested historical zero-matter manifest identity')
        if b2e[IDS['c']]['config']!=z2e.get(IDS['c'],{}).get('config'): raise RuntimeError('historical and extension case c configs differ')
        results=[]
        for label,cid in IDS.items():
            entry=z2e.get(cid)
            if not entry or entry.get('phase')!='b2' or not isinstance(entry.get('config'),dict): raise RuntimeError(f'{label}: missing B2 extension manifest binding')
            rel=entry.get('prefix_relative'); parts=pathlib.PurePosixPath(rel or '')
            if not rel or parts.is_absolute() or '..' in parts.parts: raise RuntimeError(f'{label}: invalid prefix path')
            prefix=ROOT+'/'+rel
            for file,key in [('INPUT.json','prefix_input_sha256'),('raw.npz','prefix_raw_sha256'),('RESULT.json','prefix_result_sha256')]:
                if sha(read_member(tf,prefix+'/'+file))!=entry.get(key): raise RuntimeError(f'{label}: source binding mismatch {file}')
            case_prefix=ROOT+'/z2_extension/results/cases/'+cid+'/'
            members=[m for m in tf.getmembers() if m.isfile() and m.name.startswith(case_prefix)]
            present={m.name[len(case_prefix):] for m in members}; required={'INPUT.json','ATTEMPT.json','RESULT.json','raw.npz'}
            if not required<=present: raise RuntimeError(f'{label}: missing selected case files {sorted(required-present)}')
            dest=case_dir/cid; dest.mkdir(parents=True,exist_ok=True)
            for m in members:
                p=dest/m.name[len(case_prefix):]; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(tf.extractfile(m).read())
            inp=json.loads((dest/'INPUT.json').read_text()); attempt=json.loads((dest/'ATTEMPT.json').read_text()); result=json.loads((dest/'RESULT.json').read_text()); config=inp.get('config')
            if any(d.get('id')!=cid for d in [inp,attempt,result]): raise RuntimeError(f'{label}: case IDs disagree')
            if config!=entry['config'] or result.get('config')!=config: raise RuntimeError(f'{label}: manifest/input/result config mismatch')
            for k,v in EXPECTED[label].items():
                if config.get(k)!=v: raise RuntimeError(f'{label}: expected {k}={v!r}, got {config.get(k)!r}')
            if label=='c' and 'P_m_i' in config: raise RuntimeError('case c extension config unexpectedly has P_m_i')
            if result.get('status')!='COMPLETED' or result.get('exit')!=0 or attempt.get('status')!='LAUNCHED': raise RuntimeError(f'{label}: result/attempt state mismatch')
            raw_path=dest/'raw.npz'; rb=raw_path.read_bytes(); rh=sha(rb)
            if result.get('raw_sha256')!=rh or result.get('raw_bytes')!=len(rb): raise RuntimeError(f'{label}: result/raw byte binding mismatch')
            with np.load(raw_path,allow_pickle=False) as nz: raw={k:np.array(nz[k]) for k in nz.files}
            if not {'s','H','a'}<=raw.keys(): raise RuntimeError(f'{label}: missing stored s,H,a')
            if any(not np.issubdtype(v.dtype,np.number) or not np.isfinite(v).all() for v in raw.values()): raise RuntimeError(f'{label}: nonfinite/non-numeric NPZ value')
            if any((v.ndim == 0) or ((v.shape[-1] if v.ndim > 1 else v.shape[0]) != 153) for v in raw.values()): raise RuntimeError(f'{label}: raw arrays lack a 153-sample trailing axis')
            if np.any(raw['a']<=0) or np.any(raw['H']<=0): raise RuntimeError(f'{label}: nonpositive a or H')
            z=1.0/raw['a']-1.0
            if not np.all(np.diff(z)<0): raise RuntimeError(f'{label}: redshift not strictly descending')
            if not math.isclose(float(z[0]),20.,rel_tol=0,abs_tol=2e-12) or not math.isclose(float(z[-1]),2.,rel_tol=0,abs_tol=2e-12): raise RuntimeError(f'{label}: full stored redshift endpoints are not z=20 to z=2')
            z4_candidates=np.flatnonzero(np.isclose(z,4.,rtol=0,atol=2e-12))
            if len(z4_candidates)!=1: raise RuntimeError(f'{label}: expected exactly one stored z=4 sample')
            z4_index=int(z4_candidates[0])
            sf=np.sqrt(6.)*raw['s']/raw['H']
            if not np.isfinite(sf).all() or not(sf[z4_index]>0 and sf[-1]<0): raise RuntimeError(f'{label}: signed S_F invalid or z4/z2 endpoint signs mismatch')
            brackets=[]
            for i in range(z4_index,152):
                if sf[i]*sf[i+1]<0: brackets.append({'index_pair':[i,i+1],'redshift_descending':[float(z[i]),float(z[i+1])],'S_F_signed':[float(sf[i]),float(sf[i+1])],'signs':['positive' if sf[i]>0 else 'negative','positive' if sf[i+1]>0 else 'negative']})
            if not brackets: raise RuntimeError(f'{label}: no strict adjacent sample sign-change bracket')
            results.append({'case_label':label,'case_id':cid,'manifest':'historical_B2_94_and_z2_extension' if label=='c' else 'z2_extension','config':config,'raw_path_in_archive':case_prefix+'raw.npz','raw_sha256':rh,'raw_bytes':len(rb),'stored_sample_count':153,'redshift_definition':'z=1/a-1','signed_shear_definition':'S_F=sqrt(6)*s/H','redshift_endpoints':[float(z[0]),float(z[-1])],'z4_sample_index':z4_index,'S_F_at_z4':float(sf[z4_index]),'S_F_at_z2':float(sf[-1]),'strict_adjacent_sign_change_brackets':brackets,'historical_serialization_failure_preserved':(dest/'RESULT.serialization_failure.json').exists(),'result_status_exit':[result.get('status'),result.get('exit')],'attempt_status':attempt.get('status'),'solver_metadata_nfev':result.get('nfev','NOT_RECORDED')})
        result={'task':'D8_LATE_SIGN_CROSSING_SAMPLE_BRACKETS','status':'PASS_DATA_ONLY_SAMPLE_BRACKETS','archive_sha256':ah,'historical_b2_manifest':{'nominal_cases':91,'guard_cases':3,'total_cases':94,'case_c_id':IDS['c'],'case_c_has_no_P_m_i':True},'ode_calls':0,'interpolation_performed':False,'continuous_zero_crossing_time_claimed':False,'cases':results,'limitations':['Brackets identify adjacent stored samples only, restricted to z=4 through z=2.','No interpolated root or continuous-time crossing is inferred.','The preserved serialization failure and missing solver metadata remain historical record limitations.']}
        dump(out/'D8_RESULT.json',result)
        dump(out/'B2_MANIFEST_IDENTITY.json',{'sha256':sha(b2_bytes),'case_c_entry':b2e[IDS['c']]})
        dump(out/'Z2_MANIFEST_IDENTITY.json',{'sha256':sha(z2_bytes),'selected_entries':[z2e[cid] for cid in IDS.values()]})
    print(json.dumps({'status':result['status'],'cases':[{'id':c['case_id'],'raw_sha256':c['raw_sha256'],'brackets':len(c['strict_adjacent_sign_change_brackets'])} for c in results],'ode_calls':0},sort_keys=True))
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc: print(f'HOLD: {type(exc).__name__}: {exc}',file=sys.stderr); raise SystemExit(2)
