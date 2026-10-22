"""Frozen T1–T8 fixtures and bounded discrimination controls."""
import math
import sys
import unittest
from fractions import Fraction as F
import thermal_ledger as ledger

EPS = 64*sys.float_info.epsilon
RECORDS = []


def check(case, actual, expected, terms):
    scale = sum(abs(x) for x in terms)
    residual = abs(actual-expected)
    tolerance = EPS*scale
    normalized = float(residual/tolerance) if tolerance else (0.0 if residual == 0 else math.inf)
    RECORDS.append(dict(check=case, residual=float(residual), tolerance=float(tolerance),
                        normalized_residual=normalized))
    if residual > tolerance:
        raise AssertionError(f'{case}: {actual} != {expected}, residual={residual}, tol={tolerance}')


def equal(case, actual, expected):
    check(case, actual, expected, [actual, expected])


class ScalarChecks(unittest.TestCase):
    def test_T1(self):
        g = ledger.gas_rhs(F(2), F(3), F(1,10), F(3,10), F(1,10), F(5), F(1))
        for key, value in dict(S_part=F(2,5), dot_n=F(-1,5), U=9, P=6,
                               dot_U=F(1,2), dot_T=F(7,15)).items():
            equal('T1.'+key, g[key], value)
        reverse = F(3,2)*(2*g['dot_T']+3*g['dot_n'])
        check('T1.reverse_chain', reverse, F(1,2), [F(3)*g['dot_T'], F(9,2)*g['dot_n'], F(1,2)])
        no_e = ledger.gas_rhs(2, 3, F(1,10), F(3,10), 0, 5, 1)
        self.assertNotEqual(no_e['dot_T'], g['dot_T'])

    def test_T2(self):
        p = ledger.particle_sources([-2,1,1], [0,3,8], [0,1,2])
        for key, value in dict(S_heavy=0, S_e=3, Q_B=11).items():
            equal('T2.'+key, p[key], value)

    def test_T3(self):
        a = ledger.photo_event(2,22,3,F(1,4))
        for key, value in dict(gas=4,binding=6,radiation=-22,nonthermal=12).items():
            equal('T3.'+key,a[key],value)
        check('T3.closure',ledger.exchange_residual(a),0,list(a.values()))
        deposition = ledger.allocation(gas=12, nonthermal=-12)
        check('T3.deposition',ledger.exchange_residual(deposition),0,list(deposition.values()))
        equal('T3.no_second_absorption',deposition['radiation'],0)

    def test_T4(self):
        a = ledger.rr_event(5,10,3)
        for key, value in dict(gas=-10,binding=-15,radiation=25).items():
            equal('T4.'+key,a[key],value)
        check('T4.closure',ledger.exchange_residual(a),0,list(a.values()))
        # chi_l=1: free-bound chi_l R+C=15, prompt cascade (chi-chi_l)R=10.
        equal('T4.bolometric_partition',15+10,a['radiation'])

    def test_T5(self):
        # <mu^(2k)>=1/(2k+1); P2=(3mu²-1)/2 gives <P2>=0, <P2²>=1/5.
        mean_p2 = (3*F(1,3)-1)/2
        mean_p2_squared = (9*F(1,5)-6*F(1,3)+1)/4
        angular = 1+mean_p2
        N = F(3**2-1,2)*angular
        U = F(3**3-1,3)*angular
        p = U*mean_p2_squared/3
        mean_D = F(1,2)+2*F(1,4)*mean_p2_squared
        FN = -mean_D*(3**2-1)
        FE = -mean_D*(3**3-1)
        for key,a,e in [('N',N,4),('U',U,F(26,3)),('p',p,F(26,45)),
                        ('FN',FN,F(-24,5)),('FE',FE,F(-78,5))]:
            equal('T5.integral_'+key,a,e)
        b = ledger.band_rhs(N,U,p,F(1,2),F(1,4),0,0,FN,FE)
        equal('T5.dot_N',b['dot_N'],F(-6,5))
        equal('T5.dot_U',b['dot_U'],F(-13,5))
        check('T5.first_law', b['dot_U']+4*F(1,2)*U+6*F(1,4)*p, -FE,
              [b['dot_U'],4*F(1,2)*U,6*F(1,4)*p,FE])

    def test_T6(self):
        for sign in (1,-1):
            K,J = sign*F(-2,3),sign*F(-7,3)
            a = ledger.band_rhs(0,2,F(1,5),F(1,2),F(1,4),0,0,K,J)
            b = ledger.band_rhs(0,3,F(-1,10),F(1,2),F(1,4),0,0,-K,-J)
            check(f'T6.number_{sign}',a['dot_N']+b['dot_N'],0,[K,-K])
            check(f'T6.energy_{sign}',a['dot_U']+b['dot_U'],F(-203,20),
                  [a['dot_U'],b['dot_U'],F(203,20)])

    def test_T7(self):
        a=ledger.allocation(nuclear_rest=-10,gas=2,nonthermal=3,radiation=4,neutrino=1)
        check('T7.synthetic_closure',ledger.exchange_residual(a),0,list(a.values()))
        equal('T7.no_atomic_binding',a['binding'],0)
        g=ledger.gas_rhs(2,3,0,F(-1,5),F(2,5),0,1)
        equal('T7.separate_sources',g['dot_T'],F(-3,10))

    def test_T8(self):
        matter = ledger.component_work(0,0,-3,0,2)
        radiation = ledger.component_work(0,0,5,0,2)
        equal('T8.matter_shear',matter,-36)
        equal('T8.radiation_shear',radiation,60)
        equal('T8.total_shear',matter+radiation,24)
        for name,a in [('open',ledger.allocation(radiation=9,external_power=9)),
                       ('extended',ledger.allocation(radiation=9,emitter=-9))]:
            check('T8.'+name,ledger.exchange_residual(a),0,list(a.values()))

    def test_invalid_inputs(self):
        invalid = [lambda:ledger.gas_rhs(0,3,0,0,0,0,1),
                   lambda:ledger.gas_rhs(2,-1,0,0,0,0,1),
                   lambda:ledger.gas_rhs(2,3,0,0,0,0,0),
                   lambda:ledger.gas_rhs(2,3,float('nan'),0,0,0,1),
                   lambda:ledger.photo_event(2,22,3,F(5,4)),
                   lambda:ledger.photo_event(-2,22,3),
                   lambda:ledger.photo_event(2,5,3),
                   lambda:ledger.photo_event(2.,5.,3.),
                   lambda:ledger.rr_event(-1,10,3),
                   lambda:ledger.photo_event(0,1,3),
                   lambda:ledger.rr_event(0,1,3)]
        for fn in invalid:
            with self.assertRaises(ValueError): fn()
        # Roundoff-sized deficit allowed; exact rational deficits are rejected.
        a=ledger.photo_event(1.,math.nextafter(3.,0.),3.)
        check('invalid.roundoff_allowance',ledger.exchange_residual(a),0,list(a.values()))
        with self.assertRaises(ValueError): ledger.photo_event(1,F(3)-F(1,10**20),3)


def discrimination_controls():
    controls=[]
    def detect(name,residual,terms):
        tolerance=EPS*sum(abs(x) for x in terms)
        detected=abs(residual)>tolerance
        controls.append(dict(control=name,residual=float(abs(residual)),tolerance=float(tolerance),
                             normalized_residual=float(abs(residual)/tolerance) if tolerance else math.inf,
                             detected=detected))
        if not detected: raise AssertionError('undetected mutation '+name)
    omit_heavy=ledger.gas_rhs(2,3,F(1,10),0,F(1,10),5,1)['dot_T']
    detect('T1.omit_S_heavy',omit_heavy-F(7,15),[omit_heavy,F(7,15)])
    a=ledger.photo_event(2,22,3,F(1,4))
    detect('T3.omit_nonthermal',sum(a[k] for k in ledger.OWNERS if k!='nonthermal'),list(a.values()))
    detect('T5.omit_shear',6*F(1,4)*F(26,45),[F(-13,5),F(52,3),F(13,15),F(-78,5)])
    detect('T5.omit_boundary',F(-78,5),[F(-13,5),F(52,3),F(13,15),F(-78,5)])
    detect('T7.omit_neutrino',-1,[-10,2,3,4,1])
    factor=1e-23
    scaled=ledger.photo_event(2,22*factor,3*factor,.25)
    check('T3.SI_closure',ledger.exchange_residual(scaled),0,list(scaled.values()))
    detect('T3.SI_omit_nonthermal',sum(scaled[k] for k in ledger.OWNERS if k!='nonthermal'),list(scaled.values()))
    return controls


if __name__ == '__main__':
    unittest.main()
