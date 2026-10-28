"""One-time input projection from immutable saved PR251 source and BB13 Table 1."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
original=Path('/mnt/data/rei_uvb_eos_audit_20261029/source/FROZEN_INPUT.json')
src=original.read_bytes(); data=json.loads(src)
assert data['source_observation_git_blob']=='61c1ecdcb1be05d47bb59165fb4cac8bb14deb52'
assert data['source_model_git_blob']=='abd45812fb38691bcc76b5bddd33c55e2e5e4be3'
assert data['z']==[2.4,2.8,3.2,3.6,4.,4.4,4.75]
# Verified against GitHub original pinned BB13 JSON and primary-source Table 1 (2026-10-29).
v=[.084,.086,.083,.077,.071,.066,.064]
lo=[-.016,-.008,-.003,-.003,-.004,-.005,-.014]
hi=[.001,.006,.012,.016,.021,.023,.023]
full={
 'schema':'REI_UVB_BB13_EOS_JEANS_BOX_SUPPORT_FROZEN_INPUT_V1',
 'observed_pr251_pin':'c5ab42c8673db614e7fb16695ad071c65becb81b',
 'prior_pr253_pin':'21c695be2f672f5487e3fe1beb69b07af07a3c92',
 'original_source_observation_git_blob':'61c1ecdcb1be05d47bb59165fb4cac8bb14deb52',
 'original_saved_calibration_git_blob':'abd45812fb38691bcc76b5bddd33c55e2e5e4be3',
 'projection_sha256':hashlib.sha256(src).hexdigest(),
 'representation':'Parsed JSON binary64 values treated as their exact real images by Fraction.from_float; same source fields with new Table1 Jeans bounds; not an original PDF raw-byte claim',
 'source_primary':'https://doi.org/10.1093/mnras/stt1610',
 'z':data['z'],
 'observed_dex':data['observed_dex'],'template_dex':data['template_dex'],
 'covariance_dex_squared':data['statistical_covariance_dex2'],
 'eos_response_dex':v,'eos_theta_bounds':[-1,1],
 'jeans_smoothing_lower_dex':lo,'jeans_smoothing_upper_dex':hi,
 'jeans_box_meaning':'All coordinates independently range within printed source-bound intervals; conservative outer box, NOT a statistical independence assumption or realizable physical parameter prior',
 'EOS_meaning':'theta=(gamma_TDR-1.4)/0.2 within [-1,1]; primary BB13 gamma baseline1.4',
 'model':'r=d-m, X=[1,z-3.6], adjusted observation r+theta*v+j; fixed C and source template',
 'old_beta':-0.04591874303144477,'old_kappa':0.06866173948059068,
 'old_Q2':11.347835208970784,'old_24test_suite':'REUSED_NOT_RERUN_IN_THIS_UNIT',
 'physical_F4':'PARTIAL','original_DAG_working':'33/88','central_last_observed':'28/88',
 'test_tolerance_abs':1e-13,'test_tolerance_rel':1e-11,
 'active_H_Li_species_changed':False,'new_IVP':0}
p=(root/'source/FROZEN_BB13_SUPPORT_INPUT.json');p.write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n')
print('created',p,'bytes',p.stat().st_size,'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
