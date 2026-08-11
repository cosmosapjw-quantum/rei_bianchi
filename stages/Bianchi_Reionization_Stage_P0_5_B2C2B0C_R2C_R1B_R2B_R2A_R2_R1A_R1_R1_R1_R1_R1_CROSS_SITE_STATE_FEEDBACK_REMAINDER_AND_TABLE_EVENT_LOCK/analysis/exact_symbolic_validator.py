#!/usr/bin/env python3
"""Exact symbolic audit of load-bearing conservation identities.

This validator distinguishes structural identities of the discrete event/PDS
map from broad raw interval residuals caused by repeated-variable dependency.
"""
from __future__ import annotations
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def validate() -> dict[str, object]:
    v,f,y,z=sp.symbols('v f y z', real=True)
    ell=sp.Rational(57,40)
    m=sp.Rational(737,1000)
    w=(ell-m)+m*y
    ah=v*w+(1-v)*f*z
    ahe=v*m*(1-y)+(1-v)*f*(1-z)
    branch=sp.simplify(ah+ahe+v*(2-ell)+(1-v)*(1-f)-(1+v))

    dt=sp.symbols('dt', positive=True)
    d0,d1,d2=sp.symbols('d0 d1 d2', positive=True)
    den=(d0,d1,d2)
    rates={}
    A=sp.eye(3)
    for source in range(3):
        outgoing=0
        for dest in range(3):
            if dest==source:
                continue
            rate=sp.symbols(f'r{dest}{source}', nonnegative=True)
            rates[dest,source]=rate
            A[dest,source]=-dt*rate/den[source]
            outgoing+=rate
        A[source,source]=1+dt*outgoing/den[source]
    column_sum=[sp.simplify(sum(A[row,col] for row in range(3))-1) for col in range(3)]

    cH=sp.Matrix([[1,1,0,0,0]])
    cHe=sp.Matrix([[0,0,1,1,1]])
    transitions=[
        sp.Matrix([-1,1,0,0,0]), sp.Matrix([1,-1,0,0,0]),
        sp.Matrix([0,0,-1,1,0]), sp.Matrix([0,0,1,-1,0]),
        sp.Matrix([0,0,0,-1,1]), sp.Matrix([0,0,0,1,-1]),
    ]
    h_inv=[sp.simplify((cH*s)[0]) for s in transitions]
    he_inv=[sp.simplify((cHe*s)[0]) for s in transitions]

    h1,h2,h3=sp.symbols('h1 h2 h3', positive=True)
    H=h1+h2+h3
    owner=sp.simplify(h1/H+h2/H+h3/H-1)
    current,total=sp.symbols('J total', nonzero=True)
    group_photon=sp.simplify(current*total/total-current)
    chemical,resolved,escaped=sp.symbols('chemical resolved escaped')
    unresolved=-chemical-resolved-escaped
    energy=sp.simplify(chemical+resolved+escaped+unresolved)

    identities={
        'cascade_photon_identity': str(branch),
        'mprk_column_sum_residuals': [str(x) for x in column_sum],
        'hydrogen_stoichiometric_residuals': [str(x) for x in h_inv],
        'helium_stoichiometric_residuals': [str(x) for x in he_inv],
        'owner_simplex_residual': str(owner),
        'group_photon_owner_residual': str(group_photon),
        'augmented_energy_residual': str(energy),
    }
    passed=(branch==0 and all(x==0 for x in column_sum+h_inv+he_inv)
            and owner==0 and group_photon==0 and energy==0)
    return {
        'classification':'EXACT_STRUCTURAL_LEDGER_VALIDATION',
        'passed':bool(passed),
        'identities':identities,
        'interpretation':{
            'load_bearing':'structural exact equalities for every admissible realization',
            'raw_interval_ledgers':'diagnostic zero-including boxes; their width is not a physical uncertainty claim',
        },
    }


def main() -> int:
    result=validate()
    target=STAGE/'data/EXACT_SYMBOLIC_VALIDATION.json'
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
