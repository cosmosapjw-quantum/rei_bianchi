"""Metadata/source audit and pre-output locks; no producer imports or grid generation."""
from pathlib import Path
from decimal import Decimal
import os,json,hashlib,zipfile,subprocess,platform,datetime
import numpy as np,scipy,pytest
ROOT=Path('/root/WU088_HH_R31AO_FOLLOWUP_20260930')
BASE=ROOT/'research/r31ao_unequal_ladder'
OUT=BASE/'ncp_preflight_20260930'
RUN=Path('/root/WU088_R31AL_Z075_RUNTIME_20260930')
ARCH=Path('/root/WU088_R31Y_PRODUCER_INTAKE_20260929/WU088_HH_C21_TRANSFER_CP4_20260923.zip')
PRE=ROOT/'research/r31al_z075_gate/authorized_z075_20260930/PRE_OUTPUT_LOCK.json'
def h(p):
    obj=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1024*1024):obj.update(b)
    return obj.hexdigest()
def save(n,x):
    p=OUT/n
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rec(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':h(p)}
def reference(path,lo,hi,meaning):
    p=RUN/path;lines=p.read_text().splitlines()
    return {'path':str(p),'archive':str(ARCH),'member':path,'sha256':h(p),'lines':[lo,hi],
            'source':'\n'.join(f'{i}: {lines[i-1]}' for i in range(lo,hi+1)),'meaning':meaning}
before={str(p.relative_to(RUN)):[p.stat().st_size,p.stat().st_mtime_ns] for p in RUN.rglob('*') if p.is_file()}
save('RUNTIME_METADATA_BEFORE.json',before)
save('ENVIRONMENT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'pytest':pytest.__version__,'longdouble_bytes':np.dtype(np.longdouble).itemsize,'longdouble_significand_bits':np.finfo(np.longdouble).nmant+1,'CPU':next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'compiler_not_invoked':True,'kernel_not_invoked':True})
pre=json.loads(PRE.read_text())
source_records=[]
archive_record=rec(ARCH)
assert archive_record['sha256']==pre['producer_archive_sha256']
additional=['cont2c/all94/run_all94.py','cont2c/convergence/run_convergence.py','inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/src/r10_blocks.py']
with zipfile.ZipFile(ARCH) as zip:
    for path in list(pre['producer_source_sha256'])+additional:
        p=RUN/path;row=rec(p);want=pre['producer_source_sha256'].get(path)
        if want:assert row['sha256']==want
        arcsha=hashlib.sha256(zip.read(path)).hexdigest() if path in zip.namelist() else None
        if p.suffix!='.so':assert arcsha==row['sha256']
        row.update({'relative_path':path,'B192_pin_equal':row['sha256']==want if want else None,'archive_member':path,'archive_member_sha256':arcsha,'archive_equal':arcsha==row['sha256'] if arcsha else None})
        source_records.append(row)
    grid_archive_names=[x for x in zip.namelist() if x.startswith('cont2c/convergence/frozen_grid_n')]
grids={128:'7b83cf7baf606cb430b576f3661b81cad6c31a686000974a04ba616e5cc59bc9',160:'787d2d58c41e8b67d3d0f0273e46af281ac5ef4bb7bcfd1fef09b1cb844e211c',192:'e1959e1bbb66b5e27410daa3d3bdb0815885919f11af3a014d86a47f15b96301'}
inp=RUN/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'
with np.load(inp,allow_pickle=False) as f:original={k:f[k] for k in f.files}
rows=[]
for n,expected in grids.items():
    p=RUN/f'cont2c/convergence/frozen_grid_n{n}.npz';assert h(p)==expected
    with np.load(p,allow_pickle=False) as f:
        mismatch=[k for k,v in original.items() if k not in f.files or not np.array_equal(v,f[k])]
        assert not mismatch
        assert f['t'].shape==(n,) and f['W'].shape==(9,n,n)
        assert all(f[k].dtype==np.float64 and np.isfinite(f[k]).all() for k in ['t','w','U','V','W'])
        assert np.min(f['t'])>0
        row={**rec(p),'order':n,'archive_member':str(p.relative_to(RUN)),'original_input_mismatch':mismatch,'t_min':float(np.min(f['t'])),'t_max':float(np.max(f['t'])),'t_array_bytes_sha256':hashlib.sha256(f['t'].tobytes()).hexdigest(),'UU_weight_array_bytes_sha256':hashlib.sha256(f['W'].tobytes()).hexdigest(),'array_shapes_dtypes':{k:{'shape':list(f[k].shape),'dtype':str(f[k].dtype)} for k in ('t','w','U','V','W')}}
    with zipfile.ZipFile(ARCH) as z:assert hashlib.sha256(z.read(row['archive_member'])).hexdigest()==expected
    rows.append(row)
assert rows[0]['t_max']<=rows[2]['t_max'] and rows[1]['t_max']<=rows[2]['t_max']
checks=[
reference('completion/mixed_h/h0_backend.py',20,30,'OD guard accepts n128/n160/n192; no change.'),
reference('completion/mixed_h/h0_fused.cpp',17,37,'Native accepts positive n<=192; dynamic n*n indexing, no n parity restriction.'),
reference('completion/mixed_derivative/run.py',6,11,'Required frozen grid files already exist for all three orders.'),
reference('exact_weights/exact_laplace_weights.py',29,48,'Intended B96--B192 range; same Hermite density/contract definitions.'),
reference('completion/mixed_h/native.py',11,20,'OD nodes use roots_legendre and mapped double weights; unchanged FROZEN_INPUTS.'),
reference('cont2c/all94/run_all94.py',12,19,'Grid generator imports nodes/inputs from r10_blocks and exact_weights/contract from same module as OD.'),
reference('inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/src/r10_blocks.py',20,26,'Same inputs and mapped roots_legendre nodes definition as OD.'),
reference('cont2c/convergence/run_convergence.py',91,103,'Frozen files formed from same api nodes/U/V/W and model inputs. No generation invoked.'),
reference('completion/mixed_derivative/jvp.cpp',39,62,'Native JVP n<=4096 dynamic size; unchanged wide radial path.'),
reference('completion/mixed_h/od_run.py',21,43,'24+23 registry, fixed coefficient/phase and tau=z/v contract.'),
reference('completion/mixed_derivative/run.py',17,34,'Independent analytic time derivative, registry/phase matches; not D+Ddagger.'),
reference('completion/radial/DERIVATION.md',100,109,'B192 finite scalar enclosure: existing B128/B160 t_max smaller, same primitive inputs/z domain. Source support only, not error certificate.')]
authority={'schema':'WU088_R31AO_ALTERNATE_LADDER_AUTHORITY_V1','verdict':'SOURCE_AUTHORITY_COMPLIANT_UNEQUAL_LADDER','orders':[128,160,192],'archive':archive_record,'source_records':source_records,'grids':rows,'checks':checks,'all_original_model_input_arrays_equal':True,'producer_sources_and_B192_binaries_unchanged':True,'grid_generation_invoked':False,'producer_invoked':False,'native_order_regression_executed':False,'source_support_is_numerical_certification':False,'rigorous_reference_bound_available':False}
save('ALTERNATE_LADDER_AUTHORITY.json',authority)
# Inventory names and small IDENTITY records only; never matrix payloads at missing orders.
roots=sorted(p for p in Path('/root').iterdir() if p.is_dir() and (p.name.startswith('WU088') or p.name.startswith('wu088')) and p!=ROOT)
paths=[];hits=[];meta=[];errors=[];arc=[]
for root in roots:
    for base,dirs,names in os.walk(root):
        dirs[:]=[d for d in dirs if d not in {'.git','venv','.venv','__pycache__','node_modules','.pytest_cache'}]
        for name in names:
            p=Path(base)/name;paths.append(p)
            if any(f'b{n}_z0.75' in str(p).lower() for n in (128,160)):hits.append({'path':str(p),'bytes':p.stat().st_size})
            if name=='IDENTITY.json':
                try:
                    v=json.loads(p.read_text(),parse_float=Decimal,parse_int=Decimal)
                    if v.get('n') in (128,160) and Decimal(str(v.get('z')))==Decimal('0.75'):meta.append(rec(p))
                except (ValueError,TypeError,OSError):pass
paths+=list(Path('/root').glob('WU088*.zip'))
for p in sorted(set(p for p in paths if p.suffix.lower()=='.zip')):
    try:
        with zipfile.ZipFile(p) as z:
            members=z.namelist();found=[{'member':i.filename,'bytes':i.file_size,'crc32':f'{i.CRC:08x}'} for i in z.infolist() if any(f'b{n}_z0.75' in i.filename.lower() for n in (128,160))]
            arc.append({'path':str(p),'bytes':p.stat().st_size,'member_count':len(members),'member_names_sha256':hashlib.sha256('\n'.join(members).encode()).hexdigest(),'target_members':found})
    except (OSError,zipfile.BadZipFile) as e:errors.append({'path':str(p),'error':str(e)})
inventory={'schema':'WU088_R31AO_B128_B160_INVENTORY_V1','roots':[str(p) for p in roots],'files_examined':len(paths),'archive_member_tables':arc,'target_paths':hits,'target_identity_metadata':meta,'scan_errors':errors,'provider_metadata_file':'PROVIDER_METADATA_INVENTORY.json','orders':{'128':{'complete_output_found':False,'status':'NOT_FOUND_IN_ENUMERATED_METADATA_MEMBER_SCOPE'},'160':{'complete_output_found':False,'status':'NOT_FOUND_IN_ENUMERATED_METADATA_MEMBER_SCOPE'}},'raw_matrix_payload_accessed_at_B128_B160':False,'global_absence_proof':False,'title_search_zero_is_absence_proof':False,'provider_zip_member_coverage':'Locally recovered archives only; unmaterialized provider ZIPs not exhaustively inspected.'}
assert not hits and not meta and not any(x['target_members'] for x in arc)
save('B128_B160_OUTPUT_INVENTORY.json',inventory)
# Reuse the already consumed B192 authority as a finite reference, not new science.
od=RUN/'completion/mixed_h/od/B192_z0.75/ASSEMBLED_OD.npz'
jvp=RUN/'completion/mixed_derivative/B192_z0.75/ASSEMBLED.npz'
assert h(od)=='7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df'
assert h(jvp)=='53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87'
odi=json.loads(od.with_name('IDENTITY.json').read_text());ji=json.loads(jvp.with_name('IDENTITY.json').read_text())
orders={}
for row in rows:
    n=row['order']
    orders[str(n)]={'OD_identity':{k:odi[k] for k in ('source_identity','driver_sha256','model_sha256','scope')},'JVP_identity':{k:ji[k] for k in ('native','driver','contract')},'frozen_grid_sha256':row['sha256'],'same_geometry_decimal':'0.75'}
    orders[str(n)]['OD_identity']['t_sha256']=row['t_array_bytes_sha256']
    orders[str(n)]['JVP_identity']['grid']=row['sha256']
save('SOURCE_CONTRACT_LOCK.json',{'schema':'WU088_R31AO_ORDER_SOURCE_CONTRACT_LOCK_V1','orders':orders,'ordering_phase':'Unchanged CP4 FROZEN_INPUTS, 24+23 registry, independent JVP contract; source/shape/dtype locked.','OD_full_weight_hash_policy':'Full 3-plane W hash is recorded in OD identity and bound to unchanged grid/contract source. Existing JVP frozen W is the first (U,U) plane; no full-W regeneration performed in preflight.','source_records':source_records,'archive_sha256':archive_record['sha256']})
secondary=json.loads((ROOT/'research/r31al_z075_gate/ncp_followup_20260930/SECONDARY_REFINEMENT_PREREGISTRATION.json').read_text())
for pin in secondary['locked_files'].values():assert h(ROOT/pin['path'])==pin['sha256']
prereg=json.loads((ROOT/'research/r31ak_eight_node/ncp_followup_20260930/NEXT_VALIDATION_PREREGISTRATION.json').read_text())
components={'engine_sha256':h(ROOT/'research/r31ad_five_node/unit_cell_model.py'),'policy_sha256':h(ROOT/'research/r31ak_eight_node/MODEL_POLICY.json'),'helper_sha256':h(ROOT/'research/r31ak_eight_node/successor_policy.py'),'eight_node_manifest_sha256':h(ROOT/'research/r31ak_eight_node/ncp_followup_20260930/EIGHT_NODE_INPUT_MANIFEST.json')}
assert components==prereg['R31AK_model_components']
aggregate=hashlib.sha256(json.dumps(components,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert aggregate=='50a5f0eeda63d6e04795e301f6b07a41fd11a4b145e267cfc608261356d49b30'
save('FREEZE_IDENTITY.json',{'R31AK_aggregate_sha256':aggregate,'components':components,'B192_OD':rec(od),'B192_JVP':rec(jvp),'parent_primary_secondary_pins_unchanged':True,'R31AK_training_knots_unchanged':True,'z075_consumed_as_training':False})
diagnostic={'orders':[128,160,192],'ratios':['5/4','6/5'],'difference_arrays':['Q160-Q128','Q192-Q160'],'blocks':['O','D_col','D_row','dotO','K_derived_from_D'],'raw_dtype':'complex256','norm_arithmetic':'Rank<=2 Gram eigenvalue formula, Frobenius norm and max abs in longdouble; decimal strings retained. No source downcast.','rho':'d128160/d160192','rho_min':'log(5/4)/log(6/5)','positive_power_incompatible_if':'rho <= rho_min','positive_power_status':'CONDITIONAL_UNEQUAL_RATIO_ASYMPTOTIC_DIAGNOSTIC','E192_cond':'d160192/((6/5)^p-1)','E160_cond':'d160192/(1-(5/6)^p)','model_assumptions':['Q_n=Q_inf+C*n^(-p)','stable matrix error direction'],'monotonicity_proof':'Ratio equals integral_0^log(5/4) exp(p*t)dt / integral_-log(6/5)^0 exp(p*t)dt. Log derivative is positive-interval weighted mean minus negative-interval weighted mean, strictly >0. Limit p->0+ is log(5/4)/log(6/5), limit p->infinity is infinity.','direction_diagnostics':['normalized real Frobenius alignment','best positive scalar fit if defined','scalar-fit residual'],'direction_certification_threshold':None,'zero_increment_status':'INCREMENT_RATIO_UNDEFINED','rigorous':False,'p_cond_is_actual_quadrature_order':False,'verdict_stability':'PRIMARY then SECONDARY at each order, same Pareto metrics/rules/tol=1e-10. All three equal existing B192 pair -> B_ORDER_VERDICT_STABLE_OVER_128_160_192 only.','SOURCE_ACCURACY_BOUND':'SOURCE_ACCURACY_BOUND_UNAVAILABLE','rigorous_gate':'RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND'}
save('UNEQUAL_DIAGNOSTIC_CONTRACT.json',diagnostic)
pin_paths={p['path'] for p in secondary['locked_files'].values()}
pin_paths.update(str(p.relative_to(ROOT)) for p in [BASE/'unequal_order_ladder.py',BASE/'order_metadata_adapter.py',BASE/'compare_order_study.py',OUT/'ALTERNATE_LADDER_AUTHORITY.json',OUT/'SOURCE_CONTRACT_LOCK.json',OUT/'FREEZE_IDENTITY.json',OUT/'UNEQUAL_DIAGNOSTIC_CONTRACT.json'])
pins=[{'path':p,'sha256':h(ROOT/p),'bytes':(ROOT/p).stat().st_size} for p in sorted(pin_paths)]
pins += source_records + [rec(RUN/f'cont2c/convergence/frozen_grid_n{n}.npz') for n in grids] + [rec(od),rec(jvp)]
save('ORDER_COMPARATOR_LOCK.json',{'schema':'WU088_R31AO_PRE_OUTPUT_ORDER_COMPARATOR_LOCK_V1','source_contract_path':str((OUT/'SOURCE_CONTRACT_LOCK.json').relative_to(ROOT)),'files':pins,'baseline_verdicts':{'primary':'PARETO_SUPPORTED_AT_SELECTED_HOLDOUT','secondary':'REFINED_PARETO_SUPPORTED_AT_Z075'},'execution_authorized':False,'new_order_direct_output_accessed':False,'comparator_ready_for_existing_or_separately_authorized_data':True})
after={str(p.relative_to(RUN)):[p.stat().st_size,p.stat().st_mtime_ns] for p in RUN.rglob('*') if p.is_file()}
assert before==after
assert all(h(Path(p['path']))==p['sha256'] for p in source_records)
save('PRESERVATION_VERIFICATION.json',{'runtime_files':len(before),'metadata_changes':[],'pinned_source_input_binary_SHA_unchanged':True,'B192_raw_SHA_unchanged':True,'grid_generation':0,'science_producer_commands':0,'science_node_count':0,'new_native_builds':0,'R31AK_model_training_knot_mutations':0})
print(json.dumps({'authority':authority['verdict'],'archive_tables':len(arc),'files_examined':len(paths),'B128_B160_hits':0,'scope_condition_satisfied':True,'science_node_count':0}))
