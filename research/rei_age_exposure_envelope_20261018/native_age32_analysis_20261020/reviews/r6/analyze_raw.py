"""Independent read-only arithmetic of already completed native age32/64 data."""
from pathlib import Path
from fractions import Fraction as F
import csv, hashlib, json, math
import numpy as np

ROOT=Path('/workspace/scratch/3fac997d7514')
TASK=ROOT/'rei_repo/research/rei_age_exposure_envelope_20261018'
A=ROOT/'intake_backup/age32/run_corrected/results/age32/attempt001/data'
B=TASK/'evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data'
OUT=ROOT/'review_theory_v9'
def read(p): return json.loads(p.read_text())
def f(x): return F.from_float(float(x))
def sumf(xs): return sum(map(f,xs),F())
def frac(x): return {'numerator':str(x.numerator),'denominator':str(x.denominator),'float':float(x)}
def ptotal(p): return f(p['N'])+sumf(p['ledgers'][4:7])
sa,sb=read(A/'setup.json'),read(B/'setup.json')
ea,eb=read(A/'endpoint.json'),read(B/'endpoint.json')
jumps=read(A/'source_jumps.json')['records']
inventory=sa['source_inventory']
assert len(jumps)==len(inventory)==32
assert [j['event'] for j in jumps]==list(range(32))
source=sumf(r[0] for r in inventory)
sources_prefix=[sumf(r[0] for r in inventory[:k]) for k in range(33)]
pre=[ptotal(j['pre'])-sources_prefix[k] for k,j in enumerate(jumps)]
post=[ptotal(j['post'])-sources_prefix[k+1] for k,j in enumerate(jumps)]
jump=[b-a for a,b in zip(pre,post)]
end=ptotal(ea)-source
initial=F(0)
hist=[pre[0]-initial]+[pre[k]-post[k-1] for k in range(1,32)]+[end-post[-1]]
assert initial+sum(jump,F())+sum(hist,F())==end
stored=read(A/'ledgers.json')
raw_intervals=read(A/'solver_return.json')['intervals']
checks=[]
for k,record in enumerate(raw_intervals):
    state=np.load(A/f'accepted_coordinates_event{k}.npy',allow_pickle=False)
    npy_photo=state[-sa['extra']:][4:7]
    target=jumps[k]['pre'] if k<32 else ea
    checks.append({'event':k,'N_bits_match':f(record['N'])==f(target['N']),
                   'photo_bits_match':all(f(x)==f(y) for x,y in zip(npy_photo,target['ledgers'][4:7]))})
assert all(c['N_bits_match'] and c['photo_bits_match'] for c in checks)
round_report={
 'schema':'rei.age32.independent_exact_telescoping.v1',
 'scope':'Exact rational algebra of stored binary64 scalar terms. History includes integration and reconstruction effects; no continuous-time numerical-error enclosure.',
 'initial_residual':frac(initial),'endpoint_residual':frac(end),
 'source_jump_sum':frac(sum(jump,F())),
 'source_jump_abs_sum':frac(sum(map(abs,jump),F())),
 'history_sum':frac(sum(hist,F())),
 'history_abs_sum':frac(sum(map(abs,hist),F())),
 'telescoping_exact':initial+sum(jump,F())+sum(hist,F())==end,
 'endpoint_stored_residual':stored['photon_residual'],
 'stored_final_arithmetic_difference':frac(f(stored['photon_residual'])-end),
 'exact_endpoint_over_jump_abs_sum':float(abs(end)/sum(map(abs,jump),F())),
 'history_to_jump_abs_sum':float(sum(map(abs,hist),F())/sum(map(abs,jump),F())),
 'all_33_accepted_snapshot_links':checks,
 'jumps':[{'event':k,'residual_delta':frac(x)} for k,x in enumerate(jump)],
 'intervals':[{'interval':k,'residual_delta':frac(x)} for k,x in enumerate(hist)]}
study=read(TASK/'observable_certificates_20261020/results/STUDY.json')
cases={c['clock']:c['populations'] for c in study['cases']}
def midpoint(v):return v[0]/2+v[1]/2
nodes=list(csv.DictReader((TASK/'vigilode_age_transport_20261019/inputs/nodes.csv').open()))
passive=[r for r in nodes if all(float(r[f'lambda{k}'])==0 for k in range(3))]
mapping={
 'schema':'rei.age32.v8_native_mapping.independent.v1',
 'fixed_model_node_count':len(nodes),'fixed_model_passive_node_count':len(passive),
 'fixed_model_passive_mass':math.fsum(float(r['mass']) for r in passive),
 'native_source_counts':{'32':float(source),'64':float(sumf(r[0] for r in sb['source_inventory']))},
 'source_total_32_minus_64':frac(source-sumf(r[0] for r in sb['source_inventory'])),
 'source_pair_number_match_count':sum(f(a[0])==f(b[0])+f(c[0]) for a,b,c in zip(inventory,sb['source_inventory'][::2],sb['source_inventory'][1::2])),
 'source_pair_number_max_abs_difference':float(max(abs(f(a[0])-f(b[0])-f(c[0])) for a,b,c in zip(inventory,sb['source_inventory'][::2],sb['source_inventory'][1::2]))),
 'source_pair_number_max_relative_difference':max(abs(float(f(a[0])-f(b[0])-f(c[0])))/float(f(b[0])+f(c[0])) for a,b,c in zip(inventory,sb['source_inventory'][::2],sb['source_inventory'][1::2])),
 'clock_32_model_matches_native':read(TASK/'vigilode_age_transport_20261019/inputs/model.json')['clocks']['32']==sa['birth_times_s'],
 'native_vs_fixed_sensitive':{},
 'last_cohort_fraction':{},
 'passive_first_example':passive[0],
 'passive_mass_over_native64_total':math.fsum(float(r['mass']) for r in passive)/eb['N'],
 'native64_input_x1':sb['x1'],'native32_input_x1':sa['x1']}
for n,ep in [(32,ea),(64,eb)]:
 p=cases[n]['sensitive']; values={'N':midpoint(p['observables'][0]),'U':midpoint(p['observables'][1])}
 mapping['native_vs_fixed_sensitive'][str(n)]={k:{'native':ep[k],'fixed_sensitive_midpoint':v,'native_minus_fixed':ep[k]-v,'relative_to_native':abs(ep[k]-v)/abs(ep[k])} for k,v in values.items()}
 mapping['last_cohort_fraction'][str(n)]={k:ep['cohorts'][-1][i]/ep[k] for i,k in enumerate(['N','U'])}
mapping['difference_comparison']={}
for i,k in enumerate(['N','U']):
 native=ea[k]-eb[k]
 fixed=midpoint(cases[32]['sensitive']['observables'][i])-midpoint(cases[64]['sensitive']['observables'][i])
 mapping['difference_comparison'][k]={'native32_minus64':native,'fixed_sensitive32_minus64':fixed,'relative_mismatch':abs(native-fixed)/abs(native)}
OUT.mkdir(exist_ok=True)
for name,data in [('EXACT_TELESCOPING.json',round_report),('MAPPING.json',mapping)]:
 (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:round_report[k] for k in ['endpoint_residual','source_jump_sum','source_jump_abs_sum','history_sum','history_abs_sum','stored_final_arithmetic_difference','exact_endpoint_over_jump_abs_sum','history_to_jump_abs_sum']},indent=2))
print(json.dumps(mapping,indent=2))
