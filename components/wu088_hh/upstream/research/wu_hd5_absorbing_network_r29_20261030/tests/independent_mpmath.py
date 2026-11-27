"""Independent mpmath matrix rebuild from primary printed source tokens, no R29 src imports."""
import csv,hashlib,json,re
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parent.parent
mp.mp.dps=75
C=mp.mpf('299792458');H=mp.mpf('6.62607015e-34');KB=mp.mpf('1.380649e-23')
SHAS={'r':'f49312061552513ffdef5aa6d144f7edb9727f8b8cb3ce6e29bd262f15845db9',
      'i':'58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c',
      'a':'887383f3978de55ed82079feeff13361ff3910d9a1c384fa2d3b9c982bdb5ef8',
      'e':'769834947ec6630887ad3b9eae2f4d487c0dffecc268a0512521ee2a79127cca'}
FILES={'r':'GL2022_700_SOURCE.json','i':'GL2022_1560_INELASTIC_SOURCE_TOKENS.csv',
       'a':'REC161_LAMDA_A_TRANSCRIPTION_REF.json','e':'REC162_CDMS2011V2_PRINTED_LEVELS.json'}

def get(key):
    b=(ROOT/'sources'/FILES[key]).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHAS[key]:raise ValueError('SOURCE IDENTITY')
    return b

def rate(s):
    mat=re.fullmatch(r'([\d.]+)\((\d{1,2})\)',s)
    if mat is None:raise ValueError('invalid source literal')
    return mp.mpf(mat[1])*mp.power(10,-int(mat[2]))

def independently_recompute(saved_rows):
    react=json.loads(get('r'));a=json.loads(get('a'));e=json.loads(get('e'))
    inel=list(csv.DictReader(get('i').decode().splitlines()))
    down={(int(q['T_K']),int(q['initial_J']),int(q['final_J'])):rate(q['token'])
          for q in inel if q['initial_v']=='0' and q['final_v']=='0'
            and 1<=int(q['initial_J'])<=4 and int(q['final_J'])<int(q['initial_J'])
            and int(q['T_K']) in (55,105,255,505,1005,2005,3005) and q['status']=='SOURCE_PRINTED_VALID'}
    assert len(down)==70
    energy={int(x['J']):mp.mpf(x['E_cm1']) for x in e['levels']}
    Avec={int(j):mp.mpf(v) for j,v in a['radiative_j_to_j_minus_1_A_per_second'].items()}
    max_abs=mp.mpf('0');max_rel=mp.mpf('0');num=0
    for row in saved_rows:
        T=int(row['T_K']);policy=row['policy'];start=int(row['initial_J']);ratio=mp.mpf(str(row['ratio_n_over_ncrit_J2']))
        ti=react['temperature_nodes_K'].index(T)
        def src(j,k):
            lit=react['tokens_jprime_j_T'][k][j][ti]
            return rate(lit)*(mp.mpf('0.75') if k%2 else mp.mpf('0.25')) if policy=='Eq6-7_spin_effective' else rate(lit)
        src_K=[sum(src(j,k) for k in range(10)) for j in range(5)]
        n=ratio*Avec[2]/src_K[2]
        G=mp.matrix(5);Gfirst=mp.matrix(5)
        for higher in range(1,5):
            for lower in range(higher):
                lowerRate=n*down[T,higher,lower]
                delta=(energy[higher]-energy[lower])*H*C*100/(KB*T)
                upperRate=lowerRate*mp.mpf(2*higher+1)/mp.mpf(2*lower+1)*mp.exp(-delta)
                for A0 in [G,Gfirst]:
                    A0[lower,higher]+=lowerRate;A0[higher,higher]-=lowerRate
                    A0[higher,lower]+=upperRate;A0[lower,lower]-=upperRate
        for higher in range(1,5):
            G[higher-1,higher]+=Avec[higher]
            G[higher,higher]-=Avec[higher];Gfirst[higher,higher]-=Avec[higher]
        for j in range(5):
            G[j,j]-=n*src_K[j];Gfirst[j,j]-=n*src_K[j]
        e0=mp.matrix(5,1);e0[start]=1
        occupation=mp.lu_solve(-G,e0)
        occFirst=mp.lu_solve(-Gfirst,e0)
        probFirstPhoton=mp.fsum(Avec[j]*occFirst[j] for j in range(1,5))
        photonCount=mp.fsum(Avec[j]*occupation[j] for j in range(1,5))
        wait=mp.fsum(occupation)
        product=[mp.fsum(n*src(j,k)*occupation[j] for j in range(5)) for k in range(10)]
        odd=mp.fsum(product[1::2])
        for actual,expected in [(probFirstPhoton,row['probability_one_or_more_photons_before_exchange']),
                                (photonCount,row['expected_photons_before_exchange']),
                                (wait,row['expected_time_to_restricted_exchange_s']),
                                (odd,row['restricted_H2_v0_odd_Jprime_probability'])]:
            expected=mp.mpf(str(expected));d=abs(actual-expected)
            max_abs=max(max_abs,d);max_rel=max(max_rel,d/max(abs(actual),mp.mpf('1e-100')))
        assert abs(mp.fsum(product)-1)<mp.mpf('1e-55')
        num+=1
    return {'rows':num,'mp_dps':mp.mp.dps,'maximum_relative':mp.nstr(max_rel,25),
            'max_abs_mixed_units_not_a_physics_metric':mp.nstr(max_abs,25),
            'validation':'numerically independent mpmath formula and data parser, same author; no different-author R6/C9'}

if __name__=='__main__':
    src=json.loads((ROOT/'results/ATLAS_210_STATE_CASES.json').read_text())
    a=independently_recompute(src['rows']);(ROOT/'results/INDEPENDENT_MPMATH.json').write_text(json.dumps(a,indent=2)+'\n')
    print(json.dumps(a,indent=2))