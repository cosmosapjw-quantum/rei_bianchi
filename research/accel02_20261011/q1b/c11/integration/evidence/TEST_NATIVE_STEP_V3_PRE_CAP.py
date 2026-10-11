"""New explicit native-conditioned absorption dependency plumbing only."""
import unittest
from types import SimpleNamespace
import numpy as np
import native_step_v3

class AbsorptionDispatchTests(unittest.TestCase):
    def test_explicit_absorption_and_original_rejection(self):
        failure=ArithmeticError('NATIVE_CERTIFICATE_REFUSED');calls=[]
        def prepare(*args,**kwargs):
            calls.append((args,kwargs));raise failure
        absorption=SimpleNamespace(prepare_incident=prepare)
        provider=SimpleNamespace(geometry=lambda t:{'H':1.,'s':0.},
            ray=lambda weights,mu,t:(None,np.array([0.]),np.array([1.])))
        source=SimpleNamespace(provider=provider,mu=np.array([0.]),edges=np.array([1.,2.]))
        source_api=SimpleNamespace(provider_event_times=lambda *a:(),
            integrate_source=lambda *a,**kw:{'R1':np.ones(1)},
            advance_source=lambda *a:{'N':np.ones((1,1)),'U_eV':np.full((1,1),1.5)})
        state={'t_s':0.,'N':np.ones((1,1)),'U_eV':np.ones((1,1))}
        with self.assertRaises(ArithmeticError) as ctx:
            native_step_v3.positive_native_step(state,1.,source,None,None,
                source_api=source_api,absorption_api=absorption)
        self.assertIs(ctx.exception,failure)
        self.assertEqual(calls[0][1],{'orders':(64,128),'rtol':1e-7})
        self.assertIn('angle=0',ctx.exception.__notes__[0])
    def test_no_implicit_conditioning_certificate(self):
        with self.assertRaisesRegex(TypeError,'absorption_api'):
            native_step_v3.positive_native_step({},1.,None,None,None,source_api=None)

if __name__=='__main__':unittest.main(verbosity=2)
