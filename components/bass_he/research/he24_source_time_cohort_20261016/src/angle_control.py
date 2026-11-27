"""HE24 opt-in Gauss-Legendre source-ray angular-order control.

Modifies only the HE23 hard-coded 8-point source-angle leggauss call at runtime;
leaves source spectral Gauss4 untouched. Uses HE24 frozen-cell continuous newborn
source replacement. Exact original native Rust executable. No native code edits.
"""
import argparse,hashlib,json,pathlib,sys,time
import numpy as np

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--he23-root',type=pathlib.Path,required=True)
 p.add_argument('--native',type=pathlib.Path,required=True)
 p.add_argument('--out',type=pathlib.Path,required=True)
 p.add_argument('--q',type=float,required=True)
 p.add_argument('--angular-order',type=int,required=True)
 p.add_argument('--n',type=int,default=8)
 a=p.parse_args()
 if not(2<=a.angular_order<=32 and abs(a.q)<=.005 and 1<=a.n<=32):raise ValueError('bounds')
 if hashlib.sha256(a.native.read_bytes()).hexdigest()!='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe':raise ValueError('binary mismatch')
 sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
 from continuous_birth_control import activate
 state=activate(a.he23_root/'src')
 sys.path.insert(0,str(a.he23_root/'src'))
 from run_native import run_case
 from he22_native_client import OWNER_SOURCE_SHA
 orig=np.polynomial.legendre.leggauss
 calls=[]
 def controlled(order):
    calls.append(order)
    return orig(a.angular_order if order==8 else order)
 np.polynomial.legendre.leggauss=controlled
 a.out.mkdir(parents=True,exist_ok=False)
 start=time.perf_counter()
 try:
    result=run_case((str(a.native),4,a.n,a.q,20.,str(a.out/'native_calls'),OWNER_SOURCE_SHA))
    rec={'status':'PASS_SCOPED','result':result}
 except Exception as e:rec={'status':'HOLD','error':repr(e)}
 finally:np.polynomial.legendre.leggauss=orig
 rec.update(schema='HE24.angular_ray_order.v1',q=a.q,n=a.n,m=4,angular_order=a.angular_order,
      original_spectral_Gauss4_unchanged=all(x in (4,8) for x in calls),source_gauss8_calls=calls.count(8),
      source_spectral_gauss4_calls=calls.count(4),elapsed_s=time.perf_counter()-start,
      original_point_binary_sha256='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe')
 (a.out/'RESULT.json').write_text(json.dumps(rec,indent=2,sort_keys=True,allow_nan=False)+'\n')
 print('q',a.q,'ang',a.angular_order,'n',a.n,'status',rec['status'],'T',rec.get('result',{}).get('temperature_final_K'),flush=True)
 if rec['status']!='PASS_SCOPED':raise SystemExit(1)
if __name__=='__main__':main()
