"""Decimal 110-digit cross-check of the *same stored native owner numbers*.

Source fields and coefficients are read via Decimal.from_float, not decimal
literal interpretation, and all algebra is grouped separately from the exact
Fraction-path implementation. This is not an independently derived RHS/provider.
"""
import csv
import math
from decimal import Decimal as D, localcontext
from pathlib import Path
from fractions import Fraction as F

TOLS=(1e-14,1e-14,1e-14,1e-26)
CHI=(13.598434599702,24.587389011,54.41776)
EV=1.602176634e-12

class DecimalCheckError(ValueError): pass

def _input(s):
 x=float(s)
 if not math.isfinite(x):raise DecimalCheckError('NONFINITE_INPUT')
 return D.from_float(x)

def read_rows(path:Path):
 with path.open(newline='') as stream:return list(csv.DictReader(stream))

def decimal_step(n,i,r,k):
 p,q=n[k-1:k+1]; u,v=i[k-1:k+1]; t,w=r[k-1:k+1]
 diff=lambda key:_input(q[key])-_input(p[key])
 dint=lambda key:_input(v[key])-_input(u[key])
 dr=lambda key:_input(w[key])-_input(t[key])
 A=[diff('abs_'+x) for x in ('HI','HeI','HeII')]
 C=[diff('ci_'+x) for x in ('HI','HeI','HeII')]
 R=[diff('rr_'+x) for x in ('HII','HeII','HeIII')]
 DR=diff('dr_HeII')
 evt=dr('RCT')
 fhe=_input(0.24)/(D(4)*(D(1)-_input(0.24)))
 H=diff('x_hii')-(A[0]+C[0]-R[0]+evt)
 He2=diff('x_heii')-((A[1]+C[1]-R[1]-DR) - (A[2]+C[2]-R[2]) + evt)/fhe
 He3=diff('x_heiii')-(A[2]+C[2]-R[2]-evt)/fhe
 photochem=sum((_input(x)*A[j] for j,x in enumerate(CHI)),D(0))*_input(EV)
 energy=diff('w')-(dint('BH')+dint('BY')+dint('BZ'))+photochem-dint('thermalMicro')
 return (H,He2,He3,energy)

def check_decimal(base:Path):
 from accepted_step_balance import calculate_components
 base=Path(base)
 select=[1,7,16,59,384]
 maximum=0.0
 checked=0
 with localcontext() as ctx:
  ctx.prec=110
  for mode in ('OFF','KF','GM'):
   b=base/mode
   n=read_rows(b/'OWNER_NATIVE_41.csv');i=read_rows(b/'OWNER_INTERNAL_5.csv');r=read_rows(b/'OWNER_SELECTED_RCT.csv')
   for k in select:
    native=calculate_components(n,i,r,k)['residual']; independent=decimal_step(n,i,r,k)
    for u,v,tol in zip(native,independent,TOLS):
     fraction_dec=D(u.numerator)/D(u.denominator)
     err=abs(fraction_dec-v)/_input(tol)
     maximum=max(maximum,float(err));checked+=1
 return {'decimal_precision':110,'selected_steps':select,'decimal_residual_components_checked':checked,'max_normalized_abs_difference':maximum,'same_input_atomic_fit_verified':False,'mathematical_error_enclosure':False}

def check_stage_summary(base:Path):
 b=Path(base)
 expected_stages={0,1,2}
 sentinel=0;accepted=0;kind2=[]
 for mode in ('OFF','KF','GM'):
  rows=read_rows(b/mode/'OWNER_ACCEPTED_STAGES.csv')
  if len(rows)!=1155:raise DecimalCheckError('STAGE_ROW_COUNT')
  for k in range(385):
   three=rows[3*k:3*k+3]
   if {int(x['stage']) for x in three}!=expected_stages or any(int(x['step'])!=k for x in three):raise DecimalCheckError('STAGE_ORDER')
   for row in three:
    n=int(row['count'])
    if k==0:
     if n!=0 or float(row['min'])!=float('inf') or row['all']!='65535':raise DecimalCheckError('BAD_INITIAL_SENTINEL')
     sentinel+=1
    else:
     if n<1:raise DecimalCheckError('EMPTY_ACCEPTED_STAGE')
     if not (math.isfinite(float(row['min'])) and math.isfinite(float(row['max'])) and float(row['min'])<=float(row['max'])):raise DecimalCheckError('BAD_STAGE_T_RANGE')
     if not(0<=int(row['any'])<=65535 and 0<=int(row['all'])<=65535):raise DecimalCheckError('STAGE_BITMASK')
     accepted+=1
     if int(row['stage'])==2:kind2.append(n)
 return {'step0_sentinel_rows':sentinel,'accepted_stage_rows':accepted,'positive_stage2_count_range':[min(kind2),max(kind2)],'distinct_stage2_counts':sorted(set(kind2)),'full_stage_inputs_stored':False,'independent_rhs_certified':False}
