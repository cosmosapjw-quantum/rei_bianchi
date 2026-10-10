#!/usr/bin/env python3
"""New PHYS21 local-Jacobian diagnostic. No trajectory, native code, or old proof.

Analytic event/temperature variations are compared with complex-step differentiation
of the smooth FT03 nonphoto RHS. Manual transcription of pinned source, not a
native implementation equivalence certificate or a rigorous error enclosure.
"""
import argparse
import cmath
import hashlib
import json
from pathlib import Path

KB=1.380649e-16
EV=1.602176634e-12
FHE=0.083
H=1e-14
CHI=(13.598434599702,24.587389011,54.41776)
LAM=(315614.0,570670.0,1263030.0)
CI_A=(21.11,32.38,19.95)
CI_P=(-1.089,-1.146,-1.089)
CI_C=(0.354,0.416,0.553)
CI_R=(0.874,0.987,0.735)
CI_D=(1.101,1.056,1.275)
DR_A=1.54e-9*11605.0**1.5
DR_B1=40.49664394833662*11605.0
DR_B2=8.099328789667*11605.0
DR_B=(DR_B1,DR_B1+DR_B2)

def temperature(y):
    x,a,b,w=y
    return 2*EV*w/(3*KB*(1+FHE+x+FHE*(a+2*b)))

def rates(T):
    alpha=[];beta=[];g=[];gp=[];bslope=[]
    for j in range(3):
        lam=LAM[j]/T
        if j==1:
            alpha.append(3e-14*lam**0.654);g.append(-0.654);gp.append(0.0)
        else:
            v=(lam/0.522)**0.470
            alpha.append((2.0 if j==2 else 1.0)*1.269e-13*lam**1.503/(1+v)**1.923)
            g.append(-1.503+1.923*0.470*v/(1+v))
            gp.append(-1.923*0.470**2*v/(1+v)**2)
        v=(lam/CI_C[j])**CI_R[j]
        beta.append(CI_A[j]*T**(-1.5)*cmath.exp(-lam/2)*lam**CI_P[j]/(1+v)**CI_D[j])
        bslope.append(-1.5+lam/2-CI_P[j]+CI_D[j]*CI_R[j]*v/(1+v))
    dr=[DR_A*T**(-1.5)*cmath.exp(-DR_B[0]/T),0.3*DR_A*T**(-1.5)*cmath.exp(-DR_B[1]/T)]
    kappa=[KB/EV*T*alpha[j]*(1.5+g[j]) for j in range(3)]
    return alpha,beta,g,gp,bslope,dr,kappa

def coordinates(y,nH):
    x,a,b,_=y
    return [1-x,FHE*(1-a-b),FHE*a],[x,FHE*a,FHE*b],nH*(x+FHE*(a+2*b))

def rhs(y,nH):
    T=temperature(y);lower,upper,ne=coordinates(y,nH)
    alpha,beta,g,gp,bslope,dr,kappa=rates(T)
    ci=[lower[j]*ne*beta[j] for j in range(3)]
    rr=[upper[j]*ne*alpha[j] for j in range(3)]
    d=[upper[1]*ne*dr[k] for k in range(2)]
    flux=[ci[0]-rr[0],ci[1]-rr[1]-sum(d),ci[2]-rr[2]]
    cool=sum(CHI[j]*ci[j]+upper[j]*ne*kappa[j] for j in range(3))+sum(KB/EV*DR_B[k]*d[k] for k in range(2))
    return [flux[0],(flux[1]-flux[2])/FHE,flux[2]/FHE,-2*H*y[3]-cool]

def analytic_jvp(y,nH,v):
    x,a,b,w=y;vx,va,vb,vw=v
    T=temperature(y);lower,upper,ne=coordinates(y,nH)
    Pi=1+FHE+x+FHE*(a+2*b)
    dPi=vx+FHE*(va+2*vb)
    dT=2*EV/(3*KB*Pi)*vw-T/Pi*dPi
    dlow=[-vx,-FHE*(va+vb),FHE*va]
    dup=[vx,FHE*va,FHE*vb]
    dne=nH*dPi
    alpha,beta,g,gp,bslope,dr,kappa=rates(T)
    dci=[ne*beta[j]*dlow[j]+lower[j]*beta[j]*dne+lower[j]*ne*beta[j]*bslope[j]/T*dT for j in range(3)]
    drr=[ne*alpha[j]*dup[j]+upper[j]*alpha[j]*dne+upper[j]*ne*alpha[j]*g[j]/T*dT for j in range(3)]
    ddr=[ne*dr[k]*dup[1]+upper[1]*dr[k]*dne+upper[1]*ne*dr[k]*(-1.5+DR_B[k]/T)/T*dT for k in range(2)]
    dkappa=[KB/EV*alpha[j]*((1+g[j])*(1.5+g[j])+gp[j]) for j in range(3)]
    dcool=sum(CHI[j]*dci[j]+ne*kappa[j]*dup[j]+upper[j]*kappa[j]*dne+upper[j]*ne*dkappa[j]*dT for j in range(3))+sum(KB/EV*DR_B[k]*ddr[k] for k in range(2))
    dflux=[dci[0]-drr[0],dci[1]-drr[1]-sum(ddr),dci[2]-drr[2]]
    return [dflux[0],(dflux[1]-dflux[2])/FHE,dflux[2]/FHE,-2*H*vw-dcool],dT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(Path(__file__).with_name('LOCAL_GAS_DERIVATIVE_CHECK.json')))
    args=parser.parse_args();step=1e-24;tol=2e-12;results=[]
    fixtures=[(0.9,0.3,0.6,50000.0,0.0),(0.89,0.29,0.61,45000.0,6.25e8),(0.92,0.35,0.55,55000.0,1.25e9)]
    for index,(x,a,b,T,t) in enumerate(fixtures):
        Pi=1+FHE+x+FHE*(a+2*b);w=1.5*KB*T*Pi/EV;y=[x,a,b,w];nH=1e-4*cmath.exp(-3*H*t).real
        for col in range(4):
            v=[0.0]*4;v[col]=1.0
            expected,expected_T=analytic_jvp(y,nH,v)
            yy=[complex(y[k],step*v[k]) for k in range(4)]
            observed=[z.imag/step for z in rhs(yy,nH)]
            for row in range(4):
                value=expected[row].real
                error=abs(value-observed[row])/max(abs(value),abs(observed[row]),1e-280)
                results.append({'fixture':index,'kind':'nonphoto_Jacobian','row':row,'column':col,'analytic':value,'complex_step':observed[row],'relative_difference':error,'pass':error<tol})
            observed_T=temperature(yy).imag/step
            error=abs(expected_T-observed_T)/max(abs(expected_T),abs(observed_T),1e-280)
            results.append({'fixture':index,'kind':'temperature_particle_count_gradient','column':col,'analytic':expected_T,'complex_step':observed_T,'relative_difference':error,'pass':error<tol})
    data={'task':'PHYS21_NEW_LOCAL_GAS_DERIVATIVE_DIAGNOSTIC','status':'PASS' if all(r['pass'] for r in results) else 'FAIL','convention':'eta=[epsilon^2]y; same local Jacobian acts on the coefficient','method':'analytic event/JVP and particle-count derivative versus complex-step smooth nonphoto RHS','complex_step':step,'relative_tolerance':tol,'check_count':len(results),'passed':sum(r['pass'] for r in results),'max_relative_difference':max(r['relative_difference'] for r in results),'fixtures_are_trajectory':False,'fixtures':fixtures,'new_native_runs':0,'new_gas_IVP_runs':0,'old_proof_replay':False,'limitations':['manual Python transcription of pinned source','checks local gas/temperature derivative, not radiation memory or solution coefficients','complex-step agreement is not a rigorous enclosure or native binary-equivalence proof'],'checks':results}
    out=Path(args.output)
    if out.exists():
        raise FileExistsError('refusing to overwrite a diagnostic result')
    out.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:data[k] for k in ['status','check_count','passed','max_relative_difference']}))
    if data['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
