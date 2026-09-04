#!/usr/bin/env python3
"""Independent 4D constraint-sign research oracle; never a production runtime.

Spatial frame primitives come from the unmodified M1 oracle. Four-dimensional
curvature is constructed from the connection, not from Gauss/Codazzi candidate
formulas. A second route differentiates a coordinate metric germ independently.
Time is s=c*t, so all connection coefficients have units of inverse length.
"""
from __future__ import annotations

import argparse
import csv
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
M1_PATH = HERE.parent / "rei_math_m1_generic_background/derive_spatial_curvature.py"


def _m1():
    spec = importlib.util.spec_from_file_location("rei_m1_spatial", M1_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("M1_ORACLE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cube(size: int):
    return [[[sp.S.Zero for _ in range(size)] for _ in range(size)] for _ in range(size)]


def _symmetric(symbols):
    a, b, c, d, e, f = symbols
    return sp.Matrix([[a, d, e], [d, b, f], [e, f, c]])


@lru_cache(maxsize=1)
def derive() -> dict[str, Any]:
    m1 = _m1()
    spatial = m1._derived_objects()
    a, n, sigma = spatial["a"], spatial["n"], spatial["sigma"]
    C3, g3 = spatial["C"], spatial["gamma"]
    H = sp.Symbol("Hgeom", real=True)
    K = H*sp.eye(3) + sigma
    K_symbols = [H] + sorted(sigma.free_symbols, key=str)
    Q_symbols = list(sp.symbols("Q11 Q22 Q33 Q12 Q13 Q23", real=True))
    Q = _symmetric(Q_symbols)
    spatial_vars = spatial["polynomial_variables"]
    adot = -K*a
    ndot = K*n+n*K-sp.trace(K)*n
    rates = {a[i]: adot[i] for i in range(3)}
    rates.update({n[i,j]: ndot[i,j] for i in range(3) for j in range(i,3)})
    gamma, dg0, C = _cube(4), _cube(4), _cube(4)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                gamma[k+1][j+1][i+1] = g3[k][j][i]
                dg0[k+1][j+1][i+1] = sp.expand(sum(sp.diff(g3[k][j][i],v)*rates[v] for v in spatial_vars))
                C[k+1][i+1][j+1] = C3[k][i][j]
            gamma[0][j+1][i+1] = K[i,j]
            gamma[j+1][0][i+1] = K[j,i]
            dg0[0][j+1][i+1] = Q[i,j]
            dg0[j+1][0][i+1] = Q[j,i]
            C[j+1][0][i+1] = -K[j,i]
            C[j+1][i+1][0] = K[j,i]
    signs = [-1, 1, 1, 1]
    eta = sp.diag(*signs)
    basis = sp.groebner(spatial["jacobi"], *spatial_vars,
                       domain=sp.QQ.frac_field(*(K_symbols+Q_symbols)), order="grevlex")

    def reduce(expr):
        expanded = sp.expand(expr)
        return sp.expand(basis.reduce(expanded)[1]) if expanded != 0 else sp.S.Zero

    @lru_cache(maxsize=None)
    def R(up, vec, left, right):
        temporal = (dg0[up][vec][right] if left == 0 else 0)-(dg0[up][vec][left] if right == 0 else 0)
        return sp.expand(temporal + sum(
            gamma[m][vec][right]*gamma[up][m][left]
            -gamma[m][vec][left]*gamma[up][m][right]
            -C[m][left][right]*gamma[up][vec][m] for m in range(4)))

    def D(i,j,k,l):
        return signs[l]*R(l,k,i,j)

    def O(i,j,k,l):
        return D(k,l,j,i)

    def D3(i,j,k,l):
        return sp.expand(sum(g3[m][k][j]*g3[l][m][i]-g3[m][k][i]*g3[l][m][j]-C3[m][i][j]*g3[l][k][m] for m in range(3)))

    def DK(i,j,k):
        return sp.expand(-sum(g3[m][j][i]*K[m,k]+g3[m][k][i]*K[j,m] for m in range(3)))

    Ricci = sp.Matrix(4,4,lambda c,b: reduce(sum(R(i,c,i,b) for i in range(4))))
    scalar = sp.expand(sum(signs[i]*Ricci[i,i] for i in range(4)))
    G = (Ricci-scalar*eta/2).applyfunc(sp.expand)
    rho, p, Lambda, kappa = sp.symbols("rho p Lambda kappa_G", real=True)
    q = sp.Matrix(sp.symbols("q1 q2 q3", real=True))
    T = sp.diag(rho,p,p,p)
    for i in range(3):
        T[0,i+1] = T[i+1,0] = -q[i]
    E = (G+Lambda*eta-kappa*T).applyfunc(sp.expand)
    divK = m1._divergence_from_connection(g3,K)
    gauss, codazzi, out_gauss, out_codazzi = [], [], [], []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                codazzi.append(reduce(D(i+1,j+1,k+1,0)+DK(i,j,k)-DK(j,i,k)))
                out_codazzi.append(reduce(O(i+1,j+1,k+1,0)-DK(i,j,k)+DK(j,i,k)))
                for l in range(3):
                    gauss.append(reduce(D(i+1,j+1,k+1,l+1)-D3(i,j,k,l)-K[i,l]*K[j,k]+K[i,k]*K[j,l]))
                    out_gauss.append(reduce(O(i+1,j+1,k+1,l+1)-D3(k,l,j,i)-K[i,k]*K[j,l]+K[i,l]*K[j,k]))
    adapter = [reduce(sum(signs[a]*O(a,b,a,d) for a in range(4))-Ricci[b,d]) for b in range(4) for d in range(4)]
    torsion = [sp.expand(gamma[d][b][a]-gamma[d][a][b]-C[d][a][b]) for d in range(4) for a in range(4) for b in range(4)]
    metric = [sp.expand(signs[d]*gamma[d][b][a]+signs[b]*gamma[b][d][a]) for d in range(4) for a in range(4) for b in range(4)]
    jacobi_rate = (ndot*a+n*adot-(K-sp.trace(K)*sp.eye(3))*n*a).applyfunc(sp.expand)
    return {"a":a,"n":n,"sigma":sigma,"H":H,"K":K,"Kdot":Q_symbols,
            "K_symbols":K_symbols,"weight1_symbols":list(spatial_vars)+K_symbols,
            "Ricci":Ricci,"G":G,"E":E,"R3":spatial["scalar"],"divK":divK,
            "Lambda":Lambda,"kappa":kappa,"rho":rho,"q":q,
            "gauss_residuals":gauss,"codazzi_residuals":codazzi,
            "adapter_residuals":adapter,"output_gauss_residuals":out_gauss,
            "output_codazzi_residuals":out_codazzi,"torsion_residuals":torsion,
            "metric_residuals":metric,"jacobi_rate_residuals":list(jacobi_rate)}


@lru_cache(maxsize=1)
def coordinate_witness() -> dict[str, Any]:
    # Independent metric differentiation, without ONF connection or constraint rules.
    s,x,y,z = sp.symbols("s x y z", real=True)
    A = sp.Symbol("A", real=True)
    coords = [s,x,y,z]
    origin = dict.fromkeys(coords,sp.S.Zero)
    ks = list(sp.symbols("k11 k22 k33 k12 k13 k23", real=True))
    K = _symmetric(ks)
    F = sp.diag(1,sp.exp(-A*x),sp.exp(-A*x))
    h = F*(sp.eye(3)+2*s*K)*F
    metric = sp.diag(-1,h)
    eta = sp.diag(-1,1,1,1)
    dg = [metric.diff(t).subs(origin) for t in coords]
    ddg = [[metric.diff(t,u).subs(origin) for u in coords] for t in coords]
    dinv = [-eta*d*eta for d in dg]

    def connection(a,b,c):
        return sp.expand(sum(eta[a,d]*(dg[b][d,c]+dg[c][d,b]-dg[d][b,c])/2 for d in range(4)))

    def derivative(mu,a,b,c):
        return sp.expand(sum((dinv[mu][a,d]*(dg[b][d,c]+dg[c][d,b]-dg[d][b,c])
            +eta[a,d]*(ddg[mu][b][d,c]+ddg[mu][c][d,b]-ddg[mu][d][b,c]))/2 for d in range(4)))

    gamma = [[[connection(a,b,c) for c in range(4)] for b in range(4)] for a in range(4)]
    ric = sp.Matrix(4,4,lambda b,d: sp.expand(sum(
        derivative(a,a,d,b)-derivative(d,a,a,b)
        +sum(gamma[a][a][m]*gamma[m][d][b]-gamma[a][d][m]*gamma[m][a][b] for m in range(4)) for a in range(4))))
    scalar = sp.trace(eta*ric)
    G = (ric-scalar*eta/2).applyfunc(sp.expand)
    # Comparison is deliberately downstream of the coordinate derivation.
    d = derive()
    mean = sp.trace(K)/3
    sigma = K-mean*sp.eye(3)
    sub = {d["a"][0]:A,d["a"][1]:0,d["a"][2]:0,d["H"]:mean}
    sub.update({d["n"][i,j]:0 for i in range(3) for j in range(i,3)})
    sub.update({d["sigma"][i,j]:sigma[i,j] for i,j in [(0,0),(1,1),(0,1),(0,2),(1,2)]})
    mixed = [sp.expand(ric[0,i+1]-d["Ricci"][0,i+1].subs(sub,simultaneous=True)) for i in range(3)]
    ham = sp.expand(G[0,0]-d["G"][0,0].subs(sub,simultaneous=True))
    return {"metric_germ":"-ds^2+omega^T(I+2sK)omega; omega=(dx,exp(-Ax)dy,exp(-Ax)dz)",
            "time":"s=c*t, evaluated at s=x=0", "ricci_03":ric[0,3],
            "mixed_residuals":mixed,"hamiltonian_residual":ham,
            "coordinate_G00":G[0,0],"coordinate_R0i":[ric[0,i+1] for i in range(3)]}


@lru_cache(maxsize=1)
def class_b_report() -> dict[str, Any]:
    d = derive()
    A,N22,N23,N33,S12,S13,kappa,q3 = sp.symbols("A N22 N23 N33 S12 S13 kappa_G q3",real=True)
    sub = {d["a"][0]:A,d["a"][1]:0,d["a"][2]:0,
           d["n"][0,0]:0,d["n"][0,1]:0,d["n"][0,2]:0,
           d["n"][1,1]:N22,d["n"][1,2]:N23,d["n"][2,2]:N33,
           d["sigma"][0,1]:S12,d["sigma"][0,2]:S13}
    carrier = sp.expand(d["divK"][2].subs(sub,simultaneous=True))
    projected = sp.expand(-d["E"][3,0].subs(sub,simultaneous=True))
    previous = carrier-kappa*q3
    fixture = {A:1,N22:0,N23:0,N33:0,S12:0,S13:1,q3:0}
    return {"geometric_carrier":carrier,"projected_momentum":projected,
            "prior_minus_derived":sp.expand(previous-projected),
            "type_V_counterexample_derived":sp.expand(projected.subs(fixture)),
            "type_V_counterexample_prior":sp.expand(previous.subs(fixture))}


@lru_cache(maxsize=1)
def mutation_records() -> list[dict[str,Any]]:
    A,N22,N23,S12,S13,kappa,q3 = sp.symbols("A N22 N23 S12 S13 kappa_G q3",real=True)
    direct = class_b_report()["projected_momentum"]
    nterm = N22*S12+N23*S13
    correct = -nterm+3*A*S13-kappa*q3
    candidates = {
        "locked_residual":correct,
        "flip_3A_residual":-nterm-3*A*S13-kappa*q3,
        "epsilon_flip_residual":nterm+3*A*S13-kappa*q3,
        "drop_S13_residual":-N22*S12-kappa*q3,
        "drop_N22_residual":(3*A-N23)*S13-kappa*q3,
        "order_flip_residual":nterm-3*A*S13-kappa*q3,
        "q_sign_residual":-nterm+3*A*S13+kappa*q3,
    }
    fixtures = [(0,2,0,1,1,1),(0,1,2,2,1,1),(0,-2,1,1,2,-1),(0,3,-1,2,3,2),
                (1,0,0,0,1,1),(2,2,1,1,2,1),(1,-1,2,3,-1,-1),(-1,3,-2,2,1,2)]
    rows = []
    for index,values in enumerate(fixtures):
        sub = dict(zip([A,N22,N23,S12,S13,q3],map(sp.Integer,values)))
        sub[kappa]=sp.S.One
        row = {"label":f"{'A' if index<4 else 'B'}{index%4+1}","class":"A" if index<4 else "B"}
        row.update({str(k):str(v) for k,v in sub.items()})
        row["derived_M3"] = str(sp.expand(direct.subs(sub)))
        row.update({name:str(sp.expand((expr-direct).subs(sub))) for name,expr in candidates.items()})
        rows.append(row)
    return rows


def claim_boundary() -> dict[str,str]:
    return {"native_runtime":"NOT_RUN","provider_export":"NOT_AUTHORIZED",
            "authority_effect_on_BASS":"NONE","constraint_propagation":"NOT_RUN",
            "first_interval":"NO_PASS_FIRST_CANONICAL_INTERVAL",
            "integration_status":"SIGN_RECONCILIATION_REQUIRED",
            "scope":"GEODESIC_NORMAL_FERMI_TRIAD_HOMOGENEOUS_CONSTRAINT_ORACLE"}


def _text(expr):
    return sp.sstr(sp.factor(expr))


def write_report(output_dir: Path) -> dict[str,Any]:
    output_dir.mkdir(parents=True,exist_ok=True)
    d = derive()
    coord = coordinate_witness()
    groups = {name:d[name] for name in ["gauss_residuals","codazzi_residuals","adapter_residuals",
              "output_gauss_residuals","output_codazzi_residuals","torsion_residuals","metric_residuals","jacobi_rate_residuals"]}
    groups["hamiltonian_residuals"] = [sp.expand(2*d["G"][0,0]-d["R3"]-sp.trace(d["K"])**2+sp.trace(d["K"]**2))]
    groups["momentum_residuals"] = [sp.expand(d["Ricci"][0,i+1]-d["divK"][i]) for i in range(3)]
    groups["coordinate_residuals"] = coord["mixed_residuals"]+[coord["hamiltonian_residual"]]
    checks = {key:{"total":len(values),"exact_zeros":sum(sp.expand(v)==0 for v in values),
                   "nonzero_residuals":[_text(v) for v in values if sp.expand(v)!=0]} for key,values in groups.items()}
    rows = mutation_records()
    passed = all(c["total"]==c["exact_zeros"] for c in checks.values())
    passed = passed and all(sp.sympify(r["locked_residual"])==0 for r in rows)
    report = {"schema":"rei-m2-spacetime-sign-diagnostic/v1",
              "status":"PASS_REI_M2_EXACT_SIGN_DIAGNOSTIC" if passed else "FAIL_REI_M2_EXACT_SIGN_DIAGNOSTIC",
              "checks":checks,"M1_source_sha256":hashlib.sha256(M1_PATH.read_bytes()).hexdigest(),
              "R3":_text(d["R3"]),"E_nn":_text(d["E"][0,0]),
              "Ricci_0i":[_text(d["Ricci"][0,i+1]) for i in range(3)],
              "class_b":{k:_text(v) for k,v in class_b_report().items()},
              "coordinate_witness":{k:([_text(v) for v in value] if isinstance(value,list) else _text(value) if isinstance(value,sp.Basic) else value) for k,value in coord.items()},
              "mutations":rows,"claim_boundary":claim_boundary(),
              "plot_note":"Absolute exact residuals times L0^2; exact zeros displayed at 1e-30 only, not measured floating residuals.",
              "visual_review":"NOT_CLAIMED_BY_GENERATOR"}
    (output_dir/"M2_SIGN_REPORT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with (output_dir/"M2_MUTATIONS.csv").open("w",newline="",encoding="utf-8") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    import matplotlib.pyplot as plt
    figure,axis = plt.subplots(figsize=(8.0,4.8))
    for key,label,marker in [("locked_residual","derived constraint","o"),("order_flip_residual","prior momentum sign","s"),("flip_3A_residual","3A sign mutation","^"),("q_sign_residual","matter sign mutation","x")]:
        axis.semilogy(range(1,9),[max(abs(float(sp.sympify(r[key]))),1e-30) for r in rows],marker=marker,label=label)
    axis.axvline(4.5,linestyle="--",linewidth=1)
    axis.set_xticks(range(1,9),[r["label"] for r in rows])
    axis.set_xlabel("Exact fixtures: class A controls | class B witnesses")
    axis.set_ylabel("Absolute residual times L0 squared")
    axis.set_title("M2 momentum-sign diagnostic (zero display floor: 1e-30)")
    axis.legend(loc="center left",bbox_to_anchor=(1,0.5))
    figure.tight_layout()
    figure.savefig(output_dir/"M2_MOMENTUM_SIGN.svg",metadata={"Date":None})
    figure.savefig(output_dir/"M2_MOMENTUM_SIGN.png",dpi=160)
    plt.close(figure)
    print(json.dumps(report,sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    result = write_report(args.output_dir)
    return 0 if result["status"]=="PASS_REI_M2_EXACT_SIGN_DIAGNOSTIC" else 1


if __name__=="__main__":
    raise SystemExit(main())
