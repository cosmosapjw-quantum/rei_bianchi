"""Six-state count suboperator with provided analytic jets and proper clock.

No source amplitude, empirical rate, whole-client certificate or energy model
is supplied. Domain validation is separate so callers can place it before
obtaining immutable provider jets. No provider callback runs in this module.
"""
import math

STATE=('x_n','x_p','x_H0','x_e_fast','x_antinue','ell')
PROVIDERS=('S','lambda_c','lambda_b','theta','alpha','chi')
NU_C=(-1,1,0,1,1);NU_B=(-1,0,1,0,1)
BARYON=(1,1,1,0,0);CHARGE=(0,1,0,-1,0);LEPTON=(0,0,1,1,-1)


def _finite(value,name):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError('NONFINITE_'+name) from exc
    if not math.isfinite(value):raise ValueError('NONFINITE_'+name)
    return value


def check_domain(z,domain,rstar,*,labels=STATE):
    if tuple(labels)!=STATE:raise ValueError('ORDERED_STATE_OR_ELECTRON_POOL_MISMATCH')
    try:
        z=tuple(_finite(v,'STATE') for v in z)
        lower=tuple(_finite(v,'LOWER_BOUND') for v in domain['lower'])
        upper=tuple(_finite(v,'UPPER_BOUND') for v in domain['upper'])
    except (KeyError,TypeError) as exc:raise ValueError('EXPLICIT_DOMAIN_REQUIRED') from exc
    if len(z)!=6 or len(lower)!=6 or len(upper)!=6:raise ValueError('SIX_COORDINATES_REQUIRED')
    if any(lo>hi for lo,hi in zip(lower,upper)) or any(v<0 for v in z[:5]):raise ValueError('INVALID_PHYSICAL_DOMAIN')
    if any(v<lo or v>hi for v,lo,hi in zip(z,lower,upper)):raise ValueError('STATE_OUTSIDE_DOMAIN')
    rstar=_finite(rstar,'REFERENCE_SCALE')
    if rstar<=0:raise ValueError('POSITIVE_REFERENCE_SCALE_REQUIRED')
    try:r=rstar*math.exp(z[5])
    except OverflowError as exc:raise ValueError('REFERENCE_OVERFLOW') from exc
    if not math.isfinite(r) or r<=0:raise ValueError('NONFINITE_OR_NONPOSITIVE_REFERENCE')
    return z,r


def evaluate(z,jets,rstar,domain,*,labels=STATE):
    """Return RHS, full6x6 analytic Jacobian, and supplied-only policy."""
    z,r=check_domain(z,domain,rstar,labels=labels)
    if not isinstance(jets,dict) or set(jets)!=set(PROVIDERS):raise ValueError('SIX_EXPLICIT_PROVIDER_JETS_REQUIRED')
    values={};gradients={}
    for name in PROVIDERS:
        try:value,gradient=jets[name];gradient=tuple(gradient)
        except (TypeError,ValueError) as exc:raise ValueError('VALUE_AND_SIX_GRADIENTS_REQUIRED') from exc
        if len(gradient)!=6:raise ValueError('VALUE_AND_SIX_GRADIENTS_REQUIRED')
        values[name]=_finite(value,name);gradients[name]=tuple(_finite(v,name+'_GRADIENT') for v in gradient)
    S,lc,lb,theta,alpha,chi=(values[name] for name in PROVIDERS)
    if S<0 or lc<0 or lb<0 or chi<=0:raise ValueError('SOURCE_RATE_OR_CLOCK_DOMAIN')
    source=S/r;dilution=theta+alpha;P=z[0]
    g=tuple((source if i==0 else 0)+NU_C[i]*lc*P+NU_B[i]*lb*P-dilution*z[i] for i in range(5))
    rhs=tuple(chi*v for v in g)+(chi*alpha,)
    jac=[]
    for i in range(5):
        row=[]
        for j in range(6):
            ds=gradients['S'][j]/r-(source if j==5 else 0)
            dd=gradients['theta'][j]+gradients['alpha'][j]
            inner=((ds if i==0 else 0)+NU_C[i]*(P*gradients['lambda_c'][j]+(lc if j==0 else 0))
                   +NU_B[i]*(P*gradients['lambda_b'][j]+(lb if j==0 else 0))
                   -z[i]*dd-(dilution if i==j else 0))
            row.append(gradients['chi'][j]*g[i]+chi*inner)
        jac.append(tuple(row))
    jac.append(tuple(gradients['chi'][j]*alpha+chi*gradients['alpha'][j] for j in range(6)))
    if not all(math.isfinite(v) for v in rhs) or not all(math.isfinite(v) for row in jac for v in row):
        raise ValueError('NONFINITE_CLIENT_OUTPUT')
    return {'rhs':rhs,'jacobian':tuple(jac),'reference_density':r,'source_per_reference':source,
            'derivative_policy':'ProvidedOnly','empirical_rates_admitted':False,
            'full_client_admitted':False,'thermal_heat':None}


def jvp(jacobian,direction):
    direction=tuple(_finite(v,'DIRECTION') for v in direction)
    if len(direction)!=6 or len(jacobian)!=6 or any(len(row)!=6 for row in jacobian):raise ValueError('JVP_DIMENSION')
    out=tuple(sum(a*b for a,b in zip(row,direction)) for row in jacobian)
    if not all(math.isfinite(v) for v in out):raise ValueError('NONFINITE_JVP')
    return out


def lifted_oracle(x0,ell0,rstar,shat,lambda_c,lambda_b,h,Theta,Aref):
    """Exact restricted lifted-source oracle; no inferred endpoint history."""
    from reused_beta_transfer import beta_transfer
    x0=tuple(_finite(v,'INITIAL_COUNT') for v in x0)
    if len(x0)!=5 or any(v<0 for v in x0):raise ValueError('FIVE_NONNEGATIVE_INITIAL_COUNTS_REQUIRED')
    ell0=_finite(ell0,'INITIAL_LOG_REFERENCE');rstar=_finite(rstar,'REFERENCE_SCALE')
    Theta=_finite(Theta,'INTEGRATED_EXPANSION');Aref=_finite(Aref,'INTEGRATED_REFERENCE_GROWTH')
    if rstar<=0:raise ValueError('POSITIVE_REFERENCE_SCALE_REQUIRED')
    out=beta_transfer(x0[0],shat,lambda_c,lambda_b,h)
    try:g=math.exp(-(Theta+Aref));rnew=rstar*math.exp(ell0+Aref);rinitial=rstar*math.exp(ell0)
    except OverflowError as exc:raise ValueError('ORACLE_EXPONENTIAL_OVERFLOW') from exc
    if g<=0 or rnew<=0 or rinitial<=0 or not all(math.isfinite(v) for v in (g,rnew,rinitial)):raise ValueError('ORACLE_EXPONENTIAL_DOMAIN')
    B=out['beta_events'];R=out['competing_removals']
    lifted=(out['parent'],x0[1]+B,x0[2]+R,x0[3]+B,x0[4]+B+R)
    updated=tuple(g*v for v in lifted)+(ell0+Aref,)
    densities=tuple(rnew*v for v in updated[:5])
    if not all(math.isfinite(v) for v in updated+densities):raise ValueError('NONFINITE_ORACLE_OUTPUT')
    return {'state':updated,'lifted_counts':lifted,'physical_densities':densities,
            'continuum_events':B,'bound_events':R,'scale_g':g,'source_history':'constant_lifted_source_only'}
