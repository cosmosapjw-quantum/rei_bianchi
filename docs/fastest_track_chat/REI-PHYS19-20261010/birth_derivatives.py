"""Exact lower-limit birth derivatives, normalized s=t/T and beta=b/T."""
def optical_derivatives(a_derivatives, sigma_D, lam, integrals):
    if len(a_derivatives)!=4 or len(sigma_D)<5 or len(integrals)!=4:
        raise ValueError('orders 0..3, 0..4, and 1..4 required')
    return [integrals[n-1]-sum(a_derivatives[n-1-r]*lam**r*sigma_D[r] for r in range(n)) for n in range(1,5)]

def survival_derivatives(A):
    """Return d_beta^n exp(-A)/exp(-A), n=0..4."""
    a,b,c,d=A
    return [1,-a,a*a-b,-a**3+3*a*b-c,a**4-6*a*a*b+3*b*b+4*a*c-d]
