"""One native prefix execution, reusable thereafter; no trajectory calls."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import time
import numpy as np
import scipy
from scipy.linalg import expm
from transport_core import (energy_nodes, number_generator, energy_generator,
    original_hat_map, projected_number_map, projected_energy_map, column_norm,
    local_defect_bound)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT/'.cuh/fastest-track/REI-CHAT-FLRW08/transport-consistency/outputs'
TASK = 'REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL'
RUSTC = '/home/cosmosapjw/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin/rustc'
HUBBLE = {'FLRW':[1e-14]*3, 'BI':[1.01e-14,0.99e-14,1e-14]}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, v):
    Path(p).write_text(json.dumps(v, indent=2, allow_nan=False)+'\n')


def command(argv, name):
    p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    (OUT/(name+'.stdout')).write_text(p.stdout)
    (OUT/(name+'.stderr')).write_text(p.stderr)
    save(OUT/(name+'.command.json'), {'argv':argv, 'exit_code':p.returncode})
    if p.returncode:
        raise RuntimeError(f'{name} exit {p.returncode}; retained stdout/stderr')
    return p.stdout


def extract_prefix():
    path = ROOT/'rust/rei_microphysics/src/paired_runtime.rs'
    source = path.read_bytes()
    marker = b'fn endpoint('
    start = source.index(marker)
    body_start = source.index(b'{', start)
    stop = source.index(b'    let (weights,wb)=source_weights(c,h,t1)?;', body_start)
    body = source[body_start+1:stop]
    wrapper = b'pub fn transport_prefix(c:&PairedConfig,h:[f64;3],s:&PairedState,dt:f64,nodes:&[f64])->Result<(Vec<f64>,Vec<f64>,Vec<f64>),ForwardError>{'
    helpers = b'''    Ok((transported,guard_n,guard_u))
}
pub fn chosen_ratio(c:&PairedConfig,h:[f64;3],t:f64,dt:f64,d:usize)->f64 {
    let q=qhat(c,d);g_point(q,h,t+dt)/g_point(q,h,t)
}
pub fn validate_input(c:&PairedConfig,s:&PairedState,e:&[f64])->Result<(),ForwardError>{validate(c,s,e)}
'''
    module = OUT/'original_transport_prefix.rs'
    module.write_bytes(source[:start]+wrapper+body+helpers)
    identity = {'source_path':str(path.relative_to(ROOT)), 'source_sha256':sha(path),
        'helper_span_bytes':[0,start], 'original_prefix_body_span_bytes':[body_start+1,stop],
        'original_prefix_lines':[source[:body_start+1].count(b'\n')+1,source[:stop].count(b'\n')],
        'original_prefix_body_sha256':hashlib.sha256(body).hexdigest(),
        'generated_module_path':str(module.relative_to(ROOT)), 'generated_module_sha256':sha(module),
        'signature_change':'endpoint -> transport_prefix; return transported vectors/guards',
        'appended_helpers':'return; chosen_ratio; validate_input',
        'body_verbatim':True, 'source_or_chemistry_invoked':False}
    save(OUT/'prefix_extraction.json', identity)
    return identity


def input_state(kind, E):
    v = np.zeros(len(E)+2)
    if kind < len(E):
        v[kind] = .05 if kind == 0 else 1.
    elif kind == 33:
        v[-2:] = [.05,.3]
    else:
        v[:len(E)] = .05*np.arange(1,len(E)+1)/561.
        v[-2:] = [.025,.125]
    return v


def qhat(d):
    mu = -1+2*((d//16)+.5)/8
    phi = 2*math.pi*((d%16)+.5)/16
    rr = math.sqrt(1-mu*mu)
    q = np.array([rr*math.cos(phi),rr*math.sin(phi),mu])
    return q/math.hypot(*q)


def log_g(h,q,t):
    return .5*math.log(float(np.sum(q*q*np.exp(-2*np.asarray(h)*t))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reuse-native', action='store_true', help='mandatory after first native execution')
    args = ap.parse_args(); start = time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
    lib = OUT/'librei_microphysics.rlib'; binary = OUT/'native_probe'; native_path = OUT/'native.json'
    if args.reuse_native:
        native = json.loads(native_path.read_text()); extraction = json.loads((OUT/'prefix_extraction.json').read_text())
        new_calls = 0
    else:
        if native_path.exists():
            raise RuntimeError('native output exists; use --reuse-native; never replay completed native prefix')
        extraction = extract_prefix()
        command([RUSTC,'--edition=2021','--crate-name','rei_microphysics','--crate-type','rlib','-O',str(ROOT/'rust/rei_microphysics/src/lib.rs'),'-o',str(lib)],'build_library')
        command([RUSTC,'--edition=2021','-O',str(HERE/'native_probe.rs'),'--extern','rei_microphysics='+str(lib),'-o',str(binary)],'build_driver')
        native = json.loads(command([str(binary)],'native_probe'))
        save(native_path,native); new_calls = 1
    E = energy_nodes(); B = number_generator(E); C = energy_generator(E)
    lam = E[1:]/np.diff(E); Lambda = float(max(lam)); Ln = 2*Lambda; Le = Ln-1
    w = np.r_[E[1:],1.]; scales = []; max_raw = 0.; moment = 0.; non_cfl_cases = 0
    worst = None; details = []
    for row in native['cases']:
        old = input_state(row['kind'],E); r = row['ratio']
        predicted = original_hat_map(E,r)@old
        observed = np.r_[row['photons'],row['guard_n'],row['guard_u']]
        diff = observed-predicted
        old_n = float(sum(old[:-1])); old_u = float(E@old[:len(E)]+old[-1])
        number_error = float((sum(abs(diff[:len(E)]))+abs(diff[-2]))/old_n)
        energy_error = float((E@abs(diff[:len(E)])+abs(diff[-1]))/old_u)
        scaled = max(number_error, energy_error); scales.append(scaled)
        max_raw = max(max_raw,float(max(abs(diff))))
        moment = max(moment,abs(float(E@observed[:len(E)]+observed[-1])-r*old_u)/old_u)
        non_cfl_cases += int((1-r)*Lambda>1)
        if worst is None or scaled>worst['scaled_error']:
            worst = {k:row[k] for k in ['geometry','t0','dt','ray','kind','ratio']}
            worst.update(scaled_error=scaled,number_l1_error=number_error,weighted_energy_l1_error=energy_error)
        if row['kind']==0:
            details.append({k:row[k] for k in ['geometry','t0','dt','ray','guard_n','guard_u']})
    operators=[]
    for s in [5e-12,1e-8,1e-6,6.25e-6,1.25e-5]:
        r=math.exp(-s); K=projected_number_map(E,r); U=projected_energy_map(E,r)
        dn=column_norm(K-expm(s*B)); de=column_norm(U-expm(s*C),w)
        operators.append({'s':s,'x_Lambda':(1-r)*Lambda,
            'number_operator_defect':dn,'energy_operator_defect':de,
            'number_local_bound':local_defect_bound(Ln,s),'energy_local_bound':local_defect_bound(Le,s),
            'matrix_cfl_residual_number':float(np.max(abs(K-(np.eye(len(E))+(1-r)*B)))),
            'matrix_cfl_residual_energy':float(np.max(abs(U-(np.eye(len(E))+(1-r)*C))))})
    global_bounds=[]
    # No stepping: quadratic bound sum s_k^2<=s_max*sum s_k for finite partitions.
    for geometry,h in HUBBLE.items():
        Hmax=max(h)
        for ray in [0,17,63,127]:
            q=qhat(ray)
            for window in [1e10,1e13]:
                total_s=log_g(h,q,0)-log_g(h,q,window)
                for dt in [500.,1000.,6.25e8,1.25e9]:
                    smax=Hmax*dt
                    bn=.5*(Ln+Ln*Ln)*smax*total_s
                    be=.5*(Le+Le*Le)*smax*total_s
                    global_bounds.append({'geometry':geometry,'ray':ray,'window_s':window,
                        'maximum_endpoint_step_s':dt,'partition_steps':math.ceil(window/dt),
                        'characteristic_total_s':total_s,'uniform_cfl_sufficient':Hmax*dt*Lambda<=1,
                        'number_sum_bound_unclipped':bn,'number_bound_clipped_2':min(2.,bn),
                        'weighted_energy_sum_bound_unclipped':be,
                        'weighted_energy_bound_clipped_2':min(2.,be),
                        'claim':'pure-transport real arithmetic only; possibly loose; no coupled certificate'})
    rational_lam=[Fraction(float(E[j]))/(Fraction(float(E[j]))-Fraction(float(E[j-1]))) for j in range(1,len(E))]
    exact_lambda=max(rational_lam)
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'rust/rei_microphysics/src').glob('*.rs'))}
    result={'task_id':TASK,'source_parent':'e63ca0735a3e3e7eebbf4498c697d806d375e191',
        'scientific_admission':'HOLD','continuum_time_error_certificate':'NOT_ESTABLISHED',
        'new_full_campaign_executions':0,'new_coupled_trajectory_executions':0,
        'native_prefix_cases':len(native['cases']),'native_prefix_max_scaled_error':max(scales),
        'native_prefix_max_raw_coordinate_error':max_raw,'native_prefix_worst_case':worst,
        'native_energy_moment_max_relative_residual':moment,'native_non_cfl_cases':non_cfl_cases,
        'native_comparison_status':'PASS' if max(scales)<=1e-9 else 'FAIL',
        'normalization':'full photon+guard number l1 / input number; weighted energy l1 / input energy; max of both',
        'non_cfl_linear_formula_rejected':True,'basis_operator_bounds_status':'PENDING_SELF_CHECK',
        'coupled_stability_status':'CONDITIONAL_NOT_CERTIFIED','production_source_modified':False,
        'floating_point_rigorous_envelope':False,'all_state_bound_scope':'real arithmetic; operator norm proof, no chemistry/source',
        'projection_domain':'closed auxiliary cone U<=10N; public runtime input requires strict U<10N',
        'grid':{'spectral_subdivisions':8,'n_mu':8,'n_phi':16},
        'Lambda':Lambda,'number_generator_norm':Ln,'weighted_energy_generator_norm':Le,
        'exact_binary_grid_constants':{'Lambda_fraction':str(exact_lambda),
            'number_norm_fraction':str(2*exact_lambda),'energy_norm_fraction':str(2*exact_lambda-1),
            'CFL_dt_BI_fraction_s':str(1/(Fraction(1.01e-14)*exact_lambda)),
            'CFL_dt_BI_s':float(1/(Fraction(1.01e-14)*exact_lambda))},
        'operator_tables':operators,'pure_transport_global_bounds':global_bounds,
        'occupied_lowest_node_witnesses':details,'prefix_extraction':extraction,
        'native_output_directory':str(OUT.relative_to(ROOT)),'native_output_sha256':sha(native_path),
        'binary_sha256':sha(binary),'library_sha256':sha(lib),'included_source_sha256':source_hashes,
        'compile_commands':[json.loads((OUT/(x+'.command.json')).read_text()) for x in ['build_library','build_driver']],
        'native_process_executions_in_this_invocation':new_calls,'native_prefix_executions_total':1,
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
                   'rustc':command([RUSTC,'--version'],'rustc_version').strip()},
        'wall_seconds':time.perf_counter()-start}
    save(HERE/'RESULTS.json',result)
    print(json.dumps({k:result[k] for k in ['native_prefix_cases','native_prefix_max_scaled_error',
        'native_energy_moment_max_relative_residual','native_non_cfl_cases','scientific_admission']}))


if __name__=='__main__':
    main()
