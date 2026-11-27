"""Fail-closed E13A accepted-stage INPUT reader, not an independent native stage solver."""
from __future__ import annotations
import csv
import math
import struct
from fractions import Fraction as F
from pathlib import Path
from accepted_step_balance import SOURCE_CHI_EV, SOURCE_EV_ERG, SOURCE_TOL, BalanceError

class WitnessError(ValueError):pass

COLS=(
 'step,mode,s0,s1,sm,dt,nH,nHe,H,Tcmb,fHe,mid_T,mid_ne,'
 'old_x,old_y,old_z,old_w,new_x,new_y,new_z,new_w,'
 'mid_x,mid_y,mid_z,mid_w,'
 'A_HI,A_HeI,A_HeII,B_HI,B_HeI,B_HeII,'
 'rhs_fx,rhs_fy,rhs_fz,rhs_w_dt,'
 'photo_delta_x,photo_delta_y,photo_delta_z,photo_delta_w,'
 'reeval_res_x,reeval_res_y,reeval_res_z,reeval_res_w,'
 'rct_events,rct_heat,rct_chemical,rct_escape,native_norm,reeval_norm'
).split(',')

def _f(v):
 try:
  result=float(v)
 except (ValueError,TypeError) as e:raise WitnessError('UNPARSABLE_BINARY64') from e
 if not math.isfinite(result):raise WitnessError('NONFINITE_BINARY64')
 return result

def bits(v):return struct.pack('>d',_f(v))

def read_stage_rows(path:Path):
 path=Path(path)
 with path.open(newline='') as handle:
  reader=csv.DictReader(handle)
  if reader.fieldnames!=COLS:raise WitnessError('E13_STAGE_SCHEMA_MISMATCH')
  rows=list(reader)
 if len(rows)!=2:raise WitnessError('PILOT_TWO_ROWS_REQUIRED')
 if any(None in row for row in rows):raise WitnessError('OVERLONG_STAGE_ROW')
 return rows

def read_other(path):
 with Path(path).open(newline='') as handle:return list(csv.DictReader(handle))

def validate_stage_rows(rows,selected_path:Path,internal_path:Path):
 if len(rows)!=2:raise WitnessError('PILOT_TWO_ROWS_REQUIRED')
 sel=read_other(selected_path)
 internal=read_other(internal_path)
 if len(sel)!=3 or len(internal)!=3:raise WitnessError('OWNER_3ROW_PILOT_MISSING')
 mode=rows[0].get('mode')
 if mode not in ('OFF','KF','GM'):raise WitnessError('BAD_MODE')
 maxima=[0.,0.,0.,0.]
 diffs=[0.,0.,0.,0.]
 for i,row in enumerate(rows,1):
  if set(row)!=set(COLS):raise WitnessError('MISSING_STAGE_INPUT_COL')
  if row['mode']!=mode or int(row['step'])!=i:raise WitnessError('MODE_OR_STEP_MISMATCH')
  for name in COLS[2:]:_f(row[name])
  old,new=sel[i-1:i+1]
  if bits(row['s0'])!=bits(old['s']) or bits(row['s1'])!=bits(new['s']):raise WitnessError('STEP_CLOCK_DISAGREES_WITH_OWNER')
  if bits(row['s1'])!=bits(internal[i]['s']):raise WitnessError('INTERNAL_CLOCK_DISAGREES')
  for a,b in zip(('x','y','z','w'),('x','y','z','w')):
   if bits(row['old_'+a])!=bits(old[b]) or bits(row['new_'+a])!=bits(new[b]):raise WitnessError('GAS_ENDPOINT_DISAGREES')
   expected=(_f(old[b])+_f(new[b]))*.5
   if bits(row['mid_'+a])!=bits(expected):raise WitnessError('GAS_MIDPOINT_DISAGREES')
  expected_sm=(_f(row['s0'])+_f(row['s1']))*.5
  if bits(row['sm'])!=bits(expected_sm):raise WitnessError('MIDPOINT_CLOCK_DISAGREES')
  dt=(_f(row['s1'])-_f(row['s0']))/_f(row['H'])
  if bits(row['dt'])!=bits(dt) or dt<=0:raise WitnessError('PROPER_TIME_STEP_DISAGREES')
  if abs(_f(row['fHe'])-_f(row['nHe'])/_f(row['nH'])) > 3e-16:raise WitnessError('FHE_GEOMETRY_DISAGREES')
  if not(1000<=_f(row['mid_T'])<=10000):raise WitnessError('E13_COMMON_TEMPERATURE_GUARD')
  if _f(row['mid_ne'])<=0:raise WitnessError('NEGATIVE_ELECTRON_DENSITY')
  # Distinct arithmetic: exact interpretation of native stage witness inputs,
  # without invoking coupled::assemble_residual or radiation::transaction.
  ff=lambda n:F.from_float(_f(row[n]))
  y0=[ff('old_'+x) for x in ('x','y','z','w')]
  y1=[ff('new_'+x) for x in ('x','y','z','w')]
  A=[ff('A_'+x) for x in ('HI','HeI','HeII')]
  B=[ff('B_'+x) for x in ('HI','HeI','HeII')]
  fHe=ff('fHe');h=ff('dt');rhs=[ff('rhs_'+x) for x in ('fx','fy','fz','w_dt')]
  ev=F.from_float(SOURCE_EV_ERG)
  chi=[F.from_float(c) for c in SOURCE_CHI_EV]
  d=[A[0],(A[1]-A[2])/fHe,A[2]/fHe,sum(B)-ev*sum(chi[j]*A[j] for j in range(3))]
  expected=[y1[j]-y0[j]-d[j]-h*rhs[j] for j in range(4)]
  for j,component in enumerate(('x','y','z','w')):
   recorded=ff('reeval_res_'+component)
   normalized=float(abs(recorded-expected[j])/F.from_float(SOURCE_TOL[j]))
   maxima[j]=max(maxima[j],float(abs(expected[j])/F.from_float(SOURCE_TOL[j])))
   diffs[j]=max(diffs[j],normalized)
   if normalized>0.01:raise WitnessError('STAGE_REEVAL_COMPONENT_INCONSISTENT')
  if bits(row['native_norm'])!=bits(row['reeval_norm']):raise WitnessError('ACCEPTED_NORM_NOT_REPLAY_EQUAL')
  if not 0<=_f(row['native_norm'])<=1:raise WitnessError('NATIVE_STAGE_GATE')
 return {'stage_records':2,'missing_stage_input_rows':0,'mode':mode,
         'source_re_evaluation':True,'native_rerun_requested':True,
         'max_source_vs_exact_scaled_difference':max(diffs),
         'max_exact_scaled_stage_residual':max(maxima),
         'independent_RHS_certificate':False,
         'original_chemical_rates_independently_evaluated':False}
