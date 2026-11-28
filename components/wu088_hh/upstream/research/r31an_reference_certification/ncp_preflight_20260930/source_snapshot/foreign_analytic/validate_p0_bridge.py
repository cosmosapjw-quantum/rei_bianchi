"""Read-only bridge to independently restored previous p0 evidence."""
from pathlib import Path
import hashlib,json
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=HERE/'P0_BRIDGE_RESULTS.json'
 if out.exists():raise FileExistsError(out)
 rows=[]
 for side in (1,2):
  oldpath=ROOT/f'issue_resolution/h_numerics/P0_side{side}.npz'
  newpath=HERE/f'B128_side{side}_s1.npz'
  with np.load(oldpath)as old,np.load(newpath)as new:
   match=all(np.array_equal(a,b)for a,b in [(old['t'],new['t']),(old['W0'],new['W'][0]),(old['norm'],new['norm'])])
   a=old['raw_fields'];b=new['even_fields'].reshape(-1,5,2,3)[:,0]
   scaled=np.max(abs(a-b)/np.maximum(1,abs(a)))
   gap=np.max(abs(old['analytic']-new['even_per'][0]*new['norm']))
   rows.append({'side':side,'inputs_exact_match':match,'field_count':a.size,'max_scaled_field_difference':float(scaled),'max_contracted_difference_Eh':float(gap),'PASS':bool(match and scaled<=2e-15 and gap<=2e-7),'old_file_sha256':sha(oldpath),'new_file_sha256':sha(newpath)})
 result={'status':'PASS'if all(r['PASS']for r in rows)else'FAIL','rows':rows,'reference_scope':'Previous restored p0 implementation; same-source bridge, not independent oracle. Original scalar 2e-15 and H screen 2e-7 unchanged.','source_sha256':sha(Path(__file__))}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
