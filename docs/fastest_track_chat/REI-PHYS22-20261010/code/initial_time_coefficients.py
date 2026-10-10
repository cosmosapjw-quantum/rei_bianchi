#!/usr/bin/env python3
"""PHYS22 local time coefficients. Decimal80, no gas IVP or native execution.

Source f64 literals are exact-real binary64 inputs to the continuum formulas.
The arithmetic is not an emulation of native f64 rounding after each operation.
The coefficient convention is [epsilon^2], with physical shear^2 separated.
"""
from __future__ import annotations
import argparse
from decimal import Decimal as D, getcontext
import hashlib
import json
from pathlib import Path
import platform

getcontext().prec=80

def b(s): return D.from_float(float(s))
Z=D(0); ONE=D(1)
KB=b('1.380649e-16'); EV=b('1.602176634e-12'); F=b('0.083')
H=b('1e-14'); NH=b('1e-4'); C=b('29979245800.0')
SH=(b('1.01e-14')-b('0.99e-14'))/2
N0=b('0.05'); SRC=b('5e-15'); EB=b('13.7'); TSTAR=b('50000')
CHI=list(map(b,['13.598434599702','24.587389011','54.41776']))
CUT=b('13.60'); PE=b('2.963'); E0=b('0.4298'); YA=b('32.88')
SIG0=b('5.475e4'); CM2=b('1e-18')
LK=list(map(b,['315614','570670','1263030']))
CIA=list(map(b,['21.11','32.38','19.95']))
CIP=list(map(b,['-1.089','-1.146','-1.089']))
CIC=list(map(b,['0.354','0.416','0.553']))
CIR=list(map(b,['0.874','0.987','0.735']))
CID=list(map(b,['1.101','1.056','1.275']))

def power(x,p): return (p*x.ln()).exp()
DR_A=b('1.54e-9')*power(b('11605'),b('1.5'))
DR_B1=b('40.49664394833662')*b('11605')
DR_B2=b('8.099328789667')*b('11605')
DR_B=[DR_B1,DR_B1+DR_B2]

def total_particles(y): return 1+F+y[0]+F*(y[1]+2*y[2])
def temperature(y): return 2*EV*y[3]/(3*KB*total_particles(y))
def dot(a,bv): return sum((x*y for x,y in zip(a,bv)),Z)
def mv(a,v): return [dot(row,v) for row in a]
def add(a,bv): return [x+y for x,y in zip(a,bv)]
def scale(s,a): return [s*x for x in a]

def sigma(e):
    if e<=CUT: raise ValueError('Local derivatives require positive cutoff margin')
    x=e/E0
    return SIG0*(x-1)**2*power(x,PE/2-b('5.5'))*power(1+(x/YA).sqrt(),-PE)*CM2

def spectral(e):
    x=e/E0;v=(x/YA).sqrt();s=sigma(e)
    a=2*x/(x-1)+PE/2-b('5.5')-PE*v/(2*(1+v))
    da=-2*x/(x-1)**2-PE*v/(4*(1+v)**2)
    dda=2*x*(x+1)/(x-1)**3-PE*v*(1-v)/(8*(1+v)**3)
    return [s,s*a,s*(a*a+da),s*(a*a*a+3*a*da+dda)],{'alpha':a,'D_alpha':da,'D2_alpha':dda}

def rates(t):
    aa=[];bb=[];gg=[];gp=[];gs=[]
    for j in range(3):
        l=LK[j]/t
        if j==1:
            aa.append(b('3e-14')*power(l,b('0.654')))
            gg.append(-b('0.654'));gp.append(Z)
        else:
            u=power(l/b('0.522'),b('0.470'))
            aa.append((2 if j==2 else 1)*b('1.269e-13')*power(l,b('1.503'))/power(1+u,b('1.923')))
            gg.append(-b('1.503')+b('1.923')*b('0.470')*u/(1+u))
            gp.append(-b('1.923')*b('0.470')**2*u/(1+u)**2)
        v=power(l/CIC[j],CIR[j])
        bb.append(CIA[j]*power(t,-b('1.5'))*(-l/2).exp()*power(l,CIP[j])/power(1+v,CID[j]))
        gs.append(-b('1.5')+l/2-CIP[j]+CID[j]*CIR[j]*v/(1+v))
    dd=[DR_A*power(t,-b('1.5'))*(-DR_B[0]/t).exp(),b('0.3')*DR_A*power(t,-b('1.5'))*(-DR_B[1]/t).exp()]
    kk=[KB/EV*t*aa[j]*(b('1.5')+gg[j]) for j in range(3)]
    return aa,bb,gg,gp,gs,dd,kk

def coordinates(y,n):
    x,h1,h2,w=y
    return [1-x,F*(1-h1-h2),F*h1],[x,F*h1,F*h2],n*(x+F*(h1+2*h2))

def nonphoto(y,n=NH):
    t=temperature(y);lo,up,ne=coordinates(y,n)
    aa,bb,g,gp,gs,dd,kk=rates(t)
    ci=[lo[j]*ne*bb[j] for j in range(3)]
    rr=[up[j]*ne*aa[j] for j in range(3)]
    dr=[up[1]*ne*d for d in dd]
    nu=[ci[0]-rr[0],ci[1]-rr[1]-sum(dr,Z),ci[2]-rr[2]]
    cool=sum((CHI[j]*ci[j]+up[j]*ne*kk[j] for j in range(3)),Z)+sum((KB/EV*DR_B[k]*dr[k] for k in range(2)),Z)
    return [nu[0],(nu[1]-nu[2])/F,nu[2]/F,-2*H*y[3]-cool]

def jvp(y,v,n=NH):
    t=temperature(y);lo,up,ne=coordinates(y,n);pi=total_particles(y)
    dpi=v[0]+F*(v[1]+2*v[2]);dt=2*EV/(3*KB*pi)*v[3]-t/pi*dpi
    dlo=[-v[0],-F*(v[1]+v[2]),F*v[1]];dup=[v[0],F*v[1],F*v[2]];dne=n*dpi
    aa,bb,g,gp,gs,dd,kk=rates(t)
    dci=[ne*bb[j]*dlo[j]+lo[j]*bb[j]*dne+lo[j]*ne*bb[j]*gs[j]/t*dt for j in range(3)]
    drr=[ne*aa[j]*dup[j]+up[j]*aa[j]*dne+up[j]*ne*aa[j]*g[j]/t*dt for j in range(3)]
    ddr=[ne*dd[k]*dup[1]+up[1]*dd[k]*dne+up[1]*ne*dd[k]*(-b('1.5')+DR_B[k]/t)/t*dt for k in range(2)]
    dk=[KB/EV*aa[j]*((1+g[j])*(b('1.5')+g[j])+gp[j]) for j in range(3)]
    dc=sum((CHI[j]*dci[j]+ne*kk[j]*dup[j]+up[j]*kk[j]*dne+up[j]*ne*dk[j]*dt for j in range(3)),Z)+sum((KB/EV*DR_B[k]*ddr[k] for k in range(2)),Z)
    vnu=[dci[0]-drr[0],dci[1]-drr[1]-sum(ddr,Z),dci[2]-drr[2]]
    return [vnu[0],(vnu[1]-vnu[2])/F,vnu[2]/F,-2*H*v[3]-dc]

def grad_temperature(y):
    t=temperature(y);pi=total_particles(y)
    return [-t/pi,-F*t/pi,-2*F*t/pi,2*EV/(3*KB*pi)]

def serialize(o):
    if isinstance(o,D):return str(o)
    if isinstance(o,dict):return {k:serialize(v) for k,v in o.items()}
    if isinstance(o,(list,tuple)):return [serialize(v) for v in o]
    return o

def calculate():
    y=[b('0.9'),b('0.3'),b('0.6'),Z]
    y[3]=3*KB*TSTAR*total_particles(y)/(2*EV)
    ss,slopes=spectral(EB);pref=C*NH*(1-y[0]);ld=scale(pref,ss)
    heat=[ld[0]*(EB-CHI[0]),ld[1]*(EB-CHI[0])+ld[0]*EB,
          ld[2]*(EB-CHI[0])+2*ld[1]*EB+ld[0]*EB,
          ld[3]*(EB-CHI[0])+3*ld[2]*EB+3*ld[1]*EB+ld[0]*EB]
    L=[ld[0],Z,Z,heat[0]];DL=[ld[1],Z,Z,heat[1]]
    CL=[ld[2]+3*ld[1],Z,Z,heat[2]+3*heat[1]]
    DCL=[ld[3]+3*ld[2],Z,Z,heat[3]+3*heat[2]]
    f_np=nonphoto(y);f0=add(f_np,scale(N0,L))
    columns=[jvp(y,[ONE if i==j else Z for i in range(4)]) for j in range(4)]
    jnp=[list(row) for row in zip(*columns)]
    ly=[[Z]*4 for _ in range(4)]
    ly[0][0]=-C*NH*ss[0];ly[3][0]=ly[0][0]*(EB-CHI[0])
    a0=[[jnp[i][j]+N0*ly[i][j] for j in range(4)] for i in range(4)]
    pref_logdot=-3*H-f0[0]/(1-y[0])
    dotCL=[pref_logdot*CL[i]-H*DCL[i] for i in range(4)]
    k3=[dotCL[i]-ld[0]*CL[i]-DL[i]*ld[1]-L[i]*CL[0]/3 for i in range(4)]
    v2=scale(2*N0/15,CL)
    v3_atom=scale(2*N0/15,k3);v3_birth=scale(2*SRC/45,CL)
    u3=scale(ONE/3,v2)
    u4_parts={'baseline_evolution':scale(N0/30,dotCL),
              'baseline_survival':scale(-N0*ld[0]/30,CL),
              'endpoint_opacity_covariance':scale(-N0*ld[1]/30,DL),
              'mean_second_opacity':scale(-N0*CL[0]/90,L),
              'local_coupled_feedback':scale(ONE/4,mv(a0,u3)),
              'continuous_birth_forcing':scale(ONE/4,v3_birth)}
    u4=[sum((p[i] for p in u4_parts.values()),Z) for i in range(4)]
    u4_direct=scale(ONE/4,add(mv(a0,u3),add(v3_atom,v3_birth)))
    gt=grad_temperature(y);tdot=dot(gt,f0)
    pi=total_particles(y);dp=f0[0]+F*(f0[1]+2*f0[2])
    gd_x=-tdot/pi+TSTAR*dp/pi**2
    gdot=[gd_x,F*gd_x,2*F*gd_x,-2*EV*dp/(3*KB*pi**2)]
    th3=dot(gt,u3);th4=dot(gt,u4)+dot(gdot,u3)
    th3parts={'thermal_energy':gt[3]*u3[3],'particle_count':dot(gt[:3],u3[:3])}
    birth4=u4_parts['continuous_birth_forcing'];birth5he=scale(ONE/5,jvp(y,birth4))
    xe=y[0]+F*(y[1]+2*y[2]);heparts={}
    for row,name in [(1,'HeII'),(2,'HeIII')]:
        electron=f_np[row]*u3[0]/(4*xe)
        thermal=jnp[row][3]/gt[3]*th3/4
        heparts[name]={'electron_density':electron,'temperature':thermal,'sum':electron+thermal,'total_u4':u4[row]}
    raw3=scale(SH*SH,u3);raw4=scale(SH*SH,u4)
    penergy_C=EB*(CL[0]+2*ld[1]+4*ld[0])
    result={'initial_state':y,'initial_temperature_K':temperature(y),'Pi0':pi,'Xe0':xe,
      'constants':{'H_s':H,'shear_s':SH,'shear_squared_s2':SH*SH,'nH_cm3':NH,'fHe':F,'N0_per_H':N0,'S_per_H_s':SRC,'birth_eV':EB,'chi_HI_eV':CHI[0],'HI_cutoff_eV':CUT,'c_cm_s':C,'kB_erg_K':KB,'eV_erg':EV},
      'spectral':{'sigma_D0_D1_D2_D3':ss,**slopes,'lambda_D0_D1_D2_D3':ld,'heat_D0_D1_D2_D3':heat,'L':L,'CL':CL,'DCL':DCL,'dot_CL_at_actual_baseline':dotCL,'cohort_age3_bracket':k3},
      'baseline_local':{'F_nonphoto':f_np,'F_total_at_initial_state':f0,'J_nonphoto':jnp,'endpoint_L_y':ly,'A_g0':a0,'temperature_gradient':gt,'temperature_gradient_time_derivative':gdot,'Tdot0':tdot,'prefactor_logdot':pref_logdot},
      'normalized_by_shear_squared':{'state_order':['xHII','xHeII','xHeIII','w_eV_per_H'],'eta_t3':u3,'eta_t4':u4,'eta_t4_direct_recurrence':u4_direct,'eta_t4_parts':u4_parts,'temperature_t3':th3,'temperature_t4':th4,'temperature_t3_parts':th3parts,'He_t4_parts':heparts,'birth_particular_t4':birth4,'birth_particular_He_t5':{'HeII':birth5he[1],'HeIII':birth5he[2]},'birth_temperature_t4':dot(gt,birth4)},
      'actual_shear_time_coefficients':{'state_t3':raw3,'state_t4':raw4,'temperature_t3_K_s3':SH*SH*th3,'temperature_t4_K_s4':SH*SH*th4,'He_t4_parts':{k:{kk:SH*SH*vv for kk,vv in val.items()} for k,val in heparts.items()},'temperature_t3_parts_K_s3':{k:SH*SH*v for k,v in th3parts.items()}},
      'leading_ledgers_normalized_by_shear_squared':{'photon_count_t3':-u3[0],'HI_ionization_t3':u3[0],'gas_thermal_plus_ionization_t3':u3[3]+CHI[0]*u3[0],'absorbed_photon_energy_t3':2*N0*penergy_C/45},
      'continuous_birth_partition':'Particular response to continuous-birth geometric forcing using the same full baseline and causal operator; not a global parameter derivative in S.',
      'time_remainder':'Local Taylor/asymptotic coefficients only. No rigorous finite-time remainder or trajectory computed.'}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError('Use a fresh output file')
    r=calculate();checks=[]
    def check(name,actual,expected,tol=D('1e-60')):
        err=abs(actual-expected)/max(abs(actual),abs(expected),D('1e-200'))
        checks.append({'name':name,'actual':actual,'expected':expected,'relative_difference':err,'tolerance':tol,'pass':err<tol})
    check('initial_temperature_normalization',r['initial_temperature_K'],TSTAR)
    n=r['normalized_by_shear_squared'];s=r['spectral'];base=r['baseline_local']
    for i in range(4):check('t4_recurrence_parts_'+str(i),n['eta_t4'][i],n['eta_t4_direct_recurrence'][i])
    check('primary_energy_ownership',r['leading_ledgers_normalized_by_shear_squared']['gas_thermal_plus_ionization_t3'],r['leading_ledgers_normalized_by_shear_squared']['absorbed_photon_energy_t3'])
    for name,p in n['He_t4_parts'].items():check(name+'_electron_thermal_decomposition',p['sum'],p['total_u4'])
    for i in (0,3):check('birth_leading_relative_to_initial_'+str(i),n['birth_particular_t4'][i],SRC*n['eta_t3'][i]/(4*N0))
    check('birth_temperature_relation',n['birth_temperature_t4'],SRC*n['temperature_t3']/(4*N0))
    # NEW third spectral derivative: differentiate D2sigma on logarithmic energy.
    est=[]
    for h in (D('1e-6'),D('5e-7')):
        plus=spectral(EB*h.exp())[0][2];minus=spectral(EB*(-h).exp())[0][2]
        est.append((plus-minus)/(2*h))
    d3=(4*est[1]-est[0])/3
    check('NEW_D3sigma_log_energy_difference',d3,s['sigma_D0_D1_D2_D3'][3],D('1e-22'))
    # NEW tangent at the actual evolving baseline: no IVP, just its first local jet.
    def local_cl(t):
        yy=add(r['initial_state'],scale(t,base['F_total_at_initial_state']))
        ee=EB*(-H*t).exp();ss=spectral(ee)[0];pref=C*NH*(-3*H*t).exp()*(1-yy[0])
        ld=scale(pref,ss);cl=ld[2]+3*ld[1]
        cq=(ee-CHI[0])*cl+2*ee*ld[1]+4*ee*ld[0]
        return [cl,cq]
    estimates=[]
    for h in (D('10'),D('5')):
        pp,mm=local_cl(h),local_cl(-h)
        estimates.append([(pp[i]-mm[i])/(2*h) for i in range(2)])
    for j,idx in enumerate((0,3)):
        val=(4*estimates[1][j]-estimates[0][j])/3
        check('NEW_actual_baseline_CL_tangent_'+str(idx),val,s['dot_CL_at_actual_baseline'][idx],D('1e-36'))
    # NEW temperature time-jet coefficient: center along the baseline first jet.
    def mapped(t):
        yy=add(r['initial_state'],scale(t,base['F_total_at_initial_state']))
        return dot(grad_temperature(yy),add(n['eta_t3'],scale(t,n['eta_t4'])))
    estimates=[]
    for h in (D('10'),D('5')):estimates.append((mapped(h)-mapped(-h))/(2*h))
    check('NEW_temperature_t4_chain_rule',(4*estimates[1]-estimates[0])/3,n['temperature_t4'],D('1e-36'))
    signs={'H_t3_negative':n['eta_t3'][0]<0,'w_t3_negative':n['eta_t3'][3]<0,'T_t3_negative':n['temperature_t3']<0,'He_t3_exact_zero':n['eta_t3'][1]==0 and n['eta_t3'][2]==0,'HeII_t4_negative':n['eta_t4'][1]<0,'HeIII_t4_positive':n['eta_t4'][2]>0}
    for name,ok in signs.items():checks.append({'name':name,'pass':ok,'kind':'coefficient sign or exact vanishing at declared IC'})
    out={'task':'REI-PHYS22-20261010','evidence_state':'derived; local coefficients numerically checked','input_commit':'3dc42c64ab32075f0a59c96af3ddf7435d9b7f97','scientific_src_tree':'cb69b4736dd046e4675557577eb8e0ead037d1f3','convention':'eta=[epsilon^2] y = shear^2*(u3*t^3+u4*t^4+...); eta is half the epsilon second derivative','time_units':'seconds','coefficient_units':'normalized u3: state/s; normalized u4: state/s^2; actual coefficients: state/s^3 and state/s^4','scope':'Actual prescribed FT03 initial-state local expansion; no gas IVP, finite-time solution or native arithmetic equivalence','decimal_digits':getcontext().prec,'python':platform.python_version(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':r,'checks':checks,'summary':{'passed':sum(c['pass'] for c in checks),'total':len(checks),'failures':sum(not c['pass'] for c in checks)},'native_runs':0,'gas_IVP_runs':0,'closed_PHYS19_PHYS20_PHYS21_proof_replays':0,'physical_admission':'HOLD'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(serialize(out),indent=2)+'\n')
    print(json.dumps(serialize({'summary':out['summary'],'actual_coefficients':r['actual_shear_time_coefficients'],'normalized_temperature_t4':n['temperature_t4']}),indent=2))
    if out['summary']['failures']:raise SystemExit(1)

if __name__=='__main__':main()
