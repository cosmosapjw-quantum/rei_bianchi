"""X1 frozen-contract standalone exact represented-input moment checker.

No projection, clipping, source correction or HE/runtime activation. The immutable
return value is JSON text (use .as_dict()). NumPy eigenvalues are diagnostic only.
"""
from fractions import Fraction
import itertools
import json
import math
import numbers
import sys

PASS = 'PASS'
FAIL = 'FAIL'
BOUNDARY = 'INDETERMINATE'


def _raw(x):
    if isinstance(x, Fraction): return {'rational': str(x)}
    if isinstance(x, (tuple,list)): return [_raw(v) for v in x]
    if isinstance(x, dict): return {str(k):_raw(v) for k,v in x.items()}
    if isinstance(x,float) and not math.isfinite(x): return {'nonfinite':repr(x)}
    if x is None or isinstance(x,(str,int,float,bool)): return x
    return {'type':type(x).__name__,'repr':repr(x)}


class Diagnostic(str):
    """Immutable JSON-serializable diagnostic record, encoded as strict JSON."""
    def __new__(cls,payload):
        return super().__new__(cls,json.dumps(_raw(payload),sort_keys=True,allow_nan=False))
    def as_dict(self): return json.loads(self)


def _scalar(x):
    if isinstance(x,bool) or not isinstance(x,numbers.Real): return False
    if isinstance(x,(int,Fraction)): return True
    try: return math.isfinite(x)
    except (TypeError,ValueError,OverflowError): return False


def _rational(x):
    return Fraction(x) if isinstance(x,(int,Fraction)) else Fraction.from_float(float(x))


def _det(a):
    if len(a)==1: return a[0][0]
    return sum((-1)**j*a[0][j]*_det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))


def _float(x):
    try: return float(x)
    except OverflowError: return {'not_binary64_representable':str(x)}


def validate_energy_moments(K,S,count=2,E=None,I=None,Kp=None,axis=None,D=None,
                            uncertainty=None,units='J',mode='source_rounded'):
    """Validate common-unit count-two inclusive kinetic energy moments.

    units is 'J' or 'fixture_energy'. uncertainty maps names K,S,E,I,Kp,D,
    axis to absolute component error bounds. Missing source error is UNKNOWN.
    Positive supplied bounds conservatively cause INDETERMINATE; no covariance
    is invented. mode='exact_input' declares represented operands authoritative;
    int/Fraction fixtures declare exact_input explicitly. Float sign/identity
    violations in default source_rounded mode remain source-indeterminate.
    """
    out=dict(schema='X1-v2',raw=_raw(dict(K=K,S=S,count=count,E=E,I=I,Kp=Kp,axis=axis,D=D,uncertainty=uncertainty,units=units,mode=mode)),
             failures=[],boundaries=[],source_unchanged=True,represented_input_only=True,source_uncertainty='not_supplied' if uncertainty is None else 'supplied',
             units=units,mode=mode,scope='conditional represented-input moment cone only; no physical calibration or HE activation')
    def bad(x): out['failures'].append(x)
    def done():
        out['decision']=FAIL if out['failures'] else BOUNDARY if out['boundaries'] else PASS
        return Diagnostic(out)
    if not isinstance(units,str) or units not in ('J','fixture_energy'): bad('single common units tag J or fixture_energy required')
    if mode not in ('source_rounded','exact_input'): bad('mode must be source_rounded or exact_input')
    vals=dict(K=K,count=count)
    vals.update({n:v for n,v in [('E',E),('I',I),('Kp',Kp),('D',D)] if v is not None})
    for n,v in vals.items():
        if not _scalar(v): bad(n+': finite real scalar required (bool/complex excluded)')
    try:
        m=[list(r) for r in S]
        if len(m)!=3 or any(len(r)!=3 for r in m) or any(not _scalar(v) for r in m for v in r): raise ValueError()
    except (TypeError,ValueError):
        bad('S: finite real 3x3 matrix required');return done()
    ax=None
    if axis is not None:
        try:
            ax=list(axis)
            if len(ax)!=3 or any(not _scalar(v) for v in ax): raise ValueError()
        except (TypeError,ValueError): bad('axis: finite real three-vector required')
    if (axis is None)!=(D is None): bad('axis and D must be supplied together')
    if any(v is not None for v in (E,I,Kp)) and any(v is None for v in (E,I,Kp)): bad('E,I,Kp must be supplied together')
    errors={}
    if uncertainty is not None:
        if not isinstance(uncertainty,dict) or set(uncertainty)-{'K','S','E','I','Kp','D','axis'}: bad('uncertainty: named absolute component/energy bounds required')
        else:
            for n,v in uncertainty.items():
                if not _scalar(v) or v<0: bad('uncertainty.'+n+': finite nonnegative absolute bound required')
                else: errors[n]=_rational(v)
    if out['failures']: return done()
    if count!=2: bad('inclusive count must equal two')
    if count<0: bad('count must be nonnegative')
    if K<0: bad('K must be nonnegative')
    for n,v in [('E',E),('I',I),('Kp',Kp)]:
        if v is not None and v<0: bad(n+' must be nonnegative')
    q={n:_rational(v) for n,v in vals.items()}
    a=[[_rational(v) for v in r] for r in m]
    qa=[_rational(v) for v in ax] if ax is not None else None
    all_exact=all(isinstance(v,(int,Fraction)) for v in list(vals.values())+[v for r in m for v in r]+(ax or []))
    authoritative=mode=='exact_input'
    if authoritative and all_exact and uncertainty is None:
        out['source_uncertainty']='exact_mathematical_fixture'
    out['certificate']=dict(method='exact rational symmetry, trace, seven principal minors and optional identities',
                            interpretation='exact input' if authoritative else 'exact represented binary64 input; source rounding unknown',
                            eigenvalues='diagnostic only; no eigensolver allowance used for admission',
                            source_error_bounds=errors if uncertainty is not None else None)
    if any(errors.values()): out['boundaries'].append('positive source error enclosure: robust moment-cone membership not established')
    def check(name,valid,residual=None):
        if residual is not None: out.setdefault('exact_residuals',{})[name]=str(residual)
        if not valid:
            if authoritative and not any(errors.values()): bad(name)
            else: out['boundaries'].append(name+': represented-input violation; source uncertainty unresolved')
    asym=max(abs(a[i][j]-a[j][i]) for i in range(3) for j in range(3))
    out['asymmetry']=_float(asym)
    check('symmetry',asym==0,asym)
    tr=sum(a[i][i] for i in range(3))-q['K']
    out['trace_residual']=_float(tr)
    check('trace=K',tr==0,tr)
    minors=[]
    for size in (1,2,3):
        for ix in itertools.combinations(range(3),size): minors.append(_det([[a[i][j] for j in ix] for i in ix]))
    out['exact_principal_minors']=[str(v) for v in minors]
    if asym==0: check('PSD principal minor negative',all(v>=0 for v in minors))
    out['min_eigenvalue']=None
    # Scale before floating diagnostics; never let an unavailable diagnostic
    # change or invalidate the exact sign certificate.
    scale=max(abs(v) for r in a for v in r)
    out['input_scale']=_float(max(scale,abs(q['K'])))
    try:
        import numpy as np
        scaled=np.array([[float(v/scale) if scale else 0. for v in r] for r in a])
        if asym==0:
            minimum=float(np.linalg.eigvalsh(scaled)[0])
            out['min_eigenvalue']=_float(_rational(minimum)*scale)
        t=[[a[i][j]-(q['K']/3 if i==j else 0) for j in range(3)] for i in range(3)]
        ts=max(abs(v) for r in t for v in r)
        norm=math.hypot(*(float(v/ts) if ts else 0. for r in t for v in r))
        out['T_frobenius_norm']=_float(_rational(norm)*ts)
        out['diagnostic_status']='scaled binary64 diagnostics; not acceptance criteria'
    except (ArithmeticError,ValueError,RuntimeError) as exc:
        out['diagnostic_status']='unavailable: '+repr(exc)
        out['T_frobenius_norm']=None
    if qa is not None:
        norm2=sum(v*v for v in qa)
        check('axis norm squared=1',norm2==1,norm2-1)
        pred=(3*sum(qa[i]*a[i][j]*qa[j] for i in range(3) for j in range(3))-q['K'])/2
        out['D_residual']=_float(q['D']-pred)
        check('D identity',q['D']==pred,q['D']-pred)
        check('D lower bound',q['D']>=-q['K']/2)
        check('D upper bound',q['D']<=q['K'])
    if E is not None:
        residual=q['E']-q['I']-q['Kp']-q['K']
        magnitude=abs(q['E'])+abs(q['I'])+abs(q['Kp'])
        ratio=magnitude/abs(q['K']) if q['K'] else None
        out['ledger_residual']=_float(residual)
        out['cancellation_ratio']=_float(ratio) if ratio is not None else None
        out['cancellation_ratio_exact']=str(ratio) if ratio is not None else 'undefined K=0'
        out['cancellation_source_error']='UNKNOWN' if uncertainty is None else 'SUPPLIED'
        check('energy ledger',residual==0,residual)
        check('available energy E-I',q['E']>=q['I'],q['E']-q['I'])
    out['numerical_policy']=dict(roundoff_for_admission='zero: exact rational operations on represented operands',
        machine_epsilon=sys.float_info.epsilon,physical_tolerance=None,source_uncertainty_is_not_roundoff=True)
    return done()
