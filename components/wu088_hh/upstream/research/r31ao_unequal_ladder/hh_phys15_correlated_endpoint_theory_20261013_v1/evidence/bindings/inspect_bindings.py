#!/usr/bin/env python3
"""Read-only PHYS15 binding inspection; exact input algebra, no source/root replay."""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import hashlib
import json
import struct
import zipfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
BASE = WORK / 'HH_PHYS14_20261012_v1'
OLD = WORK / 'phys14_intake/ncp07/HH_PHYS07_NCP_LOCAL_20261011_v1'
ARCHIVE = WORK / 'phys14_intake/WU088_HH_PHYS07_NCP_LOCAL_20261011_v1.zip'
ARCHIVE_SHA = '4ea6b7dbbc714493ac85f944a65a353a1ee75abf5742c3e7ce65a7df56cc3465'

def load(path):
    return json.loads(Path(path).read_text())

def bits(s):
    return Q(struct.unpack('>d', bytes.fromhex(s))[0])

def interval(d):
    if 'exact' in d:
        return tuple(Q(*map(int, d['exact'][k])) for k in ('lo', 'hi'))
    return tuple(bits(d[k + '_bits']) for k in ('lo', 'hi'))

def dec(x, direction):
    with localcontext() as c:
        c.prec = 18
        c.rounding = direction
        return str(Decimal(x.numerator) / Decimal(x.denominator))

def exact(x):
    return [str(x.numerator), str(x.denominator)]

def emit_iv(pair):
    lo, hi = pair
    return {'exact': {'lo': exact(lo), 'hi': exact(hi)},
            'outward_decimal': [dec(lo, ROUND_FLOOR), dec(hi, ROUND_CEILING)]}

def identity(path):
    path = Path(path)
    b = path.read_bytes()
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

stages = {}
for name in ('first_half', 'full'):
    prefix = BASE / 'inputs/ncp07/results' / name
    box = load(prefix / 'SOURCE_BOX.json')
    pre = load(prefix / 'PREBE.json')
    domain = load(prefix / 'C2_DOMAIN.json')
    diag = load(prefix / 'UNIFORM_DIAGNOSTICS.json')
    common = load(prefix / 'COMMON_INPUT_SCOPE.json')
    stages[name] = {'box': box, 'pre': pre, 'domain': domain,
                    'diag': diag, 'common': common}

one, two = stages['first_half'], stages['full']
n1, n2 = [bits(s['box']['nH_bits']) for s in (one, two)]
f1, f2 = [bits(s['box']['nHe_stored_bits']) / bits(s['box']['nH_bits']) for s in (one, two)]
h1, hF = [bits(s['box']['dt_bits']) for s in (one, two)]
M1, MF = [bits(s['pre']['fl_dt_SOURCE_bits']) for s in (one, two)]

assert h1 == 625000000 and hF == 2*h1
assert MF == 2*M1
assert one['common'] == two['common']
assert one['domain']['X'] == two['domain']['X']
assert one['diag']['center'] == two['diag']['center']
assert one['diag']['radius'] == two['diag']['radius']
shared_leaf_keys = ['energy_bits', 'sigma_bits', 'heat_bits', 'fHe_bits', 'Hmean_bits']
assert all(one['box'][k] == two['box'][k] for k in shared_leaf_keys)
assert load(BASE/'inputs/ncp07/results/first_half/NATIVE_CONSTANT_LEAVES.json') == load(BASE/'inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json')

# The same exact stored COMMON Jet payload appears after the duration header.
bhalf = (BASE/'inputs/ncp07/results/first_half/prebe_input_words.bin').read_bytes()
bfull = (OLD/'results/full/prebe_input_words.bin').read_bytes()
assert len(bhalf) == len(bfull) == 4090360
assert bhalf[:32] == bfull[:32] and bhalf[40:] == bfull[40:]
assert struct.unpack('<5d', bhalf[:40]) == (1e-14,1e-14,1e-14,160000000000.0,625000000.0)
assert struct.unpack('<5d', bfull[:40]) == (1e-14,1e-14,1e-14,160000000000.0,1250000000.0)

# Restore exactly two newly needed small immutable source members.
assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA
manifest = {r['path']:r for r in load(OLD/'MANIFEST.json')['files']}
extra_records = []
with zipfile.ZipFile(ARCHIVE) as z:
    for rel in ('results/first_half/SOURCE_CENTRE.json', 'candidate/src/hh_primary_extension.rs'):
        member = 'HH_PHYS07_NCP_LOCAL_20261011_v1/' + rel
        matches = [i for i in z.infolist() if i.filename == member]
        assert len(matches) == 1
        data = z.read(matches[0])
        prior = manifest[rel]
        assert len(data) == prior['bytes']
        assert hashlib.sha256(data).hexdigest() == prior['sha256']
        assert data == (OLD/rel).read_bytes()
        target = HERE/'extra_inputs'/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == data
        else:
            with target.open('xb') as f:
                f.write(data)
        extra_records.append({**identity(target), 'archive_member':member,
                              'original_manifest_sha256':prior['sha256'],
                              'archive_member_equals_existing_intake':True})

thermo = load(BASE/'inputs/phys13/THERMO_RESULTS.json')
advance = load(BASE/'results/advance01/ADVANCE_RESULTS.json')
root_boxes = {r['stage']:list(map(interval,r['root_image']['intervals'])) for r in thermo['rows']}
root_boxes['second_half'] = list(map(interval,advance['root_certificate']['root_image']))
hull = [(min(b[i][0] for b in root_boxes.values()), max(b[i][1] for b in root_boxes.values())) for i in range(4)]
X = list(map(interval,one['domain']['X']))
assert all(X[i][0] < hull[i][0] <= hull[i][1] < X[i][1] for i in range(4))
df = f2-f1
assert df > 0
Nlo, Nhi = 1+hull[1][0]+2*hull[2][0], 1+hull[1][1]+2*hull[2][1]
Pilo = 1+hull[0][0]+f1*Nlo
Pihi = 1+hull[0][1]+f1*Nhi
shift = (hull[3][0]*df*Nlo/Pihi, hull[3][1]*df*Nhi/Pilo)
pulled_w = (hull[3][0]+shift[0],hull[3][1]+shift[1])
assert X[3][0] < pulled_w[0] <= pulled_w[1] < X[3][1]

needed = [
 'src/phys14_advance.py','SCIENTIFIC_CONTRACT.md','review/DECISION.json',
 'review/GEOMETRY_REVIEW.json','inputs/phys09/PROJECTED_RESULTS.json',
 'inputs/phys11/CARRY_RESULTS.json','inputs/phys13/THERMO_RESULTS.json',
 'inputs/phys13/DECISION.json','results/advance01/ADVANCE_RESULTS.json',
 'inputs/ncp07/candidate/src/phys04_transport.rs',
 'inputs/ncp07/candidate/src/phys04_mixed.rs',
 'inputs/ncp07/candidate/src/ft03_interval.rs',
 'inputs/ncp07/candidate/src/paired_runtime.rs',
 'inputs/ncp07/candidate/src/coupled_primary.rs',
 'inputs/ncp07/src/sourcebox.rs',
 'inputs/ncp07/results/full/SOURCE_CENTRE.json',
 'inputs/ncp07/results/first_half/prebe_input_words.bin']
for name in ('first_half','full'):
    needed += ['inputs/ncp07/results/'+name+'/'+fn for fn in (
        'SOURCE_BOX.json','SOURCE_BOX_COMPONENTS.json','SOURCE_CENTRE_COMPONENTS.json',
        'C2_DOMAIN.json','UNIFORM_DIAGNOSTICS.json','PREBE.json','COMMON_INPUT_SCOPE.json',
        'NATIVE_CONSTANT_LEAVES.json')]

constant_rows = {}
for name,s in stages.items():
    b=s['box']; const={k:{'bits':b[k],'exact':exact(bits(b[k]))} for k in ('nH_bits','nHe_stored_bits','fHe_bits','Hmean_bits','dt_bits')}
    const['fhat']={'exact':exact(bits(b['nHe_stored_bits'])/bits(b['nH_bits']))}
    const['M']={'bits':s['pre']['fl_dt_SOURCE_bits'],'exact':exact(bits(s['pre']['fl_dt_SOURCE_bits']))}
    constant_rows[name]=const

decision=load(BASE/'review/DECISION.json')
record={
 'schema':'WU088_HH_PHYS15_ASSUMPTIONS_AND_BINDINGS_V1',
 'created_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Read-only binding and constructive source-normalization derivation for same-COMMON Full vs actual two-half theory.',
 'source_root':str(BASE), 'source_commit':'087a16f28d0ee4fc7ae74ae50bfcafe578716e85',
 'git_read_receipt':'GIT_HEAD_AND_ROOT_READ.json',
 'inherited_premises':decision['inherited_premises']+[
    'The Full C2/root and derivative enclosures inherited through PHYS09/13 remain valid for the same geometric coefficient selection.',
    'One joint alpha fixes COMMON gas/photon/guard state, captured physical leaves and their source graph, common isotropic rho, and normalized ray weights; the same alpha is used in all three stages and throughout global lambda,b in [0,1]^2.'],
 'exact_bindings':{
    'COMMON_SCOPE_JSON_equal':True, 'COMMON_binary_payload_after_5word_header_equal':True,
    'COMMON_payload_sha256':hashlib.sha256(bhalf[40:]).hexdigest(),
    'COMMON_full_frame':identity(OLD/'results/full/prebe_input_words.bin'),
    'COMMON_half_frame':identity(BASE/'inputs/ncp07/results/first_half/prebe_input_words.bin'),
    't0_seconds':160000000000,'h_seconds':625000000,'t1_seconds':160625000000,'t2_seconds':161250000000,
    'Full_dt_equals_two_h':True,'M_Full_equals_two_Mhalf':True,
    'total_birth_capture_defect_exact':['0','1'],
    'X_equal':True,'gas_centres_equal':True,'radii_equal':True,
    'centre':[0.915,0.3,0.6,13.5],'radius':[0.015,0.01,0.01,0.5],
    'shared_leaf_keys':shared_leaf_keys,'native_constant_leaves_equal':True,
    'second_half_endpoint_physical_leaves':'Exactly the original Full SOURCE_BOX leaves; shared nonphoto/q functions, but duration h and new incoming.',
    'source_centre_semantics':'Gas-centre evaluation at the same c=(0.915,0.3,0.6,13.5), over whole global lambda,b; nonphoto/q have no explicit lambda,b.',
    'constants':constant_rows,
    'n1_over_n2':{'exact':exact(n1/n2)},
    'fhat1_minus_fhat2':emit_iv((f1-f2,f1-f2)),
    'sigma_active_HI_nodes':list(range(16,33)),
    'helium_photo_sigma_all_zero':all(bits(row[1])==bits(row[2])==0 for row in two['box']['sigma_bits']),
    'energy_nodes_count':33,'source_birth_node':24,
    'captured_heat_policy':'Read SOURCE_BOX heat_bits; preserve captured fl(E_j-CHI_a) leaves.'},
 'exact_source_bridge':{
    'e_i':'x+fhat_i*(y+2*z)', 'Pi_i':'1+fhat_i+e_i', 'T_i':'C_T*w/Pi_i',
    'aligned_g_star':'(x,y,z,w*Pi_2/Pi_1)',
    'temperature_identity':'T_2(g_star)=T_1(g)',
    'r':'n1*e1/(n2*e2)',
    'FT03_species':'F_np_1[0:3](g)=r*F_np_2[0:3](g_star)',
    'FT03_thermal':'F_np_1[w](g)=r*F_np_2[w](g_star)+n1*e1*(fhat1-fhat2)*k_wHe(y,z,T_1)',
    'HH':'q_1(g)=(n1/n2)*q_2(g_star)',
    'conditions':'Exact-real fixed-leaf photo-off FT03 and HH sources with common fit/constants. Active photo and -2H*w are added separately. k_wHe is given in ASSUMPTIONS_AND_BINDINGS_KO.md.',
    'hull':{k:[emit_iv(v) for v in b] for k,b in root_boxes.items()},
    'joint_root_hull':[emit_iv(v) for v in hull],
    'positive_w_pullback_shift_eV_per_H':emit_iv(shift),
    'pulled_hull_w':emit_iv(pulled_w),
    'pullback_upper_X_margin':emit_iv((X[3][1]-pulled_w[1],X[3][1]-pulled_w[1])),
    'all_root_hull_and_pullback_segments_inside_original_X':True,
    'whole_closed_X_pullback_invariance_claimed':False,
    'basis':['derived from original source graph','exact input/domain algebra checked'],
    'new_source_transcendental_evaluations':0},
 'constructive_corrections':[
    {'target':'same-alpha comparison','observation':'Each existing first-stage result allows a fixed coefficient selection; comparing independent selections loses path correlation.','action':'Define one joint alpha and restrict both old stages and the PHYS14 continuation to its geometric lift.'},
    {'target':'Full source vs second-half source','observation':'nH,nHe,nonphoto,q and endpoint constants are identical; dt and photon incoming differ.','action':'Cancel the shared source first and use a divided difference on the convex root hull.'},
    {'target':'first_half vs Full source time dependence','observation':'nH differs and exact fhat differs by about 6.95e-18.','action':'Use the exact temperature-aligned density/readout bridge or a centre-anchored two-source difference retaining the fhat term.'},
    {'target':'birth chronology','observation':'M_Full=2*M_half exactly while first-half births undergo an extra remap and absorption.','action':'Set total amount capture defect to exact zero; retain age/remap/absorption of first injection.'},
    {'target':'readout difference','observation':'Full and second_half share exact fhat2,C_T,nH2.','action':'Use delta_e=delta_x+fhat2*(delta_y+2*delta_z), delta_T=C_T*(Pi_F*delta_w-w_F*delta_e)/(Pi_F*Pi_2); n_e difference=nH2*delta_e.'},
    {'target':'source centre availability','observation':'first_half SOURCE_CENTRE.json omitted from PHYS14 core but exists in pinned NCP07 archive.','action':'Restore exact member into extra_inputs; no new source evaluation.'}],
 'source_domains':{'X':[emit_iv(x) for x in X],
    'C2_status':{k:s['domain']['status'] for k,s in stages.items()},
    'physical_incoming_nonnegative':True,
    'parameter_extension':'Underlying same fixed-leaf C2 real family in a small open neighbourhood of [0,1]^2; positive source-aligned denominators.',
    'geometric_reuse':'PHYS14 review/GEOMETRY_REVIEW.json establishes each captured ray enclosure contains rho(h) or rho(2h), and normalized geometric weights. Only that selected linked subfamily is used.',
    'spectral_guard':'Keep all 33 nodes and total lower guard, including signed derivative tails. Geometric remap is a common linear ray map; absorption denominator is ray-independent.'},
 'newly_restored_inputs':{'archive':identity(ARCHIVE),'members':extra_records,'manifest':identity(OLD/'MANIFEST.json')},
 'selected_input_identities':[identity(BASE/p) for p in needed],
 'genuinely_missing_inputs_for_current_derived_comparison':[],
 'remaining_research_obligations':[
    'Assemble correlated gas and photon endpoint defect with the selected joint alpha and positive denominator family.',
    'Enclose the needed averaged Jacobian/source-time contribution on the original convex root hull and propagate to T/e/w.',
    'Use independent review for newly derived defect equations and any new numerical enclosure.'],
 'execution_accounting':{'scientific_source_calls':0,'native_calls':0,'root_or_history_replays':0,'cloud_writes':0,'local_operation':'Targeted file reads, archive member extraction and exact rational identity/domain checks only.'}}

# Root-file identity uses current provider object identities, not a re-download loop.
git=load(HERE/'GIT_HEAD_AND_ROOT_READ.json')
for item in git['root_documents']:
    b=(BASE/'publication_overlay'/item['path']).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert blob==item['git_blob_sha']
    item['existing_PHYS14_overlay_matches_remote_blob']=True
    item['local_sha256']=hashlib.sha256(b).hexdigest()
(HERE/'GIT_HEAD_AND_ROOT_READ.json').write_text(json.dumps(git,ensure_ascii=False,indent=2)+'\n')
(HERE/'BINDINGS.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'COMPLETE','selected_files':len(needed),'extra_members':len(extra_records),'M_full_minus_2Mhalf':'0','fhat1_minus_fhat2':record['exact_bindings']['fhat1_minus_fhat2']['outward_decimal'],'w_pullback_shift':record['exact_source_bridge']['positive_w_pullback_shift_eV_per_H']['outward_decimal'],'pullback_inside_X':True},indent=2))
