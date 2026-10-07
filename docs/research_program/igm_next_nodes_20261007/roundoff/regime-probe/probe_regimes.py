#!/usr/bin/env python3
"""Diagnostic-only binary64 hydrogen BE arithmetic probe; no trajectory edits.
References use exact rational arithmetic on each supplied binary64 operand.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from pathlib import Path
from collections import defaultdict
import ctypes, ctypes.util, hashlib, itertools, json, math, platform, random, struct, sys
W = Path(__file__).resolve().parent
MIN = math.ulp(0.0)
MAX = sys.float_info.max
NORMAL = sys.float_info.min
LIBM = ctypes.util.find_library('m')
libm = ctypes.CDLL(LIBM)
fma = libm.fma
fma.argtypes = [ctypes.c_double]*3
fma.restype = ctypes.c_double
assert fma(1+2**-27, 1-2**-27, -1) == -(2**-54)

def two_sum(a,b):
    s=a+b
    bv=s-a
    return s,(a-(s-bv))+(b-bv)

def pos(x,p,r):
    return (x+p)/(1.0+p+r)

def delta(x,p,r):
    return x+(p-(p+r)*x)/(1.0+p+r)

def delta_split(x,p,r):
    return x+(p*(1-x)-r*x)/(1.0+p+r)

def delta_fma(x,p,r):
    return x+fma(-(p+r),x,p)/(1.0+p+r)

def scaled_pos(x,p,r):
    d=1.0+p+r
    if math.isfinite(d):
        return (x+p)/d
    return (0.5*x+0.5*p)/(0.5+0.5*p+0.5*r)

def compensated(x,p,r):
    # Half-scaling is used only when the unscaled positive denominator overflows.
    h=1.0
    if not math.isfinite(1.0+p+r):
        x,p,r,h=0.5*x,0.5*p,0.5*r,0.5
    nh,nl=two_sum(x,p)
    dh,dl1=two_sum(h,p)
    dh,dl2=two_sum(dh,r)
    q=nh/dh
    # FMA is essential for the high product residual; fsum combines four floats.
    residual=math.fsum([fma(-q,dh,nh),nl,-q*dl1,-q*dl2])
    y=q+residual/dh
    # Formula fallback, not projection/clipping. No such fallback seen yet.
    return y if math.isfinite(y) and 0.0<=y<=1.0 else q

def guarded(x,p,r,limit=0.5):
    s=p+r
    if s<=limit:
        y=delta(x,p,r)
        if math.isfinite(y) and 0.0<=y<=1.0:
            return y
    return scaled_pos(x,p,r)

def guarded_decrement(x,p,r):
    s=p+r
    if s<=0.5:
        d=(p-s*x)/(1.0+p+r)
        y=x+d
        if math.isfinite(y) and 0<=y<=1 and (d>=0 or -d<=0.5*x):
            return y
    return scaled_pos(x,p,r)

FUNCS={'positive_quotient':pos,'delta_sum':delta,'delta_split':delta_split,
       'delta_fma':delta_fma,'positive_overflow_scaled':scaled_pos,
       'compensated_positive':compensated,'guard_delta_half':guarded,'guard_delta_half_decrement':guarded_decrement,
       'guard_delta_2m20':lambda x,p,r:guarded(x,p,r,2**-20)}

def bits(v):
    return struct.unpack('>Q',struct.pack('>d',v))[0]
def hx(v):
    return v.hex()
def dec(q):
    with localcontext() as c:
        c.prec=45
        return str(Decimal(q.numerator)/Decimal(q.denominator))

def detail(label,x,p,r,ref,ys):
    nearest=float(ref)
    vals={}
    for name,y in ys.items():
        valid=math.isfinite(y) and 0<=y<=1
        vals[name]={'value':repr(y),'hex':hx(y),'ulp_distance_to_nearest':abs(bits(y)-bits(nearest)) if valid else None,
                    'exact_signed_error':dec(F(y)-ref) if math.isfinite(y) else None}
    return {'label':label,'x0':x,'P':p,'R':r,'hex':[hx(x),hx(p),hx(r)],
            'exact_reference_fraction':str(ref),'exact_reference_decimal_45':dec(ref),
            'nearest':nearest,'nearest_hex':hx(nearest),'methods':vals}

SPECIAL=[
('stiff_root_erasure',(1.0,0.0,1e20)),
('stiff_root_erasure_source',(0.5,1.0,1e20)),
('denominator_overflow',(1.0,1e308,1e308)),
('maximum_coefficients',(0.5,MAX,MAX)),
('legitimate_underflow',(MIN,0.0,1.0)),
('half_min_subnormal_broken_tie',(MIN,MIN,3.0)),
('subnormal_rounds_up',(0.0,MIN,0.5)),
('fixed_zero',(0.0,0.0,MAX)),
('fixed_one',(1.0,MAX,0.0)),
]

def cases():
    for label,trip in SPECIAL:
        yield 'named',label,trip
    coeff={0.0,MIN,2*MIN,math.nextafter(NORMAL,0),NORMAL,MAX,1e308,
           math.nextafter(.5,0),.5,math.nextafter(.5,1),
           math.nextafter(1,0),1.,math.nextafter(1,2),2.,1e-20,1e20}
    for e in [-1070,-1050,-1022,-1000,-600,-100,-54,-53,-52,-30,-20,-10,-2,-1,0,1,20,53,54,100,500,970,1000,1023]:
        a=math.ldexp(1.,e)
        coeff.add(a)
        if e in [-53,-52,53,54,1023]:
            coeff.add(math.nextafter(a,0));coeff.add(math.nextafter(a,math.inf))
    xs=[0.,MIN,2*MIN,math.nextafter(NORMAL,0),NORMAL,2**-1000,2**-600,2**-100,
        2**-54,2**-53,1e-8,0.0002,.25,math.nextafter(.5,0),.5,math.nextafter(.5,1),
        1-2**-40,1-2**-52,math.nextafter(1,0),1.]
    for i,(x,p,r) in enumerate(itertools.product(xs,sorted(coeff),sorted(coeff))):
        yield 'boundary_grid',f'grid_{i}',(x,p,r)
    rng=random.Random(0xBE20261007)
    def exponent_float(lo=-1074,hi=1023):
        e=rng.randint(lo,hi)
        return math.ldexp(rng.uniform(1,2),e)
    def random_x():
        k=rng.randrange(5)
        if k==0:return exponent_float(-1074,-1)
        if k==1:return 1-exponent_float(-1074,-1)
        if k==2:return rng.choice(xs)
        return rng.random()
    for i in range(30000):
        yield 'exponent_random',f'exp_{i}',(random_x(),exponent_float(),exponent_float())
    for i in range(30000):
        yield 'weak_random',f'weak_{i}',(random_x(),exponent_float(-1074,-3),exponent_float(-1074,-3))
    for i in range(15000):
        x=random_x();p=exponent_float(-1074,10);r=exponent_float(54,1023)
        yield 'stiff_random',f'stiff_{i}',(x,p,r)
    # Exact coefficients recorded immediately before the original hydrogen update.
    records=json.loads((W.parent/'diagnostic-records.json').read_text())
    trial=None
    for rec in records:
        if rec['kind']=='trial':trial=rec['number']
        elif rec['kind']=='inner_energy':
            d={k:struct.unpack('>d',bytes.fromhex(v))[0] for k,v in rec['bits'].items()}
            yield 'captured',f'captured_{trial}',(d['old_x'],d['a0'],d['r0'])

def newstats():
    return {'count':0,'nearest':0,'not_nearest':0,'nonfinite':0,'outside_unit_interval':0,
            'false_zero':0,'worst_ulp_distance':0,'worst_example':None,'first_non_nearest':None,
            'first_false_zero':None,'first_outside':None}

def main():
    stats=defaultdict(lambda:defaultdict(newstats));saved={};n=0
    comparisons=defaultdict(lambda:{'better_than_positive':0,'same_error':0,'worse_than_positive':0})
    capture=[]
    max_guard_negative_ratio=0.0
    for group,label,(x,p,r) in cases():
        assert math.isfinite(x+p) and 0<=x<=1 and 0<=p<=MAX and 0<=r<=MAX
        ref=(F(x)+F(p))/(1+F(p)+F(r));near=float(ref)
        ys={k:f(x,p,r) for k,f in FUNCS.items()}
        n+=1
        keep=group in ('named','captured')
        if group=='captured':capture.append(label)
        if p+r<=.5 and x>0:
            d=(p-(p+r)*x)/(1+p+r)
            max_guard_negative_ratio=max(max_guard_negative_ratio,-d/x)
        for name,y in ys.items():
            s=stats[group][name];s['count']+=1
            finite=math.isfinite(y);valid=finite and 0<=y<=1
            nearest=y==near
            if nearest:s['nearest']+=1
            else:
                s['not_nearest']+=1
                if s['first_non_nearest'] is None:s['first_non_nearest']=label;keep=True
            if not finite:s['nonfinite']+=1
            elif not 0<=y<=1:
                s['outside_unit_interval']+=1
                if s['first_outside'] is None:s['first_outside']=label;keep=True
            if y==0 and near>0:
                s['false_zero']+=1
                if s['first_false_zero'] is None:s['first_false_zero']=label;keep=True
            if valid:
                ulps=abs(bits(y)-bits(near))
                if ulps>s['worst_ulp_distance']:
                    s['worst_ulp_distance']=ulps;s['worst_example']=label;keep=True
            if math.isfinite(ys['positive_quotient']) and finite:
                eq=abs(F(ys['positive_quotient'])-ref);ey=abs(F(y)-ref)
                key='better_than_positive' if ey<eq else 'worse_than_positive' if ey>eq else 'same_error'
                comparisons[name][key]+=1
        if keep:saved[label]=detail(label,x,p,r,ref,ys)
    # Save only referenced examples plus the complete named and captured sets.
    needed={k for k in saved if k.startswith('captured_') or k in {a for a,_ in SPECIAL}}
    for group,ss in stats.items():
        for s in ss.values():
            needed.update(s[k] for k in ['worst_example','first_non_nearest','first_false_zero','first_outside'] if s[k])
    saved={k:saved[k] for k in sorted(needed)}
    source=W.parent/'baseline_igm_step.rs'
    out={'scope':'diagnostic-only; exact rational references on finite binary64 P,R,x0; no trajectory, clipping, tolerance, source or gate edits',
         'seed':'0xBE20261007','cases':n,
         'environment':{'python':sys.version,'platform':platform.platform(),'libm':LIBM,'subnormal_nonzero':MIN>0},
         'stats':stats,'compared_exact_absolute_error':comparisons,
         'maximum_observed_negative_delta_over_x_weak_half':max_guard_negative_ratio,
         'captured_labels':capture,'examples':saved,
         'inputs_sha256':{str(p.relative_to(W.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [W.parent/'diagnostic-records.json',W.parent/'exact-local-analysis.json',source]},
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (W/'results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('TOTAL',n)
    for group,ss in stats.items():
        print(group)
        for name,s in ss.items():
            print(name, 'nearest',s['nearest'],'/',s['count'],'nonfinite',s['nonfinite'],'outside',s['outside_unit_interval'],
                  'falsezero',s['false_zero'],'worstulps',s['worst_ulp_distance'],'example',s['worst_example'])
    print('max weak negative correction/x',max_guard_negative_ratio)
    print('exact error comparisons',dict(comparisons))
if __name__=='__main__':main()
