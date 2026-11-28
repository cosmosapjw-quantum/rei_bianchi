#!/usr/bin/env python3
"""PHYS18: bounded correlated mixed parameter responses from frozen enclosures.

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


def main(parent15: pathlib.Path, parent16: pathlib.Path, parent17: pathlib.Path, output: pathlib.Path):
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
        inputs.append({"root": {parent15: "PHYS15", parent16: "PHYS16", parent17: "PHYS17"}[root], "path": rel,
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
        """Interval mixed jet: (value, ∂lambda, ∂b, ∂lambdab), ordinary derivatives."""
        __slots__ = ("v", "u", "b", "w")
        def __init__(self, value=0, u=0, b=0, w=0):
            if isinstance(value,D): self.v,self.u,self.b,self.w=value.v,value.u,value.b,value.w
            else: self.v,self.u,self.b,self.w=I(value),I(u),I(b),I(w)
        def __add__(self,z):
            z=D(z);return D(self.v+z.v,self.u+z.u,self.b+z.b,self.w+z.w)
        __radd__=__add__
        def __neg__(self):return D(-self.v,-self.u,-self.b,-self.w)
        def __sub__(self,z):return self+-D(z)
        def __rsub__(self,z):return D(z)+-self
        def __mul__(self,z):
            z=D(z);return D(self.v*z.v,self.u*z.v+self.v*z.u,self.b*z.v+self.v*z.b,
                            self.w*z.v+self.u*z.b+self.b*z.u+self.v*z.w)
        __rmul__=__mul__
        def reciprocal(self):
            r=1/self.v
            return D(r,-self.u*r**2,-self.b*r**2,2*self.u*self.b*r**3-self.w*r**2)
        def __truediv__(self,z):return self*D(z).reciprocal()
        def __rtruediv__(self,z):return D(z)*self.reciprocal()
        def __pow__(self,n):
            assert isinstance(n,int) and n>=0
            if n==0:return D(1)
            if n==1:return D(self)
            return D(self.v**n,n*self.v**(n-1)*self.u,n*self.v**(n-1)*self.b,
                     n*self.v**(n-1)*self.w+n*(n-1)*self.v**(n-2)*self.u*self.b)
        def meet(self,value=None,u=None,b=None,w=None):
            return D(*[z if t is None else z.meet(t) for z,t in zip((self.v,self.u,self.b,self.w),(value,u,b,w))])

    ncp = "inputs/phys14/inputs/ncp07/results/"
    box = read(parent15, ncp+"full/SOURCE_BOX.json")
    half = read(parent15, ncp+"first_half/SOURCE_BOX.json")
    comp = read(parent15, ncp+"full/SOURCE_BOX_COMPONENTS.json")
    hcomp = read(parent15,ncp+"first_half/SOURCE_BOX_COMPONENTS.json")
    centre = read(parent15, ncp+"full/SOURCE_CENTRE.json")
    ccomp = read(parent15, ncp+"full/SOURCE_CENTRE_COMPONENTS.json")
    native = read(parent15, ncp+"full/NATIVE_CONSTANT_LEAVES.json")
    p09 = read(parent15, "inputs/phys14/inputs/phys09/PROJECTED_RESULTS.json")
    p11 = read(parent15, "inputs/phys14/inputs/phys11/CARRY_RESULTS.json")
    p14 = read(parent15, "inputs/phys14/results/advance01/ADVANCE_RESULTS.json")
    uniform = read(parent15, "inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json")
    p16 = read(parent16, "checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json")
    e16 = read(parent16, "checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json")
    p17 = read(parent17,"checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json")
    contract = read(parent17,"contracts/MIXED_RESPONSE_CONTRACT.json")
    assert inputs[-2]["sha256"]=="fd4fc0fe6bcf035496270bb92f0c56c44ca43d16694cb40296087569a305e7c0"
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

    # All sensitivities refer to the same fixed-alpha family and shared parameters.
    U1,V1,W1=[[raw(z) for z in first[k]] for k in ('U','V','W')]
    U,Vv,W=[[raw(z) for z in p14['gas_response'][k]] for k in ('U','V','W')]
    UF0,VF0,WF=[[raw(z) for z in full[k]] for k in ('U','V','W')]
    du,db=[[raw(z) for z in p17['responses'][p]['d_theta']] for p in ('lambda','b')]
    su,sb=[[raw(z) for z in p17['responses'][p]['stage_increment_theta']] for p in ('lambda','b')]
    UF=[z.meet(u-dz) for z,u,dz in zip(UF0,U,du)]
    VF=[z.meet(v-dz) for z,v,dz in zip(VF0,Vv,db)]
    gd1=[D(z,u,v,w) for z,u,v,w in zip(g1,U1,V1,W1)]
    gd2=[D(z,u,v,w) for z,u,v,w in zip(y,U,Vv,W)]
    bd=D(I(0,1),0,1,0)
    Z0d=[D(z) for z in Z0]
    RZ0,R2Z0,dRZ0=R(Z0d),R(R(Z0d)),deltaR(Z0d)
    Q1=[z+bd*j for z,j in zip(RZ0,Jbirth)]
    D1=[1+(1-gd1[0])*(h*a) for a in a1]
    D2=[1+(1-gd2[0])*(h*a) for a in a2]
    DFy=[1+(1-gd2[0])*(2*h*a) for a in a2]
    A1,A,AF=[[1/z for z in row] for row in (D1,D2,DFy)]
    tau=[(1-gd2[0])*(h*a) for a in a2]
    L,LF=[t/den for t,den in zip(tau,D2)],[2*t/den for t,den in zip(tau,DFy)]
    C1=[t*aa*aa*af for t,aa,af in zip(tau,A,AF)]
    C2=[t*c1 for t,c1 in zip(tau,C1)]
    Z1=[a*z for a,z in zip(A1,Q1)]
    carry_meets=0
    for j in range(33):
        Q1[j]=Q1[j].meet(*[raw(firstphot['groups'][j]['incoming'][k]) for k in ('value','U','V','W')])
        Z1[j]=Z1[j].meet(*[raw(firstphot['groups'][j]['outgoing_joint'][k]) for k in ('value','U','V','W')])
        carry_meets+=8
    Q2=[z+bd*j for z,j in zip(R(Z1),Jbirth)]
    P1=[(1-a)*q1 for a,q1 in zip(A1,Q1)]
    for j in range(33):
        P1[j]=P1[j].meet(*[raw(firstphot['groups'][j]['absorbed'][k]) for k in ('value','U','V','W')])
        Q2[j]=Q2[j].meet(*[raw(p14['photon_state']['incoming'][k][j]) for k in ('value','U','V','W')])
        carry_meets+=8
    P2=[l*z for l,z in zip(L,Q2)]
    Z2=[a*z for a,z in zip(A,Q2)]
    for j in range(33):
        P2[j]=P2[j].meet(*[raw(p14['photon_state']['absorbed'][k][j]) for k in ('value','U','V','W')])
        Z2[j]=Z2[j].meet(*[raw(p14['photon_state']['outgoing'][k][j]) for k in ('value','U','V','W')])
        carry_meets+=8
    for j in range(2):
        Z2[33+j]=Z2[33+j].meet(*[raw(p14['photon_state']['guard'][k][j]) for k in ('value','U','V','W')])
        carry_meets+=4
    # The stage equation encloses the small mixed increment directly (M13).
    sW_direct=[w-w1 for w,w1 in zip(W,W1)]
    sW_rhs=add(scale(h,add(add(mv(Jy,W),[tensor2(Hy[i],U,Vv) for i in range(4)]),
                          scale(dot(qy['g'],Vv),hh))),VI([z.w for z in P2]))
    sW=[z.meet(w) for z,w in zip(sW_rhs,sW_direct)]
    sd=[D(z,u,v,w) for z,u,v,w in zip(ss,su,sb,sW)]
    zeta=[((1-gd2[0])*(c*bits(box['sigma_bits'][j][0])*(n2-n1))-sd[0]*a1[j])*h
          for j in range(33)]+[D(0),D(0)]
    dA1=[z*a1v*av for z,a1v,av in zip(zeta,A1,A)]
    dAQ=[a*z for a,z in zip(dA1,Q1)]
    commQ=[D(0) for _ in range(35)]
    for j in range(1,33):
        commQ[j-1]+=(1-gd2[0])*(alpha[j]*h*(a2[j-1]-a2[j]))*A[j-1]*A[j]*Q1[j]
    rmJ=RminusI([D(z) for z in Jbirth])
    photon={
        'opacity_change':[-z+l*w for z,l,w in zip(dAQ,L,R(dAQ))],
        'absorption_transport_commutator':[l*z for l,z in zip(L,commQ)],
        'stock_intermediate_redshift':[-l*z for l,z in zip(L,RminusI(RZ0))],
        'stock_backward_euler':[c2*z for c2,z in zip(C2,R2Z0)],
        'remap_composition':[lf*z for lf,z in zip(LF,dRZ0)],
        'birth_redshift':[bd*l*a*z for l,a,z in zip(L,A,rmJ)],
        'birth_backward_euler':[-bd*c1*j for c1,j in zip(C1,Jbirth)]}
    # Residual gas derivative with exact density pullback and only C2 data.
    timeW,bridgeW=density_bridge(W1,I(0))
    _,bridgeV=density_bridge(V1,I(0))
    H1np=[old.jet(z)['gg'] for z in hcomp['nonphoto']]
    H1q=old.jet(half['q'])['gg']
    H1=[[[H1np[i][j][k]+par_lambda*H1q[j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
    DH12=[[[H1[i][j][k]-Hy[i][j][k] for k in range(4)] for j in range(4)] for i in range(4)]
    gas_sectors={
        'source_time_linear':timeW,
        'stage_mixed_increment':scale(-h,mv(Jy,sW)),
        'stage_linear_curvature':scale(-h,[tensor2(H12[i],ss,W1) for i in range(4)]),
        'stage_Hessian_difference':scale(h,[tensor2(DH12[i],U1,V1) for i in range(4)]),
        'stage_lambda_increment':scale(-h,[tensor2(Hy[i],su,V1) for i in range(4)]),
        'stage_birth_increment':scale(-h,[tensor2(Hy[i],U,sb) for i in range(4)]),
        'HH_gradient_time':scale(h*bridgeV['HH_time_theta_per_second'],hh),
        'HH_gradient_birth_increment':scale(-h*dot(qy['g'],sb),hh),
        'HH_gradient_movement':scale(-h*tensor2(q12['gg'],ss,V1),hh)}
    sectors={**gas_sectors,**{name:VI([z.w for z in vec]) for name,vec in photon.items()}}
    rmixed=[sum((z[i] for z in sectors.values()),I(0)) for i in range(4)]
    # Reconstruct Full derivatives on the true endpoint, then intersect original exports.
    ell=[2*h*a for a in a2]
    Dy=[1+l*(1-y[0]) for l in ell]
    Df=[dy+l*d[0] for dy,l in zip(Dy,ell)]
    assert all(z.lo>0 for z in Df)
    QF=[raw(z) for z in p16['linked_factors']['QF']]
    _,JBf,HBF,qf=B_jets(gF)
    Hphoto=VI([2*l*l*qf0/(den**3) for l,qf0,den in zip(ell,QF,Df)])
    HF=[[[(-2*h*HBF[i][j][k]+(Hphoto[i] if j==k==0 else I(0))).meet(Ggg[i][j][k])
            for k in range(4)] for j in range(4)] for i in range(4)]
    Hgl=[[-2*h*hh[i]*qf['g'][j] for j in range(4)] for i in range(4)]
    Hgbvec=VI([2*l*j/(den**2) for l,j,den in zip(ell,Jbirth,Df)])
    Hgb=[[Hgbvec[i] if j==0 else I(0) for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4):
            Hgl[i][j]=Hgl[i][j].meet(raw(box['G_g_lambda'][i][j]))
            Hgb[i][j]=Hgb[i][j].meet(raw(box['G_g_b'][i][j]))
    Hlb=[I(0).meet(raw(z)) for z in box['G_lambdab']]
    # M3: direct mixed implicit forcing, evaluated independently of r_mixed.
    Bfull=add(add([tensor2(HF[i],UF,VF) for i in range(4)],mv(Hgl,VF)),mv(Hgb,UF))
    Bfull=add(Bfull,Hlb)
    rhs_direct=add(mv(JF,W),Bfull)
    dW_direct,cert_direct=transfer(rhs_direct)
    dW_subtract=[w-wf for w,wf in zip(W,WF)]
    # M4: preserve small d, d_lambda, d_b explicitly.
    npy,qjy=local_jets(y);npf,qjf=local_jets(gF)
    DHsource=[[[ -2*h*((npy[i]['gg'][j][k]-npf[i]['gg'][j][k])+
                   par_lambda*(qjy['gg'][j][k]-qjf['gg'][j][k])*hh[i]) for k in range(4)] for j in range(4)] for i in range(4)]
    DHphoto=VI([2*l**3*qf0*d[0]*(denf**2+denf*deny+deny**2)/(deny**3*denf**3)
                for l,qf0,denf,deny in zip(ell,QF,Df,Dy)])
    DHgb=VI([2*l*l*j*d[0]*(denf+deny)/(deny**2*denf**2)
             for l,j,denf,deny in zip(ell,Jbirth,Df,Dy)])
    segF=[hull(z,w) for z,w in zip(y,gF)]
    _,qseg=local_jets(segF)
    endpoint_sectors={
        'endpoint_linear_movement':scale(-1,[tensor2(Ggg[i],d,W) for i in range(4)]),
        'endpoint_source_Hessian_difference':scale(-1,[tensor2(DHsource[i],U,Vv) for i in range(4)]),
        'endpoint_photo_Hessian_difference':scale(-U[0]*Vv[0],DHphoto),
        'endpoint_lambda_defect':scale(-1,[tensor2(HF[i],du,Vv) for i in range(4)]),
        'endpoint_birth_defect':scale(-1,[tensor2(HF[i],UF,db) for i in range(4)]),
        'endpoint_HH_gradient_difference':scale(2*h*tensor2(qseg['gg'],d,Vv),hh),
        'endpoint_HH_birth_defect':scale(-1,mv(Hgl,db)),
        'endpoint_birth_gradient_difference':scale(-U[0],DHgb),
        'endpoint_birth_lambda_defect':scale(-1,mv(Hgb,du))}
    rhs_correlated=add(rmixed,[sum((z[i] for z in endpoint_sectors.values()),I(0)) for i in range(4)])
    dW_correlated,cert_corr=transfer(rhs_correlated)
    dW=[a.meet(b).meet(c0) for a,b,c0 in zip(dW_correlated,dW_direct,dW_subtract)]
    Fu,Fb=[raw(p17['responses'][p]['DeltaT_theta_K']) for p in ('lambda','b')]
    T2u,T2b=[raw(p17['responses'][p]['T2_theta_K']) for p in ('lambda','b')]
    Pu,Pb=[raw(p17['responses'][p]['PiF_theta']) for p in ('lambda','b')]
    T2w=(CT*W[3]-T2*dot(le,W)-T2u*dot(le,Vv)-T2b*dot(le,U))/Pi2
    deu,deb=dot(le,du),dot(le,db)
    row=[(CT*I(i==3)-(T2-dT)*le[i])/PiF for i in range(4)]
    geometry_parts={
        'second_endpoint_mixed_temperature':-T2w*de/PiF,
        'lambda_temperature_birth_electrons':-T2u*deb/PiF,
        'birth_temperature_lambda_electrons':-T2b*deu/PiF,
        'lambda_defect_birth_denominator':-Fu*Pb/PiF,
        'birth_defect_lambda_denominator':-Fb*Pu/PiF,
        'value_defect_mixed_denominator':-dT*dot(le,W)/PiF}
    geometry=sum(geometry_parts.values(),I(0))
    Fmixed=dot(row,dW)+geometry
    Fmixed_direct=dot(row,dW_direct)+geometry
    Fmixed_correlated=dot(row,dW_correlated)+geometry
    Fmixed_subtract=dot(row,dW_subtract)+geometry
    prior=Q('1.958485175177039e-9')
    interaction=Fmixed.meet(I(-prior,prior))
    contributions={}
    for name,rhs in {**sectors,**endpoint_sectors}.items():
        v,cc=transfer(rhs)
        contributions[name]={'rhs':rhs,'d_mixed':v,'temperature_K':dot(row,v),
                             'temperature_width_K':I((dot(row,v)).hi-(dot(row,v)).lo)}
    # Mixed conservation ledger: all 35 coordinates, number and energy guards.
    RFZ0=[r2.v-dr.v for r2,dr in zip(R2Z0,dRZ0)]
    QFd=[D(q0)+2*bd*j for q0,j in zip(RFZ0,Jbirth)]
    ZhatF=[a*qv for a,qv in zip(AF,QFd)]
    dZhat=[z-zf for z,zf in zip(Z2,ZhatF)]
    psum=[sum((v[j] for v in photon.values()),D(0)) for j in range(35)]
    def number(v):return sum(v[:33],D(0))+v[33]
    def energy(v):return sum((v[j]*E[j] for j in range(33)),D(0))+v[34]
    ledger_n=number(psum).w+number(dZhat).w
    ledger_e=energy(psum).w-(1-rho)*energy(P1).w+energy(dZhat).w
    assert ledger_n.contains_zero() and ledger_e.contains_zero()
    results={
        'schema':'WU088_HH_PHYS18_MIXED_RESPONSE_V1','status':'CANDIDATE_COMPUTED',
        'scope':{'same_COMMON':True,'same_global_lambda_b':True,'parameter_box':[[0,1],[0,1]],
                 'fixed_alpha':'inherited source-aligned geometric-isotropic C2 family',
                 'new_source_calls':0,'new_reaction_fits':0,'new_root_solves':0,'history_replays':0},
        'arithmetic':{'method':'PHYS14 exact Fraction plus outward 256-bit dyadic intervals',
                      'mixed_jet':'ordinary partial lambda,b derivatives, no factorial rescaling'},
        'input_identities':inputs,
        'bindings':{'first_half':{'U':U1,'V':V1,'W':W1},'second_half':{'U':U,'V':Vv,'W':W},
                    'full':{'U_original':UF0,'V_original':VF0,'U_intersection':UF,'V_intersection':VF,'W':WF},
                    'parameter_slots':{'gas':[0,1,2,3],'lambda':4,'b':5},'H_lambdab_export':[raw(z) for z in box['G_lambdab']],
                    'H_lambdab_source_identity':Hlb,'photon_carry_scalar_intersections':carry_meets},
        'fixed_endpoint':{'d':d,'d_lambda':du,'d_b':db,'DeltaT_K':dT,'DeltaT_lambda_K':Fu,'DeltaT_b_K':Fb,
                          'Pi2':Pi2,'PiF':PiF,'T2':T2,'T2_lambda':T2u,'T2_b':T2b,'T2_lambdab':T2w,
                          'g1':g1,'g2':y,'gF':gF,'CT':CT,'le':le,'common_goal_row':row},
        'fixed_transfer':{'C':C,'B':B,'q':q,'S':S,'JF':JF,'I_CJF':EJ,'HggF':HF,'Hg_lambdaF':Hgl,'Hg_bF':Hgb},
        'stage_increment':{'value':ss,'lambda':su,'b':sb,'mixed_direct':sW_direct,'mixed_from_stage':sW_rhs,'mixed_intersection':sW},
        'density_bridge':{'W1':bridgeW,'V1':bridgeV},
        'photon_jets':{name:[{'value':z.v,'U':z.u,'V':z.b,'W':z.w} for z in vec] for name,vec in photon.items()},
        'gas_mixed_residual_sectors':gas_sectors,'mixed_residual_sectors':sectors,'r_lambdab':rmixed,
        'endpoint_correction_sectors':endpoint_sectors,'direct_forcing':Bfull,'direct_rhs':rhs_direct,'correlated_rhs':rhs_correlated,
        'direct_inverse_certificate':cert_direct,'correlated_inverse_certificate':cert_corr,
        'd_mixed_direct':dW_direct,'d_mixed_correlated':dW_correlated,'d_mixed_original_subtraction':dW_subtract,'d_mixed_intersection':dW,
        'temperature_geometry_parts_K':geometry_parts,'temperature_geometry_K':geometry,
        'DeltaT_mixed_direct_K':Fmixed_direct,'DeltaT_mixed_correlated_K':Fmixed_correlated,
        'DeltaT_mixed_original_subtraction_K':Fmixed_subtract,'DeltaT_mixed_intersection_K':Fmixed,
        'four_corner_interaction_K':interaction,'interaction_previous_magnitude_bound_K':I(prior),
        'contributions':contributions,
        'photon_ledger':{'number_zero_residual':ledger_n,'energy_zero_residual':ledger_e,'all_35_slots':True,
                        'DeltaZhat_mixed':[z.w for z in dZhat]},
        'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    (output/'MIXED_RESPONSE_RESULTS.json').write_text(json.dumps(out(results),ensure_ascii=False,indent=2)+'\n')
    summary={k:old.short(results[k]) for k in ('status','elapsed_seconds','peak_rss_kib','d_mixed_direct','d_mixed_correlated',
                  'd_mixed_original_subtraction','d_mixed_intersection','DeltaT_mixed_direct_K','DeltaT_mixed_correlated_K',
                  'DeltaT_mixed_original_subtraction_K','DeltaT_mixed_intersection_K','four_corner_interaction_K','temperature_geometry_K')}
    summary['temperature_contributions_K']={n:old.short(v['temperature_K']) for n,v in contributions.items()}
    summary['temperature_geometry_parts_K']=old.short(geometry_parts)
    summary['ranked_contribution_widths_K']=sorted([{ 'sector':n,'width_K':old.short(v['temperature_width_K']) } for n,v in contributions.items()],key=lambda x:float(x['width_K'][1]),reverse=True)
    (output/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ('parent15','parent16','parent17','output'):ap.add_argument('--'+name,type=pathlib.Path,required=True)
    a=ap.parse_args();main(a.parent15.resolve(),a.parent16.resolve(),a.parent17.resolve(),a.output.resolve())
