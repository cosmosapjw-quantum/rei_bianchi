"""Exact stored-denominator discrete BE diagnostics; no native execution."""
from fractions import Fraction as F
from decimal import Decimal,localcontext
from pathlib import Path
import argparse,json,math,struct,sys,re,hashlib
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'src'))
from compare_results import endpoint_metrics,match_observations,relative

def exact(v):
 if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('NONFINITE_STORED_VALUE')
 return F.from_float(float(v))
def record(v):
 with localcontext() as c:
  c.prec=80;d=str(Decimal(v.numerator)/Decimal(v.denominator))
 return dict(numerator=str(v.numerator),denominator=str(v.denominator),decimal80=d)
def analyze_row(r):
 keys=['dt','before_N','Q','after_N','lambda_min','lambda_max','d_min','d_max','Q_lo','Q_hi','S_lo','S_hi']
 v={k:exact(r[k]) for k in keys}
 if any(x<0 for x in v.values()) or not isinstance(r['nodes'],int) or r['nodes']<0:raise ValueError('NEGATIVE_BE_OBSERVER')
 if not 1<=v['d_min']<=v['d_max'] or not v['Q_lo']<=v['Q']<=v['Q_hi'] or v['S_lo']>v['S_hi']:raise ValueError('BE_ORDER_DOMAIN')
 if r['kernel']!='STORED_DENOMINATOR_DISCRETE_BE':raise ValueError('WRONG_KERNEL')
 lo=v['Q_lo']/v['d_max'];hi=v['Q_hi']/v['d_min']
 return dict(cohort=r['cohort'],birth_bits=r['birth_bits'],a_bits=r['a_bits'],nodes=r['nodes'],zero_nodes=r['nodes']==0,
             exact_stored_kernel_enclosure=[record(lo),record(hi)],outward_division_sum=[record(v['S_lo']),record(v['S_hi'])],
             rounded_after_minus_enclosure=[record(v['after_N']-hi),record(v['after_N']-lo)],
             reconstruction_rounded_Q_minus_rounded_before=record(v['Q']-v['before_N']),
             after_inside_outward_kernel_sum=v['S_lo']<=v['after_N']<=v['S_hi'],
             scope='STORED_DENOMINATOR_DISCRETE_BE; before/after are rounded plain sums; not an enclosure of unrounded physical coefficients')
def analyze_trace(path,complete,output=None):
 rows=[];count=0;outside=0;zero=0;handle=None
 if not path.is_file():return dict(status='MISSING_TRACE',records=[],complete=False)
 if output is not None:
  output.parent.mkdir(parents=True,exist_ok=True);handle=output.with_suffix('.tmp').open('w')
 try:
  with path.open() as stream:
   for line in stream:
    if not line.strip():continue
    try:row=analyze_row(json.loads(line))
    except (ValueError,KeyError,TypeError) as e:return dict(status='INVALID_TRACE',reason=str(e),records=rows,complete=False,valid_prefix_rows=count)
    count+=1;outside+=not row['after_inside_outward_kernel_sum'];zero+=row['zero_nodes']
    if handle:handle.write(json.dumps(row,separators=(',',':'))+'\n')
    else:rows.append(row)
 finally:
  if handle:handle.close();output.with_suffix('.tmp').replace(output)
 return dict(status='COMPLETE' if complete else 'INCOMPLETE_ACCEPTED_PREFIX',complete=complete,records=rows,
             record_count=count,zero_node_rows=zero,rounded_after_outside_kernel_sum_rows=outside,
             exact_rows_file=str(output) if output else None,PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED')
def _finite_pair(left,right):
 if left is None or right is None:return dict(status='MISSING_PAIR',missing=['left' if left is None else 'right'])
 a=json.loads((left/'endpoint.json').read_text());b=json.loads((right/'endpoint.json').read_text())
 for root,obj in [(left,a),(right,b)]:
  if 'birth_times_s' not in obj and (root/'setup.json').is_file():obj['birth_times_s']=json.loads((root/'setup.json').read_text())['birth_times_s']
 m=endpoint_metrics(a,b)
 selected=[m['N'],m['U'],m['temperature_K'],*m['photo_events'],*m['Gamma_s'],*m['heat_erg_per_absorber_s']]
 matches,missing=match_observations(json.loads((left/'observations.json').read_text()),json.loads((right/'observations.json').read_text()))
 return dict(status='AVAILABLE',metrics=m,target=.005,target_met=all(v is not None and v<=.005 for v in selected),
   common_observations=[dict(x=y['x'],side=y['side'],N=relative(x['physical']['N'],y['physical']['N']),U=relative(x['physical']['U'],y['physical']['U'])) for x,y in matches],missing_or_ambiguous=missing,
   claim='FINITE_DIFFERENCE_ONLY; common frozen native153/config/B1 lineage must be bound by run receipts; no convergence/admission')
def finite_pair(left,right):
 if left is None or right is None:return dict(status='MISSING_PAIR',missing=[name for name,value in [('left',left),('right',right)] if value is None])
 try:return _finite_pair(left,right)
 except (ValueError,KeyError,TypeError,OSError) as e:return dict(status='INVALID_PAIR',reason=str(e),target=.005)
def eligibility(row,identity):
 if row.get('status')!='COMPLETE':return 'NOT_COMPLETE'
 if identity is None or row.get('identity')!=identity:return 'CURRENT_IDENTITY_MISMATCH'
 outputs=row.get('outputs')
 if not outputs:return 'MISSING_OUTPUT_IDENTITIES'
 for name,digest in outputs.items():
  path=Path(row['data'])/name
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:return 'OUTPUT_HASH_MISMATCH'
 return 'ELIGIBLE'
def postprocess(root,ledger,reference=None):
 roots={};identity=ledger.get('current_identity');reasons={r['attempt']:eligibility(r,identity) for r in ledger['attempts']}
 for name in ['time8','time16','time32']:
  good=[r for r in ledger['attempts'] if r['case']==name and reasons[r['attempt']]=='ELIGIBLE']
  roots[name]=Path(good[-1]['data']) if good else None
 result=dict(PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED',nonlinear_response_bound='NOT_ESTABLISHED',result_eligibility=reasons,pairs={
  'time8_vs_time16':finite_pair(roots['time8'],roots['time16']),'time16_vs_time32':finite_pair(roots['time16'],roots['time32'])},traces={})
 for name,path in roots.items():
  result['pairs'][name+'_vs_age32']=finite_pair(path,reference)
 for r in ledger['attempts']:
  stderr=Path(r['data']).parent/'stderr.log'
  totals=re.findall(r'REI_REPAIR_TOTAL count=(\d+) maximum_mass_bits=([0-9a-f]+)',stderr.read_text()) if stderr.is_file() else []
  result.setdefault('repair_statistics',{})[r['attempt']]=dict(count=int(totals[-1][0]),maximum_mass_bits=totals[-1][1]) if totals else dict(status='MISSING_FINAL_STATS')
  result['traces'][r['attempt']]=analyze_trace(Path(r['data'])/'be_trace.jsonl',reasons[r['attempt']]=='ELIGIBLE',root/'analysis'/('BE_'+r['attempt']+'.jsonl'))
 (root/'ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--reference',type=Path);a=p.parse_args();postprocess(a.root,json.loads((a.root/'CAMPAIGN.json').read_text()),a.reference)
