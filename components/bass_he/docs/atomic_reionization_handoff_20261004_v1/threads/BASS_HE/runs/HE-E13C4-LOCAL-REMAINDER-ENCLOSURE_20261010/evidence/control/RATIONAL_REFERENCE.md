# Exact rational reference enclosures

The reference routines use Python integers and `Fraction`. They do not call
Decimal transcendental functions, NumPy, SciPy, or the owner's interval routines.

For positive `x`, select `k` such that `y=x/2^k <= 1/8`. After the Taylor terms
through `y^n/n!`, the first omitted term is `a=y^(n+1)/(n+1)!`; all subsequent
term ratios are at most `r=y/(n+2)<1`. Thus `S_n <= exp(y) <= S_n+a/(1-r)`.
Positive squaring preserves the enclosure and gives an enclosure of `exp(x)`.
Each exact rational endpoint is rounded outward onto a `10^(-130)` grid to
bound integer growth. This rounding does not rely on floating-point arithmetic.
Negative arguments use `exp(-x)=1/exp(x)` with reversed endpoints.

For `x>0`, write `x=m*2^k`, `1<=m<2`, using exact rational multiplication or
division by two. Set `z=(m-1)/(m+1)`, so `0<=z<1/3`. The expansion

`ln(m)=2*sum_{j=0}^infinity z^(2j+1)/(2j+1)`

has positive terms. After the term indexed `j`, its remaining tail is no larger
than `2*z^(2j+3)/((2j+3)*(1-z^2))`. Apply the same series at `m=2` to enclose
`ln(2)`, then add `k*ln(2)` with correct endpoint reversal for negative `k`.

For `x=n/d>=0` and integer `S=10^110`, integer square root selects `k` such that
`k^2*d <= n*S^2 < (k+1)^2*d`. Dividing by `S` provides exact lower and upper
square-root bounds. Exact rational squares get identical endpoints.

Positive-base powers first enclose `exponent*ln(base)` and then use the monotone
exponential enclosure. The test reference for `J(rate,h)` uses
`(1-exp(-rate*h))/rate` and treats `rate=0` as the exact `h` limit.

These proofs establish each returned rational enclosure. The finite comparison
suite tests particular owner outputs against those enclosures; it does not by
itself constitute a proof for all owner-code inputs or the whole physical model.
