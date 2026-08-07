#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; STAGE=HERE.parent; REPO=STAGE.parents[1]
R1=REPO/'stages'/'Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2'
R2A=REPO/'stages'/'Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
im=load('adv_im',HERE/'initial_material_state.py'); lm=load('adv_lm',HERE/'state_derived_owner_law.py')
state=im.build_initial_material_state(r1_root=R1,r2a_root=R2A); model=lm.StateDerivedOwnerLaw(r1_root=R1,r2a_root=R2A,initial_state=state); rec=model.forcing.iloc[0].to_dict(); base=model.evaluate(forcing_row=rec,state_frame=state.frame)
checks={}
# Determinism
again=model.evaluate(forcing_row=rec,state_frame=state.frame); checks['repeat_hash_identity']=base.node_hashes==again.node_hashes
# Negative material must fail closed.
bad=state.frame.copy(); bad.loc[0,'N_HI']=-1.0
try: model.evaluate(forcing_row=rec,state_frame=bad); checks['negative_material_rejected']=False
except ValueError: checks['negative_material_rejected']=True
# Negative authoritative opacity must fail closed.
bad_rec=dict(rec); bad_rec['kappa_G1_cMpc-1']=-1.0
try: model.evaluate(forcing_row=bad_rec,state_frame=state.frame); checks['negative_authoritative_opacity_rejected']=False
except ValueError: checks['negative_authoritative_opacity_rejected']=True
# Nonzero G3 total on a state with no explicit atomic support must fail closed.
zero=state.frame.copy();
for c in ['N_HI','N_HeI','N_HeII']: zero[c]=0.0
try: model.evaluate(forcing_row=rec,state_frame=zero); checks['nonzero_target_on_zero_support_rejected']=False
except ValueError: checks['nonzero_target_on_zero_support_rejected']=True
checks['subgrid_resolved_source_exact_zero']=lm.RESOLVED_SOURCE['EFFECTIVE_HI_SUBGRID']==(0,0,0)
checks['post_hoc_lane_selection_forbidden']=base.metadata['post_hoc_lane_selection_used'] is False
checks['primary_lane_predeclared']=base.metadata['primary_subgrid_lane']=='LOCAL_NEUTRAL_HAZARD_PRIMARY'
result={'classification':'R2B_R1_ADVERSARIAL_AUDIT','checks':checks,'pass':all(checks.values())}
(STAGE/'data'/'adversarial_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2,sort_keys=True));raise SystemExit(0 if result['pass'] else 2)
