#!/usr/bin/env python3
"""Exact algebra checks for PHYS15; no physical history/root computation.

Raw source leaves are read without importing any scientific candidate.  The
spectra and gas four-jets below are explicit manufactured rational examples.
The transport uses the actual 33 captured energy nodes and a rational rho.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import struct
import time


class Jet:
    """Value, lambda, b, lambda-b coefficients in Q[e,f]/(e^2,f^2)."""
    __slots__ = ("v", "u", "b", "w")

    def __init__(self, v=0, u=0, b=0, w=0):
        if isinstance(v, Jet):
            self.v, self.u, self.b, self.w = v.tuple()
        else:
            self.v, self.u, self.b, self.w = map(Q, (v, u, b, w))

    def tuple(self):
        return self.v, self.u, self.b, self.w

    def __add__(self, y):
        y = Jet(y)
        return Jet(*(a + b for a, b in zip(self.tuple(), y.tuple())))

    __radd__ = __add__

    def __neg__(self):
        return Jet(*(-a for a in self.tuple()))

    def __sub__(self, y):
        return self + -Jet(y)

    def __rsub__(self, y):
        return Jet(y) + -self

    def __mul__(self, y):
        y = Jet(y)
        return Jet(self.v*y.v,
                   self.u*y.v + self.v*y.u,
                   self.b*y.v + self.v*y.b,
                   self.w*y.v + self.u*y.b + self.b*y.u + self.v*y.w)

    __rmul__ = __mul__

    def inv(self):
        assert self.v != 0
        return Jet(1/self.v, -self.u/self.v**2, -self.b/self.v**2,
                   2*self.u*self.b/self.v**3 - self.w/self.v**2)

    def __truediv__(self, y):
        return self * Jet(y).inv()

    def __rtruediv__(self, y):
        return Jet(y) * self.inv()


def bits(s):
    return Q(struct.unpack(">d", bytes.fromhex(s))[0])


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def add(*vectors):
    return [sum(values, Jet()) for values in zip(*vectors)]


def sub(a, b):
    return [x-y for x, y in zip(a, b)]


def scale(c, v):
    return [c*x for x in v]


def diag(a, v):
    return [x*y for x, y in zip(a, v)]


def main(project: Path, output: Path):
    t0 = time.perf_counter()
    paths = {
        "half_box": project/"inputs/ncp07/results/first_half/SOURCE_BOX.json",
        "full_box": project/"inputs/ncp07/results/full/SOURCE_BOX.json",
        "half_birth": project/"inputs/ncp07/results/first_half/PREBE.json",
        "full_birth": project/"inputs/ncp07/results/full/PREBE.json",
        "half_native": project/"inputs/ncp07/results/first_half/NATIVE_CONSTANT_LEAVES.json",
        "full_native": project/"inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json",
        "phys14_theory": project/"theory/THEORY_CANDIDATE_KO.md",
        "phys14_code": project/"src/phys14_advance.py",
    }
    raw = {k: json.loads(p.read_text()) for k, p in paths.items()
           if p.suffix == ".json"}
    hb, fb = raw["half_box"], raw["full_box"]
    hn, fn = raw["half_native"], raw["full_native"]
    E = [bits(s) for s in fb["energy_bits"]]
    h = bits(hb["dt_bits"])
    M = bits(raw["half_birth"]["fl_dt_SOURCE_bits"])
    MF = bits(raw["full_birth"]["fl_dt_SOURCE_bits"])
    sigma = [bits(row[0]) for row in fb["sigma_bits"]]
    heat = [bits(row[0]) for row in fb["heat_bits"]]
    chi = bits(fn["CHI_bits"][0])
    c = bits(fn["c_bits"])
    a1 = [c*bits(hb["nH_bits"])*s for s in sigma]
    a2 = [c*bits(fb["nH_bits"])*s for s in sigma]
    assert len(E) == 33 and all(x < y for x, y in zip(E, E[1:]))
    assert hb["energy_bits"] == fb["energy_bits"]
    assert hb["sigma_bits"] == fb["sigma_bits"]
    assert hb["heat_bits"] == fb["heat_bits"]
    assert hn["CHI_bits"] == fn["CHI_bits"]
    assert hn["c_bits"] == fn["c_bits"]
    assert h == 625000000 and bits(fb["dt_bits"]) == 2*h
    assert MF == 2*M
    active = [j for j, s in enumerate(sigma) if s]
    assert active == list(range(16, 33))
    assert all(bits(row[1]) == bits(row[2]) == 0 for row in fb["sigma_bits"])
    assert all(sigma[j] > sigma[j+1] > 0 for j in range(16, 32))
    heat_equal = [heat[j] == E[j]-chi for j in active]
    assert all(heat_equal)

    n = 35
    checks = []
    assertions = 0

    def eq(name, left, right):
        nonlocal assertions
        if isinstance(left, Jet):
            left, right = [left], [right]
        assert len(left) == len(right)
        for i, (x, y) in enumerate(zip(left, right)):
            for s, (a, b) in enumerate(zip(x.tuple(), y.tuple())):
                assertions += 1
                assert a == b, (name, i, s)
        checks.append({"id": name, "coordinates": len(left),
                       "jet_slots": 4, "result": "pass_scoped"})

    def R(v, rho):
        y = [Jet() for _ in range(n)]
        y[33], y[34] = v[33], rho*v[34]
        for j in range(33):
            e = rho*E[j]
            if e < E[0]:
                y[33] += v[j]
                y[34] += e*v[j]
            elif e == E[j]:
                y[j] += v[j]
            else:
                assert j >= 1 and E[j-1] < e < E[j]
                alpha = (E[j]-e)/(E[j]-E[j-1])
                y[j-1] += alpha*v[j]
                y[j] += (1-alpha)*v[j]
        return y

    def number(v):
        return sum(v[:33], Jet()) + v[33]

    def energy(v):
        return sum((e*x for e, x in zip(E, v[:33])), Jet()) + v[34]

    def absorbed_energy(v):
        return sum((e*x for e, x in zip(E, v[:33])), Jet())

    def absorbed_heat(v):
        return sum((e*x for e, x in zip(heat, v[:33])), Jet())

    rho0 = Q(1)-Q(1, 160000)
    stock = [Jet(Q(1, 10000*(j+1))) for j in range(33)] + [Jet(Q(1,50000)), Jet(E[0]/100000)]
    J = [Jet() for _ in range(n)]
    J[24] = Jet(M)
    x1 = Jet(Q(913,1000), Q(1,100000), Q(3,100000), Q(-1,1000000))
    x2 = Jet(Q(915,1000), Q(7,100000), Q(5,100000), Q(1,1000000))
    bjet = Jet(Q(2,5), 0, 1, 0)

    def one_case(name, rho, z0, birth, first_x, second_x, av1, av2):
        A1 = [(1+h*a*(1-first_x)).inv() for a in av1] + [Jet(1), Jet(1)]
        A = [(1+h*a*(1-second_x)).inv() for a in av2] + [Jet(1), Jet(1)]
        AF = [(1+2*h*a*(1-second_x)).inv() for a in av2] + [Jet(1), Jet(1)]
        tau = [h*a*(1-second_x) for a in av2] + [Jet(), Jet()]
        B1, B, BF = ([1-a for a in arr] for arr in (A1, A, AF))
        C2 = [t*t*a*a*f for t,a,f in zip(tau,A,AF)]
        C1 = [t*a*a*f for t,a,f in zip(tau,A,AF)]
        dA = [a1-a for a1,a in zip(A1,A)]
        q1 = add(R(z0,rho), scale(birth,J))
        n1 = diag(A1,q1)
        q2 = add(R(n1,rho),scale(birth,J))
        n2 = diag(A,q2)
        qF = add(R(z0,rho*rho),scale(2*birth,J))
        nF = diag(AF,qF)
        delta_direct = sub(n2,nF)
        P1, P2, PF = diag(B1,q1),diag(B,q2),diag(BF,qF)
        Pi_direct = sub(add(P1,P2),PF)
        RR = R(R(z0,rho),rho)
        dR = sub(RR,R(z0,rho*rho))
        comm = sub(R(diag(A,q1),rho),diag(A,R(q1,rho)))
        dAq1 = diag(dA,q1)
        outgoing_terms = [
            diag(A,R(dAq1,rho)),
            diag(A,comm),
            scale(-1,diag(C2,RR)),
            diag(AF,dR),
            scale(birth,diag([a*a for a in A],sub(R(J,rho),J))),
            scale(birth,diag(C1,J)),
        ]
        photo_terms = [
            sub(diag(B,R(dAq1,rho)),dAq1),
            diag(B,comm),
            diag(B,sub(R(z0,rho),RR)),
            diag(C2,RR),
            diag(BF,dR),
            scale(birth,diag([bb*aa for bb,aa in zip(B,A)],sub(R(J,rho),J))),
            scale(-birth,diag(C1,J)),
        ]
        eq(name+"/outgoing_factorization",delta_direct,add(*outgoing_terms))
        eq(name+"/photo_factorization",Pi_direct,add(*photo_terms))
        eq(name+"/number_ledger",number(delta_direct),-number(Pi_direct))
        eq(name+"/energy_ledger",energy(delta_direct),
           (rho-1)*birth*energy(J)-rho*absorbed_energy(P1)-absorbed_energy(P2)+absorbed_energy(PF))
        eq(name+"/heat_moment_reduction",absorbed_heat(Pi_direct),
           (1-rho)*(absorbed_energy(P1)-birth*energy(J))-energy(delta_direct)+chi*number(delta_direct))
        eq(name+"/opacity_difference",dA,
           [h*(a2*(1-second_x)-a1*(1-first_x))*u*v
            for a1,a2,u,v in zip(av1,av2,A1[:33],A[:33])] + [Jet(),Jet()])
        return {"outgoing":delta_direct,"photo":Pi_direct,"C2":C2,"C1":C1,
                "dR":dR,"A1":A1,"A":A,"AF":AF,"q1":q1,"q2":q2,"P1":P1}

    full = one_case("captured_grid_four_jet",rho0,stock,bjet,x1,x2,a1,a2)
    zeros = [Jet() for _ in range(n)]
    empty_a = [Q(0)]*33
    free = one_case("transparent",rho0,stock,bjet,x1,x2,empty_a,empty_a)
    eq("transparent/only_remap_and_birth_redshift",free["outgoing"],
       add(free["dR"],scale(bjet,sub(R(J,rho0),J))))
    eq("transparent/photo_zero",free["photo"],zeros)
    frozen = one_case("same_opacity_no_redshift_no_birth",Q(1),stock,Jet(),x2,x2,a2,a2)
    eq("frozen_stock/BE_absorption_subdivision",frozen["outgoing"],
       scale(-1,diag(frozen["C2"],stock)))
    born = one_case("same_opacity_no_redshift_birth_only",Q(1),zeros,bjet,x2,x2,a2,a2)
    eq("birth_only/BE_birth_chronology",born["outgoing"],scale(bjet,diag(born["C1"],J)))

    # General anchor g*=gF: the actual endpoint A2 is different from anchor A*.
    star_x = Jet(Q(914,1000),Q(1,100000),Q(2,100000),Q(-1,1000000))
    star = one_case("general_anchor_reference",rho0,stock,bjet,x1,star_x,a1,a2)
    A2 = full["A"]
    q2 = full["q2"]
    general_direct = sub(diag(A2,q2),diag(star["AF"],add(R(stock,rho0*rho0),scale(2*bjet,J))))
    extra = diag([a-s for a,s in zip(A2,star["A"])],q2)
    eq("general_anchor/outgoing_endpoint_opacity",general_direct,add(star["outgoing"],extra))
    eq("general_anchor/secant_opacity_factor",extra,
       scale(x2-star_x,diag([h*a*u*v for a,u,v in zip(a2,A2[:33],star["A"][:33])] + [Jet(),Jet()],q2)))

    # Sparse commutator and original-grid remap moments, retaining guards.
    av = full["A"]
    comm_direct = sub(R(diag(av,stock),rho0),diag(av,R(stock,rho0)))
    comm_sparse = [Jet() for _ in range(n)]
    for j in range(1,33):
        alpha = (1-rho0)*E[j]/(E[j]-E[j-1])
        comm_sparse[j-1] += alpha*(av[j]-av[j-1])*stock[j]
    # Original j=0 is HI-inactive, so transport into both guards commutes.
    eq("commutator/single_subdiagonal",comm_direct,comm_sparse)
    eq("remap/number_moment",number(full["dR"]),Jet())
    eq("remap/energy_moment",energy(full["dR"]),Jet())

    result = {
        "schema": "WU088_HH_PHYS15_PHOTON_ALGEBRA_CHECK_V1",
        "status": "completed", "result": "pass_scoped",
        "scope": "Exact algebra substitutions in manufactured rational four-jet examples; source leaf identities from original captured bits",
        "scientific_history_runs": 0, "native_runs": 0, "candidate_imports": 0,
        "arithmetic": "Python Fraction; exact dual algebra Q[e,f]/(e^2,f^2)",
        "rho": {"numerator":rho0.numerator,"denominator":rho0.denominator,
                "interpretation":"manufactured rational check value; no exponential evaluation"},
        "checks": checks, "scalar_equalities": assertions,
        "leaf_evidence": {"captured_energy_nodes":33,
            "active_HI_nodes":active,"all_He_opacities_exact_zero":True,
            "HI_active_sigma_strictly_decreasing":True,
            "half_dt_bits":hb["dt_bits"],"full_dt_bits":fb["dt_bits"],
            "full_dt_equals_two_halves_exact":True,
            "half_birth_bits":raw["half_birth"]["fl_dt_SOURCE_bits"],
            "full_birth_bits":raw["full_birth"]["fl_dt_SOURCE_bits"],
            "full_birth_equals_two_halves_exact":True,
            "captured_heat_equals_exact_energy_minus_captured_chi_on_active":heat_equal,
            "original_heat_leaves_retained":True},
        "inputs":[{"id":k,"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)}
                  for k,p in paths.items()],
        "script_sha256":sha(Path(__file__)),
        "elapsed_seconds":time.perf_counter()-t0,
        "proof_location":"PHOTON_DEFECT_THEOREM_KO.md",
        "judgement":"Candidate derivations are preserved for parent and independent review."
    }
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"result":result["result"],
                      "identities":len(checks),"scalar_equalities":assertions,
                      "scientific_history_runs":0,"elapsed_seconds":result["elapsed_seconds"],
                      "output":str(output),"output_sha256":sha(output)},ensure_ascii=False))


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    main(args.project,args.output)
