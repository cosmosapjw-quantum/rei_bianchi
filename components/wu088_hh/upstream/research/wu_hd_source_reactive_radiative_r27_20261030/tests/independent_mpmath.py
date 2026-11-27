"""Independent mpmath transcription-level recomputation of R27 crossover cells.

Does not import the R27 implementation; this is a same-author,
independent-algorithm numerical check, NOT distinct-author R6/C9.
"""
from pathlib import Path
from decimal import Decimal
import hashlib, json, re, sys
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
mp.mp.dps=85
pdf=json.loads((ROOT/'sources/GL2022_700_SOURCE.json').read_text())
rec=json.loads((ROOT/'sources/REC161_LAMDA_A_TRANSCRIPTION_REF.json').read_text())
rows=json.loads((ROOT/'results/R27_SOURCE_REACTIVE_RADIATIVE.json').read_text())['source_rows']
grid=pdf['tokens_jprime_j_T']; temperatures=pdf['temperature_nodes_K']
As={int(j):mp.mpf(v) for j,v in rec['radiative_j_to_j_minus_1_A_per_second'].items()}
assert len(rows)==60
valid=[];errors=[]
for row in rows:
 if row['status']!='SOURCE_POSITIVE_TRANSCRIBED_A':continue
 J=row['HD_initial_J'];T=row['T_K'];i=temperatures.index(T)
 vals=[]
 for jp in range(10):
  literal=grid[jp][J][i]; m=re.fullmatch(r'([0-9.]+)\(([0-9][0-9])\)',literal)
  assert m, literal
  x=mp.mpf(m[1])*mp.power(10,-int(m[2])); assert x>0
  vals.append(x)
 spin_k=mp.fsum([(mp.mpf(3)/4 if jp%2 else mp.mpf(1)/4)*v for jp,v in enumerate(vals)])
 reference_ncrit=As[J]/spin_k
 x=mp.mpf(row['critical_Hplus_density_spin_cm_neg3'])
 errors.append(float(abs(reference_ncrit-x)/reference_ncrit));valid.append((J,T))
assert len(valid)==44
worst=max(errors)
assert worst<1e-69,(worst,valid[errors.index(worst)])
report={'schema':'wu.r27.mpmath_independent_source_calculation','mpmath_dps':85,'input_rows':len(rows),'verified_cells':len(valid),'maximum_relative_discrepancy':worst,'independence':'same-author different algorithm and numeric library, not independent scientist','status':'PASS'}
(ROOT/'results/INDEPENDENT_MPMATH.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
