"""New controls for proposed optimization semantics, not a native promotion suite."""
import math
import numpy as np
import pytest
import sympy as s


def test_phase_product_rule_exact_symbolic():
    t,v,de=s.symbols('t v de', real=True, nonzero=True)
    z=s.symbols('z', real=True)
    f=s.Function('f')
    phase=s.exp(s.I*(v*v*t/2+de*t))
    target=phase*(v*s.diff(f(z),z).subs(z,v*t)+s.I*(v*v/2+de)*f(v*t))
    assert s.simplify(s.diff(phase*f(v*t),t)-target)==0


def test_pure_phase_linear_midpoint_error_exact():
    a, h=s.symbols('a h', real=True)
    midpoint=(s.exp(s.I*a*h/2)+s.exp(-s.I*a*h/2))/2
    assert s.simplify(s.expand_complex(midpoint)-s.cos(a*h/2))==0


def test_algebraic_metric_identity_does_not_certify_interpolant_derivative():
    # O=e^t, D=dotO/2 at endpoints. Interpolating all three preserves the
    # algebraic identity, while d(interp O)/dt != interp(dotO).
    O0,O1=1.,math.exp(4.)
    Dmid=(O0/2+O1/2)/2
    dotOmid=(O0+O1)/2
    assert 2*Dmid==dotOmid
    assert not math.isclose((O1-O0)/4,dotOmid,rel_tol=1e-6)


@pytest.mark.parametrize('omega', [[0.3,-2.1],[0.,0.],[10.,2.]])
def test_phase_gauge_connection_term_is_required(omega):
    O=np.array([[2.,0.2+0.1j],[0.2-0.1j,1.]])
    dotO=np.array([[.1,.3j],[-.3j,-.2]])
    K=np.array([[.2j,.1+.2j],[-.1+.2j,-.4j]])
    D=.5*dotO+K
    U=np.diag(np.exp(1j*np.array(omega)*.7))
    dU=np.diag(1j*np.array(omega))@U
    Dt=U.conj().T@D@U+U.conj().T@O@dU
    derivative=dU.conj().T@O@U+U.conj().T@dotO@U+U.conj().T@O@dU
    assert np.allclose(Dt+Dt.conj().T,derivative,rtol=0,atol=2e-14)
