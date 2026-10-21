"""Prepare a manifest-checked native copy and export frozen coefficients once.

No native history or transformed RHS is evaluated by the exporter. The source
packets are the original 64 injection templates; only their clocks will change.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(TASK / 'src'))
from prepare_native import prepare
from native_inputs import load_manifest

ACCESSOR = '''
// BEGIN RESEARCH_READ_ONLY_NODE_EXPORT
impl PreparedAbsorption {
    pub fn research_export_nodes(&self, ab: [f64; 3], nh: f64)
        -> Result<Vec<(usize, f64, f64, [f64; 3], [f64; 3])>, ForwardError>
    {
        self.evaluate(ab, nh, 0.0)?;
        Ok(self.nodes.iter().map(|n| (n.cell, n.q, n.number, n.sigma, n.excess_ev)).collect())
    }
}
// END RESEARCH_READ_ONLY_NODE_EXPORT
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--native-input-dir', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--fetch-missing', action='store_true')
    parser.add_argument('--rust-prefix', type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    native = runtime / 'prepared_native'
    records = runtime / 'export'
    records.mkdir(parents=True, exist_ok=True)
    if (records / 'EXPORT_RECEIPT.json').exists():
        raise RuntimeError('Export receipt already exists; no repeated native export permitted.')
    identity = prepare(TASK, native, args.archive, args.repo,
                       args.fetch_missing, native_input_dir=args.native_input_dir)
    manifest = load_manifest(TASK, args.archive)
    transport = native / 'rust/rei_microphysics/src/axbi_covariant_transport.rs'
    prepared_bytes = transport.read_bytes()
    transport.write_bytes(prepared_bytes + ACCESSOR.encode())
    source = native / 'rust/rei_microphysics/examples/positive_native.rs'
    generated = source.read_text()
    if generated.count('fn main(') != 1:
        raise RuntimeError('Unexpected generated example main count')
    archive_data = TASK / 'evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data'
    expected = json.loads((archive_data / 'setup.json').read_text())
    endpoint = json.loads((archive_data / 'endpoint.json').read_text())
    assert expected['birth_count'] == 64 and expected['n_mu'] == 8
    assert expected['source_subdivisions'] == 8 and expected['transport_cells'] == 16
    assert endpoint['flat'][:4] == [0.010065857799832125, 0.010066719415292124,
                                   0.000999219556540277, 1.1243735845579859]
    setup_body = generated.split('fn server(', 1)[1].split('    let x0 =', 1)[1].split('    if binary_rpc {', 1)[0]
    setup_body = '    let x0 =' + setup_body
    setup_body = setup_body.replace('    println!(', '    writeln!(&mut setup_file, ')
    end = setup_body.rfind(');')
    setup_body = setup_body[:end] + ')?;' + setup_body[end + 2:]
    export_main = r'''
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::io::Write;
    let out = std::env::args().nth(1).ok_or("output directory required")?;
    let out = Path::new(&out);
    let (birth_count, nmu, source, transport_cells) = (64, 8, 8, 16);
    let s = setup(0.0, birth_count, nmu, source, transport_cells)?;
    let mut setup_file = fs::File::create(out.join("native_setup.json"))?;
SETUP_BODY
    let x: f64 = ENDPOINT_X;
    let fractions: [f64; 3] = ENDPOINT_FRACTIONS;
    let a = x.exp();
    let point = s.d.geometry_point(a)?;
    let g = point.geometry()?;
    let nh = s.d.n_h0_cm3 / a.powi(3);
    let nhe = s.d.n_he0_cm3 / a.powi(3);
    let ab = [nh * (1.0-fractions[0]), nhe*(1.0-fractions[1]-fractions[2]), nhe*fractions[1]];
    let rays = s.d.transport.ray_geometry(&g)?;
    let c = HHeModel::controlled_fixture().c_cm_s;
    let mut csv = fs::File::create(out.join("nodes.csv"))?;
    writeln!(csv,"cohort,cell,node,q,mass,sigma0,sigma1,sigma2,excess0,excess1,excess2,energy,lambda0,lambda1,lambda2,birth_logx,birth_time_s")?;
    let mut counts = vec![];
    for (cohort, template) in s.templates.iter().enumerate() {
        let prep = s.d.transport.prepare(template, &g)?;
        let nodes = prep.research_export_nodes(ab, nh)?;
        counts.push(nodes.len());
        let b = s.d.geometry_point(s.births[cohort].exp())?.time_s;
        for (node, (cell, q, mass, sigma, excess)) in nodes.into_iter().enumerate() {
            let ray = &rays[cell / s.d.transport.n_energy()];
            let rates = [c*ab[0]*sigma[0], c*ab[1]*sigma[1], c*ab[2]*sigma[2]];
            writeln!(csv,"{cohort},{cell},{node},{q},{mass},{},{},{},{},{},{},{},{},{},{},{},{}",
                sigma[0],sigma[1],sigma[2],excess[0],excess[1],excess[2],q*ray.scale,
                rates[0],rates[1],rates[2],s.births[cohort],b)?;
        }
    }
    let mut coarse = vec![];
    for n in [8usize,16,32,64] {
        let times = (0..n).map(|j| s.d.geometry_point((x0+0.002*(j as f64+0.5)/n as f64).exp()).map(|p|p.time_s)).collect::<Result<Vec<_>,_>>()?;
        coarse.push(format!("\"{n}\":{:?}",times));
    }
    fs::write(out.join("model.json"), format!("{{\"model\":\"fixed_source_fixed_opacity_age_transport\",\"endpoint_x\":{x},\"observe_time_s\":{},\"h_per_s\":{},\"nh_cm3\":{nh},\"nhe_cm3\":{nhe},\"absorber_cm3\":{:?},\"fractions\":{:?},\"w_ev_per_h\":ENDPOINT_W,\"node_counts\":{:?},\"clocks\":{{{}}}}}",point.time_s,point.h_per_s,ab,fractions,counts,coarse.join(",")))?;
    Ok(())
}
'''
    export_main = (export_main.replace('SETUP_BODY', setup_body)
                   .replace('ENDPOINT_X', repr(expected['x1']))
                   .replace('ENDPOINT_FRACTIONS', repr(endpoint['flat'][:3]))
                   .replace('ENDPOINT_W', repr(endpoint['flat'][3])))
    derived = source.with_name('vigilode_export.rs')
    derived.write_text(generated.replace('fn main(', 'fn original_unused_main(', 1) + export_main)
    env = dict(os.environ)
    env['PATH'] = str(args.rust_prefix / 'bin') + os.pathsep + env['PATH']
    env['CARGO_HOME'] = str(runtime / 'cargo_home')
    env['CARGO_TARGET_DIR'] = str(runtime / 'native_target')
    command = [str(args.rust_prefix / 'bin/cargo'), 'run', '--release', '-j', '2',
               '--manifest-path', str(native / 'rust/rei_microphysics/Cargo.toml'),
               '--example', 'vigilode_export', '--', str(records)]
    started = time.monotonic()
    result = subprocess.run(command, env=env, capture_output=True, text=True,
                            input='', timeout=120)
    (records / 'command.stdout').write_text(result.stdout)
    (records / 'command.stderr').write_text(result.stderr)
    receipt = {'command': command, 'exit_code': result.returncode,
               'wall_seconds': time.monotonic()-started, 'native_exports': 1,
               'native_rhs_calls': 0, 'source_templates': 64,
               'prepared_identity': identity, 'original_manifest_count': len(manifest['files']),
               'original_example_sha256': sha(source), 'derived_example_sha256': sha(derived),
               'appended_accessor_sha256': hashlib.sha256(ACCESSOR.encode()).hexdigest(),
               'archived_setup_sha256': sha(archive_data/'setup.json'),
               'archived_endpoint_sha256': sha(archive_data/'endpoint.json')}
    if result.returncode == 0:
        actual = json.loads((records/'native_setup.json').read_text())
        comparisons = {key: actual[key] == expected[key] for key in
                       ['births','birth_times_s','physical_births','source_inventory','encoded_births']}
        receipt['archived_source_exact_comparisons'] = comparisons
        if not all(comparisons.values()):
            raise RuntimeError('Native source does not exactly match archived setup')
        receipt['files'] = {p.name: sha(p) for p in records.iterdir() if p.is_file()}
    (records / 'EXPORT_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    if result.returncode:
        raise RuntimeError(result.stderr)
    print(json.dumps({'status':'EXPORTED','output':str(records),
                      'native_exports':1,'native_rhs_calls':0,
                      'wall_seconds':receipt['wall_seconds']}))


if __name__ == '__main__':
    main()
