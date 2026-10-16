#!/usr/bin/env python3
"""Construct the additive REI development SSOT from explicitly checked source records.
Does not mutate historical project state or scientific acceptance thresholds.
"""
from pathlib import Path
import json, csv, hashlib, datetime
ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'contracts'; D=ROOT/'docs'
C.mkdir(exist_ok=True); D.mkdir(exist_ok=True)
STAMP='2026-10-16'; repo='cosmosapjw-quantum/rei_bianchi'

def jwrite(name,obj):
    (C/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=False)+'\n',encoding='utf-8')

def source(id,kind,url,rev,scope,state='source_verified_metadata',reuse='conditional'):
    return dict(id=id,kind=kind,url=url,revision=rev,scope=scope,evidence_status=state,reuse_policy=reuse)

sources=[
source('S00_USER_ADDENDUM','attached_snapshot','inputs/user_additional_dag_20261016.txt','sha256_filled_in_manifest','2026-10-16 user 6-track planning draft: 21 enumerated nodes, historical values unverified','user_supplied','reconcile'),
source('S01_REI_MAIN','github_branch','https://github.com/'+repo+'/tree/main','ae3402713c4b6530ab2b27f008f5f5d5c6a999ed','Historical durable compact main; NOT current native owner','verified_head','historical'),
source('S02_REI_PR150','github_pr','https://github.com/'+repo+'/pull/150','da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7','Owner FLRW native production, frozen driver/input per experiment; SOURCE005/010/012, typed failures','verified_pr_head','direct_conditional'),
source('S03_REI_FROZEN_OWNER','github_commit','https://github.com/'+repo+'/commit/6ea2b1b4b3875c9163cafc45efe720afded43fc4','6ea2b1b4b3875c9163cafc45efe720afded43fc4','PR174 exact frozen native Rust owner for comparisons, not necessarily current PR150 HEAD','reported_in_pr174','exact_for_v11'),
source('S04_REI_PR171','github_pr','https://github.com/'+repo+'/pull/171','c07ba9b839aa003a7b9afb3c6be9adce24761eeb','Source-age native positive reference: age/transport HOLD','verified_pr_lineage','scoped'),
source('S05_REI_PR173','github_pr','https://github.com/'+repo+'/pull/173','e7296e0647d711d7c49ebfd757fb3b68da430e9f','Positive optical-coordinate oracle, prescribed opacity; 21/21 scoped tests and split quadrature','verified_pr_head','conditional'),
source('S06_REI_PR174','github_pr','https://github.com/'+repo+'/pull/174','70ad2b58840cc6041152011028d67af14c30bca8','V11 source-free clock/midpoint 41 tests and 144-row experiment; Rust V11 native NOT_RUN','verified_pr_head','conditional'),
source('S07_REI_PR104','github_pr','https://github.com/'+repo+'/pull/104','f66929c23ea3fa6e39dd4808e5b27d136c568a03','Reduced z20->4+ fixed-temperature H/He singly ionized volume history, 14 cases','verified_pr_metadata','scoped'),
source('S08_REI_PR137','github_pr','https://github.com/'+repo+'/pull/137','203fdf1d4deff0f981dc75b2100adf16da94a153','Unpolarized gamma/neutrino Einstein-Boltzmann coupling, NOT complete polarized hierarchy','verified_pr_metadata','conditional'),
source('S09_REI_PR151','github_pr','https://github.com/'+repo+'/pull/151','58af6385197ad93cc940b4a1755cbcd4db5398ed','Independent R9 microphysical trace Li/Be conditional bridging','verified_pr_metadata','conditional'),
source('S10_REI_DOSSIER_20261014','dropbox_pdf','/BASS_DERIVATION_DOSSIERS_20260912/Reionization_Standalone_Dossier.pdf','dropbox_rev:65dc5d675f45d0af03d47;bytes:967541','Dossier chapter 1 17-state nuclear/charge; positive opacity moments; covariant tau; chapter2 energy ledger. Source text read via connector','parsed_text_reviewed_no_byte_SHA','direct_theory'),
source('S11_REI_CURRENT_PLAN','github_file','https://github.com/'+repo+'/blob/da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7/docs/fastest_track_chat/CURRENT_PLAN.json','gitblob:5dde7195706efa013dca3cc85c957d6a3783dbb7','AXBI original goal and overlays, inherited not overwritten','exact_blob_sha','plan_map'),
source('S12_REI_PRODUCTION_DAG','github_file','https://github.com/'+repo+'/blob/da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7/research/flrw_production_integration_20261015/NEXT_DAG.json','gitblob:4df1197c6b133614e08419a67120f2d42a85600e','Current production transport dependency and typed HOLD','exact_blob_sha','plan_map'),
source('S13_GRACKLE','primary_code','https://github.com/grackle-project/grackle','github_project_unpinned','H/He non-equilibrium primordial chemistry source; explicit PR174 Grackle3.4.1 source commit af7939494ce65007887ada7b98d1813df6843346','official_project_checked','external_reference'),
source('S14_VERNER1996','primary_atomic_data','https://www.pa.uky.edu/~verner/photo.html','1996,doi:10.1086/177435','Ground-state photoionization fit and thresholds, not excited-state or complete Case-A cascades','primary_source_checked','external_reference'),
source('S15_MACKEY2012','primary_paper','https://arxiv.org/abs/1201.5651','2012,A&A:539:A147','Photon-conserving RT time-centering and multifrequency accuracy limits','primary_source_checked','external_reference'),
source('S16_HYREC2','primary_code','https://github.com/nanoomlee/HYREC-2','2020,doi:10.1103/PhysRevD.102.083517','Primordial recombination donor only, NOT reionization rate replacement','primary_source_checked','external_reference'),
source('S17_REI_LEGACY_CORE','restored_sandbox','/mnt/data/rei_chat_ssot_20261016','sha256_per-file_not_rebound','Previous turn local snapshots of ray oracle, optical age, V11 and Rust reference; not a production native checkout','runtime_accessible','use_small_references')
]
jwrite('SOURCE_REGISTRY.json',dict(schema='rei.ssot.source.registry.v2',as_of=STAMP,sources=sources))

conventions={
'schema':'rei.ssot.physics.v2','date':STAMP,
'geometry':{'metric_signature':'(-,+,+,+)','epsilon123':'+1','metric':'ds²=-c²dt²+sum_i a_i(t)²(dx^i)² for diagonal BI','mean_scale':'a=(a1 a2 a3)^(1/3)','LRS_scale_factors':'(a*exp(-b),a*exp(-b),a*exp(2b))','LRS_Hubble':'(H-s,H-s,H+2s) where s=db/dt', 'shear_scalar':'sigma_abs=sqrt(sigma_ab sigma^ab/2) = sqrt(3)*abs(s)', 'Sigma':'sigma_abs/H when H>0; otherwise retain sigma_abs and H separately','legacy_r':'r=s/H and Sigma=sqrt(3)*abs(r) in adopted convention','orientation':'sign(s) separately from Sigma','free_decay':'s ∝ a^(-3) only when shear propagation sources absent'},
'normalization':{'total_H_nuclei':'n_H includes hydrogen isotopes only if explicitly stated; D counted separately under elemental-nuclei mode','baryon_count':'sum_A A*n_A, unambiguously count each isotope exactly once','helium_per_total_H':'y_He=n_He/n_H; He charge states relative to total n_He or total n_H must specify denominator','ionized_volume_Q':'Q_HII != local x_HII or n_e/n_H unless closure given','n_e_rest':'electron rest-frame proper number density; do not apply Lorentz gamma twice','n_e_normal':'normal-frame density; requires explicit frame map'},
'constants':{'c':'299792458 m/s','hbar':'1.054571817e-34 J s','k_B':'1.380649e-23 J/K','sigma_T':'6.6524587321e-29 m² (reference, bound to input source in production)','eV_to_J':'1.602176634e-19 J'},
'energy':{'ray_energy':'E=-p_a n^a c for normal observer','BI_conserved':'spatial covariant p_i=a_i E e_i/c','ray_map':'E1/E0=sqrt(sum_i[e0_i*a_i0/a_i1]^2)','solid_angle_J':'(prod_i a_i0/a_i1)/(E1/E0)^3 for n0->n1','opacity_hazard':'kappa=c*sum_a n_a^proper*sigma_a[E(t)] in s^-1','source_age':'integral over birth-time with cohort-dependent E/direction and kappa','no_clipping':True,'no_extrapolation':True,'case_a_case_b':'exclusive operator branches; CaseA transported escape must not double count OTS CaseB'},
'observer':{'d_tau_nontilted':'c*sigma_T*n_e^rest dt normal ray proper time','d_tau_tilted':'c*sigma_T*n_e^rest*gamma*(1-beta.e) dt for future-directed ray and normal time','tau_tail':'unknown tail -> total tau and total visibility return null','redshift_surface':'event time t*(direction,geometry) solves observed redshift; do not replace with fixed coordinate time'},
'applicability':{'current_physical_baseline':'non-tilted LRS Bianchi-I / matched FLRW','counterfactual_shear':'|s/H| around 1e-3..1e-1 must explicitly label COUNTERFACTUAL when applied to CMB constrained free-decay mode','11_Bianchi':'future family-specific registry; not admitted','finite_tilt':'separate conditional extension; no inferred solver from BI diagonal rays'}
}
jwrite('PHYSICS_CONVENTIONS.json',conventions)

species=[('n',1,0,'neutron','nuclear'),('H0',1,0,'H','atomic'),('H+',1,1,'H','atomic'),('D0',2,0,'D','atomic'),('D+',2,1,'D','atomic'),('T0',3,0,'T','atomic'),('T+',3,1,'T','atomic'),('He3_0',3,0,'He3','atomic'),('He3_1',3,1,'He3','atomic'),('He3_2',3,2,'He3','atomic'),('He4_0',4,0,'He4','atomic'),('He4_1',4,1,'He4','atomic'),('He4_2',4,2,'He4','atomic'),('Li7_0',7,0,'Li7','atomic'),('Li7_1',7,1,'Li7','atomic'),('Li7_2',7,2,'Li7','atomic'),('Li7_3',7,3,'Li7','atomic')]
species_data=[dict(id=x,baryon_number=A,charge=q,nuclear_isotope=iso,sector=sec,physical_species_type='number_density',unit='m^-3',rest_frame='common-rest-frame',authority='dossier_v20261014_ch1_eq_1_15') for x,A,q,iso,sec in species]
jwrite('STATE_VARIABLES.json',{'schema':'rei.ssot.state.v2','dossier_17':species_data,'extension_requires_source':{'Li6':'separate conditional 6Li q=0..3 pending original rate-source/check','Be7':'independent nuclear daughter/EC donor; not silently in 17 state vector','nonthermal_e':'separate distribution f_e(p,x), not n_e duplicate','photons':'positive cohort measure per H or comoving packet; never untyped counts'},'required_dynamical_state':['a_i','H_i','proper_time_s','gas_temperature_K','species_number_density_m3','free_electron_density_rest_m3','radiation_number_per_H_or_comoving','radiation_energy_J','event_ledger','energy_ledger'],'enforce_isotope_mass_baryon_number':True,'charge_invariant':'sum charge*ions - n_e + positrons = fixed as set by initial conditions and sources'})

owner_matrix=[
{'process':'photoionization_HI_HeI_HeII','owner':'rei radiation absorption transaction','upstream':'Verner1996 source or pinned native equivalent','exclusive_with':['separate unowned photon sink'],'requires':['photon_birth_id','spectral_energy','absorber_id','binding_chi','heat_excess','electron_created']},
{'process':'recombination_caseA','owner':'Grackle Case-A gas event + transported escaped photons','upstream':'Grackle3.4.1+BASS_HE when source-bound','exclusive_with':['caseB_OTS_same_event'],'requires':['cooling_internal_energy_convention','escape_photon','species_transition']},
{'process':'recombination_caseB','owner':'OTS local effective solver branch','upstream':'explicit Case-B table','exclusive_with':['caseA_explicit_recombination_escape_same_event'],'requires':['on_the_spot_assumption','frequency_bin_limitations']},
{'process':'impact_ionization','owner':'Grackle CI or opt-in CR primary model','upstream':'Grackle/bass_cr','exclusive_with':['duplicated source term event'],'requires':['threshold_energy','recoil_gas','ionization_species']},
{'process':'thermal_energy','owner':'one shared gas energy equation','upstream':'igm_thermal.rs','exclusive_with':['separate untracked thermal drift'],'requires':['d_n_tot_dt','adiabatic_expansion','photoheat','CE','FF','CMB','reaction_binding']},
{'process':'CMB_Compton','owner':'single gas-CMB transaction','upstream':'Grackle or validated equivalent','exclusive_with':['second CMB exchange in other lane'],'requires':['electron_density','radiation_temperature','signed_gas_and_CMB_reservoir']},
{'process':'H_D_charge_exchange','owner':'AtomicRhs XOR ThermalSubstep','upstream':'deuterium_thermal_coupling.rs','exclusive_with':['AtomicRhs_and_ThermalSubstep_both'],'requires':['spectator_EOS','H_D_isotope_census','fixed_volume_vs_cosmo_expansion']},
{'process':'optical_depth','owner':'bass observer consumer','upstream':'actual REI n_e rest-current output','exclusive_with':['Q_as_independent_electron_multiplier'],'requires':['proper_time','electron_frame','ray_tetrad','observer_endpoint','tail_state']},
{'process':'primordial_IC','owner':'rec_bianchi donor','upstream':'pinned rec_bianchi revision','exclusive_with':['HyRec_as_postz20_reionization_solver'],'requires':['cosmology','Tgas','He_normalization','initial_time','composition_mass']},
{'process':'BASS_gamma_nu_Thomson','owner':'BASS I/E/B/V or scoped unpolarized hierarchy','upstream':'BASS current code','exclusive_with':['Thomson_scattering_on_neutrinos'],'requires':['ne_true','sigmaT','nu_collisionless','screen_basis_for_polarized']}
]
jwrite('PROCESS_OWNER_REGISTRY.json',dict(schema='rei.ssot.owners.v2',owners=owner_matrix))

# The user paste identifies 21 nodes despite calling it 18: 2+6+3+3+3+4=21.
N=[]
def node(id,track,depends,goal,inputs,output,physics_gate,numeric_gate,resources='sandbox',status='PLANNED',claim='NOT_ADMITTED',refs=None,next_action=None,notes=None):
 inputs = [inputs] if isinstance(inputs,str) else inputs
 output = [output] if isinstance(output,str) else output
 physics_gate = [physics_gate] if isinstance(physics_gate,str) else physics_gate
 N.append(dict(id=id,track=track,depends_on=depends,goal=goal,inputs=inputs,outputs=output,physics_acceptance=physics_gate,numerical_acceptance=numeric_gate,execution_budget=resources,status=status,scientific_claim=claim,source_refs=refs or [],on_pass=next_action or [],important_notes=notes or []))
node('DOSSIER-V2','0',[],'Reformulate research dossier into source-to-code SSOT and executable smoke','S00 user draft, S10 source dossier, S02 S04 S05 S06 S11 S12', ['Dossier MD/PDF','contracts JSON/JSON Schema','Rust positive source-age smoke','checked source identities'],['metadata crosswalk 17-state baseline and physical conventions; owner matrix','do not override existing plan; do not promote conditional results'],'JSON DAG acyclic, 21 source-proposal IDs preserved, rust test offline, repeatable outputs',resources='sandbox 1 build job/<=1.5GiB/<=120s per command',status='COMPLETE_SCOPED_DOC_REFERENCE_TESTED',refs=['S00_USER_ADDENDUM','S10_REI_DOSSIER_20261014','S11_REI_CURRENT_PLAN'],next_action=['SYNC-01','FT-B1A'])
node('SYNC-01','0',['DOSSIER-V2'],'Read actual branch tip and merge/rebase design without mutating active PR150/owners','S01,S02,S11,owner AGENTS/CLAUDE',[ 'explicit source commit matrix','semantic port ledger','non-destructive branch strategy'],['preserve dirty and untracked, only author task-specific new branch','source clock/rates/domain identities before any transplant'],'tiny scoped build/test; no full historical replays',status='READY_SANDBOX',refs=['S01_REI_MAIN','S02_REI_PR150','S11_REI_CURRENT_PLAN'],next_action=['RT-R9_R10','SA-03','ISO-EOS','LRS-V11'])
node('SYNC-02','0',['SYNC-01'],'Preserve native source-age task owner and old expired resource envelope; establish sandbox-only scope','PR171/PR166 owner blobs, source identities',['task-owned job reservation','physical input lock','NCP no-call policy'],['no production checkpoint mutation and no unapproved capacity','compare frozen source/clock identically'],'scoped pilot only within real sandbox ceiling',status='HOLD_NATIVE_CAMPAIGN',refs=['S04_REI_PR171','S02_REI_PR150'],next_action=['SA-01','SA-02','OBS-O5'],notes=['Existing 2026-10-16 02:50:17Z external campaign deadline remains expired; this thread does not use NCP'])
node('RT-R9_R10','B',['SYNC-01'],'Consolidate source-locked interpolation and isotope rate R9/R10 theory receipts','R1-R8 rate-table and Grackle source','single rate contract version with domain and exact breakpoints',['original source branch piecewise/caps/floors recorded','Li6/Li7 elemental electronic equality CONDITIONAL only'],'verify all source table identifiers, no extrapolation',status='READY_SANDBOX',refs=['S02_REI_PR150','S13_GRACKLE'],next_action=['RT-C1_C3'])
node('RT-C1_C3','B',['RT-R9_R10'],'Implement 65537 logT SoA table with direct native branch fallbacks','igm_rates.rs actual SOURCE and test vectors','Rust opt-in table module + branch detector + tests',['source-domain fail closed; structural zeros exact','maximum relative rate error <=1e-5 on admitted smooth spans; no rounding of branch transitions'],'sandbox <=2GiB RAM, <=2 jobs, short batch',status='READY_SANDBOX',refs=['S13_GRACKLE','S02_REI_PR150'],next_action=['RT-C4_C5'])
node('RT-C4_C5','B',['RT-C1_C3'],'PreparedDirectRates at exact bitwise T and optional Li6/Li7 charge RHS','temperature identities + Voronov/Badnell pinned records','typed direct/table adapter and Li conditional provider',['no chemical source interpolation across discontinuity; nuclear-charge conservation','bitwise equality in identical direct path, LTE error scoped, no unknown Li isotope-specific rates'],'sandbox <=2GiB',status='READY_AFTER_RATE_SOURCE',refs=['S13_GRACKLE','S09_REI_PR151'],next_action=['RT-C6_C7'])
node('RT-C6_C7','B',['RT-C4_C5'],'Targeted rate and isotope invariant tests','rate fixtures, domain branch temperatures','Rust deterministic tests and evidence','nuclear/baryon/electron and atomic energy invariants; no clipping','rate <=1e-5, input identity exact, signed error class instead of retune','sandbox <=1GiB',status='PENDING',next_action=['RT-C8'])
node('RT-C8','B',['RT-C6_C7'],'Benchmark direct/prepared/table scalar and 4-worker only at matched accuracy','same 421431-T query source pool or bounded subset with source identity','CSV timings/cost break-even and memory','all methods identical scientific integrands where admitted','warmup/setup+B and query costs c, matched-error speedup only, no fabrication','sandbox bounded; 1-2 threads default, 4 only measured',status='PENDING',next_action=['RT-C9_C10'])
node('RT-C9_C10','B',['RT-C8'],'Review and publish opt-in rate implementation','changed files, scoped validation','atomic dataset release and exact replay manifest',['independent scientific claim gate remains separate from timing'], 'one fresh review pass, no full historical test campaign','sandbox',status='PENDING',next_action=['ISO-COUPLE'])
node('SA-01','A',['SYNC-02'],'Refine native birth age 32→64 and time grid independently, preserve known failures','PR171 source/case fixed MD14 BB50k/Grackle','survivor N/U and species event convergence matrix',['same source histories/clock/geometry; no source replacement'], 'age N/U and local native time isolated; 90.13% observed old discrepancy not a tolerance','sandbox only small replays; heavy full campaign DEFER',status='HOLD_NATIVE_SOURCE_INTAKE',refs=['S04_REI_PR171','S05_REI_PR173'],next_action=['FLRW-CONV'])
node('SA-02','A',['SYNC-02'],'Refine HeI spectral64→128→256 at fixed other axes','PR171 qref+0.1 age8/angular8/source sub8','integrated HeI events, Gamma and moment rate ledger',['threshold-aware Verner spectra, no unclaimed exact continuum error'], 'frozen adjacent integrated HeI relative target <0.5%, more than one pair to establish convergence','sandbox limited 1 case; full production HOLD',status='HOLD_NATIVE_SOURCE_INTAKE',refs=['S04_REI_PR171','S14_VERNER1996'],next_action=['FLRW-CONV'])
node('SA-03','A',['SYNC-01'],'Fix qminus endpoint serialization without recomputing full native history','SOURCE012 qminus saved endpoint, actual source schema','q0,qplus,qminus consistent output fields with null for absent','do not invent proper_time/T/Gamma/heat missing sources','exact restored data identity and serialization roundtrip','sandbox',status='READY_SANDBOX',next_action=['BI-SIGNED'])
node('OBS-O5','C',['SYNC-02'],'Collect opt-in accepted-step (R,J) packets only in new bounded run','owner observer default off','<=6 packets, <=48 new RHS attempts with status labels',['observer disabled leaves physics unchanged'], 'full/half branch tags, accepted/rejected labels exact, Newton residual norm<=1e-11','fresh sandbox pilot only; NCP historical cutoff excluded',status='HOLD_NEW_PHYSICAL_RUN',next_action=['OBS-O6'])
node('OBS-O6','C',['OBS-O5'],'Analyze -J^-1 R and EOS sensitivity from actual accepted steps','O5 saved Newton packets','conditioned local correction and scalar diagnostic',['no treating linear correction as certified nonlinear state error'], 'condition number, residual reconstruction, added work accounting','sandbox Python/Rust tiny algebra',status='HOLD_INPUT_PACKET',next_action=['FLRW-CONV'])
node('LRS-V11','C',['SYNC-01'],'Use 41-test source-free midpoint / 144-case matrix, run only changed Rust native clock seam','PR174 donor, frozen owner 6ea2b1','per-process clock matrix and runtime ledger',['photons+stellar OFF, CI/CE/FF/CMB/RR/DR ON; no false source-on parity'], 'baseline vs CE-only vs full midpoint; smooth nonstiff p~2 only after Rust tests','sandbox opt-in mini, no full 144 re-sweep',status='READY_SCOPED_RUST_CLOCK',refs=['S06_REI_PR174','S03_REI_FROZEN_OWNER'],next_action=['FLRW-CONV'])
node('FLRW-CONV','D',['SA-01','SA-02'],'Close full-source-on time/age/transport/spectrum and angular accuracy for z20->4 without replaying original full campaigns','FULL005 Q512/Q1024 saved histories, SA01 SA02 proofs','budgeted matched-state convergence/false-HeII closures',['positive, species and photon/energy conservation incl source birth'], 'separate time, angle, transport spectral and age axes; no error inference from one pair','deferred if insufficient sandbox memory/runtime',status='HOLD_CONVERGENCE_NOT_ADMITTED',refs=['S02_REI_PR150'],next_action=['BI-SIGNED'],notes=['Existing FULL005 itself is retained; closure requires new evidence, not automatic whole-history rerun'])
node('BI-SIGNED','D',['FLRW-CONV','SA-03'],'Run four signed BI cases and matched isotropized Hubble control, output abundance histories','q_ref compatibility plus actual Sigma map; same IC and source','paired BI/isoHB/FLRW x_i(t), T(t), source and shear curves',['Sigma(s) definition declared; shear bound conditional; all large shear labeled COUNTERFACTUAL'], 'sigma->0 FLRW, E_num(deltaO)<=0.1 A_target when target above floating floor','full campaign future, tiny manufactured tests now',status='HOLD_FULL_CONV',refs=['S07_REI_PR104','S08_REI_PR137'],next_action=['BASS-TAU','ISO-COUPLE'])
node('BASS-TAU','D',['BI-SIGNED'],'Integrate true electron-current tau and finite-bin visibility with observer/redshift surfaces','matched n_e^rest(t) from BI and FLRW','partial tau/DeltaTau/bin-masses and 5-way error ledger',['signed photon direction, matter clock, tilt only with frame-preserving true current'], 'unknown tails => null global tau/P; do not call reduced Q whole tau','sandbox bounded numerical integration when data present',status='HOLD_NATIVE_ELECTRON_HISTORY',next_action=['REL-GATE'])
node('ISO-EOS','E',['SYNC-01'],'Derive full network including He spectator heat capacity and D/T/3He/6,7Li mass census','dossier eq 1.15 & 2.60-2.66, owner thermal-CX','typed EOS and reaction stoichiometric matrix spec',['A-weighted baryon sum and q electron, one free-electron/FF/CMB owner'], 'single fixed-volume pure H/D previous PASS not extended to expanding gas','sandbox algebra/small tests',status='READY_SANDBOX',refs=['S10_REI_DOSSIER_20261014'],next_action=['ISO-COUPLE'])
node('ISO-COUPLE','E',['RT-C9_C10','ISO-EOS','BI-SIGNED'],'Opt-in D/H plus spectators and common-owner photon/gas transactions','D isotope rates + rates prepared, source-locked Bianchi backgrounds','source-linked Rust added full-network lane',['CX AtomicRhs XOR substep, one photo absorber, one CMB+FF+electron owner'], 'proven matched source domain, chemistry/timestep convergence and no bound-width deterioration','sandbox targeted, full cosmos deferred',status='HOLD_DEPS',next_action=['ISO-RUN'])
node('ISO-RUN','E',['ISO-COUPLE'],'Compute multi-isotope charge/thermal histories with trace validity','same backgrounds/SHA and trace initial abundances','D/H and optional Li6/7 curves vs time/T with error budget',['no undocumented isotope-specific rate equality as physical claim'], 'source/age/time refinement and conserved totals','full campaign deferred',status='HOLD_DEPS',next_action=['REL-GATE'])
node('REL-GATE','E',['BASS-TAU','ISO-RUN'],'Release per-claim scoped output and reproducible research package','all reports, input hashes and actual acceptance','DAG status/versioned package','false PASS protection; per-claim admission, not one global blanket','all mandatory scientific gates explicit, backup restore check','sandbox metadata then science by scoped validator',status='HOLD_DEPENDENCIES',next_action=[])
# Fast track independent lines, don't subordinate scientific output to full source-on convergence
node('FT-B1A','FAST',['SYNC-01'],'Use saved PR104 reduced history as prescribed donor for collisionless BI directional I_E(mu), q and tau record','PR104 donor and BI geometry, possible stored curves','finite directional intensity, signed quadrupole; same-H isotropic comparator',['collisionless does not depend on n_e; present separate tau not Thomson action'], 'Killing energy/angle map and interpolation, scan angular/spectral without full EoR','sandbox <=1GiB, Rust or Python oracle',status='READY_AFTER_SAVED_PR104_FILE',refs=['S07_REI_PR104'],next_action=['FT-B1B','FT-C'])
node('FT-B1B','FAST',['FT-B1A'],'Opt-in unpolarized Thomson collision and finite test E2 if screen basis provided','BASS Thomson kernel + true prescribed ne','I_l evolution, integrated tau and optional Stokes diagnostic',['photon Thomson vs collisionless neutrinos, gain/loss balance, no fake polarization'], 'zero ne, isotropic, quadrupole damping, temporal and angular convergence','sandbox small l<=8',status='PENDING_INPUT',refs=['S08_REI_PR137'],next_action=['FT-ID'])
node('FT-C','FAST',['FT-B1A','ISO-EOS'],'Introduce minimal physical UV photoionization+heat feedback only when spectral source pinned','Verner HI/He, single owner state','one-way vs two-way Q/heat/tau (finite interval)','photoheating requires energy-weighted actual UV, cannot use CMB intensity for HI ionization','ionization+energy conservation and no double recomb','sandbox toy then physical only with source',status='PENDING_SOURCE',refs=['S14_VERNER1996'],next_action=['FT-ID'])
node('FT-ID','FAST',['FT-B1B'],'Compare directional response vs nuisance and scalar Sigma degeneracy, no unconditional detection claim','paired intensity/collisional tau and uncertainty source','finite-resolution identifiability proxy, conditional no-go if proved',['observer map, fixed cosmology and valid shear class'], 'Jacobian singular-value/error ratio and finite counterexamples','sandbox small SVD, observational data optional',status='PENDING',next_action=['REL-GATE'])
# 21 user-listed nodes + DOSSIER and 4 FAST = 26
jwrite('RESEARCH_DAG.json',dict(schema='rei.ssot.dag.v2',date=STAMP,repo=repo,scope='sandbox-first additive SSOT; frozen original plans/PR not mutated',source_proposal_enumerated_nodes=21,source_proposal_header_claim=18,source_proposal_inconsistency='21 actual nodes (2+6+3+3+3+4), not 18; preserve all IDs',added_nodes=['DOSSIER-V2','FT-B1A','FT-B1B','FT-C','FT-ID'],statuses_are_planning_not_new_scientific_pass=True,nodes=N))

# Schema (small strict required-fields rather than a redundant security system)
json_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:rei:ssot:dag:v2','type':'object','required':['schema','date','nodes','source_proposal_enumerated_nodes'],'properties':{'schema':{'const':'rei.ssot.dag.v2'},'date':{'type':'string'},'source_proposal_enumerated_nodes':{'const':21},'nodes':{'type':'array','minItems':21,'items':{'type':'object','required':['id','depends_on','goal','inputs','outputs','physics_acceptance','numerical_acceptance','status','scientific_claim','on_pass','execution_budget'],'properties':{'id':{'type':'string','minLength':2},'depends_on':{'type':'array','items':{'type':'string'},'uniqueItems':True},'goal':{'type':'string','minLength':5},'status':{'type':'string'},'scientific_claim':{'type':'string'}},'additionalProperties':True}}},'additionalProperties':True}
jwrite('SCHEMAS.dag.schema.json',json_schema)

code_map=[
['BI-KILLING','Bianchi directional E(t), e_i(t)','rust/rei_microphysics/src/bianchi_i.rs','CharacteristicRay::pullback, GeometrySnapshot','SIGMA and redshift math','FT-B1A,BI-SIGNED'],
['GAS-RHS','H/He proper chemistry+thermal','rust/rei_microphysics/src/igm_rates.rs; igm_thermal.rs; igm_state.rs','IgmGasState, igm_point_rhs','CaseA vs B, native T clock','LRS-V11,RT-C1_C3'],
['PHOTON-OWNER','single photon sink and event','rust/rei_microphysics/src/axbi_covariant_transport.rs; axbi_driver.rs','fixed q packets; event receipts','born photon clock, false HeII, thresholds','SA-01,SA-02,FLRW-CONV'],
['SOURCE-AGE','positive source-cohort Duhamel','research/rei_optical_age_20261016; research/rei_positive_age_reference_20261016','event-split positive quadrature','source age vs transport vs time','SA-01,SA-02'],
['D-ISOTOPE','pure H/D thermal charge exchange','rust/rei_microphysics/src/deuterium_thermal_charge_exchange.rs; deuterium_thermal_coupling.rs','ThermalCxComponent','spectator EOS and CX XOR','ISO-EOS,ISO-COUPLE'],
['OBS-TAU','electron current optical depth','external BASS consumer + REI saved electron traces','n_e frame, fixed observed-redshift surface','tail unknown and event tangent','BASS-TAU,FT-B1B'],
['REC-IC','primordial chemistry donor','external/rec_bianchi.lock.json','initial abundances and proper time','H/He baseline and locked cosmology','SYNC-01,FLRW-CONV']]
with (C/'CODE_MAP.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['physics_ID','equation_or_state','owner_path','implementation_symbols','verification_convention','dag_nodes']);w.writerows(code_map)

claim=[
{'id':'FLRW_FULL005','evidence':'PR150 reports Q512/Q1024 z20->4 completed', 'admission':'historical_execution_only','open':'full time/angle/spectrum convergence'},
{'id':'LRS_V11_SOURCE_OFF','evidence':'PR174 41 Python tests and 144-row matrix; previous fresh rerun', 'admission':'conditional_smooth_source_free','open':'actual Rust clock causal isolation and source-on p2'},
{'id':'OPTICAL_AGE_SMOOTH','evidence':'PR173 21 Python tests and analytic z-space', 'admission':'prescribed_piecewise_opacity_only','open':'native nonlinear feedback and exact source clock'},
{'id':'SA_NATIVE_AGE','evidence':'PR171 16->32 survivor relative 90.13% difference', 'admission':'hold','open':'cohort ages and native time refinement'},
{'id':'SA_NATIVE_HEI','evidence':'PR171 transport32->64 accumulated HeI event relative 0.7497%', 'admission':'hold','open':'<0.5% target with additional independent grid'},
{'id':'REDUCED_BROAD_HISTORY','evidence':'PR104 source-bound reduced 14 scenarios','admission':'promote_scoped_reduced_only','open':'full H/He thermal native, isotopic EoR, total tau'},
{'id':'BI_OBSERVATIONAL_SHEAR','evidence':'Dossier weak-anisotropy map and conditional CMB quadrupole free-decay estimate','admission':'conditional_geometry_result','open':'self-consistent observational fit and modern model constraints'},
{'id':'D_H_THERMAL_CX','evidence':'PR150 source current pure H/D fixed proper-volume finite kernel','admission':'scoped_fixed_volume_only','open':'expanded EOS spectators / full cosmological heat flow'},
{'id':'R9_LI_BE','evidence':'PR151 unit7 conditional source models','admission':'scoped_studies','open':'thermal deposition and full ionizing illumination'},
{'id':'DOSSIER_V2','evidence':'This turn source synthesis, schemas and Rust smoke test','admission':'scoped_dev_ssot_tested_not_production','open':'downstream native physics'}]
jwrite('CLAIM_MATRIX.json',{'schema':'rei.ssot.claim.v2','claims':claim})

budget={'schema':'rei.ssot.budget.v2','environment':'ChatGPT sandbox only, no local Codex, no external NCP','rust':{'toolchain':'1.94.1 from user tarball, prefix /mnt/data/rust-1.94.1-prefix; verify each new session','jobs_default':1,'max_jobs_while_observed_rss_low':2,'cargo_flags':['--offline','--locked'],'build_target':'source slice and tests; never full campaign by default'},'tiers':{'T0':{'wall_seconds':30,'ram_mib':256,'examples':'JSON validation / analytic tests'},'T1':{'wall_seconds':120,'ram_mib':1024,'examples':'isolated Rust test small 1-thread'},'T2':{'wall_seconds':180,'ram_mib':2048,'examples':'bounded Rust module + adaptive small case; preflight memory first'},'T3':{'wall_seconds':'not allocated in sandbox','ram_mib':'not allocated','examples':'full z20->4, 144-case retest, 65537 dense optional memory if costs unknown'}},'checkpoint':'save after each bounded science/code unit and before long builds','never':'run any NCP/local host, overwrite owner checkpoint or silently merge'}
jwrite('RESOURCE_BUDGET.json',budget)

observable={'schema':'rei.ssot.observables.v2','contracts':[
{'name':'abundance_by_time','fields':['proper_time_s','redshift_label','T_gas_K','x_HII','x_HeII','x_HeIII','x_DII_optional','source_identity','approximation'],'invariant':'each charge-state between 0 and isotope total and all nuclei conserved','status':'requires_native_history'},
{'name':'source_age_heI','fields':['age_bin','transport_bin','Gamma_HeI_s^-1','cumulative_HeI_events_per_H','survivor_number_per_H','energy_per_H_J'],'error_axes':['birth_age','transport_spectral','native_time','source_substep'],'admission':'adjacent integrated event relative <0.005 AND additional evidence for continuum'},
{'name':'tau_partial','fields':['t_start_s','t_end_s','tau_partial','tail_status','rest_frame','observer_direction','source_revision'],'tail_rule':'if missing tail, total_tau=null','status':'consumer_contract'},
{'name':'directional_intensity','fields':['proper_time_s','energy_eV','mu','I_E','I20_over_I00','isotropized_H_control','shear_convention'],'admission':'collisionless diagnostic cannot be claimed Thomson response'},
{'name':'signed_shear_response','fields':['r=s/H','Sigma=sqrt3abs(r)','orientation_sign','physical_or_counterfactual','deltaO_geometric','deltaO_isotropic_history','noise_floor'],'admission':'conditional CMB constraint and signal/non-signal separate'},
{'name':'ledger','fields':['B_photon','A_HI','A_HeI','A_HeII','A_D_optional','survivor_N','E_photon','E_binding','E_thermal','E_escape','E_CMB','E_work'],'admission':'single event / source energy and no double counting; diagnostic residual not temporal order'}]}
jwrite('OBSERVABLE_CONTRACTS.json',observable)

jwrite('BACKUP_AND_PUBLICATION.json',{'schema':'rei.ssot.backup.v2','cadence':'Each requested conversation turn: finish bounded work -> local hashes -> create-only Library and Google Drive backup -> separate GitHub additive branch/PR publication -> Dropbox if connector accepts generated conversation file -> remote metadata/readback','locations':{'library':'/REI_DOSSIER_SSOT_20261016/','drive':'/Google Drive/rei_bianchi_research_backups/ (create-only)','github':'cosmosapjw-quantum/rei_bianchi research/rei-dossier-ssot-sandbox-v2-20261016 (add-only)','dropbox':'/bianchi/research_backups/rei_bianchi/ (only if fileParam accepts generated package)'},'reproduction_levels':['LOCAL_SHA_VERIFIED','PROVIDER_ACK','PROVIDER_SIZE_ID_VERIFIED','FULL_BYTE_RESTORED_AND_SHA_VERIFIED','SCIENTIFIC_TEST_VERIFIED'],'fallback':'Never claim Dropbox or restore success without matched tool receipt','mutation_scope':'No PR merges, no modification of existing default branch/historical receipt, only additive project-owned docs and standalone source until owner integration'} )

# JSONL task card format
with (C/'TASK_CARDS.jsonl').open('w',encoding='utf-8') as f:
 for x in N:
  card={'id':x['id'],'prerequisite_ids':x['depends_on'],'task_type':x['track'],'science_goal':x['goal'],'inputs':x['inputs'],'outputs':x['outputs'],'acceptance':{'physics':x['physics_acceptance'],'numerical':x['numerical_acceptance']},'run_budget':x['execution_budget'],'source_refs':x['source_refs'],'fail_closed_if':'source identity, units, no-clipping, owner transaction or result claim mismatch','pass_to':x['on_pass'],'state':x['status']}
  f.write(json.dumps(card,ensure_ascii=False)+'\n')

# concise machine-readable policy of known older DAG ID transports
jwrite('DAG_CROSSWALK.json',{
'schema':'rei.ssot.crosswalk.v2','mapping_requires_readback':True,
'original_plan':{'commit':'da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7','path':'docs/fastest_track_chat/CURRENT_PLAN.json','original_next':'AX01','original_goal':'non-tilted axisymmetric BI abundance/time/temperature'},
'links':[
{'source':'FT-B1A','parent_lane':'2026-10-12 SCIENTIFIC_FAST_TRACK_RESET B1A','relation':'read_only_donor; optical collisionless diagnostics'},
{'source':'FT-B1B','parent_lane':'BASS_TAU; BASS hierarchy I/E/B/V','relation':'conditional_collision_operator; no E/B without screen'},
{'source':'FLRW-CONV','parent_lane':'PR150 FULL005 + NEXT_DAG COVARIANT_NATIVE_TRANSPORT','relation':'depends on scoped native error requalification'},
{'source':'SA-01','parent_lane':'PR173 SOURCE_AGE_SURVIVOR_NATIVE_AGE32_64_AND_TIME_REFINE','relation':'same native endpoint/source identity'},
{'source':'SA-02','parent_lane':'PR173 SOURCE_AGE_HEI_NATIVE_SPECTRAL64_128_256','relation':'native transport spectral only, not source age'},
{'source':'LRS-V11','parent_lane':'PR174 sourcefree all-midpoint Python','relation':'independent oracle; code changes require Rust new run'},
{'source':'ISO-COUPLE','parent_lane':'PR150 pure H/D thermal CX','relation':'extension must fix EOS and owner double count'},
{'source':'BASS-TAU','parent_lane':'RUX10/11 finite electron current/observer','relation':'partial tau only without tail'}],
'conflicts':[{'source':'SOURCE 18-node claim','resolution':'21 actual enumerated IDs retained'},{'source':'Sigma notation mixed between projects','resolution':'canonical Sigma=sqrt(sigma_ab*sigma^ab/2)/H=sqrt3|s|/H; r=s/H separate'},{'source':'2026-10-16 archive campaign allocation expired','resolution':'old deadline remains expired; sandbox T0-T2 only'},{'source':'PR150 current vs frozen owner SHA','resolution':'current PR150 HEAD != frozen PR174 source; no transplantation without diff/review'}]})

# Generate DAG mermaid and summary table from SSOT
lines=['flowchart TD']
for x in N:
 lines.append(f'  {x["id"].replace("-","_")}["{x["id"]}"]')
 for dep in x['depends_on']:
  lines.append(f'  {dep.replace("-","_")} --> {x["id"].replace("-","_")}')
(D/'DAG.mmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(D/'DAG_NODE_GUIDE_KO.md').write_text('# 상세 실행 노드 사양 (JSON에서 생성)\n\n'+ '\n\n'.join(f'''## {n['id']} | {n['track']} | {n['status']}

**목표:** {n['goal']}

**선행:** {', '.join(n['depends_on']) or '없음'}

**입력:** {n['inputs']}

**출력:** {', '.join(n['outputs'])}

**물리적 수용조건:** {', '.join(n['physics_acceptance'])}

**수치/구현 수용조건:** {n['numerical_acceptance']}

**자원:** {n['execution_budget']}

**근거:** {', '.join(n['source_refs']) or '선행 DAG 링크'}

**PASS 다음 단계:** {', '.join(n['on_pass']) or '해당 단계 종료'}

**현재 주장:** {n['scientific_claim']}.
''' for n in N)+'\n',encoding='utf-8')

print('generated',len(N),'DAG nodes:',len(list(C.glob('*.json'))),'JSON files')