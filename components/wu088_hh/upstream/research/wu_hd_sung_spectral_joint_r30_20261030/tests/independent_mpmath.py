"""Algorithmically separate high-precision reconstruction of R30 first-event and line-by-line photon-H2 split.
Uses immutable R29 verified source Grid rates, independent mp LU and independent
constructed G rather than calling R29 assemble / R30 metrics_one functions.
This is NOT a separate author's R6/C9.
"""
import json
from pathlib import Path
import mpmath as mp
from src import spectral as s

def run(dps=75):
 mp.mp.dps=dps
 p=s.load_r29();grid=p.load_grid()
 measured=[mp.mpf(z['nu_cm_minus1']) for z in s.get_sung()['lines']]
 E=[mp.mpf('0')]
 for x in measured:E.append(E[-1]+x)
 h=mp.mpf('6.62607015e-34');c=mp.mpf('299792458');kb=mp.mpf('1.380649e-23')
 sun=[mp.mpf(str(grid.A[j])) for j in range(1,5)]
 parsed=json.loads((s.ROOT/'results'/'R30_CASES_210.json').read_text())['rows']
 seen=0;worst_abs=mp.mpf(0);worst_rel=mp.mpf(0);worst_name='';line_worst=mp.mpf(0);joint_worst=mp.mpf(0)
 all_line=list(__import__('csv').DictReader((s.ROOT/'results'/'R30_PHOTON_ATLAS_840.csv').open()))
 all_joint=list(__import__('csv').DictReader((s.ROOT/'results'/'R30_RESTRICTED_H2_JOINT_2100.csv').open()))
 for idx,x in enumerate(parsed):
  T=x['T_K'];pol=x['policy'];n=mp.mpf(str(x['nHplus_cm3']));one=mp.mpf(1)
  M=mp.matrix(5,5);F=mp.matrix(5,5)
  prod=mp.matrix(10,5)
  for j in range(5):
   for k in range(10):
    w=one if pol=='raw_SQM' else (mp.mpf('0.75') if k%2 else mp.mpf('0.25'))
    prod[k,j]=n*mp.mpf(str(grid.q[(T,j,k)]))*w
   reaction=sum(prod[k,j] for k in range(10));M[j,j]-=reaction;F[j,j]-=reaction
  for high in range(1,5):
   for low in range(high):
    down=n*mp.mpf(str(grid.down[(T,high,low)]))
    kT=(E[high]-E[low])*mp.mpf(100)*h*c/(kb*mp.mpf(T))
    up=down*(mp.mpf(2*high+1)/mp.mpf(2*low+1))*mp.exp(-kT)
    for mat in (M,F):
     mat[low,high]+=down;mat[high,high]-=down
     mat[high,low]+=up;mat[low,low]-=up
   M[high-1,high]+=sun[high-1];M[high,high]-=sun[high-1]
   F[high,high]-=sun[high-1]
  b=mp.matrix([1 if j==x['initial_J'] else 0 for j in range(5)])
  m=mp.lu_solve(-M,b);m0=mp.lu_solve(-F,b)
  A=mp.matrix(4,1)
  U=mp.matrix(4,1)
  for high in range(1,5):
   A[high-1]=sun[high-1]*m0[high]
   U[high-1]=sun[high-1]*m[high]
  allp=prod*m;no=prod*m0;withp=allp-no
  checks={'photons_at_least_one_probability':sum(A),
          'expected_photons':sum(U),
          'no_photon_exchange_probability':sum(no),
          'integrated_photon_energy_J_per_initial_HD':sum(h*c*100*measured[j]*U[j] for j in range(4)),
          'lifetime_to_restricted_exchange_s':sum(m)}
  for k,val in checks.items():
   got=mp.mpf(str(x[k]));delta=abs(val-got);rel=delta/max(abs(val),mp.mpf('1e-50'))
   worst_abs=max(worst_abs,delta)
   if rel>worst_rel:worst_rel=rel;worst_name=k
  for j in range(4):
   q=all_line[4*idx+j]
   d=abs(mp.mpf(q['probability_this_is_first_photon'])-A[j]);line_worst=max(line_worst,d)
   d=abs(mp.mpf(q['expected_photons_this_line'])-U[j]);line_worst=max(line_worst,d)
  for j in range(10):
   row=all_joint[10*idx+j]
   for k,val in [('probability_restricted_product_Jprime',allp[j]),('joint_probability_no_photon_and_product',no[j]),('joint_probability_at_least_one_photon_and_product',withp[j])]:
    joint_worst=max(joint_worst,abs(mp.mpf(row[k])-val))
  if abs(sum(allp)-1)>mp.mpf('1e-60') or abs(sum(no)+sum(A)-1)>mp.mpf('1e-60'):
   raise AssertionError('high-precision physical conservation failed')
  seen+=1
 result={'method':'INDEPENDENT_MP75_MATRIX_CONSTRUCTION_NOT_PARENT_ASSEMBLE','distinct_author':False,'dps':dps,'verified_cases':seen,'verified_line_rows':4*seen,'verified_product_rows':10*seen,
   'max_relative_selected_five_metrics':float(worst_rel),'worst_metric_name':worst_name,
   'max_absolute_line_metric':float(line_worst),'max_absolute_joint_probability':float(joint_worst),
   'physical_sum_to_one':'PASS_MP75_BOTH_TRANSIENT_AND_FIRST_PHOTON_CHEM_SINK','claim':'same-author independent algorithm, not R6/C9 distinct-author'}
 (s.ROOT/'results'/'INDEPENDENT_MP75.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
