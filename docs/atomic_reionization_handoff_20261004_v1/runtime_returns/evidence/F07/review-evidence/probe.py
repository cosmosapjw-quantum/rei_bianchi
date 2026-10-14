import copy, hashlib, json, math, pathlib, runpy, subprocess, sys
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2]); sys.dont_write_bytecode=True
scenario=root/'configs/rei_fastest_v1/science_scenario_v1.json'
schema=root/'configs/rei_fastest_v1/science_scenario_v1.schema.json'
validator=root/'docs/atomic_reionization_handoff_20261004_v1/tools/verify_science_scenario.py'
config=json.loads(scenario.read_text()); spec=json.loads(schema.read_text())
identity={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in json.loads((root/'.cuh/fastest-track/REI-F07/review-scope.json').read_text())['files']}
api_files=['rust/rei_microphysics/src/atomic_provider.rs','rust/rei_microphysics/src/ft03_rates.rs','rust/rei_microphysics/src/hhe_events.rs','rust/rei_microphysics/src/angular_photons.rs']
identity.update({name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in api_files})
(out/'source-identities.json').write_text(json.dumps(identity,indent=2)+'\n')
argv=[sys.executable,'-B',str(validator),'--scenario',str(scenario),'--schema',str(schema),'--output',str(out/'screening.json')]
(out/'validator.argv.json').write_text(json.dumps(argv,indent=2)+'\n')
p=subprocess.run(argv,cwd=root,text=True,capture_output=True)
(out/'validator.stdout').write_text(p.stdout); (out/'validator.stderr').write_text(p.stderr)
print('CANONICAL_VALIDATOR_EXIT',p.returncode)
print('CANONICAL_SCREEN_BYTES_EQUAL', (out/'screening.json').read_bytes()==(root/'.cuh/fastest-track/REI-F07/screening.json').read_bytes())
module=runpy.run_path(str(validator),run_name='review_probe')
mutations={
 'quadrature_zero': [(('spectral','angular_quadrature','n_mu'),[0,8,16])],
 'negative_kB': [(('constants','k_B_erg_K'),-1.380649e-16)],
 'outside_real_ft03_guard': [(('atomic_model','fit_implementation_temperature_guard_K'),[1000.,200000.]),(('atomic_model','scenario_temperature_guard_K'),[1000.,160000.]),(('initial_state','temperature_K'),120000.)],
 'source_below_actual_verner_cutoff': [(('source','energy_at_birth_ev'),13.599),(('initial_state','photon_energy_ev'),13.599)]
}
for name,changes in mutations.items():
 candidate=copy.deepcopy(config)
 for keys,value in changes:
  d=candidate
  for k in keys[:-1]: d=d[k]
  d[keys[-1]]=value
 (out/(name+'.scenario.json')).write_text(json.dumps(candidate,indent=2)+'\n')
 try:
  module['validate'](candidate,spec); result=module['screen'](candidate)
  print('MUTATION',name,'ACCEPTED',result['status'],'thermal',result['initial_thermal_erg_cm3'])
 except Exception as e:
  result={'exception':type(e).__name__,'message':str(e)}
  print('MUTATION',name,'REJECTED',result)
 (out/(name+'.result.json')).write_text(json.dumps(result,indent=2)+'\n')
# Independent binary64 screening arithmetic and explicit packet normalizations.
H=1e-14; t=1e13; E=13.7; nH=1e-4; fhe=.083; kb=1.380649e-16
ne=nH*.9+nH*fhe*(.3+2*.6)
print('INDEPENDENT_EOS',json.dumps({'ne':ne,'u':1.5*kb*50000*(nH+nH*fhe+ne)}))
print('INDEPENDENT_NUMBER',json.dumps({'integrated_source_per_H':5e-15*t,'initial_ref_cm3':nH*.05,'injected_ref_cm3':nH*5e-15*t,'initial_cohort_proper_cm3_end':nH*.05/math.exp(3*H*t)}))
for label,hmax in [('FLRW',H),('BIANCHI_I',1.01*H)]:
 tb=math.log(E/13.5984346)/hmax; tv=math.log(E/13.60)/hmax
 print('INDEPENDENT_GEOMETRY',json.dumps({'pair':label,'volume_end':math.exp(3*H*t),'nH_end':nH/math.exp(3*H*t),'oldest_Emin':E*math.exp(-hmax*t),'candidate_binding_cross_s':tb,'actual_verner_cutoff_cross_s':tv,'difference_s':tb-tv,'relative_time_difference':(tb-tv)/tb}))
for nmu,nphi in zip(config['spectral']['angular_quadrature']['n_mu'],config['spectral']['angular_quadrature']['n_phi']):
 w=(2/nmu)*(2*math.pi/nphi)/(4*math.pi)
 print('QUADRATURE',json.dumps({'nmu':nmu,'nphi':nphi,'positive_weight':w>0,'weight':w,'sum':math.fsum([w]*(nmu*nphi))}))
# Compile only the exact existing two self-contained provider modules in a temp harness.
rs='#[derive(Debug)] pub enum ForwardError { InvalidInput(&\'static str) }\n'
rs+='#[path = '+json.dumps(str(root/'rust/rei_microphysics/src/atomic_provider.rs'))+'] mod atomic_provider;\n'
rs+='#[path = '+json.dumps(str(root/'rust/rei_microphysics/src/ft03_rates.rs'))+'] mod ft03_rates;\n'
rs+='fn main() { let p=atomic_provider::AtomicProvider::reference(); for e in [13.5984346,13.599,13.6,13.7] { println!("HI_CROSS_SECTION e={} sigma={:?}",e,p.cross_section(atomic_provider::Absorber::HI,e)); } for t in [50000.0,120000.0] { println!("FT03_RATE t={} result={:?}",t,ft03_rates::ft03_coefficients(t)); } }\n'
(out/'provider_probe.rs').write_text(rs)
cmd=['rustc','--edition=2021','-A','dead_code',str(out/'provider_probe.rs'),'-o',str(out/'provider_probe')]
(out/'rustc.argv.json').write_text(json.dumps(cmd,indent=2)+'\n')
r=subprocess.run(cmd,cwd=root,text=True,capture_output=True)
(out/'rustc.stdout').write_text(r.stdout); (out/'rustc.stderr').write_text(r.stderr)
print('RUSTC_EXIT',r.returncode)
if r.returncode==0:
 cmd=[str(out/'provider_probe')]; (out/'provider.argv.json').write_text(json.dumps(cmd)+'\n')
 r=subprocess.run(cmd,cwd=root,text=True,capture_output=True)
 (out/'provider.stdout').write_text(r.stdout); (out/'provider.stderr').write_text(r.stderr)
 print('PROVIDER_EXIT',r.returncode); print(r.stdout,end='')
else: print(r.stderr)
