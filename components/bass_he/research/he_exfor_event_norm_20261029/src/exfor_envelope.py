"""Conditional 330 MeV EXFOR angular integral, no physical rate admission.
Exact source and interval geometry; numerical elementary antiderivative.
"""
from fractions import Fraction as F
from dataclasses import dataclass
from hashlib import sha256, sha1
from pathlib import Path

SOURCE_SHA256='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
SOURCE_GIT_BLOB='c49433293921dbb012d7f1b0387745732a598efa'
SOURCE_COMMIT='939a14d7bba1ddce51975cb5e8711ce96b3b0871'
SOURCE_PATH='exforall/M04/M0475.x4'
NB_TO_M2=F(1,10**37)

def q(x):
    if isinstance(x,(float,bool)):raise ValueError('float/bool not exact')
    if type(x) not in (F,int,str):raise TypeError('exact Fraction/int/string required')
    return F(x)

@dataclass(frozen=True)
class DA:
    energy:F
    theta:F
    value:F
    stat:F
    @property
    def lo(self):return max(F(0),self.value-self.stat)
    @property
    def hi(self):return self.value+self.stat

@dataclass(frozen=True)
class SIG:
    energy:F
    value:F
    stat:F

def load_source(path):
    raw=Path(path).read_bytes()
    if sha256(raw).hexdigest()!=SOURCE_SHA256:raise ValueError('source sha256')
    if sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SOURCE_GIT_BLOB:
        raise ValueError('source git blob')
    s=raw.decode('ascii')
    if 'METHOD     (COINC,TOF)' not in s or 'ERR-ANALYS (ERR-S) Statistical errors.' not in s:
        raise ValueError('source provenance')
    def table(tag,header,unit,n):
        x=s.split('SUBENT        '+tag,1)[1].split('ENDSUBENT',1)[0]
        if header not in x or unit not in x:raise ValueError('source columns')
        data=x.split('DATA                 ',1)[1].split('\n',1)[1].split('ENDDATA',1)[0]
        rows=[]
        for line in data.splitlines()[2:]:
            v=line.split()
            if v:
                if len(v)!=n:raise ValueError('source row')
                rows.append(tuple(q(t) for t in v))
        return rows
    a=table('M0475002','EN         ANG-CM     DATA-CM    ERR-S',
            'MEV        ADEG       NB/SR      NB/SR',4)
    b=table('M0475003','EN         DATA       ERR-S','MEV        NB         NB',3)
    if len(a)!=12 or len(b)!=6:raise ValueError('source row count')
    return tuple(DA(*r) for r in a),tuple(SIG(*r) for r in b)

def rows330(da):
    p=tuple(sorted((x for x in da if x.energy==330),key=lambda x:x.theta))
    if len(p)!=4 or len({x.theta for x in p})!=4 or any(not 0<x.theta<90 for x in p):
        raise ValueError('source 330 rows')
    return p

def min_L(points,stat_box=True):
    lo=[p.lo if stat_box else p.value for p in points]
    hi=[p.hi if stat_box else p.value for p in points]
    return max([F(0)]+[max(F(0),lo[i]-hi[j])/abs(points[i].theta-points[j].theta)
        for i in range(len(points)) for j in range(len(points)) if i!=j])

def envelope(points,L,theta,kind):
    L=q(L);theta=q(theta)
    if L<0 or not 0<=theta<=90:raise ValueError('domain')
    if kind=='lower':return max([F(0)]+[p.lo-L*abs(theta-p.theta) for p in points])
    if kind=='upper':return min(p.hi+L*abs(theta-p.theta) for p in points)
    raise ValueError('kind')

def segments(points,L,kind):
    L=q(L)
    if L<min_L(points):raise ValueError('L below feasible threshold')
    knots=sorted({F(0),F(90)}|{p.theta for p in points})
    out=[]
    for a,b in zip(knots[:-1],knots[1:]):
        mid=(a+b)/2
        lines=[(F(0),F(0))] if kind=='lower' else []
        for p in points:
            sign=1 if mid>=p.theta else -1
            if kind=='lower':lines.append((p.lo+L*sign*p.theta,-L*sign))
            elif kind=='upper':lines.append((p.hi-L*sign*p.theta,L*sign))
            else:raise ValueError('kind')
        cuts={a,b}
        for i,(ai,bi) in enumerate(lines):
            for aj,bj in lines[i+1:]:
                if bi!=bj:
                    x=(aj-ai)/(bi-bj)
                    if a<x<b:cuts.add(x)
        cuts=sorted(cuts)
        for x,y in zip(cuts[:-1],cuts[1:]):
            mid=(x+y)/2
            aa,bb=(max if kind=='lower' else min)(lines,key=lambda z:z[0]+z[1]*mid)
            if out and out[-1][1]==x and out[-1][2:]==(aa,bb):
                out[-1]=(out[-1][0],y,aa,bb)
            else:out.append((x,y,aa,bb))
    return tuple(out)

def angular_integral(points,L,kind,dps=70):
    """Sharp full-sphere I=4*pi*(pi/180)*int_0^90 f(theta)sin(pi theta/180)dtheta [nb].
    Exact piecewise-affine envelope; high-precision transcendental evaluation.
    The output decimal is not an interval-rounding certificate.
    """
    import mpmath as mp
    if type(dps)!=int or not 30<=dps<=200:raise ValueError('precision')
    pieces=segments(points,L,kind)
    with mp.workdps(dps):
        k=mp.pi/180
        def to_mp(x):return mp.mpf(x.numerator)/x.denominator
        def antideriv(x,a,b):
            xx=to_mp(x); aa=to_mp(a); bb=to_mp(b)
            return -(aa+bb*xx)*mp.cos(k*xx)/k+bb*mp.sin(k*xx)/(k*k)
        value=mp.fsum(4*mp.pi*k*(antideriv(y,a,b)-antideriv(x,a,b))
                      for x,y,a,b in pieces)
        return mp.nstr(value,dps-12)

def sharp_bounds(points,L,dps=70):
    lo=angular_integral(points,L,'lower',dps)
    hi=angular_integral(points,L,'upper',dps)
    import mpmath as mp
    if mp.mpf(lo)>mp.mpf(hi):raise ArithmeticError('infeasible bounds')
    return {'L_nb_sr_per_deg':str(q(L)),'full_sphere_I_lower_nb':lo,
            'full_sphere_I_upper_nb':hi,'event_sigma_nb':None,
            'physical_rate_m3s':None,'physical_activation':False,
            'uncertainty_type':'coordinatewise_ERR-S_sensitivity_not_joint_CI',
            'exact_piecewise_geometry':True,'numeric_rounding_certified':False}

def conditional_sigma(points,L,convention,dps=70):
    """Hypothetical full-sphere convention, not EXFOR admission.
    inclusive_D: I=2*sigma_event; randomly_oriented_one_D: I=sigma_event.
    """
    kappa={'inclusive_D':2,'randomly_oriented_one_D':1}.get(convention)
    if kappa is None:raise ValueError('explicit convention required')
    import mpmath as mp
    r=sharp_bounds(points,L,dps)
    with mp.workdps(dps):
        r.update(convention=convention,kappa=kappa,
                 conditional_sigma_lower_nb=mp.nstr(mp.mpf(r['full_sphere_I_lower_nb'])/kappa,dps-12),
                 conditional_sigma_upper_nb=mp.nstr(mp.mpf(r['full_sphere_I_upper_nb'])/kappa,dps-12))
    return r

def manufactured_rate(sigma_bounds,n_he=None,photon_flux=None,source_class=None):
    """R=n_He Phi sigma for a manufactured monoenergetic flux, never physical."""
    if source_class!='MANUFACTURED_TEST_ONLY':raise ValueError('source class')
    if n_he is None or photon_flux is None:
        return {'R_lower_m3s':None,'R_upper_m3s':None,'physical_activation':False}
    n=q(n_he);phi=q(photon_flux)
    if n<0 or phi<0:raise ValueError('negative density/flux')
    import mpmath as mp
    with mp.workdps(70):
        scale=mp.mpf(n.numerator)/n.denominator*mp.mpf(phi.numerator)/phi.denominator*mp.mpf('1e-37')
        return {'R_lower_m3s':mp.nstr(scale*mp.mpf(sigma_bounds['conditional_sigma_lower_nb']),55),
                'R_upper_m3s':mp.nstr(scale*mp.mpf(sigma_bounds['conditional_sigma_upper_nb']),55),
                'physical_activation':False}
