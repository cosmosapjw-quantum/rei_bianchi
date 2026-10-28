"""Single subprocess, constrained current-unit source computation."""
import json,math,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'src'))
from profile import fit
from reference_decimal import fit as ref_fit

def main():
 bb=json.loads((P/'input/BB13.json').read_text());cal=json.loads((P/'input/CALIBRATION_RESULT.json').read_text())
 z=bb['z'];obs=bb['values'];m=cal['template_log10_Gamma12'];C=bb['statistical_covariance_dex2'];v=bb['slope_nuisance']['response_dex']
 r=fit(z,obs,m,C,v);rr=ref_fit(z,obs,m,C,v)
 checks=[];rtol=1e-10;atol=1e-12
 def check(name,a,b,variance=False):
  a=float(a);b=float(b);tol=(1e-15 if variance else atol)+rtol*max(abs(a),abs(b))
  checks.append({'name':name,'actual':a,'reference':b,'delta':abs(a-b),'tolerance':tol,'passed':abs(a-b)<=tol})
 for name,field in [('beta0','beta_theta0'),('kappa0','kappa_theta0'),('betader','beta_dtheta'),('kappader','kappa_dtheta'),('theta_star','bounded_theta_star'),('theta_unc','unconstrained_theta_diagnostic')]:
  rf={'theta_unc':'theta_unconstrained'}.get(name,name);check(name,r[field],rr[rf])
 for i in range(2):
  for j in range(2):check(f'cov{i}{j}',r['conditional_covariance'][i][j],rr['cov'][i][j],variance=True)
 for th,name in [(-1,'-1'),(0,'0'),(1,'1')]:
  pts=rr['profile_points'][name];f=r['profile_points'][[-1,0,1].index(th)]
  check(f'Q2_{name}',f['Q2'],pts[0]);check(f'Q0_{name}',f['Q0'],pts[1]);check(f'kappa_{name}',f['kappa'],pts[2][1])
 check('parentQ0theta0',r['theta0']['Q0'],cal['statistical_only']['residual_chi2'])
 check('parentEOSQtheta1',r['theta_plus']['Q0'],cal['EOS_box_profile']['residual_chi2'])
 suite=unittest.defaultTestLoader.discover(str(P/'tests'),pattern='test_profile.py')
 u=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(suite)
 result={'status':'NUMERICALLY_CHECKED_SCOPED' if all(t['passed'] for t in checks) and u.wasSuccessful() else 'FAILED','source_checks':checks,'source_check_passes':sum(x['passed'] for x in checks),'unit_methods':u.testsRun,'unit_errors':len(u.errors),'unit_failures':len(u.failures),'new_IVPs':0,'old_campaign_replays':0,'physical_F4':'PARTIAL','canonical_DAG':'28/88','independent_author_review':'NOT_RUN'}
 (P/'results/PRIMARY.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
 (P/'results/DECIMAL80_REFERENCE.json').write_text(json.dumps(rr,indent=2)+'\n')
 (P/'results/TEST_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'theta_star':r['bounded_theta_star'],'unconstrained':r['unconstrained_theta_diagnostic'],'beta':r['best_profile']['beta'],'kappa':r['best_profile']['kappa'],'Q2':r['best_profile']['Q2'],'Q0theta1':r['theta_plus']['Q0'],'slope_box':r['kappa_box'],'corr':r['projected_EOS_vs_tilt_correlation'],'unit_methods':u.testsRun,'check_passes':result['source_check_passes'],'checks':len(checks)},indent=2))
 if result['status']=='FAILED':raise SystemExit(1)
if __name__=='__main__':main()
