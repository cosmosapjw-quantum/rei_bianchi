"""One build and one four-endpoint campaign; no history execution."""
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
def dump(name, value):
    (ROOT/'evidence'/name).write_text(json.dumps(value,indent=2)+'\n')
def rel(x,y): return float(abs(f(x)-y)/abs(y)) if y else (0.0 if x==0 else float('inf'))

expected={'baseline':'f39c09cac72359ecff4366ba5e0828d75c7d44185d126fd499f9e741bfb5005e',
          'refined':'4204d0ea44b23c868e5c5e330029bc35303ae85466cdb4671e60ba9d4a140611'}
rows=[]
for label,sha in expected.items():
    raw=(ROOT.parent/'rec_rei_cold_intake01_20261011'/'inputs'/f'{label}.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha
    for row in json.loads(raw):
        assert row['cosmology']['fsR']==row['cosmology']['meR']==1
        rows.append((label,row['endpoint']))
assert hashlib.sha256((ROOT/'source'/'history.c').read_bytes()).hexdigest()=='8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976'
archive=pathlib.Path('/home/cosmosapjw/rec_worktrees/p02b-flrw-endpoint-20261010/archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27'
for phase,command,limit,stdin in [
    ('BUILD',['cargo','build','--release','--locked','--manifest-path',str(ROOT/'native'/'Cargo.toml')],300,None),
    ('CAMPAIGN',[str(ROOT/'native'/'target'/'release'/'cold_compton_component01')],120,
     ''.join(' '.join(repr(e[k]) for k in ['Tm_K','Tgamma_K','nH_m3','nHe_m3','xe_per_H','H_s1'])+'\n' for _,e in rows))]:
    start=time.monotonic()
    proc=subprocess.run(command,input=stdin,text=True,capture_output=True,timeout=limit)
    wall=time.monotonic()-start
    (ROOT/'evidence'/f'FIRST_{phase}.stdout').write_text(proc.stdout)
    (ROOT/'evidence'/f'FIRST_{phase}.stderr').write_text(proc.stderr)
    receipt={'command':command,'exit':proc.returncode,'wall_s':wall,'timeout_s':limit}
    if phase=='CAMPAIGN': receipt.update(stdin=stdin,binary_sha256=hashlib.sha256(pathlib.Path(command[0]).read_bytes()).hexdigest())
    dump(f'{phase}_RECEIPT.json',receipt)
    assert proc.returncode==0, f'{phase} failed; preserve and stop for Astra'
outputs=[json.loads(line) for line in proc.stdout.splitlines()]
assert len(outputs)==4
reports=[]
for (label,e),out in zip(rows,outputs):
    tm,tg,nh,nhe,xe=(f(e[k]) for k in ['Tm_K','Tgamma_K','nH_m3','nHe_m3','xe_per_H'])
    rate=f(4.91466895548409e-22)*tg**4
    tdot=rate*xe/(1+xe+nhe/nh)*(tg-tm)
    q=f(1.5)*f(1.380649e-23)*nh*xe*rate*(tg-tm)
    errors={key:rel(out[key],oracle) for key,oracle in [('Tdot',tdot),('du_gas',q),('du_CMBbath',-q)]}
    parity=rel(out['legacy_recovered'],tdot)
    residual=abs(out['du_gas']+out['du_CMBbath'])/abs(out['du_gas'])
    eos_error=rel(out['du_gas'],f(1.5)*f(1.380649e-23)*(nh+nhe+nh*xe)*f(out['Tdot']))
    assert max(errors.values())<=3e-12 and parity<=3e-12 and eos_error<=3e-12
    assert residual<=1e-13
    assert all(out[k]==0 for k in ['dnHI','dnHII','dnHeI','dnHeII','dnHeIII','dne','dubinding'])
    assert out['Tdot']>0 and out['du_gas']>0 and out['du_CMBbath']<0
    reports.append({'label':label,'z':e['z'],'state':out,'relative_errors':errors,'legacy_nonequilibrium_parity_error':parity,'eos_relative_error':eos_error,'gas_bath_scaled_residual':residual})
result={'unit':'COLD_COMPTON_COMPONENT01','status':'PASS_SCOPED','rows':reports,
        'build_count':1,'campaign_count':1,'history_executions':0,
        'equal_temperature_zero_electron_hot_sign_checks':'PASS',
        'scientific_admission':'HOLD'}
dump('VALIDATION.json',result)
print(json.dumps({'status':'PASS_SCOPED','rows':4,'max_relative_error':max(max(r['relative_errors'].values()) for r in reports),'max_legacy_parity_error':max(r['legacy_nonequilibrium_parity_error'] for r in reports),'max_eos_relative_error':max(r['eos_relative_error'] for r in reports),'max_power_residual':max(r['gas_bath_scaled_residual'] for r in reports)}))
