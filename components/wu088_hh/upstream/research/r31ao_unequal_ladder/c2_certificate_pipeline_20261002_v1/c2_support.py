"""Bounded exact C2 support. No scientific dispatch or floating arithmetic."""
from fractions import Fraction
from pathlib import Path
import hashlib, importlib.util, json, os, re, sys

ROOT = Path(__file__).resolve().parent
LADDER = ROOT/'vendor/repo/research/r31ao_unequal_ladder'
PIN_SHA = '9b81cb18eedd44b079bd96fcebeb4792b168d1cbe059980a6d9f63ae407bd9ea'
MAX_BYTES = 32 * 1024 * 1024
BITS = 8192

class ContractError(ValueError):
    pass

def complete_indices(indices, count):
    if type(count) is not int or not 1 <= count <= 2592:
        raise ContractError('count outside contract')
    seen = set()
    for value in indices:
        if len(seen) >= count: raise ContractError('count exceeds contract')
        if type(value) is not int or not 0 <= value < count: raise ContractError('index outside contract')
        if value in seen: raise ContractError('duplicate index')
        seen.add(value)
    if len(seen) != count: raise ContractError('missing indices: ' + str(count-len(seen)))
    return tuple(sorted(seen))

def canonical(value):
    try: return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    except (TypeError, ValueError, RecursionError) as e: raise ContractError('finite JSON required') from e

def digest(value): return hashlib.sha256(canonical(value)).hexdigest()
def byte_sha(value): return hashlib.sha256(value).hexdigest()

def sha(value):
    if type(value) is not str or re.fullmatch('[0-9a-f]{64}', value) is None: raise ContractError('canonical SHA256 required')
    return value

def keys(value, required):
    if type(value) is not dict or set(value) != set(required): raise ContractError('missing/extra keys')

def typed_equal(actual, expected, name):
    if type(actual) is not type(expected) or actual != expected: raise ContractError('binding mismatch: '+name)

def sealed(value, key):
    if type(value) is not dict or key not in value: raise ContractError('missing seal')
    if digest({k:v for k,v in value.items() if k != key}) != sha(value[key]): raise ContractError('seal mismatch: '+key)

def seal(value, key):
    if key in value: raise ContractError('already sealed')
    return {**value, key:digest(value)}

def rational(token):
    if type(token) is not str or len(token)>5000 or re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?', token) is None:
        raise ContractError('bounded canonical rational required')
    if any(len(s.lstrip('-')) > 2467 for s in token.split('/')): raise ContractError('integer allocation cap')
    q = Fraction(token)
    if str(q) != token: raise ContractError('noncanonical rational')
    return bounded(q)

def bounded(q):
    if max(q.numerator.bit_length(), q.denominator.bit_length()) > BITS: raise ContractError('rational bit cap')
    return q

def dyadic(token):
    q=rational(token)
    if q.denominator & (q.denominator-1): raise ContractError('dyadic required')
    return q

def arf_interval(lo, hi):
    lo,hi=dyadic(str(lo)),dyadic(str(hi))
    if lo>hi: raise ContractError('reversed interval')
    n=max(lo.denominator.bit_length()-1, hi.denominator.bit_length()-1)
    return {'lower_mantissa':str(int(lo*(1<<n))), 'upper_mantissa':str(int(hi*(1<<n))), 'exponent2':str(-n)}

def strict_bytes(data):
    if type(data) is not bytes or len(data)>MAX_BYTES: raise ContractError('JSON byte cap')
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise ContractError('duplicate JSON key')
            out[k]=v
        return out
    def refuse(_): raise ContractError('JSON float/nonfinite forbidden')
    try: return json.loads(data,object_pairs_hook=pairs,parse_float=refuse,parse_constant=refuse)
    except (ValueError, UnicodeError, RecursionError) as e: raise ContractError('invalid JSON: '+str(e)) from e

def read_json(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_BYTES: raise ContractError('bounded regular input required')
    with p.open('rb') as f: return strict_bytes(f.read(MAX_BYTES+1))

def write_new(path, value):
    data=canonical(value)+b'\n'
    if len(data)>MAX_BYTES: raise ContractError('output byte cap')
    with Path(path).open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())

def verify_pins(root=ROOT):
    root=Path(root)
    data=(root/'SOURCE_PINS.json').read_bytes()
    if byte_sha(data)!=PIN_SHA: raise ContractError('source pin manifest changed')
    pins=strict_bytes(data)
    for rel,info in pins['files'].items():
        p=root/rel
        if p.is_symlink() or not p.is_file(): raise ContractError('source missing/symlink: '+rel)
        if p.stat().st_size!=info['bytes'] or byte_sha(p.read_bytes())!=info['sha256']:
            raise ContractError('source/input changed: '+rel)
    return pins

def load(name, path):
    path=Path(path).resolve()
    if name in sys.modules:
        if Path(sys.modules[name].__file__).resolve()!=path: raise ContractError('ambiguous import')
        return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod
    old=sys.dont_write_bytecode; sys.dont_write_bytecode=True
    try: spec.loader.exec_module(mod)
    finally: sys.dont_write_bytecode=old
    return mod
