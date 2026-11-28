"""Read-only source boundary for C0A. Never imports historical receiver code."""
import ast
import hashlib
import re
from pathlib import Path

MAX_SOURCE_BYTES = 1024*1024
CONTEXT = {'geometry':'Bianchi_I_fixed_principal_or_commuting',
           'measure':'initial_isotropic', 'matter_frame':'non_tilted',
           'quantity':'log_energy_ratio_after_isotropic_redshift'}

class SourceUnavailable(RuntimeError):
    """A declared call site is not an admitted rate implementation."""

def call_inventory(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError('bounded regular source file required')
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    tree = ast.parse(text)
    result = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == 'r2n'):
            segment = ast.get_source_segment(text,node)
            result.append({'function':node.func.attr,'line':node.lineno,
                           'end_line':node.end_lineno,'call_sha256':hashlib.sha256(segment.encode()).hexdigest()})
    return sorted(result,key=lambda r:(r['line'],r['function']))

def verify_sources(root, lock):
    root = Path(root).resolve(strict=True)
    if not isinstance(lock,list) or not lock or len(lock)>256:
        raise ValueError('nonempty bounded source lock required')
    seen = set()
    for item in lock:
        if type(item) is not dict or set(item) != {'path','bytes','sha256'}:
            raise ValueError('invalid source record')
        name = item['path']
        if type(name) is not str or not name or name in seen:
            raise ValueError('source path duplicate or invalid')
        seen.add(name)
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('unsafe source path')
        if type(item['bytes']) is not int or not 0<=item['bytes']<=MAX_SOURCE_BYTES:
            raise ValueError('invalid source byte count')
        if type(item['sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',item['sha256']):
            raise ValueError('invalid SHA256')
        p = root/rel
        if any((root/Path(*rel.parts[:i])).is_symlink() for i in range(1,len(rel.parts)+1)):
            raise ValueError('symlink source forbidden')
        if not p.is_file() or p.stat().st_size != item['bytes']:
            raise ValueError('source missing or size mismatch: '+name)
        if hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('source hash mismatch: '+name)
    return {'verified':len(seen)}

def require_g7_context(context):
    if type(context) is not dict or context != CONTEXT:
        raise ValueError('G7 requires exact fixed-principal initial-isotropic context')
    return True

def request_physical_rates(*args, **kwargs):
    """This release has NO rate-function bodies or physical admission path.

A future source-bound continuation must supply and review those dependencies.
No boolean flag, callback, or manufactured fixture can override this state.
"""
    raise SourceUnavailable('MICRO0_DEFINITION_AND_PHYSICAL_DOMAIN_NOT_BOUND')
