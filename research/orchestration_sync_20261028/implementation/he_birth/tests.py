"""New exact moment controls and saved N16 samples; no old producer imports."""
import argparse,pathlib,json,hashlib
from fractions import Fraction as F
from birth_moments import calculate,validate,A,M,e,s,pstar_c_squared,b_squared,K0

ROOT=pathlib.Path(__file__).resolve().parent

def direct_moment(a,t,power):
    # Expand (1-mu²)(a0+a1*mu²+a2*mu⁴), integrate monomials directly.
    c=[a[0],a[1]-a[0],a[2]-a[1],-a[2]]
    return 2*sum(c[j]*(1-t**(2*j+power+1))/F(2*j+power+1) for j in range(4))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();reference=json.loads((ROOT/'source_reference.json').read_text());path=pathlib.Path(reference['certificate_path']);raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==reference['certificate_sha256'];saved=json.loads(raw)
    # Direct Lorentz factor expression, independently factorized before comparison.
    gamma_squared=(A+e)**2/(A*A+2*A*e);beta_squared=e*e/(A+e)**2
    assert gamma_squared*(1-beta_squared)==1
    lorentz_b_squared=gamma_squared*beta_squared*((A*A+2*A*e)/4-M*M);assert lorentz_b_squared==b_squared
    assert 2*(K0+M)==A+e and 2*K0==A+e-2*M
    manufactured=[]
    for a,t,expect in [([F(1),F(0),F(0)],F(0),F(1,5)),([F(1),F(0),F(0)],F(1,2),F(47,100)),([F(0),F(0),F(1)],F(0),F(5,9))]:
        out=calculate(a,[t,t]);D=direct_moment(a,t,0);N=direct_moment(a,t,2);assert N/D==expect==F(out['mu_second'][0])==F(out['mu_second'][1]);assert D==F(out['Dg'][0]) and N==F(out['Ng'][0])
        if t==F(1,2):assert D==F(5,12) and N==F(47,240)
        manufactured.append({'coefficients':list(map(str,a)),'threshold':str(t),'D':str(D),'N':str(N),'mu_second':str(expect),'pass':True})
    rejected=[]
    for label,coeff,t in [('negative',[-1,0,0],[0,0]),('negative_interior',[1,-5,5],[0,0]),('zero',[0,0,0],[0,0]),('zero_acceptance',[1,0,0],[1,1])]:
        try:calculate(coeff,t)
        except ValueError as err:rejected.append({'label':label,'reason':str(err)})
        else:raise AssertionError('invalid moment domain accepted')
    case16=next(z for z in saved['cases'] if z['N']==16);vertices=case16['polytopes']['inner']['vertices'];candidate=saved['candidate']['parameters'];assert list(map(F,candidate))==[F(1411,10000),-F(1,4),F(33,25)]
    samples=[('fixed_witness',candidate)]+[('N16_vertex_'+str(j),v) for j,v in enumerate(vertices)]
    rows=[];identity_count=0
    for name,coef in samples:
        a=validate(coef)
        for aperture,entry in saved['moments'].items():
            interval=entry['threshold'];out=calculate(a,interval);t=(F(interval[0])+F(interval[1]))/2;D=direct_moment(a,t,0);N=direct_moment(a,t,2);ratio=N/D
            assert F(out['Dg'][0])<=D<=F(out['Dg'][1]);assert F(out['Ng'][0])<=N<=F(out['Ng'][1]);assert F(out['mu_second'][0])<=ratio<=F(out['mu_second'][1]);variance=lorentz_b_squared*ratio;cov=-variance;assert variance+variance+2*cov==0
            assert 2*K0==F(out['pair_kinetic_total_MeV']);assert K0*K0+variance>=K0*K0
            if aperture=='FULL':assert F(out['mu_second'][0])==ratio==F(out['mu_second'][1])
            identity_count+=1;rows.append({'sample':name,'coefficients':list(map(str,a)),'aperture':aperture,**out,'independent_midpoint':{'t':str(t),'D':str(D),'N':str(N),'mu_second':str(ratio),'variance_MeV2':str(variance),'covariance_MeV2':str(cov),'pair_total_variance_MeV2':'0'},'midpoint_enclosed':True})
    output={'unit':'HE-BIRTH-MOMENT15','source_reference':reference,'constants':{'A_MeV':str(A),'M_MeV':str(M),'e_MeV':str(e),'s_MeV2':str(s),'pstar_c_squared_MeV2':str(pstar_c_squared),'b_squared_MeV2':str(b_squared),'K0_MeV':str(K0)},'rows':rows,'manufactured_controls':manufactured,'rejection_controls':rejected,'counts':{'actual_samples':len(samples),'N16_inner_vertices':len(vertices),'apertures':len(saved['moments']),'sample_aperture_rows':len(rows),'midpoint_identity_checks':identity_count,'manufactured_moment_checks':len(manufactured),'rejections':len(rejected),'Lorentz_identity_checks':3},'exact_checks_pass':True,'event_rate':None,'normalization':None,'birth_pool':'UNASSIGNED','deposition_fraction':None,'Gamma_thermal':None,'Cv':None,'species_heating':None,'independent_binding_RHS':None,'physical_completion_delta':0,'claim':'conditional per-sample birth moments; no global extrema or physical thermal deposition'}
    pathlib.Path(args.output).write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':main()
