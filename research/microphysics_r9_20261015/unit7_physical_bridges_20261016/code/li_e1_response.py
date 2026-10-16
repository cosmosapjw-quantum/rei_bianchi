#!/usr/bin/env python3
"""A2 finite E1 sums plus authoritative saved A1 continuum; no quadrature."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time
import li_photo_driver as a1

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/laneA2'
F=a1.FIELDS

def dump(path,obj): path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def csvout(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def boolean(value):
    if value=='True':return True
    if value=='False':return False
    raise ValueError('invalid explicit CSV Boolean '+repr(value))

def belongs(e,band,cap):
    if band=='sub_Lyman':return a1.BV<=e<13.6
    if band=='upper_old':return 13.6<=e<a1.BK
    if band=='extension':return a1.BK<=e<=cap
    if band=='covered_total':return a1.BV<=e<a1.BK
    return a1.BV<=e<=cap

def main():
    started=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    contract=json.loads((ROOT/'spec/LI_E1_RESPONSE_ADDENDUM.json').read_text())
    manifest={};paths={}
    for name,info in contract['inputs'].items():
        local=ROOT/'inputs/laneA2'/Path(info['path']).name
        source=local if local.exists() else Path(info['path'])
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!=info['sha256'] or source.stat().st_size!=info['bytes']:raise RuntimeError('immutable input identity failure '+name)
        if source!=local:shutil.copyfile(source,local)
        manifest[name]={'original_path':info['path'],'original_sha256':digest,'copied_path':str(local.relative_to(ROOT)),
            'copied_sha256':hashlib.sha256(local.read_bytes()).hexdigest(),'bytes':local.stat().st_size}
        paths[name]=local
    dump(ROOT/'inputs/laneA2/manifest.json',manifest)
    parent=json.loads(paths['A1_contract'].read_text())
    reconstruction=json.loads((ROOT/'results/laneA/provider_reconstruction.json').read_text())
    assert reconstruction['PH1']=={'1s':parent['PH1_1s'],'2s':parent['PH1_2s']}
    assert reconstruction['PH2_2s']==parent['PH2_2s']
    a1.PH1=reconstruction['PH1'];a1.PH2=reconstruction['PH2_2s']
    lines=a1.readcsv(paths['E1_lines']);mixtures=json.loads(paths['mixtures'].read_text())['mixture_moments']
    mixture={(m['species'],m['n']):m for m in mixtures}
    linegroups={key:[] for key in mixture}
    for r in lines:
        e=float(r['photon_eV']);p=float(r['photon_count']);energy=float(r['energy_eV'])
        assert math.isfinite(e) and e>0 and math.isfinite(p) and p>=0 and math.isfinite(energy)
        linegroups[r['species'],int(r['n'])].append((e,p,energy))
    assert len(lines)==contract['expected']['E1_rows']
    emax=max(e for group in linegroups.values() for e,_,_ in group)
    assert emax==contract['expected']['E1_max_photon_eV']
    continuum={}
    for r in a1.readcsv(paths['A1_response']):
        authoritative=boolean(r['authoritative'])
        if int(r['quadrature_nodes'])!=256 or not authoritative:continue
        key=(r['species'],int(r['n']),r['band'],r['shell'])
        assert key not in continuum;continuum[key]=r
    moment={}
    for r in a1.readcsv(paths['A1_source_moments']):
        authoritative=boolean(r['authoritative'])
        if int(r['quadrature_nodes'])==256 and authoritative and r['band']=='full_source':
            key=r['species'],int(r['n']);assert key not in moment;moment[key]=r
    assert set(moment)==set(mixture)==set(linegroups)
    expected={(s,n,b,sh) for s,n in mixture for b in contract['bands'] for sh in contract['shells']}
    assert set(continuum)==expected
    raw={};rows=[];source_rows=[];fractions=[]
    for key,m in mixture.items():
        sp,n=key;group=linegroups[key];cm=moment[key];delta=float(cm['Delta_eV'])
        maxline=max(e for e,_,_ in group);cap=max(delta,maxline)
        count=math.fsum(p for _,p,_ in group);energy=math.fsum(e*p for e,p,_ in group)
        contN=float(cm['photon_count']);contU=float(cm['energy_eV'])
        source_rows.append({'species':sp,'n':n,'E1_rows':len(group),'E1_source_cap_eV':maxline,'continuum_source_cap_eV':delta,'source_cap_eV':cap,
            'E1_photon_count':count,'E1_energy_eV':energy,'continuum_photon_count':cm['photon_count'],'continuum_energy_eV':cm['energy_eV'],
            'combined_photon_count':count+contN,'combined_energy_eV':energy+contU,'saved_E1_photon_count':m['E1_photon_count'],
            'saved_E1_energy_eV':m['E1_energy_eV'],'saved_initial_excitation_eV':m['initial_excitation_eV'],
            'photon_closure_residual':count+contN-m['E1_photon_count']-2*m['terminal_2s_probability'],
            'energy_closure_residual_eV':energy+contU-m['initial_excitation_eV']})
        evaluated=[(e,p,a1.sigma(e,'1s')*1e-22,a1.sigma(e,'2s')*1e-22) for e,p,_ in group]
        for band in contract['bands']:
            for sh,index in [('1s',2),('2s',3)]:
                b=a1.BK if sh=='1s' else a1.BV
                selected=[r for r in evaluated if belongs(r[0],band,cap)]
                g=math.fsum(r[1]*r[index] for r in selected)
                w=a1.EV*math.fsum(r[1]*r[index]*r[0] for r in selected)
                k=a1.EV*math.fsum(r[1]*r[index]*(r[0]-b) for r in selected if r[index]>0)
                raw[sp,n,band,sh,'E1']=[g,w,k,a1.EV*b*g,a1.EV*(a1.BK-a1.BV)*g if sh=='1s' else 0.]
            raw[sp,n,band,'total','E1']=[math.fsum(v) for v in zip(raw[sp,n,band,'1s','E1'],raw[sp,n,band,'2s','E1'])]
            for sh in contract['shells']:
                old=continuum[sp,n,band,sh]
                raw[sp,n,band,sh,'continuum']=[float(old[f]) for f in F]
                raw[sp,n,band,sh,'combined']=[math.fsum(v) for v in zip(raw[sp,n,band,sh,'E1'],raw[sp,n,band,sh,'continuum'])]
                for component in contract['components']:
                    values=raw[sp,n,band,sh,component];g,w=values[:2]
                    exported={f:old[f] if component=='continuum' else values[j] for j,f in enumerate(F)}
                    rows.append(dict(species=sp,n=n,band=band,shell=sh,component=component,source_cap_eV=delta if component=='continuum' else maxline if component=='E1' else cap,
                        E1_source_cap_eV=maxline,continuum_source_cap_eV=delta,**exported,mean_absorbed_energy_eV=w/(a1.EV*g) if g>0 else None))
        total=raw[sp,n,'full_total','total','combined']
        fractions.append({'species':sp,'n':n,'source_cap_eV':cap,
            'continuum_fractions_G_W_K':dict(zip(F[:3],[raw[sp,n,'full_total','total','continuum'][j]/total[j] if total[j]>0 else None for j in range(3)])),
            'E1_fractions_G_W_K':dict(zip(F[:3],[raw[sp,n,'full_total','total','E1'][j]/total[j] if total[j]>0 else None for j in range(3)])),
            '1s_fractions_G_W_K':dict(zip(F[:3],[raw[sp,n,'full_total','1s','combined'][j]/total[j] if total[j]>0 else None for j in range(3)]))})
    assert len(rows)==1440
    csvout('li_completed_source_response.csv',rows);csvout('li_completed_source_moments.csv',source_rows)
    point=[{'E_eV':emax,'shell':s,'kernel_Mb':a1.sigma(emax,s),'Decimal_log_reference_Mb':a1.decimal_reference(emax,s)} for s in ['1s','2s']]
    summary={'contract_id':contract['contract_id'],'input_manifest':manifest,'mixtures':32,'line_rows':len(lines),'response_rows':len(rows),
        'maximum_E1_photon_eV':emax,'new_range_checks':point,'fractions':fractions,'A1_rerun':False,'new_quadrature':False,
        'parent_A1_status':json.loads((ROOT/'evidence/LI_PHOTO_EXECUTION.json').read_text())['status'],
        'claim':'completed E1+two-photon smooth direct absorption, primary kinetic energy and shell threshold bookkeeping under unit hypothetical illumination',
        'not_inferred':['actual deposited heat','Auger or fluorescence yield','final charge fractions','transport','physical H(t)','external NCP result']}
    dump(OUT/'li_completed_source_summary.json',summary)
    sys.path.insert(0,str(ROOT/'tests'))
    from test_li_e1_response import validate
    tests=validate(raw,source_rows,linegroups,mixture,point,rows,continuum,contract)
    dump(OUT/'li_e1_tests.json',tests)
    elapsed=time.perf_counter()-started
    evidence={'requested_executor_model':'gpt-6.1-sol','requested_executor_reasoning':'high','observed_runtime_model':'UNKNOWN','requested_authority':'Astra','observed_authority_model':'UNKNOWN',
        'contract_id':contract['contract_id'],'command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 5s python code/li_e1_response.py > results/laneA2/li_e1_run.log 2>&1',
        'wall_seconds':elapsed,'extra_numerical_seconds_limit':5,'threads_max':1,'thread_environment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
        'finite_sum_passes':1,'A1_quadrature_reruns':0,'A1_prior_authorized_TEST_PLUMBING_repairs':1,'A2_repairs':0,'Python':sys.version,'platform':platform.platform(),
        'tests':tests,'status':'PASS_PENDING_INDEPENDENT_AUTHORITY_REVIEW' if tests['passed'] and elapsed<=5 else 'FAIL_RETURN_TO_AUTHORITY','parent_A1_status':summary['parent_A1_status'],
        'cost_and_runtime_model_telemetry':'UNKNOWN; unavailable','contract_sha256':hashlib.sha256((ROOT/'spec/LI_E1_RESPONSE_ADDENDUM.json').read_bytes()).hexdigest()}
    dump(ROOT/'evidence/LI_E1_RESPONSE_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'wall_seconds':elapsed,'tests':tests,'new_range_checks':point,'LiIII_fractions':[r for r in fractions if r['species']=='LiIII_infinite_mass']}))
    return 0 if tests['passed'] and elapsed<=5 else 1

if __name__=='__main__':sys.exit(main())
