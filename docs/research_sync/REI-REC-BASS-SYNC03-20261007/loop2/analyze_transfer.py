#!/usr/bin/env python3
"""Transfer supplier boxes to the declared finite endpoint-linear observable."""
import csv,gzip,hashlib,json,math,pathlib
from decimal import Decimal as D,localcontext,ROUND_FLOOR,ROUND_CEILING
R=pathlib.Path(__file__).resolve().parents[1]
OUT=R/'loop2'; OUT.mkdir(exist_ok=True)
C=299792458.; SIGMA=6.6524587e-29

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(v):return D.from_float(float(v))
def tails(rows,key,rounding):
 with localcontext() as ctx:
  ctx.prec=90;ctx.rounding=rounding
  k=exact(C)*exact(SIGMA)*D(1000000)
  v=[D(0)]*len(rows)
  for i in range(len(rows)-2,-1,-1):
   dt=exact(rows[i+1]['normal_time_s'])-exact(rows[i]['normal_time_s'])
   assert dt>0
   cell=k*dt*(exact(rows[i][key])+exact(rows[i+1][key]))/D(2)
   v[i]=v[i+1]+cell
  return v

def delta(a,b,rounding):
 with localcontext() as ctx:
  ctx.prec=90;ctx.rounding=rounding
  return a-b

def outerfloat(v,lower):return math.nextafter(float(v),-math.inf if lower else math.inf)

def run():
 gate=json.loads((R/'state/SYNC_GATE_LOOP1.json').read_text())
 assert gate['loop1_admitted'] is True
 native=json.loads((R/'loop1/outputs/NATIVE_SUMMARY.json').read_text())
 independent=json.loads((R/'loop1/evidence/DECIMAL_RESULT.json').read_text())
 assert independent['status']=='PASS'
 all_data={};hist=[];common=[];checks=[]
 for h in native['histories']:
  name=h['history'];p=R/h['input'];assert sha(p)==h['input_sha256']
  with gzip.open(p,'rt') as f:rows=list(csv.DictReader(f))
  assert all(0<=float(r['ne_conditional_lo'])<=float(r['ne_proper_cm3'])<=float(r['ne_conditional_hi']) for r in rows)
  assert all(float(r['D_gas_normal_observer'])==1 for r in rows)
  lo=tails(rows,'ne_conditional_lo',ROUND_FLOOR);hi=tails(rows,'ne_conditional_hi',ROUND_CEILING)
  with localcontext() as ctx:
   ctx.prec=90
   mid=tails(rows,'ne_proper_cm3',ctx.rounding)
  assert all(a<=b<=c for a,b,c in zip(lo,mid,hi))
  assert lo[0]<=exact(h['tau_tail0'])<=hi[0]
  with gzip.open(R/h['output'],'rt') as f:nrows=list(csv.DictReader(f))
  assert len(rows)==len(nrows)
  residual=max(abs(float(m)-float(n['tau_tail0'])) for m,n in zip(mid,nrows))
  all_data[name]=(rows,lo,mid,hi,nrows)
  hist.append({'history':name,'source_sha256':sha(p),'rows':len(rows),'tau_native':h['tau_tail0'],'tau_decimal90':str(mid[0]),'tau_conditional_lo':str(lo[0]),'tau_conditional_hi':str(hi[0]),'max_native_depth_abs_error':residual,'native_initial_tau_inside_box':True})
  checks.append({'id':name+'_source_and_box','status':'PASS'})
 pairs=[]
 for level in range(3):
  fr,fl,fm,fu,fn=all_data[f'T{level}_FLRW'];br,bl,bm,bu,bn=all_data[f'T{level}_BI']
  assert [r['normal_time_s'] for r in fr]==[r['normal_time_s'] for r in br]
  a=delta(bl[0],fu[0],ROUND_FLOOR);b=delta(bu[0],fl[0],ROUND_CEILING)
  with localcontext() as ctx:
   ctx.prec=90
   nominal=bm[0]-fm[0]
   # Nominal correctly rounded exponentials only; no probability enclosure claim.
   sF=( -fm[0]).exp();sB=(-bm[0]).exp()
   mass_delta=sF-sB
  sign='POSITIVE' if a>0 else 'NEGATIVE' if b<0 else 'UNRESOLVED'
  native_delta=float(bn[0]['tau_tail0'])-float(fn[0]['tau_tail0'])
  pairs.append({'level':f'T{level}','cells':len(fr)-1,'delta_tau_BI_minus_FLRW_decimal90':str(nominal),'conditional_delta_lo':str(a),'conditional_delta_hi':str(b),'conditional_sign':sign,'relative_delta_tau':float(nominal/fm[0]),'native_subtracted_delta_tau':native_delta,'native_vs_decimal_contrast_abs_error':float(abs(exact(native_delta)-nominal)),'delta_scattered_mass_tail0':str(mass_delta),'claim':'source-conditional endpoint-linear finite slab; continuum sign not certified'})
  stride=(len(fr)-1)//200
  for i in range(0,len(fr),stride):
   low=delta(bl[i],fu[i],ROUND_FLOOR);high=delta(bu[i],fl[i],ROUND_CEILING)
   with localcontext() as ctx:
    ctx.prec=90;diff=bm[i]-fm[i]
   common.append({'level':f'T{level}','time_s':fr[i]['normal_time_s'],'tau_FLRW':float(fm[i]),'tau_BI':float(bm[i]),'delta_tau':float(diff),'conditional_delta_lo':outerfloat(low,True),'conditional_delta_hi':outerfloat(high,False),'ne_FLRW_cm3':float(fr[i]['ne_proper_cm3']),'ne_BI_cm3':float(br[i]['ne_proper_cm3'])})
 # Independent analytic cases for the positive-linear transfer arithmetic.
 for density in (0.,2.5):
  rr=[{'normal_time_s':t,'ne_proper_cm3':density} for t in (0,2,5)]
  l=tails(rr,'ne_proper_cm3',ROUND_FLOOR)[0];u=tails(rr,'ne_proper_cm3',ROUND_CEILING)[0]
  with localcontext() as ctx:
   ctx.prec=200;truth=exact(C)*exact(SIGMA)*D(1000000)*exact(density)*D(5)
  assert l<=truth<=u;checks.append({'id':f'analytic_constant_{density}','status':'PASS'})
 ds=[D(p['delta_tau_BI_minus_FLRW_decimal90']) for p in pairs]
 with localcontext() as ctx:
  ctx.prec=90;d10=ds[1]-ds[0];d21=ds[2]-ds[1]
  ratio=abs(d10/d21) if d21 else None
 refinement={'delta_T1_minus_T0':str(d10),'delta_T2_minus_T1':str(d21),'empirical_successive_difference_ratio':None if ratio is None else str(ratio),'observed_log2_ratio':None if ratio is None else math.log2(float(ratio)),'interpretation':'empirical diagnostic only; no asymptotic order or continuum error certificate','T2_contrast_change_over_signal':float(abs(d21/ds[2]))}
 result={'status':'PASS','scope':'conditional_endpoint_linear_observable_transfer','gate_sha256':sha(R/'state/SYNC_GATE_LOOP1.json'),'precision':90,'rounding':['ROUND_FLOOR','ROUND_CEILING'],'constants_interpretation':'exact binary64 BASS c and sigma_T values; cm3_to_m3=1000000 exact','histories':hist,'paired':pairs,'refinement':refinement,'checks':checks,'continuous_sign':'NOT_CERTIFIED','physical_observer_tail':'NOT_PROVIDED','native_core_modified':False}
 (OUT/'TRANSFER_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 with (OUT/'paired_observables.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=pairs[0].keys());w.writeheader();w.writerows(pairs)
 with (OUT/'common_grid.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=common[0].keys());w.writeheader();w.writerows(common)
 print(json.dumps({'status':'PASS','paired':pairs,'refinement':refinement},indent=2))

if __name__=='__main__':run()
