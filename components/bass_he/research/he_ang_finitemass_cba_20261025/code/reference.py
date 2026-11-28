"""High precision and original-integral controls for the frozen new fixtures.

No parent science scripts or suites are imported or executed.
"""
import mpmath as mp


def mpjson(z):
    return {'real': mp.nstr(mp.re(z), 85), 'imag': mp.nstr(mp.im(z), 85)}


def scaled(a, b):
    return abs(a-b)/max(mp.mpf(1), abs(b))


def mp_parameters(M):
    M = mp.mpf(M)
    return M/(M+1), 1/(M+1)


def mp_overlap(lam, s, kvec):
    lam = mp.mpf(lam)
    s, kvec = list(map(mp.mpf, s)), list(map(mp.mpf, kvec))
    k = mp.sqrt(sum(v*v for v in kvec)); eta = lam/k
    A = sum((d-p)**2 for d, p in zip(s, kvec))+lam*lam
    ss = sum(d*d for d in s); B = ss+(lam-1j*k)**2
    C = mp.exp(1j*eta*(mp.log(A)-mp.log(B)))
    return 16*mp.pi*lam*C*(ss-(1+1j*eta)*sum(d*p for d, p in zip(s, kvec)))/(A*A*B)


def mp_form_factor(M, Delta, kvec):
    mu, b = mp_parameters(M)
    Delta, kvec = list(map(mp.mpf, Delta)), list(map(mp.mpf, kvec))
    k = mp.sqrt(sum(v*v for v in kvec)); eta = mu/k
    plus = mp_overlap(mu, [mu*d for d in Delta], kvec)
    minus = mp_overlap(mu, [-b*d for d in Delta], kvec)
    Nc = mp.exp(mp.pi*eta/2)*mp.gamma(1-1j*eta)/(2*mp.pi)**mp.mpf('1.5')
    return Nc*mp.sqrt(mu**3/mp.pi)*(plus-minus), plus, minus


def original_integral(lam, s, kvec):
    """K integral after exact parabolic zeta integration, k along +z.

    The integrand contains the original hypergeometric Coulomb state and
    bound exponential; it contains no closed-form Nordsieck I or K.
    """
    lam = mp.mpf(lam)
    s, kvec = list(map(mp.mpf, s)), list(map(mp.mpf, kvec))
    if kvec[0] or kvec[1] or kvec[2] <= 0:
        raise ValueError('frozen quadrature fixtures require k along +z')
    p = kvec[2]; eta = lam/p
    qz = s[2]-p; qperp2 = s[0]**2+s[1]**2
    beta = (lam+1j*qz)/2; d = qperp2/4
    A = qperp2+qz*qz+lam*lam
    decay = A/(2*(lam+1j*qz))
    def integrand(xi):
        return mp.exp(-decay*xi)*mp.hyp1f1(1j*eta, 1, 1j*p*xi)*(xi+1/beta-d*xi/(beta*beta))
    segments = [(0, 1), (1, 4), (4, 12), (12, mp.inf)]
    parts = [mp.quad(integrand, [lo, hi]) for lo, hi in segments]
    return mp.pi/(2*beta)*sum(parts), parts
