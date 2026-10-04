"""New stage-level energy/number cone tests, with no native execution."""
from pathlib import Path
from fractions import Fraction as F
import json, random
import mpmath as mp
from reference import M, photo_oracle, photon_oracle, encode, MPC, EV
from moment_cone import exact_forward_euler_limit, margins
ROOT=Path(__file__).resolve().parents[1]

def main():
    import sympy as sp
    Ls,Rs,Ns0,Us0=sp.symbols('L R N U', positive=True)
    wl=(Rs*Ns0-Us0)/(Rs-Ls);wr=(Us0-Ls*Ns0)/(Rs-Ls)
    i0,i1=sp.symbols('I0 I1')
    residuals=[wl+wr-Ns0,Ls*wl+Rs*wr-Us0,(Us0-Ls*Ns0)+(Rs*Ns0-Us0)-(Rs-Ls)*Ns0,(-i1*Ns0+Us0*i0)/Ns0**2-(-i1/Ns0+(Us0/Ns0)*(i0/Ns0))]
    checked=[str(sp.simplify(v)) for v in residuals]
    assert checked==['0']*4
    (ROOT/'results/SYMBOLIC_CONE.json').write_text(json.dumps({'identities':4,'residuals':checked,'basis':'endpoint positive measure representation and absorption-weighted mean derivative'},indent=2)+'\n')
    rng=random.Random(20261005);counts={'finite':0,'unbounded':0,'outward_boundary':0}
    for _ in range(240):
        L=F(rng.randint(1,30));R=L+F(rng.randint(1,30));N=F(rng.randint(1,20),7)
        U=N*(L+(R-L)*F(rng.randint(0,20),20));dN=F(rng.randint(-20,20),13);dU=F(rng.randint(-400,400),17)
        h=exact_forward_euler_limit(L,R,N,U,dN,dU)
        if h is None:
            counts['unbounded']+=1
            assert min(margins(L,R,N+100*dN,U+100*dU))>=0
        elif h==0:
            counts['outward_boundary']+=1
            assert min(margins(L,R,N+F(1,10**8)*dN,U+F(1,10**8)*dU))<0
        else:
            counts['finite']+=1
            assert min(margins(L,R,N+h*dN,U+h*dU))>=0
            assert min(margins(L,R,N+h*F(999,1000)*dN,U+h*F(999,1000)*dU))>=0
            assert min(margins(L,R,N+h*F(1001,1000)*dN,U+h*F(1001,1000)*dU))<0
    base=json.loads((ROOT/'inputs/FLRW05_NATIVE_CALL_VECTORS.json').read_text()); inp=base['photon_balance_input']
    r=[photo_oracle(c) for c in base['calls']];H=M(inp['hubble_s']);nH=M(1e-4);a=M(inp['scale_factor']);nHc=a**3*nH
    flux=[H*M(e)*M(tr)/nH for e,tr in zip(inp['edge_energy_ev'],inp['edge_n_per_cm3_ev'])]
    bins=[];dUs=[];Us=[];Ns=[];count_rates=[];photo_rhs=photon_oracle(inp,[sum(x['events']) for x in r])
    for g,c in enumerate(base['calls']):
        L,R=map(M,inp['edge_energy_ev'][g:g+2]);N=M(inp['comoving_photons_cm3'][g])/nHc
        vol=(a*M(MPC))**3
        Nq=sum(M(v['n_comoving_per_cmpc3']) for v in c['nodes'])/vol/nH
        U=sum(M(v['energy_ev'])*M(v['n_comoving_per_cmpc3']) for v in c['nodes'])/vol/nH
        J=sum(r[g]['events'])/nH;A=r[g]['absorbed']/nH/M(EV)
        dN=photo_rhs['dc'][g]/nHc
        dU=-A-H*U+R*flux[g+1]-L*flux[g]
        qs=(N,U-L*N,R*N-U);dqs=(dN,dU-L*dN,R*dN-dU)
        lim=[None if d>=0 else -q/d for q,d in zip(qs,dqs)]
        h=min(t for t in lim if t is not None);limN=lim[0]
        htrial=(h+limN)/2 if limN and limN>h else h*mp.mpf('1.01')
        bins.append({'bin':g,'N':N,'U_eV':U,'Nq_minus_input_N':Nq-N,'dN_s':dN,'dU_eV_s':dU,
         'count_only_limit_s':limN,'lower_face_limit_s':lim[1],'upper_face_limit_s':lim[2],
         'cone_limit_s':h,'limiting_face':['N','U-LN','RN-U'][lim.index(h)],'trial_h_s':htrial,
         'trial_count':N+htrial*dN,'trial_lower_margin':qs[1]+htrial*dqs[1],'trial_upper_margin':qs[2]+htrial*dqs[2]})
        Us.append(U);dUs.append(dU);Ns.append(N);count_rates.append(J)
    absorption=sum(x['absorbed'] for x in r)/nH/M(EV)
    bindings=sum(sum(x['binding']) for x in r)/nH/M(EV);heat=sum(sum(x['heat']) for x in r)/nH/M(EV)
    energy_residual=sum(dUs)+absorption+H*sum(Us)+M(inp['edge_energy_ev'][0])*flux[0]-M(inp['edge_energy_ev'][-1])*flux[-1]
    assert abs(energy_residual)<mp.mpf('1e-80')
    assert abs(absorption-bindings-heat)<mp.mpf('1e-80')
    # Exact manufactured FLRW bin, H is an arbitrary positive inverse time.
    # With H=1/tstar the resulting bound is h/tstar=1/3, not h/tstar=1.
    neg={'bin_edges_eV':[10,20],'N':'1','U_eV':'15','H_tstar':'1','Phi_lower_tstar':'1','Phi_upper_tstar':'0',
         'dN_dtau':'-1','dU_dtau_eV':'-25','count_only_dtau':'1','cone_dtau':'1/3','chosen_dtau':'1/2',
         'new_N':'1/2','new_U_eV':'5/2','new_U_over_N_eV':'5','lower_face':'-5/2'}
    result={'status':'DERIVED_AND_FINITE_CHECKED_NOT_NATIVE_OR_TRUNCATION_CERTIFICATE','exact_rational_cases':240,'case_types':counts,
            'bin_stage':bins,'negative_control':neg,'stage_energy':{'U_eV_per_H':sum(Us),'absorbed_eV_H_s':absorption,'binding_eV_H_s':bindings,'heat_eV_H_s':heat,'work_eV_H_s':H*sum(Us),'lower_exit_eV_H_s':M(inp['edge_energy_ev'][0])*flux[0],'moment_energy_residual':energy_residual},
            'independent_U_in_inspected_photon_balance':False,'no_production_timestep_changed':True}
    (ROOT/'results/STAGE_CONE_AND_ENERGY.json').write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(result),indent=2))
if __name__=='__main__':main()
