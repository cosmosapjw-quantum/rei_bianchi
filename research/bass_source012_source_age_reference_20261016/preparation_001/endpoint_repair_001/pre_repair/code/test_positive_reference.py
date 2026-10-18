"""Synthetic falsifiers only. Never execute or spawn a native helper."""
import math
import unittest
from positive_reference import (Domain,DomainReject,Hold,HelperFailure,Counters,
                                heun,transaction,integrate,schedule,common_mesh,decode_setup)


class PositiveReferenceTests(unittest.TestCase):
    def setUp(self):
        self.d = Domain(.08,.001)
        self.v = (.25,.125,.0625,5.)

    def test_simplex_and_finite_falsifiers(self):
        self.d.validate(self.v)
        for bad in ((-1e-20,.1,.1,5),(1.00001,.1,.1,5),(.2,-1e-20,.1,5),
                    (.2,.8,.3,5),(.2,.1,float('nan'),5)):
            with self.assertRaises(DomainReject): self.d.validate(bad)

    def test_eos_bounds_and_directional_affine_bound(self):
        f,kb=.08,.001
        d=1+f+self.v[0]+f*(self.v[1]+2*self.v[2])
        low=1.5*kb*d; high=1.5*kb*1e6*d
        self.d.validate((*self.v[:3],low));self.d.validate((*self.v[:3],high))
        for w in (math.nextafter(low,-math.inf),math.nextafter(high,math.inf)):
            with self.assertRaises(DomainReject): self.d.validate((*self.v[:3],w))
        self.assertEqual(self.d.euler_bound(self.v,(-1.,0,0,0)),.9*.25)
        with self.assertRaisesRegex(Hold,'DOMAIN_HOLD'):
            self.d.euler_bound((0.,.1,.1,5.),(-1.,0,0,0))

    def test_zero_degenerate_and_nonempty_support_cones(self):
        d=Domain(.08,.001,((4,5,2.,4.),(6,7,2.,2.)))
        d.validate(self.v+(0.,0.,.25,.5))
        d.validate(self.v+(.25,.75,.25,.5))
        for tail in ((0.,1e-30,.25,.5),(.25,.49,.25,.5),(.25,1.01,.25,.5),
                     (.25,.75,.25,math.nextafter(.5,math.inf))):
            with self.assertRaises(DomainReject): d.validate(self.v+tail)

    def test_manufactured_heun_and_no_rhs_at_algebraic_two_h(self):
        seen=[]; c=Counters()
        def rhs(x,v): seen.append((x,v)); return (.1*x,0.,0.,0.)
        out=heun(rhs,0.,self.v,.2,self.d,c)
        # Exact integral of h'=.1*x is .05*x^2; independent closed form.
        self.assertAlmostEqual(out[0],.25+.05*.2**2,places=15)
        self.assertEqual([x for x,v in seen],[0.,.2]);self.assertEqual(c.rhs,2)
        # Distinguishes Heun from Euler using y'=y: 1+h+h^2/2.
        out=heun(lambda x,v:(v[0],0,0,0),0.,self.v,.1,self.d,Counters())
        self.assertAlmostEqual(out[0],.25*(1+.1+.1**2/2),places=15)

    def test_full_two_half_estimate_and_fine_not_richardson(self):
        c=Counters(); h=.01
        fine,e=transaction(lambda x,v:(v[0],0,0,0),0.,self.v,h,self.d,c)
        expected=.25*(1+h/2+(h/2)**2/2)**2
        coarse=.25*(1+h+h*h/2)
        expected_e=abs(expected-coarse)/(3*(2e-13+2e-9*max(.25,abs(expected))))
        self.assertAlmostEqual(fine[0],expected,places=15)
        self.assertAlmostEqual(e,expected_e,places=6)
        self.assertEqual((c.attempts,c.rhs,c.accepted),(1,6,0))
        self.assertNotEqual(fine[0],fine[0]+(fine[0]-coarse)/3)

    def test_transaction_domain_rejection_rollback_and_exact_costs(self):
        initial=list(self.v); seen=[];c=Counters()
        def fake(x,v):
            seen.append((x,v))
            return (100.,0.,0.,0.) if len(seen)==1 else (0.,0.,0.,0.)
        out=integrate(fake,initial,self.d,[0.,.01],initial_h=.01,counts=c)
        self.assertEqual(initial,list(self.v));self.assertEqual(out['state'],self.v)
        self.assertEqual(seen[1],(0.,self.v))
        self.assertEqual((c.attempts,c.rhs,c.accepted,c.rejected_domain,c.rejected_error,c.failed_helper),(3,13,2,1,0,0))

    def test_error_reject_and_callback_failure_keep_costs(self):
        c=Counters()
        out=integrate(lambda x,v:(v[0],0,0,0),self.v,self.d,[0.,.01],initial_h=.01,counts=c)
        self.assertGreater(c.rejected_error,0)
        self.assertEqual(c.attempts,c.accepted+c.rejected_error)
        self.assertEqual(c.rhs,6*c.attempts)
        self.assertLess(abs(out['state'][0]-.25*math.exp(.01)),1e-8) # synthetic analytic falsifier, not physical tolerance
        failed=Counters();old=list(self.v)
        def broken(x,v): raise ValueError('synthetic helper protocol failure')
        with self.assertRaises(HelperFailure):integrate(broken,old,self.d,[0.,.01],counts=failed)
        self.assertEqual(old,list(self.v))
        self.assertEqual((failed.attempts,failed.rhs,failed.failed_helper,failed.accepted),(1,1,1,0))
        with self.assertRaisesRegex(Hold,'STEP_UNDERFLOW'):
            transaction(broken,1.,self.v,1e-30,self.d,Counters())

    def test_all_discrete_birth_schedules_common_mesh_and_once_only(self):
        a0=1/21;a1=a0*math.exp(.002);mesh=common_mesh(a0,a1)
        self.assertEqual(len(mesh),58) # endpoints + 8+16+32 distinct midpoint knots
        for n in (8,16,32):
            births,weight=schedule(a0,a1,n)
            self.assertEqual(weight,(math.log(a1)-math.log(a0))/n)
            self.assertTrue(all(x in mesh for x in births))
            # Independent uniform quadrature: exactly n positive equal mass births.
            size=4+2*n; initial=self.v+(0.,)*(2*n)
            supports=tuple((4+2*j,5+2*j,2.,4.) for j in range(n))
            d=Domain(.08,.001,supports);inject=[]
            for j in range(n):
                inc=[0.]*size;inc[4+2*j]=1/n;inc[5+2*j]=3/n;inject.append(inc)
            out=integrate(lambda x,v:(0.,)*size,initial,d,mesh,births,inject)
            self.assertEqual(out['counts'].births,n)
            self.assertEqual(sum(out['state'][4::2]),1.)
            self.assertEqual(sum(out['state'][5::2]),3.)
            for x,v in out['saved']:
                for j,b in enumerate(births):
                    if x < b:self.assertEqual(v[4+2*j],0.)
            self.assertEqual(out['x'],math.log(a1))

    def test_fake_setup_protocol_identity_shape_and_unborn_controls(self):
        a0=1/21;a1=a0*math.exp(.002);births,_=schedule(a0,a1,8)
        r=dict(protocol='SOURCE012_RHS_ONLY_V1',q=-.1,birth_count=8,cells=1,
               native_base='35d9747a0bbedcafdb568467ce7c1e7a25f965b6',
               overlay='553ce556d9f8662290c000ec675c7e6007c9d895',
               f=.08,kb_eV_K=.001,initial=list(self.v)+( [0.]*16),
               x0=math.log(a0),x1=math.log(a1),mesh=common_mesh(a0,a1)[1:],births=births,
               support_lo=[[2.]]*8,support_hi=[[4.]]*8,inject=[[.125,.375]]*8)
        domain,initial,mesh,births,inject=decode_setup(r)
        out=integrate(lambda x,v:(0.,)*len(v),initial,domain,mesh,births,inject)
        self.assertEqual(out['counts'].births,8)
        for key,value in [('q',0),('native_base','wrong'),('initial',list(self.v)+[1.]*16)]:
            bad=dict(r);bad[key]=value
            with self.assertRaises(ValueError):decode_setup(bad)


if __name__=='__main__':
    unittest.main(verbosity=2)
