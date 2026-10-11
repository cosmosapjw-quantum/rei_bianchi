"""New dependency-injection behavior only; no old native/solver test replay."""
import unittest
from types import SimpleNamespace
import native_step_v2

class DispatchTests(unittest.TestCase):
    def test_explicit_source_dependency_and_original_diagnostics(self):
        calls=[]
        failure=ArithmeticError('NEW_SOURCE_REJECTION')
        failure.diagnostics={'input_t0':2.,'input_t1':3.}
        class API:
            @staticmethod
            def provider_event_times(source,t0,t1):
                calls.append(('events',source,t0,t1)); return (2.5,)
            @staticmethod
            def integrate_source(source,t0,t1,*,event_times):
                calls.append(('integrate',source,t0,t1,event_times));raise failure
        provider=SimpleNamespace(geometry=lambda t:{})
        source=SimpleNamespace(provider=provider)
        with self.assertRaises(ArithmeticError) as ctx:
            native_step_v2.positive_native_step({'t_s':2.},3.,source,None,None,source_api=API)
        self.assertIs(ctx.exception,failure)
        self.assertEqual(calls,[('events',source,2.,3.),('integrate',source,2.,3.,(2.5,))])
        self.assertEqual(ctx.exception.diagnostics,{'input_t0':2.,'input_t1':3.})
    def test_no_implicit_old_source_fallback(self):
        with self.assertRaisesRegex(TypeError,'source_api'):
            native_step_v2.positive_native_step({},1.,None,None,None)

if __name__=='__main__':unittest.main(verbosity=2)
