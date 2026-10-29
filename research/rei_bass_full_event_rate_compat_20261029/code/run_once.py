"""Static scientific run; no IVP or full BASS/REI chemistry simulation."""
from pathlib import Path
from decimal import Decimal
import sys, json
p=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(p/'code'))
import event_rate_compat as m

locks=m.source_lock()
rank=m.rank_witness()
minimax=m.minimax_two_epochs()
replay=m.same_source_frozen_replay()
assert len(replay)==7 and max(x['max_relative_rhs_difference'] for x in replay)<2e-14
assert rank['ranks']==(3,6)
selected=m.selected_rows()
out={"schema":"REI_BASS_EVENT_RATE_COMPAT_RESULT_V1",
    "source_shas":locks,"BASS_single_UV_shape":"G0=uv_scale*Gphoto fixed photon_field spectral index -2.5 and 5..200 eV",
    "P19_13_row_scope":"manual 13-row numeric source projection, NOT original P19 59-row byte-equivalent",
    "calibration_knots_included":len(selected),"rank_result":rank,
    "minimax_result":minimax,"pr262_same_source_frozen_replay":replay,
    "max_relative_frozen_F":max(x['max_relative_rhs_difference'] for x in replay),
    "max_relative_frozen_J":max(x['max_relative_jacobian_difference'] for x in replay),
    "actual_bass_rate_coefficients":"NOT_AVAILABLE_IN_OWNER_PR234_SOURCE_ZIP",
    "actual_original_REI_external_model_config":"ILLUSTRATIVE_UNCALIBRATED_DIFFERENT_PHOTON_SOURCE",
    "physics_scope":"Rank tests and positivity for three rate-space channels; no physical spectral inversion, BASS source exchange, full J, tau, or IVP",
    "NO_MORE_IVPs":True,
    "DAG_working":"33/88","DAG_central":"28/88","physical_delta":0,
    "scoped_review_different_author":"NOT_RUN"}
(p/'results'/'RESULT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
with open(p/'results'/'RATES_11.tsv','w') as f:
    for row in selected:
        f.write('\t'.join(str(x) for x in (row[0],row[1],row[3],row[5]))+'\n')
print(json.dumps({"rank":rank,"minimax_rel":minimax['minimax_relative_error'],"max_REI_replay_rhs_rel":out['max_relative_frozen_F'],"rows_replayed":len(replay)},indent=2))
