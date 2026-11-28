"""E11 exact-f64 analysis of E10 live vs E7 Endpoint readouts.

Pure data consumer: no native physics solver and no changed observational
units, atomic coefficients, or time discretization. Fail-closed identity.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
from e11.observer_alias import (
    f64,assert_same_bits,photo_weights,source,paired_alias_decomposition,
    symmetric_pair,condition,allowance_ratio,load_mode_csv
)
MODES=('OFF','KF','GM')
GAMMA=(("Gamma_hi","Gamma_HI"),("Gamma_hei","Gamma_HeI"),("Gamma_heii","Gamma_HeII"))
OWNER_KEYS={'s':'ln_a','x':'x_hii','y':'x_heii','z':'x_heiii','w':'w'}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()


def display(q:F,places=28):
    with localcontext() as c:
        c.prec=places
        return str(Decimal(q.numerator)/Decimal(q.denominator))


def parse_mode(mode, e10_root, e7_root):
    e10=load_mode_csv(e10_root/f'full_{mode}/OWNER_NATIVE_41.csv',step_column='not_present')
    side=load_mode_csv(e10_root/f'full_{mode}/OWNER_SELECTED_RCT.csv')
    hist=load_mode_csv(e7_root/f'data/histories/{mode}_N384_P512_O4.csv')
    endpoint=load_mode_csv(e7_root/f'data/endpoint/{mode}_N384_P512_O4_Q4.csv')
    rows=[]
    source_bin_checks=0
    g_live_checks=0
    for k,(n,s,h,e) in enumerate(zip(e10,side,hist,endpoint)):
        if int(s['step'])!=k or int(h['step'])!=k or int(e['step'])!=k:
            raise ValueError(f'{mode} BAD_STEP_{k}')
        for field,owner in OWNER_KEYS.items():
            assert_same_bits(n[owner],s[field],f'{mode} E10_NATIVE_VS_SIDECAR:{field}@{k}')
            assert_same_bits(n[owner],h[field],f'{mode} E10_NATIVE_VS_E7_HISTORY:{field}@{k}')
            assert_same_bits(n[owner],e[field],f'{mode} E10_NATIVE_VS_E7_ENDPOINT:{field}@{k}')
            source_bin_checks+=3
        for owner,other in GAMMA:
            assert_same_bits(n[owner],h[other],f'{mode} LIVE_GAMMA_HIST_ID:{other}@{k}')
            g_live_checks+=1
        live=tuple(f64(n[g]) for g,e_name in GAMMA)
        end=tuple(f64(e[e_name]) for o,e_name in GAMMA)
        weights=photo_weights(f64(e['nHe'])/f64(e['nH']),f64(e['x']),f64(e['y']),f64(e['z']))
        rates=tuple(allowance_ratio(live[i],end[i]) for i in range(3))
        r=source(weights,live); q=source(weights,end)
        if r-q!=sum((weights[i]*(live[i]-end[i]) for i in range(3)),F(0)):
            raise ArithmeticError('FIXED_STATE_OBSERVER_RATE_DIFFERENCE')
        rows.append({'k':k,'n':n,'h':h,'e':e,'s':f64(e['s']),
                     'weights':weights,'live':live,'endpoint':end,
                     'native_photo':r,'endpoint_photo':q,'alias_photo':r-q,'ratios':rates})
    return rows,source_bin_checks,g_live_checks


def audit(e10_root:Path,e7_root:Path,output_dir:Path):
    output_dir=Path(output_dir)
    if output_dir.exists():
        raise FileExistsError('OUTPUT_MUST_BE_NEW')
    allm={};clock_identical=0; background_identical=0; species_identity_count=0
    max_ratio={}; max_alias_by_mode={}; paired={}; data_rows=[]; paired_rows=[]
    anchor_observer_equality={}
    input_hashes={}
    for mode in MODES:
        rs,states,live_g=parse_mode(mode,e10_root,e7_root)
        assert len(rs)==385
        allm[mode]=rs
        anchor_steps=[d['k'] for d in rs if d['k']%16==0 and d['live']==d['endpoint']]
        nonanchor_equal=[d['k'] for d in rs if d['k']%16!=0 and d['live']==d['endpoint']]
        if anchor_steps!=list(range(0,385,16)):
            raise AssertionError('PINNED_E10_E7_N24_ANCHOR_PARITY_LOST')
        anchor_observer_equality[mode]={'anchors_all_three_gamma_bit_equal':len(anchor_steps),
                                      'off_anchor_all_three_gamma_bit_equal':len(nonanchor_equal)}
        input_hashes[mode]={}
        for group,p in (
            ('owner',e10_root/f'full_{mode}/OWNER_NATIVE_41.csv'),
            ('sidecar',e10_root/f'full_{mode}/OWNER_SELECTED_RCT.csv'),
            ('e7_history',e7_root/f'data/histories/{mode}_N384_P512_O4.csv'),
            ('endpoint',e7_root/f'data/endpoint/{mode}_N384_P512_O4_Q4.csv')):
            input_hashes[mode][group]=sha(p)
        for species_idx,spec in enumerate(('HI','HeI','HeII')):
            best=max(rs,key=lambda z:z['ratios'][species_idx])
            max_ratio[f'{mode}:{spec}']={
              'step':best['k'],'ratio':float(best['ratios'][species_idx]),
              'live_per_s':float(best['live'][species_idx]),
              'endpoint_per_s':float(best['endpoint'][species_idx]),
              'difference_live_minus_endpoint_per_s':float(best['live'][species_idx]-best['endpoint'][species_idx])}
        max_alias_by_mode[mode]=max(rs,key=lambda z:abs(z['alias_photo']))['k']
        species_identity_count+=3*len(rs)
        for d in rs:
            data_rows.append({'mode':mode,'step':d['k'],'s':str(float(d['s'])),
              'native_photo_per_H_s':display(d['native_photo']),
              'endpoint_photo_per_H_s':display(d['endpoint_photo']),
              'alias_per_H_s':display(d['alias_photo']),
              'rate_HI_ratio':str(float(d['ratios'][0])),
              'rate_HeI_ratio':str(float(d['ratios'][1])),
              'rate_HeII_ratio':str(float(d['ratios'][2]))})
    for k in range(385):
        for mode in ('KF','GM'):
            x=allm['OFF'][k];y=allm[mode][k]
            assert_same_bits(x['e']['s'],y['e']['s'],'MODE_PAIRED_CLOCK')
            clock_identical+=1
            for key in ('nH','nHe','H'):
                assert_same_bits(x['e'][key],y['e'][key],f'PAIRED_BACKGROUND_{key}')
                background_identical+=1
            for rates in ('live','endpoint'):
                vals=symmetric_pair(x['weights'],y['weights'],x[rates],y[rates])
                if vals['delta']!=source(y['weights'],y[rates])-source(x['weights'],x[rates]):
                    raise ArithmeticError('SYMMETRIC_PAIRED_SOURCE')
            both=paired_alias_decomposition(x['weights'],y['weights'],x['live'],y['live'],x['endpoint'],y['endpoint'])
            native=y['native_photo']-x['native_photo']
            endpoint=y['endpoint_photo']-x['endpoint_photo']
            assert both['total']==native-endpoint
            paired_rows.append({'mode':mode,'step':k,'s':str(float(y['s'])),
              'delta_native':display(native),'delta_endpoint':display(endpoint),
              'difference_alias':display(both['total']),
              'observer_rate_difference':display(both['rate']),
              'observer_occupancy_difference':display(both['occupancy']),
              'relative_alias_vs_endpoint_signal':str(float(abs(both['total']/endpoint))) if endpoint else '',
              'alias_cancellation_condition':str(float(condition(both['rate'],both['occupancy']))) if both['total'] else ''})
    for mode in ('KF','GM'):
        q=[r for r in paired_rows if r['mode']==mode]
        with_signal=[a for a in q if a['relative_alias_vs_endpoint_signal']!='']
        big=max(q,key=lambda r:abs(float(r['difference_alias'])))
        worst_relative=max(with_signal,key=lambda r:float(r['relative_alias_vs_endpoint_signal']))
        end=q[-1]
        sign_changes={}
        for key in ('delta_native','delta_endpoint'):
            last_nonzero_sign=0;crossings=[]
            for rec in q:
                v=F(rec[key]);sign=(v>0)-(v<0)
                if sign and last_nonzero_sign and sign != last_nonzero_sign:
                    crossings.append([rec['step']-1,rec['step']])
                if sign: last_nonzero_sign=sign
            sign_changes[key]=crossings
        paired[mode]={
          'paired_rows':len(q),
          'last_native':end['delta_native'],
          'last_endpoint':end['delta_endpoint'],
          'last_alias':end['difference_alias'],
          'last_alias_rate_term':end['observer_rate_difference'],
          'last_alias_occupancy_term':end['observer_occupancy_difference'],
          'max_abs_alias_step':big['step'],
          'max_abs_alias_per_H_s':big['difference_alias'],
          'largest_nonzero_relative_alias_step':worst_relative['step'],
          'largest_nonzero_relative_alias_over_endpoint_signal':worst_relative['relative_alias_vs_endpoint_signal'],
          'paired_source_sign_change_brackets':sign_changes}
    result={
      'task':'HE_E11_GAMMA_OBSERVER_ALIAS_PAIRED_PHOTO_SOURCE',
      'claim':'EXACT_SAVED_F64_OBSERVER_ALIAS_TRANSFER__NOT_TRUE_ERROR',
      'source_identity':'EXACT_E10_AND_E7_PINNED_CSV_FROM_ARCHIVE',
      'state_and_gamma_identity':{'mode_rows':1155,'exact_E10_E7_state_clock_checks':1155*5*3,'exact_live_gamma_checks':1155*3,'mode_matched_clocks':clock_identical,'mode_matched_background_fields':background_identical},
      'exact_source_per_species_cases':species_identity_count,
      'exact_paired_source_and_alias_decompositions':770,
      'anchor_observer_equality':anchor_observer_equality,
      'max_rate_alias_e7_allowance_ratio':max_ratio,
      'max_absolute_photo_source_alias_epoch_by_mode':max_alias_by_mode,
      'paired':paired,
      'selected_epochs':{},
      'missing_ledger_fields':['BH','BY','BZ','bindMicro','thermalMicro'],
      'nonidentifiable_from_E10_output':True,
      'photo_heat_moment':None,
      'feedback_into_solver':False,
      'physical_admission':False,
      'new_native_steps':0,
      'input_hashes':input_hashes}
    for step in (0,1,16,59,192,384):
        result['selected_epochs'][str(step)]={}
        for mode in MODES:
            d=allm[mode][step]
            result['selected_epochs'][str(step)][mode]={
                'native_gamma':[float(g) for g in d['live']],
                'endpoint_gamma':[float(g) for g in d['endpoint']],
                'native_source':float(d['native_photo']),
                'endpoint_source':float(d['endpoint_photo']),
                'observer_source_delta':float(d['alias_photo'])}
    # Atomic output: prepare in memory and create a fresh directory only after all identity and math assertions pass.
    output_dir.mkdir(parents=True)
    for name,rows in (('OBSERVER_SOURCE.csv',data_rows),('PAIRED_OBSERVER_ALIAS.csv',paired_rows)):
        with (output_dir/name).open('x',newline='') as fh:
            writer=csv.DictWriter(fh,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            fh.flush();os.fsync(fh.fileno())
    with (output_dir/'RESULTS.json').open('x') as fh:
        json.dump(result,fh,indent=2,sort_keys=True);fh.write('\n');fh.flush();os.fsync(fh.fileno())
    return result


if __name__=='__main__':
    if len(sys.argv)!=4:
        raise SystemExit('USAGE python -m e11.run_analysis EXTRACTED_E10 EXTRACTED_E7 FRESH_OUTPUT_DIR')
    r=audit(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
    print('E11_DONE modes3 rows1155 paired770')
    print('E11_WORST_RATE',max((v['ratio'],k) for k,v in r['max_rate_alias_e7_allowance_ratio'].items()))
    print('E11_PAIRED',r['paired'])
