"""One selected source-bounded trial; no legacy source imports or IVP."""
import json,math,sys,unittest,csv
from pathlib import Path
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from tilt_gls import fit
from reference_decimal import fit as dfit

def main():
    spec=json.loads((R/'CONTRACT.json').read_text())
    BB=json.loads((R/'input/BB13.json').read_text())
    cal=json.loads((R/'input/CALIBRATION_RESULT.json').read_text())
    obs=BB['values']; model=cal['template_log10_Gamma12']; z=BB['z']; C=BB['statistical_covariance_dex2']
    if not (len(z)==7 and z==[2.4,2.8,3.2,3.6,4.,4.4,4.75]):raise RuntimeError('FROZEN_GRID_CHANGED')
    r=fit(z,obs,model,C);ref=dfit(z,obs,model,C)
    tol=spec['tolerance'];rtol=tol['relative'];atol=tol['absolute']
    labels=['beta','kappa','Q0','Q2','DeltaQ']; comparisons={}
    for key in labels:
        a=r[key];b=float(ref[key]);delta=abs(a-b);limit=atol+rtol*max(abs(a),abs(b))
        comparisons[key]=dict(value=a,decimal=b,diff=delta,limit=limit,passed=delta<=limit)
    for i in range(2):
        for j in range(2):
            a=r['covariance'][i][j];b=float(ref['cov'][i][j]);delta=abs(a-b)
            limit=tol['variance_abs']+rtol*max(abs(a),abs(b))
            comparisons[f'cov{i}{j}']=dict(value=a,decimal=b,diff=delta,limit=limit,passed=delta<=limit)
    comparisons['source_saved_Q0']=dict(value=r['Q0'],saved=cal['statistical_only']['residual_chi2'],passed=math.isclose(r['Q0'],cal['statistical_only']['residual_chi2'],rel_tol=rtol,abs_tol=atol))
    comparisons['source_saved_beta']=dict(value=r['beta0'],saved=cal['statistical_only']['beta_log10_amplitude'],passed=math.isclose(r['beta0'],cal['statistical_only']['beta_log10_amplitude'],rel_tol=rtol,abs_tol=atol))
    comparisons['nested_nonnegative']=dict(value=r['DeltaQ'],passed=r['DeltaQ']>=-atol)
    comparisons['Q2_Q0_partition']=dict(value=abs(r['DeltaQ']-r['delta_from_slope_identity']),passed=math.isclose(r['DeltaQ'],r['delta_from_slope_identity'],rel_tol=rtol,abs_tol=atol))
    tests=unittest.defaultTestLoader.discover(str(R/'tests'),pattern='test_tilt.py')
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(tests)
    verdict=all(v['passed'] for v in comparisons.values()) and result.wasSuccessful()
    record={'status':'SCOPED_NUMERICAL_PASS' if verdict else 'FAILED','unit_tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'production_vs_reference':comparisons,'new_IVPs':0,'old_runs_replayed':0,'fixed_EOS_theta':0,'physical_F4':'PARTIAL','central_DAG':'28/88','working_REI':'33/88','independent_author_review':'NOT_RUN'}
    (R/'results').mkdir(parents=True,exist_ok=True)
    (R/'results/TEST_RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
    (R/'results/RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
    (R/'results/DECIMAL80_REFERENCE.json').write_text(json.dumps(ref,indent=2)+'\n')
    with (R/'results/TILT_MODEL_ROWS.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['z','x=z-3.6','observed_dex','template_dex','observed-minus-template_dex','model_beta_plus_kappa_x_dex','residual_after_tilt_dex'])
        for i in range(7):w.writerow([z[i],r['x'][i],obs[i],model[i],r['r'][i],r['beta']+r['kappa']*r['x'][i],r['residual2'][i]])
    print(json.dumps({k:r[k] for k in ['beta','kappa','covariance','Q0','Q2','DeltaQ','dof2']},indent=2))
    print('UNIT_COUNT',result.testsRun,'FAILURES',len(result.failures),'REFERENCE_CHECKS',len(comparisons),'ALL_PASS',verdict)
    if not verdict:raise SystemExit(1)
if __name__=='__main__':main()
