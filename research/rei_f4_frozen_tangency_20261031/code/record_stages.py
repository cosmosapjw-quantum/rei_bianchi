from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
phases={
 'R1':('scope','Frozen-trajectory source tangency and chemical energy port; no IVP'),
 'R2':('primary-source','Read original BASS193/REI hybrid source at immutable PR298 raw SHA; Grackle 2017 and Norman 2015 referenced'),
 'R3':('preconditions','Separate derivative-free Delta F and finite-grid D_tY; fixed H,T,n_b,UV, clock'),
 'R4':('alternatives','Compare BASS native F vs REI HHe replacement; enumerate dynamic re-evolution as forbidden'),
 'R5':('derivation','Derive necessary Delta F=0 for same Y(t); chemical binding energy source and temperature compensation as counterfactual'),
 'R6':('same-author-review','Physical checks/boundaries; true distinct author NOT_RUN'),
 'R7':('calculator','193x21 exact source mismatches and six physical plots generated'),
 'R8':('science-judgment','Frozen BASS path incompatible with substituted vector field at 193 sampled states; no general nonexistence theorem'),
 'R9':('computational-form','Explicit units eV erg cm^-3, x=ln(a/a_ini), dt/dx=1/H, charge and heat capacity'),
 'R10':('handoff','Original source ZIP plus final source/prerequisite identity and next actions preserved'),
 'C1':('contract','193 original states, no source/IC/IVP mutation'),
 'C2':('mapping','PR298 21x21 F/J, q,A,Y with source x,z/t, thermal CV'),
 'C3':('algorithm','Direct Delta F, 3-point sampled derivative only auxiliary, Simpson exposure diagnostic'),
 'C4':('execution','One bounded process and one self review; standalone source-contained archive'),
 'C5':('implementation','Portable Python source + 193-row CSV, arrays NPZ and six plots'),
 'C6':('tests','18 targeted source/charge/energy/counterfactual tests'),
 'C7':('physics-check','Baryon, electron, He branching and energy stoichiometry'),
 'C8':('accuracy','Derivative-free source mismatch primary; 3-point D_tY has finite-grid error, midpoint-clock difference reported'),
 'C9':('same-author-review','Physical hostile audit done; true blind distinct-author NOT_RUN'),
 'C10':('publish-boundary','One auxiliary science node, canonical unchanged; draft PR and cloud restore receipts after publication')}
for k,(phase,content) in phases.items():
    d=dict(schema='REI_F4_ONE_BOUNDED_SOURCE_PHASE_V1',stage=k,phase=phase,content=content,
      source_PR=298,source_sha256='012635501cc5d9717ae775e9482b351b239003aa6c7db4dd2035ffa4760b7f2d',
      working_DAG='33/88',central_DAG='28/88',physical_fast_DAG='4/7',canonical_delta=0,
      evidence='ONE_SOURCE_193_EPOCH_CALCULATION;RETROSPECTIVE_PHASE_RECORD',
      subagent='NOT_RUN',distinct_author_R6_C9='NOT_RUN',new_ivp=0,merge=False,production='HOLD')
    (ROOT/'stages'/f'{k}.json').write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print('STAGE_RECORDS=20; R6/C9 independent NOT_RUN; source nodes=33/88 28/88 4/7')
