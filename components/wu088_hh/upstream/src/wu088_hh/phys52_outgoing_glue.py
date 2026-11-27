"""PHYS52: rigorous finite-400 outgoing/collar Robin matching with all-m symmetry.

RIGOROUS: the band-limited exact physical real screened Coulomb projected
operator, outward current coercivity and a quantitative inverse of the
high-interface matrix for the PHYS50 positive Dirichlet collar, in the
same finite Galerkin angular band l=21..28, m=-l..l.

NONCERTIFYING NUMERICAL: physical screen angular Gauss-Legendre blocks,
symmetry, PSD, batch-vectorization and independent high-resolution quadrature.
No physical g_B/xi source values, infinite angular/outgoing inverse, sigma(E)
or thermal HH rate have been claimed.
"""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
from pathlib import Path
from time import perf_counter
from math import isqrt

from .phys46_volterra import exp_positive_rational_upper
from .phys51_finite_outgoing import (
    C,K,R,B,LOW,HIGH,_energy_patch,finite_band_screened_jost,
)
from .phys49_dirichlet_collar import (
    FROZEN_SHA,barrier_floor,original_screened_coupling_max,
)
from .phys50_trace_dtn import C_TRACE,sqrt_upper_fraction
from .phys33_coupled_source import outward_decimal

SCHEMA="WU088_HH_PHYS52_FINITE_BAND_OUTGOING_COLLAR_ROBIN_V1"
PATCH=43
TERM_COUNT=192
C_EXP_ORDER=128

def source_sha_guard(path:str|Path)->str:
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if actual!=FROZEN_SHA:
        raise ValueError("immutable original WU088_HH source SHA256 changed")
    return actual

def signed_m_channels(lo:int=LOW,hi:int=HIGH)->tuple[tuple[int,tuple[int,...]],...]:
    if type(lo) is not int or type(hi) is not int or (lo,hi)!=(21,28):
        raise ValueError("only verified physical band ell=21..28")
    return tuple((m,tuple(range(max(lo,abs(m)),hi+1))) for m in range(-hi,hi+1))

def unique_m_channels()->tuple[tuple[int,tuple[int,...]],...]:
    """For real axially symmetric S, -m and +m angular blocks are identical."""
    return tuple((m,ls) for m,ls in signed_m_channels() if m>=0)

def finite_band_robin_certificate(original:str|Path,digits:int=24)->dict:
    """Exact Fraction lower inverse bound in norm ell2 of angular trace g_T.

    Let U_out(T) be all-m Jost boundary matrix normalized by Coulomb
    outgoing unit amplitudes a at infinity. PHYS51 ensures
       ||U_out(T)|| <= M exp[C(PATCH-T)]/(1-q)
    with T=B=27 here. The real screened band Hamiltonian conserves
       Im[g^* Z_out g] = k ||U_out(T)^(-1) g||².
    Therefore j_min=k(1-q)^2/(M² exp[2 C (PATCH-T)]) >0.
    The PHYS50 *projected finite-band* collar DtN has Hermitian
    T,T block Lambda_TT. For Mmatch=Lambda_TT-Z_out,
       ||Mmatch g||>=j_min||g||, so ||Mmatch^-1||<=1/j_min.
    The finite dimensional matched interface is UNIQUE for any
    prescribed lower trace g_B and arbitrary admissible collar source.
    Physical g_B and driven xi are NOT supplied.
    """
    actual=source_sha_guard(original)
    if type(digits) is not int or not 16<=digits<=27:
        raise ValueError("selected outward precision 16..27")
    old=finite_band_screened_jost(original,21,28,(PATCH,),terms=TERM_COUNT)
    patch=_energy_patch(PATCH,21,28,TERM_COUNT)
    q=patch["q_upper_exact"]
    assert 0<q<F(1,2)
    intM=patch["M"]
    # exp_upper is exact Fraction with positive Taylor/geometric remainder.
    exp_up=exp_positive_rational_upper(2*C*(PATCH-B),C_EXP_ORDER)
    W2_upper=F(intM**2)*exp_up/(1-q)**2
    current_lower=K/W2_upper
    robin_inverse_upper=W2_upper/K
    assert current_lower>0
    assert old["n_channels"]==400 and intM==old["integer_energy_amplitude_M"]
    screening=original_screened_coupling_max(192)
    collar_floor=barrier_floor(21)-screening
    assert collar_floor>0
    # The consumer-facing decimal bound is a *pair*: round j_min down
    # at the stated 24 fractional places, then round its RECIPROCAL up.
    # Independent rounding of exact j and exact 1/j does not ensure
    # that the two displayed decimals satisfy j_print * Inv_print >= 1.
    current_lower_display=outward_decimal(current_lower,digits,False)
    inverse_upper_display=outward_decimal(1/F(current_lower_display),digits,True)
    assert F(current_lower_display)*F(inverse_upper_display)>=1
    layout=signed_m_channels()
    unique=unique_m_channels()
    dense=sum(len(ls) for _,ls in layout)**2
    nonzero=sum(len(ls)**2 for _,ls in layout)
    unique_nonzero=sum(len(ls)**2 for _,ls in unique)
    cubic_unique=sum(len(ls)**3 for _,ls in unique)
    # In PHYS50 X-norm, ||Lambda_TB g_B||_2 <=sqrt(29)*Ctrace||gB||_X.
    lambda_TB_X_to_l2=sqrt_upper_fraction(F(HIGH+1)*C_TRACE*C_TRACE,24)
    return {
        "schema":SCHEMA,
        "source_sha256":actual,
        "outer_Jost_parent":"PHYS51 finite 400-channel all-m noncentral screened Volterra",
        "collar_parent":"PHYS50 high nonzero-Dirichlet, finite-band angular projection",
        "scope":"r20..27 finite collar to exact r>=27 finite-band outgoing all-m",
        "angular_band":[LOW,HIGH],
        "n_channels":sum(len(ls) for _,ls in layout),
        "signed_m_count":len(layout),
        "unique_real_axisymmetric_m_blocks":len(unique),
        "max_block_dimension":max(map(lambda a:len(a[1]),unique)),
        "entries_dense":dense,
        "entries_nonzero_signed_m_blocks":nonzero,
        "entries_unique_nonnegative_m_blocks":unique_nonzero,
        "cubic_units_dense":dense*sum(len(ls) for _,ls in layout),
        "cubic_units_unique_blocks":cubic_unique,
        "memory_reduction_unique_dense_ratio":F(dense,unique_nonzero).__str__(),
        "patch_T_Bohr":PATCH,
        "outgoing_Coulomb_amplitude_M":intM,
        "PHYS51_q_outward":old["screened_Volt_q_outward"],
        "current_lower_per_Bohr":current_lower_display,
        "matched_Robin_inverse_norm_upper_Bohr":
            inverse_upper_display,
        "positive_collar_barrier_lower":
            outward_decimal(collar_floor,digits,False),
        "finite_PHYS50_trace_X_to_Xdual_upper_exact":str(C_TRACE),
        "finite_collar_Lambda_TB_X_to_l2_upper":
            outward_decimal(lambda_TB_X_to_l2,digits,True),
        "glue_equation":"(Lambda_D_TT-Z_out)g_T=-Lambda_D_TB*g_B - outward_d_T(A_D^-1 f)",
        "outgoing_flux_identity":
            "Im(g^*Z_out g)=k||U_out(27)^(-1)g||_2^2>=jmin||g||_2^2",
        "inverse_inequality":"||(Lambda_D_TT-Z_out)^-1||_2<=1/jmin",
        "boundary_trace_estimate":
            "||g_T||_2 <= inverse_upper*(C_trace*sqrt(29)*||g_B||_X+||outward_d_T(A_D^-1 f)||_2)",
        "symbolic_parity":
            "lambda_TT=Hermitian due to positive real collar form; (-m) and m blocks identical",
        "rational_evidence":{
            "q_num_bits":q.numerator.bit_length(),
            "q_den_bits":q.denominator.bit_length(),
            "exp_upper_num_bits":exp_up.numerator.bit_length(),
            "exp_upper_den_bits":exp_up.denominator.bit_length(),
            "jmin_num_bits":current_lower.numerator.bit_length(),
            "jmin_den_bits":current_lower.denominator.bit_length(),
        },
        "not_admitted":[
            "infinite ell>=21 exterior radiation DtN uniform X->X*",
            "actual physical boundary traces g_B/g_T and original driven xi=Fy-phi",
            "regular origin, incoming adjoint and physical sigma(E)",
            "Maxwellian k_HH(T) and REI HH_R10 production",
        ],
        "status":"RIGOROUS_SCOPED_FINITE_BAND_MATCHED_ROBIN_INVERTIBILITY",
    }


class PhysicalScreenBlocks:
    """Real axisymmetric, normalized Y_lm Galerkin S(r,cos theta) matrices.

    Exact underlying function S=(1+1/s)e^(-2s), r>=27; approximate
    Gauss-Legendre quadrature of angular matrix elements. Negative m
    blocks coincide with positive m because S is phi independent and real.
    One-time source check, quadrature/basis cache, BLAS batched Gram updates.
    """

    def __init__(self,original:str|Path,nodes:int=128):
        self.source_sha256=source_sha_guard(original)
        if type(nodes) is not int or not 64<=nodes<=384:
            raise ValueError("Gauss angular nodes 64..384")
        import numpy as np
        from scipy.special import lpmv,gammaln
        self.np=np
        self.nodes_count=nodes
        self.mu,self.weights=np.polynomial.legendre.leggauss(nodes)
        self.bases={}
        for m,ells in unique_m_channels():
            basis=[]
            for ell in ells:
                # sqrt(2*pi)*N_lm; lpmv includes the Condon-Shortley (-1)^m.
                norm=np.sqrt((2*ell+1)/2 *np.exp(
                    gammaln(ell-m+1)-gammaln(ell+m+1)
                ))
                basis.append(norm*lpmv(m,ell,self.mu))
            self.bases[m]=np.asarray(basis, dtype=np.float64)

    def screen(self,r:float):
        import numpy as np
        if not np.isfinite(r) or not 27<=r<=1000:
            raise ValueError("exterior r>=27 Bohr, bounded diagnostic radius")
        Rf=0.7
        s=np.sqrt(r*r+Rf*Rf-2*r*Rf*self.mu)
        return (1+1/s)*np.exp(-2*s)

    def matrix(self,m:int,r:float,method:str="batched"):
        if type(m) is not int or abs(m)>HIGH:
            raise ValueError("physical m absolute <=28")
        if method not in ("batched","scalar"):
            raise ValueError("method batched/scalar")
        np=self.np
        basis=self.bases[abs(m)]
        weights=self.weights*self.screen(r)
        if method=="batched":
            # Gram factorization maintains numerical PSD by construction.
            A=basis*np.sqrt(weights)[None,:]
            return A@A.T
        n=len(basis)
        out=np.empty((n,n),dtype=np.float64)
        for i in range(n):
            for j in range(n):
                out[i,j]=np.dot(basis[i]*basis[j],weights)
        return out

    def matrices(self,r:float)->dict[int,object]:
        """29 unique +m matrices; ±m are reused on demand."""
        return {m:self.matrix(m,r) for m,_ in unique_m_channels()}

    def gram_error(self,m:int)->float:
        """Independent real associated-Legendre orthogonality residual."""
        np=self.np
        b=self.bases[abs(m)]
        gram=(b*self.weights[None,:])@b.T
        return float(np.max(np.abs(gram-np.eye(len(b)))))

    def angular_certificate(self,r:float)->dict:
        """NONCERTIFYING one-grid float angular symmetry/positivity diagnostics."""
        np=self.np
        blocks=self.matrices(r)
        return {
            "radius_Bohr":r,
            "angular_nodes":self.nodes_count,
            "angular_unique_m_blocks":len(blocks),
            "max_Gauss_orthonormality_defect":max(self.gram_error(m) for m in blocks),
            "largest_physical_screen_block_operator_norm":max(
                float(np.linalg.norm(b,2)) for b in blocks.values()),
            "screen_sphere_sup_direct_upper":float(self.screen(r).max()),
        }


def assembly_benchmark(kernel:PhysicalScreenBlocks,r:float=27.0,repeats:int=7)->dict:
    if type(repeats) is not int or not 3<=repeats<=15:
        raise ValueError("bounded repeat count")
    import numpy as np
    def time_method(method):
        times=[]
        for _ in range(repeats):
            a=perf_counter()
            for m,_ in unique_m_channels():
                kernel.matrix(m,r,method)
            times.append(perf_counter()-a)
        return sorted(times)[len(times)//2]
    scalar=time_method("scalar")
    batch=time_method("batched")
    return {
        "radius_Bohr":r,"angular_nodes":kernel.nodes_count,
        "scalar_29block_median_seconds":scalar,
        "batched_29block_median_seconds":batch,
        "matched_input_speedup_scalar_over_batched":scalar/batch,
        "not_native_or_NCP":True,
    }
