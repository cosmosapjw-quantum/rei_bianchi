#!/usr/bin/env python3
"""Produce SOURCE-SCOPED read-only HH Coulomb-to-REI advisory; never a physical rate."""
from __future__ import annotations
import argparse,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys44_rei_guard import read_rei_guard
from wu088_hh.phys45_screened_exterior import FROZEN_ID

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--matrix",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--rei-root",type=Path,default=Path.home()/"Dropbox/bianchi/rei_bianchi")
 p.add_argument("--wu-root",type=Path,default=ROOT)
 a=p.parse_args()
 dat=a.matrix.read_bytes()
 cert=json.loads(dat)
 if cert['schema']!='WU088_HH_PHYS45_YUKAWA_COUPLED_EXTERIOR_V1' or cert['original_source_sha256']!=FROZEN_ID:
  raise ValueError("phys45 exact matrix and original frozen input required")
 guard=read_rei_guard(a.rei_root,a.wu_root)
 assert guard['physical_rate_admission']=='HOLD'
 advisory={
  'schema':'WU088_HH_PHYS45_REI_CONSUMER_ADVISORY_V1',
  'admission':'HOLD_NOT_AN_HH_RATE_PROVIDER',
  'provider':'WU088_HH PHYS45 exact Coulomb+offcentre screening boundary research',
  'original_frozen_source_sha256':FROZEN_ID,
  'derived_exact_matrix_sha256':hashlib.sha256(dat).hexdigest(),
  'derived_exact_matrix_file':str(a.matrix.resolve().relative_to(a.wu_root.resolve())),
  'species_and_reaction':'microscopic H(1s)+H(1s) electron spectator model, NOT cosmological source',
  'coupled_channels':'normalized m=0 ell0..20 at original exterior a0=20; no full m/ell propagation claim',
  'reference_partial_wave':'central Coulomb etaC=-10/7; outgoing Green resolvent not yet proved',
  'certified_exterior_full_angular_screened_radial_L1_upper':
       cert['tails']['full_screened_plus_2V_radial_L1_upper'],
  'certified_exterior_all_high_ell_noncentral_radial_L1_operator_upper':
       cert['tails']['ell_gt20_off_central_source_L1_operator_upper'],
  'source_receiver':{
   'consumer_repository':'cosmosapjw-quantum/rei_bianchi',
   'local_owner_revision_read_only':guard['local_rei_head_read_only'],
   'public_latest_reviewed_pr_number':129,
   'public_latest_reviewed_pr_head':'fa20d75e344a28c833a47cbca82315ccbbdf6882',
   'local_OWNER_and_PR_are_same_revision':guard['local_rei_head_read_only']=='fa20d75e344a28c833a47cbca82315ccbbdf6882',
   'local_AXBI_source_id':guard['consumer_source_identity'],
   'local_FT03_fixture_model':guard['separate_ft03_model_identity'],
   'local_HH_R10_excluded':guard['consumer_actual_existing_HH_R10_excluded'],
   'local_external_authority_guard':guard['consumer_actual_require_physical_source_fails_closed'],
  },
  'required_before_any_physical_consumer_update':[
   'true noncentral screened exterior Volterra/Green weighted resolvent + outgoing DtN, driven regular origin',
   'continuous scattering inverse and incoming adjoint amplitude with physical flux normalization',
   'channel-resolved microscopic sigma(E) and Maxwellian k_HH(T) with identical-pair convention',
   'exact source/binding/process owner and adopted proper-clock REI interval state, density and thermal units',
   'no double counting existing H-He electron-impact collisional channel and matched source histories',
  ],
  'thermal_k_HH_cm3_s':None,
  'actual_q_HH_per_H_s':None,
  'actual_dotT_HH_K_s':None,
  'actual_dot_ne_HH_cm3_s':None,
  'production_HH_R10':'OFF',
  'affected_external_repos':[],
  'no_direct_input_into_AX08_solver':True,
 }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(advisory,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'consumer_local_head':guard['local_rei_head_read_only'],
 'latest_PR_head':advisory['source_receiver']['public_latest_reviewed_pr_head'],
 'matching_owner_revision':advisory['source_receiver']['local_OWNER_and_PR_are_same_revision'],
 'rate_status':advisory['admission'],'result':str(a.out)}))
if __name__=='__main__':main()
