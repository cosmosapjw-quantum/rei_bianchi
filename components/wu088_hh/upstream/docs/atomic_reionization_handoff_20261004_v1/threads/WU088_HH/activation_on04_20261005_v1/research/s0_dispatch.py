"""Fail-closed canonical S0 input -> named HH research native command.

This entry executes the HH cohort research path, not the certified fixed-energy
F08 producer. Input identity, physical choices, run scope and output are bound.
"""
from __future__ import annotations
from pathlib import Path
import argparse, gzip, hashlib, json, math, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1'

def _pairs(items):
    d={}
    for k,v in items:
        if k in d: raise ValueError('DUPLICATE_JSON_KEY:'+k)
        d[k]=v
    return d

def bind(scenario:Path, mode:str, geometry:str, end_s:float, dt_s:float)->dict:
    if mode not in ('OFF','LCS','KS'):raise ValueError('HH_MODE')
    if geometry not in ('FLRW','BIANCHI_I'):raise ValueError('HH_GEOMETRY')
    raw=scenario.read_bytes()
    c=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('S0_IDENTITY_MISMATCH')
    if isinstance(end_s,bool) or not math.isfinite(end_s) or not 0<end_s<=8e11:raise ValueError('HH_RESEARCH_PREFIX_DOMAIN')
    if dt_s not in tuple(c['time']['refinement_dt_s']):raise ValueError('HH_TIMESTEP_DOMAIN')
    if end_s/dt_s!=int(end_s/dt_s):raise ValueError('HH_INTEGER_MACRO_GRID_REQUIRED')
    i=c['initial_state']; b=c['background']; n=c['numerics']; a=c['atomic_model']; s=c['source']; k=c['constants']
    return {'schema':'wu088.hh_on04.bound-input.v1','parent_sha256':EXPECTED,'scenario_id':c['scenario_id'],
      'research_model':'HH_ON04_COHORT_S0_'+mode,'mode':mode,'geometry':geometry,'H':b['pairs'][geometry]['H_per_s'],
      'nH0':i['nH0_cm3'],'fHe':i['fHe'],'initial_fractions':[i['fractions'][x] for x in ('HII','HeII','HeIII')],
      'initial_temperature':i['temperature_K'],'initial_photons_per_H':i['photon_number_per_H'],'initial_energy_ev':i['photon_energy_ev'],
      'source_energy_ev':s['energy_at_birth_ev'],'source_rate':s['photons_per_H_per_s'],
      'kb':k['k_B_erg_K'],'ev':k['eV_erg'],'c':k['c_cm_s'],'chi':k['binding_threshold_ev'],'cutoffs':k['cross_section_cutoff_ev'],
      'T_domain':a['scenario_temperature_guard_K'],'local_limit':n['strict_local_error_limit'],'ledger_limit':n['conservation_scaled_tolerance'],
      'full_horizon_s':c['time']['t_end_s'],'end_s':end_s,'dt_s':dt_s,'n_mu':c['spectral']['angular_quadrature']['n_mu'][0],
      'n_phi':c['spectral']['angular_quadrature']['n_phi'][0],
      'source_scheme':'accepted-two-half-endpoint-birth; midpoint photo source; fixed-grid threshold diagnosis',
      'canonical_F08_changed':False,'physical_admission':False}

def generate(c:dict)->str:
    def f(x):return format(float(x),'.17e')
    scalars={'FHE':c['fHe'],'NH0':c['nH0'],'KB':c['kb'],'EV':c['ev'],'CL':c['c'],'T0':c['initial_temperature'],'N0':c['initial_photons_per_H'],
             'EINIT':c['initial_energy_ev'],'EBIRTH':c['source_energy_ev'],'RATE':c['source_rate'],'HORIZON':c['full_horizon_s'],
             'LOCAL_LIMIT':c['local_limit'],'LEDGER_LIMIT':c['ledger_limit'],'TMIN':c['T_domain'][0],'TMAX':c['T_domain'][1]}
    lines=[f'const {k}:f64={f(v)};' for k,v in scalars.items()]
    lines += [f'const CH:[f64;3]=[{",".join(map(f,c["chi"]))}];',f'const INITF:[f64;3]=[{",".join(map(f,c["initial_fractions"]))}];',
      f'const NMU:usize={c["n_mu"]}; const NPHI:usize={c["n_phi"]}; const NN:usize=NMU*NPHI;',
      f'const SCENARIO_SHA:&str="{EXPECTED}";']
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--scenario',type=Path,required=True);ap.add_argument('--mode',required=True)
    ap.add_argument('--geometry',required=True);ap.add_argument('--end',type=float,default=8e11);ap.add_argument('--dt',type=float,default=1e10)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--rustc',default='/mnt/data/rust-1.94.1-prefix/bin/rustc');a=ap.parse_args()
    c=bind(a.scenario,a.mode,a.geometry,a.end,a.dt)
    # Refuse before creating outputs/compiling whenever the request is malformed.
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'BOUND_INPUT.json').write_text(json.dumps(c,indent=2,allow_nan=False)+'\n')
    config=generate(c);target=ROOT/'research/generated_s0.rs'
    if target.exists() and target.read_text()!=config:raise ValueError('COMPILED_SCENARIO_DRIFT')
    target.write_text(config)
    source_manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*.rs'))}
    ident=hashlib.sha256(json.dumps(source_manifest,sort_keys=True).encode()).hexdigest()
    binary=ROOT/'build/s0_hh_native';binary.parent.mkdir(exist_ok=True)
    stamp=ROOT/'build/source_stamp';compiler=Path(a.rustc)
    compiler_sha=hashlib.sha256(compiler.read_bytes()).hexdigest()
    wanted=ident+':'+compiler_sha
    commands=[]
    if not binary.exists() or not stamp.exists() or stamp.read_text()!=wanted:
        cmd=[a.rustc,'--edition=2021','-C','opt-level=2',str(ROOT/'research/s0_on04_root.rs'),'-o',str(binary)]
        r=subprocess.run(cmd,capture_output=True,timeout=120);commands.append({'argv':cmd,'exit':r.returncode})
        (a.output/'compile.stdout').write_bytes(r.stdout);(a.output/'compile.stderr').write_bytes(r.stderr)
        if r.returncode:raise RuntimeError('RUST_COMPILE_FAILED')
        stamp.write_text(wanted)
    cmd=[str(binary),a.mode,a.geometry,repr(a.end),repr(a.dt)]
    with (a.output/'native.stderr').open('wb') as err,gzip.open(a.output/'native.jsonl.gz','wb',compresslevel=5) as out:
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=err)
        for data in iter(lambda:p.stdout.read(1<<18),b''):out.write(data)
        rc=p.wait()
    commands.append({'argv':cmd,'exit':rc})
    receipt={'task':'HH-ON04','commands':commands,'native_exit':rc,'source_digest':ident,'source_files':source_manifest,
       'scenario_sha256':EXPECTED,'compiler_sha256':compiler_sha,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
       'output_sha256':hashlib.sha256((a.output/'native.jsonl.gz').read_bytes()).hexdigest(),'binding':c,'physical_admission':False}
    (a.output/'EXECUTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'mode':a.mode,'geometry':a.geometry,'exit':rc,'output':str(a.output)}));sys.exit(rc)
if __name__=='__main__':main()
