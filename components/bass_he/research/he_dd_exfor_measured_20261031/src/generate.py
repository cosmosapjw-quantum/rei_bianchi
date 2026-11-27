"""Emit actual EXFOR-measured source tables and conditional first-hit FLRW physics.

Run from parent checkout or full private restoration ZIP. Scientifically distinct
EXFOR reaction codes are never silently identified with each other.
"""
from __future__ import annotations
import sys, json, csv,math,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from exfor_source import get_datasets,checksum,normalized_catalog,cross_section_rows,write_csv,PRIMARY_IDS
from physics_from_exfor import (prior_sigma_nb, measured_model_comparison, anchored_local_physics,
obs_absorption_fraction,model_1958_integrated,polarization_energy_near_90,
JETP1958_TABLE_I,sigma_cyburt_cm2,absorption_anchored_first_hit,model_photoabsorption_gap)

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
INPUT=WORK/'private_source'
D=ROOT/'data';F=ROOT/'figures';D.mkdir(exist_ok=True);F.mkdir(exist_ok=True)
plt.rcParams['svg.hashsalt']='BASS_HE_EXFOR_MEASURED_20261031_fixed'
RAW_SHA='09df36e79f6c050dd7b0c6ae434805a4957bedd2e5a7132479c1c94daa90dd5d'
JETP_SHA='7cb9676493bfc68579e0ff015cc841c4f0d1a8b0c70b1e8b22a0ce90cc36b420'

def save_fig(name):
    plt.savefig(F/(name+'.png'),dpi=170,bbox_inches='tight',metadata={'Software':'BASS_HE-exfor-source'})
    plt.savefig(F/(name+'.svg'),bbox_inches='tight',metadata={'Date':'2026-10-31','Creator':'BASS_HE-exfor-source'})
    plt.close()

def main():
    raw=INPUT/'X4sShowX4StdOut.txt'
    if not raw.exists() or checksum(raw)!=RAW_SHA:raise RuntimeError('missing or changed original EXFOR source: '+str(raw))
    if checksum(INPUT/'e_007_04_0600.pdf')!=JETP_SHA:raise RuntimeError('1958 source PDF changed')
    ds=get_datasets(raw.read_text(encoding='utf-8',errors='replace'))
    catalog=normalized_catalog(ds);write_csv(D/'EXFOR_CATALOG_2270.csv',catalog)
    inventory=[]
    for k,v in ds.items():
        rows=v['rows'];energies=[r['EN'] for r in rows if r.get('EN') is not None]
        inventory.append({'subentry':k,'author':v['meta'].get('author1',''),'year':v['meta'].get('year',''),
        'x4ref':v['meta'].get('x4ref1',''),'reaction':v['meta'].get('reaction',''),
        'quantity_units':v['units'][0],'n_numeric':len(rows),'min_point_E_MeV':min(energies) if energies else None,
        'max_point_E_MeV':max(energies) if energies else None,
        'source_role':v['source_role'],
        'not_all_independent_measured_points':True})
    write_csv(D/'EXFOR_INVENTORY_84.csv',inventory)

    pT=cross_section_rows(ds,'M0484003');dd=cross_section_rows(ds,'M0475003');obs=pT+dd
    abs=cross_section_rows(ds,'M0520002');pion=cross_section_rows(ds,'L0138002')
    four_nucleon=cross_section_rows(ds,'M0384002')
    write_csv(D/'MEASURED_EXCLUSIVE_4.csv',obs)
    write_csv(D/'MEASURED_INCLUSIVE_ABSORPTION_4.csv',abs)
    write_csv(D/'MEASURED_PION_NEAR_THRESHOLD_87.csv',pion)
    write_csv(D/'MEASURED_FOUR_NUCLEON_3.csv',four_nucleon)
    asym=[]
    for i,r in enumerate(ds['G4081002']['rows']):
        asym.append({'EXFOR_subentry':'G4081002','row_index':i+1,'E_MeV':r['EN'],
         'angle_cm_deg':r['ANG-CM'],'compiled_asymmetry':r['DATA'],
         'compiler_data_err_source_unspecified':r['DATA-ERR'],
         'author_sign_inverted':-r['DATA'],'not_absolute_cross_section':True})
    write_csv(D/'POLARIZATION_COMPILER_13.csv',asym)
    pt90,delta=polarization_energy_near_90(ds)
    write_csv(D/'POLARIZATION_90DEG_4.csv',pt90)
    gorb= [{'channel':channel,'window':window,'integrated_mb_MeV':value,'stat_mb_MeV':error,
            'source':'JETP_7_p601_Table_I_1958','same_experiment_intervals_overlap':True}
            for channel,window,value,error in JETP1958_TABLE_I]
    write_csv(D/'JETP1958_TABLE_I_6.csv',gorb)
    modelint=model_1958_integrated();write_csv(D/'JETP1958_CYBURT_COMPARE_6.csv',modelint)
    compare=measured_model_comparison(obs);write_csv(D/'OBSERVED_VS_MODEL_4.csv',compare)
    local=anchored_local_physics(obs);write_csv(D/'LOCAL_FIRST_HIT_SOURCE_ANCHORED_12.csv',local)
    fractions=obs_absorption_fraction(obs,abs);write_csv(D/'MEASURED_EXCLUSIVE_ABSORPTION_SHARE_3.csv',fractions)
    abs_local=absorption_anchored_first_hit(obs,abs);write_csv(D/'INCLUSIVE_ABSORPTION_FIRST_HIT_9.csv',abs_local)
    missing_gap=model_photoabsorption_gap(obs,abs);write_csv(D/'MODEL_VS_INCLUSIVE_GAP_3.csv',missing_gap)

    # 1997 entries M0520 and M0546 are the same experiment and must not be counted twice.
    aa=ds['M0520002']['rows'];bb=ds['M0546002']['rows']
    va={(r['EN'],r['DATA'],r['ERR-S']) for r in aa}
    vb={(r['EN'],r['DATA'],r['ERR-S']) for r in bb}
    duplicate={'entries':'M0520002_and_M0546002','same_publication':'MacCormick_PhysRevC55_1033_1997',
       'n_new_compilation':len(aa),'n_older_compilation':len(bb),
       'triplet_identical_energy_data_stat':len(va&vb),
       'new_only_energy_data_stat':sorted([list(x) for x in va-vb]),
       'old_only_energy_data_stat':sorted([list(x) for x in vb-va]),
       'claim':'one_experiment_two_EXFOR_subentry_versions_not_independent',
       'use_for_physics':'M0520002_2025_09_29_revision'}
    (D/'DUPLICATE_1997_CROSSWALK.json').write_text(json.dumps(duplicate,indent=2,ensure_ascii=False)+'\n')

    # Source-owned figures. Current plotting never manufactures missing measurements.
    E=np.linspace(200,250,201)
    plt.figure(figsize=(7,4.7))
    plt.errorbar([x['E_MeV'] for x in pT],[x['sigma_nb']/1000 for x in pT],yerr=[x['stat_nb']/1000 for x in pT],fmt='o',capsize=3,label='Arends et al. 1979 EXFOR pT (stat)')
    plt.plot(E,[sigma_cyburt_cm2(x,'pT')/1e-30 for x in E],label='Cyburt 2003 high-E function (model)')
    plt.ylabel('sigma[pT] (microbarn)');plt.xlabel('Incident gamma energy (MeV)');plt.title('He-4(gamma,p)T: direct measured anchors vs model')
    plt.grid(alpha=.25);plt.legend(fontsize=8);save_fig('PT_SOURCE_VS_CYBURT')

    plt.figure(figsize=(7,4.7))
    plt.errorbar([x['E_MeV'] for x in dd],[x['sigma_nb'] for x in dd],yerr=[x['stat_nb'] for x in dd],fmt='o',capsize=3,label='Arends et al. 1976 EXFOR dd (stat)')
    plt.step([190,201,225,249.999],[4.34]*4,where='post',label='Rice 2000 broad-bin pointwise surrogate (not measured E)')
    plt.xlabel('Incident gamma energy (MeV)');plt.ylabel('sigma[dd] (nanobarn)');plt.title('He-4(gamma,d)d: measured excitation anchors vs bin surrogate');plt.grid(alpha=.25);plt.legend(fontsize=8);save_fig('DD_SOURCE_VS_RICE')

    plt.figure(figsize=(7,4.7))
    plt.errorbar([x['E_MeV'] for x in abs],[x['sigma_nb']/1000 for x in abs],yerr=[x['stat_nb']/1000 for x in abs],fmt='o',capsize=3,label='Inclusive photoabsorption MacCormick 1997')
    plt.errorbar([x['E_MeV'] for x in pT],[x['sigma_nb']/1000 for x in pT],yerr=[x['stat_nb']/1000 for x in pT],fmt='s',capsize=3,label='Exclusive pT Arends 1979')
    plt.errorbar([x['E_MeV'] for x in four_nucleon],[x['sigma_nb']/1000 for x in four_nucleon],yerr=[x['stat_nb']/1000 for x in four_nucleon],fmt='^',capsize=3,label='2p2n TAGX 1992')
    plt.scatter([x['E_MeV'] for x in pion],[x['sigma_nb']/1000 for x in pion],s=11,alpha=.4,label='Neutral pion near threshold Barnett 2008')
    plt.yscale('symlog',linthresh=0.1);plt.xlabel('Incident gamma energy (MeV)');plt.ylabel('sigma (microbarn; symlog)');
    plt.title('Measured distinct channels: NOT the same observable');plt.legend(fontsize=7);plt.grid(alpha=.2);save_fig('HE4_DISTINCT_SOURCE_CHANNELS')

    plt.figure(figsize=(7,4.7))
    plt.errorbar([x['E_MeV'] for x in pt90],[x['A_compiler_signed'] for x in pt90],
        yerr=[x['DATA_ERR_source_type_unspecified'] for x in pt90],fmt='o-',capsize=3)
    plt.ylabel('EXFOR compiler-signed asymmetry (dimensionless)');plt.xlabel('Incident gamma energy (MeV)');
    plt.ylim(-1,0);plt.title('G4081002: pT near 90 deg, digitized angular asymmetry');plt.grid(alpha=.25);save_fig('PT_POLARIZATION_90DEG')

    measured=[x for x in modelint if x['energy_interval_MeV']=='75-170']
    plt.figure(figsize=(7,4.7))
    xx=np.arange(len(measured));lab=[x['channel'] for x in measured]
    plt.errorbar(xx-.12,[x['observed_integrated_mb_MeV'] for x in measured],yerr=[x['observed_stat_mb_MeV'] for x in measured],fmt='o',capsize=3,label='Gorbunov 1958 Table I (stat only)')
    plt.scatter(xx+.12,[x['cyburt2003_integrated_mb_MeV'] for x in measured],marker='s',label='Integrated Cyburt 2003 function')
    plt.xticks(xx,lab);plt.ylabel('Integral over 75-170 MeV (MeV millibarn)');
    plt.title('Source-integrated light-nucleus photofragmentation');plt.grid(alpha=.25);plt.legend(fontsize=8);save_fig('JETP1958_75_TO_170_INTEGRALS')

    result={'program':'BASS_HE_EXFOR_SOURCE_OWNER_20261031','source_files':{
      'EXFOR_STDOUT_SHA256':RAW_SHA,'JETP1958_PDF_SHA256':JETP_SHA},
      'source_coverage':{'subentries':84,'numeric_source_rows_all_kinds':2270,
        'measured_exclusive_150_250':len(obs), 'measured_inclusive_200_250':len(abs),
        'measured_pion_150_250':len(pion),'measured_2p2n_150_250':len(four_nucleon),
        'polarization_measurement_120_250':len(asym),'jetp_1958_integrated_rows':len(modelint),
        'new_model_conditional_local_first_hit_rows':len(local),
        'new_derived_measured_to_model_rows':len(compare),
        'new_derived_exclusive_over_absorption_rows':len(fractions),
        'new_inclusive_source_anchored_local_rows':len(abs_local),
        'new_four_channel_vs_inclusive_gap_rows':len(missing_gap),
        'source_inventory_not_independent_data':True},
      'anchor_model_comparisons':compare,
      'inclusive_photoabsorption_first_hit_sample':[x for x in abs_local if x['z']==10000],
      'measured_inclusive_vs_incomplete_model':missing_gap,
      'jetp_1958_75_to170_comparisons':measured,
      'polarization_near90_delta':delta,
      'duplicated_1997_catalog':duplicate,
      'physics_scope':'FLRW reference fixed_z LOCAL first collision with one measured channel at exact source E; others inherited model; NOT full cascade',
      'hold':{'central_dag':'28/88','he_physical_dag':'14/18','canonical_delta':0,'R_event':None,'heat_rate':None,'kappa':None,'L4':False,'PRODUCTION':'HOLD','NO_MERGE':True,'AUTO_NEXT_NODE':False},
      'source_caveats':['1958 integrals not pointwise sigma; overlapping windows correlated','EXFOR G408 compiler sign inverted; not total cross section',
      'M0520 and M0546 represent the same MacCormick 1997 campaign','pT 5-percent systematic shared across energies',
      'M0475 DD reports statistical error only; unreported systematic is unresolved, not zero',
      'no source-owned BASS gamma history, e+/- cascades, FastD total deposition, or nuclear network']}
    (D/'SCIENTIFIC_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'counts':result['source_coverage'],'figures_png':len(list(F.glob('*.png'))),
        'first_hit_sample':[x for x in local if x['z']==10000],'sha_raw':RAW_SHA},indent=2))

if __name__=='__main__':main()
