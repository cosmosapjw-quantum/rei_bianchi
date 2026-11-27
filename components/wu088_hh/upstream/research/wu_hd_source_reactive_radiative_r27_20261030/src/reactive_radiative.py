#!/usr/bin/env python3
"""WU R27: physical-source-derived HD reactive/radiative one-step competition.

Only exact GL2022 printed temperature nodes and REC161 radiative A transcription.
Never produce physical Q, PES thresholds, cross sections, reverse rates, bath heat.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from decimal import Decimal, localcontext
from pathlib import Path

GL2022_DOI="10.1063/5.0128598"
R26_BLOB_SHA256='1258b1150577e732a8e175a16a7a78b09e69bc5a02407ed6e351f7e31eb3d7c8'
R26_SOURCE_PDF_SHA256='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754'
REC161_TRANSCRIPTION_BLOB='bd5a7f0e29ff6dd228cd8e927d6932b74d8cb4b9'
REC161_REF_SHA256='887383f3978de55ed82079feeff13361ff3910d9a1c384fa2d3b9c982bdb5ef8'
KB_MEV=Decimal('0.08617333262145177433663659334080639201233039577582555107965705109640240')
H=Decimal('6.62607015e-34'); C=Decimal('299792458'); ELEC=Decimal('1.602176634e-19')
BO_J0_ROUND_MEV=Decimal('3.4'); H2_J1_CM=Decimal('118.48684')
SPECT_R23_MEV=Decimal('20.95002099384045759056749544382632657967')

class SourceProblem(ValueError): pass

def digest(b: bytes)->str: return hashlib.sha256(b).hexdigest()

def token_value(tok: str)->Decimal | None:
    """Returns None for source-printed zero (never physics-certified zero)."""
    m=re.fullmatch(r'(\d+(?:\.\d*)?|\.\d+)\((\d\d)\)',tok)
    if not m: raise SourceProblem('BAD_PRINTED_TOKEN '+str(tok))
    num=Decimal(m.group(1)); return num*Decimal(10)**(-int(m.group(2))) if num!=0 else None

def source_import(r26_json:Path, rec_source:Path):
    source=json.loads(r26_json.read_bytes())
    if source['doi']!=GL2022_DOI or source['pdf_sha256']!=R26_SOURCE_PDF_SHA256: raise SourceProblem('WRONG_R26_SOURCE')
    grid=source['tokens_jprime_j_T']
    h=digest(json.dumps(grid,ensure_ascii=True,separators=(',',':')).encode())
    if h!=R26_BLOB_SHA256: raise SourceProblem('R26_CELLS_NOT_ORIGINAL')
    temps=source['temperature_nodes_K']
    if temps!=[15,55,105,255,505,1005,1505,2005,2505,3005] or len(grid)!=10 or any(len(a)!=7 or any(len(b)!=10 for b in a) for a in grid): raise SourceProblem('BAD_R26_SHAPE')
    rec_bytes=rec_source.read_bytes()
    if digest(rec_bytes)!=REC161_REF_SHA256: raise SourceProblem('REC_TRANSCRIBED_A_IDENTITY_MISMATCH')
    rec=json.loads(rec_bytes)
    if rec['status']!='SOURCE_TRANSCRIPTION_FROM_REC_PR161_NOT_RAW_2289_BYTE_SOURCE' or rec['source_git_blob']!=REC161_TRANSCRIPTION_BLOB: raise SourceProblem('WRONG_REC_SOURCE')
    a={int(k):Decimal(v) for k,v in rec['radiative_j_to_j_minus_1_A_per_second'].items()}
    if set(a)!=set(range(1,9)) or any(v<=0 for v in a.values()):raise SourceProblem('BAD_REC_A')
    return source,grid,temps,rec,a,h

def compute(r26_json:Path,rec_source:Path):
    with localcontext() as ctx:
        ctx.prec=75
        source,grid,temps,rec,As,token_sha=source_import(r26_json,rec_source)
        rows=[]
        for J in range(1,7):
            for i,T in enumerate(temps):
                values=[token_value(grid[jp][J][i]) for jp in range(10)]
                num_missing=sum(v is None for v in values)
                suspect=(J==5 or (J==3 and T==2505))
                status='PRINTED_ZERO_CENSORED' if num_missing else ('SOURCE_SUSPECT_DUPLICATE' if J==5 else ('SOURCE_SUSPECT_EXPONENT' if J==3 and T==2505 else 'SOURCE_POSITIVE_TRANSCRIBED_A'))
                # Source sums are still numerical totals when incomplete/suspect;
                # they are DIAGNOSTIC and cannot certify a total K or ncrit.
                k_raw=sum((v for v in values if v is not None),Decimal(0))
                k_eff=sum((v*(Decimal('0.75') if jp%2 else Decimal('0.25')) for jp,v in enumerate(values) if v is not None),Decimal(0))
                ok=status=='SOURCE_POSITIVE_TRANSCRIBED_A'
                ncrit=As[J]/k_eff if ok else None
                ncrit_raw=As[J]/k_raw if ok else None
                rows.append({'T_K':T,'HD_initial_J':J,'A_J_to_Jminus1_s_inv':str(As[J]),
                  'source_positive_cell_count':10-num_missing,'source_printed_zero_count':num_missing,
                  'raw_SQM_K_source_partial_cm3_s':str(k_raw),'Eq6_7_spin_effective_K_source_partial_cm3_s':str(k_eff),
                  'critical_Hplus_density_spin_cm_neg3':str(ncrit) if ncrit is not None else '',
                  'critical_Hplus_density_raw_diagnostic_cm_neg3':str(ncrit_raw) if ncrit_raw is not None else '',
                  'hazard_50percent_rule':'n(H+)=A/K, one-step radiative-vs-forward exchange only' if ok else '',
                  'status':status})
        # R24 basic Maxwell positivity support bound against external candidate thresholds.
        tok15=grid[1][2][0];tok55=grid[1][2][1]
        k15=token_value(tok15);k55=token_value(tok55)
        if k15 is None or k55 is None:raise SourceProblem('TARGET_SOURCE_CENSORED')
        delta_beta=1/(KB_MEV*Decimal(15))-1/(KB_MEV*Decimal(55))
        norm=(Decimal(55)/Decimal(15))**Decimal('1.5')
        # Correct: k15/k55 <= norm * Exp[-delta_beta*theta]
        theta_bound=((k55/k15)*norm).ln()/delta_beta
        dJ=H*C*Decimal(100)*H2_J1_CM/(ELEC*Decimal('1e-3'))
        theta_BO=BO_J0_ROUND_MEV+dJ
        cases=[]
        for name,theta in [('2019_BO_J0_PLUS_H2_J1_ROTATION_APPROX',theta_BO),('R23_EXTERNAL_SPECTROSCOPIC_CANDIDATE',SPECT_R23_MEV)]:
            allowed_ratio=norm*(-delta_beta*theta).exp()
            allowed_k15=k55*allowed_ratio
            cases.append({'candidate':name,'threshold_meV':str(theta),'allowed_k15_cm3_s':str(allowed_k15),
                 'original_k15_cm3_s':str(k15),'observed_over_allowed':str(k15/allowed_k15),
                 'required_k15_reduction_fraction':str(Decimal(1)-allowed_k15/k15),
                 'status':'CONDITIONAL_MODEL_CONVENTION_TEST_NOT_PES_NATIVE_THRESHOLD'})
        report={'schema':'wu.r27.source_reactive_radiative.v1',
          'scope':{'physical_data_first':True,'R26_canonical_done':34,'R26_canonical_total':49,'R27_auxiliary_data_done':1,'R27_auxiliary_data_total':1,
             'owner_ACK':None,'native_PES_threshold':None,'physical_Q':None,'full_A':None,'L4':False,'production':'NOT_ISSUED'},
          'sources':{'GL2022_2022_DOI':GL2022_DOI,'GL2022_source_pdf_sha256':R26_SOURCE_PDF_SHA256,'GL2022_700_token_tensor_sha256':token_sha,
             'REC_2021_LAMDA_HD_transcribed_via_PR161_blob':REC161_TRANSCRIPTION_BLOB,'REC_source_raw_byte_reacquisition':'NOT_RUN',
             'Velilla2008_source_PES_archive':'NOT_ACQUIRED','2019_BO_approx_DOI':'10.1093/mnras/stz1797','R23_external_spectroscopy_model':'NOT_SAME_PES'},
          'physics':{'definition':'At a fixed source T, gamma_rxn=n(H+) K_J(T); gamma_spont=A(J->J-1); ncrit=A/K (cm^-3), no other channels.',
             'reaction_policy':'Eq6-7 final ortho/para 3/4 odd, 1/4 even (not twice)','source_A_policy':'REC161 visible-text transcription, not exact raw LAMDA byte source',
             'unqualified_zero':'excluded from certified ncrit','suspect_J5':'Table1 and Table2 source rates duplicate for all T; not integrated',
             'suspect_2505_J3':'Table8 6.72(16) source exponent; not integrated',
             'no_thermal_interpolation':True,'no_owner_mutation':True,
             'nonLTE':'No H2 collisional redistributions, upward radiation or nine-level stationary solution; one-step competition only'},
          'counts':{'source_temperature_nodes':10,'initial_J_one_through_six':6,'all_rows':len(rows),'admissible_rows':sum(r['status']=='SOURCE_POSITIVE_TRANSCRIBED_A' for r in rows),'source_censored_rows':sum(r['status']=='PRINTED_ZERO_CENSORED' for r in rows),'suspect_rows':sum(r['status'].startswith('SOURCE_SUSPECT') for r in rows)},
          'threshold_consistency':{'rate_reference':'raw state J2 to Jp1, not Eq6/7 weighted mixture',
               'k15_literal':tok15,'k55_literal':tok55,'beta_difference_per_meV':str(delta_beta),'theta_laplace_upper_meV':str(theta_bound),
               '2019_bo_j0_threshold_rounded_meV':str(BO_J0_ROUND_MEV),'H2_J1_rot_from_spectroscopy_meV':str(dJ),'theta_2019_BO_Jp1_approx_meV':str(theta_BO),
               'assumptions':'T-independent sigma(E)>=0, entrance-relative kinetic energy, support E>=theta, ordinary Maxwell rate integral; cross-paper comparisons not same source-native PES',
               'candidate_cases':cases},
          'source_rows':rows}
        return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--r26-source-json',type=Path,required=True)
    p.add_argument('--rec-reference-json',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    res=compute(a.r26_source_json,a.rec_reference_json)
    a.out.mkdir(exist_ok=True,parents=True)
    (a.out/'R27_SOURCE_REACTIVE_RADIATIVE.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
    with (a.out/'R27_CRITICAL_DENSITIES.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(res['source_rows'][0].keys()));w.writeheader();w.writerows(res['source_rows'])
    print('rows',res['counts'],'theta_necessary_meV',res['threshold_consistency']['theta_laplace_upper_meV'])
    for J in [1,2,3,4,5,6]:
        z=next(r for r in res['source_rows'] if r['HD_initial_J']==J and r['T_K']==105)
        print('105K J',J,'status',z['status'],'ncrit',z['critical_Hplus_density_spin_cm_neg3'])
if __name__=='__main__':main()
