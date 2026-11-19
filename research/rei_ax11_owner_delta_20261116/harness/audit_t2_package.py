#!/usr/bin/env python3
"""Bounded static/resource/input checks; never pretend a Rust build was run."""
import ast,hashlib,json,math,struct,time
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1];REPO=UNIT.parents[1]
PKG=UNIT/'t2_package';OLD=REPO/'research/rei_ax11_t1_wave_20261116'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=UNIT/'audit_v1/T2_PACKAGE_AUDIT.json';assert not out.exists();tic=time.monotonic();cpu=time.process_time()
    a=json.loads((PKG/'ALLOCATION.json').read_text());m=json.loads((PKG/'PACKAGE_MANIFEST.json').read_text())
    for rel,v in m['files'].items():assert (PKG/rel).stat().st_size==v['bytes'] and sha(PKG/rel)==v['sha256']
    assert sha(PKG/'harness/native_executor.py')==a['executor_sha256'];ast.parse((PKG/'harness/native_executor.py').read_text())
    original=(OLD/'harness/ax11_production_segment.rs').read_text();expected=original
    for before,after in m['wrapper_text_replacements'].items():expected=expected.replace(before,after)
    assert expected==(PKG/'harness/ax11_production_segment.rs').read_text()
    # Directly detect why the old production executable cannot be a T2 entry.
    assert 'cfg.local_target.to_bits()!=2.5e-6_f64.to_bits()' in original
    assert 'cfg.initial_dln_a.to_bits()!=1e-4_f64.to_bits()' in original
    assert 'cfg.local_target.to_bits()!=6.25e-7_f64.to_bits()' in expected
    assert 'cfg.initial_dln_a.to_bits()!=1e-10_f64.to_bits()' in expected
    assert 'state.next_dln_a<1e-10' in original and 'state.next_dln_a<1e-10' in expected
    prefix_manifest=json.loads((PKG/'PREFIX_INPUT_MANIFEST.json').read_text());prefix_checks={};inputcount=0
    for case,files in prefix_manifest.items():
        base=REPO.parent/f'ax11_work/native_prefix_v1/time_preflight_results/{case}_T2_FLOOR_START'
        for name,v in files.items():
            p=base/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],str(p);inputcount+=1
        lines=(base/'checkpoint.end.txt').read_text().splitlines();v=list(map(float,lines[1].split()));n=list(map(int,lines[2].split()))
        values=[v[0],*v[3:10],*map(float,lines[3].split())];counts=[n[0],n[1],n[5],n[2],n[3],n[4]];photons=list(map(float,lines[4].split()))
        with (base/'raw/state_trace.bin').open('rb') as f:
            header=f.read(56);assert header[:8]==b'AX11TRC1';fields=struct.unpack('<6Q',header[8:]);size,records=fields[3:5];assert records==4097
            f.seek(56+4096*size);saved=f.read(size)
        actual=struct.pack('<32d6Q',*values,*counts)+struct.pack('<'+'d'*len(photons),*photons)
        assert actual==saved
        ref=dict(x.split('=',1) for x in (base/'config.cfg').read_text().splitlines())
        cfg=dict(x.split('=',1) for x in (PKG/a['configs'][case]['path']).read_text().splitlines())
        keys={'max_steps','max_attempts','max_rhs','max_wall_s','output_budget_mib'}
        assert {k:v for k,v in cfg.items() if k not in keys}=={k:v for k,v in ref.items() if k not in keys}
        assert float(cfg['local_target'])==6.25e-7 and float(cfg['initial_dln_a'])==1e-10
        prefix_checks[case]={'checkpoint_equals_native_full_state_trace_record_4096':True,'native_cloud_input_hashes_equal':True,
                            'config_physics_fields_exact':True,'accepted':n[0],'trials':n[1],'RHS':n[4],'wall_s_retained':v[10]}
    c=a['caps'];maxcpu=2*c['per_case_CPU_s']+c['preparation_CPU_and_wall_cap_s']+a['postprocess_reservation']['CPU_s']+60
    maxwall=2*c['per_case_wall_s']+c['preparation_CPU_and_wall_cap_s']+a['postprocess_reservation']['wall_s']+60
    assert maxcpu<=c['aggregate_CPU_s'] and maxwall<=c['aggregate_sum_job_wall_s']
    assert c['all_segment_starts_including_preflight']==3+2*c['per_case_full_segments']
    assert math.ceil((c['per_case_accepted']-4096)/c['segment_accepted'])<=c['per_case_full_segments']
    assert c['automatic_retries']==0 and c['max_concurrent_cases']==2 and c['build_starts']==1
    result={'status':'PASS_SCOPED_STATIC_INPUT_AND_RESOURCE_CHECKS','native_execution':'NOT_RUN','Rust_compile':'NOT_RUN_CLOUD_RUST_UNAVAILABLE',
      'old_T1_binary_compatibility':'REJECTED_BY_EXACT_PHYSICAL_SCOPE_GUARDS','native_build_required':1,'native_preflight_required':['PLUS8','PLUS8resume','ZERO16'],
      'wrapper_changes':'Only enumerated T1->T2 scope labels, resource ceilings, intended target and startup step; original physical library/output loop/guards unchanged',
      'prefix_input_files_hash_verified':inputcount,'prefix_checks':prefix_checks,
      'maximum_new_CPU_s_including_preparation_controller_postprocess':maxcpu,
      'maximum_new_sum_job_wall_s_including_reservations':maxwall,
      'remaining_aggregate_reserve_s':c['aggregate_CPU_s']-maxcpu,
      'old_cost':'Bounded profile + full T1 retained; historical earlier accumulated cost UNKNOWN',
      'known_limit':'CPU timing forecast conditional; no guarantee of endpoint under finite caps',
      'new_completed_nodes':0,'DAG':'10/17;28/88',
      'execution':{'CPU_s':time.process_time()-cpu,'wall_s':time.monotonic()-tic,'script_sha256':sha(Path(__file__))}}
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
