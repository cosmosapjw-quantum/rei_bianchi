"""R28: the actual GL2022 SI Tables 12–28 nonreactive proton+HD source versus R27 exchange and REC A.
Strictly a conditional first-event model, NOT full chemical/thermal or non-LTE network.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib,json,csv,re
from .parse_source import source_catalog, SOURCE_SHA, TEMPS

RAW='./sources/GL2022_CSIC_supplement.pdf'
R27='./sources/R27_SOURCE_REACTIVE_RADIATIVE.json'
R27_SHA256='b72af2990fbddbc46a496238d9d0d50ad8eb26e61b8e810f27228222e3814339'
VALID=re.compile(r'^([0-9]+(?:\.[0-9]+)?)\(([0-9]+)\)$')
SUSPECT={(12,0,1,1505):'isolated printed exponent 1.91(11), local 1005K=2.48(10) 2005K=1.56(10); no repair'}
D=Decimal

def source_rate(tok):
    m=VALID.fullmatch(tok)
    if not m:raise ValueError('UNQUALIFIED_SOURCE_TOKEN: '+tok)
    return D(m.group(1))*(D(10)**(-int(m.group(2))))


def source_rows(pdf:Path,include_pdf=True):
    data=source_catalog(pdf)
    normalized=[]
    for x in data:
        y=dict(x)
        y['status']='SOURCE_PRINTED_VALID' if y['source_token_valid'] else 'SOURCE_MALFORMED_TOKEN'
        if (y['table'],y['initial_v'],y['initial_J'],y['T_K']) in SUSPECT:y['status']='SOURCE_SUSPECT_EXPONENT'
        if y['initial_v']==y['final_v'] and y['initial_J']==y['final_J']:
            y['status']='SOURCE_IDENTITY_DIAGONAL_PRINTED'
        y['rate_cm3_s']=str(source_rate(y['token'])) if y['status']=='SOURCE_PRINTED_VALID' else None
        normalized.append(y)
    return normalized


def build(pdf:Path,r27_path:Path):
    all_cells=source_rows(pdf)
    r27_bytes=r27_path.read_bytes()
    if hashlib.sha256(r27_bytes).hexdigest()!=R27_SHA256: raise ValueError('R27_SOURCE_HASH_MISMATCH')
    r27=json.loads(r27_bytes); original_data=r27['source_rows']
    if len(original_data)!=60:raise ValueError('R27 60 input rows not found')
    key=defaultdict(list)
    for s in all_cells:
        key[(s['initial_v'],s['initial_J'],s['final_v'],s['final_J'],s['T_K'])].append(s)
    for k,v in key.items():
        if len(v)!=1:raise ValueError('duplicate source transition key '+str(k))
    result=[]
    with localcontext() as context:
        context.prec=80
        for r in original_data:
            j,T=int(r['HD_initial_J']),int(r['T_K']); down=[]
            for lower in range(j):
                s=key.get((0,j,0,lower,T))
                if not s: raise ValueError(('missing down rate',j,lower,T))
                down.append(s[0])
            statuses=[s['status'] for s in down]
            status=r['status']
            if any(q!='SOURCE_PRINTED_VALID' for q in statuses):status='INELASTIC_SOURCE_HELD'
            if status=='SOURCE_POSITIVE_TRANSCRIBED_A':
                kx=D(r['Eq6_7_spin_effective_K_source_partial_cm3_s'])
                kc=sum((D(s['rate_cm3_s']) for s in down),D(0))
                A=D(r['A_J_to_Jminus1_s_inv'])
                ncrit_x=A/kx
                ncrit_c=A/kc
                frac_x_at_old=ncrit_x*kx/(ncrit_x*(kx+kc)+A)
                frac_c_at_old=ncrit_x*kc/(ncrit_x*(kx+kc)+A)
                frac_rad_at_old=A/(ncrit_x*(kx+kc)+A)
                max_x_at_high_density=kx/(kx+kc)
                # equal 50% first-event reaction possible only when kx>kc.
                reaction_half_density=A/(kx-kc) if kx>kc else None
                row={'K_exchange_Eq6_7_cm3_s':str(kx),'K_HD_inelastic_down_cm3_s':str(kc),
                     'A_HD_J_to_Jminus1_s_inv':str(A),'ncrit_exchange_vs_single_radiative_cm_neg3':str(ncrit_x),
                     'ncrit_inelastic_down_vs_single_radiative_cm_neg3':str(ncrit_c),
                     'P_first_exchange_at_R27_ncrit':str(frac_x_at_old),
                     'P_first_inelastic_at_R27_ncrit':str(frac_c_at_old),
                     'P_first_radiative_at_R27_ncrit':str(frac_rad_at_old),
                     'P_exchange_density_infinity_upper_given_down':str(max_x_at_high_density),
                     'n_Hplus_for_P_first_exchange_half_cm_neg3':str(reaction_half_density) if reaction_half_density is not None else None,
                     'physical_claim':'SOURCE_CONDITIONAL_THREE_COMPETING_EVENTS; OMIT_UPWARD_AND_OTHER_RADIATIVE_AND_VIBRATIONAL; UPPER_FOR_ADDITIONAL_NONNEGATIVE_CHANNELS'}
            else:
                row={k:None for k in ('K_exchange_Eq6_7_cm3_s','K_HD_inelastic_down_cm3_s',
                    'A_HD_J_to_Jminus1_s_inv','ncrit_exchange_vs_single_radiative_cm_neg3',
                    'ncrit_inelastic_down_vs_single_radiative_cm_neg3','P_first_exchange_at_R27_ncrit',
                    'P_first_inelastic_at_R27_ncrit','P_first_radiative_at_R27_ncrit',
                    'P_exchange_density_infinity_upper_given_down','n_Hplus_for_P_first_exchange_half_cm_neg3')}
                row['physical_claim']='SOURCE_QUALIFICATION_HELD_NOT_ZERO'
            result.append({'J_initial':j,'T_K':T,'rate_source_tables':[s['table'] for s in down],
                           'downward_source_tokens':{str(s['final_J']):s['token'] for s in down},
                           'source_rate_status':status,'prior_R27_status':r['status'],**row})
    return all_cells,result


def write(pdf,r27,out):
    out.mkdir(parents=True,exist_ok=True)
    cells,rows=build(pdf,r27)
    summary={'schema':'wu.r28.gl2022_proton_hd_full_inelastic_and_three_event.v1',
             'source_pdf_sha256':SOURCE_SHA,
             'source_pdf_bytes':273554,
             'r27_source_json_sha256':R27_SHA256,
             'source_doi':'10.1063/5.0128598',
             'source_inelastic_tables':list(range(12,29)),
             'all_inelastic_printed_cells':len(cells),
             'all_inelastic_row_count':len(cells)//10,
             'all_inelastic_source_statuses':dict(Counter(c['status'] for c in cells)),
             'J_1_to_6_down_source_cells':210,
             'three_event_candidate_rows':len(rows),
             'three_event_admitted_rows':sum(x['source_rate_status']=='SOURCE_POSITIVE_TRANSCRIBED_A' for x in rows),
             'row_statuses':dict(Counter(x['source_rate_status'] for x in rows)),
             'three_event_model':'one first event at T and n_Hplus constant; chemical HD->H2+D+ vs proton-excited HD rotational downward vs one spontaneous J->J-1 photon; no other channels, reverse, nonLTE bath, Q or ownership',
             'uncertainty':'not measured empirical rates; neither source uncertainties nor hidden printed anomalies fitted',
             'printed_valid_semantics':'Source literal syntactic validity only; source published computed SQM, not experimental validation, scientific uncertainty, or exact zero.',
             'DAG':{'before':[34,49],'after':[34,49],'new_canonical_nodes':0,'auxiliary_scoped_source_dataset':[1,1]},
             'physical_Q':None,'PES_native_threshold':None,'molecular_owner_ACK':None,'HH_R10':'OFF','L4':False,'full_A':None,'production':'NOT_ISSUED','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN'}
    (out/'INELASTIC_SOURCE_CELLS.json').write_text(json.dumps({'metadata':summary,'cells':cells},ensure_ascii=False,indent=2)+'\n')
    (out/'THREE_HAZARD_ROWS.json').write_text(json.dumps({'metadata':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n')
    keys=list(rows[0].keys());
    with open(out/'THREE_HAZARD_ROWS.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();
        for row in rows:writer.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in row.items()})
    (out/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--pdf',type=Path,default=Path(RAW));p.add_argument('--r27',type=Path,default=Path(R27));p.add_argument('--out',type=Path,default=Path('results'))
 a=p.parse_args();print(json.dumps(write(a.pdf,a.r27,a.out),indent=2))