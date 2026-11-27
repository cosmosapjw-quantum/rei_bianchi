from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent
def put(p,d):
 q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
reads=[
 dict(repo='WU088_HH',pr=56,commit='ca616e02fcbd4330003346090beb6e6e88daa3ad',path='research/hh_phys23_20261013/results/EXPOSURE_CONE.json',read='GitHub fetch_file, relevant result fields; long remainder truncated',reuse='direct common PHYS22 majorant identity and exposure constants; local full PHYS23 data remains calculation input',limitations='Posted and local PHYS23 archives are distinct. No byte equivalence or supersession claimed. Rate prescription tables not combined.'),
 dict(repo='BASS_HE',pr=39,commit='d9cb8c3ec3524ebd7d5c8418f2fda5fd329ef62f',path='research/theory13_kinetic_error_bridge_20261013/THEORY13.md',git_blob='0144cd5a1001f7e4da10133c69e3b27529453df4',read='full compact proof through GitHub fetch_file',reuse='transform: positive endpoint Lipschitz cones, changed weight from affine abundance in time to Maxwellian energy kernel',limitations='THEORY13 D=1e-3 cm^-3,f=2/25,total time<=1e9 s differs from P01. Numeric KN/recoil/temporal radii not transported; external review pending remains.'),
 dict(repo='bass_cr',pr=51,commit='15193ccf88207de3a5134a4dc56c72e8ed1c7262',path='research/cr_time_donor_20261013/THEORY_AND_DELIVERY_KO.md',git_blob='5a6245e024d00c9acad8857d5578cb971d697238',read='full compact theory/delivery via GitHub fetch_file',reuse='structural: use the same event count for species, free charge and threshold energy; allocate positive residual contributions without replaying a cascade',limitations='Electron-donor HI/HeI model,99.6K and cold snapshot are not H-H ground-state data. No cross-section or numerical bound transplanted.'),
 dict(repo='rei_bianchi',pr=114,commit='a5c958c414dea41216b445c05f58df837f05cacb',read='live latest relevant PR metadata; frozen source/physical inputs inherited from local PHYS23/22 archive',reuse='direct existing warm P01 gas4/photon2904, source, frame, clock and closure',limitations='No new native build or HH activation.'),
 dict(repo='bass',pr=141,commit='d520c5e47ebf5cf218351082430ae3ef5e1ab3ec',read='live latest relevant PR metadata; receiver contract extract inherited from local PHYS23',reuse='direct beta0 sampled Thomson rate/cell definitions and fixed observable transfer',limitations='Numerical comparison tolerances are not physical omission budgets; original missing prelaunch executable-hash history retained.'),
 dict(repo='WU088_HH',commit='ca616e02fcbd4330003346090beb6e6e88daa3ad',path='research/r31ao_unequal_ladder/hh_atomic_reuse_plan_20261012_v2/contracts/HH_PROCESS_OWNER_ROWS.json',git_blob='f6842af243fd293ec37c3047d46bbfafa12359d8',read='full contract via GitHub fetch_file',reuse='channel mapping: LCS free-electron ionization versus singlet H+H- ion-pair',limitations='Microscopic ion-pair lane has electron yield0. It supplies no direct rate envelope for the free-electron channel.')]
for x in reads:
 x['url']='https://github.com/cosmosapjw-quantum/'+x['repo']+('/blob/'+x['commit']+'/'+x['path'] if 'path'in x else '/pull/'+str(x['pr']))
put('CROSS_REPO_REUSE.json',{'date':'2026-10-13','discovery':'latest updated relevant PR per repo at current read, plus exact connected files; no claim of exhaustive all-branch survey','reads':reads,'mutations':[],'common_majorant_sha256':'9b6b44acee637ac8adde1ca114e258c38747d48b3a750146614742786d8444ed','local_PHYS23_archive_sha256':'4bc8ad7392d0991435da78d35aff99b2d700bf6cfb1895466b7d06fcdebb09bd','posted_PHYS23_archive_sha256_from_PR':'2af6c191d0049a7ab57d09357beaffd9d8ef311da4f354d2c696b0b8aeaa6f2e'})
put('SOURCE_REGISTRY.json',{'date':'2026-10-13','discovery_tools':['SciSpace','Exa','web'],'sources':[
 {'id':'SHELDON1965','title':'Cross section for impact ionization of H(1s) atoms by H(1s) atoms near threshold','author':'J. W. Sheldon','report':'NASA-TN-D-3134','url':'https://ntrs.nasa.gov/citations/19660002855','pdf':'https://ntrs.nasa.gov/api/citations/19660002855/downloads/19660002855.pdf','access':'official record and parsed primary text; screenshot attempts failed','used':'same free-electron channel; Rosen sudden/classical approximation; singlet/triplet models; threshold to twice threshold domain','not_used':'graph-digitized values, unverified image formulas, or an H-H physical error factor. The cited factor-about-two comparison in the conclusion concerns He-He and Ar-Ar.'},
 {'id':'BARKLEM2007','title':'Non-LTE Balmer line formation in late-type spectra: Effects of atomic processes involving hydrogen atoms','url':'https://arxiv.org/abs/astro-ph/0702222','primary_pdf':'https://www.aanda.org/articles/aa/pdf/2007/16/aa6686-06.pdf','access':'Exa primary-content extraction and arXiv abstract; official PDF fetch/screenshot access incomplete','used':'lab/CM energy and threshold ambiguities in classical recipes; limits on near-threshold inference from high-energy comparisons'},
 {'id':'GLOVER2015','title':'Simulating the formation of massive seed black holes in the early Universe II: Impact of rate coefficient uncertainties','url':'https://arxiv.org/abs/1504.00514','section':'3.2.8','access':'parsed primary PDF and inherited PHYS23 evidence; screenshot unavailable','used':'context for cross-section extrapolation underlying rate prescriptions; no new fit coefficients imported'},
 {'id':'MCCLURE1968','title':'Ionization and Electron Transfer in Collisions of Two H Atoms:1.25-117keV','doi':'10.1103/PhysRev.166.22','url':'https://journals.aps.org/pr/abstract/10.1103/PhysRev.166.22','access':'primary publisher search result; later page fetch cache miss','used':'reported laboratory energy coverage only; 625eV CM is the calculated equal-mass lower-energy conversion'},
 {'id':'WOLFRAM_INTERVAL','url':'https://reference.wolfram.com/language/ref/Interval.html','access':'official documentation','used':'directed endpoint-rounding semantics'},
 {'id':'XACT','url':'https://xact.es/download/xAct_1.3.0.tgz','access':'downloaded and actually loaded in Wolfram','sha256':'7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be'}],
 'excluded_discovery_hits':['electron-impact hydrogen','proton-impact hydrogen','H2 molecular targets','H/Ar scattering','H+H- ion-pair results as direct free-electron events'],
 'physical_envelope_status':'No calibrated finite-bin uncertainty/slope/tail contract was recovered in the sources actually read. Candidate same-channel model retained for follow-up, not discarded.',
 'pdfs_redistributed':False})
put('NEXT_INPUT_CONTRACT.json',{
 'unit':'PHYS25_NEAR_THRESHOLD_CHANNEL_CALIBRATION',
 'channel':'H(1s)+H(1s)->H+ + H(1s)+e_free',
 'energy_frame':'CM relative kinetic energy, eV; lab adapter L=2E for equal masses',
 'cross_section_semantics':'total inclusive single-ionization event cross section, cm^2; one electron per event; network coefficient is half of event average',
 'spin':'unpolarized1/4 singlet+3/4 triplet only when the supplied spin-resolved cross sections include their spatial exchange treatment',
 'T_box_K':['49999.63846','50000.36154'],
 'requested_priority_support_CM_eV':['13.598434599702','27.196869199404'],
 'full_support':'threshold..infinity with explicit residual-tail envelope',
 'finite_bin_options':['pointwise lower/upper cross-section bounds','compatible exact endpoint values plus justified Lipschitz bounds on each connected support'],
 'physical_bin_values':None,'justified_slope_bounds':None,'tail_envelope':None,'physical_observable_budgets':None,
 'required_provenance':['input identity/version','reaction and event multiplicity','lab/CM mapping','spin and basis/channel identities','data/systematic/model error attribution','energy coverage','tail and threshold handling'],
 'stop_condition':'Evaluate positive bin envelope plus explicit tail; check common-tube validity and the supplied observable budget; refine only bins dominating the remaining width.',
 'preserved_independent_lanes':['HH_STRICT_NATIVE','HH_SINGLET','global RUX','BASS_HE kinetic closure','bass_cr nonthermal cascade']})
put('DECISION.json',{
 'unit':'PHYS24','decision':'promote_for_specified_use',
 'scope':'Maxwellian cross-section-to-rate map with explicit event/frame convention; sharp Lipschitz conditional envelopes; continuous warm-box bin weights; fixed-consumer budget map',
 'support':['derived','numerically-checked','symbolically-checked'],
 'physical_cross_section_coverage':'unresolved','scientific_omission_budget':None,
 'claims':[
 {'id':'C1','claim':'pair/CM normalization and temperature-uniform positive energy weights','decision':'adopt','evidence':['report §§2-3','wolfram/OBSERVED_RESULTS.json','results/KERNEL_BIN_TABLE.csv']},
 {'id':'C2','claim':'sharp envelope and nested refinement for compatible nonnegative Lipschitz cross sections','decision':'adopt under stated data/L assumptions','evidence':['report §4','checks/VALIDATION.json','wolfram/verify_endpoint_cones.wl']},
 {'id':'C3','claim':'near-threshold priority from uniform absolute cross-section-error weights','decision':'adopt for allocation, not a physical event fraction','evidence':['results/PHYS24_RESULT.json']},
 {'id':'C4','claim':'fixed P01 observable budget bound from per-bin upper envelopes','decision':'adopt if actual input envelope/tail and budget supplied','evidence':['report §7','predecessor23/WU088_HH_PHYS23_20261013/results/PHYS23_RESULT.json']},
 {'id':'C5','claim':'physical HH omission admissibility','decision':'hold','required':['calibrated cross-section/rate coverage','scientific observable allocation']}],
 'novelty':'specific cross-repo Maxwellian-weight extension and computed input-priority/budget coefficients; general positive integration or Lipschitz extension principle not claimed novel',
 'external_independent_review':False,'research_motivation':'turn existing rigorous response bounds into atomic-data accuracy requirements without replaying coupled histories',
 'no_new_ODE_or_native_or_scattering_runs':True,'remote_mutation':False})
put('RESEARCH_STATE.json',{'unit':'PHYS24','track':'theory','stages':[
 {'id':'R1','status':'completed','output':'same warm P01 cross-section-to-budget question and scope'},
 {'id':'R2','status':'completed','output':'local PHYS23 plus latest5repo references and primary same-channel benchmark'},
 {'id':'R3','status':'completed','output':'event/pair/spin/energy convention; local-versus-remote PHYS23 distinction'},
 {'id':'R4','status':'completed','output':'finite bins and endpoint-cone candidates; positive Maxwellian extension chosen'},
 {'id':'R5','status':'completed','output':'change-of-variable, positivity, sharpness, nestedness, tail and budget derivations'},
 {'id':'R6','status':'completed','output':'same-assistant alternate arithmetic and CAS; external independence not claimed'},
 {'id':'R7','status':'completed','output':'actual xAct/Wolfram and58+4 Python checks; continuous-T proof'},
 {'id':'R8','status':'completed','output':'specified-use adoption, unresolved physical inputs explicit in DECISION'},
 {'id':'R9','status':'completed','output':'report, executable verification and exact coefficient files'},
 {'id':'R10','status':'completed','output':'manifest-bound package and PHYS25 contract'}],
 'policy_adjustment':{'previous':'reduce next research to waiting for a calibrated physical rate table','observation':'HE endpoint-cone proof and inherited positive response coefficients support immediate useful weighted-bin calculations','action':'complete the conditional envelope/weight/budget calculation while preserving unfilled physical coverage fields','physical_assumptions_changed':False},
 'next':'PHYS25_NEAR_THRESHOLD_CHANNEL_CALIBRATION','publication':'local artifacts only'})
put('FAILURE_LEDGER.json',{'entries':[
 {'kind':'runtime_environment','operation':'container HTTP downloads','evidence':'checks/acquisition.json','effect':'no local raw copy of live remote files obtained by container; source content read through GitHub/Exa/web instead','resolved_for_current_science':True},
 {'kind':'runtime_environment','operation':'web PDF screenshots','sources':['NASA Sheldon','Glover','official Barklem access'],'effect':'use parsed prose only; no plot digitization or image-dependent formula adoption','resolved_for_claimed_source_scope':True}],
 'scientific_test_failures':0,'first_Wolfram_status':'PASS','second_Wolfram_status':'PASS'})
print('Records written')
