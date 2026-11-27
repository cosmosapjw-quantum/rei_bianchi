"""Create the bounded C2e specification; never launch a scientific solver."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def create(name,value):
    data=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    path=ROOT/name
    tmp=path.with_suffix(path.suffix+'.pending')
    if path.exists():raise FileExistsError(path)
    with tmp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()
    fd=os.open(path.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)

contract={
 'schema':'bass-he.c2e.domain-target.v1',
 'node':'C2E_COLLISION_DOMAIN_AND_SPECTRAL_TARGET_CONTRACT',
 'scope':'conditional domain maps and static electronic spectral-target semantics; no physical solves',
 'evidence_status':{'source_recovery':'SOURCE_BOUND','domain_maps':'DERIVED','target_definitions':'DERIVED','production_domain':'UNRESOLVED','numerical_projector_isolation':'NOT_RUN'},
 'authority':{'parent_commit':'67ba38b0e8665543840fcb674bb8310fd47f7266','original_prompt_sha256':hashlib.sha256((ROOT/'provenance/USER_CONTRACT_ORIGINAL.txt').read_bytes()).hexdigest(),'source_note':'source_notes/DOMAIN_AUTHORITY.json'},
 'conventions':{'electron_count':1,'spin':'omitted','relativity':'nonrelativistic','charges_e':[1,2],'electronic_origin':'charge_center_O','nuclear_center_of_mass_is_electronic_origin':False,'a_A':'hbar^2/(m_e*kappa)','E_A':'hbar^2/(m_e*a_A^2)','kappa':'e^2/(4*pi*epsilon0)','nuclear_repulsion_in_H_e':False,'H_e_continuum_threshold_E_A':0,'nuclear_repulsion_if_added':'2*kappa/R; shifts every electronic eigenvalue and continuum threshold together'},
 'collision_domain':{
   'priority_energy_anchors':[{'value':.5,'unit':'keV/u','status':'RESEARCH_PRIORITY_ONLY'},{'value':5.,'unit':'keV/u','status':'RESEARCH_PRIORITY_ONLY'}],
   'production_energy_frame':None,'mass_normalization':None,'projectile_isotope_and_mass':None,'target_isotope_and_mass':None,
   'production_trajectory':None,'finite_b_interval':None,'finite_time_or_z_window':None,'production_R_interval':None,
   'formal_impact_integral':'2*pi*integral_0^infinity b*P_f(b) db',
   'families':{
      'straight_line':{'authority':'requested comparison family, not selected production model','assumptions':['R_vector=(b,0,v*t)','b>=0','v>0','closest approach at t=0'],'R':'sqrt(b^2+v^2*t^2)','R_min':'b','angular_speed_abs':'b*v/R^2','head_on_R_zero':True},
      'repulsive_Rutherford':{'authority':'requested conditional comparison family','assumptions':['relative central U(R)=K/R','K>0','E_cm>0','J=mu*v*b'],'R_min':'K/(2*E_cm)+sqrt((K/(2*E_cm))^2+b^2)','head_on_R_min':'K/E_cm','bare_nuclear_K':'2*kappa','neutral_entrance_screening_included':False},
      'coupled_classical':{'authority':'requested downstream F1 comparison','force_law':None,'initial_conditions':None,'R_domain':'must derive from selected equations and solution'}},
   'diagnostic_cutoffs_imported_as_physical_domain':False,
   'source_energy_frames_are_interchangeable':False,
   'full_C2_collision_coverage_certified':False,
   'missing_production_inputs':['production_energy_frame','mass_normalization','projectile_isotope_and_mass','target_isotope_and_mass','production_trajectory','finite_b_interval','finite_time_or_z_window','production_R_interval']},
 'targets':{
   'fixed_pair':{'rank':2,'members':['lowest_m0_g','lowest_abs_m1_cos_phi_bright'],'static_invariant_subspace':True,'projector_type':'symmetry_resolved_observable_pair','is_full_H_energy_Riesz_projector':False,'full_H_external_gap':0,'excluded_exact_degenerate_partner':'sin_phi_dark','incoming_H1s_included':False,'closure':'C2a-d specified pair observables and finite-point empirical tests only'},
   'large_R_rank5':{'rank':5,'atomic_members':['H_1s','He_2s','He_2p_m0','He_2p_m_plus1','He_2p_m_minus1'],'sector_ranks':{'m0':3,'m_plus1':1,'m_minus1':1},'spin_included':False,'large_R_cluster_energy_E_A':-.5,'isolation':'qualitative sufficiently-large-R asymptotic cluster; finite collision interval unverified','finite_interval_R':None,'certified_external_gap_lower_bound':None,'quantitative_large_R_start':None,'actual_UA_correlation_established':False,'equal_to_lowest_five_excited_for_all_R_claimed':False,'uniform_full_H_gap_to_R_zero_claimed':False,'transport':'orthonormal frame overlap SVD/polar transport when sigma_min>registered threshold; internal crossings do not alone close exterior gap'},
   'ground_plus_rank5':{'rank':6,'status':'asymptotic channel embedding candidate, not certified six-channel dynamics','includes_exact_Q_completion_in_formulation':True,'finite_Q_truncation_accuracy_certified':False},
   'D1_model':{'original_minimum_rank':3,'fourth_state':'requires bounded justification in original contract','replaced_by_rank5_or_rank6_automatically':False,'status':'NOT_RELEASED'},
   'planar_even_reduction':{'status':'CONDITIONAL_NOT_ADOPTED','required':['entire trajectory/frame/ETF generator preserves y-reflection','incoming channel even'],'large_R_cluster_even_rank':4,'with_ground_even_rank':5}},
 'error_contract':{
   'empirical_convergence_is_continuum_enclosure':False,'Ritz_gap_is_certified_external_gap':False,'L2_projector_error_certifies_Ly_matrix_elements':False,
   'needed_enclosures':['bound/essential-spectrum exterior separation','continuum discretization and spatial tail','projector error in required norm','weighted derivative or observable form bound for L_y','interval variation between nodes','time and impact tails only after an actual collision model is specified'],
   'new_numeric_tolerances':None,'new_R_grid':None,'existing_tolerances':'parent pair criteria preserved for reuse only; not silently assigned to new projector gates'},
 'execution':{'new_eigensolves':0,'new_scientific_quadratures':0,'new_time_propagations':0,'old_scientific_suites_rerun':0,'Eq55':'NOT_RUN','NCP64_actual_scaling':'NOT_RUN','manufactured_semantic_tests_only':True,'execution_ready':False,'scientific_commands':[]},
 'hpc_policy':{'hot_kernels':'binary64 Fortran/OpenMP/SIMD','task_parallelism':'explicit OpenMPI','fast_math':False,'implicit_backend_fallback':False,'same_workload_performance_measurement_required':True,'actual_host_preflight_required':True,'local_unbound':'BASS_LOCAL_UNBOUND=1 and OMP_PROC_BIND=FALSE','NCP_default_binding':'core/close'},
 'global_gates':{'CODE_I02_CLOSED':True,'full_C2_closed':False,'scientific_PROMOTE':'HOLD','full_certificate_fail_closed':True,'Eq55_next_node_authorized':False,'production_default_change':'NOT_AUTHORIZED'},
 'next_single_node':'C2F_SYMMETRY_COMPLETE_CLUSTER_PROJECTOR_IMPLEMENTATION',
 'closure_meaning':'definitions and conditional domain maps fixed; physical production domain and spectral isolation remain open'
}
create('contract/C2E_TARGET_AND_DOMAIN_CONTRACT.json',contract)
draft={
 'schema':'bass-he.c2f.preregistration-draft.v1','node':contract['next_single_node'],
 'status':'DESIGN_AND_MANUFACTURED_TESTS_ONLY__PHYSICAL_LAUNCH_DISABLED',
 'purpose':'implement multi-state symmetry-complete target selection and projector transport before any new physical interval claim',
 'interfaces':['eigensolver returns all requested m-sector Ritz vectors plus exterior guard states and residual metadata','do not select only a single bright vector for a full-H projector','distinguish energy-contour target from symmetry-block target','principal angles from singular values; polar transport covariant under U(k) rotations','exterior gaps separated from internal splittings and reported as Ritz diagnostics until enclosure'],
 'manufactured_acceptance':['random unitary rotations preserve projector','internal exact degeneracy does not fail full-cluster transport','omitted exact-degenerate partner rejects full-H isolation','external gap closure blocks an isolation claim','small singular value stops transport rather than rephasing an individual state','source/state identity and all bounds preserved'],
 'physical_launch_enabled':False,'exact_R_set':None,'target_at_each_R':None,'basis_and_box':None,'guard_state_count':None,'norm_and_projector_thresholds':None,'gap_certificate_method_and_threshold':None,'wall_memory_and_eigenstate_budget':None,
 'prerequisites_for_physical_manifest':['all null execution parameters explicitly registered and independently reviewed','cost/resource preflight','reuse C2d states only where state/target/discretization identities match','same strict numerical/HPC policy'],
 'forbidden_promotions':['no D1 propagation','no Eq55','no full_C2 closure','no production benchmark fit','no inherited pair tolerances silently reused for projector accuracy'],
 'next_after_implementation':'choose one bounded physical reference task only after its separate concrete preregistration is complete'
}
create('contract/C2F_PREREGISTRATION_DRAFT.json',draft)
print(json.dumps({'contract_created':True,'next_node':draft['node'],'physical_launch_enabled':False}))
