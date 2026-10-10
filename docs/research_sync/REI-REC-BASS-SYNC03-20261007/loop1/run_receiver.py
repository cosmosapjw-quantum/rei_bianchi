#!/usr/bin/env python3
"""Compile exact BASS modules and consume immutable actual F08 exports."""
import csv, gzip, hashlib, io, json, math, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent
SYNC = ROOT.parent
SOURCE = SYNC / 'intake/rei/sources/runs/rei_fastest_v1/paired/consumer_inputs'
RUSTC = pathlib.Path(os.environ.get('SYNC03_RUSTC', str(SYNC.parent / 'runtime_recovery/rust-1.94.1/bin/rustc')))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence, outputs = ROOT/'evidence', ROOT/'outputs'
    evidence.mkdir(exist_ok=True); outputs.mkdir(exist_ok=True)
    binary = evidence/'f08_receiver'
    command = [str(RUSTC), '--edition=2021', '-O', str(ROOT/'native/f08_receiver.rs'), '-o', str(binary)]
    if os.environ.get('SYNC03_RUST_SYSROOT'):
        command.extend(['--sysroot',os.environ['SYNC03_RUST_SYSROOT']])
    build = subprocess.run(command, text=True, capture_output=True)
    (evidence/'BUILD.stdout').write_text(build.stdout); (evidence/'BUILD.stderr').write_text(build.stderr)
    version = subprocess.run([str(RUSTC),'--version'],text=True,capture_output=True)
    build_receipt = {'command':command,'exit_code':build.returncode,'rustc':version.stdout.strip(),'rustc_version_exit':version.returncode,'rustc_version_stderr':version.stderr,'LD_LIBRARY_PATH':os.environ.get('LD_LIBRARY_PATH','')}
    (evidence/'BUILD.json').write_text(json.dumps(build_receipt,indent=2)+'\n')
    if build.returncode: raise RuntimeError('native compilation failed; evidence retained')
    source_manifest=json.loads((SYNC/'intake/rei/NE_INPUT_MANIFEST.json').read_text())
    source_by_name={pathlib.Path(item['path']).name:item for item in source_manifest['files']}
    summaries=[]
    for level in (0,1,2):
      for geometry in ('FLRW','BI'):
        name=f'T{level}_{geometry}'
        path=SOURCE/f'{name}-electron_density.csv.gz'
        authority=source_by_name[path.name]
        assert digest(path)==authority['sha256'], 'immutable input hash mismatch'
        with gzip.open(path,'rt',newline='') as f: rows=list(csv.DictReader(f))
        t=[float(r['normal_time_s']) for r in rows]; ne=[float(r['ne_proper_cm3']) for r in rows]
        assert len(rows)>=2 and all(math.isfinite(v) for v in t+ne)
        assert all(b>a for a,b in zip(t,t[1:])) and all(v>=0 for v in ne)
        assert all(float(r['D_gas_normal_observer'])==1 for r in rows), 'nonzero-tilt requires separate ray authority'
        payload=''.join(f'{a:.17e},{b:.17e}\n' for a,b in zip(t,ne))
        started=time.monotonic()
        proc=subprocess.run([str(binary)],input=payload,text=True,capture_output=True)
        elapsed=time.monotonic()-started
        (evidence/f'{name}.stderr').write_text(proc.stderr)
        run={'command':[str(binary)],'exit_code':proc.returncode,'wall_seconds':elapsed,'input':str(path.relative_to(SYNC)),'input_sha256':digest(path),'stdin_sha256':hashlib.sha256(payload.encode()).hexdigest()}
        (evidence/f'{name}.RUN.json').write_text(json.dumps(run,indent=2)+'\n')
        if proc.returncode: raise RuntimeError(f'{name} native receiver failed')
        output=outputs/f'{name}-visibility.csv.gz'
        output.write_bytes(gzip.compress(proc.stdout.encode(),mtime=0))
        native=list(csv.DictReader(io.StringIO(proc.stdout)))
        assert len(native)==len(rows)
        q=[float(r['q_normal_s_inverse']) for r in native]
        p=[float(r['cell_probability_tail0']) for r in native[:-1]]
        summaries.append({'history':name,'rows':len(rows),'cells':len(rows)-1,'t_start_s':t[0],'t_end_s':t[-1],'ne_min_cm3':min(ne),'ne_max_cm3':max(ne),'tau_tail0':float(native[0]['tau_tail0']),'survival_start_tail0':float(native[0]['survival_tail0']),'integrated_probability_tail0':math.fsum(p),'mass_residual_tail0':math.fsum([float(native[0]['survival_tail0']),*p])-1.0,'left_endpoint_depth_diagnostic':math.fsum(qi*(b-a) for qi,a,b in zip(q,t,t[1:])),'right_endpoint_depth_diagnostic':math.fsum(qi*(b-a) for qi,a,b in zip(q[1:],t,t[1:])),'output':str(output.relative_to(SYNC)),'output_sha256':digest(output),**run})
    manifest={'schema':'SYNC03_F08_BASS_NATIVE_RECEIVER_V1','bass_commit':'1e45e0f48cd83dcb21c23d4087fa5526195331d7','rei_export_commit':source_manifest['head'],'source_files':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in sorted((ROOT/'native').rglob('*.rs'))],'native_binary_sha256':digest(binary),'histories':summaries,'claim':'finite endpoint-PL integrated cold-Thomson opacity; no continuum or finite-temperature certificate'}
    (outputs/'NATIVE_SUMMARY.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'NATIVE_EXECUTED','histories':[{k:h[k] for k in ('history','cells','tau_tail0','mass_residual_tail0')} for h in summaries]},indent=2))

if __name__=='__main__':main()
