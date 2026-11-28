#!/usr/bin/env python3
"""Independent exact algebra for HE-FLRW02; does NOT execute the Rust consumer."""
from __future__ import annotations
import json
from pathlib import Path
import sympy as s


def main() -> None:
    checks: list[dict[str, str]] = []
    witnesses: list[dict[str, str]] = []
    def equal(name: str, expr: s.Expr) -> None:
        value = s.cancel(s.expand(expr))
        if value != 0:
            raise AssertionError((name, value))
        checks.append({'name': name, 'residual': '0'})
    def nonzero(name: str, expr: s.Expr) -> None:
        value = s.factor(expr)
        if value == 0:
            raise AssertionError((name, value))
        witnesses.append({'name': name, 'nonzero_expression': str(value)})

    c, V, lam, nh, ny, dt, q = s.symbols('c V lambda nH nHe dt q', positive=True)
    b = s.symbols('bH bHeI bHeII', positive=True)  # binding energies in erg
    E = s.symbols('E0:3', positive=True)          # photon energies in erg
    N = s.symbols('N0:3', nonnegative=True)       # comoving node counts
    lower = s.symbols('l0:3', nonnegative=True)  # proper absorber density
    sig = s.Matrix(3, 3, lambda a,g: s.Symbol(f'sigma{a}{g}', nonnegative=True))
    A = s.Matrix(3, 3, lambda a,g: c*lower[a]*sig[a,g]*N[g]/V)
    G = [c*sum(sig[a,g]*N[g] for g in range(3))/V for a in range(3)]
    L = c*sum(lower[a]*sig[a,g]*N[g] for a in range(3) for g in range(3))
    H = sum(A[a,g]*(E[g]-b[a]) for a in range(3) for g in range(3))
    B = sum(A[a,g]*b[a] for a in range(3) for g in range(3))
    Q = sum(A[a,g]*E[g] for a in range(3) for g in range(3))
    equal('F01_event_conversion', L - V*sum(A))
    equal('F01_heat_binding', H+B-Q)
    for a in range(3):
        equal(f'F01_species_gamma_{a}', sum(A[a,g] for g in range(3))-lower[a]*G[a])
    # A: same proper state; only comoving representation changes.
    subA = {V: lam**3*V, **{N[g]:lam**3*N[g] for g in range(3)}}
    # B: same comoving nuclear/photon inventories, same fractions and energies.
    subB = {V: lam**3*V, **{lower[a]:lower[a]/lam**3 for a in range(3)}}
    outputs = {'gamma0':G[0], 'events':sum(A), 'heat':H, 'binding':B, 'loss':L}
    for name, value in outputs.items():
        factorA = lam**3 if name == 'loss' else 1
        factorB = lam**-3 if name in ('gamma0','loss') else lam**-6
        equal('same_proper_'+name, value.subs(subA, simultaneous=True)-factorA*value)
        equal('same_comoving_'+name, value.subs(subB, simultaneous=True)-factorB*value)
    p = s.symbols('p0:3', nonnegative=True)
    for a in range(3):
        for g in range(3):
            equal(f'F01_F03_photo_{a}_{g}', A[a,g].subs({N[k]:V*p[k] for k in range(3)}, simultaneous=True)-c*lower[a]*sig[a,g]*p[g])
    C = s.symbols('C0:3', nonnegative=True)
    R = s.symbols('R0:3', nonnegative=True)
    photo = s.symbols('A0:9', nonnegative=True)
    P = s.Matrix(3,3,photo)
    j = [sum(P[a,g] for g in range(3))+C[a]-R[a] for a in range(3)]
    du = sum(P[a,g]*(E[g]-b[a]) for a in range(3) for g in range(3))-sum(C[a]*b[a]+R[a]*q for a in range(3))
    dp = [-sum(P[a,g] for a in range(3)) for g in range(3)]
    escape = sum(R[a]*(b[a]+q) for a in range(3))
    f = s.Matrix([j[0]/nh,(j[1]-j[2])/ny,j[2]/ny,du,*dp])
    wn = s.Matrix([nh,ny,2*ny,0,1,1,1])
    we = s.Matrix([nh*b[0],ny*b[1],ny*(b[1]+b[2]),1,*E])
    equal('F03_electron_photon_RHS', wn.dot(f)-sum(C)+sum(R))
    equal('F03_total_energy_RHS', we.dot(f)+escape)
    r = s.Matrix(s.symbols('r0:7', real=True)); re = s.Symbol('r_escape', real=True)
    delta = dt*f+r
    equal('BE_number_residual_projection', wn.dot(delta)-dt*(sum(C)-sum(R))-wn.dot(r))
    equal('BE_energy_residual_projection', we.dot(delta)+dt*escape+re-we.dot(r)-re)
    # Constructive sharpness of the exact-arithmetic infinity-norm bound.
    eps = s.Symbol('epsilon', positive=True)
    scales = s.Matrix([1,1,1,*s.symbols('su sp0 sp1 sp2', positive=True)])
    se = s.Symbol('s_escape', positive=True)
    equal('number_bound_positive_vertex', wn.dot(eps*scales)-eps*wn.dot(scales))
    equal('energy_bound_positive_vertex', we.dot(eps*scales)+eps*se-eps*(we.dot(scales)+se))
    nonzero('missing_volume_conversion', L-sum(A))
    wrongn = s.Matrix([nh,ny,ny,0,1,1,1])
    nonzero('missing_HeIII_electron_factor', wrongn.dot(f)-sum(C)+sum(R))
    wrongE = s.Matrix([nh*b[0],ny*b[1],ny*b[2],1,*E])
    nonzero('noncumulative_HeIII_binding', wrongE.dot(f)+escape)
    nonzero('same_proper_extra_a_cubed', G[0].subs(subA, simultaneous=True)/lam**3-G[0])
    nonzero('unjustified_number_conservation_with_collisions_recombinations', wn.dot(f))
    # Independently build numerical rational ledgers for each transformed input.
    # These are synthetic arithmetic probes, not fits, Rust, or trajectories.
    def rational_ledger(volume, counts, densities):
        cc = s.Integer(3)
        ss = [[s.Rational(a+g+1,13) for g in range(3)] for a in range(3)]
        gamma = [cc*sum(ss[a][g]*counts[g]/volume for g in range(3)) for a in range(3)]
        events = sum(densities[a]*gamma[a] for a in range(3))
        loss = sum(cc*sum(densities[a]*ss[a][g] for a in range(3))*counts[g] for g in range(3))
        assert loss == volume*events
        return gamma[0], events, loss
    v0 = s.Integer(8)
    counts0 = [s.Rational(g+2,10) for g in range(3)]
    densities0 = [s.Rational(a+1,7) for a in range(3)]
    base = rational_ledger(v0, counts0, densities0)
    grid = []
    for scale in (s.Rational(1,8),s.Rational(1,2),s.Integer(1),s.Integer(3)):
        proper = rational_ledger(v0*scale**3, [x*scale**3 for x in counts0], densities0)
        comoving = rational_ledger(v0*scale**3, counts0, [x/scale**3 for x in densities0])
        proper_ratios = [s.cancel(x/y) for x,y in zip(proper,base)]
        comoving_ratios = [s.cancel(x/y) for x,y in zip(comoving,base)]
        assert proper_ratios == [1,1,scale**3]
        assert comoving_ratios == [scale**-3,scale**-6,scale**-3]
        grid.append({'lambda':str(scale),'output_order':['gamma_HI','events','comoving_loss'],
                     'baseline_values':[str(x) for x in base],
                     'same_proper_ratios':[str(x) for x in proper_ratios],
                     'same_comoving_ratios':[str(x) for x in comoving_ratios],
                     'event_residual':'0'})
    result={'task':'HE-FLRW02A','status':'EXACT_ALGEBRA_PASS','symbolic_identity_count':len(checks),'nonzero_witness_count':len(witnesses),'rational_probe_count':len(grid),'identities':checks,'mutation_witnesses':witnesses,'rational_probes':grid,'rust_runs':0,'physical_fit_evaluations':0,'history_runs':0,'independent_scientific_review':'NOT_RUN','claim_ceiling':'conditional exact event/residual algebra only; no rounded interval certificate'}
    out=Path(__file__).resolve().parent/'evidence/RESULTS.json'; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','symbolic_identity_count','nonzero_witness_count','rational_probe_count','rust_runs','physical_fit_evaluations','history_runs')},indent=2))

if __name__ == '__main__':
    main()
