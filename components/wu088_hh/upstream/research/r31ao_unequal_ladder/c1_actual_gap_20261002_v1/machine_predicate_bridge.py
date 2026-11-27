"""Exact scalar replay; does not rerun the archived comparator or SVD."""
from fractions import Fraction as Q
import re
from c1_support import BindingError, vendor

E = vendor('engine')
LIMITS = E.Limits(max_precision=128,max_entries=94,max_integer_bits=8192,
                  max_work_bits=32768,max_operations=100000)
TOKEN = re.compile(r'(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE]([+-]?[0-9]+))?\Z')

def token_bits(token: str) -> int:
    # JSON norm scalars must be nonnegative, finite decimal lexical tokens.
    if type(token) is not str or not 1 <= len(token) <= 64:
        raise BindingError('decimal lexical string required')
    match = TOKEN.fullmatch(token)
    if match is None or (match[1] is not None and abs(int(match[1])) > 400):
        raise BindingError('invalid or over-budget scalar token')
    return E.round_binary64(Q(token),limits=LIMITS)

def rounding_bracket(q: Q):
    """The directed-down/up finite binary64 values, by exact rational comparison."""
    bits = E.round_binary64(q,limits=LIMITS)
    rounded = E.binary64_value(bits)
    if rounded == q:
        return rounded, rounded
    if rounded < q:
        neighbor = bits - 1 if bits >> 63 else bits + 1
        return rounded, E.binary64_value(neighbor)
    neighbor = bits + 1 if bits >> 63 else (bits - 1 if bits else (1 << 63) | 1)
    return E.binary64_value(neighbor), rounded

def audit_tokens(local, other, comparison):
    if comparison not in ('PRIMARY','SECONDARY'):
        raise BindingError('PRIMARY or SECONDARY required')
    if not isinstance(local,(list,tuple)) or not isinstance(other,(list,tuple)) or len(local)!=2 or len(other)!=2:
        raise BindingError('exactly K,Dmax tokens required')
    lb,ob = [token_bits(t) for t in local],[token_bits(t) for t in other]
    lv,ov = [E.binary64_value(b) for b in lb],[E.binary64_value(b) for b in ob]
    rne = E.audit_frozen_binary64(lb,ob,comparison=comparison,limits=LIMITS)
    weak_all, strict_all, brackets = [], [], []
    for a,b in zip(lv,ov):
        add = rounding_bracket(b + E.TOLERANCE)
        expr = b-a if comparison=='PRIMARY' else b-E.TOLERANCE
        sub = rounding_bracket(expr)
        weak_all.append(a <= add[0])
        strict_all.append(sub[0] > E.TOLERANCE if comparison=='PRIMARY' else a < sub[0])
        brackets.append({'other_plus_tol':[str(x) for x in add],
                         'strict_expression':[str(x) for x in sub]})
    robust = all(weak_all) and any(strict_all)
    return {'comparison':comparison, 'metric_order':['K','Dmax'],
            'local_decimal_tokens':list(local),'other_decimal_tokens':list(other),
            'local_bits':[f'{b:016x}' for b in lb], 'other_bits':[f'{b:016x}' for b in ob],
            'rne':rne, 'all_ieee_modes_supported':True if robust else None,
            'all_modes_semantics':'Sufficient across directed rounding, toward zero and nearest for these fixed represented input scalars; null means not established',
            'directed_expression_brackets':brackets,
            'historical_fenv_verified':False, 'historical_SVD_rerun':False,
            'input_provenance_admitted':False}
