"""New source-specific exact arithmetic. No provider solve or old computation."""
import csv
from fractions import Fraction as F
import json
from pathlib import Path
from tdcs54 import (ratio_profile,feasible_scale_interval,minimax_profile,
    pair_contrast,source_angle_vectors,conditional_printing_ratio_interval,
    validate_source_rows,serialized)

UNIT=Path(__file__).resolve().parents[1]


def main():
    rows=list(csv.DictReader((UNIT/'source/jones2000_tableIV_cross_sections.csv').read_text().splitlines()))
    metadata=json.loads((UNIT/'source/SOURCE_METADATA.json').read_text())
    table=json.loads((UNIT/'source/TABLE_IV_INPUT.json').read_text())
    if table['rows']!=rows:raise ValueError('source CSV/JSON literal rows differ')
    validated=validate_source_rows(rows,metadata)
    printed=json.loads((UNIT/'source/PRINTED_RATIO_CONTROLS.json').read_text())
    summaries=json.loads((UNIT/'source/PAPER_APPROXIMATE_SUMMARIES.json').read_text())
    groups={};controls=[]
    for name,indices in validated['groups'].items():
        selected=[rows[i] for i in indices];nominal=[r['experiment_TDCS_au'] for r in selected];models={}
        for label,column in [('CDW_EIS','CDW_EIS_TDCS_au'),('CCC99','CCC99_TDCS_au')]:
            profile=ratio_profile([r[column] for r in selected],nominal)
            optimum=minimax_profile(profile['ratios'],F(13,20),F(27,20))
            paper=summaries.get(name,{}).get(label)
            models[label]={'profile':profile,'optimum':optimum,
                           'nominated_sensitivity':feasible_scale_interval(profile['ratios'],F(1,10),F(13,20),F(27,20)),
                           'paper_approximate_summary':paper,
                           'exact_nominal_delta_percent':100*optimum['free_delta'],
                           'exact_minus_paper_percentage_points':100*optimum['free_delta']-F(paper['reported_percent'].rstrip('%')) if paper else None}
        groups[name]={'row_indices_zero_based':indices,'models':models}
    for label,column in [('CDW_EIS','CDW_EIS_TDCS_au'),('CCC99','CCC99_TDCS_au')]:
        if len(printed[label])!=8:raise ValueError('8printed ratios per producer required')
        for i,(row,p) in enumerate(zip(rows,printed[label])):
            controls.append({'row_index_zero_based':i,'producer':label,'source_printed_string':p,
                             **conditional_printing_ratio_interval(row[column],row['experiment_TDCS_au'],p)})
    located=[rows[i] for i in validated['groups']['located_anchors_2']]
    if len(located)!=2:raise ValueError('only2located rows admitted')
    contrasts={label:pair_contrast(located[0][column],located[1][column],located[0]['experiment_TDCS_au'],located[1]['experiment_TDCS_au'],F(1,10)) for label,column in [('CDW_EIS','CDW_EIS_TDCS_au'),('CCC99','CCC99_TDCS_au')]}
    geometry=[{'row_index_zero_based':i,**source_angle_vectors(rows[i]['fast_angle_counterclockwise_deg'],rows[i]['slow_angle_clockwise_deg'])} for i in validated['groups']['located_anchors_2']]
    result={'status':'NUMERICALLY_CHECKED_SCOPED_PENDING_C9','source':metadata,'source_rows_literal':rows,
            'source_validation':validated,'groups':groups,'pair_contrasts':contrasts,'located_geometry':geometry,
            'printing_controls':controls,'printing_compatible_count':sum(c['compatible'] for c in controls),
            'paper_summaries_are_descriptive_not_gates':True,
            'nominal_rounding_does_not_certify_source_accuracy':True,
            'physical_provider_admitted':False,'parent_status':'SOURCE_INPUT_PENDING',
            'old_suite_runs':0,'new_IVP':0,'source_solver_runs':0,'fast_energy':'NOT_EVALUATED'}
    (UNIT/'results/source_analysis.json').write_text(json.dumps(serialized(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'groups':list(groups),'source_values':24,'printed_ratio_controls':len(controls),
                      'printing_compatible':sum(c['compatible'] for c in controls),'located_points':2,
                      'all_CDW_delta_exact':str(groups['all_reported_features_8']['models']['CDW_EIS']['optimum']['free_delta'])}))


if __name__=='__main__':main()
