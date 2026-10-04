"""Derived kinetic moment, for a T-independent capture cross section.
No density factors; T in kelvin, alpha in cm^3/s, output in erg cm^3/s.
"""
KB=1.380649e-16

def kinetic_moment(T, alpha, logarithmic_slope):
    return KB*T*alpha*(1.5+logarithmic_slope)
