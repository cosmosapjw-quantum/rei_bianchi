from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[1]
def save(name,obj):
    p=R/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    return hashlib.sha256(p.read_bytes()).hexdigest()
result=json.loads((R/'results/RESULT.json').read_text())
source={
 'schema':'REI_SAVED17_SOURCE_RECONCILIATION_V1',
 'original_model':{'repo':'cosmosapjw-quantum/rei_bianchi','path':'research/rei_external_sources_20261028/implementation/model.py','git_blob':'1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc','representation':'typed topology extracted from GitHub; original full bytes not copied'},
 'original_saved_csv':{'repo':'cosmosapjw-quantum/rei_bianchi','commit':'022f2ed85595364f05834d8eb1573434efce92d0','path':'research/rei_source_history_20261028/outputs/pilot17_populations.csv','git_blob':'189c2d903e25c18bee49e0ab6add3ba1d1805e93'},
 'selected_saved_rows':{'count':7,'states_per_row':17,'selected_json_sha256':'7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77','canonical_numeric_format':'%.16e z,elapsed,17 populations joined by | and LF','canonical_length':3059,'FNV1a64':'174743cb945f8bfe','relation':'numeric content equality of selected 7 rows at 17 significant digits; not full CSV byte equality'},
 'parent_pr261':{'head':'8a3107a6477a648ad87a4db2a52240c1bea4cc42','BB13_raw_sha256':'13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b','P19_projection_sha256':'dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff','P19_original_git_blob':'218d81f68447da438228a7b102e1cec96a8e8a1a'},
 'source_exclusions':['No full model.py byte copy','No 361-epoch trajectory re-integration','No Li photoionization source','No actual electron density or physical K','No source spectrum reconstruction']
}
save('SOURCE_RECONCILIATION.json',source)
contract={
 'schema':'REI_UVB_SAVED17_SOURCE_TANGENT_CONTRACT_V1','unit':'REI_UVB_SAVED17_SOURCE_TANGENT_20261029','parent_PR':261,
 'state_order':'n,H1_0,H1_1,D_0,D_1,T_0,T_1,He3_0,He3_1,He3_2,He4_0,He4_1,He4_2,Li7_0,Li7_1,Li7_2,Li7_3',
 'state_units':'number per Href','time':'proper elapsed seconds; source frozen at saved z_mean','z_domain':[2.4,4.75],
 'parameters':['beta (dex)','kappa (dex per redshift)'],'moments_order':['Gamma_HI_s-1','heat_HI_eV_s-1','Gamma_HeI_s-1','heat_HeI_eV_s-1','Gamma_HeII_s-1','heat_HeII_eV_s-1'],
 'model':'F_UVB=S diag(E*y) P R6; R6=R6_P19 10**(beta+kappa*(z-3.6))',
 'jacobians':{'J_y_photo_only':'S diag(P R6) E (17x17)','J_R_photo_only':'S diag(E*y) P (17x6)','B_a_photo_only':'ln(10) F_UVB outer (1,z-3.6) (17x2)','electron_source':'Q^T F_UVB','electron_source_jac':'Q^T B_a'},
 'identities':['A^T S=0','1^T S=0','Q^T S=ones(7)','mu1(J_y_photo_only)=0','rank(B_a(z))<=1','rank(stack(B_a(z_i)))=2 if two nonzero blocks and distinct z'],
 'energy':{'threshold_eV':[13.6,13.6,13.6,24.6,54.4,24.6,54.4],'ionization_storage':'sum I_k*y_source,k*Gamma_k','photoelectron_excess':'sum y_source,k*heat_k','absorbed_photon':'ionization_storage+photoelectron_excess','thermalization':'NOT_BOUND_NO_AUTO_DEPOSITION'},
 'envelopes':{'source':'PR260 conditional Z+Gaussian ellipsoid','deterministic_q':0,'joint2_95_q':5.991464547107982,'interpretation':'pointwise frozen-state source-rate bounds, not physical n_e posterior or trajectory envelope'},
 'acceptance':{'python_new_tests':'15/15 PASS','cpp_direct_event_rows':'7/7 PASS','cpp_max_relative_component_error':3.251e-16,'max_baryon_B_residual':max(x['baryon_source_max_abs'] for x in result['entries']),'max_rankone_B_residual':max(x['rank1_frobenius_residual'] for x in result['entries'])},
 'exclusions':['full J_y chemistry','full state sensitivity D_a y','actual D_a n_e','physical K,nHref,H binding','Bianchi directional observed redshift','tau tangent','source error radii','new IVP'],
 'dag':{'working_completed':33,'central_last_completed':28,'total':88,'new_physical_nodes':0},
 'production':{'F4':'PARTIAL','L4_ready':False,'physical_temperature':None,'native25':None,'physical_radii':None,'no_more_ivps':True}
}
save('CONTRACT.json',contract)
overlay={'schema':'REI_UVB_SAVED17_SOURCE_TANGENT_DAG_OVERLAY_V1','original':{'working':'33/88','central_last':'28/88','delta':0,'mutated':False},'nodes':[
 {'id':'SAVED17_UVB_JR','status':'IMPLEMENTED_SCOPED_REVIEW_HOLD','depends_on':['REI_PR261_RATE6_PORT','REI_PR248_ON_REFINED_SAVED','REI_EXTERNAL_MODEL_EVENT_TOPOLOGY'],'claim_gate':'different_author_R6_C9'},
 {'id':'FULL_CHEM_JY_ACTUAL','status':'INPUT_REQUIRED','depends_on':['SAVED17_UVB_JR','actual recombination/nuclear/CR and electron-feedback source','matching physical bath'],'claim_gate':'source_identity_full_Jy'},
 {'id':'CHEM_VARIATIONAL_SOLUTION','status':'INPUT_REQUIRED_NO_IVP_AUTH','depends_on':['FULL_CHEM_JY_ACTUAL','actual tangent IC','clock and nHref'],'claim_gate':'physical_D_a_y'},
 {'id':'TAU_PHYSICAL_RESPONSE','status':'BLOCKED','depends_on':['CHEM_VARIATIONAL_SOLUTION','BASS_PR234_tau_row','physical H,K and D_aH'],'claim_gate':'physical_D_a_tau'},
 {'id':'CMB_DIRECTIONAL_OBSERVABLE','status':'BLOCKED','depends_on':['TAU_PHYSICAL_RESPONSE','directional redshift/geodesic map','Thomson scattering frame'],'claim_gate':'observational_Bianchi_transfer'},
 {'id':'PHYSICAL_L4','status':'BLOCKED','depends_on':['CMB_DIRECTIONAL_OBSERVABLE','physical norm','source and clock error enclosures'],'claim_gate':'production'}],
 'no_ivp':True,'no_canonical_promotion':True}
save('NEXT_DAG_OVERLAY.json',overlay)
resource={'schema':'REI_UVB_SAVED17_SOURCE_TANGENT_RESOURCE_V1','date':'2026-10-29','new_ivp':0,'original_gls_replay':0,'old_17state_replay':0,'new_figures':0,'python_tests':15,'cpp_rows':7,'test_time_log':'results/TEST_TIME.txt','cpp_time_log':'results/CPP_TIME.txt','historical_main_budget':'CLOSED_NO_TRANSFER','historical_presentation_budget':'CLOSED_NO_TRANSFER','global_pass':False,'unmeasured_overhead':'UNKNOWN_NOT_ZERO','runtime_python':'PYTHON_PASS','runtime_cpp':'CPP_PASS','native_subagent':'NOT_EXPOSED'}
save('RESOURCE_AND_GATES.json',resource)
print('contracts built')
