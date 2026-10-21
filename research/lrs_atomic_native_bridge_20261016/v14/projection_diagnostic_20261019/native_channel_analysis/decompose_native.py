"""Read preserved V14 native CSVs; no native evolution or toy suite runs.

Exact finite EOS split (coarse c, fine f):
  T_c - T_f = (w_c-w_f)/(A D_c) - T_f (e_c-e_f)/D_c,
  A=3 k_B/2 in eV/K, D=1+Y+e.
CSV decimal parsing uses 60-digit arithmetic to avoid adding subtraction noise.
"""
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import math
import argparse

getcontext().prec = 60
D = Decimal
Y = D('.2454') / (4 * (1-D('.2454')))
A = D('1.5') * D('1.380649e-16') / D('1.602176634e-12')
CHI = (D('13.598434599702'), D('24.587389011'), D('54.41776'))
E0 = D('.075') + Y * (D('.12') + 2*D('.03'))
W0 = A * D(15000) * (1+Y+E0)
_parser = argparse.ArgumentParser(description=__doc__)
_parser.add_argument('--input-dir', type=Path,
    default=Path(__file__).resolve().parents[2] / 'executions/REI_LRS_V14_20261018T124115Z/full/evidence',
    help='Preserved native birth CSV directory; default is the repository V14 full-run evidence.')
_parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
_args = _parser.parse_args()
ROOT = _args.input_dir.resolve()
OUTPUT = _args.output_dir.resolve()
RAW_HASHES = {
    '1e-5': 'a4105e751d66ba59975c39d70c5d5822029cb5be0dd64094224417b28939e2f9',
    '1e-4': '58bde576741a8f8a980721da80990e2397c97f3e94a3500bac790e6745476e5f',
}


def enrich(row):
    x = {k: (v if k == 'mode' else D(v)) for k,v in row.items()}
    x['e'] = x['HII'] + Y*(x['HeII']+2*x['HeIII'])
    x['particles'] = 1+Y+x['e']
    x['w_eV_H'] = A*x['T_K']*x['particles']
    for label,prefix,suffix,keys in (
        ('photo_total','photo_','',('HI','HeI','HeII')),
        ('CI_total','CI_','',('HI','HeI','HeII')),
        ('RR_total','RR_','',('HII','HeII','HeIII')),
        ('CE_total_eV_H','CE_','_eV_H',('HI','HeI','HeII')),
        ('RR_total_eV_H','RR_','_eV_H',('HII','HeII','HeIII')),
    ):
        x[label] = sum((x[prefix+k+suffix] for k in keys),D(0))
    x['CI_binding_eV_H'] = sum((c*x['CI_'+k] for c,k in zip(CHI,('HI','HeI','HeII'))),D(0))
    x['RR_binding_eV_H'] = sum((c*x['RR_'+k] for c,k in zip(CHI,('HII','HeII','HeIII'))),D(0))
    x['electron_event_residual_H'] = x['e'] - E0 - x['photo_total'] - x['CI_total'] + x['RR_total'] + x['DR_HeII']
    x['gas_residual_eV_H'] = (x['w_eV_H'] - W0 - x['photo_heat_eV_H'] - x['CMB_eV_H']
        + x['thermal_work_eV_H'] + x['CI_binding_eV_H'] + x['CE_total_eV_H']
        + x['RR_total_eV_H'] + x['DR_HeII_eV_H'] + x['FF_eV_H'])
    return x


def difference(coarse,fine):
    delta = {k: coarse[k]-fine[k] for k in coarse if k!='mode'}
    invAD = 1 / (A*coarse['particles'])
    invD = 1 / coarse['particles']
    phi = fine['T_K'] * invD
    energy = {
        'photo_heat': delta['photo_heat_eV_H']*invAD,
        'CI_binding': -delta['CI_binding_eV_H']*invAD,
        'CE': -delta['CE_total_eV_H']*invAD,
        'RR_cooling': -delta['RR_total_eV_H']*invAD,
        'DR_cooling': -delta['DR_HeII_eV_H']*invAD,
        'FF': -delta['FF_eV_H']*invAD,
        'CMB': delta['CMB_eV_H']*invAD,
        'gas_work': -delta['thermal_work_eV_H']*invAD,
        'gas_residual': delta['gas_residual_eV_H']*invAD,
    }
    electron = {
        'photo_electrons': -phi*delta['photo_total'],
        'CI_electrons': -phi*delta['CI_total'],
        'RR_electrons': phi*delta['RR_total'],
        'DR_electrons': phi*delta['DR_HeII'],
        'electron_residual': -phi*delta['electron_event_residual_H'],
    }
    eos_w = delta['w_eV_H']*invAD
    eos_e = -phi*delta['e']
    combined = {
        'photo':energy['photo_heat']+electron['photo_electrons'],
        'CI':energy['CI_binding']+electron['CI_electrons'],
        'RR':energy['RR_cooling']+electron['RR_electrons'],
        'DR':energy['DR_cooling']+electron['DR_electrons'],
        'CE':energy['CE'],'FF':energy['FF'],'CMB':energy['CMB'],
        'gas_work':energy['gas_work'],
        'residual':energy['gas_residual']+electron['electron_residual'],
    }
    err = delta['T_K'] - sum(combined.values(),D(0))
    assert abs(err) < D('1e-45'),err
    assert abs(delta['T_K']-eos_w-eos_e)<D('1e-45')
    return {'delta':delta,'eos_w_K':eos_w,'eos_e_K':eos_e,
        'energy_channels_K':energy,'electron_channels_K':electron,
        'combined_channels_K':combined,'decomposition_error_K':err}


def serializable(obj):
    if isinstance(obj,D):return float(obj)
    if isinstance(obj,dict):return {str(k):serializable(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [serializable(x) for x in obj]
    return obj


def order(a,b):
    if a==0 or b==0:return None
    return {'p':math.log2(float(abs(a/b))),'sign_change':a*b<0}


result={'scope':'Preserved native CSV analysis only. No new native runs or toy tests.',
    'precision_decimal_digits':getcontext().prec,'Y':Y,'A_eV_K':A,'W0_eV_H':W0,
    'raw_hashes':RAW_HASHES,'intervals':{}}
for tag,expected_sha in RAW_HASHES.items():
    path=ROOT/f'birth_{tag}.csv'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected_sha
    rows=list(csv.DictReader(path.open()))
    endpoints={}
    for row in rows:
        if int(row['step'])!=int(row['N']):continue
        endpoints.setdefault(row['mode'],{})[int(row['N'])]=enrich(row)
    pairs={};orders={}
    for mode,seq in endpoints.items():
        pairs[mode]={n:difference(x,seq[2*n]) for n,x in seq.items() if 2*n in seq}
        orders[mode]={}
        for n,pair in pairs[mode].items():
            if 2*n not in pairs[mode]:continue
            other=pairs[mode][2*n]
            orders[mode][n]={
                'raw':{k:order(v,other['delta'][k]) for k,v in pair['delta'].items()},
                'combined':{k:order(v,other['combined_channels_K'][k]) for k,v in pair['combined_channels_K'].items()},
            }
    excess={}
    for on,off in [('physical_gl2','source_off_gl2'),('physical_midpoint','source_off_midpoint'),('common_combined','source_off')]:
        excess[on]={}
        for n,p in pairs[on].items():
            q=pairs[off][n]
            excess[on][n]={
                'delta_T_K':p['delta']['T_K']-q['delta']['T_K'],
                'raw_differences':{k:v-q['delta'][k] for k,v in p['delta'].items()},
                'combined_channels_K':{k:v-q['combined_channels_K'][k] for k,v in p['combined_channels_K'].items()},
            }
    off_rows=[x for x in rows if x['mode'].startswith('source_off')]
    off_inventory={'rows':len(off_rows),
        'maximum_photons_per_H':max(D(x['photons_per_H']) for x in off_rows),
        'maximum_photo_events_per_H':max(sum((D(x[k]) for k in ('photo_HI','photo_HeI','photo_HeII')),D(0)) for x in off_rows)}
    excess_orders={mode:{n:order(pair['delta_T_K'],seq[2*n]['delta_T_K'])
        for n,pair in seq.items() if 2*n in seq} for mode,seq in excess.items()}
    clock={}
    for mode in ('source_off','source_off_midpoint','source_off_gl2'):
        clock[mode]={}
        for n,pair in pairs[mode].items():
            history=[x for x in rows if x['mode']==mode and int(x['N'])==n]
            penultimate,terminal=history[-2:]
            slope=(D(terminal['T_K'])-D(penultimate['T_K']))/(D(terminal['X'])-D(penultimate['X']))
            clock[mode][n]={'delta_X':pair['delta']['X'],
                'last_step_secant_K_per_X':slope,
                'first_order_endpoint_displacement_estimate_K':slope*pair['delta']['X'],
                'actual_delta_T_K':pair['delta']['T_K'],
                'interpretation':'Native endpoint secant diagnostic, not an exact resampling or promoted convergence order.'}
    result['intervals'][tag]={'endpoints':endpoints,'refinement_pairs':pairs,'observed_orders':orders,
        'on_minus_segmented_off_refinement':excess,'on_minus_segmented_off_orders':excess_orders,
        'source_off_photon_inventory':off_inventory,'source_off_endpoint_clock_diagnostic':clock}
    print('\nINTERVAL',tag)
    for mode in endpoints:
        print('\nMODE',mode)
        for n,p in pairs[mode].items():
            c=p['combined_channels_K']
            print('N',n,'dT',float(p['delta']['T_K']),'d_w_K',float(p['eos_w_K']),'d_e_K',float(p['eos_e_K']),
                  'pT',orders[mode].get(n,{}).get('raw',{}).get('T_K'),
                  'dSourceN',float(p['delta']['source_N']), 'dPhotons',float(p['delta']['photons_per_H']),
                  'channels',json.dumps({k:float(v) for k,v in c.items()}))
    print('\nGL2_RAW_DIFFS')
    for n,p in pairs['physical_gl2'].items():
        keys=('source_N','source_U','photo_total','photo_heat_eV_H','photo_HI','photo_HeI','photo_HeII','CI_binding_eV_H','CE_total_eV_H','RR_total_eV_H','DR_HeII_eV_H','FF_eV_H','CMB_eV_H','thermal_work_eV_H','photon_work_eV_H','escape_eV_H','boundary_U_eV_H','gas_residual_eV_H','electron_event_residual_H')
        print('N',n,json.dumps({k:float(p['delta'][k]) for k in keys}))
OUTPUT.mkdir(exist_ok=True)
(OUTPUT/'native_refinement_decomposition.json').write_text(json.dumps(serializable(result),indent=2)+'\n')
print('SAVED',OUTPUT/'native_refinement_decomposition.json')
