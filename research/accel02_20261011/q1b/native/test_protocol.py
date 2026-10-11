"""Bounded CELL_RHS_V1 checks: no trajectory, point-grid replay or shared oracle.

Photo effects are active-minus-dark at a fixed gas state. The imported gas
provider is deliberately common; these tests verify the new moment bridge,
not the independently unvalidated cell opacity reconstruction.
"""
import json
import math
import pathlib
import subprocess
import sys
import unittest

BIN = pathlib.Path(__file__).parent / 'target/release/rei_q1b_cell_native_v1'
EV = 1.602176634e-12
KB = 1.380649e-16
CHI = [13.598434599702, 24.587389011, 54.41776]


def fixture(x=(.2, .3, .1), a=1., h=2e-17, shear=1e-19):
    nh, nhe, temp = 1e-3, 8e-5, 5000.
    ne = nh*x[0]+nhe*(x[1]+2*x[2])
    w = 1.5*KB*temp*(nh+nhe+ne)/(nh*EV)
    return [0., a, .03, h, shear, nh, nhe, *x, w, 46.]


def cell(p, mu=.5):
    return [mu, .7, p[3]+p[4]*(3*mu*mu-1), 1e-8, 8e-7,
            1e-20, 9e-19, 1e-16, 2e-17, 1e-18,
            7e-15, 2e-15, 2e-16]


def command(p, cells, *, must_fail=False):
    line = 'CELL_RHS_V1 '+' '.join(format(v,'.17e') for v in
                                p+[len(cells)]+sum(cells,[]))+'\n'
    r = subprocess.run([str(BIN)], input=line, capture_output=True, text=True,
                       check=True)
    if must_fail:
        assert r.stdout.startswith('ERR '), r.stdout
        return r.stdout.strip()
    assert r.stdout.startswith('OK '), (r.stdout, r.stderr)
    return [float(v) for v in r.stdout.split()[1:]]


class CellProtocolTests(unittest.TestCase):
    def close(self, a, b, rtol=2e-11):
        self.assertLessEqual(abs(a-b),rtol*max(abs(a),abs(b),1e-100),(a,b))

    def test_paired_ionization_heat_and_cell_sinks(self):
        p=fixture(); c=cell(p); o=command(p,[c]); d=command(p,[])
        nh,nhe=p[5:7]; x,y,z=p[7:10]; V=p[1]**3
        lower=[nh*(1-x),nhe*(1-y-z),nhe*y]
        events=[lower[j]*c[7+j]/V for j in range(3)]
        for i,e in enumerate([events[0]/nh,(events[1]-events[2])/nhe,events[2]/nhe]):
            self.close(o[i]-d[i],e)
        heat=sum(lower[j]*(c[10+j]-CHI[j]*c[7+j])/V for j in range(3))
        self.close(o[3]-d[3],heat/nh)
        self.close(o[15],c[5]-sum(lower[j]*c[7+j] for j in range(3)))
        self.close(o[16],c[6]-sum(lower[j]*c[10+j] for j in range(3))-c[2]*c[4])
        photo_binding=sum(CHI[j]*events[j] for j in range(3))
        self.close(heat+photo_binding,sum(lower[j]*c[10+j]/V for j in range(3)))
        self.assertLess(abs(o[12]),1e-12);self.assertLess(abs(o[13]),1e-12)

    def test_zero_absorber_keeps_finite_gamma_without_division(self):
        p=fixture(x=(1.,0.,1.)); c=cell(p); o=command(p,[c]); d=command(p,[])
        for i in range(4): self.close(o[i],d[i])
        for j in range(3): self.close(o[8+j],c[7+j])
        self.close(o[15],c[5]); self.close(o[16],c[6]-c[2]*c[4])
        self.assertEqual(o[7],0.)

    def test_empty_cell_and_reference_volume(self):
        p=fixture(); c=cell(p); a=command(p,[c]); q=p.copy();q[1]=2.
        bigger=c.copy()
        for i in range(3,13):bigger[i]*=8.
        b=command(q,[bigger]); empty=[0.,.7,p[3]-p[4],0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
        e=command(p,[c,empty]);self.assertEqual(e[:17],a);self.assertEqual(e[17:],[0.,0.])
        entering=empty.copy();entering[5:7]=[1e-20,2e-19]
        born=command(p,[entering]);dark=command(p,[])
        self.assertEqual(born[15:],[1e-20,2e-19])
        self.assertEqual(born[:4],dark[:4])
        for j in [0,1,2,3,8,9,10,11]:self.close(a[j],b[j])
        for j in [4,5,6,7,14,15,16]:self.close(8*a[j],b[j])

    def test_source_and_anisotropic_work_are_paired(self):
        p=fixture(); c=cell(p,mu=1.);c[7:]=[0.]*6
        o=command(p,[c]); d=command(p,[])
        self.close(o[5]-d[5],(p[3]+2*p[4])*c[4]*EV)
        self.close(o[6],c[6]*EV)
        self.close(o[16]*EV+(o[5]-d[5]),o[6])
        self.close(o[15],c[5])

    def test_invalid_moment_inputs_are_rejected(self):
        p=fixture()
        for index,value in [(3,-1e-8),(4,0.),(4,1.),(2,0.),(7,0.),(10,1e-20),(1,0.),(6,1e-10)]:
            c=cell(p);c[index]=value;command(p,[c],must_fail=True)
        c=cell(p);c[3:5]=[0.,0.];command(p,[c],must_fail=True)
        c=cell(p);c[5]=0.;command(p,[c],must_fail=True)

    def test_cmb_sign_and_absent_helium(self):
        p=fixture();p[11]=6000.;a=command(p,[]);p[11]=46.;b=command(p,[])
        self.assertGreater(a[14],0.);self.assertLess(b[14],0.)
        self.close(a[4],b[4]);self.close(a[3]-b[3],(a[14]-b[14])/(p[5]*EV))
        p[6]=0.; o=command(p,[cell(p)]);self.assertEqual(o[1:3],[0.,0.])


if __name__=='__main__':
    unittest.main(verbosity=2)
