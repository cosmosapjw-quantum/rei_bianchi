"""Public Lumina simulation histories, with explicit finite support and units."""
import bisect
import json
import math
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]
KINDS={'SFRD':('sfrd_lumina.txt',2,'Msun yr^-1 cMpc^-3'),
       'xHI_median':('HI_reion_lumina.txt',8,'volume-weighted neutral fraction'),
       'xHeIII_median':('HeIII_reion_lumina.txt',8,'volume-weighted HeIII fraction'),
       'tau_CMB':('tau_cmb_vs_z_lumina.txt',2,'dimensionless cumulative optical depth')}


def load_histories():
    provenance=json.loads((UNIT/'sources/LUMINA_DATA_PROVENANCE.json').read_text())
    expected={row['name']:row for row in provenance['files']};histories={}
    for kind,(filename,width,units) in KINDS.items():
        rows=[]
        for line in (UNIT/'sources/lumina'/filename).read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            row=[float(value) for value in line.split()]
            if len(row)!=width or any(not math.isfinite(x) or x<0 for x in row):
                raise ValueError('Lumina row shape or finite nonnegative field mismatch: '+filename)
            if width==8 and any(x>1 for x in row[1:]):raise ValueError('fraction outside[0,1]')
            rows.append(row)
        if len(rows)!=expected[filename]['row_count']:raise ValueError('Lumina source row-count mismatch: '+filename)
        ascending=all(b[0]>a[0] for a,b in zip(rows,rows[1:]));descending=all(b[0]<a[0] for a,b in zip(rows,rows[1:]))
        if not ascending and not descending:raise ValueError('Lumina source redshifts not strictly monotone')
        violations=0
        if width==8:
            for row in rows:
                labeled_order=[row[j] for j in (6,4,2,1,3,5,7)]
                violations+=int(any(b<a for a,b in zip(labeled_order,labeled_order[1:])))
        histories[kind]={'rows_ascending_z':rows if ascending else list(reversed(rows)),
            'raw_redshift_order':'ascending' if ascending else 'descending','source':filename,'units':units,
            'selected_value_column':1,'classification':'SIMULATION_MODEL_HISTORY_NOT_OBSERVATION',
            'quantile_header_order_violations':violations,
            'quantile_status':'UNRESOLVED_HEADER_ORDER_RETAIN_RAW_USE_MEDIAN_ONLY' if kind=='xHeIII_median' and violations else 'NOT_USED_IN_ADAPTER'}
    return histories


def history_at(kind,z,histories=None):
    if histories is None:histories=load_histories()
    if kind not in histories:raise ValueError('unknown Lumina history field')
    history=histories[kind];rows=history['rows_ascending_z'];knots=[row[0] for row in rows]
    common={'kind':kind,'z':z,'support_z':[knots[0],knots[-1]],'units':history['units'],
            'classification':history['classification'],'source':history['source'],'quantile_status':history['quantile_status']}
    if not math.isfinite(z) or not knots[0]<=z<=knots[-1]:
        return {**common,'status':'MISSING_OUTSIDE_SUPPLIED_SUPPORT','value':None}
    j=bisect.bisect_left(knots,z)
    if j<len(knots) and knots[j]==z:value=rows[j][1];method='EXACT_KNOT'
    else:
        fraction=(z-knots[j-1])/(knots[j]-knots[j-1]);value=(1-fraction)*rows[j-1][1]+fraction*rows[j][1]
        method='LINEAR_VALUE_IN_Z'
    return {**common,'status':'AVAILABLE_MODEL_HISTORY','value':value,'interpolation':method,
            'interpolation_error':'NOT_CALIBRATED','observational_covariance':None}


def domain_report(redshifts=(20.,10.,6.,4.,3.)):
    histories=load_histories()
    return {'histories':{kind:{'row_count':len(h['rows_ascending_z']),'support_z':[h['rows_ascending_z'][0][0],h['rows_ascending_z'][-1][0]],
                'units':h['units'],'raw_redshift_order':h['raw_redshift_order'],'quantile_status':h['quantile_status'],
                'quantile_header_order_violations':h['quantile_header_order_violations']} for kind,h in histories.items()},
            'queries':[{'z':z,'fields':{kind:history_at(kind,z,histories) for kind in KINDS},
                        'Puchwein_raw_rate_support':0<=z<=15.1,'BB2013_calibrated_support':2.4<=z<=4.75} for z in redshifts],
            'SFRD_to_Gamma':'MISSING_SPECTRAL_YIELD_AGE_METALLICITY_ESCAPE_AND_TRANSPORT',
            'HeIII_quantile_policy':'RAW_COLUMNS_PRESERVED_NOT_SORTED_OR_USED_AS_CONFIDENCE_INTERVALS',
            'tau_status':'Model cumulative depth; source assumes fully ionized H+He belowz3',
            'new_IVPs':0,'new_observational_fit_from_Lumina':False}
