"""Frozen fixed-center PWBE Eqs1-12; scalar binary64 reference.

Exact outgoing swap, both nuclear subtractions, one unpolarized spin average.
This is neither BO exchange nor an empirically qualified full event provider.
"""
import math
import numbers

METADATA = {
    'model': 'Weigold_Eqs19_20_exact_swapped_PWBE_independent_spin_trace',
    'measure': 'dE_B dOmega_A dOmega_B; dOmega=dmu dphi',
    'energy_unit': 'Hartree', 'momentum_unit': 'hbar/a0',
    'physical_TDCS_scaling': 'a0^2/Eh per sr^2',
    'source_Eq21_unpolarized_adopted': False,
    'finite_mass_recoil_law': False, 'physical_provider_admitted': False,
}


def _real(value, name):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(name + ' must be a finite real scalar')
    try:
        value = float(value)
    except (OverflowError, ValueError):
        raise ValueError(name + ' is not finite') from None
    if not math.isfinite(value):
        raise ValueError(name + ' is not finite')
    return value


def _finite(value):
    if isinstance(value, dict):
        for x in value.values(): _finite(x)
    elif isinstance(value, (list, tuple)):
        for x in value: _finite(x)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite/overflow in PWBE arithmetic')
    return value


def spin_channels(D, X):
    """Raw singlet/triplet and their once-weighted unpolarized mixture."""
    def amplitude(z):
        if isinstance(z, bool) or not isinstance(z, numbers.Complex):
            raise ValueError('amplitude must be a finite complex scalar')
        z = complex(z)
        if not (math.isfinite(z.real) and math.isfinite(z.imag)):
            raise ValueError('nonfinite amplitude')
        return z
    D, X = amplitude(D), amplitude(X)
    try:
        singlet, triplet = abs(D + X)**2, abs(D - X)**2
        return _finite({'singlet': singlet, 'triplet': triplet,
                        'unpolarized': 0.25*singlet + 0.75*triplet})
    except OverflowError:
        raise ValueError('spin arithmetic overflow') from None


def _geometry(E0, EB, muA, muB, ordered):
    if type(ordered) is not bool:
        raise ValueError('ordered must be bool')
    E0, EB = _real(E0, 'E0'), _real(EB, 'EB')
    muA, muB = _real(muA, 'muA'), _real(muB, 'muB')
    if not E0 > 0.5 or not 0 < EB < E0 - 0.5:
        raise ValueError('require E0>1/2 and 0<EB<E0-1/2')
    EA = (E0 - 0.5) - EB
    if ordered and EB > EA:
        raise ValueError('ordered sector requires EA>=EB; equality is pointwise boundary')
    if not (-1 <= muA <= 1 and -1 <= muB <= 1):
        raise ValueError('mu outside [-1,1]')
    try:
        k0, kA, kB = [math.sqrt(e)*math.sqrt(2) for e in (E0, EA, EB)]
        kA2, kB2 = 2*EA, 2*EB
        sA, sB = math.sqrt((1-muA)*(1+muA)), math.sqrt((1-muB)*(1+muB))
        RA, RB = kA*sA, kB*sB
        z = k0 - kA*muA - kB*muB
        DA2 = (k0-kA)**2 + 2*k0*kA*(1-muA)
        DB2 = (k0-kB)**2 + 2*k0*kB*(1-muB)
        if not (DA2 > 0 and DB2 > 0):
            raise ValueError('positive momentum gaps not represented')
        am = 1 + z*z + (RA-RB)**2
        ap = 1 + z*z + (RA+RB)**2
        a = 1 + z*z + RA*RA + RB*RB
        b = 2*RA*RB
        g = dict(E0=E0, EA=EA, EB=EB, muA=muA, muB=muB,
                 k0=k0,kA=kA,kB=kB,kA2=kA2,kB2=kB2,sA=sA,sB=sB,
                 RA=RA,RB=RB,z=z,DeltaA2=DA2,DeltaB2=DB2,
                 alpha=1/DA2,beta=1/DB2,hA=(1/(1+kA2))**2,
                 hB=(1/(1+kB2))**2,a=a,b=b,a_minus_b=am,a_plus_b=ap,
                 P0=(32/math.pi**2)*(kA/k0)*kB,
                 domain='ordered_equal_boundary' if EA==EB else ('ordered_interior' if ordered else 'full_labeled_diagnostic'))
        return _finite(g)
    except (OverflowError, ZeroDivisionError):
        raise ValueError('geometry overflow/invalid arithmetic') from None


def pwbe_point(E0, EB, muA, muB, phi, ordered=True):
    g = _geometry(E0,EB,muA,muB,ordered)
    phi = math.remainder(_real(phi, 'phi'), 2*math.pi)
    try:
        # Cartesian norm is nonnegative; no subtraction of large squared norms.
        qx = -g['RA'] - g['RB']*math.cos(phi)
        qy = -g['RB']*math.sin(phi)
        q2 = qx*qx + qy*qy + g['z']**2
        invq, invA, invB = 1/(1+q2), 1/(1+g['kA2']), 1/(1+g['kB2'])
        # Rationalized difference of inverse squares, both nuclear terms retained.
        def sub(k2, inv):
            return (k2-q2)*(2+k2+q2)*invq*invq*inv*inv
        d = g['alpha']*sub(g['kB2'],invB)
        x = g['beta']*sub(g['kA2'],invA)
        source_norm = math.sqrt(2)/math.pi**3
        D, X = source_norm*d, source_norm*x
        channels = spin_channels(D,X)
        w = (d-x/2)**2 + 0.75*x*x
        return _finite({'geometry':g,'phi':phi,'q2':q2,'d':d,'x':x,
                        'D':D,'X':X,'spin':channels,'w':w,'K':g['P0']*w,
                        'metadata':METADATA})
    except (OverflowError, ZeroDivisionError):
        raise ValueError('point overflow/invalid arithmetic') from None


def azimuth_integrals(a,b,*,a_minus_b=None,a_plus_b=None):
    a,b = _real(a,'a'), _real(b,'b')
    if not (a>b>=0): raise ValueError('require a>b>=0')
    if (a_minus_b is None)!=(a_plus_b is None):
        raise ValueError('both stable endpoints required')
    am = a-b if a_minus_b is None else _real(a_minus_b,'a_minus_b')
    ap = a+b if a_plus_b is None else _real(a_plus_b,'a_plus_b')
    if not am>0 or not ap>0:raise ValueError('positive denominator endpoints required')
    if a_minus_b is not None and not (math.isclose(am+ap,2*a,rel_tol=2e-13) and math.isclose(ap-am,2*b,rel_tol=2e-13,abs_tol=2e-15)):
        raise ValueError('stable endpoint metadata inconsistent with a,b')
    try:
        rho=math.sqrt(am)*math.sqrt(ap)
        inva=1/a; r=b/a; y=rho/a
        I2=inva**2/y**3
        I4=inva**4*(2+3*r*r)/(2*y**7)
        J2=-inva**2*r/y**3 if b else 0.0
        J4=-inva**4*r*(4+r*r)/(2*y**7) if b else 0.0
        var=inva**4*r*r*(5+3*y)/(2*y**7*(1+y)) if b else 0.0
        return _finite({'rho':rho,'I2':I2,'I4':I4,'J2':J2,'J4':J4,'var_t':var})
    except (OverflowError, ZeroDivisionError):
        raise ValueError('azimuth-integral overflow/invalid arithmetic') from None


def pwbe_azimuth(E0,EB,muA,muB,ordered=True):
    g=_geometry(E0,EB,muA,muB,ordered)
    v=azimuth_integrals(g['a'],g['b'],a_minus_b=g['a_minus_b'],a_plus_b=g['a_plus_b'])
    try:
        al,be,ha,hb=g['alpha'],g['beta'],g['hA'],g['hB']
        A2=(al-be/2)**2+0.75*be*be
        A1=-2*al*al*hb-2*be*be*ha+al*be*(ha+hb)
        A0=(al*hb-be*ha/2)**2+0.75*(be*ha)**2
        db,xb=al*(v['I2']-hb),be*(v['I2']-ha)
        M0=A2*v['var_t']+(db-xb/2)**2+0.75*xb*xb
        M0poly=math.fsum([A2*v['I4'],A1*v['I2'],A0])
        term1,term2=A2*v['J4'],A1*v['J2']
        M1=math.fsum([term1,term2])
        Kbar,Cbar=g['P0']*M0,g['P0']*M1
        defined=M0>0 and Kbar>0
        cosphi=M1/M0 if defined else None
        pair=g['muA']*g['muB']+g['sA']*g['sB']*cosphi if defined else None
        cancellation=(abs(term1)+abs(term2))/abs(M1) if M1 else None
        return _finite({'geometry':g,'integrals':v,'M0':M0,'M1':M1,
                        'M0_polynomial':M0poly,'Kbar':Kbar,'Cbar':Cbar,
                        'conditional_defined':defined,'cos_phi':cosphi,
                        'sin_phi':0.0 if defined else None,'pair_dot':pair,
                        'conditioning':{'M1_cancellation_ratio':cancellation,
                                        'M0_absolute_scale':M0,
                                        'binary64_zero_density':M0==0 or Kbar==0,
                                        'scope':'finite frozen fixtures; no all-dynamic-range fidelity guarantee; no epsilon clipping'},
                        'metadata':METADATA})
    except (OverflowError,ZeroDivisionError):
        raise ValueError('moment overflow/invalid arithmetic') from None


def conditional_azimuth_pdf(E0,EB,muA,muB,phi,ordered=True):
    moment=pwbe_azimuth(E0,EB,muA,muB,ordered=ordered)
    # Validate phi even if the conditional law is undefined.
    _real(phi,'phi')
    if not moment['conditional_defined']:
        return {'defined':False,'pdf':None,'reason':'computed zero-density conditional law is undefined'}
    point=pwbe_point(E0,EB,muA,muB,phi,ordered=ordered)
    return _finite({'defined':True,'pdf':point['K']/(2*math.pi*moment['Kbar'])})
