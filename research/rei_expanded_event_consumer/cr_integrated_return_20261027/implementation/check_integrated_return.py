"""One bounded prescribed check, raw observations retained on first failure."""
import time
import signal
signal.setitimer(signal.ITIMER_PROF,.75-time.process_time())
from copy import deepcopy
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import sys
import integrated_return as c

HERE=Path(__file__).resolve().parent
OUT=HERE/'attempt01'
B=1.4e6
TOL=2e-14
CHECKS=0


def check(name,error=0.0,tol=TOL,**detail):
    global CHECKS
    CHECKS+=1
    ok=isinstance(error,(int,float)) and math.isfinite(error) and abs(error)<=tol
    with (OUT/'CHECKS.jsonl').open('a') as f:
        f.write(json.dumps({'check':name,'error':error,'tolerance':tol,'pass':ok,**detail},allow_nan=False)+'\n')
    if not ok: raise AssertionError(name+': '+str(error))


def scaled(error, operands):
    s=math.fsum(abs(v) for v in operands)
    return abs(error)/s if s else (0.0 if error==0 else math.inf)


def close(name,got,want,scale=None,tol=TOL):
    check(name,scaled(got-want,[got,want] if scale is None else scale),tol)


def reject(name,call):
    try: call()
    except (ValueError,TypeError,KeyError,OverflowError): check(name); return
    raise AssertionError('accepted invalid '+name)


def oracle(A,K,G,b,dA,dK,dG,db):
    # Explicit row formulas independent of consumer helpers, Decimal precision50.
    with localcontext() as ctx:
        ctx.prec=50
        A,K,G,b,dA,dK,dG,db=map(Decimal.from_float,(A,K,G,b,dA,dK,dG,db))
        v=[Decimal(0)]*27; t=[Decimal(0)]*27
        for i,num,dnum,sign in ((11,A,dA,1),(12,A,dA,-1),(21,A,dA,-1),(22,K,dK,-1),(25,A,dA,1),(26,G,dG,1)):
            v[i]=sign*num/b
            t[i]=sign*(dnum*b-num*db)/(b*b)
        return [float(x) for x in v],[float(x) for x in t]


def main():
    events=c.read_actual()
    model=json.loads((c.UNIT/'vendor/native_identity/atomic_model.json').read_text())
    coeff=json.loads((c.UNIT/'vendor/native_identity/atomic_coefficients.json').read_text())
    check('native_species_identity',0 if model['species_order'][11:13]==['He4II','He4III'] else 1)
    check('native_binding_identity',0 if coeff['photo_VF1996']['2:1']['Eth_eV']==54.42 else 1)
    maps=[]
    for j,e in enumerate(events):
        tag=str(j)+':'+e['case']+':'+e['z']
        A=e['integrated_count_m3']; K=-e['integrated_energy_J_m3']['fast_kinetic']; G=e['integrated_energy_J_m3']['radiation']
        dA=.11*A; dK=-.07*K; dG=dK+c.I*dA; db=.13*B
        p=c.consume(e,B,dA=dA,dK=dK,dG=dG,db=db)['native_projection']
        v,t=p['flat27_diagnostic'],p['flat27_jvp']
        ov,ot=oracle(A,K,G,B,dA,dK,dG,db)
        for i in range(27):
            close(tag+':Decimal_value:'+str(i),v[i],ov[i])
            close(tag+':Decimal_jvp:'+str(i),t[i],ot[i],scale=[abs(ov[i]),abs(ot[i])])
            if i not in (11,12,21,22,25,26): check(tag+':exactzero:'+str(i),0 if v[i]==t[i]==0 else 1)
        check(tag+':source_energy',scaled(math.fsum((G,-K,-c.I*A)),[G,K,c.I*A]),2e-13)
        for name,res,ops in (
            ('He4_nuclei',v[11]+v[12],[v[11],v[12]]),
            ('nuclear_mass',4*v[11]+4*v[12],[4*v[11],4*v[12]]),
            ('thermal_electrons',v[11]+2*v[12]-v[21],[v[11],2*v[12],v[21]]),
            ('thermal_particles',2*v[11]+3*v[12]-v[21],[2*v[11],3*v[12],v[21]]),
            ('energy',math.fsum((-c.I*A/B,-K/B,G/B)),[c.I*A/B,K/B,G/B]),
            ('energy_tangent',p['energy_constraint_jvp'],[c.I*dA/B,dK/B,dG/B,c.I*A*db/B**2,K*db/B**2,G*db/B**2])):
            check(tag+':'+name,scaled(res,ops))
        # Two prescribed centered mixed FD steps, same analytic operand scales.
        physical=(A,K,G,B); direction=(dA,dK,dG,db)
        row_scales=[abs(x)+abs(y) for x,y in zip(ov,ot)]
        fd_errors=[]
        for h in (2e-4,1e-4):
            plus=c.normalize(*[x+h*d for x,d in zip(physical,direction)])['flat27_diagnostic']
            minus=c.normalize(*[x-h*d for x,d in zip(physical,direction)])['flat27_diagnostic']
            errors=[]
            for i in range(27):
                err=scaled((plus[i]-minus[i])/(2*h)-t[i],[row_scales[i]])
                check(tag+':mixed_FD:'+str(h)+':'+str(i),err,2e-8); errors.append(err)
            fd_errors.append({'h':h,'max_scaled_error':max(errors)})
        beta=1.7; dbeta=-.09*beta; r=B/beta; dr=(db-r*dbeta)/beta
        X,dX=c.reference(v,t,beta,dbeta)
        for i,num,dnum,sgn in ((11,A,dA,1),(12,A,dA,-1),(21,A,dA,-1),(22,K,dK,-1),(25,A,dA,1),(26,G,dG,1)):
            with localcontext() as ctx:
                ctx.prec=50
                D=Decimal.from_float
                refv=float(Decimal(sgn)*D(num)/D(r))
                reft=float(Decimal(sgn)*(D(dnum)*D(r)-D(num)*D(dr))/(D(r)*D(r)))
            close(tag+':reference_value:'+str(i),X[i],refv)
            close(tag+':reference_tangent:'+str(i),dX[i],reft,scale=[abs(dnum/r),abs(num*dr/r**2),abs(X[i]*dbeta/beta)])
        clock=c.integrated_clock_pair(e,B,2.3e-18,dH=-.2e-18,dA=dA,dK=dK,dG=dG,db=db)
        check(tag+':clock_identical',0 if clock['proper']==clock['eta'] and all(x==0 for x in clock['d_dH']) else 1)
        check(tag+':production_no_b',0 if c.consume(e)['native_projection'] is None else 1)
        cap=c.capacity(A,K,1e4,1.0,100*c.EV_J); sm=cap['smax']; s=.25*sm; ds=.17*s
        margins=[]
        for amp in (0.0,.25*sm,sm,1.01*sm):
            m=[1e4-amp*A,1-amp*A,100*c.EV_J-amp*K]
            units=[1e4,1,100*c.EV_J]
            check(tag+':capacity:'+str(amp),0 if ((amp<=sm and all(z>=-2e-14*u for z,u in zip(m,units))) or (amp>sm and any(z<0 for z in m))) else 1)
            margins.append({'s':amp,'capacity_margins':m})
        # Scale-amplified actual event is manufactured endpoint fixture only.
        dn=[s*B*z for z in v]; ddn=[ds*B*z+s*(B*dz+db*z) for z,dz in zip(v,t)]
        x=[1.0]*27; x[24]=math.log(10000); dx=[.11]*27; dx[24]=.03
        xp,tx=c.endpoint_reference(x,dx,2,3,.26,-.21,dn,ddn)
        for i in range(27):
            if i==24: expected,dt=x[i],dx[i]
            else:
                # Independent quotient formulas, written directly.
                with localcontext() as ctx:
                    ctx.prec=50
                    D=Decimal.from_float
                    expected=float((Decimal(2)*D(x[i])+D(dn[i]))/Decimal(3))
                    dt=float(((D(.26)*D(x[i])+Decimal(2)*D(dx[i])+D(ddn[i]))*Decimal(3)-(Decimal(2)*D(x[i])+D(dn[i]))*D(-.21))/Decimal(9))
            close(tag+':endpoint:'+str(i),xp[i],expected)
            close(tag+':endpoint_jvp:'+str(i),tx[i],dt,scale=[abs(.26*x[i]/3),abs(2*dx[i]/3),abs(ddn[i]/3),abs(expected*.21/3)])
        # Unit-specific discriminating mutation signatures, never a global norm.
        signatures={
            'dropfastcount':abs(v[21])/(A/B),
            'routeGalsotowext':abs(G/B)/(G/B),
            'thermalizeK':abs(K/B)/(K/B),
            'missingdb':abs((dA/B)-t[11])/(A/B),
            'missingdbeta':abs(beta*t[11]-dX[11])/(A/r),
            'use_over_H':abs(v[11]/2.3e-18-v[11])/(A/B),
            'omitendpointdrplus':abs((2*dx[11]+x[11]*.26+ddn[11])/3-tx[11])/abs(xp[11]),
            'wrongly_rebase_logT':abs(2*x[24]/3-xp[24])/abs(xp[24])}
        for name,sig in signatures.items(): check(tag+':mutation:'+name,0 if sig>1e-6 else 1,signature=sig)
        # Independent input directions: deliberately incompatible dG returns nonzero.
        bad=c.normalize(A,K,G,B,dG=G)['energy_constraint_jvp']
        close(tag+':incompatible_energy_derivative',bad,G/B)
        check(tag+':negative_energy_derivative',0 if c.normalize(A,K,G,B,dG=-G)['energy_constraint_jvp']<0 else 1)
        observation={'canonical_event_id':e['canonical_event_id'],'case':e['case'],'z':e['z'],
            'raw_event':e,'A_m3':A,'K_J_m3':K,'G_J_m3':G,'consumer_b_fixture_m3':B,
            'projection':p,'reference_delta':X,'reference_jvp':dX,'FD':fd_errors,
            'capacity_certificate':cap,'manufactured_capacity_controls':margins,
            'endpoint_fixture':{'xplus':xp,'jvp':tx,'not_a_physical_history':True},
            'mutation_signatures':signatures,'state_update_applied':False}
        with (OUT/'OBSERVATIONS.jsonl').open('a') as f: f.write(json.dumps(observation,allow_nan=False)+'\n')
        maps.append({'index':j,'case':e['case'],'z':e['z'],'canonical_event_id':e['canonical_event_id'],'native25':v[:25],'photon_count':v[25],'photon_energy_J':v[26]})
    e=events[0]
    for value in (-1,0,float('inf'),float('nan'),True,'1.4e6'):
        reject('invalid_b:'+str(value),lambda value=value:c.consume(e,value))
    reject('missing_b_for_jvp',lambda:c.consume(e,None,dA=1))
    for field,value in (('frame','other'),('source_qualification',None)):
        bad=deepcopy(e); bad[field]=value
        reject('invalid_'+field,lambda bad=bad:c.consume(bad,B))
    for field,value in (('native_channel','HI'),('native_maximum_eV',50001)):
        bad=deepcopy(e); bad['source_qualification'][field]=value
        reject('invalid_'+field,lambda bad=bad:c.consume(bad,B))
    bad=deepcopy(e); bad['per_event_template']['conditional_mean_kinetic_eV']=50000
    reject('invalid_support',lambda:c.consume(bad,B))
    bad=deepcopy(e); bad['integrated_energy_J_m3']['fast_kinetic']*=-1
    reject('wrong_sign_energy',lambda:c.consume(bad,B))
    for name in ('event_rate_m3_s','exposure_s','instantaneous_rhs','emission_time_history','emission_spectrum','physical_heating_J_m3'):
        bad=deepcopy(e); bad[name]=1
        reject('no_fabricated_'+name,lambda bad=bad:c.consume(bad,B))
    seen=set(); c.admit_once(e,seen,case=e['case'],z=e['z'])
    reject('duplicate_event',lambda:c.admit_once(e,seen,case=e['case'],z=e['z']))
    reject('alternative_scenario',lambda:c.admit_once(events[1],seen,case=e['case'],z=e['z']))
    reject('alternative_batch',lambda:c.consume(events,B))
    ze=deepcopy(e)
    ze['integrated_count_m3']=0.0
    ze['integrated_energy_J_m3']={k:0.0 for k in c.cr.RESERVOIRS}
    ze['density_delta_m3']={k:0.0 for k in c.cr.STOICHIOMETRY}
    ze['per_event_template']['conditional_mean_kinetic_eV']=None
    ze['per_event_template']['energy_J_per_event']=None
    ze['per_event_template']['energy_representation']='UNDEFINED_ZERO_COUNT'
    ze['retained_photon_port']['integrated_count_m3']=0.0
    ze['retained_photon_port']['integrated_energy_J_m3']=0.0
    check('manufactured_zero_event_reader',0 if c.consume(ze,B)['native_projection']['flat27_diagnostic']==[0.0]*27 else 1)
    zero=c.normalize(0,0,0,B)
    check('zero_event',0 if zero['flat27_diagnostic']==[0.0]*27 else 1)
    check('zero_amplitude',0 if [0*z for z in maps[0]['native25']]==[0.0]*25 else 1)
    check('zero_capacity_unconstrained',0 if c.capacity(0,0,0,0,0)['smax'] is None else 1)
    reject('negative_A',lambda:c.normalize(-1,0,0,B))
    reject('negative_K',lambda:c.normalize(0,-1,0,B))
    reject('negative_G',lambda:c.normalize(0,0,-1,B))
    reject('nonfinite_direction',lambda:c.normalize(1,1,1,B,dA=float('inf')))
    (OUT/'ACTUAL24_MAPS.json').write_text(json.dumps(maps,indent=2,allow_nan=False)+'\n')
    md=['# Actual24 diagnostic maps','', 'Each row is an alternative; no rows are summed. b=1.4e6 m^-3 is a consumer fixture.', '', '| index | case | z | DeltaY11 | DeltaY12 | Deltazeta | Deltawnt (J) | photon count | photon energy (J) |','|---|---|---|---|---|---|---|---|---|']
    for m in maps:
        v=m['native25']; md.append('| '+' | '.join(map(str,(m['index'],m['case'],m['z'],v[11],v[12],v[21],v[22],m['photon_count'],m['photon_energy_J'])))+' |')
    (OUT/'ACTUAL24_MAPS.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({'status':'PASS_PENDING_INDEPENDENT_REVIEW','check_count':CHECKS,'actual_alternatives':len(maps),'physical_update_applied':False}))

if __name__=='__main__': main()
