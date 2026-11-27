"""Read-only audit of PR378 exact commit and claim gates. No merge.
Verify stored hashes, clock controls, event-level budgets and test scope.
"""
import subprocess as sp,json,hashlib,io,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;C='b145729be3d9d103ef1379c9efe5f85687558bc6';BASE='a3cd7cdc3e7cf7c9059c3c420338bdd1d60d0b15'
def git(*args):return sp.check_output(['git','-C',str(D.parent.parent),*args])
def blob(f):return git('show',C+':'+f)
def read(f):return json.loads(blob(f))
def run():
 assert git('ls-remote','origin','refs/pull/378/head').decode().split()[0]==C
 tree=git('rev-parse',C+'^{tree}').decode().strip();assert git('merge-base','HEAD',C).decode().strip()==BASE
 p='research/unified_igm_20261127/';v='components/bass_rec/validation/'
 dag=read(p+'DAG.json');trace=read(v+'ACCEPTED_MATERIAL_TRACE.json');receipt=read(p+'verification/SECOND_LOOP.json')
 hashes={f:hashlib.sha256(blob(f)).hexdigest() for f in receipt['evidence_sha256']};assert hashes==receipt['evidence_sha256']
 rows=np.genfromtxt(io.BytesIO(blob(v+'material_trace_qpos_64.tsv')),names=True,delimiter='\t');slope=(rows['y_DII'][-1]-rows['y_DII'][-2])/(rows['time_s'][-1]-rows['time_s'][-2])
 controls=[]
 for a in trace['matched_proper_time_controls']:
  n=a['accepted_steps'];q=trace['cases'][f'q+0.005_n{n}'];f=trace['cases'][f'q+0.000_n{n}'];m=a['matched_state']
  fixed=q['final_y_DII']-f['final_y_DII'];matched=m['final_y_DII']-f['final_y_DII'];assert fixed==a['fixed_z_y_DII_difference'] and matched==a['matched_time_y_DII_difference']
  controls.append(dict(steps=n,fixed=fixed,matched=matched,reduction=fixed/matched,clock_fraction=abs(a['fixed_z_time_difference_s'])/f['elapsed_proper_s'],H_relative=q['final_H_s']/f['final_H_s']-1,clock_slope=(fixed-matched)/a['fixed_z_time_difference_s'],time_residual=a['matched_time_difference_s'],endpoint_dz=a['adjusted_end_z']-a['FLRW_end_z'],actual_elapsed=f['elapsed_proper_s']))
 long=read('components/wu088_hh/analysis/results/FIVE_CASE_TRACE.json')['signed_responses'];H=long['SHEAR_PLUS'];h=long['SHEAR_HALF_PLUS']
 hh=dict(fixed=H[0]['signed_at_max'],proper=H[1]['signed_at_max'],coarse_relative=[q['paired_coarsening_max_abs_at_common_coordinates']/q['max_abs'] for q in H],half_amplitude_ratios=[H[i]['signed_at_max']/h[i]['signed_at_max'] for i in range(2)])
 he=read('components/bass_he/analysis/F05_CONSERVED_ENERGY.json');assert he['source_rows']==92160
 cr=read(p+'results/cell_plus.json');n=cr['CR_window_births_m3'];fast=cr['native']['born_kinetic_ev_m3'];deb=cr['CR_window_projectile_debit_eV_m3']
 rtest=read(v+'REI_HOST_REGRESSION.json');btest=read(v+'TEST_RESULTS.json')
 # Check actual tracked source unchanged between regression commit and head.
 regression_source_diff=git('diff','--name-only',rtest['tested_source_commit'],C,'--','rust/rei_microphysics','components/bass_rec/bass','components/bass_rec/rec').decode().strip();assert not regression_source_diff
 c=controls[-1];clock_error_est=slope*c['time_residual']
 out=dict(pr_head=C,tree=tree,base=BASE,verified_evidence_sha256=hashes,controls=controls,terminal_trace_slope_per_s=float(slope),estimated_remaining_clock_y=float(clock_error_est),estimated_clock_fraction_of_matched=float(abs(clock_error_est/c['matched'])),scope=dict(D_feedback=trace['D_feedback_on_gas'],CR=trace['cosmic_ray_source'],additional_photo_sinks=trace['additional_photo_sinks_applied'],geometry_feedback=read(p+'results/SECOND_INTEGRATION.json')['native']['scope']),long_D=hh,He=dict(joint=he['simultaneous_total_upper_erg'],marginal=he['unconstrained_sum_of_branchwise_upper_energies_erg'],excess=he['excess_of_marginal_sum_relative_to_joint_upper']),CR=dict(births=n,kinetic=fast,mean_birth_energy_eV=fast/n,projectile_debit=deb,fast_fraction=fast/deb,total_ledger_abs=abs(cr['native']['residual_ev_m3']),transfer_ledger_abs=abs(cr['CR_transfer_partition_residual_eV_m3'])),DAG=dag['count'],admission=receipt['scientific_admission'],recorded_regression=dict(BASS=btest['BASS']['passed'],REC=btest['REC']['passed'],REI=rtest['result']['passed'],source_commit=rtest['tested_source_commit'],source_diff_to_head=regression_source_diff,rerun=False),scope_note='read-only exact Git evidence audit, numerical summaries recomputed, no tests rerun or source changes in integration PR; endpoint slope estimate not rigorous bound')
 (D/'PR378_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='verified_evidence_sha256'},flush=True)
if __name__=='__main__':run()
