#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

HERE=Path(__file__).resolve()
STAGE=HERE.parents[1]
REPO=HERE.parents[3]
R1=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1_RATE_DERIVED_POSITIVE_MULTIRATE_RELAXATION_CONE_LOCK/data'
R2A=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data'
keys=['shape_lane','interval_index','substep','macro_index']
rate=pd.read_csv(R1/'rate_interval_lock.csv')
piv=rate.pivot(index=keys,columns='family',values=['endpoint_previous','endpoint_target']).reset_index()
piv.columns=['_'.join([str(x) for x in c if str(x)]) if isinstance(c,tuple) else c for c in piv.columns]
piv=piv.rename(columns={k+'_':k for k in keys})
target=pd.read_csv(R2A/'macro_projection.csv')[keys+['M_sink_H_cap_cosmic_cMpc3','M_sink_H_cap_volume_cMpc3']]
target=target.sort_values(['shape_lane','macro_index','interval_index','substep']).copy()
# Previous cap is the previous endpoint's cap; for the constructed initial endpoint use the first target cap.
target['prev_cap_cosmic']=target.groupby(['shape_lane','macro_index'])['M_sink_H_cap_cosmic_cMpc3'].shift(1).fillna(target['M_sink_H_cap_cosmic_cMpc3'])
target['prev_cap_volume']=target.groupby(['shape_lane','macro_index'])['M_sink_H_cap_volume_cMpc3'].shift(1).fillna(target['M_sink_H_cap_volume_cMpc3'])
d=piv.merge(target,on=keys,how='left',validate='one_to_one')
for suffix in ['previous','target']:
    d[f'neutral_{suffix}']=d[f'endpoint_{suffix}_M']-d[f'endpoint_{suffix}_I']
d['previous_state_cone_pass']=(d.endpoint_previous_M>=0)&(d.endpoint_previous_I>=0)&(d.neutral_previous>=0)&(d.endpoint_previous_U>=0)
d['target_state_cone_pass']=(d.endpoint_target_M>=0)&(d.endpoint_target_I>=0)&(d.neutral_target>=0)&(d.endpoint_target_U>=0)
d['previous_mass_caps_pass']=(d.endpoint_previous_M<=d.prev_cap_cosmic*(1+2e-11))&(d.endpoint_previous_M<=d.prev_cap_volume*(1+2e-11))
d['target_mass_caps_pass']=(d.endpoint_target_M<=d.M_sink_H_cap_cosmic_cMpc3*(1+2e-11))&(d.endpoint_target_M<=d.M_sink_H_cap_volume_cMpc3*(1+2e-11))
d['J_endpoint_nonnegative_pass']=(d.endpoint_previous_J_G1>=0)&(d.endpoint_target_J_G1>=0)&(d.endpoint_previous_J_G2a>=0)&(d.endpoint_target_J_G2a>=0)
d['convex_state_segment_pass']=d.previous_state_cone_pass&d.target_state_cone_pass&d.previous_mass_caps_pass&d.target_mass_caps_pass
# Minimum linear endpoint slack; sufficient because each cone inequality is affine along the segment.
d['minimum_endpoint_neutral_slack']=d[['neutral_previous','neutral_target']].min(axis=1)
d['minimum_endpoint_cosmic_cap_slack']=np.minimum(d.prev_cap_cosmic-d.endpoint_previous_M,d.M_sink_H_cap_cosmic_cMpc3-d.endpoint_target_M)
d['minimum_endpoint_volume_cap_slack']=np.minimum(d.prev_cap_volume-d.endpoint_previous_M,d.M_sink_H_cap_volume_cMpc3-d.endpoint_target_M)
out=STAGE/'data/convex_endpoint_segment_audit.csv'
d.to_csv(out,index=False)
summary={
 'classification':'R2C_R1A_CONVEX_ENDPOINT_SEGMENT_AUDIT',
 'macro_pair_count':int(len(d)),
 'previous_state_cone_failure_count':int((~d.previous_state_cone_pass).sum()),
 'target_state_cone_failure_count':int((~d.target_state_cone_pass).sum()),
 'mass_cap_endpoint_failure_count':int((~(d.previous_mass_caps_pass&d.target_mass_caps_pass)).sum()),
 'current_endpoint_nonnegative_failure_count':int((~d.J_endpoint_nonnegative_pass).sum()),
 'convex_state_segment_failure_count':int((~d.convex_state_segment_pass).sum()),
 'minimum_neutral_slack':float(d.minimum_endpoint_neutral_slack.min()),
 'minimum_cosmic_cap_slack':float(d.minimum_endpoint_cosmic_cap_slack.min()),
 'minimum_volume_cap_slack':float(d.minimum_endpoint_volume_cap_slack.min()),
 'interpretation':'Every inherited state endpoint pair lies in the convex M-I-U and interpolated mass-cap cone; common-equilibrium failures arise from extrapolation beyond the endpoint segment.',
 'pass':bool(d.convex_state_segment_pass.all() and d.J_endpoint_nonnegative_pass.all())
}
(STAGE/'data/convex_endpoint_segment_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
raise SystemExit(0 if summary['pass'] else 1)
