"""One selected source-bound suite; separate 90-digit scalar formula oracle."""
import math
from decimal import Decimal as D, localcontext, Context
from fractions import Fraction
from pathlib import Path
import unittest
from code_dr import DRModel, load_source, number, parameter_images

ROOT=Path(__file__).resolve().parents[1]


def oracle(row, temperature, loss=False, clipped=False):
    # Independently written scalar formula; never calls interval kernel/range.
    with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
        t=D(temperature); total=D(0)
        for raw_c,raw_e in zip(row['c_cm3_s_K32'],row['E_K']):
            c=D.from_float(float(raw_c)); e=D.from_float(float(raw_e))
            if clipped and c<0:
                continue
            term=c*(e if loss else 1)*(-e/t).exp()/(t*t.sqrt())
            total+=term
        return D.from_float(1e-6)*total*(D.from_float(1.380649e-23) if loss else 1)


def oracle_derivative(row,temperature,loss=False):
    with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
        t=D(temperature); total=D(0)
        for c,e in zip(row['c_cm3_s_K32'],row['E_K']):
            c=D.from_float(float(c));e=D.from_float(float(e));x=e/t
            total+=c*(e if loss else 1)*(x-D('1.5'))*(-x).exp()/(t*t.sqrt())
        return D.from_float(1e-6)*total*(D.from_float(1.380649e-23) if loss else 1)


class SelectedControls(unittest.TestCase):
    output={}

    def test_selected_source_and_analytic_controls(self):
        path=ROOT/'source/atomic_coefficients.json';data=load_source(path);m=DRModel(data)
        records={'parameter_images':parameter_images(data),'finite_ranges':[],
                 'signed_vs_clipped':[],'underflow_vs_absence':[],'taylor':[],
                 'precision_comparison':[],'rejections':[]}
        for key,row in data['dr'].items():
            for loss in (False,True):
                cert=m.positivity(key,loss)
                self.assertTrue(cert['strict_positive'])
                if 'margin' in cert:
                    self.assertGreater(Fraction(int(cert['margin']['num']),int(cert['margin']['den'])),0)
                for lo,hi in ((100,101),(14000,16000),(300000,400000),(900000,1000000),(100,1000000)):
                    bounds=m.range(key,lo,hi,loss)
                    # Single independent interior sample; proof, not sampling, certifies full range.
                    mid=D((lo+hi)//2);value=oracle(row,mid,loss)
                    self.assertLessEqual(bounds.lo,value);self.assertLessEqual(value,bounds.hi)
                    self.assertGreater(bounds.lo,0)
                    records['finite_ranges'].append({'key':key,'quantity':'L' if loss else 'alpha',
                        'interval_K':[lo,hi],'bounds':bounds.wire(),'oracle_T_K':str(mid),
                        'oracle_value':str(value),'positivity':cert})
                direct=oracle(row,D(100),loss)
                binary=1e-6*sum(float(c)*(float(e) if loss else 1)*100.0**(-1.5)*math.exp(-float(e)/100)
                               for c,e in zip(row['c_cm3_s_K32'],row['E_K']))*(1.380649e-23 if loss else 1)
                self.assertGreater(direct,0)
                records['underflow_vs_absence'].append({'key':key,'quantity':'L' if loss else 'alpha',
                    'T_K':100,'mathematical_oracle':str(direct),'binary64_scalar':repr(binary),
                    'binary64_zero_observed':binary==0,'structural_absence':False})
                if key in ('2:1','3:1'):
                    signed=oracle(row,D(1000000),loss);clipped=oracle(row,D(1000000),loss,True)
                    with localcontext(Context(prec=90)):
                        bias=clipped-signed
                    self.assertGreater(bias,0)
                    records['signed_vs_clipped'].append({'key':key,'quantity':'L' if loss else 'alpha',
                        'T_K':1000000,'signed':str(signed),'clipped':str(clipped),'positive_bias':str(bias)})
        # Interior peak independently evaluated at high precision, beyond endpoints.
        with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
            e=D(463300);peak=2*e/3
            def scalar_kernel(t):return (-e/t).exp()/(t*t.sqrt())
            actual_peak=scalar_kernel(peak)
            endpoint_max=max(scalar_kernel(D(300000)),scalar_kernel(D(400000)))
        k=m.term_range(D(463300),m.domain(300000,400000))
        self.assertGreater(actual_peak,endpoint_max);self.assertGreaterEqual(k.hi,actual_peak)
        records['interior_peak']={'T_K':str(peak),'peak':str(actual_peak),
                                  'endpoint_only_max':str(endpoint_max),'enclosure':k.wire()}
        t0=number(14919.863839279506)
        # Both actual signed rows and positive row, alpha and loss, all six log steps.
        for key,row in data['dr'].items():
            for loss in (False,True):
                f0=oracle(row,t0,loss);d0=oracle_derivative(row,t0,loss)
                for den in (128,256,512):
                    for sign in (-1,1):
                        with localcontext(Context(prec=90,Emin=-999999,Emax=999999)):
                            requested_h=D(sign)/den;target=t0*requested_h.exp()
                            actual_h=(target/t0).ln()
                            direct=oracle(row,target,loss)
                            residual=direct-f0-d0*actual_h
                        result=m.taylor(key,14000,16000,t0,target,loss)
                        self.assertLessEqual(result['enclosure'].lo,direct)
                        self.assertLessEqual(direct,result['enclosure'].hi)
                        self.assertLessEqual(residual.copy_abs(),result['radius'])
                        records['taylor'].append({'key':key,'quantity':'L' if loss else 'alpha',
                            'T0_K':str(t0),'T0_origin':'interpolation of saved background only',
                            'requested_h':str(requested_h),'target_K':str(target),'actual_h_oracle':str(actual_h),
                            'direct_value':str(direct),'direct_residual':str(residual),
                            'remainder_radius':str(result['radius']),'h_bounds':result['h'].wire(),
                            'f0_bounds':result['f0'].wire(),'d0_bounds':result['d0'].wire(),
                            'linearized_enclosure':result['enclosure'].wire(),'contained':True})
        for precision in (50,70):
            mm=DRModel(data,precision)
            for loss in (False,True):
                r=mm.range('2:1',14000,16000,loss);v=oracle(data['dr']['2:1'],D(15000),loss)
                self.assertLessEqual(r.lo,v);self.assertLessEqual(v,r.hi)
                records['precision_comparison'].append({'digits':precision,'quantity':'L' if loss else 'alpha','bounds':r.wire(),'oracle':str(v)})
        self.assertEqual(m.range('1:1',100,101).lo,0)
        self.assertTrue(m.positivity('1:1')['structural_absence'])
        records['absence']={'key':'1:1','alpha_bounds':m.range('1:1',100,101).wire(),
                            'L_bounds':m.range('1:1',100,101,True).wire(),'structural_absence':True}
        bad=[('unknown_key',lambda:m.range('9:9',100,101)),
             ('hash_mismatch',lambda:load_source(path,'0'*64))]
        for name,x,y in [('bool',True,101),('complex',100+0j,101),('nan',D('NaN'),101),
                         ('infinity',float('inf'),101),('low',99,101),('high',100,1000001),('reversed',101,100)]:
            bad.append((name,lambda x=x,y=y:m.range('2:1',x,y)))
        for name,call in bad:
            with self.assertRaises((ValueError,TypeError)):
                call()
            records['rejections'].append({'case':name,'refused':True})
        self.output.update(records)
