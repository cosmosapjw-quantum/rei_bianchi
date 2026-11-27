#!/usr/bin/env python3
"""PHYS17: bounded correlated parameter responses from frozen enclosures.

Only immutable enclosures and the unchanged PHYS14 arithmetic primitives are
used. No Source.evaluate, reaction fit, nonlinear root, or history is invoked.
The value/derivative dual graph below applies the exact differentiated photon
sector identities; source bridges use C2 jets and an analytic He isolation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import pathlib
import resource
import sys
import time
from fractions import Fraction as Q


def main(parent15: pathlib.Path, parent16: pathlib.Path, output: pathlib.Path):
    tic = time.perf_counter()
    inputs = []
    arithmetic = parent15 / "inputs/phys14/src/phys14_advance.py"
    assert hashlib.sha256(arithmetic.read_bytes()).hexdigest() == "d20d9797278b8da71d38a3db229325dc7792d3991863f07bcdb7f72f2ba5567a"
    spec = importlib.util.spec_from_file_location("p14_arithmetic_only", arithmetic)
    old = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(old)
    I, raw, bits, out = old.I, old.from_raw, old.exact_bits, old.out
    dot, mv, add, scale = old.dot, old.matvec, old.vadd, old.scale

    def read(root, rel):
        path = root / rel
        data = path.read_bytes()
        inputs.append({"root": "PHYS15" if root == parent15 else "PHYS16", "path": rel,
                       "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        return json.loads(data)

    def hull(*xs):
        return I(min(x.lo for x in xs), max(x.hi for x in xs))

    def tensor2(hess, v, w):
        return sum((hess[j][k] * v[j] * w[k] for j in range(4) for k in range(4)), I(0))

    def solve_exact(a, b):
        mat = [list(row) + [v] for row, v in zip(a, b)]
        for j in range(4):
            k = next(k for k in range(j, 4) if mat[k][j])
            mat[j], mat[k] = mat[k], mat[j]
            pivot = mat[j][j]
            mat[j] = [z / pivot for z in mat[j]]
            for k in range(4):
                if k != j:
                    fac = mat[k][j]
                    mat[k] = [x - fac*y for x, y in zip(mat[k], mat[j])]
        return [mat[j][-1] for j in range(4)]

    class D:
        """First-order dual interval, for one global parameter at a time."""
        __slots__ = ("v", "d")
        def __init__(self, value=0, derivative=0):
            if isinstance(value, D):
                self.v, self.d = value.v, value.d
            else:
                self.v, self.d = I(value), I(derivative)
        def __add__(self, z):
            z = D(z)
            return D(self.v+z.v, self.d+z.d)
        __radd__ = __add__
        def __neg__(self): return D(-self.v, -self.d)
        def __sub__(self, z): return self + -D(z)
        def __rsub__(self, z): return D(z) + -self
        def __mul__(self, z):
            z = D(z)
            return D(self.v*z.v, self.d*z.v+self.v*z.d)
        __rmul__ = __mul__
        def __truediv__(self, z):
            z = D(z)
            return D(self.v/z.v, (self.d*z.v-self.v*z.d)/(z.v**2))
        def __rtruediv__(self, z): return D(z)/self
        def __pow__(self, n):
            assert isinstance(n, int) and n >= 0
            return D(1) if n == 0 else D(self.v**n, n*(self.v**(n-1))*self.d)
        def meet(self, value=None, derivative=None):
            return D(self.v if value is None else self.v.meet(value),
                     self.d if derivative is None else self.d.meet(derivative))

    ncp = "inputs/phys14/inputs/ncp07/results/"
    box = read(parent15, ncp+"full/SOURCE_BOX.json")
    half = read(parent15, ncp+"first_half/SOURCE_BOX.json")
    comp = read(parent15, ncp+"full/SOURCE_BOX_COMPONENTS.json")
    centre = read(parent15, ncp+"full/SOURCE_CENTRE.json")
    ccomp = read(parent15, ncp+"full/SOURCE_CENTRE_COMPONENTS.json")
    native = read(parent15, ncp+"full/NATIVE_CONSTANT_LEAVES.json")
    p09 = read(parent15, "inputs/phys14/inputs/phys09/PROJECTED_RESULTS.json")
    p11 = read(parent15, "inputs/phys14/inputs/phys11/CARRY_RESULTS.json")
    p14 = read(parent15, "inputs/phys14/results/advance01/ADVANCE_RESULTS.json")
    uniform = read(parent15, "inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json")
    p16 = read(parent16, "checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json")
    e16 = read(parent16, "checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json")
    inputs.append({"root": "PHYS15", "path": str(arithmetic.relative_to(parent15)),
                   "bytes": arithmetic.stat().st_size,
                   "sha256": hashlib.sha256(arithmetic.read_bytes()).hexdigest()})

    h = I(bits(half["dt_bits"]))
    assert h.lo == h.hi == 625000000 and bits(box["dt_bits"]) == 2*h.lo
    n1, n2 = I(bits(half["nH_bits"])), I(bits(box["nH_bits"]))
    f1 = I(bits(half["nHe_stored_bits"]))/n1
    f2 = I(bits(box["nHe_stored_bits"]))/n2
    df = I(bits(half["nHe_stored_bits"])/bits(half["nH_bits"])
           -bits(box["nHe_stored_bits"])/bits(box["nH_bits"]))
    rn = I(bits(half["nH_bits"])/bits(box["nH_bits"]))
    H = I(bits(box["Hmean_bits"]))
    c = I(bits(native["c_bits"]))
    chi = I(bits(native["CHI_bits"][0]))
    CT = 2*I(bits(native["ev_erg_bits"]))/ (3*I(bits(native["kb_bits"])))
    E = [I(bits(z)) for z in box["energy_bits"]]
    a1 = [c*n1*bits(z[0]) for z in box["sigma_bits"]]+[I(0), I(0)]
    a2 = [c*n2*bits(z[0]) for z in box["sigma_bits"]]+[I(0), I(0)]
    heat = [I(bits(z[0])) for z in box["heat_bits"]]
    rho = raw(p16["linked_factors"]["rho"])
    birth_M = raw(p16["linked_factors"]["M"])
    alpha = [I(0)]+[(1-rho)*E[j]/(E[j]-E[j-1]) for j in range(1,33)]
    Z0 = [raw(z) for z in p16["linked_factors"]["common_Z0"]]
    Jbirth = [I(0) for _ in range(35)]
    Jbirth[24] = birth_M
    g1 = [raw(z) for z in p16["root_boxes"]["g1"]]
    y = [raw(z) for z in p16["root_boxes"]["g2"]]
    gF = [raw(z) for z in p16["root_boxes"]["gF"]]
    d = [raw(z) for z in e16["endpoint_d_intersection"]]
    dT = raw(e16["DeltaT_K_after_endpoint_intersection"])
    X = [raw(z) for z in p14["root_certificate"]["domain_X"]]
    gc = [I(Q(z)) for z in uniform["center"]]
    ss = [raw(z) for z in p16["linked_factors"]["stage_increment"]]
    par_lambda = I(0,1)
    hh = [I(1),I(0),I(0),-chi]
    le = [I(1),f2,2*f2,I(0)]
    le1 = [I(1),f1,2*f1,I(0)]
    Pi2 = 1+f2+dot(le,y)
    T2 = CT*y[3]/Pi2
    de = dot(le,d)
    PiF = Pi2-de
    assert PiF.lo > 0

    npj, npc = [old.jet(z) for z in comp["nonphoto"]], [old.jet(z) for z in ccomp["nonphoto"]]
    qj, qc = old.jet(box["q"]), old.jet(centre["q"])
    def local_jets(g):
        assert all(z.within(x) for z,x in zip(g,X))
        delta = [z-zc for z,zc in zip(g,gc)]
        return ([old.taylor_jet(j,jc,delta) for j,jc in zip(npj,npc)],
                old.taylor_jet(qj,qc,delta))
    def B_jets(g):
        np, q = local_jets(g)
        value = [np[i]["value"]+par_lambda*q["value"]*hh[i] for i in range(4)]
        jac = [[np[i]["g"][j]+par_lambda*q["g"][j]*hh[i] for j in range(4)] for i in range(4)]
        hess = [[[np[i]["gg"][j][k]+par_lambda*q["gg"][j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
        value[3] -= 2*H*g[3]
        jac[3][3] -= 2*H
        return value,jac,hess,q

    def R(v):
        q = [D(0) for _ in range(35)]
        q[33],q[34] = v[33]+v[0],(v[34]+v[0]*E[0])*rho
        for j in range(1,33):
            q[j-1] += v[j]*alpha[j]
            q[j] += v[j]*(1-alpha[j])
        return q
    def RminusI(v):
        q = [D(0) for _ in range(35)]
        q[0] = -v[0]
        q[33],q[34] = v[0],v[0]*(rho*E[0])+v[34]*(rho-1)
        for j in range(1,33):
            transfer = v[j]*alpha[j]
            q[j-1] += transfer
            q[j] -= transfer
        return q
    def deltaR(v):
        q = [D(0) for _ in range(35)]
        for j in range(2,33):
            ratio = (E[j-1]-E[j-2])/(E[j]-E[j-1])
            pref = v[j]*(alpha[j]*alpha[j-1])
            q[j-2] += pref
            q[j-1] -= pref*(1+ratio)
            q[j] += pref*ratio
        q[1] += v[1]*(alpha[1]*(alpha[1]+rho-1))
        q[0] -= v[1]*(alpha[1]*(alpha[1]+rho))
        q[33] += v[1]*alpha[1]
        q[34] += v[1]*(rho*E[0]*alpha[1])
        return q
    def V(v):
        return [sum(v[:33],D(0)),D(0),D(0),sum((v[j]*heat[j] for j in range(33)),D(0))]
    def VI(v):
        return [sum(v[:33],I(0)),I(0),I(0),dot(heat,v[:33])]

    first = next(s for s in p09["stages"] if s["stage"] == "first_half")
    full = next(s for s in p09["stages"] if s["stage"] == "full")
    firstphot = next(s for s in p11["stages"] if s["stage"] == "first_half")
    by, Jy, Hy, qy = B_jets(y)
    seg12 = [hull(z,w) for z,w in zip(g1,y)]
    _, _, H12, q12 = B_jets(seg12)

    # Full-endpoint Jacobian, fixed preconditioner, and signed inverse tail.
    C = [[I(Q(z)) for z in row] for row in uniform["fixed_C"]]
    B = [[raw(z).hi for z in row] for row in uniform["B"]]
    q = raw(uniform["q"]).hi
    S = [Q(z) for z in uniform["radius"]]
    assert q < 1 and all(sum(B[i][j]*S[j]/S[i] for j in range(4)) <= q for i in range(4))
    majorant_matrix = [[Q(i==j)-B[i][j] for j in range(4)] for i in range(4)]
    Ggg = [[[raw(z) for z in row] for row in component] for component in box["G_gg"]]
    JF = [[raw(box["A_Gg"][i][j]).meet(raw(centre["A_Gg"][i][j])+
            dot(Ggg[i][j],[gF[k]-gc[k] for k in range(4)])) for j in range(4)] for i in range(4)]
    EJ = [[(I(i==j)-dot(C[i],[JF[k][j] for k in range(4)])).meet(I(-B[i][j],B[i][j]))
           for j in range(4)] for i in range(4)]
    def transfer(rhs):
        cr = mv(C,rhs)
        mag = solve_exact(majorant_matrix,[z.mag() for z in cr])
        rem = [sum(B[i][j]*mag[j] for j in range(4)) for i in range(4)]
        assert all(mag[i]>=0 and mag[i]-rem[i]==cr[i].mag() for i in range(4))
        result = [z+I(-r,r) for z,r in zip(cr,rem)]
        initial = list(result)
        for _ in range(3):
            result = [z.meet(w) for z,w in zip(result,add(cr,mv(EJ,result)))]
        return result,{"C_rhs":cr,"absolute_majorant":mag,"tail":rem,"initial":initial}

    # Derivatives of the exact density/temperature bridge. The He identity is
    # derived from Fw+chi*Fx and differentiated as a function, not as a bound.
    def density_bridge(v, dlambda):
        sg = g1[1]+2*g1[2]
        eg1,eg2 = dot(le1,g1),dot(le,g1)
        Pi1 = 1+f1+eg1
        pull = -g1[3]*df*(1+sg)/Pi1
        pull_v = -df*(((1+sg)*v[3]+g1[3]*(v[1]+2*v[2]))/Pi1
                      -g1[3]*(1+sg)*dot(le1,v)/(Pi1**2))
        gs = list(g1); gs[3] += pull
        vs = list(v); vs[3] += pull_v
        seg = [hull(z,w) for z,w in zip(g1,gs)]
        ng,qg = local_jets(g1)
        ns,qs = local_jets(gs)
        nh,qh = local_jets(seg)
        rem1 = (rn-1)+rn*df*sg/eg2
        re = 1+rem1
        re_v = rn*df*(eg2*(v[1]+2*v[2])-sg*dot(le,v))/(eg2**2)
        scalar = ns[3]["value"]+chi*ns[0]["value"]
        sg1 = [ns[3]["g"][j]+chi*ns[0]["g"][j] for j in range(4)]
        sg2 = [[ns[3]["gg"][j][k]+chi*ns[0]["gg"][j][k] for k in range(4)] for j in range(4)]
        es = dot(le,gs); Pis = 1+f2+es
        U = scalar/(n2*es)
        Ug = [(sg1[j]/es-scalar*le[j]/(es**2))/n2 for j in range(4)]
        Ugg = [[(sg2[j][k]/es-(sg1[j]*le[k]+sg1[k]*le[j])/(es**2)
                    +2*scalar*le[j]*le[k]/(es**3))/n2 for k in range(4)] for j in range(4)]
        u = [I(1),I(0),I(0),gs[3]/Pis]
        Du_v = [I(0),I(0),I(0),vs[3]/Pis-gs[3]*dot(le,vs)/(Pis**2)]
        kHe_identity = (U-gs[0]*dot(Ug,u))/f2
        kHe = kHe_identity.meet(raw(p16["source_bridge"]["kwHe"]))
        dkHe = (dot(Ug,vs)-vs[0]*dot(Ug,u)-gs[0]*(tensor2(Ugg,vs,u)+dot(Ug,Du_v)))/f2
        np_v = [rem1*dot(ng[i]["g"],v)+re_v*ns[i]["value"]+
                re*pull*dot(nh[i]["gg"][3],v)+re*ns[i]["g"][3]*pull_v for i in range(4)]
        he_v = n1*df*(dot(le1,v)*kHe+eg1*dkHe)
        np_v[3] += he_v
        q_v = (rn-1)*dot(qg["g"],v)+rn*pull*dot(qh["gg"][3],v)+rn*qs["g"][3]*pull_v
        delta_q = raw(p16["source_bridge"]["HH_time_difference"])
        total = [h*(np_v[i]+(par_lambda*q_v+dlambda*delta_q)*hh[i]) for i in range(4)]
        return total,{"gstar":gs,"vstar":vs,"pull_w":pull,"pull_w_theta":pull_v,
                      "re_minus1":rem1,"re_theta":re_v,"kHe_identity":kHe_identity,"kHe":kHe,
                      "D_kHe":dkHe,"He_correction_theta_per_second":he_v,
                      "nonphoto_time_theta_per_second":np_v,"HH_time_theta_per_second":q_v,
                      "HH_time_explicit_forcing":scale(h*dlambda*delta_q,hh)}

    results = {}
    for parameter,slot in (("lambda","U"),("b","V")):
        v = [raw(z) for z in first[slot]]
        yt = [raw(z) for z in p14["gas_response"][slot]]
        ft = [raw(z) for z in full[slot]]
        dlambda,db = I(parameter=="lambda"),I(parameter=="b")
        gd1,gd2 = [D(z,w) for z,w in zip(g1,v)], [D(z,w) for z,w in zip(y,yt)]
        bd = D(I(0,1),db)
        Z0d = [D(z) for z in Z0]
        RZ0,R2Z0,dRZ0 = R(Z0d),R(R(Z0d)),deltaR(Z0d)
        Q1 = [z+bd*j for z,j in zip(RZ0,Jbirth)]
        D1 = [1+(1-gd1[0])*(h*a) for a in a1]
        D2 = [1+(1-gd2[0])*(h*a) for a in a2]
        DF = [1+(1-gd2[0])*(2*h*a) for a in a2]
        A1,A,AF = [[1/z for z in row] for row in (D1,D2,DF)]
        tau = [(1-gd2[0])*(h*a) for a in a2]
        L,LF = [t/den for t,den in zip(tau,D2)], [2*t/den for t,den in zip(tau,DF)]
        C1 = [t*aa*aa*af for t,aa,af in zip(tau,A,AF)]
        C2 = [t*c1 for t,c1 in zip(tau,C1)]
        Z1 = [a*z for a,z in zip(A1,Q1)]
        for j in range(33):
            Q1[j] = Q1[j].meet(raw(firstphot["groups"][j]["incoming"]["value"]),
                               raw(firstphot["groups"][j]["incoming"][slot]))
            Z1[j] = Z1[j].meet(raw(firstphot["groups"][j]["outgoing_joint"]["value"]),
                               raw(firstphot["groups"][j]["outgoing_joint"][slot]))
        Q2 = [z+bd*j for z,j in zip(R(Z1),Jbirth)]
        for j in range(33):
            Q2[j] = Q2[j].meet(raw(p14["photon_state"]["incoming"]["value"][j]),
                               raw(p14["photon_state"]["incoming"][slot][j]))
        P2 = [l*z for l,z in zip(L,Q2)]
        for j in range(33):
            P2[j] = P2[j].meet(raw(p14["photon_state"]["absorbed"]["value"][j]),
                               raw(p14["photon_state"]["absorbed"][slot][j]))
        bt = add(mv(Jy,yt),scale(dlambda*qy["value"],hh))
        st = add(scale(h,bt),VI([z.d for z in P2]))
        st = [z.meet(yt[k]-v[k]) for k,z in enumerate(st)]
        sd = [D(z,w) for z,w in zip(ss,st)]
        dA1 = [((1-gd2[0])*(c*bits(box["sigma_bits"][j][0])*(n2-n1))-sd[0]*a1[j])*h*A1[j]*A[j]
                for j in range(33)]+[D(0),D(0)]
        dAQ = [a*z for a,z in zip(dA1,Q1)]
        commQ = [D(0) for _ in range(35)]
        for j in range(1,33):
            commQ[j-1] += (1-gd2[0])*(alpha[j]*h*(a2[j-1]-a2[j]))*A[j-1]*A[j]*Q1[j]
        rmJ = RminusI([D(z) for z in Jbirth])
        photon = {
            "opacity_change":[-z+l*w for z,l,w in zip(dAQ,L,R(dAQ))],
            "absorption_transport_commutator":[l*z for l,z in zip(L,commQ)],
            "stock_intermediate_redshift":[-l*z for l,z in zip(L,RminusI(RZ0))],
            "stock_backward_euler":[c2*z for c2,z in zip(C2,R2Z0)],
            "remap_composition":[lf*z for lf,z in zip(LF,dRZ0)],
            "birth_redshift":[bd*l*a*z for l,a,z in zip(L,A,rmJ)],
            "birth_backward_euler":[-bd*c1*j for c1,j in zip(C1,Jbirth)]}
        time_term,bridge = density_bridge(v,dlambda)
        move_endpoint = scale(-h,mv(Jy,st))
        move_curve = scale(-h,[tensor2(H12[i],ss,v)+dlambda*dot(q12["g"],ss)*hh[i] for i in range(4)])
        sectors = {"source_time":time_term,"gas_movement_endpoint":move_endpoint,
                   "gas_movement_curvature":move_curve,
                   **{name:VI([z.d for z in vec]) for name,vec in photon.items()}}
        rtheta = [sum((z[i] for z in sectors.values()),I(0)) for i in range(4)]
        mixed = [[raw(z) for z in row] for row in box["G_g_lambda" if parameter=="lambda" else "G_g_b"]]
        hess_feedback = [tensor2(Ggg[i],d,yt) for i in range(4)]
        mixed_feedback = mv(mixed,d)
        rhs = [rtheta[i]-hess_feedback[i]-mixed_feedback[i] for i in range(4)]
        dt,certificate = transfer(rhs)
        direct_subtraction = [yt[i]-ft[i] for i in range(4)]
        dt = [z.meet(w) for z,w in zip(dt,direct_subtraction)]
        det,PiFtheta = dot(le,dt),dot(le,yt)-dot(le,dt)
        T2theta = (CT*yt[3]-T2*dot(le,yt))/Pi2
        Ttheta = (CT*dt[3]-T2*det-T2theta*de-dT*PiFtheta)/PiF
        goal_row = [(CT*I(i==3)-(T2-dT)*le[i])/PiF for i in range(4)]
        goal_geometry = (-T2theta*de-dT*dot(le,yt))/PiF
        contribution = {}
        for name,rs in {**sectors,"endpoint_Hgg_feedback":scale(-1,hess_feedback),
                        "endpoint_Hgtheta_feedback":scale(-1,mixed_feedback)}.items():
            ds,_ = transfer(rs)
            contribution[name] = {"rhs":rs,"dtheta":ds,"temperature_K":dot(goal_row,ds)}
        results[parameter] = {"parameter":parameter,"inherited_slot":slot,
            "first_half_response":v,"second_half_response":yt,"full_response":ft,
            "stage_increment_theta":st,"stage_increment_independent_subtraction":[yt[k]-v[k] for k in range(4)],
            "source_time_bridge":bridge,"photon_sector_theta":{k:[z.d for z in vec] for k,vec in photon.items()},
            "residual_derivative_sectors":sectors,"r_theta":rtheta,
            "endpoint_Hgg_feedback":hess_feedback,"endpoint_Hgtheta_feedback":mixed_feedback,
            "correlated_rhs":rhs,"inverse_certificate":certificate,
            "d_theta":dt,"d_e_theta_per_H":det,"d_ne_theta_cm3":n2*det,
            "DeltaT_theta_K":Ttheta,"T2_theta_K":T2theta,"PiF_theta":PiFtheta,
            "temperature_goal_row":goal_row,"temperature_geometry_term_K":goal_geometry,
            "contributions":contribution,"independent_response_subtraction":direct_subtraction,
            "component_width_improvement":[I((w.hi-w.lo)/(z.hi-z.lo)) for z,w in zip(dt,direct_subtraction)]}
    result = {"schema":"WU088_HH_PHYS17_PARAMETER_RESPONSE_V1","status":"CANDIDATE_COMPUTED",
        "scope":{"same_COMMON":True,"same_global_lambda_b":True,"lambda":[0,1],"b":[0,1],
                 "fixed_alpha":"inherited source-aligned geometric-isotropic fixed-coefficient C2 family",
                 "derivative":"actual same-family finite endpoint difference",
                 "new_physical_source_calls":0,"new_reaction_fit_evaluations":0,"new_nonlinear_root_solves":0,"history_replays":0},
        "arithmetic":{"method":"unchanged PHYS14 Fraction primitives with outward 256-bit dyadic rounding",
                      "small_linear_solve":"exact rational 4x4 majorant only","dual_graph":"analytic first-order propagation"},
        "input_identities":inputs,"constants":{"h":h,"n1":n1,"n2":n2,"f1":f1,"f2":f2,"Deltaf":df,"rn":rn,
            "CT":CT,"CHI_H":chi,"rho":rho,"birth_M":birth_M},
        "fixed_endpoint_data":{"d":d,"DeltaT_K":dT,"Pi2":Pi2,"PiF":PiF,"T2":T2,"stage_increment":ss},
        "fixed_transfer":{"C":C,"B":B,"q":q,"S":S,"JF":JF,"I_CJF":EJ,"Ggg":Ggg},
        "responses":results,"elapsed_seconds":time.perf_counter()-tic,
        "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    path = output/"PARAMETER_RESPONSE_RESULTS.json"
    path.write_text(json.dumps(out(result),ensure_ascii=False,indent=2)+"\n")
    summary = {"status":result["status"],"elapsed_seconds":result["elapsed_seconds"],
               "peak_rss_kib":result["peak_rss_kib"],
               "responses":{p:{"d_theta":old.short(v["d_theta"]),"DeltaT_theta_K":old.short(v["DeltaT_theta_K"]),
                               "r_theta":old.short(v["r_theta"]),"stage_increment_theta":old.short(v["stage_increment_theta"]),
                               "component_width_improvement":old.short(v["component_width_improvement"]),
                               "temperature_contributions_K":{n:old.short(z["temperature_K"]) for n,z in v["contributions"].items()},
                               "temperature_geometry_term_K":old.short(v["temperature_geometry_term_K"])} for p,v in results.items()}}
    (output/"SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent15",type=pathlib.Path,required=True)
    ap.add_argument("--parent16",type=pathlib.Path,required=True)
    ap.add_argument("--output",type=pathlib.Path,required=True)
    args = ap.parse_args()
    main(args.parent15.resolve(),args.parent16.resolve(),args.output.resolve())
