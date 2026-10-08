#!/usr/bin/env python3
"""Actual endpoint checks, stored-sample algebra and strict receiver refusals."""
from pathlib import Path
from fractions import Fraction as F
import copy,hashlib,json,math,struct,sys
from packet import digest,check,require_certified_family,GAMMA_UNIT,ENERGY_UNIT,KIND
from upstream_bridge.vendor.source_transfer import State,Moments,project,spectral_moments,fixed_difference,ContractError

ROOT=Path(__file__).resolve().parents[3]
raw=json.loads((ROOT/'observed/observation.raw.json').read_text())
pins=json.loads((ROOT/'receipts/INTAKE.json').read_text())
for name,pin in pins['payload'].items():
    b=(ROOT/'payload'/name).read_bytes()
    assert len(b)==pin['bytes'] and hashlib.sha256(b).hexdigest()==pin['sha256'], 'ACTUAL_ACCEPTED_INPUT_PIN_MISMATCH:'+name
build=json.loads((ROOT/'receipts/BUILD_IDENTITY.json').read_text())
assert build['pin']==pins['build_pin']
for entry in build['files']:
    assert hashlib.sha256((ROOT/'source'/entry['path']).read_bytes()).hexdigest()==entry['sha256'], 'SOURCE_PIN_MISMATCH:'+entry['path']
compiler=json.loads((ROOT/'receipts/COMPILER.json').read_text())
from_hex=lambda x:struct.unpack('>d',bytes.fromhex(x))[0]
samples=[[from_hex(x) for x in l.split(',')] for l in (ROOT/'observed/samples.binary64.csv').read_text().splitlines()]
assert len(samples)==raw['node_count']==2440
assert raw['cost']=={'stored_replay':[0,0],'six_moment_observer':[0,7320],'original_gamma_parity':[0,7320],'threshold_tests':[0,9]}
assert raw['Gamma']==raw['gamma_native']
assert raw['state_unchanged'] and raw['grid_context_bitwise'] and raw['accepted_transactions']==2
F64=lambda x:F.from_float(float(x))
c,kb,eps,ct=raw['constants'];nh,nhe=raw['background'][3:5]
context={
 'producer_commit':pins['base'],'receiver_contract_head':pins['contract_head'],
 'receiver_contract_core':'93bed7e210296db7cd250421f48cdc25aff3029f',
 'accepted_source_build_pin':pins['build_pin'],'accepted_transaction':'committed-2',
 'accepted_payload_sha256':pins['payload']['typed.bin']['sha256'],
 'archival_HEAD_sha256':pins['payload']['HEAD']['sha256'],
 'original_context_sha256':pins['payload']['context.bin']['sha256'],
 'accepted_science_sha256':pins['payload']['step2.science.txt']['sha256'],
 'epoch_ln_a':raw['epoch_ln_a'],'photon_epoch_ln_a':raw['epoch_ln_a'],
 'gas_state':raw['gas'],'gas_epoch_ln_a':raw['epoch_ln_a'],
 'background':raw['background'],'background_recovery':'original pinned recipe at exact accepted epoch; original endpoint background not separately stored',
 'EOS':'T=2*w/(3*kB*(1+nHe/nH+h+(nHe/nH)*(y+2*z)))',
 'source_model':'manufactured_hhe_v1; original cold broad source 13.7..100eV',
 'material_provider':'grackle341_caseA_lowT_subset_v1; observed gas only',
 'photo_provider':'same accepted-source AtomicProvider::reference Verner outer-shell fit',
 'provider_source_sha256':hashlib.sha256((ROOT/'source/rei-adaptive-loop/review-snapshot-v4/rust/rei_microphysics/src/atomic_provider.rs').read_bytes()).hexdigest(),
 'chi_ev':raw['chi_ev'],'chi_convention':'binding energies; not Verner fit support thresholds',
 'provider_cutoffs_ev':raw['provider_cutoffs_ev'],'constants':{'c_cm_s':c,'kb_erg_k':kb,'ev_erg':eps,'c_thomson_cm3_s':ct},
 'thomson_constant_identity':'same igm_thermal.rs SIGMA_T_CM2=6.6524587051e-25 times observed c; no optical-history certification',
 'quadrature':'original Grid512/Gauss4 threshold/time-event split; recovered39983-byte context matches regenerated grid bitwise',
 'samples_sha256':hashlib.sha256((ROOT/'observed/samples.binary64.csv').read_bytes()).hexdigest(),
 'reduction':'node then HI/HeI/HeII; original nested c*nH*sigma*f*w product order; ordered binary64 additions; Ecal uses same sigma/term times same E',
 'observer_code_sha256':{str(p.relative_to(Path(__file__).parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.rglob('*')) if p.is_file() and p.suffix in ('.rs','.py','.toml','.lock')},
 'observer_compiler':compiler,'observer_binary_sha256':hashlib.sha256((ROOT/'target/debug/igm_rate_export01').read_bytes()).hexdigest(),
}
packet={'schema':'igm-instantaneous-singleton-observation/v1','context':context,'context_id':digest(context),
 'units':{'Gamma':GAMMA_UNIT,'incident_Ecal':ENERGY_UNIT},'Gamma':raw['Gamma'],'incident_Ecal':raw['incident_Ecal'],
 'family_kind':KIND,'family_id':'accepted-step2-observation:'+pins['payload']['typed.bin']['sha256'],
 'generators':None,'generator_ids':None,'uncertainty_widths':None,'provider_error':'UNKNOWN',
 'continuum_error':'UNKNOWN','family_admission':'HOLD_MISSING_EXTERNAL_FAMILY_PREMISE','physical':'HOLD','full_Wide':'HOLD','history_integrated':False,'cost':raw['cost']}
packet['observation_id']=digest({'context_id':packet['context_id'],'Gamma':packet['Gamma'],'incident_Ecal':packet['incident_Ecal']})
check(packet,packet['context_id'])
controls=[]
# Stored samples do not call any provider; compare all six ordered reductions exactly.
gamma=[0.]*3;energy=[0.]*3
for row in samples:
    eta,w,f,e,*_=row
    assert w>0 and f>=0 and e>0
    for i in range(3):
        sigma,term=row[4+i],row[7+i]
        assert sigma>=0 and term>=0
        if e<raw['provider_cutoffs_ev'][i]:assert sigma==0
        gamma[i]+=term;energy[i]+=term*e
assert gamma==packet['Gamma'] and energy==packet['incident_Ecal'];controls.append('6 exact ordered stored-sample owner/output comparisons')
# Independent exact finite algebra checks against a forward roundoff bound ONLY.
rows=[{'index':j,'weight':F64(x[1]),'density':F64(x[2]),'energy_eV':F64(x[3]),**{k:F64(x[4+i]) for i,k in enumerate(('sigma_HI','sigma_HeI','sigma_HeII'))}} for j,x in enumerate(samples)]
exact=spectral_moments(rows,F64(c),F64(nh));u=F(1,2**53);r=(len(samples)+5)*u/(1-(len(samples)+5)*u)
for observed,answer in zip((*gamma,*energy),(*exact.gamma,*exact.energy_ev_s)):
    assert abs(F64(observed)-answer)<=r*abs(answer)
controls.append('6 independent Fraction finite sums within binary64 operation-count roundoff bound; NOT continuum/provider widths')
h,y,z,w=raw['gas'];state=State(*(F64(x) for x in (h,y,z,w,nh,nhe,raw['background'][2],kb,eps,ct)))
moments=Moments(tuple(map(F64,gamma)),tuple(map(F64,energy)));chi=tuple(map(F64,raw['chi_ev']));out=project(state,moments,chi)
assert out['electron_dt_per_h_s']==out['h_dt_s']+state.f_he*(out['heii_dt_s']+2*out['heiii_dt_s'])
assert out['absorbed_erg_h_s']==out['binding_erg_h_s']+out['heat_erg_h_s']
assert out['temperature_dt_k_s']==2*out['heat_erg_h_s']/(3*state.kb_erg_k*state.particles)-state.temperature*out['electron_dt_per_h_s']/state.particles
assert out['photo_q_ell_source']==state.c_thomson_cm3_s*state.n_h*out['electron_dt_per_h_s']/state.hubble_s**2
controls.append('4 exact pinned receiver photo-source/EOS identities at actual observed full gas state')
def refuses(label,p,code):
    try:check(p,packet['context_id'])
    except ValueError as e:assert code in str(e);controls.append(label);return
    raise AssertionError(label+' not refused')
for field in ('epoch_ln_a','gas_epoch_ln_a','photon_epoch_ln_a'):
    q=copy.deepcopy(packet);q['context'][field]=math.nextafter(q['context'][field],math.inf);q['context_id']=digest(q['context']);refuses('changed '+field,q,'CONTEXT_MISMATCH')
for label,path in [('gas',('gas_state',0)),('binding threshold',('chi_ev',0)),('fit threshold',('provider_cutoffs_ev',0))]:
    q=copy.deepcopy(packet);key,i=path;q['context'][key][i]=math.nextafter(q['context'][key][i],math.inf);q['context_id']=digest(q['context']);refuses('changed '+label,q,'CONTEXT_MISMATCH')
for field in ('provider_source_sha256','quadrature','original_context_sha256','EOS','accepted_payload_sha256'):
    q=copy.deepcopy(packet);q['context'][field]+='changed';q['context_id']=digest(q['context']);refuses('changed '+field,q,'CONTEXT_MISMATCH')
q=copy.deepcopy(packet);q['units']['Gamma']='cm^-3 s^-1';refuses('target-density rate units refused',q,'UNITS_REQUIRED')
q=copy.deepcopy(packet);q['units']['incident_Ecal']='erg absorber^-1 s^-1';refuses('erg energy conversion refused',q,'UNITS_REQUIRED')
q=copy.deepcopy(packet);q['Gamma'][0]*=4*math.pi;refuses('extra4pi value conversion refused',q,'SUBTHRESHOLD')
q=copy.deepcopy(packet);q['family_kind']='supplied_uncertainty';q['generators']=[];refuses('singleton not promoted to parameter family',q,'NOT_CERTIFIED')
for field,value in [('uncertainty_widths',[0]*6),('generator_ids',[]),('generators',[]),('provider_error',0),('continuum_error',0),('family_admission','CERTIFIED'),('physical','PASS'),('full_Wide','PASS'),('history_integrated',True)]:
    q=copy.deepcopy(packet);q[field]=value;refuses('fabricated singleton '+field+' refused',q,'NOT_CERTIFIED' if field in ('uncertainty_widths','generator_ids','generators') else 'INVARIANTS_REQUIRED')
try:require_certified_family(packet)
except ValueError as e:assert 'NOT_SINGLETON' in str(e);controls.append('family receiver explicit refusal')
else:raise AssertionError('family admission')
try:fixed_difference(state,moments,State(state.h,state.y,state.z,state.w_erg_h*2,state.n_h,state.n_he,state.hubble_s,state.kb_erg_k,state.ev_erg,state.c_thomson_cm3_s),moments,chi)
except ContractError:controls.append('changed gas/EOS cannot use same-state difference')
else:raise AssertionError('state refusal')
# Algebra-only threshold fixture: zero excess heat does NOT imply zero Tdot.
edge=Moments((F(1),F(0),F(0)),(chi[0],F(0),F(0)));threshold=project(state,edge,chi)
assert threshold['heat_erg_h_s']==0 and threshold['temperature_dt_k_s']<0;controls.append('threshold algebra distinguishes heat from particle-dilution Tdot; not provider fixture')
(ROOT/'observed/EXPORT01.json').write_text(json.dumps(packet,indent=2)+'\n')
rat=lambda v:str(v.numerator)+'/'+str(v.denominator)
(ROOT/'observed/PHOTO_ALGEBRA.json').write_text(json.dumps({'source':'exact PR87 projector; direct point algebra only, no certified family','context_id':packet['context_id'],'native_per_second':{k:rat(v) for k,v in out.items()},'physical':'HOLD'},indent=2)+'\n')
result={'status':'PASS_SINGLETON_OBSERVATION_ONLY','controls':controls,'control_count':len(controls),'ordered_moment_comparisons':6,'independent_finite_algebra_comparisons':6,'native_gamma_bitwise_comparisons':3,'native_control_count':raw['native_controls'],'cost':raw['cost'],'new_history_steps':0,'native_rhs_final_export':0,'family_admission':'HOLD','continuum_provider_uncertainty':'UNKNOWN'}
(ROOT/'receipts/RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
