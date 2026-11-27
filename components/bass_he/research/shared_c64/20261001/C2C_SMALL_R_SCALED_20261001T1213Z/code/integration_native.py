"""Strict binary64 weighted products, fixed-order patch sums, no backend fallback."""
import ctypes,hashlib,json,os
from pathlib import Path
from functools import lru_cache
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def native_identity():
 p=Path(os.environ.get('BASS_INNER_LIBRARY',str(ROOT/'native/build/libbass_inner.so'))).resolve(strict=True)
 m=p.with_suffix('.build.json');raw=m.read_bytes();meta=json.loads(raw);digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if meta.get('schema')!='bass-inner-build-v1' or meta.get('abi')!=1 or meta.get('library_sha256')!=digest or meta.get('source_sha256')!=hashlib.sha256((ROOT/'native/inner_product.f90').read_bytes()).hexdigest():raise RuntimeError('INNER_NATIVE_IDENTITY_MISMATCH')
 if os.environ.get('BASS_INNER_EXPECTED_SHA256',digest)!=digest:raise RuntimeError('INNER_NATIVE_EXPECTED_SHA256_MISMATCH')
 return {'library':str(p),'library_sha256':digest,'build_manifest_sha256':hashlib.sha256(raw).hexdigest(),'build':meta}
@lru_cache(maxsize=2)
def _load(path,digest):
 lib=ctypes.CDLL(path);lib.bass_inner_abi.restype=ctypes.c_int
 if lib.bass_inner_abi()!=1:raise RuntimeError('INNER_ABI_MISMATCH')
 f64=np.ctypeslib.ndpointer(dtype=np.float64,ndim=1,flags='C_CONTIGUOUS');i32=np.ctypeslib.ndpointer(dtype=np.int32,ndim=1,flags='C_CONTIGUOUS')
 lib.bass_inner.argtypes=[ctypes.c_int,ctypes.c_int,i32,f64,f64,f64,f64];lib.bass_inner.restype=None
 return lib

def sum_products(weights,left,right,counts):
 arr=[np.asarray(x) for x in (weights,left,right)];co=np.asarray(counts)
 if any(np.iscomplexobj(x) or x.ndim!=1 or not np.isfinite(x).all() for x in arr):raise ValueError('finite real vectors required')
 n=len(arr[0])
 if any(len(x)!=n for x in arr) or n<1 or n>np.iinfo(np.int32).max:raise ValueError('incompatible or overflowing vectors')
 if co.ndim!=1 or len(co)<1 or not np.issubdtype(co.dtype,np.integer) or np.any(co<=0) or np.any(co>np.iinfo(np.int32).max) or sum(map(int,co))!=n:raise ValueError('invalid patch counts')
 a=[np.ascontiguousarray(x,dtype=np.float64) for x in arr];co=np.ascontiguousarray(co,dtype=np.int32);identity=native_identity();out=np.zeros(1)
 _load(identity['library'],identity['library_sha256']).bass_inner(n,len(co),co,*a,out)
 if not np.isfinite(out).all():raise FloatingPointError('nonfinite native inner product')
 return float(out[0])
