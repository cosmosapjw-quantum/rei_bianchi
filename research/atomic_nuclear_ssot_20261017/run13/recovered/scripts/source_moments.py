"""Independent smooth MD14 source integration on the SAME prescribed donor.

This checks source measures, not nonlinear gas/opacity history accuracy.
Time moments use dimensionless elapsed proper time. CDF normalization is a
read-only diagnostic and never changes physical photon weights.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,json,numpy as np,csv
from scipy.integrate import quad,solve_ivp
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'inputs'))
from source_table import BackgroundTable
MPC_CM=3.085677581491367e24

def measure_checks():
 f=json.load(open(R/'inputs/FINITE_BIRTH_PACKET.json'));case=f['case'];x0,x1=f['x0'],f['x1'];dx=x1-x0;t0,t1=f['t0_s'],f['t1_s'];h=t1-t0
 g=BackgroundTable(R/'inputs/bass164/PRODUCER_RECEIPT.json',R/'inputs/bass164/PROPOSED_REI_BACKGROUND.csv')
 logyield=1./(.00038*.002**.227+.01858)-np.log10(2.55)
 # Independent transcription from actual immutable axbi_sources.rs, not a fit substitution.
 def integrand(z,k=0):
  pt=g.point_at_x(case,x0+dx*z);a=f['a0']*np.exp(dx*z);zp=1./a
  jcom=.2*10**logyield*(.015*zp**2.7/(1.+(zp/2.9)**5.6))/MPC_CM**3*1e6
  elapsed=(pt.time_s-t0)/h
  return jcom/pt.h_per_s*dx*elapsed**k
 ref=[]
 for k in range(8):
  q,e=quad(lambda z:integrand(z,k),0.,1.,epsabs=2e-18,epsrel=2e-12,limit=60);ref.append([q,e])
 # Native source sum of photon fractions/angular weights is retained, not rescaled.
 # Comparing a normalized diagnostic CDF does not change the production packet.
 cum=solve_ivp(lambda z,y:[integrand(z)],(0,1),[0.],method='DOP853',rtol=3e-13,atol=1e-18,dense_output=True,max_step=.05)
 rows=[];diagnostics=[]
 for r in [1,2,4,6]:
  p=json.load(open(R/f'inputs/refined/r{r}.json'));a=np.asarray(p['cohorts']);w=a[:,6]*p['a0']**3;u=(a[:,1]-t0)/h
  for k in range(8):
   val=float(np.dot(w,u**k));rows.append({'subdivisions':r,'moment_k':k,'native':val,'reference':ref[k][0],'relative_difference':(val-ref[k][0])/ref[k][0],'quad_error_estimate_abs':ref[k][1]})
  cells=a.reshape(-1,384,9);birth= cells[:,0,0];weight=(cells[:,:,6].sum(axis=1)*p['a0']**3)
  coarsecdf=np.cumsum(weight)/sum(weight);finecdf=cum.sol((birth-x0)/dx)[0]/cum.y[0,-1]
  dcdf=max(np.max(abs(coarsecdf-finecdf)),np.max(abs(np.r_[0.,coarsecdf[:-1]]-finecdf)))
  diagnostics.append({'subdivisions':r,'birth_times':len(birth),'max_normalized_CDF_difference':float(dcdf),'largest_normalized_source_atom':float(max(weight)/sum(weight))})
 with (R/'evidence/SOURCE_MOMENTS.csv').open('w') as f0:
  wr=csv.DictWriter(f0,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 rec={'method':'independently transcribed MD14 comoving emissivity, original Python BASS clock, SciPy quad and scalar DOP853 cumulative source','normalization':'read-only diagnostic, native physical packet never renormalized','moment_relative_max':max(abs(r['relative_difference']) for r in rows),'total_count_relative_max':max(abs(r['relative_difference']) for r in rows if r['moment_k']==0),'reference_photon_count_com3':ref[0][0],'cdf_discrepancy':diagnostics}
 (R/'evidence/SOURCE_MOMENTS.json').write_text(json.dumps(rec,indent=2)+'\n');return rec
if __name__=='__main__':print(json.dumps(measure_checks(),indent=2))
