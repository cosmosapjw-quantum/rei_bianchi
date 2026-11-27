"""Independent alternate mpmath100 arithmetic and exact sympy rationals (R23 only)."""
import json
from pathlib import Path
import mpmath as mp
from sympy import Rational
p=Path(__file__).resolve().parents[1]
a=json.loads((p/'sources/MOLECULAR_IONIZATION_LITERALS.json').read_text())
r=json.loads((p/'results/R23_MOLECULAR_CYCLE.json').read_text())
mp.mp.dps=100
m=a['molecular_ionization'];rot=a['rotation'];get=lambda k:mp.mpf(m[k]['value'])
f=(get('EI_HD_cm1')+get('EI_HDp_cm1')-get('EI_H2_cm1')-get('EI_H2p_cm1')+
   mp.mpf(rot['H2_X_v0_J1_minus_J0_cm1']['value'])-
   mp.mpf(rot['HD_X_v0_J2_minus_J0_kHz']['value'])*1000/mp.mpf('29979245800'))
q=-f*mp.mpf('6.62607015e-34')*mp.mpf('299792458')*100*1000/mp.mpf('1.602176634e-19')
assert mp.almosteq(f,mp.mpf(r['delta_E_cm1']),rel_eps=mp.mpf('1e-80'))
assert mp.almosteq(q,mp.mpf(r['Q_spectroscopy_candidate_meV']),rel_eps=mp.mpf('1e-80'))
fr=Rational('124568.48466')+Rational('131224.6841650')-Rational('124417.4911573')-Rational('131058.1219937')+Rational('118.48684')-Rational(8006533168*1000,29979245800)
assert mp.almosteq(mp.mpf(str(fr.numerator))/mp.mpf(str(fr.denominator)),f,rel_eps=mp.mpf('1e-95'))
print(json.dumps({'mpmath_digits':100,'comparison':'R23 Decimal85 vs mp100 and exact SymPy Rational','delta_cm1':mp.nstr(f,35),'Q_meV':mp.nstr(q,35),'max_abs_delta_against_Decimal':mp.nstr(abs(f-mp.mpf(r['delta_E_cm1'])),6),'verdict':'PASS'},indent=2))
