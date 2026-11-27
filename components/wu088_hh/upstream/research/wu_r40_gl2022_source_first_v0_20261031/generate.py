#!/usr/bin/env python3
"""WU R40, owner-unresolved original-source sensitivity of multistep HD(v=1)->v=0 first passage.
This is a collision-only, fixed T, finite 19-level kinetic subnetwork;
not a 3-body reactive S-matrix or global astrophysical cooling prediction.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, re, subprocess, sys, zipfile
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.constants import h, c, k as KB

T_GRID=(15.,55.,105.,255.,505.,1005.,1505.,2005.,2505.,3005.)
EXPECTED_PDF_SHA='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754'
EXPECTED_EPAPS_SHA='3db766f912d7cc9010f6c5b95ab8f2a98aceae5e7ad261d677e80ad1c57c8c4d'
EXPECTED_RADEX_SHA='b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save_csv(path,rows):
    assert rows
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)

def parse_pdf_token_tables(pdf):
    text=subprocess.run(['pdftotext','-layout',str(pdf),'-'],check=True,text=True,capture_output=True).stdout
    offsets=list(re.finditer(r'\bTable\s+(\d+):',text))
    by={int(m.group(1)):(m.end(),offsets[i+1].start() if i+1<len(offsets) else len(text)) for i,m in enumerate(offsets)}
    assert set(range(1,12)).issubset(by),sorted(by)
    rx=re.compile(r'(?<!\w)(\d*\.\d+)\((\d{2})\)')
    token_by={};duplicates=[]
    for jp in range(10):
        s,e=by[jp+1];body=text[s:e];rows={}
        for line in body.splitlines():
            m=re.match(r'^\s*\(0,([0-6])\)\s+(.*)$',line)
            if m:
                j=int(m.group(1));values=[a+'('+b+')' for a,b in rx.findall(m.group(2))]
                assert len(values)==10,(jp,j,len(values),line)
                assert j not in rows
                rows[j]=values
        assert set(rows)==set(range(7)),(jp,sorted(rows))
        for j in range(7):
            for ti,T in enumerate(T_GRID):token_by[(jp,j,T)]=rows[j][ti]
    s,e=by[11];b=text[s:e];thermal=[a+'('+v+')' for a,v in rx.findall(b)]
    # Table 11 contains exactly one row of 10 rates after temperature row.
    assert len(thermal)==10,thermal
    assert len(token_by)==700
    return token_by,thermal

def decimal_rate(token):
    m=re.fullmatch(r'(\d*\.?\d+)\((\d{2})\)',token)
    assert m,token
    return float(m.group(1))*10**(-int(m.group(2)))

def load_parent_emaa(r36):
    location=r36/'src/emaa_primary.py'
    spec=importlib.util.spec_from_file_location('wu_r36_source_emaa',location)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    data=module.parse_radex(r36/'sources/HD.Rovibration.805a7aa5.radex')
    cross,valid,missing=module.raw_crosswalk(data, r36/'sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv')
    return module,data,cross,valid,missing

def first_hit(data,module,T,override):
    # EMAA-derived 19-level collision generator in cm^3 s^-1 at n(H+)=1 cm^-3.
    Q=module.bath_rates(data,T,1.0,overrides=override)
    states=[data['levels'][i] for i in range(1,20)]
    A=[i for i,s in enumerate(states) if s['v']==0]; U=[i for i,s in enumerate(states) if s['v']==1]
    assert len(A)==12 and len(U)==7
    # Transient generator includes all v1-v1 collisions, with v0 absorbing on FIRST arrival.
    Q_uu=Q[np.ix_(U,U)];Q_au=Q[np.ix_(A,U)]
    # Dimensionless temporary scaling avoids tiny rates in scipy linear solver; preserve physical units later.
    R=-Q_uu*1e10
    B=np.linalg.solve(R.T,(Q_au*1e10).T).T
    time_s_at_1_cm3=np.linalg.solve(R.T,np.ones(len(U)))*1e10
    # Single-step branch conditioned on immediately entering v0 (not the unconditional first-collision distribution); comparator only.
    direct=Q_au/np.sum(Q_au,axis=0)
    if not (np.all(np.isfinite(B)) and np.min(B)>-1e-12 and np.max(np.abs(np.sum(B,axis=0)-1))<2e-10):
        raise ValueError('first-passage absorption probability conservation failed')
    if np.min(time_s_at_1_cm3)<=0:raise ValueError('invalid mean hitting time')
    EA=np.array([states[i]['E']*100*h*c for i in A]);EU=np.array([states[i]['E']*100*h*c for i in U])
    assert np.all(np.isfinite(EA))
    return {'B':B,'direct':direct,'time_s':time_s_at_1_cm3,'Qinternal_J':EU-(EA@B),
       'A':A,'U':U,'Q':Q,'Q_uu':Q_uu,'Q_au':Q_au, 'E_A':EA,'E_U':EU}

def rel_g(x,y):
    return (x-y)/y if y!=0 else None

def compute(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    src=root/'input/H_HD_rate_Supplementary_Material.pdf'
    epaps=root/'input/original_214302_1_epaps.zip';r36=root/'r36'
    assert sha(src)==EXPECTED_PDF_SHA
    assert sha(epaps)==EXPECTED_EPAPS_SHA
    assert sha(r36/'sources/HD.Rovibration.805a7aa5.radex')==EXPECTED_RADEX_SHA
    with zipfile.ZipFile(epaps) as z:
        assert z.namelist()==['H_HD_rate_Supplementary_Material.pdf']
        assert z.read(z.namelist()[0])==src.read_bytes()
    pdf_tokens,print_thermal=parse_pdf_token_tables(src)
    j=json.loads((root/'r33_Gl700_source.json').read_text())
    assert j['pdf_sha256']==EXPECTED_PDF_SHA
    mismatches=[]
    for (jp,init,T),tok in pdf_tokens.items():
        assert tok==j['tokens_jprime_j_T'][jp][init][T_GRID.index(T)],(jp,init,T,tok)
    assert print_thermal==j['table11_thermal_nominal_tokens']
    module,data,cross,valid,missing=load_parent_emaa(r36)
    issue=[r for r in cross if r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH']
    assert len(issue)==50 and len(missing)==16
    groups=defaultdict(dict)
    for r in issue:
        pair=((int(r['initial_v']),int(r['initial_J'])),(int(r['final_v']),int(r['final_J'])))
        groups[pair][float(r['T_K'])]=(int(r['EMAA_up_id']),int(r['EMAA_low_id']))
    assert len(groups)==7
    labels=[f'{v}J{j}->{w}J{k}' for ((v,j),(w,k)) in sorted(groups)]
    # Independent PDF-printed source thermal7. Missing v0 J7,8 reaction inputs: this is NOT a reproduction of main Eq.5 j<=8.
    lv=data['levels'];lev={(v['v'],v['J']):v for v in lv.values()}
    E0=lev[(0,0)]['E'];hc_over_k=100*h*c/KB
    thermal_rows=[];reactive_rates=[]
    for T in T_GRID:
        j_weights=[(2*jj+1)*math.exp(-(lev[(0,jj)]['E']-E0)*hc_over_k/T) for jj in range(7)]
        Z=sum(j_weights)
        kpar,kort=0.,0.
        for ji,wj in enumerate(j_weights):
            for jp in range(10):
                token=pdf_tokens[(jp,ji,T)];value=decimal_rate(token)
                censored=value==0. and int(token.split('(')[1].strip(')'))==0
                # Displayed zero is a censored printed value; zero here is a nonnegative lower-bound contribution, not a physical zero.
                term=wj/Z*(0.0 if censored else value)*(.25 if jp%2==0 else .75)
                if jp%2==0:kpar+=term
                else:kort+=term
                reactive_rates.append({'T_K':T,'initial_HD_J':ji,'final_H2_J':jp,
                     'source_token':token,'rate_cm3_s':f'{value:.16e}' if not censored else '',
                     'spin_multiplier':'.25' if jp%2==0 else '.75',
                     'thermal7_contribution_cm3_s':f'{term:.16e}' if not censored else '',
                     'source_flag':'PRINTED_ZERO_CENSORED' if censored else 'J5_Jp1_DUPLICATE' if ji==5 and jp==1 else 'J3_Jp7_2505_EXPONENT' if ji==3 and jp==7 and T==2505 else 'source_printed'})
        calc=kpar+kort;printed=decimal_rate(print_thermal[T_GRID.index(T)])
        # Suspected anomalous entries kept literal; do not fabricate corrections.
        suspect_ji5= j_weights[5]/Z*.75*decimal_rate(pdf_tokens[(1,5,T)])
        suspect_j3j7= j_weights[3]/Z*.75*decimal_rate(pdf_tokens[(7,3,T)]) if T==2505 else 0.
        thermal_rows.append({'T_K':T,'supplement_Table11_token':print_thermal[T_GRID.index(T)],
            'Table11_printed_cm3_s':f'{printed:.16e}',
            'reconstruction_j0to6_cm3_s':f'{calc:.16e}',
            'para_j0to6_cm3_s':f'{kpar:.16e}','ortho_j0to6_cm3_s':f'{kort:.16e}',
            'ratio_reconstructed_over_printed':f'{calc/printed:.12e}',
            'difference_cm3_s':f'{calc-printed:.16e}',
            'suspect_J5_Jp1_contribution_cm3_s':f'{suspect_ji5:.16e}',
            'suspect_J3_Jp7_T2505_contribution_cm3_s':f'{suspect_j3j7:.16e}',
            'interpretation':'source_j<=6_lower_bound_if_any_printed_censored_zero_not_full_main_j<=8'})
    save_csv(out/'GL2022_PRINTED_REACTION_700.csv',reactive_rates)
    save_csv(out/'TABLE11_RECONSTRUCTION_10.csv',thermal_rows)
    pdfrisk=[{'problem':'J5_jp1_duplicated', 'n':10,'status':'SOURCE_SUSPECT_UNCORRECTED','reason':'J5 row exactly duplicated across Tables 1 and 2, visually verified'},
        {'problem':'J3_jp7_T2505_exponent', 'n':1,'status':'SOURCE_SUSPECT_UNCORRECTED','reason':'Table 8 2505 K token 6.72(16) versus neighbor values; visually verified'}]
    (out/'SOURCE_RISKS.json').write_text(json.dumps(pdfrisk,indent=2)+'\n')
    # Distinguish per pair by WHOLE original printed source representation, not inferred preferred source.
    results=[];branches=[];group_rows=[]
    group_keys=sorted(groups.keys())
    max_mass=0.;max_delta=0.;max_abs_Edelta=0.;max_direct_shift=0.
    for T in T_GRID:
        base=first_hit(data,module,T,None)
        hybrid=first_hit(data,module,T,valid)
        max_mass=max(max_mass,np.max(np.abs(np.sum(base['B'],axis=0)-1)),np.max(np.abs(np.sum(hybrid['B'],axis=0)-1)))
        for k,initial in enumerate(base['U']):
            initial_label=lv[initial+1]['label'];uJ=lv[initial+1]['J']
            for label,d in [('EMAA_primary',base),('GL_printed_hybrid',hybrid)]:
                B=d['B'][:,k];indirect=float(np.linalg.norm(B-d['direct'][:,k],1))
                max_direct_shift=max(max_direct_shift,indirect)
                results.append({'T_K':T,'initial_v':1,'initial_J':uJ,'source_lane':label,
                    'p_first_v0_J0to4':f'{sum(B[z] for z,a in enumerate(d["A"]) if lv[a+1]["J"]<=4):.16e}',
                    'p_first_v0_J5to11':f'{sum(B[z] for z,a in enumerate(d["A"]) if lv[a+1]["J"]>=5):.16e}',
                    'mean_first_v0_time_at_n1_cm3_s':f'{d["time_s"][k]:.16e}',
                    'expected_internal_release_J':f'{d["Qinternal_J"][k]:.16e}',
                    'expected_internal_release_over_kB_K':f'{d["Qinternal_J"][k]/KB:.16e}',
                    'conditional_single_step_vs_multistep_L1':f'{indirect:.16e}',
                    'p_sum':f'{sum(B):.16e}',
                    'scope':'collision_only_first_v0_hit_nHplus_1cm3_no_radiation_no_chemical'})
                for ai,a in enumerate(d['A']):
                    branches.append({'T_K':T,'initial_v':1,'initial_J':uJ,'final_v0_J':lv[a+1]['J'],
                       'source_lane':label,'P_first_v0_hit':f'{B[ai]:.16e}',
                       'P_v0_given_direct_v0_step':f'{d["direct"][ai,k]:.16e}'})
            delta=hybrid['B'][:,k]-base['B'][:,k]
            delta_l1=float(np.sum(np.abs(delta)));max_delta=max(max_delta,delta_l1)
            delta_e=float(hybrid['Qinternal_J'][k]-base['Qinternal_J'][k]);max_abs_Edelta=max(max_abs_Edelta,abs(delta_e))
            for group in group_keys:
                mapping={key:valid[key] for key in valid if ((lv[key[0]]['v'],lv[key[0]]['J']),(lv[key[1]]['v'],lv[key[1]]['J']))==group}
                isol=first_hit(data,module,T,mapping)
                gdelta=isol['B'][:,k]-base['B'][:,k]
                group_rows.append({'T_K':T,'initial_v':1,'initial_J':uJ,
                    'GL_discrepant_transition':f'{group[0][0]}J{group[0][1]}->{group[1][0]}J{group[1][1]}',
                    'only_that_pair_printed_vs_EMAA_P_L1':f'{np.sum(np.abs(gdelta)):.16e}',
                    'only_that_pair_delta_internal_release_J':f'{isol["Qinternal_J"][k]-base["Qinternal_J"][k]:.16e}',
                    'only_that_pair_delta_first_v0_time_s_at_n1':f'{isol["time_s"][k]-base["time_s"][k]:.16e}',
                    'flag':'source_choice_not_owner_correction'})
    assert len(results)==140 and len(branches)==1680 and len(group_rows)==490
    save_csv(out/'FIRST_V0_HIT_SUMMARY_140.csv',results)
    save_csv(out/'FIRST_V0_HIT_BRANCHES_1680.csv',branches)
    save_csv(out/'PAIR_ISOLATED_SENSITIVITY_490.csv',group_rows)
    # Pair group 0J2->0J0 in absorbed set cannot influence any v1 hitting probability: exact structural result.
    zero_grp=[r for r in group_rows if r['GL_discrepant_transition']=='0J2->0J0']
    assert len(zero_grp)==70
    assert all(float(z['only_that_pair_printed_vs_EMAA_P_L1'])==0.0 for z in zero_grp)
    summary={'state':'SOURCE_QUALIFIED_SCOPED_NONAUTHORITATIVE',
       'canonical_DAG':'34/49_UNCHANGED','auxiliary_R40':'1/1_SCOPED' ,
       'rows':{'original_gl_reaction':len(reactive_rates),'thermal7_audit':len(thermal_rows),
         'first_v0_branch':len(branches),'first_v0_summary':len(results),'pair_isolated':len(group_rows)},
       'original_PDF_SHA256':EXPECTED_PDF_SHA,'original_EPAPS_SHA256':EXPECTED_EPAPS_SHA,
       'prior_R36_same_PDF_byte_identical':True,'gl_emaa_mismatch_rows_prior':len(issue),
       'gl_emaa_mismatch_transition_groups':len(groups),'gl_unprinted_pairs':len(missing),
       'max_13th_check_firsthit_mass_defect':float(max_mass),
       'max_L1_first_hit_GLhybrid_minus_EMAA':float(max_delta),
       'max_abs_internal_release_delta_J':float(max_abs_Edelta),
       'max_L1_multistep_vs_direct_first_collision':float(max_direct_shift),
       'table11_reconstructed_vs_printed_T105':next(r for r in thermal_rows if r['T_K']==105.),
       'table11_reconstructed_vs_printed_T3005':next(r for r in thermal_rows if r['T_K']==3005.),
       'critical_boundary':['first-entry v0 absorbing, not overall HD destruction','collision-only static T, n(H+)=1 per cm3',
            'hybrid uses only GL source printed valid cells, unresolved 50 conflicts do not identify correct owner rates',
            'stated thermal audit j<=6 is not original main Eq5 j<=8 and printed zeros are censored lower-bound contributions',
            'rates inside excluded states unknown not zeros; use EMAA source only for full 19-state transitions',
            'no new scattering S matrix, chemistry, source-owner acknowledgement, or production'],
       'sources':{'GL2022_DOI':'10.1063/5.0128598','Lepers2019_DOI':'10.1093/mnras/stz1797',
                   'Lepers2021_erratum_DOI':'10.1093/mnras/staa3146'}}
    (out/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--out',type=Path,default=None)
    args=ap.parse_args();print(json.dumps(compute(args.root,args.out or args.root/'results'),indent=2))
