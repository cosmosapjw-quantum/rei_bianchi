"""Pinned represented-real native RR times Mao loss, not a callback FP bound."""
from collections import OrderedDict
from decimal import Decimal as D, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
import hashlib,json
from pathlib import Path
from deps.dr_interval_original import Arithmetic,Interval,number

SOURCE_HASHES={'atomic_coefficients.json':'38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc',
              'mao2017_selected.json':'34b5fb8dab049744faa0c6f734ce59f1c72b931b3cf2db298c01156f86d17803'}
KEYS=('1:1','2:1','2:2','3:1','3:2','3:3')


def decode(x):
    if type(x) is str:
        x=D(x)
    return number(x)


def load_sources(directory,expected=None):
    data={}
    for name,digest in (SOURCE_HASHES if expected is None else expected).items():
        raw=(Path(directory)/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('source SHA256 mismatch: '+name)
        data[name]=json.loads(raw)
    if set(data)!=set(SOURCE_HASHES):raise ValueError('two complete source identities required')
    return data


def square(x):
    """Exact square image via directed scalar products, including zero crossing."""
    a=x.a
    lower=D(0) if x.lo<=0<=x.hi else min(a.op('multiply',v,v,ROUND_FLOOR) for v in (x.lo,x.hi))
    upper=max(a.op('multiply',v,v,ROUND_CEILING) for v in (x.lo,x.hi))
    return Interval(a,lower,upper)


class RRMao:
    def __init__(self,data,precision=60):
        self.data=data;self.a=Arithmetic(precision)
        self.s,self.k,self.ev=map(number,(1e-6,1.380649e-23,1.602176634e-19))
        self.cache=OrderedDict()

    def i(self,x):return self.a.interval(decode(x))

    def domain(self,lo,hi=None):
        t=self.a.interval(decode(lo),decode(lo if hi is None else hi))
        if t.lo<100 or t.hi>1000000:raise ValueError('outside 100..1000000 K')
        return t

    def parameters(self,key):
        if type(key) is not str or key not in KEYS:raise ValueError('unknown RR/Mao key')
        rr=self.data['atomic_coefficients.json']['rr'][key]
        pars=tuple(number(float(rr[n])) for n in ('A_cm3_s','B','T0_K','T1_K','C','T2_K'))
        z,q=map(int,key.split(':'))
        candidates=[r for r in self.data['mao2017_selected.json']['rows'] if r['initial_Z']==z and r['initial_q']==q]
        if len(candidates)!=1:raise ValueError('missing/duplicate Mao source row')
        row=candidates[0]
        if row['recombined_s']!=z-q+1:raise ValueError('Mao recombined electron mapping mismatch')
        mao=tuple(number(float(v)) for v in row['a0_b0_c0_a1_b1_a2_b2'])
        if len(mao)!=7 or mao[0]<=0 or mao[3]<0 or mao[5]<0:raise ValueError('invalid Mao positivity data')
        self.monotonic_certificate(pars,key)
        return pars,mao

    @staticmethod
    def monotonic_certificate(pars,key):
        A,B,T0,T1,C,T2=map(Q,pars)
        if not (A>0 and T1>T0>0 and T2>=0 and C>=0 and 0<B and B+C<1):
            raise ValueError('actual RR coefficient conditions violated')
        if C==0:return {'strict_decrease':True,'basis':'C=0; positive RR2 bracket'}
        bound,power=(Q(151,1000),16) if key=='3:1' else (Q(36,1000),18) if key=='3:2' else (None,None)
        if bound is None or not (C<bound and T1/T0<2**power and bound*power*Q(7,10)<Q(27,10)):
            raise ValueError('exact sufficient monotonicity certificate unavailable')
        return {'strict_decrease':True,'basis':'C ln(T1/T0)<rational bound<2.7<e',
                'bound_num':str((bound*power*Q(7,10)).numerator),'bound_den':str((bound*power*Q(7,10)).denominator)}

    def images(self,key):
        rr,mao=self.parameters(key)
        def image(v):
            f=float(v);n,d=f.as_integer_ratio()
            return {'hex':f.hex(),'num':str(n),'den':str(d),'decimal':str(v)}
        return {'rr':[image(v) for v in rr],'mao':[image(v) for v in mao],
                's':image(self.s),'k':image(self.k),'eV_J':image(self.ev),
                'Mao_mapping':'n_recombined=Z-q+1','source_embedded_comparisons':'EXPOSED_PRIOR_EVALUATIONS_NOT_NEW_RUNS'}

    def signature(self):
        c=self.a.context
        return (c.prec,c.Emin,c.Emax,c.clamp,c.rounding,tuple(sorted((str(s),v) for s,v in c.traps.items())))

    def alpha_point(self,pars,t):
        A,B,T0,T1,C,T2=map(self.i,pars)
        u=(t/T0).transcend('sqrt');v=(t/T1).transcend('sqrt')
        b=B+C*(-T2/t).transcend('exp')
        exponent=-(u.transcend('ln'))-(1-b)*(1+u).transcend('ln')-(1+b)*(1+v).transcend('ln')
        return self.i(self.s)*A*exponent.transcend('exp')

    def box(self,key,lo,hi):
        t=self.domain(lo,hi);rr,mao=self.parameters(key)
        cachekey=(rr,mao,self.s,self.k,self.ev,t.lo,t.hi,self.signature())
        stored=self.cache.get(cachekey)
        if stored is not None:
            self.cache.move_to_end(cachekey)
            return {name:Interval(self.a,*ends) for name,ends in stored.items()}
        A,B,T0,T1,C,T2=map(self.i,rr)
        u=(t/T0).transcend('sqrt');v=(t/T1).transcend('sqrt');z=T2/t
        correction=C*(-z).transcend('exp');b=B+correction
        bp=correction*z;bpp=bp*(z-1)
        p=u/(1+u);q=v/(1+v)
        lam=(1+u).transcend('ln')-(1+v).transcend('ln')
        r1=self.i(D('-.5'))-((1-b)*p+(1+b)*q)/2+bp*lam
        r2=-((1-b)*p*(1-p)+(1+b)*q*(1-q))/4+bp*(p-q)+bpp*lam
        left=self.alpha_point(rr,self.i(t.lo));right=self.alpha_point(rr,self.i(t.hi))
        alpha=Interval(self.a,right.lo,left.hi)
        a0,b0,c0,a1,b1,a2,b2=map(self.i,mao)
        ell=(self.i(self.k)*t/self.ev).transcend('ln')
        U=a1*(-b1*ell).transcend('exp');V=a2*(-b2*ell).transcend('exp')
        P=U/(1+U);Qv=V/(1+V)
        factor=a0*(-b0*ell-c0*square(ell)).transcend('exp')*(1+V)/(1+U)
        m1=-b0-2*c0*ell-b2*Qv+b1*P
        m2=-2*c0+square(b2)*Qv*(1-Qv)-square(b1)*P*(1-P)
        loss=self.i(self.k)*t*alpha*factor;w=1+r1+m1
        result={'alpha':alpha,'factor':factor,'loss':loss,'r1':r1,'r2':r2,'m1':m1,'m2':m2,
                'd_alpha':alpha*r1,'dd_alpha':alpha*(square(r1)+r2),
                'd_loss':loss*w,'dd_loss':loss*(square(w)+r2+m2)}
        if any(result[n].lo<=0 for n in ('alpha','factor','loss')):
            raise ArithmeticError('positive finite box not preserved')
        self.cache[cachekey]={name:(value.lo,value.hi) for name,value in result.items()}
        if len(self.cache)>128:self.cache.popitem(last=False)
        return {name:Interval(self.a,value.lo,value.hi) for name,value in result.items()}

    def range(self,key,lo,hi,quantity='alpha'):
        if quantity not in ('alpha','loss'):raise ValueError('quantity must be alpha or loss')
        return self.box(key,lo,hi)[quantity]

    def point(self,key,t,quantity='alpha'):return self.range(key,t,t,quantity)

    def first_derivative(self,key,t,quantity='alpha'):
        if quantity not in ('alpha','loss'):raise ValueError('quantity must be alpha or loss')
        return self.box(key,t,t)['d_'+quantity]

    def uniform_second_bound(self,key,lo,hi,quantity='alpha'):
        if quantity not in ('alpha','loss'):raise ValueError('quantity must be alpha or loss')
        return self.box(key,lo,hi)['dd_'+quantity].magnitude()

    def taylor(self,key,Tstar,target,domain,quantity='alpha'):
        if type(domain) not in (list,tuple) or len(domain)!=2:raise ValueError('two domain endpoints required')
        interval=self.domain(*domain);center=self.domain(Tstar);point=self.domain(target)
        if not (interval.lo<=center.lo<=interval.hi and interval.lo<=point.lo<=interval.hi):
            raise ValueError('Taylor endpoints outside declared domain')
        f0=self.point(key,Tstar,quantity);d0=self.first_derivative(key,Tstar,quantity)
        if point.lo==center.lo:
            return {'h':self.i(0),'radius':D(0),'f0':f0,'d0':d0,'B2':self.uniform_second_bound(key,*domain,quantity),'enclosure':f0}
        h=(point/center).transcend('ln');B2=self.uniform_second_bound(key,*domain,quantity)
        radius=(self.i(B2)*h.magnitude()*h.magnitude()/2).hi
        return {'h':h,'radius':radius,'B2':B2,'f0':f0,'d0':d0,
                'enclosure':f0+d0*h+Interval(self.a,radius.copy_negate(),radius)}
