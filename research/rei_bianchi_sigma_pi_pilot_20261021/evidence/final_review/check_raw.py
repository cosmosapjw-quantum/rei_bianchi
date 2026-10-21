"""Read-only independent raw-result audit; no integration or solver implementation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,csv,math,hashlib
from pathlib import Path
import numpy as np
from scipy.linalg import expm
P=Path(__file__).resolve().parents[1]/'repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021'
sys.path.insert(0,str(P/'vendor'))
from canonical_fv import CanonicalMomentumFV
from lrs_boltzmann import legendre_matrix
R=P/'results/pilot';run=json.loads((R/'run.json').read_text());lock=json.loads((P/'vendor/REI_BACKGROUND_FAMILY_LOCK.json').read_text());cos=lock['cosmology'];a0=lock['clock']['a_ref'];h0=cos['H0_per_s'];om=cos['Omega_m'];orr=cos['Omega_r'];ol=cos['Omega_lambda'];href=h0*math.sqrt(om/a0**3+orr/a0**4+ol);mpref=.1*om/a0**3
M=CanonicalMomentumFV(30.,0.,24,12,3);A=legendre_matrix(8,power=4)[::2,::2]
for row in json.loads((P/'SOURCE_ATTRIBUTION.json').read_text())['files']:
 v=(P/row['vendored_path']).read_bytes();o=(P.parents[2]/'intake/repo/source147'/row['original_path']).read_bytes() if False else (Path(__file__).resolve().parents[1]/'intake/repo/source147'/row['original_path']).read_bytes()
 assert v==o and hashlib.sha256(v).hexdigest()==row['sha256']
for name,sha in run['identity']['model_files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha
csvrows={r['id']:r for r in csv.DictReader((R/'endpoints.csv').open())};files=sorted((R/'cases').glob('*.json'));assert len(files)==len(csvrows)==len(list((R/'cases').glob('*.npz')))==625
stats={'cases':0,'samples':0,'max_observable_recompute_abs':0.,'max_axis_abs':0.,'max_expm_energy_abs':0.,'max_endpoint_csv_abs':0.,'max_abs_k':0.,'minimum_brightness':1e99,'minimum_H':1e99,'minimum_E0':1e99,'max_reference_abs':0.,'max_reference_gamma_nu_abs':0.,'max_reference_number_abs':0.,'max_full_odd_energy_abs':0.};keys=set();child=0.
for p in files:
 row=json.loads(p.read_text());c=row['case'];assert row['status']=='COMPLETED' and row['exit_status']==0 and row['identity']==run['identity'];assert c['id']==p.stem
 keys.add((c['eps_sigma']*c['Sigma0'],c['eps_pi']*c['Pi0']));d=np.load(p.with_suffix('.npz'));y=d['state'];x=d['x'];assert y.shape==(8,65) and x.shape==(65,) and np.all(np.diff(x)>0)
 for k in d.files:assert np.isfinite(d[k]).all()
 assert abs(x[0])<1e-15 and abs(x[-1]-math.log(.2/a0))<1e-14
 a=a0*np.exp(x);m=M.moment_batch(x,y[1]);s=href*y[2];H=np.sqrt(h0*h0*(.9*om/a**3+mpref*m[:,0]+orr/a**4*y[3]+ol)+s*s);pn=orr/a**4*y[4]/3+mpref*(m[:,2]-m[:,1])/3
 calc={'Sigma':math.sqrt(3)*abs(s)/H,'signed_Pi':math.sqrt(3)*3*h0*h0*pn/H**2,'s_over_H':s/H,'H_per_s':H,'b':y[1],'E0':y[3],'E2':y[4]}
 for k,v in calc.items():stats['max_observable_recompute_abs']=max(stats['max_observable_recompute_abs'],float(np.max(abs(v-d[k]))))
 assert np.all(H>0) and np.all(y[3]>0) and row['min_massive_cell_population']>=0
 stats['max_axis_abs']=max(stats['max_axis_abs'],abs(calc['Sigma'][0]-c['Sigma0']),abs(calc['signed_Pi'][0]-c['eps_pi']*c['Pi0']))
 for i in (16,32,48,64):stats['max_expm_energy_abs']=max(stats['max_expm_energy_abs'],float(np.max(abs(expm(y[1,i]*A)@y[3:,0]-y[3:,i]))))
 for k,v in row['endpoint'].items():
  assert v==float(d[k][-1]);stats['max_endpoint_csv_abs']=max(stats['max_endpoint_csv_abs'],abs(float(csvrows[c['id']][k])-v))
 for k in ('Sigma0','Pi0','eps_sigma','eps_pi','sigma_index','pi_index'):assert float(csvrows[c['id']][k])==c[k]
 stats['cases']+=1;stats['samples']+=len(x);stats['max_abs_k']=max(stats['max_abs_k'],abs(row['initial']['k']));stats['minimum_brightness']=min(stats['minimum_brightness'],float(d['sampled_min_angular_brightness'].min()));stats['minimum_H']=min(stats['minimum_H'],float(H.min()));stats['minimum_E0']=min(stats['minimum_E0'],float(y[3].min()));child+=row['child_wall_s']
assert len(keys)==625 and child==run['aggregate_child_wall_s']
metrics=json.loads((P/'results/validation/metrics.json').read_text())
for i,entry in enumerate(metrics['comparisons']):
 d=np.load(P/f'results/validation/comparison_{i}.npz');f=d['full_state'];assert f.shape==(40,65)
 for k,claimed in entry['max_abs_difference'].items():
  actual=float(np.max(abs(d['reduced_'+k]-d['full_'+k])));assert actual==claimed;stats['max_reference_abs']=max(stats['max_reference_abs'],actual)
 stats['max_reference_gamma_nu_abs']=max(stats['max_reference_gamma_nu_abs'],float(np.max(abs(f[4:13]-f[22:31]))));stats['max_reference_number_abs']=max(stats['max_reference_number_abs'],float(np.max(abs(f[[13,31]]-1))));stats['max_full_odd_energy_abs']=max(stats['max_full_odd_energy_abs'],float(np.max(abs(f[[5,7,9,11,23,25,27,29]]))))
for e in metrics['angular_checks']:
 _,pi,sign=e['case'];d=np.load(P/f'results/validation/L12_pi{pi}_sign{sign}.npz');cid=f's12_{sign:+d}_p12_{int(np.sign(pi)):+d}';r=np.load(R/'cases'/f'{cid}.npz')
 for k,v in e['endpoint_L8_L12_abs'].items():assert abs(abs(float(d[k][-1]-r[k][-1]))-v)<1e-15
for folder in ('plots','plots_v2'):
 if not (R/folder).exists():continue
 rows=list(csv.DictReader((R/folder/'heatmap_plot_data.csv').open()));assert len(rows)==676
 for r in rows:
  c=csvrows[r['case_id']];assert float(r['Sigma0'])==float(c['Sigma0']) and float(r['Pi0'])==float(c['Pi0']) and float(r['Sigma_end'])==float(c['Sigma'])
  assert int(c['eps_sigma']) in (0,int(r['eps_sigma_panel'])) and int(c['eps_pi']) in (0,int(r['eps_pi_panel']))
 receipt={p.parent.name:json.loads(p.read_text())['exit_status'] for p in (P/'receipts').glob('*/command.json')};assert all(v==0 for v in receipt.values())
stats.update({'unique_signed_pairs':len(keys),'recomputed_child_wall_s':child,'receipts_exit_status':receipt,'source_bytes_match_original':True,'model_hashes_match_executed_identity':True,'expm_checked_times_per_case':4,'review_mode':'read-only no integrations'})
Path(__file__).with_name('RAW_AUDIT.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
