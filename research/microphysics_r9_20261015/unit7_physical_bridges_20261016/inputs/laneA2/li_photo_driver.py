#!/usr/bin/env python3
"""Finite direct Li I photoionization response; frozen R9_UNIT7_LI_PHOTO_v1."""
import csv
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/laneA'
BV=5.392
BK=64.39
EV=1.602176634e-19
I=0.08144613055216544
FIELDS=['G_over_J_m2','W_abs_over_J_J_m2','K_primary_over_J_J_m2','Q_threshold_over_J_J_m2','X_core_over_J_J_m2']
PH1={}
PH2=[]

def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def readcsv(path):
    with path.open() as f: return list(csv.DictReader(f))

def writecsv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def stage(contract):
    manifest={}
    for category in ['immutable_inputs','prior_results','provider_inputs']:
        for name,info in contract[category].items():
            dest=ROOT/('inputs/verner' if category=='provider_inputs' else 'inputs/laneA')/name
            source=dest if dest.exists() else Path(info['path'])
            original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
            if original_hash!=info['sha256'] or source.stat().st_size!=info['bytes']:
                raise RuntimeError('immutable input identity failure: '+name)
            if source!=dest: shutil.copyfile(source,dest)
            manifest[name]={'frozen_original_path':info['path'],'original_sha256':original_hash,
                'local_path':str(dest.relative_to(ROOT)),'copied_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                'bytes':dest.stat().st_size}
    dump(ROOT/'inputs/laneA/manifest.json',manifest)
    return manifest

def provider(contract):
    global PH1,PH2
    src=(ROOT/'inputs/verner/phfit2.f').read_text()
    # Fixed-form continuation labels occupy column 6; strip them before DATA parsing.
    body='\n'.join(line[6:] for line in src.splitlines() if line and line[0] not in '*cC')
    def data(pattern):
        match=re.search(pattern+r'\s*/([^/]+)/',body,re.I)
        if not match: raise ValueError('provider DATA not found: '+pattern)
        return [float(v) for v in match.group(1).replace('\n','').split(',')]
    PH1={s:data(r'DATA\s*\(PH1\(I,\s*3,\s*3,\s*'+str(k)+r'\),I=1,6\)') for s,k in [('1s',1),('2s',2)]}
    PH2=data(r'DATA\s*\(PH2\(I,\s*3,\s*3\),I=1,7\)')
    assert PH1['1s']==contract['PH1_1s'] and PH1['2s']==contract['PH1_2s'] and PH2==contract['PH2_2s']
    l=data(r'DATA\s*\(L\(I\),I=1,7\)')
    ni=data(r'DATA\s*\(NINN\(I\),I=1,30\)')
    nt=data(r'DATA\s*\(NTOT\(I\),I=1,30\)')
    assert l[:2]==[0,0] and ni[2]==1 and nt[2]==2
    table=[list(map(float,r.split())) for r in (ROOT/'inputs/verner/table1.dat').read_text().splitlines() if r.split()[:2]==['3','3']]
    old=[list(map(float,r.split())) for r in (ROOT/'inputs/laneA/photo.dat').read_text().splitlines() if r.split()[:2]==['3','3']]
    assert len(table)==2 and len(old)==1
    assert all(r[4:]==PH1['1s' if r[2]==1 else '2s'] for r in table)
    assert old[0][2:]==[BV,BK]+PH2
    result={'PH1':PH1,'PH2_2s':PH2,'L_1s_2s':l[:2],'NINN_3':ni[2],'NTOT_3':nt[2],
        'table1_rows':table,'photo_dat_row':old[0],'independent_tables_equal':True,
        'effective_branch_rules':contract['branch_rule'],'occupancy_multiplier':1,
        'energy_domain_eV':[0,contract['source']['max_expected_Delta_eV']],
        'public_Fortran_execution':'NOT_RUN_compiler_unavailable' if shutil.which('gfortran') is None else 'COMPILER_PRESENT_NOT_YET_EXECUTED'}
    dump(OUT/'provider_reconstruction.json',result)
    return result

def ph1(e,s):
    b,e0,s0,ya,p,yw=PH1[s]; t=e/e0
    return s0*((t-1)**2+yw*yw)*t**(p/2-5.5)*(1+math.sqrt(t/ya))**(-p)

def ph2(e):
    e0,s0,ya,p,yw,y0,y1=PH2; x=e/e0-y0; v=math.hypot(x,y1)
    return s0*((x-1)**2+yw*yw)*v**(p/2-5.5)*(1+math.sqrt(v/ya))**(-p)

def sigma(e,s):
    if s=='total': return sigma(e,'1s')+sigma(e,'2s')
    if s=='3' or e<(BK if s=='1s' else BV): return 0.
    return ph1(e,s) if s=='1s' or e>=BK else ph2(e)

def decimal_reference(e,s):
    if s=='3' or e<(BK if s=='1s' else BV): return 0.
    with localcontext() as c:
        c.prec=50; d=Decimal; en=d(str(e))
        if s=='1s' or e>=BK:
            _,e0,s0,ya,p,yw=map(lambda x:d(str(x)),PH1[s]); t=en/e0
            polynomial=(t-1)**2+yw*yw
        else:
            e0,s0,ya,p,yw,y0,y1=map(lambda x:d(str(x)),PH2); x=en/e0-y0
            t=(x*x+y1*y1).sqrt(); polynomial=(x-1)**2+yw*yw
        # Independent log-form rather than the kernel's product of powers.
        answer=(s0.ln()+polynomial.ln()+(p/2-d('5.5'))*t.ln()-p*(1+(t/ya).sqrt()).ln()).exp()
        return float(answer)

def shape(y):
    if y<=0 or y>=1: return 0.
    w=y*(1-y)
    return w*(1-(4*w)**.8)+.88*4**.8*w**2.33

def source(e,delta):
    return 2*shape(e/delta)/(delta*I)

def legendre(n):
    # Newton roots of Legendre recurrence, no NumPy or previous-runtime dependency.
    points=[]
    for j in range(1,n//2+1):
        x=math.cos(math.pi*(j-.25)/(n+.5))
        for _ in range(20):
            a,b=1.,x
            for k in range(2,n+1): a,b=b,((2*k-1)*x*b-(k-1)*a)/k
            derivative=n*(x*b-a)/(x*x-1)
            step=b/derivative; x-=step
            if abs(step)<3e-16: break
        a,b=1.,x
        for k in range(2,n+1): a,b=b,((2*k-1)*x*b-(k-1)*a)/k
        derivative=n*(x*b-a)/(x*x-1)
        w=2/((1-x*x)*derivative**2)
        points.extend([(-x,w),(x,w)])
    return sorted(points)

def quad(fn,lo,hi,points):
    if hi<=lo: return 0.
    mid=(lo+hi)/2; half=(hi-lo)/2
    return half*math.fsum(w*fn(mid+half*x) for x,w in points)

def bands(delta):
    def clip(a,b):
        lo=min(a,delta); return lo,max(lo,min(b,delta))
    return {name:clip(a,b) for name,a,b in [('sub_Lyman',BV,13.6),('upper_old',13.6,BK),
        ('extension',BK,delta),('covered_total',BV,BK),('full_total',BV,delta)]}

def integrate(delta,points):
    out={}
    for band,(lo,hi) in bands(delta).items():
        edges=sorted(set([lo,hi]+[x for x in [BV,13.6,BK] if lo<x<hi]))
        for shell in ['1s','2s']:
            g=w=k=0.
            threshold=BK if shell=='1s' else BV
            for a,b in zip(edges[:-1],edges[1:]):
                g+=quad(lambda e:source(e,delta)*sigma(e,shell),a,b,points)*1e-22
                w+=quad(lambda e:source(e,delta)*sigma(e,shell)*e,a,b,points)*1e-22*EV
                k+=quad(lambda e:source(e,delta)*sigma(e,shell)*(e-threshold),a,b,points)*1e-22*EV
            out[band,shell]=[g,w,k,EV*threshold*g,EV*(BK-BV)*g if shell=='1s' else 0.]
        out[band,'total']=[sum(v) for v in zip(out[band,'1s'],out[band,'2s'])]
    return out

def independent(delta):
    from scipy.integrate import quad as scipy_quad
    accum=[0.,0.,0.]; errors=[0.,0.,0.]
    for lo,hi in [bands(delta)[b] for b in ['sub_Lyman','upper_old','extension']]:
        if hi<=lo: continue
        for index in range(3):
            def fn(e):
                ss=[sigma(e,s) for s in ['1s','2s']]
                factor=sum(ss) if index==0 else (e*sum(ss) if index==1 else (e-BK)*ss[0]+(e-BV)*ss[1])
                return source(e,delta)*factor
            value,error=scipy_quad(fn,lo,hi,epsabs=1e-12,epsrel=2e-12,limit=100)
            accum[index]+=value; errors[index]+=error
    return [accum[0]*1e-22,accum[1]*1e-22*EV,accum[2]*1e-22*EV],errors

def relative(a,b,floor): return abs(a-b)/max(abs(a),abs(b),floor)

def main():
    started=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
    contract=json.loads((ROOT/'spec/LI_PHOTO_CONTRACT.json').read_text())
    manifest=stage(contract); reconstruction=provider(contract)
    mixtures=json.loads((ROOT/'inputs/laneA/cascade_mixture.json').read_text())['mixture_moments']
    transitions=readcsv(ROOT/'inputs/laneA/transitions.csv')
    delta={}
    for species in dict.fromkeys(m['species'] for m in mixtures):
        rows=[r for r in transitions if r['species']==species and [r[k] for k in ['n_upper','l_upper','n_lower','l_lower']]==['2','1','1','0']]
        assert len(rows)==1; delta[species]=float(rows[0]['photon_eV'])
    assert len(mixtures)==32 and len(delta)==8
    raw={}; moments=[]; response=[]; convergence=[]; cross=[]; comparisons=[]
    for e in [5.391,BV,5.393,13.6,40,64.389,math.nextafter(BK,-math.inf),BK,64.391,80,max(delta.values())]:
        for s in ['1s','2s','3','total']:
            cross.append({'E_eV':e,'shell':s,'sigma_Mb':sigma(e,s),'branch':'unoccupied' if s=='3' else ('zero' if sigma(e,s)==0 else ('PH2' if e<BK and s=='2s' else 'PH1' if s!='total' else 'sum')),
                'Decimal_reference_Mb':sum(decimal_reference(e,a) for a in ['1s','2s']) if s=='total' else decimal_reference(e,s)})
    writecsv('li_photo_cross_sections.csv',cross)
    for nodes in [64,128,256]:
        points=legendre(nodes)
        cache={sp:integrate(de,points) for sp,de in delta.items()}
        for m in mixtures:
            sp=m['species']; n=m['n']; p=m['terminal_2s_probability']; de=delta[sp]
            base={'species':sp,'n':n,'quadrature_nodes':nodes,'authoritative':nodes==256}
            for (band,shell),values in cache[sp].items():
                vals=[p*v for v in values]; raw[sp,n,nodes,band,shell]=vals
                lo,hi=bands(de)[band]
                row=dict(base,band=band,shell=shell,E_lo_eV=lo,E_hi_eV=hi,**dict(zip(FIELDS,vals)))
                row['mean_absorbed_energy_eV']=vals[1]/(EV*vals[0]) if vals[0]>0 else None
                response.append(row)
            for band,(lo,hi) in {'full_source':(0,de),'extension':bands(de)['extension']}.items():
                moments.append(dict(base,band=band,Delta_eV=de,P_2s=p,photon_count=p*quad(lambda e:source(e,de),lo,hi,points),
                    energy_eV=p*quad(lambda e:e*source(e,de),lo,hi,points),saved_reservoir_eV=m['terminal_2s_energy_eV'],P_Delta_eV=p*de))
    writecsv('li_photo_response.csv',response); writecsv('li_photo_source_moments.csv',moments)
    for m in mixtures:
        sp=m['species']; n=m['n']
        for band in bands(delta[sp]):
            for shell in ['1s','2s','total']:
                a=raw[sp,n,128,band,shell]; b=raw[sp,n,256,band,shell]
                for j,field in enumerate(FIELDS):
                    convergence.append({'species':sp,'n':n,'band':band,'shell':shell,'field':field,'value_64':raw[sp,n,64,band,shell][j],
                        'value_128':a[j],'value_256':b[j],'relative_128_256':relative(a[j],b[j],1e-35 if j==0 else 1e-53)})
    writecsv('li_photo_quadrature.csv',convergence)
    for old in readcsv(ROOT/'inputs/laneA/twophoton_LiI_response.csv'):
        if old['authoritative']!='True': continue
        sp=old['species']; n=int(old['n']); band=old['band']; new=raw[sp,n,256,band,'total']
        for field,index in [('Gamma_over_J_m2',0),('H_over_J_J_m2',2),('Abs_over_J_J_m2',1)]:
            value=float(old[field]); comparisons.append({'species':sp,'n':n,'band':band,'legacy_field':field,'legacy':value,'new':new[index],
                'relative_difference':relative(value,new[index],1e-35 if index==0 else 1e-53)})
    writecsv('li_photo_comparison.csv',comparisons)
    independent_results=[]
    for sp,de in delta.items():
        values,errors=independent(de); target=raw[sp,3,256,'full_total','total']; p=next(m['terminal_2s_probability'] for m in mixtures if m['species']==sp and m['n']==3)
        independent_results.append({'species':sp,'P_reference':1.,'G_W_K':values,'raw_quad_error_estimates_Mb_eV_units':errors,
            'scaled_mixture_checks':[{'n':m['n'],'relative_G_W_K':[relative(v*m['terminal_2s_probability'],raw[sp,m['n'],256,'full_total','total'][j],1e-35 if j==0 else 1e-53) for j,v in enumerate(values)]} for m in mixtures if m['species']==sp]})
    dump(OUT/'li_photo_independent.json',{'route':'scipy.integrate.quad QUADPACK adaptive Gauss-Kronrod; split disjoint bands; once per species P=1','species':independent_results})
    decompositions=[]
    for m in mixtures:
        sp=m['species']; n=m['n']; full=raw[sp,n,256,'full_total','total']; ext=raw[sp,n,256,'extension','total']; old=raw[sp,n,256,'covered_total','total']
        decompositions.append({'species':sp,'n':n,'Delta_eV':delta[sp],'extension_response_fractions':dict(zip(FIELDS,[ext[j]/full[j] if full[j]>0 else None for j in range(5)])),
            'fractional_increase_over_covered':dict(zip(FIELDS,[ext[j]/old[j] if old[j]>0 else None for j in range(5)])),
            '1s_shell_fractions':dict(zip(FIELDS,[raw[sp,n,256,'full_total','1s'][j]/full[j] if full[j]>0 else None for j in range(5)])),
            '2s_shell_fractions':dict(zip(FIELDS,[raw[sp,n,256,'full_total','2s'][j]/full[j] if full[j]>0 else None for j in range(5)])),
            'legacy_valence_subtraction_J_m2':full[1]-EV*BV*full[0],'primary_K_J_m2':full[2],'X_core_J_m2':full[4]})
    summary={'contract_id':contract['contract_id'],'input_manifest':manifest,'mixtures':32,'species_Delta_eV':delta,
        'edge':{'left_2s_Mb':ph2(BK),'right_2s_Mb':ph1(BK,'2s'),'right_1s_Mb':ph1(BK,'1s'),
            'total_step_ratio':sigma(BK,'total')/ph2(BK),'outer_fractional_change':ph1(BK,'2s')/ph2(BK)-1,'exact_edge_branch':'PH1 both shells',
            'inner_threshold_eV':BK,'1s_event_valence_subtraction_excess_eV':BK-BV},'decompositions':decompositions,
        'interpretation':'smooth direct absorption and primary photoelectron kinetic energy; shell threshold bookkeeping; no relaxation or heat/charge yields',
        'numerical_accuracy_is_not_physical_percent_accuracy':True,'public_Fortran_execution':reconstruction['public_Fortran_execution']}
    dump(OUT/'li_photo_summary.json',summary)
    sys.path.insert(0,str(ROOT/'tests'))
    sys.modules['li_photo_driver']=sys.modules[__name__]
    from test_li_photo_validation import validate
    tests=validate(raw,moments,cross,convergence,comparisons,independent_results,mixtures,delta)
    dump(OUT/'li_photo_tests.json',tests)
    elapsed=time.perf_counter()-started
    evidence={'requested_executor_model':'gpt-6.1-sol','requested_executor_reasoning':'high','observed_runtime_model':'UNKNOWN','requested_theory_authority':'Astra','observed_theory_authority_model':'UNKNOWN',
        'command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python code/li_photo_driver.py','Python':sys.version,'platform':platform.platform(),
        'thread_environment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},'wall_seconds':elapsed,
        'numerical_run_seconds_limit':30,'per_command_seconds_limit':30,'finite_ladder':[64,128,256],'public_Fortran_execution':reconstruction['public_Fortran_execution'],
        'compiler_installation':'NOT_ATTEMPTED','tests':tests,'status':'PASS_PENDING_INDEPENDENT_AUTHORITY_REVIEW' if tests['passed'] and elapsed<=30 else 'FAIL_RETURN_TO_AUTHORITY',
        'cost_and_runtime_model_telemetry':'UNKNOWN; unavailable','all_raw_results_preserved':True,'contract_sha256':hashlib.sha256((ROOT/'spec/LI_PHOTO_CONTRACT.json').read_bytes()).hexdigest()}
    dump(ROOT/'evidence/LI_PHOTO_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'wall_seconds':elapsed,'tests':tests,'edge':summary['edge']}))
    return 0 if tests['passed'] and elapsed<=30 else 1

if __name__=='__main__': sys.exit(main())
