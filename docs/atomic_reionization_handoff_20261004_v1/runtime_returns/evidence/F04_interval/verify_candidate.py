from pathlib import Path
import subprocess,json,math
from sage.all import RealIntervalField
root=Path.cwd();d=root/'.cuh/fastest-track/REI-F04-INTERVAL';R=RealIntervalField(200);cargo='/home/cosmosapjw/.cargo/bin/cargo';manifest='rust/rei_microphysics/Cargo.toml'
subprocess.run([cargo,'test','--manifest-path',manifest,'--test','interval_math','--locked'],check=True)
subprocess.run([cargo,'build','--manifest-path',manifest,'--example','interval_probe','--locked'],check=True)
oracle=json.loads((d/'oracle.json').read_text());commands=[]
for c in oracle['cases']:
 fields=[c['op'],str(c['lo']),str(c['hi'])]
 if c['op']=='POW':fields.append(str(c['p']))
 if c['op']=='JET_BETA':fields += [str(c['A']),str(c['B'])]
 commands.append(' '.join(fields))
commands+=oracle['invalid_commands'];binary=root/'rust/rei_microphysics/target/debug/examples/interval_probe'
p=subprocess.run([str(binary)],input='\n'.join(commands)+'\n',capture_output=True,text=True,check=True)
rows=[json.loads(line) for line in p.stdout.splitlines()];assert len(rows)==len(commands),(len(rows),len(commands));checks=0
def contains(value,lo,hi):
 global checks
 assert len(value)==2 and all(math.isfinite(x) for x in value) and value[0]<=value[1],value
 got=R(value[0],value[1]);expected=R(lo,hi)
 assert got.lower()<=expected.lower() and got.upper()>=expected.upper(),(value,lo,hi)
 checks+=1
for c,out in zip(oracle['cases'],rows):
 assert not out.get('error'),(c,out)
 if c['op']!='JET_BETA':contains(out['value'],c['range_lower'],c['range_upper'])
 else:
  assert len(out['gradient'])==7 and len(out['hessian'])==7 and all(len(row)==7 for row in out['hessian'])
  for sample in c['samples']:
   for key,val in [('value',out['value']),('gradient',out['gradient'][0]),('hessian',out['hessian'][0][0])]:contains(val,sample[key]['lo'],sample[key]['hi'])
  for i in range(1,7):contains(out['gradient'][i],0,0)
  for i in range(7):
   for j in range(7):
    if i or j:contains(out['hessian'][i][j],0,0)
for row in rows[len(oracle['cases']):]:assert row.get('error') is True,row;checks+=1
print(json.dumps({'status':'PASS','scalar_or_jet_cases':len(oracle['cases']),'interval_reference_checks':checks,'invalid_domains':len(oracle['invalid_commands']),'scope':'Finite interval/Jet2 prerequisite qualification only; actual HHe residual/root/remainder not certified','scientific_admission':'HOLD'}))
