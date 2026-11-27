"""Independent arithmetic reference at 90 digits for 43 R28 first-event records.
Operates from original R27 published source row and extracted PDF table source-token
values, not from the arithmetic outputs of src.three_hazard.
"""
from __future__ import annotations
import json, re
from pathlib import Path
import mpmath as m
from src.parse_source import source_catalog

ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'sources/GL2022_CSIC_supplement.pdf'
R27=ROOT/'sources/R27_SOURCE_REACTIVE_RADIATIVE.json'
R28=ROOT/'results/THREE_HAZARD_ROWS.json'

def check():
    m.mp.dps=90
    original=json.loads(R27.read_text())['source_rows']; derived=json.loads(R28.read_text())['rows'];assert len(original)==len(derived)==60
    idx={(r['initial_v'],r['initial_J'],r['final_v'],r['final_J'],r['T_K']):r['token'] for r in source_catalog(T)}
    relative_error=m.mpf('0'); n=0; upper=[]
    for src, recorded in zip(original,derived):
        if recorded['source_rate_status']!='SOURCE_POSITIVE_TRANSCRIBED_A':continue
        J=int(src['HD_initial_J']); tmp=int(src['T_K'])
        kval=m.mpf(str(src['Eq6_7_spin_effective_K_source_partial_cm3_s']))
        A=m.mpf(str(src['A_J_to_Jminus1_s_inv']))
        down=m.mpf('0')
        for l in range(J):
            token=idx[(0,J,0,l,tmp)]; mat=re.fullmatch(r'(\d+(?:\.\d*)?)\((\d+)\)',token)
            if mat is None:raise AssertionError('Unqualified token in admitted row')
            down+=m.mpf(mat[1])*m.power(10,-int(mat[2]))
        # At n=A/K, the law can be independently evaluated through dimensionless R=kin/K.
        ratio=down/kval
        ph=m.mpf('1')/(m.mpf('2')+ratio)
        pdown=ratio/(m.mpf('2')+ratio)
        prad=m.mpf('1')/(m.mpf('2')+ratio)
        phinf=m.mpf('1')/(1+ratio)
        for key,value in [('P_first_exchange_at_R27_ncrit',ph),('P_first_inelastic_at_R27_ncrit',pdown),('P_first_radiative_at_R27_ncrit',prad),('P_exchange_density_infinity_upper_given_down',phinf)]:
            got=m.mpf(recorded[key]);relative_error=max(relative_error,abs(got-value)/max(abs(value),m.mpf('1e-80')))
        upper.append((J,tmp,m.nstr(ph,17),m.nstr(phinf,17)))
        n+=1
    return {'algorithm':'independent ratio-only first-event formula re-parsing 210 original PDF data cells','dps':90,'checked_rows':n,'max_relative_error':m.nstr(relative_error,28),'sample_105K':[r for r in upper if r[1]==105]}

if __name__=='__main__':
    d=check();print(json.dumps(d,indent=2));assert d['checked_rows']==43;assert m.mpf(d['max_relative_error'])<m.mpf('1e-70')