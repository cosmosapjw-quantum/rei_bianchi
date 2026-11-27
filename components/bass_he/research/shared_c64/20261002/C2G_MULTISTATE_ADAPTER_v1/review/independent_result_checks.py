"""Read-only C2g evidence audit; no provider/solver/embedding imports.
Angular orthogonality is integrated analytically. Each independent radial
reduction uses six Gauss points per union element and degree-four Lobatto
basis recovered via its Vandermonde interpolation equations.
"""
from pathlib import Path
import hashlib,json,os,time
from datetime import datetime,timezone
import numpy as np
from numpy.polynomial.legendre import Legendre,leggauss
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def identity(p):
 p=Path(p); b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def exact_identity(record):
 actual=identity(record['path']);assert actual==record,(actual,record)
def close(actual,expected,tol,label):
 delta=float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))));assert delta<=tol,(label,actual,expected,delta,tol);return delta

def archive(path):
 with np.load(path,allow_pickle=False) as a:
  out={k:a[k].copy() for k in a.files}
 out['doc']=json.loads(out['metadata_json'].tobytes());return out

def radial_frame(a,knots,ordinals):
 # Distinct numerical path: solve the monomial Vandermonde interpolation
 # equations, evaluate all radial channels at once, integrate angles exactly.
 degree=a['doc']['degree'];assert degree==4
 nodes=np.r_[-1.,Legendre.basis(degree).deriv().roots(),1.]
 interpolation=np.linalg.solve(np.vander(nodes,increasing=True),np.eye(degree+1))
 x,w=leggauss(6);r=(knots[:-1,None]+knots[1:,None])/2+(knots[1:,None]-knots[:-1,None])*x/2
 weights=(knots[1:,None]-knots[:-1,None])*w/2;r=r.ravel();weights=weights.ravel()
 b=a['boundaries'];idx=np.searchsorted(b,r,side='right')-1
 assert np.all((idx>=0)&(idx<len(b)-1))
 q=2*(r-b[idx])/(b[idx+1]-b[idx])-1
 basis=np.vander(q,N=degree+1,increasing=True)@interpolation
 c=a['coefficients'][ordinals]
 vals=np.einsum('klpj,pj->plk',c[:,:,idx[:,None]*degree+np.arange(degree+1)],basis,optimize=True)
 # dimensions radial_sample, l, selected_root; padded angular channels below.
 return vals,weights,r

def frame_pair(a,b,oa,ob):
 knots=np.unique(np.r_[a['boundaries'],b['boundaries'],16.]);ua,w,r=radial_frame(a,knots,oa);ub,wb,rb=radial_frame(b,knots,ob)
 assert np.array_equal(w,wb) and np.array_equal(r,rb)
 L=max(ua.shape[1],ub.shape[1]);A=np.zeros((len(r),L,len(oa)));B=np.zeros((len(r),L,len(ob)))
 A[:,:ua.shape[1]]=ua;B[:,:ub.shape[1]]=ub
 return (A*np.sqrt(w)[:,None,None]).reshape(-1,len(oa)),(B*np.sqrt(w)[:,None,None]).reshape(-1,len(ob))

def white(A):
 G=A.T@A; e,v=np.linalg.eigh(G);assert min(e)>0
 return A@((v/np.sqrt(e)[None,:])@v.T)

def compare(a,b,oa,ob):
 A,B=frame_pair(a,b,oa,ob);U,V=white(A),white(B);over=U.T@V
 sigma=np.linalg.svd(over,compute_uv=False);res=V-U@over
 return float(np.linalg.svd(res,compute_uv=False)[0]),float(sigma[-1])

def observables(a,ordinals):
 knots=np.unique(np.r_[a['boundaries'],16.]);u,w,r=radial_frame(a,knots,ordinals)
 A=(u*np.sqrt(w)[:,None,None]).reshape(-1,len(ordinals));G=A.T@A;e,v=np.linalg.eigh(G);C=(v/np.sqrt(e)[None,:])@v.T
 rr=np.repeat(r,u.shape[1]);N=A@C
 return {'mass_gram':G,'trace_r2':float(np.sum(N*N*rr[:,None]**2)),
 'outer_layer':float(np.linalg.eigvalsh(N[rr>=16].T@N[rr>=16])[-1])}

def main():
 started=time.monotonic(); review=load(ROOT/'review/PRELAUNCH_INDEPENDENT_REVIEW.json');pre=load(ROOT/'contract/PHYSICAL_PREREGISTRATION.json');manifest=load(ROOT/'contract/PHYSICAL_TASKS.json');analysis=load(ROOT/'results/analysis/ANALYSIS.json');runtime=load(ROOT/'results/ANALYSIS_RUNTIME.json');ledger=load(ROOT/'results/campaign_ledger/AMENDED_COMPLETED.json')
 checks=[];records=[]
 for field in ('manifest','preregistration','postprocess_helper','integrated_test_evidence','independent_check_source','independent_check_evidence'):exact_identity(review[field])
 for ident in review['source_identity'].values():exact_identity(ident)
 for name in ('source','build_metadata','library'):exact_identity(review['native_identity'][name])
 assert ledger['status']=='PASS' and ledger['successful_layouts']==2 and ledger['sector_solves_completed']==24 and ledger['independent_roots_returned']==108 and ledger['source_unchanged']
 checks.append('prelaunch exact code, contracts, native library, build and evidence bytes unchanged')
 assert ledger['launch_attempts']==3 and ledger['prephysics_failed_attempts']==1 and ledger['original_failure_preserved']
 for rec in ledger['evidence']:exact_identity(rec)
 assert ledger['wall_seconds_all_attempts']<=pre['campaign']['max_total_layout_wall_seconds']
 close(ledger['wall_seconds_all_attempts'],sum(load(rec['path'])['process']['wall_seconds'] for rec in ledger['evidence']),0.,'all-attempt wall sum')
 checks.append('campaign total exactly 2 successful layouts, 24 sector solves, 108 independent roots; original pre-physics failure retained and all three attempts within 600 seconds')
 assert runtime['status']=='PASS' and runtime['physical_eigensolves']==0 and runtime['source_unchanged']
 assert runtime['process']['termination'] is None and runtime['process']['returncode']==0
 assert runtime['process']['wall_seconds']<=pre['campaign']['postprocess_wall_seconds']
 assert runtime['process']['sampled_owned_rss_peak_bytes']<=4*1024**3
 exact_identity(runtime['result']);exact_identity(runtime['helper_identity'])
 assert analysis['status']=='ANALYSIS_COMPLETE' and analysis['eigensolves_started_by_analysis']==0
 assert analysis['registered_thresholds_unchanged']==pre['gates']
 for name,value in {'full_C2_closed':False,'scientific_PROMOTE':'HOLD','full_H_certificate':False,'continuum_certificate':False,'PDE_residual_certified':False,'atomic_correlation_established':False,'outside_box_tail_bound':False,'Eq55':'NOT_RUN','Eq55_next_node_authorized':False,'NCP64_actual_scaling':False,'production_default_change':'NOT_AUTHORIZED'}.items():assert analysis['scope'][name]==value
 original_helper=(ROOT/'provenance/run_analysis_bounded.py').read_bytes(); retry_helper=(ROOT/'provenance/run_analysis_bounded_retry1.py').read_bytes(); assert retry_helper==original_helper.replace(b'results/native_mpi_2x1.json', b'results/native_mpi_2x1_retry1.json')
 checks.append('postprocess limits and fail-closed scientific scope preserved; retry helper differs only by approved native result path')
 layouts={};layout_evidence={};totalroots=0
 for layout in pre['campaign']['layouts']:
  name=layout['id'];launch=load(ROOT/'results'/(f'{name}_retry1.json' if name=='native_mpi_2x1' else f'{name}.json'));assert launch['status']=='PASS' and launch['post_identity_error'] is None
  process=launch['process'];assert process['returncode']==0 and process['termination'] is None
  assert process['wall_seconds']<=pre['campaign']['per_layout_wall_seconds'] and process['sampled_owned_rss_peak_bytes']<=4*1024**3
  exact_identity(launch['context']);exact_identity(launch['worker_result']);context=load(launch['context']['path']);worker=load(launch['worker_result']['path']);assert context['source']==review['source_identity'];assert worker['status']=='PASS' and not worker['post_identity_errors']
  assert sorted(x['rank'] for x in worker['workers'])==list(range(layout['ranks']))
  assert len(worker['results'])==12
  arch={}
  for i,(task,row) in enumerate(zip(manifest['tasks'],worker['results'])):
   assert row['task']==task and row['task_id']==task['task_id'] and row['task_index']==i and row['rank']==i%layout['ranks'] and row['status']=='PASS' and row['backend']==layout['backend']
   exact_identity(row['receipt']);assert load(row['receipt']['path'])=={k:v for k,v in row.items() if k!='receipt'}
   ref=row['result']['archive'];fi=identity(ref['source_path']);assert (fi['sha256'],fi['bytes'])==(ref['source_sha256'],ref['source_bytes'])
   a=archive(ref['source_path']);assert len(a['energies'])==task['nroots'];totalroots+=len(a['energies']);assert a['doc']['source_id']==task['task_id'];assert a['doc']['archive_writer_sha256']==review['source_identity']['code/multistate_provider.py']['sha256'];assert np.array_equal(a['energies'],row['result']['energies']);assert np.array_equal(a['residuals'],row['result']['algebraic_residuals']);assert np.array_equal(a['boundaries'],task['boundaries']);assert a['doc']['m']==task['m'] and a['doc']['R']==task['R']
   assert np.all(np.diff(a['energies'])>=0) and np.all(a['coefficients'][:,:,(0,-1)]==0)
   assert np.array_equal(a['coefficients'][:,:,1:-1].reshape(len(a['energies']),-1).T,a['coefficient_vectors'])
   o=observables(a,list(range(task['nroots'])));close(o['mass_gram'],a['mass_gram'],2e-12,f'{name}/{task["task_id"]}/independent_mass')
   arch[(task['level'],task['R'],task['m'])]=a
  layouts[name]=arch;layout_evidence[name]={'wall_seconds':process['wall_seconds'],'sampled_owned_rss_peak_bytes':process['sampled_owned_rss_peak_bytes'],'launch':identity(ROOT/'results'/(f'{name}_retry1.json' if name=='native_mpi_2x1' else f'{name}.json')),'roots':54,'sector_solves':12}
 assert totalroots==108
 checks.append('all task ownership, archive SHA256, root count, coefficients and independent radial mass Gram verified')
 diffs={'trace_r2':0.,'outer_layer':0.,'basis_projector':0.,'cross_R_projector':0.,'backend_projector':0.,'backend_energy':0.};independent={'observables':{},'basis':{},'cross_R':{},'backend':{}}
 levels=[x['name'] for x in pre['basis']['levels']];Rs=pre['physical_model']['R_set'];names=[x['id'] for x in pre['campaign']['layouts']]
 for name in names:
  arch=layouts[name]
  for lev in levels:
   for R in Rs:
    o0=observables(arch[(lev,R,0)],[1,2,3]);o1=observables(arch[(lev,R,1)],[0]);value={'trace_r2':o0['trace_r2']+2*o1['trace_r2'],'outer_layer':max(o0['outer_layer'],o1['outer_layer'])};label=f'{name}/{lev}/R{R}';independent['observables'][label]=value
    for grid in ('registered','refined'):
     target=analysis['snapshot_diagnostics'][grid][name][f'{lev}/R{R}'];diffs['trace_r2']=max(diffs['trace_r2'],close(value['trace_r2'],target['trace_r2'],2e-10,label+'/trace_r2'));diffs['outer_layer']=max(diffs['outer_layer'],close(value['outer_layer'],target['outer_layer_probability_max'],2e-12,label+'/outer_layer'))
   sector=[compare(arch[(lev,Rs[0],m)],arch[(lev,Rs[1],m)],ords,ords) for m,ords in [(0,[1,2,3]),(1,[0])]];value={'projector_operator_distance':max(x[0] for x in sector),'principal_overlap_sigma_min':min(x[1] for x in sector)};independent['cross_R'][f'{name}/{lev}']=value
   for grid in ('registered','refined'):
    target=analysis['cross_R'][grid][name][lev];diffs['cross_R_projector']=max(diffs['cross_R_projector'],close(value['projector_operator_distance'],target['projector_operator_distance'],2e-11,name+'/'+lev+'/cross_R'));close(value['principal_overlap_sigma_min'],target['principal_overlap_sigma_min'],2e-11,'cross_R sigma')
  for lower,upper in zip(levels,levels[1:]):
   for R in Rs:
    sector=[compare(arch[(lower,R,m)],arch[(upper,R,m)],ords,ords) for m,ords in [(0,[1,2,3]),(1,[0])]];dist=max(x[0] for x in sector);label=f'{lower}_to_{upper}/R{R}';independent['basis'][f'{name}/{label}']=dist;diffs['basis_projector']=max(diffs['basis_projector'],close(dist,analysis['basis_refinement'][name][label]['projector_operator_distance'],2e-11,'basis projector'))
 for lev in levels:
  for R in Rs:
   sector=[compare(layouts[names[0]][(lev,R,m)],layouts[names[1]][(lev,R,m)],ords,ords) for m,ords in [(0,[1,2,3]),(1,[0])]];dist=max(x[0] for x in sector);energy=max(float(np.max(np.abs(layouts[names[0]][(lev,R,m)]['energies']-layouts[names[1]][(lev,R,m)]['energies']))) for m in (0,1));label=f'{lev}/R{R}';independent['backend'][label]={'projector_operator_distance':dist,'energy_max_abs_error':energy};diffs['backend_projector']=max(diffs['backend_projector'],close(dist,analysis['backend_parity'][label]['projector_operator_distance'],2e-11,'backend projector'));diffs['backend_energy']=max(diffs['backend_energy'],close(energy,analysis['backend_parity'][label]['all_returned_energy_max_abs_error'],0.,'backend energy'))
 checks.append('independent analytic-angular/radial mass-form observables, cross-R/basis projectors and backend parity agree with 3D common-grid analysis')
 rows=analysis['gates']['all'];failed=[]
 for row in rows:
  assert np.isfinite(row['value']) and np.isfinite(row['threshold']);passed=row['value']<=row['threshold'] if row['comparison']=='<=' else row['value']>row['threshold'];assert passed==row['pass']
  if not passed:failed.append(row)
 assert analysis['gates']['failed_count']==len(failed) and analysis['gates']['first_failed_gate']==(failed[0] if failed else None)
 for cat in ('implementation','candidate_transport','finite_basis_exploration'):assert analysis['gates'][cat+'_pass']==all(x['pass'] for x in rows if x['category']==cat)
 checks.append('every scalar gate recomputed with frozen threshold and failure list preserved')
 out={'schema':'bass-he.c2g.independent-result-check.v1','status':'PASS_FOR_EVIDENCE_CONSISTENCY','checks':checks,'input_analysis':identity(ROOT/'results/analysis/ANALYSIS.json'),'input_runtime':identity(ROOT/'results/ANALYSIS_RUNTIME.json'),'independent_method':'Angular orthogonality integrated analytically; degree-four Lobatto FEM interpolated by Vandermonde inverse; positive six-point GL on radial union including r=16. No production solver/provider/embedding modules imported.','max_difference_from_author_analysis':diffs,'independent_reductions':independent,'layout_evidence':layout_evidence,'gate_categories':{cat:analysis['gates'][cat+'_pass'] for cat in ('implementation','candidate_transport','finite_basis_exploration')},'failed_gates':failed,'gate_count':len(rows),'roots_examined':totalroots,'reviewer_eigensolves':0,'elapsed_seconds':time.monotonic()-started,'utc':datetime.now(timezone.utc).isoformat(),'limitations':['No recomputation of finite generalized residual from H and M: full matrices not persisted; compared exact archive/receipt scalar and prelaunch code evidence.','No continuum certificate, physical PDE residual, atomic correlation or NCP64 scaling claim.','This independent reduction verifies finite-basis output consistency, not true discretization accuracy.']}
 out['review_source']=identity(__file__)
 path=ROOT/'review/INDEPENDENT_RESULT_CHECKS.json'
 with path.open('x') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:out[k] for k in ('status','max_difference_from_author_analysis','gate_categories','gate_count','roots_examined','elapsed_seconds')},indent=2))
if __name__=='__main__':main()
