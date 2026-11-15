"""Verify original +0.01 history bytes and compute only checkpoint-supported scope."""
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIVATE=ROOT/'private'
EXPECTED={'plus_0.csv':'1f29ed5dd6a7cc0588eceb9cc8748a3f3ab78e94c482f3758fd585f8910c1587','plus_1.csv':'dbe87394cb417ae18c700325a95f8e1ddebf1fed220375c3f4df947c992f66b3','plus_1_checkpoint.txt':'7af4071c8267f349c0a1d106759aa39d5fa47423ecbb76137692d31d1f5f82a2','source_identity.txt':'d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'}
for name,sha in EXPECTED.items():
    assert hashlib.sha256((PRIVATE/name).read_bytes()).hexdigest()==sha,name
checkpoint=(PRIVATE/'plus_1_checkpoint.txt').read_text().splitlines()
v=list(map(float,checkpoint[1].split()));c=list(map(int,checkpoint[2].split()))
checkpoint_fields=dict(zip(['a','time_s','b','x_HII','x_HeII','x_HeIII'],v[:6]))
rows=[];sizes=[];boundary=None
for k,name in enumerate(['plus_0.csv','plus_1.csv']):
    with (PRIVATE/name).open() as f:
        part=list(csv.DictReader(f))
    sizes.append(len(part))
    if k:
        boundary=rows[-1]==part[0];assert boundary
        part=part[1:]
    rows.extend(part)
matching=[i for i,r in enumerate(rows) if float(r['a'])==v[0]]
assert matching==[c[0]],matching
cut=matching[0]
assert all(float(rows[cut][k])==x for k,x in checkpoint_fields.items())
accepted=rows[:cut+1]
fhe=.2454/(4*(1-.2454));h0=67.4*1e5/3.0856775814913673e24
href=h0*math.sqrt(.000092*21**4+.315*21**3+1-.315-.000092)
maxres={'Sigma_equals_s_over_H_abs':0.,'H_model_relative':0.,'s_model_relative':0.,'hydrogen_closure_abs':0.,'helium_closure_abs':0.,'charge_closure_abs':0.}
last=None;milestones={str(x):None for x in [.1,.5,.9]}
for r in accepted:
    x={k:float(z) for k,z in r.items() if k!='case_id'}
    a=x['a'];H=x['H_per_s'];s=x['s_per_s']
    sm=.01*href*((1/21)/a)**3
    hm=math.sqrt(h0*h0*(.000092/a**4+.315/a**3+1-.315-.000092)+sm*sm)
    vals={'Sigma_equals_s_over_H_abs':abs(x['Sigma']-s/H),'H_model_relative':abs(H/hm-1),'s_model_relative':abs(s/sm-1),'hydrogen_closure_abs':abs(x['x_HI']+x['x_HII']-1),'helium_closure_abs':abs(x['x_HeI']+x['x_HeII']+x['x_HeIII']-1),'charge_closure_abs':abs(x['ne_proper_cm3']/x['nH_proper_cm3']-x['x_HII']-fhe*(x['x_HeII']+2*x['x_HeIII']))}
    for k,z in vals.items():maxres[k]=max(maxres[k],z)
    if last:
        assert a>last['a'] and x['time_s']>last['time_s']
        for threshold in [.1,.5,.9]:
            if milestones[str(threshold)] is None and last['x_HII']<threshold<=x['x_HII']:
                w=(threshold-last['x_HII'])/(x['x_HII']-last['x_HII'])
                milestones[str(threshold)]={'bracket_zbar':[last['zbar'],x['zbar']],'bracket_xHII':[last['x_HII'],x['x_HII']],'zbar_linear':last['zbar']+w*(x['zbar']-last['zbar']),'time_s_linear':last['time_s']+w*(x['time_s']-last['time_s'])}
    last=x
assert max(maxres.values())<1e-12,maxres
report={'schema':'rei.axbi.recovered_plus_prefix.v1','evidence_status':'NUMERICALLY_CHECKED_RECOVERED_SAVED_HISTORY_NOT_REFINED','file_sha256':EXPECTED,'input_rows':sizes,'duplicate_boundary_exact_all_columns':boundary,'deduplicated_raw_rows':len(rows),'checkpoint_supported_rows':len(accepted),'checkpoint_accepted':c[0],'quarantined_post_checkpoint_rows':len(rows)-len(accepted),'checkpoint_exact_matches':checkpoint_fields,'clock_origin':'elapsed proper seconds since zbar20; non-tilted gas','q_ref':.01,'Sigma_initial':float(rows[0]['Sigma']),'checkpoint_last_row':accepted[-1],'raw_tail_last_row':rows[-1],'max_residuals':maxres,'milestones':milestones,'covered_zbar':[20.,float(accepted[-1]['zbar'])],'full_zbar4_history':False,'AX11_refinement_completed':False,'scientific_admission':'NOT_ISSUED','cost_note':'Checkpoint cost is lower than actual interrupted cost; raw47rows and unknown terminal work are preserved.'}
(ROOT/'RECOVERED_PLUS_PREFIX_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['input_rows','deduplicated_raw_rows','checkpoint_supported_rows','quarantined_post_checkpoint_rows','covered_zbar','max_residuals','milestones']}))
