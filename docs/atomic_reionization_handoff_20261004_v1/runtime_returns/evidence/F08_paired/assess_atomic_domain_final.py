"""Actual provider-domain intake for F09; no astrophysical campaign or source change."""
from pathlib import Path
import json,hashlib
ROOT=Path.cwd();P=ROOT/'.cuh/fastest-track/REI-F08-PAIRED';E=P/'external-final'
reads=json.loads((E/'selected-read-receipts.json').read_text())
for item in reads:assert hashlib.sha256((ROOT/item['local']).read_bytes()).hexdigest()==item['sha256']
he=json.loads((E/'BASS_HE-HE_F3_DOMAIN_GATE.json').read_text());hh=json.loads((E/'WU088_HH-OWNER_INPUT_REQUEST.json').read_text())
def intersection(a,b):
 lo=max(a[0],b[0]);hi=min(a[1],b[1]);return [lo,hi] if lo<=hi else None
common=intersection(he['KF96_domain_K'],he['GM25_domain_K']);assert common==he['pair_common_domain_K'];ft03=he['active_FT03_domain_K'];s0=[35000,60000];assert intersection(ft03,common) is None and intersection(s0,common) is None
r={'task_id':'REI-F09','status':'EXTERNAL_PROVIDER_DOMAIN_AND_BINDING_BLOCKED','baseline_task':'REI-F08','baseline_validation_state':'READ_ACTUAL_CAMPAIGN_RECEIPT_AT_CLOSEOUT','paired_scenario_path':'configs/rei_fastest_v1/science_scenario_v1.json','paired_scenario_sha256':hashlib.sha256((ROOT/'configs/rei_fastest_v1/science_scenario_v1.json').read_bytes()).hexdigest(),'provider_read_receipts':reads,'temperature_domains_K':{'active_FT03':ft03,'certified_S0_box':s0,'KF96':he['KF96_domain_K'],'GM25':he['GM25_domain_K'],'provider_common':common,'FT03_common_intersection':intersection(ft03,common),'S0_common_intersection':intersection(s0,common)},'null_intersection_means':'EMPTY_SET_NOT_MISSING_DATA','He_F2_global_return_accepted':False,'He_F3_completed':False,'HH_F2_owner_provider_binding_ready':hh['ready_for_HH_F1'],'HH_owner_receipt_status':hh['status'],'atomic_sensitivity_campaigns_executed':0,'combined_campaign_receipt':None,'duplicate_astrophysical_campaigns':0,'baseline_HH_RCT_CR':'OFF_DECLARED_MODEL_NO_NEGLIGIBILITY_CLAIM','baseline_validity_blocked_by_optional_provider':False,'forbidden_substitutions':he['do_not'],'next_executable_condition':he['reopen_trigger'],'L01':'DORMANT_NO_OWNER_SELECTED_EXTENSION_INPUTS','scientific_admission':'HOLD','physical_uncertainty_bound':'NOT_MEASURED'}
state=json.loads((E/'BASS_HE-CURRENT_FASTEST_STATE.json').read_text());r['He_F2_global_return_accepted']=state['HE_F2_global_completed'];r['latest_supplier_addon_receipts']={k:state[k] for k in ['HE_RCT_STEP01_addon','HE_RCT_STEP02_static'] if k in state};r['supplier_addons_rerun_here']=False
(P/'atomic-domain-final-assessment.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
