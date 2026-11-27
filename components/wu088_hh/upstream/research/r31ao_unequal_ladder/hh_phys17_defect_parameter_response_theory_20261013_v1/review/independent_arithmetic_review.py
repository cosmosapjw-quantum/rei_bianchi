#!/usr/bin/env python3
"""Independent PHYS17 stored-data arithmetic review.

This program imports no candidate program and no PHYS14 arithmetic helper.
Arithmetic uses exact rational interval endpoints without intermediate dyadic
rounding. A 24-term Leibniz determinant and Cramer's rule replace the candidate
Gaussian elimination. Only stored enclosures are read; no physical source,
reaction fit, nonlinear root, or history execution occurs.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, pathlib, re, resource, struct, sys, time
from fractions import Fraction as F

class R:
    __slots__=("lo","hi")
    def __init__(self,a=0,b=None):
        if isinstance(a,R): self.lo,self.hi=a.lo,a.hi; return
        if isinstance(a,dict):
            if "exact" in a:
                a,b=(F(*map(int,a["exact"][z])) for z in ("lo","hi"))
            else: a,b=(bits(a[z]) for z in ("lo_bits","hi_bits"))
        self.lo,self.hi=F(a),F(a if b is None else b)
        assert self.lo<=self.hi
    def __add__(self,b): b=R(b); return R(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self): return R(-self.hi,-self.lo)
    def __sub__(self,b): return self+-R(b)
    def __rsub__(self,b): return R(b)+-self
    def __mul__(self,b):
        b=R(b); v=[a*c for a in (self.lo,self.hi) for c in (b.lo,b.hi)]
        return R(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=R(b); assert not b.lo<=0<=b.hi
        return self*R(1/b.hi,1/b.lo)
    def __rtruediv__(self,b): return R(b)/self
    def __pow__(self,n):
        assert n>=0 and isinstance(n,int)
        if n==0:return R(1)
        if n%2 and self.lo<=0<=self.hi:return R(self.lo**n,self.hi**n)
        if n%2==0 and self.lo<=0<=self.hi:return R(0,max(abs(self.lo),abs(self.hi))**n)
        a,b=self.lo**n,self.hi**n; return R(min(a,b),max(a,b))
    def meet(self,b):b=R(b);return R(max(self.lo,b.lo),min(self.hi,b.hi))
    def holds(self,b):b=R(b);return self.lo<=b.lo and b.hi<=self.hi
    def overlaps(self,b):b=R(b);return self.lo<=b.hi and b.lo<=self.hi
    def mag(self):return max(abs(self.lo),abs(self.hi))
    def point(self):assert self.lo==self.hi;return self.lo

def bits(s): return F(struct.unpack(">d",bytes.fromhex(s))[0])
def V(x):return [R(z) for z in x]
def M(x):return [V(z) for z in x]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),R())
def mv(a,b):return [dot(x,b) for x in a]
def add(a,b):return [x+y for x,y in zip(a,b)]
def tensor(h,a,b):return sum((R(h[j][k])*a[j]*b[k] for k in range(4) for j in range(4)),R())
def det(a):
    n=len(a);answer=F()
    for p in itertools.permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=F(sign)
        for i in range(n):term*=a[i][p[i]]
        answer+=term
    return answer
def cramer(a,b):
    denominator=det(a);assert denominator
    return [det([[b[i] if k==j else a[i][k] for k in range(4)] for i in range(4)])/denominator for j in range(4)]
def contain(a,b):assert all(R(x).holds(y) for x,y in zip(a,b))
def overlap(a,b):assert all(R(x).overlaps(y) for x,y in zip(a,b))
def report_interval(x):return {"lo":str(x.lo),"hi":str(x.hi),"display":[float(x.lo),float(x.hi)]}

def main(args):
    tic=time.perf_counter();checks=[];inputs=[]
    def read(root,rel):
        p=root/rel;data=p.read_bytes()
        inputs.append({"path":str(p),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
        return json.loads(data)
    def check(name,fn):
        try:
            detail=fn()
            checks.append({"id":name,"result":"PASS","detail":detail})
        except Exception as exc:
            checks.append({"id":name,"result":"FAIL","error_class":type(exc).__name__,"error":str(exc)})
    p15,p16,p17=args.parent15.resolve(),args.parent16.resolve(),args.parent17.resolve()
    candidate=read(p17,"checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json")
    forcing=read(p17,"checks/application/forcing01/results/FORCING_FEEDBACK_RESULTS.json")
    neumann=read(p17,"checks/application/neumann02/results/DERIVATIVE_NEUMANN_RESULTS.json")
    corollaries=read(p17,"theory/PARAMETER_COROLLARIES.json")
    ncp="inputs/phys14/inputs/ncp07/results/"
    full=read(p15,ncp+"full/SOURCE_BOX.json")
    centre=read(p15,ncp+"full/SOURCE_CENTRE.json")
    half=read(p15,ncp+"first_half/SOURCE_BOX.json")
    leaves=read(p15,ncp+"full/NATIVE_CONSTANT_LEAVES.json")
    uniform=read(p15,"inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json")
    p09=read(p15,"inputs/phys14/inputs/phys09/PROJECTED_RESULTS.json")
    p14=read(p15,"inputs/phys14/results/advance01/ADVANCE_RESULTS.json")
    p16a=read(p16,"checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json")
    p16e=read(p16,"checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json")
    wl=read(p17,"checks/wolfram/WOLFRAM_XACT_EXECUTION.json")
    original_first=next(x for x in p09["stages"] if x["stage"]=="first_half")
    original_full=next(x for x in p09["stages"] if x["stage"]=="full")
    const={k:R(v) for k,v in candidate["constants"].items()}
    fixed=candidate["fixed_endpoint_data"];ft=candidate["fixed_transfer"]
    C=M(ft["C"]);B=[[R(z).point() for z in row] for row in ft["B"]]
    q=R(ft["q"]).point();S=[R(z).point() for z in ft["S"]]
    A=[[F(i==j)-B[i][j] for j in range(4)] for i in range(4)]
    EJ=M(ft["I_CJF"]);GG=ft["Ggg"]
    d=V(fixed["d"]);de=dot([R(1),const["f2"],2*const["f2"],R(0)],d)
    le=[R(1),const["f2"],2*const["f2"],R(0)]
    y=V(p16a["root_boxes"]["g2"]);gF=V(p16a["root_boxes"]["gF"])
    def identities():
        for x in candidate["input_identities"]:
            r=p15 if x["root"]=="PHYS15" else p16
            b=(r/x["path"]).read_bytes()
            assert len(b)==x["bytes"] and hashlib.sha256(b).hexdigest()==x["sha256"]
        return {"identities_checked":len(candidate["input_identities"])}
    check("immutable_candidate_input_identities",identities)
    def constants():
        expected={"h":bits(half["dt_bits"]),"n1":bits(half["nH_bits"]),"n2":bits(full["nH_bits"]),
                  "f1":bits(half["nHe_stored_bits"])/bits(half["nH_bits"]),
                  "f2":bits(full["nHe_stored_bits"])/bits(full["nH_bits"]),
                  "CT":2*bits(leaves["ev_erg_bits"])/(3*bits(leaves["kb_bits"])),
                  "CHI_H":bits(leaves["CHI_bits"][0])}
        expected["Deltaf"]=expected["f1"]-expected["f2"];expected["rn"]=expected["n1"]/expected["n2"]
        for k,v in expected.items():assert const[k].holds(v)
        assert expected["Deltaf"]<0 and bits(full["dt_bits"])==2*expected["h"]
        assert R(fixed["PiF"]).lo>0
        return {"binary64_or_exact_ratio_constants":len(expected),"PiF_positive":True}
    check("native_constants_and_finite_denominator",constants)
    def preconditioner():
        for i in range(4):
            assert S[i]==F(uniform["radius"][i])
            for j in range(4):
                assert C[i][j].point()==F(uniform["fixed_C"][i][j])
                assert B[i][j]==R(uniform["B"][i][j]).hi
            assert sum(B[i][j]*S[j]/S[i] for j in range(4))<=q
        assert q==R(uniform["q"]).hi and 0<=q<1
        assert det(A)>0
        return {"det_I_minus_B":str(det(A)),"q":float(q)}
    check("unchanged_C_B_q_S_and_majorant_invertibility",preconditioner)
    def derivative_slots():
        count=0
        for i in range(4):
            residual=full["G"][i]
            for j in range(4):
                for k in range(4):
                    a,b=R(full["G_gg"][i][j][k]),R(residual["signed_hessian"][j][k])
                    assert a.lo==b.lo and a.hi==b.hi
                    assert R(GG[i][j][k]).holds(a);count+=1
                for label,slot in (("G_g_lambda",4),("G_g_b",5)):
                    a,b=R(full[label][i][j]),R(residual["signed_hessian"][j][slot])
                    assert a.lo==b.lo and a.hi==b.hi;count+=1
        return {"export_slot_equalities":count}
    check("original_residual_Hessian_and_mixed_slots",derivative_slots)
    def jacobian_enclosure():
        gc=[R(F(z)) for z in uniform["center"]]
        for i in range(4):
            for j in range(4):
                mean=R(centre["A_Gg"][i][j])+dot(V(full["G_gg"][i][j]),[gF[k]-gc[k] for k in range(4)])
                expected=mean.meet(full["A_Gg"][i][j])
                assert R(ft["JF"][i][j]).holds(expected)
                bare=R(i==j)-dot(C[i],[R(ft["JF"][k][j]) for k in range(4)])
                assert EJ[i][j].holds(bare.meet(R(-B[i][j],B[i][j])))
        return {"entries":16,"same_JF_tail_intersections":16}
    check("Full_Jacobian_centered_inclusion_and_signed_tail",jacobian_enclosure)

    def independent_transfer(rhs,initial=None,record_cr=None):
        cr=mv(C,V(rhs)) if record_cr is None else V(record_cr)
        m=cramer(A,[x.mag() for x in cr])
        assert all(x>=0 for x in m)
        tail=[sum(B[i][j]*m[j] for j in range(4)) for i in range(4)]
        z=[cr[i]+R(-tail[i],tail[i]) for i in range(4)] if initial is None else V(initial)
        for _ in range(3):z=[x.meet(y) for x,y in zip(z,add(cr,mv(EJ,z)))]
        return cr,m,tail,z

    for param,resp in candidate["responses"].items():
        v,u,uf=V(resp["first_half_response"]),V(resp["second_half_response"]),V(resp["full_response"])
        st=V(resp["stage_increment_theta"]);dt=V(resp["d_theta"])
        slot="U" if param=="lambda" else "V"
        def carry(v=v,u=u,uf=uf,slot=slot):
            for given,original in ((v,V(original_first[slot])),(u,V(p14["gas_response"][slot])),(uf,V(original_full[slot]))):
                for a,b in zip(given,original):assert a.lo==b.lo and a.hi==b.hi
            return {"gas_components":12}
        check(param+"_inherited_stage_responses",carry)
        def bridge_checks(resp=resp,v=v,u=u,st=st):
            contain([u[i]-v[i] for i in range(4)],st)
            b=resp["source_time_bridge"];g=V(p16a["root_boxes"]["g1"]);gs=V(b["gstar"]);vs=V(b["vstar"])
            f1,f2,df,rn=const["f1"],const["f2"],const["Deltaf"],const["rn"]
            le1=[R(1),f1,2*f1,R(0)]
            sg=g[1]+2*g[2];sgt=v[1]+2*v[2];e1=dot(le1,g);e2=dot(le,g);pi1=1+f1+e1
            pv=-df*(((1+sg)*v[3]+g[3]*sgt)/pi1-g[3]*(1+sg)*dot(le1,v)/(pi1**2))
            rv=rn*df*(e2*sgt-sg*dot(le,v))/(e2**2)
            assert R(b["pull_w_theta"]).holds(pv)
            assert R(b["re_theta"]).holds(rv)
            assert gs[3].holds(g[3]+R(b["pull_w"]))
            assert vs[3].holds(v[3]+R(b["pull_w_theta"]))
            X=V(p14["root_certificate"]["domain_X"]);contain(X,gs)
            assert R(b["kHe"]).hi<=0
            assert R(b["kHe_identity"]).holds(R(b["kHe"]))
            assert R(p16a["source_bridge"]["kwHe"]).holds(R(b["kHe"]))
            return {"small_factor_preserved":True,"gstar_in_original_X":True}
        check(param+"_correlated_increment_and_density_pullback",bridge_checks)
        def residual_sum(resp=resp):
            sectors=resp["residual_derivative_sectors"];p=resp["photon_sector_theta"]
            heat=[R(bits(z[0])) for z in full["heat_bits"]]
            for name,z in p.items():
                row=V(z)
                projected=[sum(row[:33],R()),R(0),R(0),dot(heat,row[:33])]
                contain(sectors[name],projected)
                assert len(z)==35 and R(z[33]).point()==0 and R(z[34]).point()==0
            contain(resp["r_theta"],[sum((R(z[i]) for z in sectors.values()),R()) for i in range(4)])
            return {"photon_sectors":len(p),"gas_residual_sectors":len(sectors),"original_groups":33,"guards":2}
        check(param+"_residual_sector_sum_and_photon_projection",residual_sum)
        def p2_feedback(resp=resp,u=u,param=param):
            hf=[tensor(GG[i],d,u) for i in range(4)]
            mf=mv(M(full["G_g_lambda" if param=="lambda" else "G_g_b"]),d)
            contain(resp["endpoint_Hgg_feedback"],hf)
            contain(resp["endpoint_Hgtheta_feedback"],mf)
            rhs=[R(resp["r_theta"][i])-R(resp["endpoint_Hgg_feedback"][i])-R(resp["endpoint_Hgtheta_feedback"][i]) for i in range(4)]
            contain(resp["correlated_rhs"],rhs)
            return {"Hessian_products":64,"mixed_products":16,"sign":"minus both feedback terms"}
        check(param+"_P2_signed_feedback_and_rhs",p2_feedback)
        def majorant(resp=resp):
            cert=resp["inverse_certificate"];cr=mv(C,V(resp["correlated_rhs"]))
            contain(cert["C_rhs"],cr)
            crr=V(cert["C_rhs"]);m=cramer(A,[x.mag() for x in crr])
            contain(cert["absolute_majorant"],[R(x) for x in m])
            tail=[sum(B[i][j]*m[j] for j in range(4)) for i in range(4)]
            contain(cert["tail"],[R(x) for x in tail])
            contain(cert["initial"],[crr[i]+R(-tail[i],tail[i]) for i in range(4)])
            return {"method":"Cramer 24-term exact determinants","nonnegative_majorant":all(x>=0 for x in m)}
        check(param+"_independent_Cramer_inverse_certificate",majorant)
        def endpoint_transfer(resp=resp,u=u,uf=uf):
            cert=resp["inverse_certificate"]
            _,_,_,z=independent_transfer(resp["correlated_rhs"],initial=cert["initial"],record_cr=cert["C_rhs"])
            z=[z[i].meet(u[i]-uf[i]) for i in range(4)]
            contain(resp["d_theta"],z)
            contain(resp["independent_response_subtraction"],V(resp["d_theta"]))
            return {"signed_refinement_steps":3,"terminal_independent_carry_intersection":True}
        check(param+"_signed_inverse_refinement_and_final_response",endpoint_transfer)
        def observables(resp=resp,u=u,dt=dt,param=param):
            e=dot(le,dt)
            contain([resp["d_e_theta_per_H"],resp["d_ne_theta_cm3"]],[e,const["n2"]*R(resp["d_e_theta_per_H"])])
            pt=dot(le,u)-e
            assert R(resp["PiF_theta"]).holds(pt)
            T2,Pi2,PiF=map(R,(fixed["T2"],fixed["Pi2"],fixed["PiF"]))
            dT=R(fixed["DeltaT_K"])
            t2theta=(const["CT"]*u[3]-T2*dot(le,u))/Pi2
            assert R(resp["T2_theta_K"]).holds(t2theta)
            t=(const["CT"]*dt[3]-T2*R(resp["d_e_theta_per_H"])-R(resp["T2_theta_K"])*de-dT*R(resp["PiF_theta"]))/PiF
            assert R(resp["DeltaT_theta_K"]).holds(t)
            value=R(resp["DeltaT_theta_K"])
            assert value.hi<0 if param=="lambda" else value.lo>0
            return {"DeltaT_theta_K":report_interval(value),"sign_margin_K":float(-value.hi if param=="lambda" else value.lo)}
        check(param+"_finite_temperature_P4_and_sign",observables)
        def contributions(resp=resp):
            row=V(resp["temperature_goal_row"]);number=0
            for sector in resp["contributions"].values():
                _,_,_,z=independent_transfer(sector["rhs"])
                contain(sector["dtheta"],z)
                assert R(sector["temperature_K"]).holds(dot(row,V(sector["dtheta"])))
                number+=1
            return {"same_JF_transfers":number,"same_goal_row":True}
        check(param+"_same_adjoint_sector_transfers",contributions)
        def forcing_consistency(param=param,resp=resp):
            f=forcing["responses"][param];count=0
            for name,rv in resp["photon_sector_theta"].items():
                for i,z in enumerate(rv):
                    total=R(f["explicit_photon"][name][i])+R(f["feedback_photon"][name][i])
                    assert R(z).overlaps(total);count+=1
            assert count==f["photon_manual_dual_consistency_intersections"]==245
            for i in range(4):assert R(resp["correlated_rhs"][i]).overlaps(R(f["explicit_correlated_rhs"][i])+R(f["feedback_correlated_rhs"][i]))
            explicit,feedback=R(f["explicit_DeltaT_theta_K"]),R(f["feedback_DeltaT_theta_K"])
            assert explicit.hi<0 if param=="lambda" else explicit.lo>0
            assert feedback.hi<0
            assert R(f["combined_DeltaT_theta_K"]).holds(explicit+feedback)
            intersection=R(f["combined_DeltaT_theta_K"]).meet(resp["DeltaT_theta_K"])
            actual=R(f["intersection_with_run02_DeltaT_theta_K"])
            assert actual.lo==intersection.lo and actual.hi==intersection.hi
            return {"photon_intersections":count,"correlated_rhs_intersections":4,"explicit_sign":("negative" if param=="lambda" else "positive"),"feedback_sign":"negative"}
        check(param+"_explicit_forcing_feedback_and_manual_dual_consistency",forcing_consistency)
        def forcing_transfer(param=param,resp=resp):
            f=forcing["responses"][param];row=V(resp["temperature_goal_row"])
            for prefix in ("explicit","feedback"):
                _,_,_,z=independent_transfer(f[prefix+"_correlated_rhs"])
                contain(f[prefix+"_d_theta"],z)
                tv=dot(row,V(f[prefix+"_d_theta"]))
                if prefix=="feedback":tv+=R(resp["temperature_geometry_term_K"])
                assert R(f[prefix+"_DeltaT_theta_K"]).holds(tv)
            return {"independent_transfers":2,"geometry_assignment":"state feedback"}
        check(param+"_explicit_feedback_inverse_transfer",forcing_transfer)

    def finite_neumann():
        lh=R(p16e["L_H"]).hi
        inherited=R(p16e["a_after_endpoint_intersection"]).hi
        a=max(inherited,max(d[i].mag()/S[i] for i in range(4)))
        geom=1+q+q*q
        for key,expected in (("q",q),("L_H",lh),("a_inherited",inherited),
                             ("a_endpoint_defect",a),("outward_copy_expansion",a-inherited),
                             ("sum_q_0_to_2",geom)):
            assert R(neumann[key]).holds(expected),key
        contain(neumann["S"],[R(x) for x in S])
        errors={}
        for parameter,item in neumann["responses"].items():
            origin=candidate["responses"][parameter]
            cf=V(item["C_f_theta"])
            contain(cf,mv(C,V(origin["correlated_rhs"])))
            norm=max(cf[i].mag()/S[i] for i in range(4))
            atheta=norm/(1-q)
            epsF=q**3*atheta
            epsy=(q**3+lh*a*geom)*atheta
            goal=sum(R(z).mag()*S[i] for i,z in enumerate(origin["temperature_goal_row"]))
            expected={"C_f_theta_scaled_norm_upper":norm,"a_theta_upper":atheta,
                      "JF_Neumann_error_upper_scaled":epsF,"Jy_Neumann_error_upper_scaled":epsy,
                      "goal_row_weighted_one_norm_upper_K":goal,
                      "JF_temperature_derivative_surrogate_error_upper_K":goal*epsF,
                      "Jy_temperature_derivative_surrogate_error_upper_K":goal*epsy,
                      "Jy_endpoint_change_factor_upper":lh*a*geom}
            assert item["m"]==2
            for key,value in expected.items():assert R(item[key]).holds(value),(parameter,key)
            errors[parameter]={"JF_error_K":float(goal*epsF),"Jy_error_K":float(goal*epsy)}
        return {"m":2,"response_parameters":2,"Jacobian_difference_factor":1,
                "outward_copy_expansion":str(a-inherited),"temperature_errors":errors}
    check("finite_Neumann_derivative_and_endpoint_change_bounds",finite_neumann)

    def monotonic_corollaries():
        la=R(candidate["responses"]["lambda"]["DeltaT_theta_K"])
        birth=R(candidate["responses"]["b"]["DeltaT_theta_K"])
        expected={"lambda_derivative":la,"b_derivative":birth,
                  "constant_defect_level_slope_db_dlambda":-la/birth,
                  "fixed_alpha_parameter_rectangle_total_span_K":birth-la,
                  "four_corner_mixed_contrast_prior_bound_K":R(-(la.hi-la.lo),la.hi-la.lo)}
        for key,value in expected.items():
            data=corollaries[key]
            got=R(F(*map(int,data["exact"][0])),F(*map(int,data["exact"][1])))
            assert got.lo==value.lo and got.hi==value.hi,key
            assert R(*map(F,data["outward_decimal"])).holds(got),key
        assert la.hi<0 and birth.lo>0
        return {"exact_interval_corollaries":5,"basis":"coordinate integration and implicit level-curve derivative", 
                "mixed_contrast_absolute_bound_K":float(la.hi-la.lo)}
    check("monotonic_finite_increment_level_curve_and_corner_corollaries",monotonic_corollaries)

    def symbolic_witness():
        # Independent quadratic implicit function: known root x(theta)=theta*p.
        # The exact derivative remainder is B[d,d_theta], computed in two ways.
        A0=[[F(2),F(1,3)],[F(-1,7),F(3)]]
        H=[[[F(1),F(2)],[F(2),F(-1)]],[[F(3),F(-2)],[F(-2),F(4)]]]
        p=[F(1),F(2)];eps=F(1,100003)
        def bi(H,a,b):return sum(H[j][k]*a[j]*b[k] for j in range(2) for k in range(2))
        for theta in (F(0),F(1,3),F(1)):
            dd=[eps*(1+theta),eps*(theta-2)];ddt=[eps,eps];yt=[p[i]+ddt[i] for i in range(2)]
            r_t=[sum(A0[i][j]*ddt[j] for j in range(2))+bi(H[i],dd,ddt) for i in range(2)]
            correction=[bi(H[i],dd,yt)-bi(H[i],p,dd) for i in range(2)]
            assert all(r_t[i]-correction[i]==sum(A0[i][j]*ddt[j] for j in range(2)) for i in range(2))
        return {"quadratic_exact_cases":3,"endpoints_included":True,"purpose":"mixed/Hessian sign witness, not physical sampling"}
    check("independent_quadratic_P2_sign_witness",symbolic_witness)
    def wolfram():
        text="\n".join(x.get("text","") for x in wl["tool_result"]["content"])
        ts=text.split('"TensorChecks" -> <|',1)[1].split("|>",1)[0]
        sc=text.split('"ScalarChecks" -> <|',1)[1].split("|>",1)[0]
        tensor_checks=re.findall(r'"([^"]+)" -> 0',ts)
        # The source output is a single Association with scalar or list values.
        entries=re.findall(r'"([^"]+)" -> (\{[^}]*\}|0)',sc)
        flattened=[]
        for name,value in entries:
            flattened.extend([int(z.strip()) for z in value.strip("{}").split(",")])
        assert len(tensor_checks)==6 and len(entries)==9 and len(flattened)==15
        assert all(x==0 for x in flattened)
        assert '"TensorAllZero" -> True' in text and '"ScalarAllZero" -> True' in text
        assert '"ExternalCanonicalizerUsed" -> False' in text
        assert '"Messages" -> {}' in text and '"Status" -> "Completed"' in text
        return {"tensor_checks":6,"scalar_groups":9,"scalar_values":15,"backend":"xPerm pure Wolfram Language group algorithms","code_and_execution_read":True}
    check("actual_Wolfram_xAct_result_and_scope",wolfram)
    elapsed=time.perf_counter()-tic
    result={"schema":"WU088_HH_PHYS17_INDEPENDENT_ARITHMETIC_V1",
      "status":"PASS" if all(c["result"]=="PASS" for c in checks) else "FAIL",
      "checks_total":len(checks),"checks_passed":sum(c["result"]=="PASS" for c in checks),
      "checks":checks,"input_identities":inputs,"candidate_imports":0,"PHYS14_helper_imports":0,
      "new_source_calls":0,"new_root_solves":0,"history_replays":0,
      "method":"Exact Fraction intervals, no intermediate rounding; independent Cramer determinant solve; source and derivation review recorded separately",
      "elapsed_seconds":elapsed,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/"INDEPENDENT_ARITHMETIC_RESULTS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"checks_total":len(checks),"checks_passed":result["checks_passed"],
                     "failed":[x for x in checks if x["result"]!="PASS"],"elapsed_seconds":elapsed,"peak_rss_kib":result["peak_rss_kib"]},ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for key in ("parent15","parent16","parent17","output"):ap.add_argument("--"+key,type=pathlib.Path,required=True)
    raise SystemExit(main(ap.parse_args()))

