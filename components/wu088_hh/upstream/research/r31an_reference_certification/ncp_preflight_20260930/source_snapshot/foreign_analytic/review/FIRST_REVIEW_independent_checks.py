"""Independent post-freeze component review. Does not import author validation."""
from pathlib import Path
import os,sys,json,time,ctypes,hashlib,subprocess,struct,functools
sys.dont_write_bytecode=True
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CAND=ROOT/'foreign_analytic'
sys.path[:0]=[str(CAND),str(ROOT/'exact_weights/deps'),str(ROOT/'issue_resolution/h_numerics')]
import numpy as np,mpmath as mp
from guarded_foreign import AnalyticForeign,LD,CD,ptr,DP,LP
from run_sentinel import inputs
mp.mp.dps=75
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def mr(x):
 a,b=LD(x).as_integer_ratio();return mp.mpf(a)/b
def mc(z):return mp.mpc(mr(z.real),mr(z.imag))
def save(name,obj):
 p=HERE/name
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(obj,indent=2)+'\n')
def ex(re,im='0'):return CD(LD(re))+CD(1j)*CD(LD(im))

def contractions():
 binary=HERE/'reduce_quad'
 command=['g++','-std=c++17','-O2','-fno-fast-math',str(HERE/'reduce_quad.cpp'),'-lquadmath','-o',str(binary)]
 cp=subprocess.run(command,capture_output=True,text=True,check=True)
 (HERE/'compile.stdout').write_text(cp.stdout);(HERE/'compile.stderr').write_text(cp.stderr)
 result=[]
 for side in (1,2):
  p=CAND/f'B128_side{side}_s1.npz'
  with np.load(p) as d:
   raw=np.ascontiguousarray(d['even_fields'].reshape(-1,5,6),dtype=CD)
   w=np.ascontiguousarray(d['W'][::2].reshape(5,-1),dtype=np.float64)
   got=np.ascontiguousarray(np.concatenate([d['even_per'].reshape(30),d['even'].reshape(6)]),dtype=CD)
   sa=np.ascontiguousarray(np.concatenate([d['even_per_sumabs'].reshape(30),d['even_sumabs'].reshape(6)]),dtype=LD)
   temp=HERE/f'reduction_side{side}.bin'
   with temp.open('wb') as f:
    f.write(struct.pack('<Q',raw.shape[0]));f.write(raw.tobytes());f.write(w.tobytes());f.write(got.tobytes());f.write(sa.tobytes())
   export_hash=sha(temp)
  cp=subprocess.run([str(binary),str(temp)],capture_output=True,text=True)
  if cp.returncode:raise RuntimeError(cp.stdout+cp.stderr)
  item=json.loads(cp.stdout);item.update(side=side,source=p.name,source_sha256=sha(p),export_sha256=export_hash,n=raw.shape[0])
  result.append(item);temp.unlink()
 return {'status':'PASS' if all(x['PASS'] for x in result) else 'FAIL','native_sum_count':72,'absolute_sum_count':72,
  'max_error_eps_sumabs':max(r['error_eps_sumabs']for x in result for r in x['rows']),
  'max_sumabs_error_eps_sumabs':max(r['sumabs_error_eps_sumabs']for x in result for r in x['rows']),
  'compile_command':command,'precision':'IEEE binary128 (113 significant bits); exact LD64/double input promotion; compensated independent reductions','cases':result}

def boys(h):
 pairs=[('-31.123456789','1.23456789'),('-17.9','-1.75'),('-.49997','.777'),('-1e-17','1.999'),('0','1.5707963267948966'),('5e-19','-2'),('19.512','-1.917'),('63.5','1.71'),('64','1.987'),('64.00000000000000001','-1.923'),('83.7','-.731'),('160.125','1.32')]
 xs=np.array([ex(*p)for p in pairs],CD);got=h.boys(xs);rows=[];eps=mr(np.finfo(LD).eps)
 for i,x in enumerate(xs):
  z=mc(x)
  for j in range(10):
   ref=mp.quad(lambda u:u**(2*j)*mp.exp(-z*u*u),[0,mp.mpf('.25'),mp.mpf('.5'),1])
   err=abs(mc(got[i,j])-ref)/(eps*max(1,abs(ref)))
   rows.append({'x':[str(x.real),str(x.imag)],'order':j,'error_over_eps':float(err),'PASS':bool(err<=128)})
 return {'status':'PASS'if all(x['PASS']for x in rows)else'FAIL','count':len(rows),'max_error_over_eps':max(x['error_over_eps']for x in rows),'reference':'mp75 adaptive defining integral on [0,1], no 1F1 or recurrence','rows':rows}

def field_oracle(g,side,n):
 g=[mc(z)for z in g];aa=[g[0].real,g[1].real];vv=[1/(2*a)for a in aa];prec=aa[side-1];R=g[10:13];dd=g[7:10]
 r10=mp.sqrt(10);outer=mp.sqrt((5+r10)/2);inner=mp.sqrt((5-r10)/2)
 x=[-outer,-inner,mp.mpf(0),inner,outer]
 w=[(7-2*r10)/60,(7+2*r10)/60,mp.mpf(8)/15,(7+2*r10)/60,(7-2*r10)/60]
 nodes=[(x[i],x[j],x[k],w[i]*w[j]*w[k])for i in range(5)for j in range(5)for k in range(5)]
 @functools.lru_cache(maxsize=20000)
 def gamma(gam):
  lam=gam*gam/(prec+gam*gam);var=vv.copy();var[side-1]=1/(2*(prec+gam*gam));v=sum(var)
  d=[dd[a]-(1 if side==1 else -1)*lam*R[a]for a in range(3)]
  ne=[[g[3],g[4]],[g[5],g[6]]]
  ne[side-1]=[ne[side-1][k]-lam*R[a]for k,a in enumerate((0,2))]
  scale=mp.sqrt(2*v);out=[mp.mpc(0)for _ in range(6)]
  for x,y,z,wt in nodes:
   yy=[d[0]+scale*x,d[1]+scale*y,d[2]+scale*z]
   radial=sum(q*q for q in yy)**n;out[0]+=wt*radial;out[3]+=wt*radial
   for e in (0,1):
    for k,a in enumerate((0,2)):
     conditional=ne[e][k]+(1 if e==0 else -1)*var[e]/v*(yy[a]-d[a])
     out[3*e+k+1]+=wt*conditional*radial
  pref=g[2]*(prec/(prec+gam*gam))**mp.mpf('1.5')*mp.exp(-prec*lam*sum(r*r for r in R))*2/mp.sqrt(mp.pi)
  return [pref*v for v in out]
 return lambda c:mp.quad(lambda gam:gamma(gam)[c],[0,1,mp.inf]),gamma

def fields(h):
 inp=inputs();a=float(inp['exponents'][3]);b=float(inp['exponents'][8]);speed=float(inp['v'])
 with np.load(CAND/'B128_side2_s1.npz')as d:t=d['t']
 _,g=h.even_geometry(a,b,np.array([t[89]]),np.array([t[26]]),3.,speed,2)
 cases=[('actual_z3_side2_new_node',2,4,g.reshape(13,1))]
 A=LD('.93');B=LD('1.71');m1=np.array([ex('.31','.07'),ex('-.17','.13'),ex('.41','-.19')]);m2=np.array([ex('-.24','-.11'),ex('.29','.04'),ex('-.37','.17')]);C=np.array([LD('.09'),LD('-.12'),LD('.06')]);n1=m1-np.array([LD('.07'),LD('.03'),LD('-.05')]);n2=m2-np.array([LD('-.02'),LD('.08'),LD('.14')])
 gg=np.array([A,B,ex('.87','-.21'),n1[0],n1[2],n2[0],n2[2],*(m1-m2),*(m2-C)],CD).reshape(13,1)
 cases.append(('noncollinear_side2',2,3,gg))
 # A real coincident inserted mean and nucleus, with complex spectator mean.
 m1=np.zeros(3,CD);n1=m1-np.array([LD('.07'),LD('.03'),LD('-.05')]);m2=np.array([ex('-.24','-.11'),ex('.29','.04'),ex('-.37','.17')])
 gc=np.array([A,B,ex('.87','-.21'),n1[0],n1[2],n2[0],n2[2],*(m1-m2),*m1],CD).reshape(13,1)
 cases.append(('coincident_side1',1,4,gc));rows=[];raw=[]
 for name,side,n,g in cases:
  got=h.even_packed(g,np.ones((5,1),np.float64),side)['raw_fields'].reshape(5,6)[n]
  oracle,cache=field_oracle(g[:,0],side,n)
  for c in range(6):
   ref=oracle(c);err=abs(mc(got[c])-ref)/max(1,abs(ref))
   rows.append({'case':name,'side':side,'power':2*n,'component':c,'scaled_error':float(err),'ref_re':mp.nstr(ref.real,60),'ref_im':mp.nstr(ref.imag,60),'PASS':bool(err<=mp.mpf('2e-15'))})
  raw.append({'case':name,'input':[[str(z.real),str(z.imag)]for z in g[:,0]],'cache':str(cache.cache_info())})
  print(json.dumps({'field_case':name,'count':len(rows)}),flush=True)
 return {'status':'PASS'if all(x['PASS']for x in rows)else'FAIL','count':len(rows),'max_scaled_error':max(x['scaled_error']for x in rows),'reference':'mp75 direct gamma quadrature and tensor five-point normalized Gauss-Hermite rule (exact for Cartesian polynomial degree <=9); conditional active coordinate. No Boys or radial moment polynomial recurrence.','rows':rows,'inputs':raw}

def guards(h):
 rows=[]
 def record(name,st,unchanged,expected):rows.append({'name':name,'status':st,'atomic_outputs':bool(unchanged),'PASS':bool(st==expected and unchanged)})
 x=np.array([ex('1'),ex('-32.00001')]);out=np.full((2,10),ex('19','7'),CD);before=out.copy()
 st=h.newlib.fg_boys(2,ptr(x),4,ptr(out),40);record('Boys_late_domain_no_output',st,np.array_equal(out,before),-206)
 buf=ctypes.create_string_buffer(128);unaligned=ctypes.cast(ctypes.addressof(buf)+1,LP)
 st=h.newlib.fg_boys(1,unaligned,2,ptr(out),20);record('Boys_unaligned_rejected',st,np.array_equal(out,before),-201)
 g=np.zeros((13,2),CD);g[0:2]=1;g[2]=1;g[2,1]=LD('1e4930');w=np.ones((5,2),np.float64)
 raw=np.full((2,5,2,3),ex('7','-9'),CD);got=np.full((6,2,3),ex('11','8'),CD);sa=np.full((6,2,3),LD(13));copies=[raw.copy(),got.copy(),sa.copy()]
 st=h.newlib.fg_even(2,1,ptr(g),g.size*2,ptr(w,DP),w.size,ptr(raw),raw.size*2,ptr(got),got.size*2,ptr(sa),sa.size)
 record('even_intermediate_overflow_atomic',st,all(np.array_equal(a,b)for a,b in zip([raw,got,sa],copies)),-207)
 odd=np.zeros((20,2),CD);odd[0:3]=1;odd[4]=1;odd[3,1]=-65
 ow=np.ones((4,2),np.float64);oo=np.full((2,3),ex('5','3'),CD);ab=np.full((2,3),LD(2));cb=[oo.copy(),ab.copy()]
 st=h.newlib.fg_odd(2,ptr(odd),odd.size*2,ptr(ow,DP),ow.size,ptr(oo),oo.size*2,ptr(ab),ab.size)
 record('odd_late_domain_atomic',st,np.array_equal(oo,cb[0])and np.array_equal(ab,cb[1]),-206)
 lib=ctypes.CDLL(None);lib.fegetround.restype=ctypes.c_int;lib.fesetround.argtypes=[ctypes.c_int];old=lib.fegetround();caught=False
 try:
  if lib.fesetround(0x800):raise RuntimeError('rounding setup failed')
  try:h.boys(np.array([ex('1')],CD))
  except RuntimeError:caught=True
 finally:lib.fesetround(old)
 rows.append({'name':'unsupported_rounding_python_rejected','PASS':caught})
 return {'status':'PASS'if all(x['PASS']for x in rows)else'FAIL','count':len(rows),'rows':rows}

def assembly():
 rows=[];eps=mr(np.finfo(LD).eps)
 for p in sorted(CAND.glob('B*_side*_s*.npz')):
  with np.load(p)as d:
   for c in range(6):
    terms=[mc(v)*mr(w)for v,w in zip(d['odd_gamma_planes'].reshape(80,6)[:,c],d['gamma_weights'])]
    ref=mp.fsum(terms);sa=mp.fsum(abs(v)for v in terms);gap=abs(mc(d['odd'].reshape(6)[c])-ref)
    ratio=gap/(eps*sa)if sa else 0
    combined=mc(d['even'].reshape(6)[c])+ref;sumscale=abs(mc(d['even'].reshape(6)[c]))+sa
    aratio=abs(mc(d['combined'].reshape(6)[c])-combined)/(eps*sumscale)if sumscale else 0
    rows.append({'case':p.stem,'component':c,'gamma_error_eps_sumabs':float(ratio),'assembly_error_eps_sumabs':float(aratio),'PASS':bool(ratio<=128 and aratio<=128)})
 return {'status':'PASS'if all(x['PASS']for x in rows)else'FAIL','count':len(rows),'rows':rows}

def main():
 started=time.perf_counter();sources={str(p.relative_to(ROOT)):sha(p)for p in [CAND/'analytic.cpp',CAND/'guarded_foreign.py',CAND/'build_native.py',CAND/'SCIENTIFIC_CONTRACT.md',CAND/'DERIVATION.md']}
 save('SCOPE.json',{'reviewer':'/root/foreign_review','candidate_author':False,'author_validation_designer':False,'model':'MODEL_UNRESOLVED','source_freeze_sha256':sources,'scope':'Exact-even foreign component, odd reconstruction, guarded API and limited primitive evidence; full production HOLD','independence':'Source read after owner freeze; reviewer-owned independent reference code only'})
 print('contraction_start',flush=True);save('CONTRACTION_CHECKS.json',contractions());print('contraction_done',flush=True)
 h=AnalyticForeign(HERE/'cache');save('REVIEW_NATIVE_IDENTITY.json',h.identity)
 save('BOYS_CHECKS.json',boys(h));print('boys_done',flush=True)
 save('GUARD_CHECKS.json',guards(h));print('guards_done',flush=True)
 save('ASSEMBLY_CHECKS.json',assembly());print('assembly_done',flush=True)
 save('FIELD_CHECKS.json',fields(h));print('fields_done',flush=True)
 unchanged={name:sha(ROOT/name)==digest for name,digest in sources.items()}
 save('EXECUTION.json',{'seconds':time.perf_counter()-started,'source_unchanged':unchanged,'all_sources_unchanged':all(unchanged.values()),'review_script_sha256':sha(__file__),'native_reference_source_sha256':sha(HERE/'reduce_quad.cpp')})
 if not all(unchanged.values()):raise RuntimeError('source changed during review')
 print('REVIEW_EXECUTION_DONE',flush=True)
if __name__=='__main__':main()
