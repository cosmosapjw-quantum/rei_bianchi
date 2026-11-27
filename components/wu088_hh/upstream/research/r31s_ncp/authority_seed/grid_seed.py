"""Minimal R31S M2 authority grid from bit-exact CP4 model fields.

This adapter reconstructs only C, exponents and v for bounded H-foreign M2.
The compact seed is a Git-tracked text representation of the exact binary64 values.
It is not a production runtime and does not replace full FROZEN_INPUTS.npz.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json
import numpy as np
from scipy.special import eval_hermite, roots_legendre

HERE = Path(__file__).resolve().parent
SEED = HERE/'M2_MODEL_SEED_SPARSE_HEX.json'
EXPECTED_SEED_GIT_BLOB_SHA1 = '43d5f2a79b8588e0844297dcf1c8ceb2df6b8ac0'
SOURCE_FROZEN_INPUTS_SHA256 = '8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
CP4_EXACT_WEIGHT_SOURCE_SHA256 = '8ad5273551728a3608b5f8d43ea77f732aebeddc96bea767be0f79206fcc39eb'
EXPECTED_ARRAY_BYTE_SHA256 = {
    'C': '5952ccecafea867f83f1454bf8f338f494770fe0356c7e026eb7222b32067b96',
    'exponents': '9564bcdfab5fc900321ecc12441b420b723f02d2991e62b3886e40c759c998a5',
    'v': '918ad765b4ad0f17db43ad69b4df1292cd481eebabba8ef1e3770b5af8aae4ac',
}

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def verify_authority() -> dict:
    got = git_blob_sha1(SEED)
    if got != EXPECTED_SEED_GIT_BLOB_SHA1:
        raise ValueError('M2 model seed Git blob drift')
    x = json.loads(SEED.read_text())
    if x.get('source_frozen_inputs_sha256') != SOURCE_FROZEN_INPUTS_SHA256:
        raise ValueError('source FROZEN_INPUTS identity drift')
    return {
        'm2_model_seed_git_blob_sha1': got,
        'source_frozen_inputs_sha256': SOURCE_FROZEN_INPUTS_SHA256,
        'cp4_exact_weight_source_sha256': CP4_EXACT_WEIGHT_SOURCE_SHA256,
        'array_byte_sha256': dict(EXPECTED_ARRAY_BYTE_SHA256),
    }

def inputs() -> dict:
    verify_authority()
    x = json.loads(SEED.read_text())
    ex = np.array([float.fromhex(v) for v in x['exponents']], dtype=np.float64)
    C = np.zeros(x['C_shape'], dtype=np.float64)
    for i,j,k,h in x['C_nonzero']:
        C[i,j,k] = float.fromhex(h)
    v = np.float64(float.fromhex(x['v']))
    built = {'C': C, 'exponents': ex, 'v': v}
    for key,a in built.items():
        if hashlib.sha256(np.asarray(a).tobytes(order='C')).hexdigest() != EXPECTED_ARRAY_BYTE_SHA256[key]:
            raise ValueError(f'reconstructed {key} byte fingerprint drift')
    return built

def nodes(n: int):
    if type(n) is not int or not 4 <= n <= 192:
        raise ValueError('frozen M2 node count must be integer 4..192')
    x,w = roots_legendre(n)
    u = (x+1)/2
    return u/(1-u), w/2/(1-u)**2

def exact_weights(t,w,mu=1.0):
    t = np.asarray(t,dtype=float); w = np.asarray(w,dtype=float)
    if t.shape != w.shape or np.any(t <= 0) or not np.isfinite(t).all() or not np.isfinite(w).all():
        raise ValueError('finite positive nodes and matching finite weights required')
    x = mu/(2*np.sqrt(t)); scale = 1/(2*np.sqrt(t))
    base = w*np.exp(-x*x)/(np.sqrt(np.pi)*np.sqrt(t))
    ladder = np.stack([base*eval_hermite(i,x)*scale**i for i in range(10)])
    return ladder[1:], ladder[:-1]

def contract(U,V,C):
    return np.stack([np.stack([left.T@C[:,:,k]@right for k in range(9)])
                     for left,right in ((U,U),(V,U),(U,V))])

def grid(n: int, ng: int=80):
    d = inputs(); t,w = nodes(n); U,V = exact_weights(t,w)
    W = contract(U,V,d['C']); gs,gw = nodes(ng); gw *= 2/np.sqrt(np.pi)
    return d,t,W,gs,gw
