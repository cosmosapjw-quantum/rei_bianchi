"""Read-only source/member audit; never imports a producer or evaluates a grid."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, zipfile, datetime, importlib.util, platform
import numpy as np, scipy, pytest

ROOT=Path('/root/WU088_HH_R31AN_FOLLOWUP_20260930')
OUT=ROOT/'research/r31an_reference_certification/ncp_preflight_20260930'
RUN=Path('/root/WU088_R31AL_Z075_RUNTIME_20260930')
ARC=Path('/root/WU088_R31Y_PRODUCER_INTAKE_20260929/WU088_HH_C21_TRANSFER_CP4_20260923.zip')
OUT.mkdir(exist_ok=False)
def sha(b): return hashlib.sha256(b).hexdigest()
def filehash(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1024*1024): h.update(b)
    return h.hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rec(p): return {'path':str(p),'sha256':filehash(p),'bytes':p.stat().st_size}
def command(name,argv):
    save(name+'.argv.json',{'argv':argv,'cwd':str(ROOT),'env_overrides':ENV})
    p=subprocess.run(argv,cwd=ROOT,env={**os.environ,**ENV},capture_output=True)
    (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
    (OUT/(name+'.exit')).write_text(str(p.returncode)+'\n')
    if p.returncode: raise RuntimeError(name+' failed')
    return {'argv_file':name+'.argv.json','stdout_file':name+'.stdout','stderr_file':name+'.stderr','exit_file':name+'.exit','exit_code':p.returncode}
ENV={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONPYCACHEPREFIX':'/tmp/wu088_r31an_pycache_20260930'}
save('ENVIRONMENT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'pytest':pytest.__version__,'longdouble':{'bytes':np.dtype(np.longdouble).itemsize,'significand_bits':np.finfo(np.longdouble).nmant+1},'raw_complex_dtype':str(np.dtype(np.clongdouble)),'CPU':next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'env_overrides':ENV,'compiler_not_invoked':True})
baseline={str(p.relative_to(RUN)):(p.stat().st_size,p.stat().st_mtime_ns) for p in RUN.rglob('*') if p.is_file()}
save('RUNTIME_METADATA_BEFORE.json',baseline)
prev=json.loads((ROOT/'research/r31al_z075_gate/authorized_z075_20260930/PRE_OUTPUT_LOCK.json').read_text())
extra=['cont2c/convergence/run_convergence.py','cont2c/convergence/CONTRACT.json','completion/radial/DERIVATION.md','completion/radial/CONTRACT.json','production/radial/DERIVATION.md']
authority=[]
archive_identity=rec(ARC)
assert archive_identity['sha256']=='c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9'
with zipfile.ZipFile(ARC) as z:
    for s in list(prev['producer_source_sha256'])+extra:
        p=RUN/s; row=rec(p); expected=prev['producer_source_sha256'].get(s)
        row.update({'relative_path':s,'B192_expected_sha256':expected,'B192_identity_equal':expected==row['sha256'] if expected else None,'archive_member':s,'archive_member_sha256':sha(z.read(s)) if s in z.namelist() else None})
        row['archive_equal']=row['archive_member_sha256']==row['sha256'] if row['archive_member_sha256'] else None
        if expected: assert row['B192_identity_equal']
        if p.suffix!='.so': assert row['archive_equal']
        row['authority_role']='EXISTING_B192_RUNTIME_BINARY_PIN' if p.suffix=='.so' else 'RECOVERED_ARCHIVE_SOURCE_OR_INPUT'
        authority.append(row)
        if p.suffix in ('.py','.cpp','.json','.md'):
            q=OUT/'source_snapshot'/s;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
save('SOURCE_AUTHORITY.json',{'archive':archive_identity,'runtime':str(RUN),'sources':authority,'producer_imported':False,'all_B192_source_binary_input_pins_equal':True})
def evidence(s,start,end,claim):
    lines=(RUN/s).read_text().splitlines()
    return {'source_path':str(RUN/s),'archive':str(ARC),'member':s,'sha256':filehash(RUN/s),'lines':[start,end],'numbered_source':'\n'.join(f'{i}: {lines[i-1]}' for i in range(start,min(end,len(lines))+1)),'observation':claim}
checks=[
evidence('completion/mixed_h/od_run.py',8,19,'OD uses grid(n), H0Fused; mixed OG only saved by OD driver.'),
evidence('completion/mixed_h/h0_backend.py',20,30,'Python OD hard limit 0<t.size<=192; B256 rejected unchanged.'),
evidence('completion/mixed_h/h0_fused.cpp',17,37,'Native OD n>192 returns -501; dynamic n*n indexing, no grid parity/divisibility requirement observed in this call path.'),
evidence('completion/mixed_derivative/run.py',6,11,'JVP requires preexisting frozen_grid_n{n}.npz; CLI does not generate missing grids.'),
evidence('completion/mixed_h/native.py',11,20,'Mapped scipy roots_legendre binary64 nodes/weights; exact Hermite weights contracted from unchanged FROZEN_INPUTS.'),
evidence('exact_weights/exact_laplace_weights.py',29,48,'Binary64 Hermite density and contraction; declared intended range frozen B96--B192; exact analytic formula is not exact floating arithmetic.'),
evidence('cont2c/convergence/run_convergence.py',91,103,'Historical generator uses shared API and create-only equality; no B144/B256 preparation run authorized here.'),
evidence('completion/mixed_derivative/native.py',10,37,'Content-addressed source cache and strict ABI probe; input t,W,norm binary64; geometry/output longdouble/clongdouble.'),
evidence('completion/mixed_derivative/jvp.cpp',39,62,'Native JVP buffer n<=4096, nw=9*n*n; no n parity/divisibility restriction observed. Kernel capacity does not supply required grid/source authority.'),
evidence('completion/mixed_h/od_run.py',21,39,'Frozen 24+23 registry, coefficients, channel phase, tau=z/v and independent directional D assembly.'),
evidence('completion/mixed_derivative/run.py',17,34,'Same registry/phase with independent analytic z-JVP and time derivative v*zJVP + phase derivative, not D+Ddagger.'),
evidence('completion/radial/radial_wide.cpp',7,73,'Longdouble significand>=64, binary128 series arithmetic for |Im x|>2; compensated series and tail stop, fixed FE_TONEAREST.'),
evidence('completion/radial/radial_wide.cpp',91,148,'Large Re>=64 Boys tail omission; scalar domain guards and maximum derivative order2.'),
evidence('completion/radial/radial_wide.cpp',150,198,'Shared sector Re>=-0.5; terminating even polynomials; direct/Kummer branch otherwise, finite result guards.'),
evidence('completion/radial/DERIVATION.md',100,109,'B192 domain enclosure only; other grids require their own t_max enclosure, not unlimited order authority.'),
evidence('completion/mixed_h/h0_backend.py',6,19,'Source-addressed cache; strict compiler flags and precision check; no binary/cache changes made.'),
evidence('foreign_analytic/build_native.py',24,58,'JVP cache key includes source/build environment/compiler/headers; order-independent binary identity; no builds invoked.')]
save('PRODUCER_FEASIBILITY.json',{'verdict':'REFERENCE_ORDER_INPUT_BLOCKED','source_modification_permitted':False,'orders':{'144':{'OD_static_capacity':'ACCEPTED_BY_SIZE_GUARD_NOT_EXECUTED','JVP':'FROZEN_GRID_MISSING','complete_producer_contract_verified':False},'256':{'OD':'REJECTED_BY_PYTHON_AND_NATIVE_HARD_LIMIT','JVP':'FROZEN_GRID_MISSING','complete_producer_contract_verified':False}},'grid_files_present':[rec(p) for p in sorted((RUN/'cont2c/convergence').glob('frozen_grid_n*.npz'))],'support_closed':False,'checks':checks,'no_grid_generation':True,'no_producer_or_native_command':True,'new_science_node_count':0})
# Inventory only names and IDENTITY.json metadata. No new-order matrix payloads read.
roots=sorted(p for p in Path('/root').iterdir() if p.is_dir() and (p.name.startswith('WU088') or p.name.startswith('wu088')) and p!=ROOT)
prune={'.git','venv','.venv','__pycache__','node_modules','.pytest_cache'}
files=[];target_paths=[];metadata_hits=[];archives=[];errors=[]
for root in roots:
    for base,dirs,names in os.walk(root):
        dirs[:]=[d for d in dirs if d not in prune]
        for name in names:
            p=Path(base)/name;files.append(p)
            lower=str(p).lower()
            if ('b144_z0.75' in lower or 'b256_z0.75' in lower): target_paths.append({'path':str(p),'bytes':p.stat().st_size})
            if name=='IDENTITY.json':
                try:
                    v=json.loads(p.read_text());n=v.get('n');zz=v.get('z')
                    if n in (144,256) and zz is not None and str(zz) in ('0.75','0.750'): metadata_hits.append({'identity':rec(p),'metadata':v})
                except (ValueError,OSError): pass
for p in Path('/root').glob('WU088*.zip'): files.append(p)
zipfiles=sorted(set(p for p in files if p.suffix.lower()=='.zip'))
for p in zipfiles:
    try:
        with zipfile.ZipFile(p) as z:
            names=z.namelist();hits=[{'member':x.filename,'bytes':x.file_size,'crc32':f'{x.CRC:08x}'} for x in z.infolist() if ('b144_z0.75' in x.filename.lower() or 'b256_z0.75' in x.filename.lower())]
            archives.append({'path':str(p),'bytes':p.stat().st_size,'member_count':len(names),'member_name_sequence_sha256':sha('\n'.join(names).encode()),'target_members':hits,'frozen_grid144_256_members':[n for n in names if 'frozen_grid_n144' in n or 'frozen_grid_n256' in n],'archive_sha256':archive_identity['sha256'] if p==ARC else (filehash(p) if hits else None)})
    except (OSError,zipfile.BadZipFile) as e: errors.append({'path':str(p),'error':str(e)})
save('LOCAL_ARCHIVE_ORDER_INVENTORY.json',{'roots':[str(x) for x in roots],'pruned_directory_names':sorted(prune),'files_examined':len(files),'archives':archives,'target_paths':target_paths,'target_identity_metadata':metadata_hits,'errors':errors,'direct_new_order_matrix_payload_accessed':False,'verdict':'NO_COMPLETE_TARGET_FOUND_IN_ENUMERATED_LOCAL_AND_ARCHIVE_NAMES_METADATA','absence_claim_scope':'Enumerated paths/member names only; not provider-wide or differently labeled content absence proof.'})
prereg=json.loads((ROOT/'research/r31ak_eight_node/ncp_followup_20260930/NEXT_VALIDATION_PREREGISTRATION.json').read_text())
component_paths={'engine_sha256':'research/r31ad_five_node/unit_cell_model.py','policy_sha256':'research/r31ak_eight_node/MODEL_POLICY.json','helper_sha256':'research/r31ak_eight_node/successor_policy.py','eight_node_manifest_sha256':'research/r31ak_eight_node/ncp_followup_20260930/EIGHT_NODE_INPUT_MANIFEST.json'}
components={k:filehash(ROOT/v) for k,v in component_paths.items()}
assert components==prereg['R31AK_model_components']
aggregate=sha(json.dumps(components,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
assert aggregate=='50a5f0eeda63d6e04795e301f6b07a41fd11a4b145e267cfc608261356d49b30'
od=RUN/'completion/mixed_h/od/B192_z0.75/ASSEMBLED_OD.npz';jvp=RUN/'completion/mixed_derivative/B192_z0.75/ASSEMBLED.npz'
assert filehash(od)=='7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df'
assert filehash(jvp)=='53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87'
def headers(p):
    out={}
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n not in ('O.npy','D_col.npy','D_row.npy','dotO.npy'): continue
            with z.open(n) as f:
                ver=np.lib.format.read_magic(f)
                read_header=np.lib.format.read_array_header_1_0 if ver==(1,0) else np.lib.format.read_array_header_2_0
                shape,fortran,dtype=read_header(f)
            out[n[:-4]]={'shape':list(shape),'dtype':str(dtype),'fortran_order':fortran}
    return out
save('FREEZE_IDENTITY_VERIFICATION.json',{'R31AK_aggregate_sha256':aggregate,'component_files':component_paths,'components':components,'B192_OD':{**rec(od),'array_headers_only':headers(od)},'B192_JVP':{**rec(jvp),'array_headers_only':headers(jvp)},'B192_reused_without_reassembly':True,'interpolation_model_frozen':True,'training_knot_state_unchanged':True,'z075_training_consumed':False,'SOURCE_ACCURACY_BOUND':'SOURCE_ACCURACY_BOUND_UNAVAILABLE'})
rigor=[
{'component':'epsilon_order','status':'MISSING','available':'Mapped Gauss-Legendre / exact analytic Hermite weight formulas and finite-order observations.','missing':'Uniform transformed-integrand quadrature remainder including endpoint/infinite-tail behavior for all O/D/dotO entries; no project-authoritative bound at B192.','evidence':[evidence('completion/mixed_h/native.py',16,20,'Finite-order quadrature construction, not continuum bound.'),evidence('exact_weights/exact_laplace_weights.py',29,48,'Density/weight formula, no integration remainder certificate.')]},
{'component':'epsilon_special_function','status':'PARTIAL_MATH_AUTHORITY_NO_COMPLETE_MATRIX_BOUND','available':'Exact-arithmetic hypergeometric tail-ratio bound and large-positive-Re Boys tail bounds.','missing':'Outward-rounded evaluation and propagated uniform mixed block bound through prefactors/fields/weight contractions. Numerical scalar controls are sampled accuracy evidence.','evidence':[evidence('completion/radial/DERIVATION.md',52,79,'Tail derivation explicitly excludes all floating-point operations proof.'),evidence('completion/radial/radial_wide.cpp',33,73,'Tail stop evaluated in nearest rounding, not interval enclosure.')]},
{'component':'epsilon_roundoff','status':'MISSING','available':'Longdouble/binary128 branch definitions, precision and FE_TONEAREST checks, strict compiler flags, compensated sums.','missing':'Certified library transcendental error, node/weight generation rounding, binary128-to-longdouble casts and accumulated operation-level enclosure; no outward-rounded interval.','evidence':[evidence('completion/radial/radial_wide.cpp',7,73,'Precision and compensated arithmetic are not error certificates.'),evidence('completion/mixed_h/h0_fused.cpp',7,20,'Compensated nearest-rounded accumulation, not outward rounding.'),evidence('completion/mixed_derivative/jvp.cpp',8,9,'Compensated complex sum.')]},
{'component':'epsilon_assembly','status':'MISSING','available':'Unchanged registry/phase and longdouble complex orbital contraction; sumabs diagnostics.','missing':'Certified coefficient/phase/transcendental errors and assembled block norm upper bounds. sumabs does not contain all errors and is not outward rounded.','evidence':[evidence('completion/mixed_h/od_run.py',25,38,'Longdouble sum/phase, diagnostic sumabs.'),evidence('completion/mixed_derivative/run.py',17,30,'Longdouble phase and analytic derivative assembly.')]}]
save('RIGOROUS_CERTIFICATION_FEASIBILITY.json',{'verdict':'RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND','decomposition':'epsilon_ref <= epsilon_order + epsilon_special_function + epsilon_roundoff + epsilon_assembly','components':rigor,'epsilon_ref_upper_bound':None,'historical_H_anchors':'FINITE_ORDER_H_EVIDENCE_NOT_MIXED_OD_DOTO_CERTIFICATE','rigorous':False,'continuum_certified':False,'source_certified':False,'SOURCE_ACCURACY_BOUND':'SOURCE_ACCURACY_BOUND_UNAVAILABLE'})
pins=['research/r31an_reference_certification/reference_certification.py','research/r31ak_eight_node/metadata_adapter.py','research/r31ak_eight_node/compare_future_holdout.py','research/r31al_z075_gate/compare_secondary_refinement.py','research/r31ak_eight_node/ncp_followup_20260930/FROZEN_HOLDOUT_PREDICTIONS.npz','research/r31al_z075_gate/ncp_followup_20260930/Z075_COARSE_PREDICTION.npz']
# Only existing exact artifacts are pinned. No future-order producer/comparator implementation is invented.
pins=[p for p in pins if (ROOT/p).exists()]
pins += ['research/r31al_z075_gate/ncp_followup_20260930/Z075_REFINEMENT_PRE_OUTPUT_LOCK.json','research/r31ak_eight_node/ncp_followup_20260930/FROZEN_HOLDOUT_DECISION_RULE.json','research/r31al_z075_gate/ncp_followup_20260930/SECONDARY_REFINEMENT_PREREGISTRATION.json']
save('ORDER_COMPARATOR_LOCK.json',{'status':'SPECIFICATION_AND_EXISTING_HELPERS_LOCKED__ORDER_INPUT_BLOCKED','orders':[144,192,256],'ratio':'4/3','blocks':['O','D_col','D_row','dotO'],'geometry_z_decimal':'0.75','tau_definition':'unchanged producer z/velocity','required_raw_differences':['Q192-Q144','Q256-Q192'],'difference_policy':'Keep complex256 raw inputs and raw differences without symmetrization or precision downgrade; preserve raw dtype, spectral 2-norm, max abs, and source/order identity. Numerical norm evaluation requires an explicitly pinned wide-precision implementation before any future direct-order access.','derived_K':'(D_col-D_row.conj().T)/2','rho_norm':'d192256/d144192 if positive finite','p_norm':'log(d144192/d192256)/log(4/3) only if d144192>d192256>0','p_norm_is_actual_quadrature_order':False,'conditional_assumptions':['Q_n=Q_inf+C*n^(-p)','stable matrix error direction'],'E192_cond':'d192256/(1-(3/4)^p)','E256_cond':'d192256/((4/3)^p-1)','conditional_status':'CONDITIONAL_ASYMPTOTIC_DIAGNOSTIC','rigorous':False,'B256_verdict_replay':'Use frozen parent PRIMARY first, SECONDARY second; both unchanged -> B_ORDER_VERDICT_STABLE only.','pins':[rec(ROOT/p) for p in pins],'executable_full_order_array_comparator_ready':False,'future_pre_output_obligations':['Lock exact order-identity metadata adapter and raw wide-precision array-difference/norm wrapper before any future B144/B256 output access.','No output-driven changes to model, rule, tolerance or comparator.'],'scope_created':False,'execution_authorized':False})
commands={}
commands['COMPILE']=command('COMPILE',[sys.executable,'-m','py_compile','research/r31an_reference_certification/reference_certification.py','research/r31an_reference_certification/test_reference_certification.py'])
commands['FOCUSED_TEST']=command('FOCUSED_TEST',[sys.executable,'-m','pytest','-q','research/r31an_reference_certification/test_reference_certification.py','--junitxml='+str(OUT/'JUNIT.xml')])
spec=importlib.util.spec_from_file_location('r31an',ROOT/'research/r31an_reference_certification/reference_certification.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.common_reference_radius([.05250496632934204,.05457284174805037],[.3723284019854093,.3880297823244174]);s=m.common_reference_radius([.05250496632934204,.05457284174805037],[.10963738645582422,.1423934281278521])
save('POLICY_ALGEBRA_REPLAY.json',{'ladder':m.study_contract(),'primary_sensitivity':p,'secondary_sensitivity':s,'per_metric_budgets':{'primary_K':.15991171777803362,'primary_Dmax':.16672847023818352,'secondary_K':.028566210013241087,'secondary_Dmax':.04391029313990087},'joint_open_budget':.028566210013241087,'units':'/t_a','actual_B192_error_estimate':False,'asymptotic_diagnostic_on_science_data':'NOT_PERFORMED_NO_ORDER_DATA','raw_order_differences_created':False,'B256_alternate_reference_verdict':'NOT_EVALUATED','new_order_grids_or_matrices_evaluated':False})
after={str(p.relative_to(RUN)):(p.stat().st_size,p.stat().st_mtime_ns) for p in RUN.rglob('*') if p.is_file()}
assert baseline==after
assert all(filehash(Path(x['path']))==x['sha256'] for x in authority)
save('PRESERVATION_VERIFICATION.json',{'runtime_files_before':len(baseline),'runtime_files_after':len(after),'runtime_metadata_changed_paths':[],'runtime_added_paths':[],'all_pinned_sources_inputs_binaries_sha_unchanged':True,'B192_OD_SHA_unchanged':filehash(od),'B192_JVP_SHA_unchanged':filehash(jvp),'science_producer_command_count':0,'science_node_count':0,'new_native_builds':0,'new_order_grid_generation':0})
save('COMMANDS.json',commands)
print(json.dumps({'source_verdict':'REFERENCE_ORDER_INPUT_BLOCKED','rigorous_verdict':'RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND','local_target_hits':len(target_paths),'metadata_target_hits':len(metadata_hits),'archives_scanned':len(archives),'archive_target_hits':sum(len(x['target_members']) for x in archives),'archive_scan_errors':len(errors),'focused_exit':commands['FOCUSED_TEST']['exit_code'],'runtime_preserved':True,'science_node_count':0}))
