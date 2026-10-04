from pathlib import Path
import json,subprocess,tempfile
r=Path.cwd(); d=r/'.cuh/fastest-track/REI-F02'
cases=json.loads((d/'decimal-oracle.json').read_text())['cases']
rlibs=list((r/'rust/rei_microphysics/target/debug/deps').glob('librei_microphysics-*.rlib'))
rlib=max(rlibs,key=lambda p:p.stat().st_mtime_ns)
parts=['use rei_microphysics::{hydrogen_step,HydrogenRates}; fn main(){']
for j,c in enumerate(cases):
 q=c['rates']; fmt=lambda x:format(x,'.17e')+'_f64'
 parts.append('let a=hydrogen_step('+fmt(c['x'])+','+fmt(c['dt'])+',HydrogenRates{photo_per_s:'+fmt(q[0])+',collisional_per_s:'+fmt(q[1])+',secondary_per_s:'+fmt(q[2])+',recombination_per_s:'+fmt(q[3])+'}).unwrap();')
 for f,v in zip(['x_next','photo_events','collisional_events','secondary_events','recombination_events'],c['expected']):
  parts.append('assert!((a.'+f+'-'+fmt(v)+').abs()<=4e-14*('+fmt(v)+').abs()+f64::from_bits(2),"case '+str(j)+' '+f+': {} expected {}",a.'+f+','+fmt(v)+');')
parts.append('}')
with tempfile.TemporaryDirectory() as t:
 p=Path(t); (p/'main.rs').write_text('\n'.join(parts))
 subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc','--edition','2021',str(p/'main.rs'),'--extern','rei_microphysics='+str(rlib),'-L','dependency='+str(rlib.parent),'-o',str(p/'check')],check=True)
 subprocess.run([str(p/'check')],check=True,timeout=10)
print(f'Independent Decimal(1100) closed-form endpoint + 4 event counts: {len(cases)} cases PASS; subnormal atol=2 ulps; finite point checks only.')
