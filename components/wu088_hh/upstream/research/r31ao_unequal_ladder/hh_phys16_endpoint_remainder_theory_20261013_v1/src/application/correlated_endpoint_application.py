#!/usr/bin/env python3
"""A bounded PHYS16 application of PHYS15 identities to archived enclosures.

No reaction-fit invocation, physical source callback, root solve or history
replay occurs. PHYS14's unchanged arithmetic helpers are imported, not its
main/Source/evaluate/implicit-stage routines. The same variables are factored
symbolically before interval evaluation. Remaining box dependency loss is
reported explicitly; it affects sharpness, not inclusion.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys
import time
from fractions import Fraction as Q


def main(parent: pathlib.Path, output: pathlib.Path):
    started = time.perf_counter()
    ap = parent / "inputs/phys14/src/phys14_advance.py"
    assert hashlib.sha256(ap.read_bytes()).hexdigest() == "d20d9797278b8da71d38a3db229325dc7792d3991863f07bcdb7f72f2ba5567a"
    spec = importlib.util.spec_from_file_location("phys14_arithmetic_reuse", ap)
    old = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(old)
    I, raw, bits, out = old.I, old.from_raw, old.exact_bits, old.out
    dot, mv, add, scale = old.dot, old.matvec, old.vadd, old.scale
    inputs = []

    def read(rel):
        p = parent / rel
        data = p.read_bytes()
        inputs.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        return json.loads(data)

    def hull(*xs):
        return I(min(x.lo for x in xs), max(x.hi for x in xs))

    def diagonal(a, v):
        return [x * y for x, y in zip(a, v)]

    def opposite(v):
        return [-x for x in v]

    def solve_exact(A, b):
        """Exact rational Gaussian elimination, used only for a 4x4 majorant."""
        n = len(b)
        M = [list(row) + [z] for row, z in zip(A, b)]
        for j in range(n):
            k = next(k for k in range(j, n) if M[k][j])
            M[j], M[k] = M[k], M[j]
            a = M[j][j]
            M[j] = [v / a for v in M[j]]
            for k in range(n):
                if k != j:
                    a = M[k][j]
                    M[k] = [x - a*y for x,y in zip(M[k],M[j])]
        return [M[k][-1] for k in range(n)]

    ncp = "inputs/phys14/inputs/ncp07/results/"
    box = read(ncp + "full/SOURCE_BOX.json")
    half = read(ncp + "first_half/SOURCE_BOX.json")
    comp = read(ncp + "full/SOURCE_BOX_COMPONENTS.json")
    ccomp = read(ncp + "full/SOURCE_CENTRE_COMPONENTS.json")
    centre = read(ncp + "full/SOURCE_CENTRE.json")
    native = read(ncp + "full/NATIVE_CONSTANT_LEAVES.json")
    pre = read(ncp + "first_half/PREBE.json")
    full_pre = read(ncp + "full/PREBE.json")
    p14 = read("inputs/phys14/results/advance01/ADVANCE_RESULTS.json")
    p13 = read("inputs/phys14/inputs/phys13/THERMO_RESULTS.json")
    p11 = read("inputs/phys14/inputs/phys11/CARRY_RESULTS.json")
    uniform = read("inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json")
    rawmodel = parent / "inputs/phys14/inputs/ncp07/candidate/src/ft03_interval.rs"
    inputs.append({"path": str(rawmodel.relative_to(parent)), "bytes": rawmodel.stat().st_size,
                   "sha256": hashlib.sha256(rawmodel.read_bytes()).hexdigest()})
    assert inputs[-1]["sha256"] == "886580a810b8ec29c8f0b6199c0e35d82fde1f46d984a5f8f1da304326a42a42"
    h = I(bits(half["dt_bits"]))
    assert h.lo == h.hi == 625000000 and bits(box["dt_bits"]) == 2*h.lo
    n1, n2 = I(bits(half["nH_bits"])), I(bits(box["nH_bits"]))
    f1 = I(bits(half["nHe_stored_bits"])) / n1
    f2 = I(bits(box["nHe_stored_bits"])) / n2
    # Preserve the exact stored density ratio difference before rounding.
    fq1 = bits(half["nHe_stored_bits"]) / bits(half["nH_bits"])
    fq2 = bits(box["nHe_stored_bits"]) / bits(box["nH_bits"])
    df = I(fq1 - fq2)
    rn = I(bits(half["nH_bits"]) / bits(box["nH_bits"]))
    H = I(bits(box["Hmean_bits"]))
    assert box["Hmean_bits"] == half["Hmean_bits"]
    c = I(bits(native["c_bits"]))
    chi = I(bits(native["CHI_bits"][0]))
    CT = 2*I(bits(native["ev_erg_bits"]))/(3*I(bits(native["kb_bits"])))
    E = [I(bits(v)) for v in box["energy_bits"]]
    a1 = [c*n1*bits(v[0]) for v in box["sigma_bits"]] + [I(0), I(0)]
    a2 = [c*n2*bits(v[0]) for v in box["sigma_bits"]] + [I(0), I(0)]
    heat = [I(bits(v[0])) for v in box["heat_bits"]]
    assert box["sigma_bits"] == half["sigma_bits"]
    assert box["energy_bits"] == half["energy_bits"]
    assert box["heat_bits"] == half["heat_bits"]
    active = [j for j in range(33) if a2[j].hi > 0]
    assert active == list(range(16,33))
    assert all(bits(v[1]) == bits(v[2]) == 0 for v in box["sigma_bits"])
    assert all((heat[j] - (E[j]-chi)).lo == (heat[j] - (E[j]-chi)).hi == 0 for j in active)
    rho = raw(p14["constants"]["rho"])
    M = I(bits(pre["fl_dt_SOURCE_bits"]))
    assert bits(full_pre["fl_dt_SOURCE_bits"]) == 2*M.lo
    alpha = [I(0)] + [(1-rho)*E[j]/(E[j]-E[j-1]) for j in range(1,33)]
    assert all(0 < z.lo <= z.hi < 1 for z in alpha[1:])
    assert all((rho**2*E[j]).lo > E[j-1].hi for j in range(1,33))
    par_lambda, par_b = I(0,1), I(0,1)
    J = [I(0) for _ in range(35)]
    J[24] = M

    def R(v):
        q = [I(0) for _ in range(35)]
        q[33],q[34] = v[33]+v[0],rho*(v[34]+E[0]*v[0])
        for j in range(1,33):
            q[j-1] += alpha[j]*v[j]
            q[j] += (1-alpha[j])*v[j]
        return q

    def RminusI(v):
        """Apply the signed sparse operator before enclosing its argument."""
        q = [I(0) for _ in range(35)]
        q[0] = -v[0]
        q[33],q[34] = v[0],rho*E[0]*v[0]+(rho-1)*v[34]
        for j in range(1,33):
            transfer = alpha[j]*v[j]
            q[j-1] += transfer
            q[j] -= transfer
        return q

    def deltaR(v):
        q = [I(0) for _ in range(35)]
        for j in range(2,33):
            ratio = (E[j-1]-E[j-2])/(E[j]-E[j-1])
            pref = alpha[j]*alpha[j-1]*v[j]
            q[j-2] += pref
            q[j-1] -= (1+ratio)*pref
            q[j] += ratio*pref
        q[1] += alpha[1]*(alpha[1]+rho-1)*v[1]
        q[0] -= alpha[1]*(alpha[1]+rho)*v[1]
        q[33] += alpha[1]*v[1]
        q[34] += rho*E[0]*alpha[1]*v[1]
        return q

    blobpath = parent / (ncp + "first_half/prebe_input_words.bin")
    blob = blobpath.read_bytes()
    inputs.append({"path":str(blobpath.relative_to(parent)),"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest()})
    assert len(blob) == 4090360
    Z0 = [sum((old.read_binary_value(blob,5,4+r*33+j) for r in range(128)),I(0)) for j in range(33)]
    Z0 += [sum((old.read_binary_value(blob,5,4+4224+offset+r) for r in range(128)),I(0)) for offset in (0,128)]
    assert all(z.lo >= 0 for z in Z0)
    RZ0, R2Z0, dRZ0 = R(Z0), R(R(Z0)), deltaR(Z0)
    Q1 = add(RZ0,scale(par_b,J))
    inherited_first = next(x for x in p11["stages"] if x["stage"] == "first_half")
    for j in range(33):
        Q1[j] = Q1[j].meet(raw(inherited_first["groups"][j]["incoming"]["value"]))
    g1 = [raw(z) for z in p14["root_certificate"]["input_g1"]]
    g2 = [raw(z) for z in p14["root_certificate"]["root_image"]]
    gF = [raw(z) for z in next(x for x in p13["rows"] if x["stage"] == "full")["root_image"]["intervals"]]
    X = [raw(z) for z in p14["root_certificate"]["domain_X"]]
    gc = [I(Q(z)) for z in uniform["center"]]
    D1 = [1+h*a*(1-g1[0]) for a in a1]
    D2 = [1+h*a*(1-g2[0]) for a in a2]
    DF = [1+2*h*a*(1-g2[0]) for a in a2]
    A1,A,AF = [[1/z for z in d] for d in (D1,D2,DF)]
    tau = [h*a*(1-g2[0]) for a in a2]
    L,LF = [t/d for t,d in zip(tau,D2)],[2*t/d for t,d in zip(tau,DF)]
    C1 = [t*a*a*f for t,a,f in zip(tau,A,AF)]
    C2 = [t*c1 for t,c1 in zip(tau,C1)]
    Z1 = diagonal(A1,Q1)
    Q2 = add(R(Z1),scale(par_b,J))
    for j in range(33):
        Q2[j] = Q2[j].meet(raw(p14["photon_state"]["incoming"]["value"][j]))
    P1 = diagonal([h*a*(1-g1[0])/d for a,d in zip(a1,D1)],Q1)
    P2 = diagonal(L,Q2)
    for j in range(33):
        P2[j] = P2[j].meet(raw(p14["photon_state"]["absorbed"]["value"][j]))
    RFZ0 = old.transport(Z0[:33],Z0[33],Z0[34],[e.lo for e in E],rho**2)
    QF = add(RFZ0[0]+[RFZ0[1],RFZ0[2]],scale(2*par_b,J))

    npj = [old.jet(x) for x in comp["nonphoto"]]
    npc = [old.jet(x) for x in ccomp["nonphoto"]]
    qj,qc = old.jet(box["q"]),old.jet(centre["q"])

    def local_jets(g):
        assert all(z.within(x) for z,x in zip(g,X))
        delta = [z-c0 for z,c0 in zip(g,gc)]
        return [old.taylor_jet(j,jc,delta) for j,jc in zip(npj,npc)],old.taylor_jet(qj,qc,delta)

    hh = [I(1),I(0),I(0),-chi]

    def B_values(g):
        np,q = local_jets(g)
        v = [np[i]["value"]+par_lambda*q["value"]*hh[i] for i in range(4)]
        v[3] -= 2*H*g[3]
        return v

    def B_jacobian(g):
        np,q = local_jets(g)
        v = [[np[i]["g"][j]+par_lambda*q["g"][j]*hh[i] for j in range(4)] for i in range(4)]
        v[3][3] -= 2*H
        return v

    def V(v):
        return [sum(v[:33],I(0)),I(0),I(0),dot(heat,v[:33])]

    stage_increment = add(scale(h,B_values(g2)),V(P2))
    segment12 = [hull(x,y) for x,y in zip(g1,g2)]
    J12 = B_jacobian(segment12)
    for z,x in zip(segment12,X):
        assert z.within(x,strict=True)
    # Temperature-aligned density bridge; a cooling-cone bound isolates He.
    s1 = g1[1]+2*g1[2]
    e1,e2at1 = g1[0]+f1*s1,g1[0]+f2*s1
    Pi1 = 1+f1+e1
    dw_pull = -g1[3]*df*(1+s1)/Pi1
    gstar = list(g1)
    gstar[3] += dw_pull
    assert all(z.within(x,strict=True) for z,x in zip(gstar,X))
    pull_segment = [hull(x,y) for x,y in zip(g1,gstar)]
    np1,q1 = local_jets(g1)
    npstar,qstar = local_jets(gstar)
    nppull,qpull = local_jets(pull_segment)
    re_minus1 = (rn-1)+rn*df*s1/e2at1
    re = 1+re_minus1
    # On the whole captured source temperature domain, all thermal reaction
    # coefficients are cooling: u>1 makes the H/HeII RR kinetic factor >0;
    # HeI has 1.5-0.654>0. CI and DR factors/populations are positive.
    rr_kinetic_lower = I(Q(1.5)-Q(1.503)+Q(1.923)*Q(.470)/2)
    assert rr_kinetic_lower.lo > 0 and Q(315614)/(Q(.522)*110000) > 1
    T1 = CT*g1[3]/Pi1
    assert 30000 < T1.lo and T1.hi < 110000
    estar = gstar[0]+f2*(gstar[1]+2*gstar[2])
    kwHe_lower = (npstar[3]["value"]/(n2*estar*f2)).lo
    assert npstar[3]["value"].hi < 0
    kwHe = I(kwHe_lower,0)
    He_correction = n1*e1*df*kwHe
    assert He_correction.lo >= 0
    dt_np = [re_minus1*np1[i]["value"]+re*nppull[i]["g"][3]*dw_pull for i in range(4)]
    dt_np[3] += He_correction
    dt_q = (rn-1)*q1["value"]+rn*qpull["g"][3]*dw_pull
    dt_B = [dt_np[i]+par_lambda*dt_q*hh[i] for i in range(4)]
    gas_time = scale(h,dt_B)
    gas_movement = scale(-h,mv(J12,stage_increment))
    # ΔA1 is factored using the same actual stage increment, not box g1-g2.
    dA1 = [h*(c*bits(box["sigma_bits"][j][0])*(n2-n1)*(1-g2[0])-a1[j]*stage_increment[0])*A1[j]*A[j] for j in range(33)]+[I(0),I(0)]
    dAQ = diagonal(dA1,Q1)
    commQ = [I(0) for _ in range(35)]
    for j in range(1,33):
        commQ[j-1] += alpha[j]*h*(a2[j-1]-a2[j])*(1-g2[0])*A[j-1]*A[j]*Q1[j]
    rmJ = RminusI(J)
    sectors = {
        "opacity_change": add(opposite(dAQ),diagonal(L,R(dAQ))),
        "absorption_transport_commutator": diagonal(L,commQ),
        "stock_intermediate_redshift": diagonal(L,opposite(RminusI(RZ0))),
        "stock_backward_euler": diagonal(C2,R2Z0),
        "remap_composition": diagonal(LF,dRZ0),
        "birth_redshift": scale(par_b,diagonal(diagonal(L,A),rmJ)),
        "birth_backward_euler": scale(-par_b,diagonal(C1,J))}
    p = [sum((v[j] for v in sectors.values()),I(0)) for j in range(35)]
    assert p[33].lo == p[33].hi == p[34].lo == p[34].hi == 0
    residual_sectors = {"source_time":gas_time,"gas_movement":gas_movement,**{k:V(v) for k,v in sectors.items()}}
    residual = [sum((v[i] for v in residual_sectors.values()),I(0)) for i in range(4)]
    Cr = mv([[I(Q(z)) for z in row] for row in uniform["fixed_C"]],residual)
    C = [[I(Q(z)) for z in row] for row in uniform["fixed_C"]]
    B = [[raw(z).hi for z in row] for row in uniform["B"]]
    q = raw(uniform["q"]).hi
    S = [Q(z) for z in uniform["radius"]]
    assert uniform["q"]["hi_bits"] == "3f1ec474231fbe16" and q < 1
    assert all(sum(B[i][j]*S[j]/S[i] for j in range(4)) <= q for i in range(4))
    majorant_matrix = [[Q(i==j)-B[i][j] for j in range(4)] for i in range(4)]

    def componentwise_transfer(rr):
        cr = mv(C,rr)
        mag = solve_exact(majorant_matrix,[z.mag() for z in cr])
        assert all(z >= 0 for z in mag)
        rem = [sum(B[i][j]*mag[j] for j in range(4)) for i in range(4)]
        assert all(mag[i]-rem[i] == cr[i].mag() for i in range(4))
        return [z+I(-v,v) for z,v in zip(cr,rem)],mag,rem

    d,majorant,rem = componentwise_transfer(residual)
    initial_d = list(d)
    fullseg = [hull(x,y) for x,y in zip(g2,gF)]
    JB = B_jacobian(fullseg)
    Dseg = [1+2*h*a*(1-fullseg[0]) for a in a2]
    vF = V([a*nf/(d0**2) for a,nf,d0 in zip(a2,QF,Dseg)])
    Abar = [[I(i==j)-2*h*JB[i][j]+(2*h*vF[i] if j==0 else I(0)) for j in range(4)] for i in range(4)]
    Ebar = [[I(i==j)-dot(C[i],[Abar[k][j] for k in range(4)]) for j in range(4)] for i in range(4)]
    Ebar = [[z.meet(I(-B[i][j],B[i][j])) for j,z in enumerate(row)] for i,row in enumerate(Ebar)]
    for _ in range(3):
        d = [x.meet(y) for x,y in zip(d,add(Cr,mv(Ebar,d)))]
    le = [I(1),f2,2*f2,I(0)]
    de,dw = dot(le,d),d[3]
    Pi2 = 1+f2+g2[0]+f2*(g2[1]+2*g2[2])
    PiF = Pi2-de
    assert PiF.lo > 0
    T2 = CT*g2[3]/Pi2
    dT = (CT*dw-T2*de)/PiF
    ellT = [(CT*I(i==3)-T2*le[i])/PiF for i in range(4)]
    attribution = {}
    for name,rs in residual_sectors.items():
        ds,_,_ = componentwise_transfer(rs)
        for _ in range(3):
            ds=[x.meet(y) for x,y in zip(ds,add(mv(C,rs),mv(Ebar,ds)))]
        attribution[name] = {"gas":ds,"temperature_K":dot(ellT,ds),"electron_per_H":dot(le,ds),"thermal_eV_per_H":ds[3]}
    anchor_terms = {
        "opacity_change":diagonal(A,R(dAQ)),
        "absorption_transport_commutator":diagonal(A,commQ),
        "stock_backward_euler":opposite(diagonal(C2,R2Z0)),
        "remap_composition":diagonal(AF,dRZ0),
        "birth_redshift":scale(par_b,diagonal(diagonal(A,A),rmJ)),
        "birth_backward_euler":scale(par_b,diagonal(C1,J))}
    anchor = [sum((v[j] for v in anchor_terms.values()),I(0)) for j in range(35)]
    DFactual = [1+2*h*a*(1-gF[0]) for a in a2]
    actual = [v+2*h*a*nf*d[0]/(da*db) for v,a,nf,da,db in zip(anchor,a2,QF,DF,DFactual)]
    nrow = [I(1) for _ in range(34)]+[I(0)]
    urow = E+[I(0),I(1)]
    dN,dU = dot(nrow,anchor),dot(urow,anchor)
    number_balance = sum(p[:33],I(0))+dN
    energy_balance = dot(E,p[:33])-(1-rho)*(dot(E,P1[:33])-par_b*M*E[24])+dU
    heat_balance = dot(heat,p[:33])-(1-rho)*(dot(E,P1[:33])-par_b*M*E[24])+dU-chi*dN
    assert number_balance.contains_zero() and energy_balance.contains_zero() and heat_balance.contains_zero()
    independent_difference = [x-y for x,y in zip(g2,gF)]
    assert all(x.within(y) for x,y in zip(d,independent_difference))
    result = {
        "schema":"WU088_HH_PHYS16_BOUNDED_APPLICATION_V1",
        "status":"CANDIDATE_COMPUTED",
        "scope":{"same_COMMON":True,"lambda":[0,1],"b":[0,1],"same_global_parameters":True,
                 "fixed_alpha":"inherited geometric isotropic source-aligned C2 family",
                 "numerical_quantification":"uniform valid interval inclusion over linked family",
                 "remaining_dependency_loss":"Interval box products reuse outer bounds; joint alpha and parameters are factored before evaluation but a full affine/Taylor parameter model is not constructed.",
                 "new_reaction_fit_evaluations":0,"new_physical_source_callbacks":0,"new_root_solves":0,"new_history_replays":0,"isolated_kwHe_transcendental_evaluations":0},
        "arithmetic":{"method":"reuse unchanged PHYS14 Fraction/directed dyadic primitives","bits":old.BITS,
                      "majorant_solution":"exact rational 4x4 solve of (I-B) m=|C r|","rho":"reuse archived interval, form rho^2 in one graph"},
        "input_identities":inputs,
        "definitions":{"d":"g2-gF","residual":"H_F(g2)","stage_increment":"g2-g1=h B2(g2)+V P2","finite_temperature":"(CT*d_w-T2*d_e)/(Pi2-d_e)"},
        "root_boxes":{"g1":g1,"g2":g2,"gF":gF,"joint_segment12":segment12},
        "linked_factors":{"rho":rho,"M":M,"common_Z0":Z0,"stage_increment":stage_increment,"Q1":Q1,"Q2":Q2,"QF":QF,"DeltaA1":dA1},
        "source_bridge":{"rn_minus1":rn-1,"f1_minus_f2":df,"temperature_K":T1,"pullback_w":dw_pull,
                         "RR_kinetic_lower":rr_kinetic_lower,"kwHe":kwHe,"He_correction_per_second":He_correction,
                         "nonphoto_time_difference":dt_np,"HH_time_difference":dt_q,"time_residual":gas_time,"movement_residual":gas_movement},
        "photon_absorption_sectors":sectors,"photon_absorption_defect":p,
        "residual_sectors":residual_sectors,"residual":residual,
        "transfer":{"C":C,"B":B,"q":q,"radius":S,"Cr":Cr,"componentwise_absolute_majorant":majorant,
                    "componentwise_remainder":rem,"initial_d":initial_d,"averaged_jacobian":Abar,"Ebar":Ebar,"intersection_iterations":3},
        "endpoint":{"d":d,"DeltaT_K":dT,"Deltae_per_H":de,"Deltaw_eV_per_H":dw,"Deltane_cm3":n2*de,
                    "Pi2":Pi2,"PiF":PiF,"temperature_covector":ellT,"independent_box_difference":independent_difference,
                    "width_improvement_factors":[I((y.hi-y.lo)/(x.hi-x.lo)) for x,y in zip(d,independent_difference)]},
        "sector_attribution":{"operator":"the same averaged Abar for all r_s; shared C,Ebar,PiF,T2 convention; interval products enclose each term","sectors":attribution},
        "photon_endpoint":{"anchor_terms":anchor_terms,"anchor":anchor,"actual_Full_secant":actual,
                           "anchor_number":dN,"anchor_energy_eV_per_H":dU,
                           "actual_number":dot(nrow,actual),"actual_energy_eV_per_H":dot(urow,actual)},
        "ledger_checks":{"anchor_number_zero_inclusion":number_balance,"anchor_energy_zero_inclusion":energy_balance,"anchor_heat_zero_inclusion":heat_balance},
        "elapsed_seconds":time.perf_counter()-started}
    output.mkdir(parents=True,exist_ok=False)
    (output/"CORRELATED_DEFECT_RESULTS.json").write_text(json.dumps(out(result),ensure_ascii=False,indent=2)+"\n")
    summary={"status":result["status"],"elapsed_seconds":result["elapsed_seconds"],"residual":old.short(residual),
             "stage_increment":old.short(stage_increment),"endpoint":old.short(result["endpoint"]),
             "source_bridge":old.short(result["source_bridge"]),"sector_temperature_K":{k:old.short(v["temperature_K"]) for k,v in attribution.items()}}
    (output/"SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--parent",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args()
    main(a.parent.resolve(),a.output.resolve())
