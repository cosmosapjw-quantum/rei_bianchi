#!/usr/bin/env python3
"""PHYS19: bounded pure parameter curvature responses from frozen enclosures.

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


def main(parent15: pathlib.Path, parent16: pathlib.Path, parent17: pathlib.Path, parent18: pathlib.Path, output: pathlib.Path):
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
        inputs.append({"root": {parent15: "PHYS15", parent16: "PHYS16", parent17: "PHYS17", parent18: "PHYS18"}[root], "path": rel,
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
        """Ordinary pure 2-jet: (value, first theta derivative, second theta derivative)."""
        __slots__ = ("v", "u", "w")
        def __init__(self, value=0, u=0, w=0):
            if isinstance(value,D): self.v,self.u,self.w=value.v,value.u,value.w
            else: self.v,self.u,self.w=I(value),I(u),I(w)
        def __add__(self,z):
            z=D(z);return D(self.v+z.v,self.u+z.u,self.w+z.w)
        __radd__=__add__
        def __neg__(self):return D(-self.v,-self.u,-self.w)
        def __sub__(self,z):return self+-D(z)
        def __rsub__(self,z):return D(z)+-self
        def __mul__(self,z):
            z=D(z);return D(self.v*z.v,self.u*z.v+self.v*z.u,
                            self.w*z.v+2*self.u*z.u+self.v*z.w)
        __rmul__=__mul__
        def reciprocal(self):
            r=1/self.v
            return D(r,-self.u*r**2,2*self.u**2*r**3-self.w*r**2)
        def __truediv__(self,z):return self*D(z).reciprocal()
        def __rtruediv__(self,z):return D(z)*self.reciprocal()
        def __pow__(self,n):
            assert isinstance(n,int) and n>=0
            if n==0:return D(1)
            if n==1:return D(self)
            return D(self.v**n,n*self.v**(n-1)*self.u,
                     n*self.v**(n-1)*self.w+n*(n-1)*self.v**(n-2)*self.u**2)
        def meet(self,value=None,u=None,w=None):
            return D(*[z if t is None else z.meet(t) for z,t in zip((self.v,self.u,self.w),(value,u,w))])

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

    # Enforce the adopted immutable pure-curvature contract before new arithmetic.
    curv_contract=read(parent18,"contracts/CURVATURE_CONTRACT.json")
    roots={r.name:r for r in (parent15,parent16,parent17,parent18)}
    binding_checks=[]
    for binding in curv_contract["input_bindings"]:
        rel=pathlib.PurePosixPath(binding["path"])
        fpath=roots[rel.parts[0]].joinpath(*rel.parts[1:])
        blob=fpath.read_bytes();sha=hashlib.sha256(blob).hexdigest()
        assert len(blob)==binding["bytes"] and sha==binding["sha256"],str(fpath)
        binding_checks.append({"path":binding["path"],"bytes":len(blob),"sha256":sha,"match":True})
    preflight=read(parent18,"theory/CURVATURE_INPUT_PREFLIGHT.json")
    mixed=read(parent18,"checks/application/run02/results/MIXED_RESPONSE_RESULTS.json")
    J1=[[raw(z) for z in row] for row in half["A_Gg"]]
    E1=[[I(i==j)-J1[i][j] for j in range(4)] for i in range(4)]
    B1=[[Q(*map(int,z)) for z in row] for row in preflight["B1_exact"]]
    S1=[Q(*map(int,z)) for z in preflight["S1_exact"]]
    q1=Q(*map(int,preflight["q1_exact"]))
    E2=[[raw(z) for z in row] for row in p14["linear_certificates"]["L_hFg"]]
    B2=[[z.mag() for z in row] for row in E2]
    S2=[raw(z).lo for z in p14["root_certificate"]["scaled_inf_scales"]]
    q2=raw(p14["root_certificate"]["refined_contraction_upper"]).hi
    for EE,BB,SS,qq in ((E1,B1,S1,q1),(E2,B2,S2,q2)):
        assert qq<1
        assert all(EE[i][j].mag()<=BB[i][j] for i in range(4) for j in range(4))
        assert all(sum(BB[i][j]*SS[j]/SS[i] for j in range(4))<=qq for i in range(4))

    def identity_transfer(rhs,EE,BB):
        mm=solve_exact([[Q(i==j)-BB[i][j] for j in range(4)] for i in range(4)], [z.mag() for z in rhs])
        tail=[sum(BB[i][j]*mm[j] for j in range(4)) for i in range(4)]
        assert all(mm[i]>=0 and mm[i]-tail[i]==rhs[i].mag() for i in range(4))
        result=[z+I(-t,t) for z,t in zip(rhs,tail)]
        initial=list(result)
        for _ in range(3):result=[z.meet(w) for z,w in zip(result,add(rhs,mv(EE,result)))]
        return result,{"rhs":rhs,"absolute_majorant":mm,"tail":tail,"initial":initial}

    # The Full fixed-gas source Hessian and its explicit first-parameter columns.
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
    H1res=[[[raw(z) for z in row] for row in comp0] for comp0 in half['G_gg']]
    H1np=[old.jet(z)['gg'] for z in hcomp['nonphoto']]
    H1q=old.jet(half['q'])['gg']
    H1=[[[H1np[i][j][k]+par_lambda*H1q[j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
    DH12=[[[H1[i][j][k]-Hy[i][j][k] for k in range(4)] for j in range(4)] for i in range(4)]
    npy,qjy=local_jets(y);npf,qjf=local_jets(gF)
    DHsource=[[[ -2*h*((npy[i]['gg'][j][k]-npf[i]['gg'][j][k])+
                   par_lambda*(qjy['gg'][j][k]-qjf['gg'][j][k])*hh[i]) for k in range(4)] for j in range(4)] for i in range(4)]
    DHphoto=VI([2*l**3*qf0*d[0]*(denf**2+denf*deny+deny**2)/(deny**3*denf**3)
                for l,qf0,denf,deny in zip(ell,QF,Df,Dy)])
    DHgb=VI([2*l*l*j*d[0]*(denf+deny)/(deny**2*denf**2)
             for l,j,denf,deny in zip(ell,Jbirth,Df,Dy)])
    segF=[hull(z,w) for z,w in zip(y,gF)]
    _,qseg=local_jets(segF)
    row=[(CT*I(i==3)-(T2-dT)*le[i])/PiF for i in range(4)]
    responses={}
    for theta,slot,dl,dbirth in [('lambda','U',1,0),('b','V',0,1)]:
        p1=[raw(z) for z in first[slot]]
        pp=[raw(z) for z in p14['gas_response'][slot]]
        pF0=[raw(z) for z in full[slot]]
        dp=[raw(z) for z in p17['responses'][theta]['d_theta']]
        sp=[raw(z) for z in p17['responses'][theta]['stage_increment_theta']]
        pF=[z.meet(a-dv) for z,a,dv in zip(pF0,pp,dp)]
        h1gt=[[raw(z) for z in r0] for r0 in half['G_g_'+theta]]
        hFgt=Hgl if theta=='lambda' else Hgb
        rhs1=scale(-1,add([tensor2(H1res[i],p1,p1) for i in range(4)],scale(2,mv(h1gt,p1))))
        K1,cert1=identity_transfer(rhs1,E1,B1)
        forcingF=add([tensor2(HF[i],pF,pF) for i in range(4)],scale(2,mv(hFgt,pF)))
        KF,certF=transfer(scale(-1,forcingF))
        gd1=[D(z,u,w) for z,u,w in zip(g1,p1,K1)]
        bd=D(I(0,1),dbirth,0)
        Z0d=[D(z) for z in Z0]
        RZ0,R2Z0,dRZ0=R(Z0d),R(R(Z0d)),deltaR(Z0d)
        Q1=[z+bd*j for z,j in zip(RZ0,Jbirth)]
        A1=[1/(1+(1-gd1[0])*(h*a)) for a in a1]
        Z1=[a*z for a,z in zip(A1,Q1)]
        carry_meets=0
        for j in range(33):
            Q1[j]=Q1[j].meet(*[raw(firstphot['groups'][j]['incoming'][k]) for k in ('value',slot)])
            Z1[j]=Z1[j].meet(*[raw(firstphot['groups'][j]['outgoing_joint'][k]) for k in ('value',slot)])
            carry_meets+=4
        Q2=[z+bd*j for z,j in zip(R(Z1),Jbirth)]
        for j in range(33):
            Q2[j]=Q2[j].meet(*[raw(p14['photon_state']['incoming'][k][j]) for k in ('value',slot)])
            carry_meets+=2
        # C8: set K2=0 only in this forcing graph. The linear K2 term is in J2.
        gd2zero=[D(z,u,0) for z,u in zip(y,pp)]
        tau0=[(1-gd2zero[0])*(h*a) for a in a2]
        L0=[t/(1+t) for t in tau0]
        photo_rhs=VI([(l*z).w for l,z in zip(L0,Q2)])
        source_rhs=scale(h,add([tensor2(Hy[i],pp,pp) for i in range(4)],scale(2*dl*dot(qy['g'],pp),hh)))
        rhs2=add(add(K1,source_rhs),photo_rhs)
        K2,cert2=identity_transfer(rhs2,E2,B2)
        gd2=[D(z,u,w) for z,u,w in zip(y,pp,K2)]
        tau=[(1-gd2[0])*(h*a) for a in a2]
        A=[1/(1+t) for t in tau];AF=[1/(1+2*t) for t in tau]
        L=[t/(1+t) for t in tau];LF=[2*t/(1+2*t) for t in tau]
        Cph1=[t*aa*aa*af for t,aa,af in zip(tau,A,AF)]
        Cph2=[t*c1 for t,c1 in zip(tau,Cph1)]
        P1=[(1-a)*qv for a,qv in zip(A1,Q1)]
        P2=[l*z for l,z in zip(L,Q2)];Z2=[a*z for a,z in zip(A,Q2)]
        for j in range(33):
            P1[j]=P1[j].meet(*[raw(firstphot['groups'][j]['absorbed'][k]) for k in ('value',slot)])
            P2[j]=P2[j].meet(*[raw(p14['photon_state']['absorbed'][k][j]) for k in ('value',slot)])
            Z2[j]=Z2[j].meet(*[raw(p14['photon_state']['outgoing'][k][j]) for k in ('value',slot)])
            carry_meets+=6
        for j,name in enumerate(('number','energy_eV_per_H')):
            Z2[33+j]=Z2[33+j].meet(*[raw(p14['photon_state']['guard'][k][name]) for k in ('value',slot)])
            carry_meets+=2
        sK_direct=[k-k1 for k,k1 in zip(K2,K1)]
        sK_rhs=add(scale(h,add(add(mv(Jy,K2),[tensor2(Hy[i],pp,pp) for i in range(4)]),
                               scale(2*dl*dot(qy['g'],pp),hh))),VI([z.w for z in P2]))
        sK=[z.meet(w) for z,w in zip(sK_direct,sK_rhs)]
        sd=[D(z,u,w) for z,u,w in zip(ss,sp,sK)]
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
            'stock_backward_euler':[c2*z for c2,z in zip(Cph2,R2Z0)],
            'remap_composition':[lf*z for lf,z in zip(LF,dRZ0)],
            'birth_redshift':[bd*l*a*z for l,a,z in zip(L,A,rmJ)],
            'birth_backward_euler':[-bd*c1*j for c1,j in zip(Cph1,Jbirth)]}
        timeK,bridgeK=density_bridge(K1,I(0))
        _,bridgep=density_bridge(p1,I(0))
        gas_sectors={
            'source_time_linear':timeK,
            'stage_pure_increment':scale(-h,mv(Jy,sK)),
            'stage_linear_curvature':scale(-h,[tensor2(H12[i],ss,K1) for i in range(4)]),
            'stage_Hessian_difference':scale(h,[tensor2(DH12[i],p1,p1) for i in range(4)]),
            'stage_tangent_change':scale(-2*h,[tensor2(Hy[i],sp,scale(I(Q(1,2)),add(pp,p1))) for i in range(4)]),
            'HH_gradient_time':scale(2*dl*h*bridgep['HH_time_theta_per_second'],hh),
            'HH_gradient_increment':scale(-2*dl*h*dot(qy['g'],sp),hh),
            'HH_gradient_movement':scale(-2*dl*h*tensor2(q12['gg'],ss,p1),hh)}
        sectors={**gas_sectors,**{name:VI([z.w for z in vec]) for name,vec in photon.items()}}
        rpure=[sum((z[i] for z in sectors.values()),I(0)) for i in range(4)]
        rhs_direct=add(mv(JF,K2),forcingF)
        dK_direct,cert_direct=transfer(rhs_direct)
        dK_subtract=[k-kf for k,kf in zip(K2,KF)]
        balanced=[p0-d0/2 for p0,d0 in zip(pp,dp)]
        endpoint_sectors={
            'endpoint_linear_movement':scale(-1,[tensor2(Ggg[i],d,K2) for i in range(4)]),
            'endpoint_source_Hessian_difference':scale(-1,[tensor2(DHsource[i],pp,pp) for i in range(4)]),
            'endpoint_photo_Hessian_difference':scale(-pp[0]**2,DHphoto),
            'endpoint_tangent_defect':scale(-2,[tensor2(HF[i],dp,balanced) for i in range(4)]),
            'endpoint_HH_gradient_difference':scale(4*dl*h*tensor2(qseg['gg'],d,pp),hh),
            'endpoint_HH_gradient_defect':scale(-2*dl,mv(Hgl,dp)),
            'endpoint_birth_gradient_difference':scale(-2*dbirth*pp[0],DHgb),
            'endpoint_birth_gradient_defect':scale(-2*dbirth,mv(Hgb,dp))}
        rhs_corr=add(rpure,[sum((z[i] for z in endpoint_sectors.values()),I(0)) for i in range(4)])
        dK_corr,cert_corr=transfer(rhs_corr)
        dK=[a.meet(b).meet(c0) for a,b,c0 in zip(dK_corr,dK_direct,dK_subtract)]
        Ft=raw(p17['responses'][theta]['DeltaT_theta_K'])
        T2t=raw(p17['responses'][theta]['T2_theta_K'])
        Pt=raw(p17['responses'][theta]['PiF_theta'])
        T2pp=(CT*K2[3]-T2*dot(le,K2)-2*T2t*dot(le,pp))/Pi2
        geometry_parts={
            'second_endpoint_pure_temperature':-T2pp*de/PiF,
            'temperature_electron_cross':-2*T2t*dot(le,dp)/PiF,
            'defect_denominator_cross':-2*Ft*Pt/PiF,
            'value_defect_pure_denominator':-dT*dot(le,K2)/PiF}
        geometry=sum(geometry_parts.values(),I(0))
        Fpure=dot(row,dK)+geometry
        TF=T2-dT;TFt=T2t-Ft
        TFpp=(CT*KF[3]-TF*dot(le,KF)-2*TFt*dot(le,pF))/PiF
        Fpure_subT=T2pp-TFpp
        Fpure=Fpure.meet(Fpure_subT)
        contributions={}
        for name,rhs in {**sectors,**endpoint_sectors}.items():
            vec,cert=transfer(rhs);temp=dot(row,vec)
            contributions[name]={'rhs':rhs,'d_pure':vec,'temperature_K':temp,'temperature_width_K':I(temp.hi-temp.lo)}
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
        assert all(z.w.lo==z.w.hi==0 for z in P2[33:])
        # The nonzero incoming/outgoing guard curvature is retained as transported data.
        responses[theta]={
            'theta':theta,'first_derivative_slot':slot,'delta_lambda':dl,'delta_birth':dbirth,
            'bindings':{'p1':p1,'p2':pp,'pF_original':pF0,'pF':pF,'d_theta':dp,'stage_increment_theta':sp},
            'first_half':{'rhs':rhs1,'K':K1,'inverse_certificate':cert1},
            'full':{'forcing':forcingF,'K':KF,'inverse_certificate':certF},
            'second_half':{'rhs':rhs2,'source_rhs':source_rhs,'photo_rhs_excluding_linear_K2':photo_rhs,'K':K2,'inverse_certificate':cert2},
            'stage_increment':{'pure_subtraction':sK_direct,'pure_from_stage':sK_rhs,'pure_intersection':sK},
            'photon_carry_scalar_intersections':carry_meets,
            'photon_jets':{name:[{'value':z.v,'theta':z.u,'theta_theta':z.w} for z in vec] for name,vec in {'Q1':Q1,'Z1':Z1,'Q2':Q2,'P1':P1,'P2':P2,'Z2':Z2}.items()},
            'photon_sector_pure':{name:[z.w for z in vec] for name,vec in photon.items()},
            'density_bridge':{'K1':bridgeK,'p1':bridgep},
            'gas_residual_sectors':gas_sectors,'residual_sectors':sectors,'r_theta_theta':rpure,
            'endpoint_correction_sectors':endpoint_sectors,'direct_rhs':rhs_direct,'correlated_rhs':rhs_corr,
            'direct_inverse_certificate':cert_direct,'correlated_inverse_certificate':cert_corr,
            'd_pure_direct':dK_direct,'d_pure_correlated':dK_corr,'d_pure_endpoint_subtraction':dK_subtract,'d_pure_intersection':dK,
            'T2_pure_K':T2pp,'TF_pure_K':TFpp,'temperature_geometry_parts_K':geometry_parts,'temperature_geometry_K':geometry,
            'F_pure_direct_K':dot(row,dK_direct)+geometry,'F_pure_correlated_K':dot(row,dK_corr)+geometry,
            'F_pure_endpoint_subtraction_K':dot(row,dK_subtract)+geometry,'F_pure_temperature_subtraction_K':Fpure_subT,
            'F_pure_K':Fpure,'contributions':contributions,
            'ledger':{'number_zero_residual':ledger_n,'energy_zero_residual':ledger_e,'all_35_slots':True,
                      'absorption_guard_pure_exact_zero':True,'incoming_guard_pure':[z.w for z in Q2[33:]],
                      'outgoing_guard_pure':[z.w for z in Z2[33:]]}}
    Fll=responses['lambda']['F_pure_K'];Fbb=responses['b']['F_pure_K']
    Mll,Mbb=Fll.mag(),Fbb.mag()
    cll,cbb=(Fll.lo+Fll.hi)/2,(Fbb.lo+Fbb.hi)/2
    rll,rbb=(Fll.hi-Fll.lo)/2,(Fbb.hi-Fbb.lo)/2
    # All coefficients are coupled through the same alpha and the same fixed COMMON.
    finite={
        'F_lambda_lambda_K':Fll,'F_b_b_K':Fbb,
        'M_lambda_lambda_K':I(Mll),'M_b_b_K':I(Mbb),
        'pure_midpoints_K':{'lambda_lambda':I(cll),'b_b':I(cbb)},
        'pure_radii_K':{'lambda_lambda':I(rll),'b_b':I(rbb)},
        'bilinear_signed_error_formula':'-lambda*(1-lambda)/2*[Fll] - b*(1-b)/2*[Fbb]',
        'bilinear_uniform_abs_error_bound_K':I((Mll+Mbb)/8),
        'bilinear_center_signed_error_K':-(Fll+Fbb)/8,
        'quadratic_corrected_model':'L_bilinear F - cll*lambda*(1-lambda)/2 - cbb*b*(1-b)/2',
        'quadratic_corrected_uniform_abs_error_bound_K':I((rll+rbb)/8),
        'anchor_F00_K':dT,
        'chord_a_lambda_K':raw(p17['responses']['lambda']['DeltaT_theta_K']),
        'chord_a_b_K':raw(p17['responses']['b']['DeltaT_theta_K']),
        'interaction_coefficient_K':raw(mixed['four_corner_interaction_K']),
        'same_family_coupling':'All coefficients refer to one fixed alpha, same COMMON and shared lambda,b; marginal intervals are not independent physical samples.',
        'corner_solves':0,
        'coefficient_resolution':'F00 uses inherited global endpoint enclosure; chords use global first derivative integrals; PHYS18 supplies the mixed interaction integral.'}
    results={'schema':'WU088_HH_PHYS19_PURE_CURVATURE_V1','status':'CANDIDATE_COMPUTED',
        'scope':curv_contract['family_scope'],
        'arithmetic':{'method':'PHYS14 exact Fraction and outward 256-bit dyadic intervals','pure_jet':'ordinary second derivative; Taylor coefficient is K/2'},
        'input_identities':inputs,'input_binding_checks':binding_checks,
        'fixed_endpoint':{'g1':g1,'g2':y,'gF':gF,'d':d,'DeltaT_K':dT,'Pi2':Pi2,'PiF':PiF,'T2':T2,'le':le,'CT':CT,'goal_row':row},
        'inverse_bindings':{'first_half':{'J':J1,'E':E1,'B':B1,'S':S1,'q':q1},
                            'full':{'C':C,'B':B,'S':S,'q':q,'JF':JF,'I_CJF':EJ},
                            'second_half':{'E':E2,'B':B2,'S':S2,'q':q2}},
        'responses':responses,'finite_response':finite,
        'execution_counters':{'source_calls':0,'reaction_fits':0,'nonlinear_root_solves':0,'history_replays':0,'heavy_queue':[],'launch':False},
        'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    (output/'CURVATURE_RESULTS.json').write_text(json.dumps(out(results),ensure_ascii=False,indent=2)+'\n')
    summary={'status':results['status'],'finite_response':old.short(finite),'elapsed_seconds':results['elapsed_seconds'],'peak_rss_kib':results['peak_rss_kib'],'responses':{}}
    for theta,res in responses.items():
        summary['responses'][theta]={k:old.short(res[k]) for k in ('F_pure_K','F_pure_direct_K','F_pure_correlated_K','F_pure_endpoint_subtraction_K','F_pure_temperature_subtraction_K','temperature_geometry_K')}
        summary['responses'][theta]['temperature_contributions_K']={n:old.short(v['temperature_K']) for n,v in res['contributions'].items()}
        summary['responses'][theta]['ranked_widths_K']=sorted([{'sector':n,'width':float(v['temperature_width_K'].hi)} for n,v in res['contributions'].items()],key=lambda z:z['width'],reverse=True)
    (output/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ('parent15','parent16','parent17','parent18','output'):ap.add_argument('--'+name,type=pathlib.Path,required=True)
    a=ap.parse_args();main(a.parent15.resolve(),a.parent16.resolve(),a.parent17.resolve(),a.parent18.resolve(),a.output.resolve())
