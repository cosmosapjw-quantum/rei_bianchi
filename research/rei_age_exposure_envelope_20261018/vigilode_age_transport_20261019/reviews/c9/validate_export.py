"""Independent read-only C9 audit of one completed native coefficient export."""
import ast
import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path('/workspace/scratch/36ed695112a9')
TASK = ROOT / 'rei_bianchi/research/rei_age_exposure_envelope_20261018'
PROBE = ROOT / 'runtime_probe/session_20261019T1225Z/vigilode_native_probe'
OUT = ROOT / 'vigilode_intake_20261019/c9_review'
OUT.mkdir(parents=True, exist_ok=True)
source = TASK / 'vigilode_age_transport_20261019/prepare_export.py'
prepared = PROBE / 'prepared_native'
export = PROBE / 'export'
archive = TASK / 'evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def exact(v): return Fraction.from_float(v)
receipt = json.loads((export / 'EXPORT_RECEIPT.json').read_text())
manifest = json.loads((TASK / 'contracts/NATIVE_INPUTS.json').read_text())
setup = json.loads((export / 'native_setup.json').read_text())
expected = json.loads((archive / 'setup.json').read_text())
endpoint = json.loads((archive / 'endpoint.json').read_text())
model = json.loads((export / 'model.json').read_text())
accessor = None
for statement in ast.parse(source.read_text()).body:
    if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ACCESSOR' for t in statement.targets):
        accessor = ast.literal_eval(statement.value).encode()
assert accessor
assert receipt['exit_code'] == 0
assert receipt['source_templates'] == 64
assert len(manifest['files']) == 153
assert manifest['native_sha'] == '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
assert receipt['prepared_identity']['native_sha'] == manifest['native_sha']
assert receipt['appended_accessor_sha256'] == sha_bytes(accessor)
transport_path = 'rust/rei_microphysics/src/axbi_covariant_transport.rs'
transport = (prepared / transport_path).read_bytes()
assert transport.endswith(accessor)
original_transport_size = manifest['files'][transport_path]['size']
assert sha_bytes(transport[:original_transport_size]) == manifest['files'][transport_path]['sha256']
old_suffix = (TASK / 'donors/pr171/prepared_node_accessor.rs').read_bytes() + (TASK / 'donors/pr171/positive_accessor.rs').read_bytes()
assert transport == transport[:original_transport_size] + old_suffix + accessor
original_frozen = []
for name, identity in manifest['files'].items():
    data = (prepared / name).read_bytes()
    if name == transport_path: data = data[:identity['size']]
    assert len(data) == identity['size'] and sha_bytes(data) == identity['sha256'], name
    original_frozen.append(name)
prepared_verified = []
for name, identity in receipt['prepared_identity']['outputs'].items():
    data = (prepared / name).read_bytes()
    if name == transport_path: data = data[:-len(accessor)]
    assert sha_bytes(data) == identity, name
    prepared_verified.append(name)
original_example = prepared / 'rust/rei_microphysics/examples/positive_native.rs'
derived_example = prepared / 'rust/rei_microphysics/examples/vigilode_export.rs'
assert sha(original_example) == receipt['original_example_sha256']
assert sha(derived_example) == receipt['derived_example_sha256']
assert derived_example.read_bytes().startswith(original_example.read_bytes().replace(b'fn main(', b'fn original_unused_main(', 1))
assert sha(archive / 'setup.json') == receipt['archived_setup_sha256']
assert sha(archive / 'endpoint.json') == receipt['archived_endpoint_sha256']
for name, digest in receipt['files'].items(): assert sha(export / name) == digest, name
comparisons = {key: setup[key] == expected[key] for key in expected}
assert all(comparisons.values()), comparisons
assert model['fractions'] == endpoint['flat'][:3] and model['w_ev_per_h'] == endpoint['flat'][3]
assert model['endpoint_x'] == setup['x1']
assert model['clocks']['64'] == setup['birth_times_s']
assert model['observe_time_s'] == endpoint['proper_time_s']
nh, nhe = model['nh_cm3'], model['nhe_cm3']
f, y, z = model['fractions']
assert model['absorber_cm3'] == [nh*(1-f), nhe*(1-y-z), nhe*y]
for key, values in model['clocks'].items():
    assert len(values) == int(key)
    assert all(0 < t < model['observe_time_s'] for t in values)
    assert all(a < b for a, b in zip(values, values[1:]))
cells = defaultdict(list)
packets = defaultdict(list)
with (export/'nodes.csv').open(newline='') as stream:
    fields = csv.DictReader(stream)
    for row in fields:
        ints = {name: int(row[name]) for name in ('cohort','cell','node')}
        row = {name: (ints[name] if name in ints else float(value)) for name,value in row.items()}
        assert all(math.isfinite(v) for v in row.values())
        assert 0 <= row['cohort'] < 64 and 0 <= row['cell'] < setup['cells']
        assert row['mass'] > 0 and row['q'] > 0 and row['energy'] > 0
        assert all(row[name] >= 0 for name in ('sigma0','sigma1','sigma2','lambda0','lambda1','lambda2','excess0','excess1','excess2'))
        cohort, cell = row['cohort'], row['cell']
        assert row['birth_logx'] == setup['births'][cohort]
        assert row['birth_time_s'] == setup['birth_times_s'][cohort]
        assert setup['physical_births'][cohort][cell] > 0
        cells[cohort,cell].append(row)
        packets[cohort].append(row)
assert sorted(packets) == list(range(64))
assert [len(packets[i]) for i in range(64)] == model['node_counts']
assert all([r['node'] for r in packets[i]] == list(range(len(packets[i]))) for i in range(64))
max_count_relative = max_energy_relative = 0.0
nonzero_missing = []
for cohort in range(64):
    for cell in range(setup['cells']):
        target_n = setup['physical_births'][cohort][cell]
        target_u = setup['physical_births'][cohort][setup['cells']+cell]
        rows = cells.get((cohort,cell), [])
        if target_n == 0:
            assert not rows
            continue
        assert rows, (cohort,cell)
        total_n = sum((exact(r['mass']) for r in rows), Fraction(0))
        total_u = sum((exact(r['mass'])*exact(r['q']) for r in rows), Fraction(0))
        rn = float(abs(total_n-exact(target_n))/exact(target_n))
        ru = float(abs(total_u-exact(target_u))/exact(target_u))
        max_count_relative = max(max_count_relative, rn)
        max_energy_relative = max(max_energy_relative, ru)
        # The source's original count threshold, not a new scientific tolerance.
        assert rn <= 64*2**-52, (cohort,cell,rn)
        # Stronger diagnostic for these occupied cells than the source's max(U,N*width) scaling.
        assert ru <= 128*2**-52, (cohort,cell,ru)
params = [(13.60,0.4298,5.475e4,32.88,2.963,0.0,0.0,0.0),
          (24.59,13.61,949.2,1.469,3.188,2.039,0.4434,2.136),
          (54.42,1.720,1.369e4,32.88,2.963,0.0,0.0,0.0)]
def sigma_reference(e, par):
    eth,e0,s0,ya,p,yw,y0,y1 = par
    if e < eth: return 0.0
    x = e/e0-y0
    y = math.sqrt(x*x+y1*y1)
    return s0*((x-1.0)*(x-1.0)+yw*yw)*y**(p/2-5.5)*(1+math.sqrt(y/ya))**(-p)*1e-18
scale = (1/21) / math.exp(model['endpoint_x'])
sigma_max_ulp = 0.0
energy_matches = 0
zero_hazard_nodes = 0
tau_max = 0.0
packet_rows = []
for i in range(64):
    rows = packets[i]
    for r in rows:
        assert r['energy'] == r['q'] * scale
        energy_matches += 1
        rates = []
        for j in range(3):
            assert r[f'lambda{j}'] == 29979245800.0 * model['absorber_cm3'][j] * r[f'sigma{j}']
            expected_excess = r['energy'] - setup['binding_ev'][j] if r[f'sigma{j}'] > 0 else 0.0
            assert r[f'excess{j}'] == expected_excess
            sig = sigma_reference(r['energy'], params[j])
            sigma_max_ulp = max(sigma_max_ulp, abs(sig-r[f'sigma{j}'])/math.ulp(sig) if sig else 0.0)
            assert (sig == 0) == (r[f'sigma{j}'] == 0)
            rates.append(r[f'lambda{j}'])
        if not any(rates): zero_hazard_nodes += 1
        tau_max = max(tau_max, math.fsum(rates)*(model['observe_time_s']-r['birth_time_s']))
    packet_mass = sum((exact(r['mass']) for r in rows),Fraction(0))
    packet_u = sum((exact(r['mass'])*exact(r['q']) for r in rows),Fraction(0))
    reference_mass = setup['source_inventory'][i][0]
    source_u = setup['source_inventory'][i][1]
    source_u_reconstructed = float(packet_u) * ((1/21)/math.exp(setup['births'][i]))
    packet_rows.append({'cohort':i,'node_count':len(rows),'exact_node_mass_as_f64':float(packet_mass),
                        'archived_source_inventory_mass':reference_mass,
                        'source_mass_relative_defect':float(abs(packet_mass-exact(reference_mass))/exact(reference_mass)),
                        'source_energy_relative_defect':abs(source_u_reconstructed-source_u)/source_u})
    assert packet_rows[-1]['source_mass_relative_defect'] <= 64*2**-52
    assert packet_rows[-1]['source_energy_relative_defect'] <= 128*2**-52
summary = {
    'status':'PASS_SCOPED_EXPORT_SOURCE_AND_NODE_IDENTITY',
    'native_reexecutions':0,'native_source_sha':manifest['native_sha'],
    'frozen_native_files_checked':len(original_frozen),
    'prepared_outputs_checked_before_read_only_append':len(prepared_verified),
    'native_original_prefix_unchanged':True,
    'export_accessor_appended_once':True,'original_example_unchanged':True,
    'derived_example_contains_unmodified_original_except_unused_main_name':True,
    'archived_setup_fields_exact':comparisons,
    'archived_endpoint_state_and_clock_exact':True,
    'receipt_file_hashes_exact':True,
    'export_files':receipt['files'],
    'export_source_sha256':sha(source),
    'node_count':sum(map(len,packets.values())),'source_packets':len(packets),
    'nonempty_cells':len(cells),'zero_hazard_nodes':zero_hazard_nodes,
    'cell_exact_dyadic_mass_max_relative_defect':max_count_relative,
    'cell_exact_dyadic_reference_energy_max_relative_defect':max_energy_relative,
    'packet_mass_max_relative_defect':max(r['source_mass_relative_defect'] for r in packet_rows),
    'packet_source_energy_max_relative_defect':max(r['source_energy_relative_defect'] for r in packet_rows),
    'physical_energy_exact_float_product_checks':energy_matches,
    'native_lambda_component_product_checks':3*sum(map(len,packets.values())),
    'sigma_python_recalculation_max_ulp_diagnostic':sigma_max_ulp,
    'clock_64_matches_actual_births':True,'clock_observe_matches_actual_endpoint':True,
    'endpoint_isotropic_energy_scale':scale,'largest_original_packet_optical_depth_float_diagnostic':tau_max,
    'total_exported_mass':math.fsum(r['mass'] for rows in packets.values() for r in rows),
    'total_endpoint_survivor_mass':endpoint['N'],
    'model_scope':'Exact exported binary64 node coefficients; frozen recorded endpoint gas and geometry; source packet birth timing only. No nonlinear trajectory or continuum coefficient certificate.',
    'production_scientific_admission':'NOT_ISSUED',
}
(OUT/'EXPORT_NODE_AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'EXPORT_PACKET_AUDIT.json').write_text(json.dumps(packet_rows,indent=2)+'\n')
print(json.dumps(summary,indent=2))

