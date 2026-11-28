"""Read-only independent-scoped numerical audit of source-carrying CSV crosswalk.
No imported implementation from reconcile.py. Not a different-author R6/C9.
"""
from pathlib import Path
from decimal import Decimal,localcontext
from collections import defaultdict
import csv,json,math

def rows(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def audit(root):
 root=Path(root);res=root/'results';inp=root/'inputs'
 s=rows(inp/'spectral/BO_ISOTOPE_THRESHOLDS_247.csv');a=rows(inp/'finite_difference/R38_R37_H2_PRODUCT_ENERGY_19200.csv');b=rows(res/'R38_SPECTRAL_R37_H2_BRANCH_Q_19200.csv');c=rows(res/'R38_SPECTRAL_R37_FIRST_EXIT_Q_1920.csv')
 delta={(r['HD_v'],r['HD_J'],r['H2_v'],r['H2_J']):r['delta_E_hartree'] for r in s}
 assert len(a)==len(b)==19200 and len(c)==1920
 with localcontext() as ctx:
  ctx.prec=70
  eh=Decimal('4.3597447222071e-18');kb=Decimal('1.380649e-23')
  max_q=Decimal(0);max_sum=Decimal(0);mass=defaultdict(Decimal);qsum=defaultdict(Decimal)
  for old,new in zip(a,b):
   assert all(old[k]==new[k] for k in ('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J','H2_final_J','P_H2_J_before_first_exit'))
   key=(old['Tgas_K'],old['n_Hplus_cm_minus3'],old['z_boundary'],old['spin_policy'],old['initial_v0_J'])
   p=Decimal(old['P_H2_J_before_first_exit'])
   d=Decimal(delta[('0',old['initial_v0_J'],'0',old['H2_final_J'])]);Q=-eh*d
   max_q=max(max_q,abs(Q-Decimal(new['Q_spectral_J'])))
   mass[key]+=p;qsum[key]+=p*Q
  for case in c:
   key=tuple(case[k] for k in ('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J'))
   max_sum=max(max_sum,abs(mass[key]-Decimal(case['P_H2_before_first_exit'])))
   mean=qsum[key]/mass[key]/kb
   assert abs(mean-Decimal(case['conditional_Q_spectral_K'])) < Decimal('2e-10')
 out={'cases':len(c),'source_branches':len(a),'max_Q_roundtrip_J':float(max_q),'max_branch_sum_discrepancy':float(max_sum),'decimal_precision_digits':70,'different_author_review':False}
 (root/'evidence/INDEPENDENT_AUDIT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 return out
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);q=ap.parse_args();print(json.dumps(audit(q.root),indent=2))
