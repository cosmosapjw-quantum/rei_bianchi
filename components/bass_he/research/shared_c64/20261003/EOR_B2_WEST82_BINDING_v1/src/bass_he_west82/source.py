"""West82 primary definitions and exact printed resonance assignments.

No cross section is recovered from a graph or fabricated from the label table.
Electronic inputs to the adapter are supplied by caller; the paper gives curves,
not their numeric arrays. Optical-point evaluation is not source admission.
"""
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction
import numpy as np
from .optical import ContractError, NumericalFailure, _number, _checked

PDF_SHA256='c5f881d1cdced9e8c14e6e61351a8f38627bcaeec029cd1050a78d3599d4760e'
TABLE_SHA256='0c019346855e71f3dd53793efa0e9505ee860d292b951ebf40c3fccc9f0eb333'


def load_resonances(path, pdf_path):
    path=Path(path); pdf_path=Path(pdf_path)
    if path.is_symlink() or pdf_path.is_symlink():raise ContractError('SYMLINK_SOURCE_REFUSED')
    if hashlib.sha256(pdf_path.read_bytes()).hexdigest()!=PDF_SHA256:
        raise ContractError('WEST82_PDF_SHA_MISMATCH')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=TABLE_SHA256:raise ContractError('TABLE_I_SHA_MISMATCH')
    t=json.loads(raw)
    if len(t['rows'])!=25 or [r['label'] for r in t['rows']]!=list(range(1,26)):
        raise ContractError('TABLE_STRUCTURE_MISMATCH')
    return t


def optical_point(R_bohr, Eu, El, dipole, *, energy_unit, c_atomic, EH=-0.5):
    """Eqs5-8. Eu/El use declared Hartree or Ry; EH is always Hartree.

    Dipole is a normalized electronic matrix element vector in e*a0 units.
    c_atomic is c in a0/t_a. Numeric A in t_a^-1 equals Gamma in Eh.
    Multiplying the resulting A by DeltaE is NOT an exact photon-energy moment.
    """
    R=_number(R_bohr,'R_bohr',positive=True); c=_number(c_atomic,'c_atomic',positive=True)
    u=_number(Eu,'Eu'); l=_number(El,'El'); eh=_number(EH,'EH_hartree')
    if energy_unit not in ('Hartree','Ry'):raise ContractError('EXPLICIT_ENERGY_UNIT_REQUIRED')
    fac=1. if energy_unit=='Hartree' else .5
    u*=fac; l*=fac; gap=u-l
    if gap<0:raise ContractError('EMISSION_REQUIRES_NONNEGATIVE_GAP')
    try:
        d=np.asarray(dipole)
        if d.dtype.kind not in 'iufc' or d.shape!=(3,):raise ValueError()
        d=np.asarray(d,dtype=np.complex128)
    except (ValueError,TypeError) as e:raise ContractError('DIPOLE_VECTOR_REQUIRED') from e
    if not np.all(np.isfinite(d)):raise ContractError('FINITE_DIPOLE_REQUIRED')
    try:
        norm=math.hypot(*(v for z in d for v in (float(z.real),float(z.imag))))
        V=math.fsum((u,-eh,2/R))
        # Log arithmetic prevents intermediate overflow/underflow of gap^3*d^2.
        if gap==0 or norm==0:A=0.
        else:
            logA=math.log(4/3)+3*math.log(gap)+2*math.log(norm)-3*math.log(c)
            A=math.exp(logA)
            if A==0:raise NumericalFailure('POSITIVE_WIDTH_UNDERFLOW')
        _checked((V,A,gap),'optical adapter')
    except (OverflowError,ValueError,ZeroDivisionError) as e:
        raise NumericalFailure('OPTICAL_ADAPTER_NUMERICAL_RANGE') from e
    return {'schema':'bass-he.west82.optical-point.v1','data_kind':'DECLARED_ELECTRONIC_INPUT_TRANSFORMATION',
            'V_hartree':V,'DeltaE_hartree':gap,'A_atomic':A,'Gamma_hartree':A,
            'imaginary_potential_hartree':-A/2,'source_equations':[3,5,6,7,8],
            'photon_energy_moment':None,'physical_source_admitted':False,
            'nuclear_repulsion_added_once':True,'Einstein_A_unit':'inverse_atomic_time',
            'Gamma_unit':'Hartree; SI relation Gamma=hbar*A'}


def paper_k2(E_cm_eV, mu_over_me):
    """Historical Eq11 token preserved. No modern-mass convention is inferred."""
    try:
        if isinstance(E_cm_eV,(bool,float)) or isinstance(mu_over_me,(bool,float)):raise ValueError()
        E=Fraction(E_cm_eV); m=Fraction(mu_over_me)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as e:
        raise ContractError('EXACT_POSITIVE_E_AND_MASS_TOKENS_REQUIRED') from e
    if E<=0 or m<=0:raise ContractError('POSITIVE_ENERGY_AND_MASS_REQUIRED')
    q=m*E/Fraction('13.602')
    try:v=float(q)
    except OverflowError as e:raise NumericalFailure('K2_RANGE_ERROR') from e
    if v==0 or not math.isfinite(v):raise NumericalFailure('K2_RANGE_ERROR')
    return {'k2_bohr_inverse_squared':v,'exact_fraction':str(q),'energy_frame':'center_of_mass',
            'conversion':'WEST1982_EQ11_13.602_NOT_MODERN_CONSTANT','mass_was_supplied':True,
            'physical_source_admitted':False}


def radial_input_point(E_hartree, V_hartree, A_atomic, mu_over_me):
    """Map to E0=Eh/(2*mu/me), L=a0; boundary and radial arrays still needed."""
    E=_number(E_hartree,'E_hartree',positive=True);V=_number(V_hartree,'V_hartree')
    A=_number(A_atomic,'A_atomic');mu=_number(mu_over_me,'mu_over_me',positive=True)
    if A<0:raise ContractError('NEGATIVE_WIDTH')
    vals=(2*mu*E,2*mu*V,2*mu*A);_checked(vals,'radial unit map')
    if vals[0]==0 or (V!=0 and vals[1]==0) or (A>0 and vals[2]==0):raise NumericalFailure('RADIAL_MAP_UNDERFLOW')
    return dict(zip(('energy_over_E0','potential_over_E0','width_over_E0'),vals),
                physical_source_admitted=False,outer_boundary_not_specified=True)
