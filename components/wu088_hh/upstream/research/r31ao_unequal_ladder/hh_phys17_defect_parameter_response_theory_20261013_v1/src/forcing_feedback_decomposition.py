#!/usr/bin/env python3
"""Factor explicit global-parameter forcing and state feedback after run02.

This is a stored-enclosure postprocess. Main run02 remains unchanged. Holding
(g1,g2) fixed defines explicit forcing; their actual inherited sensitivities
define state feedback. Both are transferred by the same Full Jacobian.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import resource
import sys
import time
from fractions import Fraction as Q


def main(p15, p16, output):
    tic=time.perf_counter()
    root=pathlib.Path(__file__).resolve().parents[1]
    deps=[]
    def read(base,rel):
        path=base/rel; data=path.read_bytes()
        deps.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        return json.loads(data)
    helper=p15/'inputs/phys14/src/phys14_advance.py'
    assert hashlib.sha256(helper.read_bytes()).hexdigest()=='d20d9797278b8da71d38a3db229325dc7792d3991863f07bcdb7f72f2ba5567a'
    spec=importlib.util.spec_from_file_location('p14_arithmetic',helper)
    old=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(old)
    I,raw,bits=old.I,old.from_raw,old.exact_bits
    dot,mv,add,scale=old.dot,old.matvec,old.vadd,old.scale
    res=read(root,'checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json')
    assert deps[-1]['sha256']=='fd4fc0fe6bcf035496270bb92f0c56c44ca43d16694cb40296087569a305e7c0'
    app=read(p16,'checks/application/run01/results/CORRELATED_DEFECT_RESULTS.json')
    base='inputs/phys14/inputs/ncp07/results/'
    box=read(p15,base+'full/SOURCE_BOX.json')
    comp=read(p15,base+'full/SOURCE_BOX_COMPONENTS.json')
    centre=read(p15,base+'full/SOURCE_CENTRE.json')
    ccomp=read(p15,base+'full/SOURCE_CENTRE_COMPONENTS.json')
    native=read(p15,base+'full/NATIVE_CONSTANT_LEAVES.json')
    uniform=read(p15,'inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json')
    h,n1,n2,rho,birthM=[raw(res['constants'][key]) for key in ('h','n1','n2','rho','birth_M')]
    c,chi=I(bits(native['c_bits'])),raw(res['constants']['CHI_H'])
    E=[I(bits(x)) for x in box['energy_bits']]
    a1=[c*n1*bits(s[0]) for s in box['sigma_bits']]+[I(0),I(0)]
    a2=[c*n2*bits(s[0]) for s in box['sigma_bits']]+[I(0),I(0)]
    heat=[I(bits(z[0])) for z in box['heat_bits']]
    alpha=[I(0)]+[(1-rho)*E[j]/(E[j]-E[j-1]) for j in range(1,33)]
    Z0=[raw(z) for z in app['linked_factors']['common_Z0']]
    Q1=[raw(z) for z in app['linked_factors']['Q1']]
    g1,y=[[raw(z) for z in app['root_boxes'][key]] for key in ('g1','g2')]
    ss=[raw(z) for z in res['fixed_endpoint_data']['stage_increment']]
    J=[I(0) for _ in range(35)];J[24]=birthM
    hh=[I(1),I(0),I(0),-chi]
    parb,parlambda=I(0,1),I(0,1)
    A1=[1/(1+h*a*(1-g1[0])) for a in a1]
    tau=[h*a*(1-y[0]) for a in a2]
    A=[1/(1+t) for t in tau]; AF=[1/(1+2*t) for t in tau]
    L=[t*a for t,a in zip(tau,A)]; LF=[2*t*f for t,f in zip(tau,AF)]
    C1=[t*a*a*f for t,a,f in zip(tau,A,AF)]
    C2=[t*c1 for t,c1 in zip(tau,C1)]
    dA=[raw(z) for z in app['linked_factors']['DeltaA1']]
    zeta=[h*(c*bits(box['sigma_bits'][j][0])*(n2-n1)*(1-y[0])-a1[j]*ss[0]) for j in range(33)]+[I(0),I(0)]

    def R(v):
        q=[I(0) for _ in range(35)]
        q[33],q[34]=v[33]+v[0],rho*(v[34]+E[0]*v[0])
        for j in range(1,33):q[j-1]+=alpha[j]*v[j];q[j]+=(1-alpha[j])*v[j]
        return q
    def RminusI(v):
        q=[I(0) for _ in range(35)]
        q[0]=-v[0];q[33]=v[0];q[34]=rho*E[0]*v[0]+(rho-1)*v[34]
        for j in range(1,33):q[j-1]+=alpha[j]*v[j];q[j]-=alpha[j]*v[j]
        return q
    def deltaR(v):
        q=[I(0) for _ in range(35)]
        for j in range(2,33):
            pref=alpha[j]*alpha[j-1]*v[j]; ratio=(E[j-1]-E[j-2])/(E[j]-E[j-1])
            q[j-2]+=pref;q[j-1]-=(1+ratio)*pref;q[j]+=ratio*pref
        q[1]+=alpha[1]*(alpha[1]+rho-1)*v[1]
        q[0]-=alpha[1]*(alpha[1]+rho)*v[1]
        q[33]+=alpha[1]*v[1];q[34]+=rho*E[0]*alpha[1]*v[1]
        return q
    def VI(v):return [sum(v[:33],I(0)),I(0),I(0),dot(heat,v[:33])]
    def comm(v):
        q=[I(0) for _ in range(35)]
        for j in range(1,33):q[j-1]+=alpha[j]*h*(a2[j-1]-a2[j])*(1-y[0])*A[j-1]*A[j]*v[j]
        return q
    RZ0,R2Z0,dRZ0=R(Z0),R(R(Z0)),deltaR(Z0)
    rmJ=RminusI(J)
    dAQ=[a*z for a,z in zip(dA,Q1)]
    RdAQ,commQ=R(dAQ),comm(Q1)
    gc=[I(Q(z)) for z in uniform['center']]
    seg=[I(min(v.lo,w.lo),max(v.hi,w.hi)) for v,w in zip(g1,y)]
    delta=[z-c for z,c in zip(seg,gc)]
    qjet=old.taylor_jet(old.jet(box['q']),old.jet(centre['q']),delta)
    npjet=[old.taylor_jet(old.jet(a),old.jet(b),delta) for a,b in zip(comp['nonphoto'],ccomp['nonphoto'])]
    Hb=[[[npjet[i]['gg'][j][k]+parlambda*qjet['gg'][j][k]*hh[i] for k in range(4)] for j in range(4)] for i in range(4)]
    tensor=lambda a,v,w:sum((a[j][k]*v[j]*w[k] for j in range(4) for k in range(4)),I(0))
    C=[[raw(z) for z in row] for row in res['fixed_transfer']['C']]
    B=[[raw(z).hi for z in row] for row in res['fixed_transfer']['B']]
    EJ=[[raw(z) for z in row] for row in res['fixed_transfer']['I_CJF']]
    def transfer(rhs):
        cr=mv(C,rhs)
        mat=[[Q(i==j)-B[i][j] for j in range(4)]+[cr[i].mag()] for i in range(4)]
        for j in range(4):
            k=next(k for k in range(j,4) if mat[k][j]);mat[j],mat[k]=mat[k],mat[j]
            fac=mat[j][j];mat[j]=[x/fac for x in mat[j]]
            for k in range(4):
                if k!=j:
                    fac=mat[k][j];mat[k]=[x-fac*y for x,y in zip(mat[k],mat[j])]
        mag=[row[-1] for row in mat]
        rem=[sum(B[i][j]*mag[j] for j in range(4)) for i in range(4)]
        vals=[z+I(-r,r) for z,r in zip(cr,rem)]
        for _ in range(3):vals=[x.meet(y) for x,y in zip(vals,add(cr,mv(EJ,vals)))]
        return vals
    summary={}
    for parameter,item in res['responses'].items():
        v,yt,st=[[raw(z) for z in item[key]] for key in ('first_half_response','second_half_response','stage_increment_theta')]
        dlam,db=I(parameter=='lambda'),I(parameter=='b')
        tt=[-h*a*yt[0] for a in a2]
        A1t=[h*a*v[0]*a0*a0 for a,a0 in zip(a1,A1)]
        At=[-t*a*a for t,a in zip(tt,A)]
        AFt=[-2*t*f*f for t,f in zip(tt,AF)]
        Lt=[t*a*a for t,a in zip(tt,A)]
        LFt=[2*t*f*f for t,f in zip(tt,AF)]
        C1t=[a*a*f*(1-2*t*a-2*t*f)*tp for t,tp,a,f in zip(tau,tt,A,AF)]
        C2t=[2*t*a*a*f*(1-t*a-t*f)*tp for t,tp,a,f in zip(tau,tt,A,AF)]
        zetat=[-h*(c*bits(box['sigma_bits'][j][0])*(n2-n1)*yt[0]+a1[j]*st[0]) for j in range(33)]+[I(0),I(0)]
        dAt=[zp*a1*a+z*(a1t*a+a1*at) for zp,z,a1,a,a1t,at in zip(zetat,zeta,A1,A,A1t,At)]
        dAQt=[at*q for at,q in zip(dAt,Q1)]
        R_dAQt=R(dAQt)
        cqt=[I(0) for _ in range(35)]
        for j in range(1,33):
            cqt[j-1]+=alpha[j]*h*(a2[j-1]-a2[j])*(-yt[0]*A[j-1]*A[j]+(1-y[0])*(At[j-1]*A[j]+A[j-1]*At[j]))*Q1[j]
        feedback_photon={
            'opacity_change':[-z+lt*r+l*rt for z,lt,r,l,rt in zip(dAQt,Lt,RdAQ,L,R_dAQt)],
            'absorption_transport_commutator':[lt*q+l*qt for lt,q,l,qt in zip(Lt,commQ,L,cqt)],
            'stock_intermediate_redshift':[-lt*z for lt,z in zip(Lt,RminusI(RZ0))],
            'stock_backward_euler':[ct*z for ct,z in zip(C2t,R2Z0)],
            'remap_composition':[lft*z for lft,z in zip(LFt,dRZ0)],
            'birth_redshift':[parb*(lt*a+l*at)*r for lt,a,l,at,r in zip(Lt,A,L,At,rmJ)],
            'birth_backward_euler':[-parb*ct*j for ct,j in zip(C1t,J)]}
        dAJ=[a*j for a,j in zip(dA,J)]
        explicit_photon={
            'opacity_change':[db*(-z+l*r) for z,l,r in zip(dAJ,L,R(dAJ))],
            'absorption_transport_commutator':[db*l*z for l,z in zip(L,comm(J))],
            'stock_intermediate_redshift':[I(0)]*35,
            'stock_backward_euler':[I(0)]*35,
            'remap_composition':[I(0)]*35,
            'birth_redshift':[db*l*a*z for l,a,z in zip(L,A,rmJ)],
            'birth_backward_euler':[-db*c1*j for c1,j in zip(C1,J)]}
        bridge=item['source_time_bridge']
        direct_source=scale(h*dlam*(raw(app['source_bridge']['HH_time_difference'])-dot(qjet['g'],ss)),hh)
        bridge_fb=[h*(raw(bridge['nonphoto_time_theta_per_second'][i])+parlambda*raw(bridge['HH_time_theta_per_second'])*hh[i]) for i in range(4)]
        curve_fb=scale(-h,[tensor(Hb[i],ss,v) for i in range(4)])
        endpoint_fb=[raw(z) for z in item['residual_derivative_sectors']['gas_movement_endpoint']]
        explicit_r=add(direct_source,VI([sum((v[j] for v in explicit_photon.values()),I(0)) for j in range(35)]))
        feedback_r=add(add(bridge_fb,add(curve_fb,endpoint_fb)),VI([sum((v[j] for v in feedback_photon.values()),I(0)) for j in range(35)]))
        direct_rhs=add(explicit_r,[-raw(z) for z in item['endpoint_Hgtheta_feedback']])
        feedback_rhs=add(feedback_r,[-raw(z) for z in item['endpoint_Hgg_feedback']])
        dd,dfb=transfer(direct_rhs),transfer(feedback_rhs)
        row=[raw(z) for z in item['temperature_goal_row']]
        geometry=raw(item['temperature_geometry_term_K'])
        Td,Tfb=dot(row,dd),dot(row,dfb)+geometry
        combined=Td+Tfb
        refined=combined.meet(raw(item['DeltaT_theta_K']))
        # Independent manual product rules and the run02 dual graph enclose
        # the same derivative. Intersections are nonempty component by component.
        for name in feedback_photon:
            for j in range(35):
                (feedback_photon[name][j]+explicit_photon[name][j]).meet(raw(item['photon_sector_theta'][name][j]))
        for i in range(4):(direct_rhs[i]+feedback_rhs[i]).meet(raw(item['correlated_rhs'][i]))
        summary[parameter]={'definition':'Explicit partial theta with g1,g2 fixed; state feedback uses their actual shared-family sensitivities',
            'explicit_photon':explicit_photon,'feedback_photon':feedback_photon,'explicit_gas_source':direct_source,
            'explicit_r_theta':explicit_r,'feedback_r_theta':feedback_r,'explicit_correlated_rhs':direct_rhs,
            'feedback_correlated_rhs':feedback_rhs,'explicit_d_theta':dd,'feedback_d_theta':dfb,
            'explicit_DeltaT_theta_K':Td,'feedback_DeltaT_theta_K':Tfb,
            'combined_DeltaT_theta_K':combined,'intersection_with_run02_DeltaT_theta_K':refined,
            'common_goal_geometry_assigned_to':'state feedback',
            'photon_manual_dual_consistency_intersections':245,'correlated_rhs_consistency_intersections':4}
    results={'schema':'WU088_HH_PHYS17_FORCING_FEEDBACK_V1','status':'CANDIDATE_COMPUTED',
        'input_identities':deps,'responses':summary,'source_calls':0,'root_solves':0,'history_replays':0,
        'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    (output/'FORCING_FEEDBACK_RESULTS.json').write_text(json.dumps(old.out(results),ensure_ascii=False,indent=2)+'\n')
    short={p:{k:old.short(v[k]) for k in ('explicit_DeltaT_theta_K','feedback_DeltaT_theta_K','combined_DeltaT_theta_K','intersection_with_run02_DeltaT_theta_K')} for p,v in summary.items()}
    (output/'SUMMARY.json').write_text(json.dumps(short,indent=2)+'\n')
    print(json.dumps(short,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent15',type=pathlib.Path,required=True)
    ap.add_argument('--parent16',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    a=ap.parse_args();main(a.parent15.resolve(),a.parent16.resolve(),a.output.resolve())
