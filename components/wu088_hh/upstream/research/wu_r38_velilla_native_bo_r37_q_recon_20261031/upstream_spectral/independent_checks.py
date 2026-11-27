"""R38 bounded same-author alternate-implementation scientific checks.
Not a distinct-author referee. Uses sine-spectral independent of FD solver.
"""
from pathlib import Path
import csv,json,sys,hashlib,math
import numpy as np
from scipy.fft import dst,idst
from scipy.sparse.linalg import LinearOperator, eigsh
from scipy.special import erfc
sys.path.insert(0,str(Path(__file__).resolve().parent))
from native_pes import NativeVelilla,MU_H2,MU_HD,HARTREE_TO_K,HARTREE_TO_CM,rovib_levels,jacobi_sides
ROOT=Path(__file__).resolve().parents[1]
P=NativeVelilla(ROOT/'build/libvelilla_h3plus.so')

def spectral_e0(mu:int|float, N:int=600, J:int=0, rmin=.60, rmax=16.):
    L=rmax-rmin
    r=rmin+L*np.arange(1,N+1)/(N+1)
    d=(np.pi*np.arange(1,N+1)/L)**2/(2*mu)
    V=np.array([P.h2(float(x))+1 for x in r])+J*(J+1)/(2*mu*r*r)
    def matvec(x):return idst(d*dst(x,type=1,norm='ortho'),type=1,norm='ortho')+V*x
    return float(np.min(eigsh(LinearOperator((N,N),matvec=matvec,dtype=float),k=2,which='SA',tol=1e-11,return_eigenvectors=False)))

rows=[]
for h in (.04,.02,.01,.005):
    eH2=rovib_levels(P,MU_H2,[(0,0)],step=h)[(0,0)]
    eHD=rovib_levels(P,MU_HD,[(0,0)],step=h)[(0,0)]
    rows.append({'method':'FD_2nd','mesh_parameter':h,'E0_H2':eH2,'E0_HD':eHD,'endo_K':(eH2-eHD)*HARTREE_TO_K})
for n in (300,500,700):
    eH2=spectral_e0(MU_H2,n)
    eHD=spectral_e0(MU_HD,n)
    rows.append({'method':'sine_spectral','mesh_parameter':n,'E0_H2':eH2,'E0_HD':eHD,'endo_K':(eH2-eHD)*HARTREE_TO_K})
with (ROOT/'results/NUMERICAL_CROSSCHECK_7.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
with (ROOT/'results/BO_ISOTOPE_THRESHOLDS_247.csv').open() as f:
 th=list(csv.DictReader(f))
with (ROOT/'results/GL2022_NATIVE_BO_RATE_PARTITIONS_48.csv').open() as f:
 sums=list(csv.DictReader(f))
with (ROOT/'results/NATIVE_PES_GEOMETRY_300.csv').open() as f:
 geo=list(csv.DictReader(f))
with (ROOT/'results/MAXWELL_KINEMATIC_TAIL_6175.csv').open() as f:
 tails=list(csv.DictReader(f))
# Independently check branch transition signs, no rate extrapolation or invented missing branches.
assert len(th)==247 and len(geo)==300 and len(tails)==6175
assert len(sums)==48
assert max(abs(float(x['maxwell_energy_tail_probability'])-(math.erfc(math.sqrt(float(x['threshold_K'])/float(x['T_K'])))+2/math.sqrt(math.pi)*math.sqrt(float(x['threshold_K'])/float(x['T_K']))*math.exp(-float(x['threshold_K'])/float(x['T_K'])))) for x in tails)<5.e-15
source_rate_endo_J0=[float(x['endothermic_channel_printed_rate_fraction']) for x in sums if x['HD_J']=='0']
assert min(source_rate_endo_J0)>1-1e-12
# Reflection and permutation check independent geometry off axes
from itertools import permutations
errors=[]
for sides in [(1.2,1.5,1.7),(1.4,4.,4.9),(2.3,3.3,4.4),(1.65,2.0,2.2)]:
 vals=[P.h3(*j)[0] for j in set(permutations(sides))]
 errors.append(max(vals)-min(vals))
assert max(errors)<1e-10
check={'status':'PASS_SCOPED_SELF_ADVERSARIAL',
       'sine_spectral_700K':rows[-1]['endo_K'],
       'FD_005K':rows[3]['endo_K'],
       'max_FD_spectral_difference_K':abs(rows[3]['endo_K']-rows[-1]['endo_K']),
       'max_3body_permutation_diff_hartree':max(errors),
       'GL_J0_all_endothermic_printed_rate_rows':len(source_rate_endo_J0),
       'nonphysical_zero_rate_imputation':False,
       'native_3body_isotope_nuclear_motion':'NOT_RUN',
       'physmath_R6_C9_distinct_author':'NOT_RUN',
       'PES_NATIVE_THRESHOLD':'PARTIAL_BO_DIATOMIC',
       'PHYSICAL_Q':'HOLD_FULL_REACTION'}
(ROOT/'evidence/INDEPENDENT_SCOPED_CHECK.json').write_text(json.dumps(check,indent=2,sort_keys=True)+'\n')
print(json.dumps(check,indent=2))
