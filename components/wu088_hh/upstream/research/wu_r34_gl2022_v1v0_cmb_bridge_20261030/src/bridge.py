"""Source-locked conditional HD(v1) quench -> HD(v0,J<=4) CMB/chemistry bridge.

This computes NEW conditionally joined observables from frozen R32 and R33,
NOT an EMAA numeric crosswalk, full kinetic system, or cosmic rate.

The selection event is first vibrational quench landing in J=0..4. Missing
v1 chemistry, v1 radiation, v0 higher-J evolution remain OUTSIDE the model.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,io,json,math,sys,zipfile
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.optimize import brentq

R33_SHA='8036d1d4cae599a1dc113612e67146fa8b822224b074f827ae2c0d9684e7a362'
R32_SHA='01482fdefef303b8cc00bd0efe9b20c23d1886a69679d76eec9d67434fe643e7'
PACKAGE_ROOT=Path(__file__).resolve().parents[1]
R33_ZIP=PACKAGE_ROOT/'archive/WU_R33_SOURCE_ORIGINAL_20261030.zip'
R33_RESTORED=PACKAGE_ROOT/'parents/R33'
R32_ZIP=R33_RESTORED/'archive/WU_R32_SOURCE_ORIGINAL_20261030.zip'
R32_MODES=('DB_UPWARD_V1','DOWN_ONLY_COUNTERFACTUAL')
R33_MODES=('raw_SQM','Eq6-7_spin_effective')
COMMON_T=(55,105,255,505,1005,3005)
DENSITY_RATIOS=(0.1,1.0,10.0)
CMB_LABELS=('OFF','z0','z5','z10','z30','z100','z300')
Z_MAP={'OFF':None,'z0':0,'z5':5,'z10':10,'z30':30,'z100':100,'z300':300}
CMJ=100*6.62607015e-34*299792458.


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def csv_rows(data:bytes):return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))

def rows_from(path):return csv_rows(Path(path).read_bytes())

def r32_rows(name):
    with zipfile.ZipFile(R32_ZIP) as z:return csv_rows(z.read('results/'+name))

def prepare_parent():
    """Restore the immutable original archive without a network dependency."""
    if not R33_ZIP.exists() or sha(R33_ZIP)!=R33_SHA:
        raise RuntimeError('R33 immutable archive missing or changed')
    if not (R33_RESTORED/'results/R33_CMB_CASES_1470.csv').exists():
        R33_RESTORED.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(R33_ZIP) as z:
            for info in z.infolist():
                if Path(info.filename).is_absolute() or '..' in Path(info.filename).parts:
                    raise RuntimeError('unsafe path in original zip')
            z.extractall(R33_RESTORED)

_R33_MODULE=None
def load_r33():
    global _R33_MODULE
    if _R33_MODULE is None:
        path=R33_RESTORED/'src/cmb5.py'
        spec=importlib.util.spec_from_file_location('wu_r33_origin_cmb5',path)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        _R33_MODULE=mod
    return _R33_MODULE

def lock_inputs():
    prepare_parent()
    for file_,digest in [(R32_ZIP,R32_SHA),(R33_ZIP,R33_SHA)]:
        if not file_.exists() or sha(file_)!=digest:raise RuntimeError('Source archive SHA mismatch '+str(file_))
        with zipfile.ZipFile(file_) as z:
            if z.testzip() is not None:raise RuntimeError('ZIP CRC failed '+str(file_))
    with zipfile.ZipFile(R33_ZIP) as z:
        manifest=json.loads(z.read('evidence/MANIFEST_SHA256.json'))
        # Only the source bytes, original previously hashed archive and parent source file are used.
    # Pins to exact previously published R33 result tables, independently computed hashes.
    pins={'R33_CMB_CASES_1470.csv':'69e04edf70949e861279bf97d8f0960a8069795fbb0af7416f2f0452947226f1',
      'R33_CMB_LINES_5880.csv':'9b935ec5beecfd4f6784378e5ad28d3d84ca70339c204bc9336ad496e2315f59',
      'R33_H2_PRODUCTS_14700.csv':'dfbbc692fffebdea5f1a985a4c047f5ef6d5c0b76c7c0b3ae80efbf1edab05f7'}
    for fn,h in pins.items():
        f=R33_RESTORED/'results'/fn
        if sha(f)!=h:raise RuntimeError('R33 result content drift '+fn)
    return pins

def r33_key(r):return (int(r['Tgas_K']),r['policy'],float(r['n_over_ncrit_J2']),int(r['initial_HD_J']),r['CMB_label'])

def r32_key(r):return (int(r['T_K']),r['mode'],int(r['initial_v1_J']))

def load_inputs():
    atlas={r32_key(r):r for r in r32_rows('ATLAS_QUENCH_126.csv')}
    group=defaultdict(list)
    for r in r32_rows('TERMINAL_V0_BRANCHES_1386.csv'):
        group[r32_key(r)].append(r)
    assert len(atlas)==126 and len(group)==126
    r33_cases={r33_key(r):r for r in rows_from(R33_RESTORED/'results/R33_CMB_CASES_1470.csv')}
    r33_products=defaultdict(list);r33_lines=defaultdict(list)
    for r in rows_from(R33_RESTORED/'results/R33_H2_PRODUCTS_14700.csv'):r33_products[r33_key(r)].append(r)
    for r in rows_from(R33_RESTORED/'results/R33_CMB_LINES_5880.csv'):r33_lines[r33_key(r)].append(r)
    assert len(r33_cases)==1470 and all(len(v)==10 for v in r33_products.values()) and all(len(v)==4 for v in r33_lines.values())
    return atlas,group,r33_cases,r33_products,r33_lines

def calc_case(T,v1mode,j1,mode,ratio,rad,atlas,group,cases,prods,lines):
    key1=(T,v1mode,j1)
    branches=group[key1]
    if len(branches)!=11 or {int(r['terminal_v0_J']) for r in branches}!=set(range(11)):
        raise RuntimeError('R32 missing a source branch')
    p=[float(x['restricted_probability']) for x in sorted(branches,key=lambda x:int(x['terminal_v0_J']))]
    if abs(sum(p)-1)>1e-12 or min(p)<0:raise RuntimeError('R32 normalization')
    retained=p[:5];w=sum(retained)
    if not 0<w<=1+1e-12:raise RuntimeError('R32 retention outside (0,1]')
    case=[cases[(T,mode,ratio,j,rad)] for j in range(5)]
    if len({float(r['nHplus_cm-3']) for r in case})!=1:
        raise RuntimeError('R33 density depends on start J')
    E1=float(atlas[key1]['initial_HD_energy_J'])
    E2=[float(sorted(branches,key=lambda x:int(x['terminal_v0_J']))[j]['terminal_E_cm-1'])*CMJ for j in range(5)]
    E3=[float(c['initial_HD_rotational_J']) for c in case]
    R32heat=sum(retained[j]*(E1-E2[j]) for j in range(5))
    seam=sum(retained[j]*(E2[j]-E3[j]) for j in range(5))
    weighted=lambda name:sum(retained[j]*float(case[j][name]) for j in range(5))
    Erad=weighted('net_radiative_transfer_J')
    bath=weighted('collisional_proton_bath_gain_J')
    terminal=weighted('pre_reaction_HD_rotational_J')
    defect=w*E1 - (R32heat+seam+bath+Erad+terminal)
    weighted_prob_none=weighted('prob_reaction_before_any_radiation')
    weighted_prob_rad=weighted('prob_any_radiative_interaction_before_reaction')
    if abs(w-(weighted_prob_none+weighted_prob_rad))>6e-13:raise RuntimeError('first-event probability mismatch')
    if abs(defect)>3.e-32:raise RuntimeError('two-stage energy representation ledger mismatch')
    # Convert post-quench product probability from each R33 initial level into
    # joint probabilities per initial v1 molecule, NOT conditional renormalization.
    P=[]
    for final in range(10):
        terms=[prods[(T,mode,ratio,j,rad)][final] for j in range(5)]
        if any(int(t['H2_final_Jprime'])!=final for t in terms):raise RuntimeError('R33 H2 ordering drift')
        anyp=sum(retained[j]*float(terms[j]['probability_all']) for j in range(5))
        nop=sum(retained[j]*float(terms[j]['joint_no_radiation']) for j in range(5))
        P.append((anyp,nop,anyp-nop))
    if abs(sum(z[0] for z in P)-w)>6e-13 or min(z[2] for z in P)<-3e-13:
        raise RuntimeError('restricted H2 probability mass mismatch')
    L=[]
    for line in range(1,5):
        terms=[lines[(T,mode,ratio,j,rad)][line-1] for j in range(5)]
        if any(int(t['line_upper_J'])!=line for t in terms):raise RuntimeError('R33 line ordering drift')
        L.append({'upper_J':line,'net_radiation_J_per_initial_v1':sum(retained[j]*float(terms[j]['net_line_radiation_J']) for j in range(5)),
            'expected_spontaneous_photons_per_initial_v1':sum(retained[j]*float(terms[j]['expected_spontaneous_emissions']) for j in range(5)),
            'expected_stimulated_photons_per_initial_v1':sum(retained[j]*float(terms[j]['expected_stimulated_emissions']) for j in range(5)),
            'expected_absorptions_per_initial_v1':sum(retained[j]*float(terms[j]['expected_CMB_absorptions']) for j in range(5))})
    if abs(sum(t['net_radiation_J_per_initial_v1'] for t in L)-Erad)>5e-32:
        raise RuntimeError('line transfer energy mismatch')
    record={'Tgas_K':T,'v1_quench_policy':v1mode,'initial_v1_J':j1,'v0_spin_policy':mode,
        'n_over_ncrit_J2':ratio,'CMB_label':rad,'T_rad_K':float(case[0]['T_rad_K']),
        'nHplus_cm-3':float(case[0]['nHplus_cm-3']),
        'quench_enter_J0to4_probability':w,'quench_outside_J0to4_probability':sum(p[5:]),
        'selected_reaction_H2_probability_per_initial_v1':sum(z[0] for z in P),
        'selected_reaction_before_radiation_probability':weighted_prob_none,
        'selected_first_radiation_before_reaction_probability':weighted_prob_rad,
        'selected_H2_odd_Jprime_probability_per_initial_v1':sum(P[j][0] for j in (1,3,5,7,9)),
        'selected_H2_odd_share_conditional_on_J0to4':sum(P[j][0] for j in (1,3,5,7,9))/w,
        'selected_spontaneous_photons_per_initial_v1':weighted('spont_emissions_per_initial'),
        'selected_stimulated_photons_per_initial_v1':weighted('stim_emissions_per_initial'),
        'selected_CMB_absorptions_per_initial_v1':weighted('CMB_absorptions_per_initial'),
        'selected_net_radiation_J_per_initial_v1':Erad,
        'selected_quench_proton_bath_gain_R32_J':R32heat,
        'selected_energetic_representation_seam_J':seam,
        'selected_postquench_proton_bath_gain_R33_J':bath,
        'selected_prechemistry_HD_rotational_energy_J':terminal,
        'selected_initial_v1_internal_energy_weighted_J':w*E1,
        'conditional_energy_ledger_residual_J':defect,
        'selected_postquench_wait_s_per_initial_v1':weighted('mean_reaction_wait_s'),
        'full_kinetic_network':False,'emaa_raw_comparison':False}
    base={k:record[k] for k in ('Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label')}
    product_rows=[dict(base,**{'H2_final_Jprime':j,'probability_per_initial_v1':P[j][0],
        'before_first_radiation_joint':P[j][1],'at_least_one_radiation_joint':P[j][2]}) for j in range(10)]
    line_rows=[dict(base,**r) for r in L]
    return record,product_rows,line_rows

def write_csv(p,rows):
    with Path(p).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def rad_on_mixture(parent,grid,T,mode,ratio,w,z):
    r33=load_r33()
    nHp=parent.reference_density(grid,T,mode)*ratio
    G,_,C,Q,rad=r33.assemble(parent,grid,T,mode,nHp,r33.T0*(1+z))
    m=np.linalg.solve(-G,np.array(w,dtype=float))
    return sum((sp*m[j]+stim*m[j]-ab*m[j-1])*r33.CMJ*cm1 for j,cm1,sp,stim,ab,_ in rad)

def generate(out:Path,with_roots=True):
    lock_inputs()
    atlas,group,cases,prods,lines=load_inputs()
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    allcases=[];prodrows=[];linerows=[];rootrows=[]
    max_defect=0
    for T in COMMON_T:
      for v1mode in R32_MODES:
       for j1 in range(7):
        for mode in R33_MODES:
         for ratio in DENSITY_RATIOS:
          for rad in CMB_LABELS:
            rec,p,l=calc_case(T,v1mode,j1,mode,ratio,rad,atlas,group,cases,prods,lines)
            allcases.append(rec);prodrows.extend(p);linerows.extend(l)
            max_defect=max(max_defect,abs(rec['conditional_energy_ledger_residual_J']))
    if len(allcases)!=3528 or len(prodrows)!=35280 or len(linerows)!=14112:raise AssertionError('grid counts')
    write_csv(dest/'BRIDGE_CASES_3528.csv',allcases)
    write_csv(dest/'BRIDGE_H2_PRODUCTS_35280.csv',prodrows)
    write_csv(dest/'BRIDGE_LINE_PHOTONS_14112.csv',linerows)
    if with_roots:
      r33=load_r33()
      parent,_,grid,_=r33.get_parent()
      for T in COMMON_T:
       for v1mode in R32_MODES:
        for j1 in range(7):
         b=group[(T,v1mode,j1)]
         w=[float(x['restricted_probability']) for x in sorted(b,key=lambda r:int(r['terminal_v0_J']))[:5]]
         for mode in R33_MODES:
          for ratio in DENSITY_RATIOS:
           f0=rad_on_mixture(parent,grid,T,mode,ratio,w,0.)
           f300=rad_on_mixture(parent,grid,T,mode,ratio,w,300.)
           a=sum(w[j]*float(cases[(T,mode,ratio,j,'z0')]['net_radiative_transfer_J']) for j in range(5))
           b300=sum(w[j]*float(cases[(T,mode,ratio,j,'z300')]['net_radiative_transfer_J']) for j in range(5))
           if abs(a-f0)>5e-31 or abs(b300-f300)>5e-31:raise AssertionError('direct vs R33 source endpoint mismatch')
           root=float(brentq(lambda z:rad_on_mixture(parent,grid,T,mode,ratio,w,z),0,300,xtol=1e-9,rtol=1e-11)) if f0*f300<0 else None
           residual=rad_on_mixture(parent,grid,T,mode,ratio,w,root) if root is not None else None
           rootrows.append({'Tgas_K':T,'v1_quench_policy':v1mode,'initial_v1_J':j1,'v0_spin_policy':mode,
              'n_over_ncrit_J2':ratio,'z0_radiation_J_per_initial_v1':f0,'z300_radiation_J_per_initial_v1':f300,
              'endpoint_sign_change':f0*f300<0,'z_balance_on_0to300':root,'T_CMB_balance_K':None if root is None else r33.T0*(1+root),
              'root_residual_J_per_initial_v1':residual,'uniqueness_not_claimed':True})
      if len(rootrows)!=504:raise AssertionError('root candidate count')
      write_csv(dest/'BRIDGE_RADIATION_BALANCE_504.csv',rootrows)
    summary={'schema':'wu.r34.gl2022_two_stage_conditional_bridge.v1','science_classification':'DERIVED_SOURCE_QUALIFIED_AUXILIARY_NO_CANONICAL_PROMOTION',
        'n_cases':len(allcases),'H2_product_rows':len(prodrows),'line_resolved_rows':len(linerows),'root_candidates':len(rootrows),
        'bracketed_roots':sum(bool(x['endpoint_sign_change']) for x in rootrows),'max_two_stage_energy_seam_J':max(abs(r['selected_energetic_representation_seam_J']) for r in allcases),
        'max_energy_residual_J':max_defect,
        'max_reaction_probability_mass_error':max(abs(r['selected_reaction_H2_probability_per_initial_v1']-r['quench_enter_J0to4_probability']) for r in allcases),
        'max_first_rad_partition_error':max(abs(r['selected_first_radiation_before_reaction_probability']+r['selected_reaction_before_radiation_probability']-r['quench_enter_J0to4_probability']) for r in allcases),
        'max_roots_abs_residual_J':max((abs(r['root_residual_J_per_initial_v1']) for r in rootrows if r['endpoint_sign_change']),default=None),
        'shared_source_T_K':list(COMMON_T),'held_source_T_2005_K':'R32_MALFORMED_TOKEN_NOT_IMPUTED',
        'v1_modes':list(R32_MODES),'v0_policies':list(R33_MODES),'density_ratios':list(DENSITY_RATIOS),'CMB_labels':list(CMB_LABELS),
        'source_SHA256':{'R33_full_original_zip':R33_SHA,'R32_full_original_zip':R32_SHA},
        'emaa_171x25_raw':'NOT_ACQUIRED','actual_EMAA_comparisons':0,'canonical_DAG':'34/49_UNCHANGED',
        'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','native_subagent':'NOT_EXPOSED',
        'PES_native_threshold':None,'physical_Q':None,'owner_ACK':None,'HH_R10':'OFF',
        'FULL_A':None,'L4':False,'PRODUCTION':'NOT_ISSUED','main_merge':False,
        'sample_105K_v1J0_DB_v0spin_ratio1_z100':next(x for x in allcases if x['Tgas_K']==105 and x['v1_quench_policy']=='DB_UPWARD_V1' and x['initial_v1_J']==0 and x['v0_spin_policy']=='Eq6-7_spin_effective' and x['n_over_ncrit_J2']==1 and x['CMB_label']=='z100'),
        'source_scope':'Conditional first v1 vibrational quench to v0 J0-4, then R33 chemistry/radiation; outside J5-10 and omitted v1 radiation/reaction are NOT physical zeros; no v0 high-J reinjection or transport.'}
    (dest/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--no-roots',action='store_true');args=ap.parse_args()
    s=generate(args.out,not args.no_roots)
    print(json.dumps({k:s[k] for k in ('n_cases','H2_product_rows','line_resolved_rows','root_candidates','bracketed_roots','max_two_stage_energy_seam_J','max_energy_residual_J','max_reaction_probability_mass_error','max_first_rad_partition_error','max_roots_abs_residual_J')},indent=2))