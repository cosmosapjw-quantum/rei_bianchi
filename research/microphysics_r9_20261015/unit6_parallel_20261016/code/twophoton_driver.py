#!/usr/bin/env python3
"""Bounded isolated 2s completion of the immutable 32 E1 mixtures."""
import csv
import ctypes as ct
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/laneB'
INPUT = ROOT / 'inputs/laneB'
CONTRACT = ROOT / 'spec/TWOPHOTON_CONTRACT.json'
EV_J = 1.602176634e-19

def read_csv(path):
    with Path(path).open() as f:
        return list(csv.DictReader(f))

def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def load_kernel():
    lib = ct.CDLL(str(OUT / 'twophoton_kernel.so'))
    for name, args in [('tp_normalizer', []), ('tp_f', [ct.c_double]),
                       ('tp_rate', [ct.c_double, ct.c_double, ct.c_int]),
                       ('tp_sigma', [ct.c_double]),
                       ('tp_integrate', [ct.c_double]*4+[ct.c_int]*2)]:
        fn = getattr(lib, name); fn.argtypes=args; fn.restype=ct.c_double
    lib.tp_reservoir.argtypes=[ct.c_double]*3+[ct.POINTER(ct.c_double)]*2
    lib.tp_reservoir.restype=None
    return lib

def build():
    cmd=['cc','-std=c99','-O2','-Wall','-Wextra','-pedantic','-fPIC','-shared',
         str(ROOT/'code/twophoton_kernel.c'),'-lm','-o',str(OUT/'twophoton_kernel.so')]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
    (OUT/'build.log').write_text(' '.join(cmd)+'\n'+p.stdout+p.stderr)
    p.check_returncode()
    return cmd

def stage_inputs(contract):
    manifest={}
    for key, info in contract['inputs'].items():
        dest=INPUT/Path(info['path']).name
        source=dest if dest.exists() else Path(info['path'])
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!=info['sha256']:
            raise RuntimeError(f'BYTE_IDENTITY_MISMATCH immutable {key}: {digest}')
        if source!=dest: shutil.copyfile(source,dest)
        manifest[key]={'file':str(dest.relative_to(ROOT)), 'sha256':digest,
                       'frozen_source':info['path'], 'bytes':dest.stat().st_size}
    (INPUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return {k:ROOT/v['file'] for k,v in manifest.items()},manifest

def main():
    started=time.perf_counter()
    OUT.mkdir(parents=True,exist_ok=True); INPUT.mkdir(parents=True,exist_ok=True)
    contract=json.loads(CONTRACT.read_text()); paths,manifest=stage_inputs(contract)
    build_cmd=build(); kernel=load_kernel()
    transitions=read_csv(paths['transitions']); cascade=read_csv(paths['cascade'])
    yields=read_csv(paths['line_yields'])
    mixtures=json.loads(paths['mixtures'].read_text())['mixture_moments']
    assert len(mixtures)==32
    assert {(r['species'],r['n']) for r in mixtures}=={
        (s,n) for s in contract['species'] for n in contract['n_values']}
    photo_rows=[line.split() for line in paths['photo'].read_text().splitlines()
                if len(line.split())==11 and line.split()[:2]==['3','3']]
    expected=[3,3,5.392,64.39,3.107,62.45,15.01,4.895,0,0,0]
    assert len(photo_rows)==1 and list(map(float,photo_rows[0]))==expected
    anchor={}
    for s in contract['species']:
        rows=[r for r in transitions if r['species']==s and
              [r['n_upper'],r['l_upper'],r['n_lower'],r['l_lower']]==['2','1','1','0']]
        assert len(rows)==1; anchor[s]=rows[0]
    dh=float(anchor['H_infinite_mass']['photon_eV'])
    species=[]
    for s in contract['species']:
        delta=float(anchor[s]['photon_eV']); z=int(anchor[s]['Z'])
        a=kernel.tp_rate(delta,dh,z)
        species.append(dict(species=s,Z=z,Delta_eV=delta,r_mu=delta/(z*z*dh),
                            A_s_inverse=a,tau_s=1/a))
    byspecies={s['species']:s for s in species}
    state={(r['species'],int(r['n']),int(r['l'])):r for r in cascade}
    line_energy={(r['species'],int(r['n_upper']),int(r['l_upper']),
                  int(r['n_lower']),int(r['l_lower'])):float(r['photon_eV']) for r in transitions}
    continuum=[]; bands=[]; responses=[]; moments=[]; times=[]; e1_lines=[]
    quadrature=[]
    for nodes in contract['numerics']['nodes']:
        total=kernel.tp_integrate(0,1,1,.5,0,nodes)
        mean=kernel.tp_integrate(0,1,1,.5,1,nodes)
        quadrature.append(dict(nodes=nodes,f_normalization=total,f_mean_y=mean))
        for row in mixtures:
            s=row['species']; n=row['n']; sp=byspecies[s]
            delta=sp['Delta_eV']; p=row['terminal_2s_probability']
            base=dict(species=s,n=n,quadrature_nodes=nodes,authoritative=nodes==256)
            def integral(lo,hi,kind):
                lo=max(0,min(delta,lo)); hi=max(0,min(delta,hi))
                return kernel.tp_integrate(lo,hi,delta,p,kind,nodes)
            edges=sorted(set([delta*j/128 for j in range(129)]+
                             [e for e in [5.392,13.6,64.39] if 0<e<delta]))
            count=energy=0
            for lo,hi in zip(edges[:-1],edges[1:]):
                nb=integral(lo,hi,0); ub=integral(lo,hi,1)
                continuum.append(dict(**base,E_lo_eV=lo,E_hi_eV=hi,photon_count=nb,energy_eV=ub))
                count+=nb; energy+=ub
            for name,lo,hi in [('below_Li',0,5.392),('sub_Lyman',5.392,13.6),
                               ('ionizing_covered',13.6,64.39),('photo_uncovered',64.39,delta)]:
                bands.append(dict(**base,band=name,E_lo_eV=min(lo,delta),
                    E_hi_eV=max(min(lo,delta),min(hi,delta)),
                    photon_count=integral(lo,hi,0),energy_eV=integral(lo,hi,1)))
            for name,hi in [('sub_Lyman',13.6),('covered_total',64.39)]:
                responses.append(dict(**base,band=name,E_lo_eV=5.392,E_hi_eV=min(hi,delta),
                    Gamma_over_J_m2=integral(5.392,hi,2),
                    H_over_J_J_m2=integral(5.392,hi,3),
                    Abs_over_J_J_m2=integral(5.392,hi,4)))
            if nodes!=256: continue
            pc=sum((2*l+1)/n**2*float(state[s,n,l]['P_terminal_2s']) for l in range(n))
            moments.append(dict(species=s,n=n,Delta_eV=delta,A_s_inverse=sp['A_s_inverse'],
                tau_s=sp['tau_s'],P_2s_saved=p,P_2s_cascade=pc,P_crosscheck_residual=p-pc,
                E1_photon_count=row['E1_photon_count'],E1_energy_eV=row['E1_energy_eV'],
                initial_excitation_eV=row['initial_excitation_eV'],
                reservoir_energy_eV=row['terminal_2s_energy_eV'],
                reservoir_model_energy_eV=p*delta,N2_infinity=count,U2_infinity_eV=energy,
                N_total_infinity=row['E1_photon_count']+count,
                energy_closure_eV=row['E1_energy_eV']+energy-row['initial_excitation_eV']))
            for x in [0,.1,1,10,None]:
                if x is None: r=0.; d=p; elapsed=None
                else:
                    rr=ct.c_double(); dd=ct.c_double(); elapsed=x/sp['A_s_inverse']
                    kernel.tp_reservoir(p,sp['A_s_inverse'],elapsed,ct.byref(rr),ct.byref(dd))
                    r=rr.value; d=dd.value
                times.append(dict(species=s,n=n,x=x,asymptotic=x is None,elapsed_seconds=elapsed,
                    remaining_2s_probability=r,decayed_probability=d,N2=2*d,U2_eV=delta*d,
                    remaining_energy_eV=delta*r,ground_probability=row['terminal_1s_probability']+d,
                    N_total=row['E1_photon_count']+2*d,
                    instantaneous_photon_rate_s_inverse=2*sp['A_s_inverse']*r,
                    instantaneous_energy_rate_eV_s=delta*sp['A_s_inverse']*r,
                    energy_closure_eV=row['E1_energy_eV']+delta*(d+r)-row['initial_excitation_eV']))
            weighted={}
            for yl in yields:
                if int(yl['initial_n'])!=n: continue
                l=int(yl['initial_l']); key=tuple(int(yl[k]) for k in ['upper_n','upper_l','lower_n','lower_l'])
                weighted[key]=weighted.get(key,0)+(2*l+1)/n**2*float(yl['mean_photons_per_initial_atom'])
            for key,number in sorted(weighted.items()):
                e=line_energy[(s,)+key]
                e1_lines.append(dict(species=s,n=n,upper_n=key[0],upper_l=key[1],lower_n=key[2],
                    lower_l=key[3],photon_eV=e,photon_count=number,energy_eV=e*number))
    for name,rows in [('twophoton_species.csv',species),('twophoton_moments.csv',moments),
                      ('twophoton_continuum.csv',continuum),('twophoton_bands.csv',bands),
                      ('twophoton_LiI_response.csv',responses),('twophoton_time.csv',times),
                      ('twophoton_E1_lines.csv',e1_lines),('twophoton_quadrature.csv',quadrature)]:
        write_csv(name,rows)
    summary=dict(contract_id=contract['contract_id'],input_manifest=manifest,mixtures=32,species=species,
        beta_normalizer_C=kernel.tp_normalizer(),quadrature=quadrature,
        continuum='asymptotic photons and eV per injected precursor; existing E1 delta lines exported separately',
        photo_above_64_39_eV='unknown cross section; retained source moments in photo_uncovered band',
        photo_normalization=contract['photo']['normalization'],time_origin=contract['time']['origin'],
        mass_policy=contract['rate']['mass_policy'],fit_accuracy=contract['shape']['reported_literature_accuracy'],
        numerical_accuracy='separate numerical tolerances defined in frozen contract; no physical precision certification',
        excluded=contract['excluded'],elapsed_seconds=time.perf_counter()-started)
    (OUT/'twophoton_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    execution=dict(requested_model='gpt-6.1-sol',observed_runtime_model='UNKNOWN',threads_max=1,
        thread_environment={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
        Python=sys.version,platform=platform.platform(),compiler=subprocess.run(['cc','--version'],capture_output=True,text=True,timeout=5).stdout,
        build_command=build_cmd,wall_seconds=time.perf_counter()-started,
        numerical_run_seconds_limit=30,per_command_seconds_limit=30,
        token_cost='UNKNOWN; no runtime usage/cost telemetry exposed',status='EXECUTED_PENDING_TEST_AND_INDEPENDENT_REVIEW')
    (OUT/'TWOPHOTON_EXECUTION.json').write_text(json.dumps(execution,indent=2)+'\n')
    print(json.dumps(dict(mixtures=32,species=len(species),continuum_rows=len(continuum),
                         wall_seconds=execution['wall_seconds'],status=execution['status'])))

if __name__=='__main__': main()
