"""Finite absorbing CTMC photon counting statistics for original WU R34 mixture.

All data are derived from unmodified source-locked R34 -> R33 -> R32 archives.
The full counting statistics are conditional on R32 first-quench arrival in
HD(v=0,J=0..4) under the R34 source-restricted two-stage model.
"""
from __future__ import annotations
import csv, importlib.util, json, math, sys, hashlib, zipfile
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parents[1]
PARENT_SHA='a43d9fa8a39f64bde756b9b2d942b831d3d2560717198dac98a0a228bf5a370e'
PARENT_ZIP=P/'archive/WU_R34_SOURCE_ORIGINAL_20261030.zip'
PARENT_DIR=P/'parents/R34'
SOURCE_PARENT_DIRNAME='WU_R34_SOURCE_ORIGINAL_20261030.zip'
E0=100*100*6.62607015e-34*299792458.  # 100 inverse centimeters in joules
BRIDGE=None

def hash_file(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()

def import_bridge():
    global BRIDGE
    if BRIDGE is None:
        if not PARENT_ZIP.exists() or hash_file(PARENT_ZIP)!=PARENT_SHA:
            raise RuntimeError('immutable parent R34 archive missing or wrong SHA-256')
        with zipfile.ZipFile(PARENT_ZIP) as z:
            if z.testzip() is not None: raise RuntimeError('parent CRC failure')
            if not (PARENT_DIR/'src/bridge.py').exists():
                for m in z.namelist():
                    path=Path(m)
                    if path.is_absolute() or '..' in path.parts:
                        raise RuntimeError('parent contains dangerous paths')
                z.extractall(PARENT_DIR)
        modname='wu_r34_fcs_owner'
        spec=importlib.util.spec_from_file_location(modname,PARENT_DIR/'src/bridge.py')
        bridge=importlib.util.module_from_spec(spec)
        sys.modules[modname]=bridge
        spec.loader.exec_module(bridge)
        bridge.lock_inputs()
        BRIDGE=bridge
    return BRIDGE

def counting_operators(rates):
    """Derivative matrices of tilted generator w.r.t. energy and counts.

    Column-state convention. Off diagonal only (the ESCAPE/LOSS diagonal is
    always untilted). Emission positive energy into radiation; absorption negative.
    """
    De=np.zeros((5,5),float)
    Ds=np.zeros((5,5),float)
    Ce=np.zeros((5,5),float)
    Ca=np.zeros((5,5),float)
    for j,cm1,sp,stim,absr,occupation in rates:
        E=cm1*100*6.62607015e-34*299792458.
        d=sp+stim
        De[j-1,j]+=d*E
        De[j,j-1]-=absr*E
        Ds[j-1,j]+=d*E*E
        Ds[j,j-1]+=absr*E*E
        Ce[j-1,j]+=d
        Ca[j,j-1]+=absr
    return De,Ds,Ce,Ca

def tilted_mgf(G,chem,rad,initial,lam_scaled):
    """Independent direct tilted-resolvent evaluation for finite differences.

    lam_scaled is dimensionless; each radiative transition is weighted by
    exp(lam_scaled * delta_E/E0). This is NOT the implementation used for moments.
    """
    A=G.copy()
    for j,cm1,sp,stim,absr,_ in rad:
        x=lam_scaled*(cm1*100*6.62607015e-34*299792458.)/E0
        A[j-1,j]+=(sp+stim)*math.expm1(x)
        A[j,j-1]+=absr*math.expm1(-x)
    q=chem.sum(axis=0)
    return float(q@np.linalg.solve(-A,initial))

def moments(G,chem,rad,initial,check_mass=True):
    """Compute exact first and second moments (resolvent matrix solves)."""
    if initial.shape!=(5,) or np.any(initial<-1e-15):raise ValueError('invalid initial distribution')
    q=chem.sum(axis=0)
    if min(q)<=0:raise ValueError('chemical absorption not positive on all states')
    resident=np.linalg.solve(-G,initial)
    mass=q@resident
    if check_mass and abs(mass-float(sum(initial)))>5e-11:
        raise AssertionError('absorption probability mass defect')
    d,s,em,ab=counting_operators(rad)
    one=np.ones(5)
    energy_mean=one@(d@resident)
    energy_second=one@(s@resident)+2*one@(d@np.linalg.solve(-G,d@resident))
    # these are conditional expectations when initial sums to unity
    energy_variance=energy_second-energy_mean**2
    mean_em=one@(em@resident)
    mean_abs=one@(ab@resident)
    sec_em=mean_em+2*one@(em@np.linalg.solve(-G,em@resident))
    sec_abs=mean_abs+2*one@(ab@np.linalg.solve(-G,ab@resident))
    cross=one@(em@np.linalg.solve(-G,ab@resident)+ab@np.linalg.solve(-G,em@resident))
    covariance=cross-mean_em*mean_abs
    var_em=sec_em-mean_em**2
    var_abs=sec_abs-mean_abs**2
    if energy_variance<-1e-37 or min(var_em,var_abs)<-1e-8:
        raise AssertionError('negative variance from computed probability law')
    return {'mean_signed_photon_energy_J':float(energy_mean),
            'second_signed_photon_energy_J2':float(energy_second),
            'variance_signed_photon_energy_J2':float(energy_variance),
            'std_signed_photon_energy_J':float(math.sqrt(max(0.,energy_variance))),
            'mean_emitted_photons':float(mean_em),
            'mean_absorbed_photons':float(mean_abs),
            'variance_emitted_photons':float(var_em),
            'variance_absorbed_photons':float(var_abs),
            'covariance_emitted_absorbed_photons':float(covariance),
            'probability_chemical_absorption':float(mass)}

def initial_mix(bridge,branches):
    ss=sorted(branches,key=lambda x:int(x['terminal_v0_J']))
    if {int(r['terminal_v0_J']) for r in ss} !=set(range(11)):
        raise AssertionError('missing R32 quench branch')
    weights=np.array([float(r['restricted_probability']) for r in ss[:5]],dtype=float)
    w=float(weights.sum())
    if not 0<w<1 or abs(sum(float(r['restricted_probability']) for r in ss)-1)>5e-12:
        raise AssertionError('source branch normalization/positive selection')
    return weights/w, w

def run_case(bridge,parent,grid,case,branches):
    T=int(case['Tgas_K'])
    j=int(case['initial_v1_J'])
    v1policy=case['v1_quench_policy']
    policy=case['v0_spin_policy']
    ratio=float(case['n_over_ncrit_J2'])
    lab=case['CMB_label']
    radT=float(case['T_rad_K'])
    nH=float(case['nHplus_cm-3'])
    initial,w=initial_mix(bridge,branches[(T,v1policy,j)])
    rr=bridge.load_r33()
    G,G0,C,Q,rad=rr.assemble(parent,grid,T,policy,nH,radT)
    s=moments(G,Q,rad,initial)
    E_owner=float(case['selected_net_radiation_J_per_initial_v1'])/w
    if abs(s['mean_signed_photon_energy_J']-E_owner)>1e-30:
        raise AssertionError('R34 photon energy mean mismatch')
    return dict({k:case[k] for k in ['Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label','T_rad_K','nHplus_cm-3']},
        selected_quench_probability=w,
        missing_higher_v0_J_quench_probability=1-w,
        signed_energy_mean_per_initial_v1_selected_J=s['mean_signed_photon_energy_J']*w,
        signed_energy_second_per_initial_v1_selected_J2=s['second_signed_photon_energy_J2']*w,
        mean_emitted_per_initial_v1_selected=s['mean_emitted_photons']*w,
        mean_absorbed_per_initial_v1_selected=s['mean_absorbed_photons']*w,
        **s)

def csv_out(path,rows):
    with open(path,'w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)

def generate(output):
    b=import_bridge()
    _,branches,_,_,_=b.load_inputs()
    r33=b.load_r33()
    parent,old,grid,centers=r33.get_parent()
    src=b.rows_from(b.PACKAGE_ROOT/'results/BRIDGE_CASES_3528.csv')
    roots=b.rows_from(b.PACKAGE_ROOT/'results/BRIDGE_RADIATION_BALANCE_504.csv')
    assert len(src)==3528 and len(roots)==504
    table=[]
    for c in src:
        table.append(run_case(b,parent,grid,c,branches))
    if len(table)!=3528:raise AssertionError('grid size')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    csv_out(output/'FCS_CONDITIONAL_3528.csv',table)
    root_results=[]
    for row in roots:
        if str(row['endpoint_sign_change']).lower()!='true':continue
        z=float(row['z_balance_on_0to300'])
        T=int(row['Tgas_K']);j=int(row['initial_v1_J'])
        vp=row['v1_quench_policy'];pol=row['v0_spin_policy'];ratio=float(row['n_over_ncrit_J2'])
        initial,w=initial_mix(b,branches[(T,vp,j)])
        n=parent.reference_density(grid,T,pol)*ratio
        radT=r33.T0*(1+z)
        G,G0,C,Q,rad=r33.assemble(parent,grid,T,pol,n,radT)
        m=moments(G,Q,rad,initial)
        if abs(m['mean_signed_photon_energy_J'])>2e-30:
            raise AssertionError('R34 root not numerically zero')
        if not m['variance_signed_photon_energy_J2']>0:
            raise AssertionError('zero-mean but no nontrivial photon counting noise')
        root_results.append({'Tgas_K':T,'v1_quench_policy':vp,'initial_v1_J':j,'v0_spin_policy':pol,
           'n_over_ncrit_J2':ratio,'z_balance':z,'T_CMB_balance_K':radT,
           'selected_quench_probability':w,**m})
    if len(root_results)!=324:raise AssertionError('count of source bracketed roots drifted')
    csv_out(output/'FCS_ZERO_MEAN_ROOTS_324.csv',root_results)
    # A source-derived joint probabilistic interval: the unspecified J>4 branch
    # can contribute anything from 0 to its total mass, hence [known, known+missing].
    # This is a BOUND IN THE TWO-STAGE CONDITIONAL MODEL, not full physical chemistry.
    pl=b.rows_from(b.PACKAGE_ROOT/'results/BRIDGE_H2_PRODUCTS_35280.csv')
    agg={}
    for r in pl:
        key=tuple(r[k] for k in ['Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'])
        a=agg.setdefault(key,[0.]*10)
        a[int(r['H2_final_Jprime'])]+=float(r['probability_per_initial_v1'])
    bounds=[]
    for row in table:
        key=tuple(row[k] for k in ['Tgas_K','v1_quench_policy','initial_v1_J','v0_spin_policy','n_over_ncrit_J2','CMB_label'])
        B=agg[key]; missing=row['missing_higher_v0_J_quench_probability']
        if abs(sum(B)-row['selected_quench_probability'])>5e-13:raise AssertionError('probability bound prior mass')
        for i,p in enumerate(B):
            bounds.append({'Tgas_K':row['Tgas_K'],'v1_quench_policy':row['v1_quench_policy'],
               'initial_v1_J':row['initial_v1_J'],'v0_spin_policy':row['v0_spin_policy'],
               'n_over_ncrit_J2':row['n_over_ncrit_J2'],'CMB_label':row['CMB_label'],
               'H2_product_Jprime':i,'known_selected_lower_bound':p,
               'missing_v0_J_gt4_mass':missing,'conditional_upper_bound':p+missing,
               'full_physical_network_bound':False})
    assert len(bounds)==35280
    csv_out(output/'SOURCE_RESTRICTED_H2_BRANCH_BOUNDS_35280.csv',bounds)
    summary={'schema':'wu.r35.fcs.v1','parent_sha256':PARENT_SHA,
       'n_source_conditional_cases':len(table),'root_cases':len(root_results),
       'H2_branch_bound_rows':len(bounds),
       'max_mean_residual_J_vs_parent':max(abs(r['mean_signed_photon_energy_J']-r['signed_energy_mean_per_initial_v1_selected_J']/r['selected_quench_probability']) for r in table),
       'root_max_abs_mean_J':max(abs(x['mean_signed_photon_energy_J']) for x in root_results),
       'min_root_variance_J2':min(x['variance_signed_photon_energy_J2'] for x in root_results),
       'max_root_variance_J2':max(x['variance_signed_photon_energy_J2'] for x in root_results),
       'root_std_range_J':[min(x['std_signed_photon_energy_J'] for x in root_results),max(x['std_signed_photon_energy_J'] for x in root_results)],
       'max_emission_absorption_count_covariance':max(x['covariance_emitted_absorbed_photons'] for x in table),
       'min_emission_absorption_count_covariance':min(x['covariance_emitted_absorbed_photons'] for x in table),
       'min_selected_landing_probability':min(r['selected_quench_probability'] for r in table),
       'max_selected_landing_probability':max(r['selected_quench_probability'] for r in table),
       'physics':'exact FCS in restricted chemically absorbing HD5 with preset CMB, conditional on first v1 quench entering J<=4',
       'not_computed':'full v1 radiation/reaction/HD high J/chemistry Q/nonlocal radiation transfer/EMAA raw numeric equivalence',
       'EMAA_source':'NOT_ACQUIRED', 'canonical_DAG':'34/49_UNCHANGED','aux_scoped':'1/1',
       'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','FULL_A':None,
       'PHYSICAL_Q':None,'L4':False,'PRODUCTION':'NOT_ISSUED','main_merge':False}
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(P/'results'))
    args=p.parse_args();print(json.dumps(generate(Path(args.out)),indent=2))
