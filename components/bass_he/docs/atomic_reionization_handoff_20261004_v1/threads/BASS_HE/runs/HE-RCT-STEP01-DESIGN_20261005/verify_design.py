#!/usr/bin/env python3
"""Exact algebra and rational examples for a proposed RCT step design.

This does not import, modify, compile or execute rei_microphysics. It verifies
specified mathematical identities, not native integration or atomic accuracy.
"""
from __future__ import annotations
import hashlib
import json
import platform
import sys
from pathlib import Path
import sympy as S

ROOT = Path(__file__).resolve().parent

def main() -> None:
    proofs: list[dict] = []
    examples: list[dict] = []
    mutations: list[dict] = []

    def identity(label: str, residual) -> None:
        if isinstance(residual, S.MatrixBase):
            flat = list(residual)
        elif isinstance(residual, (list, tuple)):
            flat = list(residual)
        else:
            flat = [residual]
        values = [S.factor(S.cancel(e)) for e in flat]
        if any(v != 0 for v in values):
            raise AssertionError((label, values))
        proofs.append({"name": label, "scalar_components": len(values), "residual": "0"})

    f,n,k,dt = S.symbols('f n k dt', positive=True)
    x,y,z,w,p0,p1,p2 = u = S.symbols('x y z w p0 p1 p2', real=True)
    Q,E,chiH,chi1,chi2 = S.symbols('Q E chiH chi1 chi2', positive=True)
    g = Q-E
    kap = k*n*f
    rate = kap*(1-x)*z
    v = S.Matrix([1,1/f,-1/f,g,0,0,0])
    rhs = v*rate
    grad = S.Matrix([S.diff(rate, a) for a in u])
    jac = rhs.jacobian(S.Matrix(u))
    identity('normalized_Jacobian_outer_product', jac-v*grad.T)
    eigen = -k*n*((1-x)+f*z)
    identity('nonzero_Jacobian_eigenvalue', (grad.T*v)[0]-eigen)
    identity('rank_one_square_identity', jac*jac-eigen*jac)
    electron = S.Matrix([1,f,2*f,0,0,0,0])
    identity('free_electron_RCT_derivative', electron.dot(rhs))
    helium_non_neutral = S.Matrix([0,1,1,0,0,0,0])
    identity('HeII_plus_HeIII_RCT_derivative', helium_non_neutral.dot(rhs))
    chemical = S.Matrix([chiH,f*chi1,f*(chi1+chi2),0,0,0,0])
    identity('chemical_thermal_escape_ownership',
             (chemical.dot(rhs)+rhs[3]+E*rate).subs(Q,chi2-chiH))
    beta = S.symbols('beta', positive=True)  # 2 eV_erg/(3 k_B)
    particles = 1+f+x+f*(y+2*z)
    temperature = beta*w/particles
    identity('RCT_keeps_particle_count', S.Matrix([S.diff(particles,a) for a in u]).dot(v))
    identity('RCT_temperature_direction', S.Matrix([S.diff(temperature,a) for a in u]).dot(v)-beta*g/particles)
    dx,dy,dz,dw,dp0,dp1,dp2 = du = S.symbols('dx dy dz dw dp0 dp1 dp2',real=True)
    shifted = rhs.subs(dict(zip(u,[a+b for a,b in zip(u,du)])), simultaneous=True)
    identity('exact_bilinear_Taylor_remainder', shifted-rhs-jac*S.Matrix(du)+kap*dx*dz*v)
    identity('mixed_Hessian_entries', [S.diff(rhs[i],x,z)+kap*v[i] for i in range(7)])
    identity('all_third_derivatives_zero', [S.diff(rhs[i],x,z,z) for i in range(7)])

    # Positive birth/death block, with dimensionless a,b,c,d = dt * rates.
    x0,y0,z0 = S.symbols('x0 y0 z0',nonnegative=True)
    I,R = S.symbols('I R',nonnegative=True)
    xg,zg = S.symbols('xg zg',real=True)
    aa,bb,cc,dd = S.symbols('a b c d',nonnegative=True)
    yp = (y0+(1-y0-z0)*aa/(1+aa)+z0*dd/(1+dd))/(1+bb/(1+aa)+cc/(1+dd))
    zp = (z0+cc*yp)/(1+dd)
    he0p = 1-yp-zp
    identity('positive_He_block_HeI_equation', he0p-(1-y0-z0)+aa*he0p-bb*yp)
    identity('positive_He_block_HeII_equation', yp-y0-aa*he0p+(bb+cc)*yp-dd*zp)
    identity('positive_He_block_HeIII_equation', zp-z0-cc*yp+dd*zp)
    identity('HeI_positive_reconstruction',he0p-((1-y0-z0)+bb*yp)/(1+aa))
    xp=(x0+dt*(I+k*n*f*zg))/(1+dt*(I+k*n*f*zg+R))
    identity('H_candidate_residual_against_new_z',
             xp-x0-dt*((1-xp)*(I+k*n*f*z)-R*xp)-dt*k*n*f*(1-xp)*(zg-z))
    identity('H_candidate_positive_HI_reconstruction',1-xp-(1-x0+dt*R)/(1+dt*(I+k*n*f*zg+R)))
    # With final populations denoted x,y,z, cross-freezing defects are exact.
    rx = dt*k*n*f*(1-x)*(zg-z)
    ry = dt*k*n*z*(x-xg)
    rz = -ry
    JH=dt*k*n*f*zg*(1-x)
    JHe=dt*k*n*f*(1-xg)*z
    identity('candidate_electron_defect_matches_mismatched_counts',rx+f*(ry+2*rz)-(JH-JHe))
    identity('cross_freezing_defects_vanish_at_fixed_point',S.Matrix([rx,ry,rz]).subs({xg:x,zg:z}))

    # Reaction ledger, all integrated counts measured per H nucleus here.
    H,HeI,HeII,J = S.symbols('H HeI HeII J',real=True)
    delta=S.Matrix([H+J,(HeI-HeII+J)/f,(HeII-J)/f,0,0,0,0])
    identity('accepted_ledger_electron_projection',electron.dot(delta)-H-HeI-HeII)
    J1,J2,E1,E2 = S.symbols('J1 J2 E1 E2',nonnegative=True)
    identity('stage_energy_moments_cancel',-Q*(J1+J2)+(Q-E1)*J1+(Q-E2)*J2+E1*J1+E2*J2)
    wrong_final_only = E2*(J1+J2)-(E1*J1+E2*J2)
    identity('final_mean_energy_mutant_exact_error',wrong_final_only-(E2-E1)*J1)
    # Isolated cross-frozen mapping has a locally attracting fixed point.
    a,b=S.symbols('alpha beta_step',positive=True)
    mapx=(x0+a*z)/(1+a*z)
    mapz=z0/(1+b*(1-x))
    product=S.diff(mapx,z)*S.diff(mapz,x)
    atroot=product.subs({x0:x-a*z*(1-x),z0:z*(1+b*(1-x))}, simultaneous=True)
    identity('isolated_Picard_spectral_radius_squared',atroot-a*z*b*(1-x)/((1+a*z)*(1+b*(1-x))))
    # The source x,z domain makes the 7-state RCT field rank <= 1.
    exact_sub={f:S.Rational(83,1000),n:S.Rational(1,10000),k:S.Rational(1,10**14),x:S.Rational(9,10),y:S.Rational(3,10),z:S.Rational(3,5),Q:S.Rational(40819325400298,10**12),E:S.Rational(39819325400298,10**12)}
    jr=jac.subs(exact_sub)
    if jr.rank()!=1: raise AssertionError('rank')
    examples.append({'name':'actual_constant_projection_rank','rank':jr.rank(),
                     'j_per_H_per_s':str(rate.subs(exact_sub)),
                     'nonzero_eigenvalue_per_s':str(eigen.subs(exact_sub)),
                     'input_kind':'exact decimal lift of pinned model/scenario constants; not native execution'})
    # Rational positive block examples at vertices/interior, no floating arithmetic.
    old_rows=[(S.Rational(0),S.Rational(0)),(S.Rational(1),S.Rational(0)),(S.Rational(0),S.Rational(1)),(S.Rational(1,5),S.Rational(3,10))]
    coefficients=[(0,0,0,0),(S.Rational(1,10),S.Rational(1,7),S.Rational(1,3),S.Rational(1,11)),(10,100,1000,10000)]
    for yi,zi in old_rows:
        for av,bv,cv,dv in coefficients:
            subs={y0:yi,z0:zi,aa:av,bb:bv,cc:cv,dd:dv}
            row=[S.cancel(q.subs(subs)) for q in (he0p,yp,zp)]
            if min(row)<0 or sum(row)!=1: raise AssertionError((subs,row))
            examples.append({'name':'positive_helium_block','old':[str(1-yi-zi),str(yi),str(zi)],'coefficients':list(map(str,(av,bv,cv,dv))),'new':list(map(str,row)),'sum':'1'})
    # Sherman-Morrison solve, derived by direct substitution, not actual FT03 Jacobian.
    vv=S.Matrix([1,2,-2,1,0,0,0]); gg=S.Matrix([-S.Rational(1,4),0,S.Rational(1,3),0,0,0,0])
    for step in (S.Rational(0),S.Rational(1,10),S.Rational(2)):
        A0=S.diag(*range(2,9)); A0[0,3]=S.Rational(1,5); A0[4,1]=S.Rational(1,7)
        bbv=S.Matrix(range(1,8))
        sv=A0.inv()*vv; sb=A0.inv()*bbv
        denominator=1-step*gg.dot(sv)
        proposed=sb+step*sv*gg.dot(sb)/denominator
        direct=(A0-step*vv*gg.T).inv()*bbv
        if proposed!=direct: raise AssertionError('low rank solve')
        examples.append({'name':'rank_one_dense_solve','dt':str(step),'denominator':str(denominator),'residual':'0','baseline_kind':'synthetic rational matrix, NOT actual FT03 derivative'})
    # Invertibility of A0 and decay of isolated RCT do NOT ensure safe update.
    A0=S.Matrix([[1,-4],[0,1]]); v2=S.Matrix([1,-1]); g2=S.Matrix([-S.Rational(1,2),S.Rational(1,2)])
    D=1-g2.dot(A0.inv()*v2); A=A0-v2*g2.T
    if A0.det()!=1 or D!=0 or A.det()!=0: raise AssertionError('singular witness')
    mutations.append({'name':'unguarded_low_rank_denominator','baseline':str(A0),'baseline_determinant':'1','RCT_nonzero_eigenvalue':str(g2.dot(v2)),'denominator':str(D),'updated_determinant':str(A.det()),'interpretation':'synthetic counterexample, not observed FT03 failure'})
    # RHS-only replacement leaves old isolated block at old state forever.
    f0=S.Rational(83,1000); oldx=S.Rational(9,10); oldz=S.Rational(3,5)
    j0=f0*(1-oldx)*oldz  # normalized dt*k*nH=1, not a physical proposed run
    frozen=S.Matrix([-j0,-j0/f0,j0/f0])
    mutations.append({'name':'replace_residual_but_leave_old_block','normalized_dt_k_nH':'1','residual_xyz':list(map(str,frozen)),'all_zero':False,'interpretation':'isolated frozen block mathematical counterexample'})
    # At a synthetic intermediate iterate, ledger conservation is not guaranteed.
    sub2={dt:1,k:1,n:1,f:f0,x:S.Rational(4,5),z:S.Rational(1,2),xg:oldx,zg:oldz}
    mismatch=S.cancel((JH-JHe).subs(sub2))
    if mismatch==0: raise AssertionError('ledger witness')
    mutations.append({'name':'accept_trial_cross_frozen_counts','JH_minus_JHe':str(mismatch),'interpretation':'iteration counts must not be accepted event ledger'})
    if S.simplify(wrong_final_only)==0: raise AssertionError('moment witness')
    mutations.append({'name':'last_stage_energy_times_total_count','error':str(S.factor(wrong_final_only)),'interpretation':'only vanishes for equal Ebar or no earlier events'})
    # Exact affine temperature/fraction feasibility along a Newton direction.
    beta0=S.Rational(10000); Tlo=S.Rational(30000); Thi=S.Rational(110000)
    U=S.Matrix([S.Rational(9,10),S.Rational(3,10),S.Rational(3,5),0,S.Rational(1,20),S.Rational(1,200),S.Rational(1,1000)])
    s0=particles.subs(dict(zip(u,U))).subs(f,f0); U[3]=S.Rational(50000)*s0/beta0
    direction=S.Matrix([S.Rational(1,5),0,0,-10,-S.Rational(1,10),0,0])
    def barriers(UU):
        xx,yy,zz,ww,pp0,pp1,pp2=UU
        ss=1+f0+xx+f0*(yy+2*zz)
        return S.Matrix([xx,1-xx,yy,zz,1-yy-zz,ww,pp0,pp1,pp2,beta0*ww-Tlo*ss,Thi*ss-beta0*ww])
    c0=barriers(U); slope=barriers(U+direction)-c0
    caps=[S.cancel(-a/b) for a,b in zip(c0,slope) if b<0]
    cap=min([S.Rational(1),*caps])
    if min(barriers(U+cap*direction))<0 or min(barriers(U+(cap+S.Rational(1,100))*direction))>=0: raise AssertionError('affine barrier')
    examples.append({'name':'affine_temperature_and_species_line_search','alpha_max':str(cap),'min_at_boundary':str(min(barriers(U+cap*direction))),'min_beyond':str(min(barriers(U+(cap+S.Rational(1,100))*direction))),'interpretation':'candidate domain only, not exact-time flow certificate'})
    # Stiff isolated iteration can be arbitrarily slow despite rho < 1.
    for ab in (S.Rational(1),S.Rational(10),S.Rational(10000)):
        rho2=ab*ab/((1+ab)*(1+ab))
        if not 0<rho2<1: raise AssertionError('rho')
        examples.append({'name':'isolated_contraction_not_uniform','alpha_z_and_beta_HI':str(ab),'rho':str(ab/(1+ab))})
    result={
        'task':'HE-RCT-STEP01-DESIGN','status':'EXACT_ALGEBRA_AND_RATIONAL_EXAMPLES_PASS',
        'symbolic_identity_groups':len(proofs),'symbolic_scalar_components':sum(p['scalar_components'] for p in proofs),
        'rational_examples':len(examples),'nonzero_or_singular_controls':len(mutations),
        'proofs':proofs,'examples':examples,'controls':mutations,
        'new_native_runs':0,'actual_stepper_implementation':False,'actual_FT03_Jacobian_evaluations':0,
        'atomic_rate_evaluations':0,'coupled_histories':0,'physical_admission':False,
        'independent_scientific_review':'NOT_RUN',
        'claim_ceiling':'exact mathematical identities under recorded fixed-k/fixed-Ebar model and rational synthetic cases; no native or interval validation',
        'python':sys.version,'sympy':S.__version__,'platform':platform.platform(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'evidence'/'DESIGN_RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({key:result[key] for key in ('status','symbolic_identity_groups','symbolic_scalar_components','rational_examples','nonzero_or_singular_controls','new_native_runs','actual_stepper_implementation')},indent=2))

if __name__=='__main__':
    main()
