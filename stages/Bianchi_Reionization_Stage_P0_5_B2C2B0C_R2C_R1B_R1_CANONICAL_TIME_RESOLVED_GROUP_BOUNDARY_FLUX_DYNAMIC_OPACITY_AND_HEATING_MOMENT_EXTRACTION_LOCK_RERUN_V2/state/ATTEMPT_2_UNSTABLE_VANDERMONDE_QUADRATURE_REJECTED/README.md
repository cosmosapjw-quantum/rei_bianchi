# Rejected Vandermonde moment inversion

Direct monomial-Vandermonde inversion at Chebyshev–Lobatto nodes becomes catastrophically ill-conditioned and is singular at `N=33` in the current double-precision environment. It is not used. The accepted calculation uses the stable Clenshaw–Curtis weight formula and verifies nonnegative weights, unit \(\ell_1\) norm and polynomial moments before applying the dense/nested gates.
