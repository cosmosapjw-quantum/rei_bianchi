"""One four-row native campaign with Decimal80 oracle on frozen binary64 inputs."""
import decimal
import hashlib
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent
decimal.getcontext().prec = 80
D = decimal.Decimal
def f(x): return D.from_float(x)
def rel(x, y): return float(abs(f(x)-y)/abs(y)) if y else (0.0 if x == 0 else float('inf'))

expected = {'baseline': 'f39c09cac72359ecff4366ba5e0828d75c7d44185d126fd499f9e741bfb5005e',
            'refined': '4204d0ea44b23c868e5c5e330029bc35303ae85466cdb4671e60ba9d4a140611'}
rows = []
for label, sha in expected.items():
    path = ROOT.parent/'rec_rei_cold_intake01_20261011'/'inputs'/f'{label}.json'
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha
    for row in json.loads(raw): rows.append((label,row['endpoint']))
source = ROOT/'source'/'HG97_astro-ph_9612232v1.pdf'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '6ea0b803b554c91d598705f96416e1a8b67549fb02cb567944eaacdba5d148b0'
stdin = ''.join(' '.join(repr(e[k]) for k in ['Tm_K','nH_m3','nHe_m3','xe_per_H'])+'\n' for _,e in rows)
binary = ROOT/'native'/'target'/'release'/'cold_hii_rr_component01'
start = time.monotonic()
proc = subprocess.run([str(binary)],input=stdin,text=True,capture_output=True,timeout=120)
wall = time.monotonic()-start
(ROOT/'evidence'/'FIRST_CAMPAIGN.stdout').write_text(proc.stdout)
(ROOT/'evidence'/'FIRST_CAMPAIGN.stderr').write_text(proc.stderr)
(ROOT/'evidence'/'CAMPAIGN_RECEIPT.json').write_text(json.dumps({'command':[str(binary)],'exit':proc.returncode,'wall_s':wall,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'stdin':stdin},indent=2)+'\n')
assert proc.returncode == 0
outputs = [json.loads(line) for line in proc.stdout.splitlines()]
assert len(outputs) == 4
reports=[]
for (label,e),out in zip(rows,outputs):
    t,nh,nhe,xe = (f(e[k]) for k in ['Tm_K','nH_m3','nHe_m3','xe_per_H'])
    lam = D('315614')/t
    alpha = D('1.269e-13')*lam**D('1.503')/(1+(lam/D('.522'))**D('.470'))**D('1.923')*D('1e-6')
    cool = D('1.778e-29')*t*lam**D('1.965')/(1+(lam/D('.541'))**D('.502'))**D('2.697')*D('1e-13')
    ne=nh*xe; r=alpha*ne*ne; c=cool*ne*ne
    chi=D('13.598434599702')*D('1.602176634e-19'); kb=D('1.380649e-23')
    oracle={'alpha_m3_s':alpha,'cooling_j_m3_s':cool,'r':r,'C':c,'dnHI':r,'dnHII':-r,'dne':-r,'duth':-c,'dubinding':-chi*r,'duescape':chi*r+c}
    errors={k:rel(out[k],v) for k,v in oracle.items()}
    tdot=(-c+D('1.5')*kb*t*r)/(D('1.5')*kb*(nh+nhe+ne))
    tscale=(c+D('1.5')*kb*t*r)/(D('1.5')*kb*(nh+nhe+ne))
    tdot_error=float(abs(f(out['Tdot'])-tdot)/tscale)
    residual=abs(out['duth']+out['dubinding']+out['duescape'])/(out['C']+out['duescape']-out['C'])
    assert max(errors.values()) <= 3e-12
    assert tdot_error <= 3e-12 and residual <= 1e-13
    assert out['dnHI']+out['dnHII'] == 0 and out['dne'] == out['dnHII'] and out['dHe'] == 0
    assert out['alpha_m3_s'] > 0 and out['cooling_j_m3_s'] > 0
    assert out['raw_guard'] == 'RAW_TEMPERATURE_DOMAIN'
    reports.append({'label':label,'z':e['z'],'coefficient_ledger_relative_errors':errors,'Tdot_scaled_error':tdot_error,'power_scaled_residual':residual,'state':out})
(ROOT/'evidence'/'VALIDATION.json').write_text(json.dumps({'unit':'COLD_HII_RR_THERMAL_COMPONENT01','status':'PASS_SCOPED','rows':reports,'build_count':1,'campaign_count':1,'history_executions':0,'native_domain_zero_reactants_guard_checks':'PASS','scientific_admission':'HOLD'},indent=2)+'\n')
print(json.dumps({'status':'PASS_SCOPED','rows':4,'max_relative_error':max(max(r['coefficient_ledger_relative_errors'].values()) for r in reports),'max_Tdot_scaled_error':max(r['Tdot_scaled_error'] for r in reports),'max_power_residual':max(r['power_scaled_residual'] for r in reports)}))
