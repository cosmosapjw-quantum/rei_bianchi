"""Selected source-bound controls; no native NumPy callback import."""
from decimal import Decimal as D,localcontext,Context
from fractions import Fraction as Q
from pathlib import Path
import unittest
from rr_mao_enclosure import RRMao,load_sources,decode,KEYS

ROOT=Path(__file__).resolve().parents[1]


def scalar_oracle(data,key,temperature):
    """Separate scalar90-digit implementation; shares Decimal/libmpdec, disclosed."""
    with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
        row=data['atomic_coefficients.json']['rr'][key]
        A,B,t0,t1,C,t2=[D.from_float(float(row[n])) for n in ('A_cm3_s','B','T0_K','T1_K','C','T2_K')]
        T=D(temperature);u=(T/t0).sqrt();v=(T/t1).sqrt();z=t2/T
        b=B+C*(-z).exp();bp=C*z*(-z).exp();bpp=bp*(z-1)
        p=u/(1+u);q=v/(1+v);lam=(1+u).ln()-(1+v).ln()
        alpha=D.from_float(1e-6)*A/(u*((1-b)*(1+u).ln()).exp()*((1+b)*(1+v).ln()).exp())
        r1=-D('.5')-((1-b)*p+(1+b)*q)/2+bp*lam
        r2=-((1-b)*p*(1-p)+(1+b)*q*(1-q))/4+bp*(p-q)+bpp*lam
        Z,charge=map(int,key.split(':'))
        mao=next(r for r in data['mao2017_selected.json']['rows'] if (r['initial_Z'],r['initial_q'])==(Z,charge))
        a0,b0,c0,a1,b1,a2,b2=[D.from_float(float(x)) for x in mao['a0_b0_c0_a1_b1_a2_b2']]
        k=D.from_float(1.380649e-23);ev=D.from_float(1.602176634e-19)
        ell=(k*T/ev).ln();U=a1*(-b1*ell).exp();V=a2*(-b2*ell).exp()
        P=U/(1+U);qv=V/(1+V)
        f=a0*(-b0*ell-c0*ell*ell).exp()*(1+V)/(1+U)
        m1=-b0-2*c0*ell-b2*qv+b1*P
        m2=-2*c0+b2*b2*qv*(1-qv)-b1*b1*P*(1-P)
        loss=k*T*alpha*f;w=1+r1+m1
        return {'alpha':alpha,'loss':loss,'factor':f,'r1':r1,'r2':r2,'m1':m1,'m2':m2,
                'd_alpha':alpha*r1,'dd_alpha':alpha*(r1*r1+r2),
                'd_loss':loss*w,'dd_loss':loss*(w*w+r2+m2),
                'alternate_loss':k*T*alpha*(D('1.5')+r1),
                'correction_derivative_term':bp*lam,'c0':c0,'a2':a2,
                'ell':ell,'incorrect_log10_factor':a0*(-b0*(ell/D(10).ln())-c0*(ell/D(10).ln())**2).exp()*(1+V)/(1+U)}


class SelectedRRControls(unittest.TestCase):
    results={}

    def test_selected_actual_rows(self):
        data=load_sources(ROOT/'source');model=RRMao(data)
        records={'ranges':[],'point_derivatives':[],'taylor':[],'source_images':{},
                 'correction_controls':[],'precision':[],'refusals':[],'tiny_steps':[],
                 'source_embedded_prior_comparisons':'READ_EXPOSURE_NOT_NEW_EVALUATION',
                 'oracle_library':'separate scalar code, shared Decimal/libmpdec90digits'}
        for key in KEYS:
            rr,mao=model.parameters(key);records['source_images'][key]=model.images(key)
            cert=model.monotonic_certificate(rr,key)
            for lo,hi in [(100,101),(14000,16000),(900000,1000000),(100,1000000)]:
                box=model.box(key,lo,hi)
                for T in (lo,(lo+hi)//2,hi):
                    direct=scalar_oracle(data,key,D(T))
                    for name in ('alpha','factor','loss','r1','r2','m1','m2','d_alpha','dd_alpha','d_loss','dd_loss'):
                        self.assertLessEqual(box[name].lo,direct[name]);self.assertLessEqual(direct[name],box[name].hi)
                    records['ranges'].append({'key':key,'domain_K':[lo,hi],'sample_T_K':T,
                        'boxes':{n:v.wire() for n,v in box.items()},
                        'direct':{n:str(v) for n,v in direct.items()},'monotonicity':cert})
            T=D(15000);direct=scalar_oracle(data,key,T);point=model.box(key,T,T)
            for name in ('alpha','factor','loss','r1','r2','m1','m2','d_alpha','dd_alpha','d_loss','dd_loss'):
                self.assertLessEqual(point[name].lo,direct[name]);self.assertLessEqual(direct[name],point[name].hi)
            self.assertLess(direct['r1'],0)
            records['point_derivatives'].append({'key':key,'T_K':str(T),'direct':{n:str(v) for n,v in direct.items()},
                                                'bounds':{n:v.wire() for n,v in point.items()}})
            # Explicitly distinguish selected Mao hybrid from derivative-moment closure.
            self.assertNotEqual(direct['loss'],direct['alternate_loss'])
            self.assertNotEqual(direct['factor'],direct['incorrect_log10_factor'])
            if key in ('3:1','3:2'):
                c=scalar_oracle(data,key,rr[5]);self.assertGreater(c['correction_derivative_term'],0)
                records['correction_controls'].append({'key':key,'T_K':str(rr[5]),'omitted_if_b_frozen':str(c['correction_derivative_term'])})
            for quantity in ('alpha','loss'):
                f0=direct[quantity];d0=direct['d_'+quantity]
                for numerator,den in ((-1,128),(1,128),(-1,256),(1,256),(0,1)):
                    with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
                        requested_h=D(numerator)/den;target=T*requested_h.exp()
                        h=(target/T).ln();val=scalar_oracle(data,key,target)[quantity]
                        residual=val-f0-d0*h
                    result=model.taylor(key,T,target,(14000,16000),quantity)
                    self.assertLessEqual(result['enclosure'].lo,val);self.assertLessEqual(val,result['enclosure'].hi)
                    if numerator:
                        self.assertLessEqual(residual.copy_abs(),result['radius'])
                    else:
                        self.assertEqual((result['h'].lo,result['h'].hi,result['radius']),(0,0,0))
                        self.assertEqual(result['enclosure'].wire(),result['f0'].wire())
                    records['taylor'].append({'key':key,'quantity':quantity,'Tstar_K':str(T),'target_K':str(target),
                        'requested_h':str(requested_h),'direct':str(val),'residual':str(residual),
                        'h':result['h'].wire(),'f0':result['f0'].wire(),'d0':result['d0'].wire(),
                        'B2':str(result['B2']),'radius':str(result['radius']),'enclosure':result['enclosure'].wire(),'contained':True})
        # Exact decimal tiny steps in both feasible directions inside [100,101].
        tiny_steps=(('100','100.'+'0'*99+'1'),('101','100.'+'9'*100))
        for anchor,target in tiny_steps:
            for quantity in ('alpha','loss'):
                result=model.taylor('1:1',anchor,target,('100','101'),quantity)
                if anchor=='100':self.assertGreaterEqual(result['h'].lo,0)
                else:self.assertLessEqual(result['h'].hi,0)
                self.assertGreaterEqual(result['radius'],0)
                with localcontext(Context(prec=180,Emin=-999999,Emax=999999)):
                    h=(D(target)/D(anchor)).ln()
                self.assertLessEqual(result['h'].lo,h);self.assertLessEqual(h,result['h'].hi)
                records['tiny_steps'].append({'key':'1:1','quantity':quantity,'anchor':anchor,'target':target,
                    'oracle_log_digits':180,'oracle_h':str(h),'h':result['h'].wire(),'radius':str(result['radius']),
                    'enclosure':result['enclosure'].wire(),'runtime_status':'observed only when authorized suite runs'})
        for precision in (50,70):
            m=RRMao(data,precision);direct=scalar_oracle(data,'3:1',D(15000))
            for quantity in ('alpha','loss'):
                v=m.range('3:1',14000,16000,quantity)
                self.assertLessEqual(v.lo,direct[quantity]);self.assertLessEqual(direct[quantity],v.hi)
                records['precision'].append({'digits':precision,'key':'3:1','quantity':quantity,'box':v.wire()})
        bad=[('unknown',lambda:model.range('9:9',100,101)),
             ('hash',lambda:load_sources(ROOT/'source',{n:'0'*64 for n in data})),
             ('quantity',lambda:model.range('1:1',100,101,'RR_derivative_loss'))]
        for name,x,y in [('bool',True,101),('complex',100+0j,101),('nan','NaN',101),('inf',float('inf'),101),
                         ('low',99,101),('high',100,1000001),('reverse',101,100)]:
            bad.append((name,lambda x=x,y=y:model.range('1:1',x,y)))
        for name,fn in bad:
            with self.assertRaises((ValueError,TypeError)):fn()
            records['refusals'].append({'case':name,'refused':True})
        records['decimal_string_semantics']={'input':'15000','exact_decimal':str(decode('15000'))}
        self.results.update(records)
