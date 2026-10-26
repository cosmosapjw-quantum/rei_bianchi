"""One combined child; no old-source scan, integration, IVP or rate fit."""
import json
import os
from pathlib import Path
import traceback

from test_beta_transfer import run_tests as beta_checks
from test_species_projection import run_tests as species_checks
from test_stopping_components import run_tests as stopping_checks

HERE=Path(__file__).resolve().parent;UNIT=HERE.parent


def main():
    output=Path(os.environ['BLOCKER_OUTPUT_DIR']);checks=[];lanes={}
    def write(name,value):(output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    def checkpoint(label):
        write('checks_partial.json',checks);write('lanes_partial.json',lanes);print(label,flush=True)
    try:
        beta=beta_checks();checks.extend(dict(lane='beta',**row) for row in beta)
        lanes['beta']={'checks':len(beta),'empirical_rate_admission':False,'thermal_heat':None,
                       'branch':'declared_continuum_beta','source_or_rate_network_activation':False}
        checkpoint('beta_complete')
        species,projection=species_checks(UNIT/'species')
        checks.extend(dict(lane='species',**row) for row in species)
        write('SPECIES_PROJECTION.json',projection)
        lanes['species']={'checks':len(species),'historical_material_identities':len(projection['historical21']),
          'unadmitted_extensions':len(projection['extensions']),'atomic_targets':len(projection['atomic_targets']),
          'full_differential_provider_admission':False,'automatic_normalization_conversion':False}
        checkpoint('species_complete')
        stopping,components=stopping_checks(UNIT/'stopping/IMPLEMENTATION_CONTRACT.json')
        checks.extend(dict(lane='stopping',**row) for row in stopping)
        write('STOPPING_COMPONENTS.json',components)
        lanes['stopping']={'checks':len(stopping),'thermal_heat':None,'old_network_activation':False,
                          'full_stopping':'PARTIAL_INPUT_DEPENDENCIES'}
        checkpoint('stopping_complete')
        results={'checks':checks,'pass_count':sum(r['pass'] for r in checks),'total':len(checks),
          'passed':all(r['pass'] for r in checks),'lanes':lanes,'new_IVPs':0,'source_atom_scans':0,
          'integrations':0,'scientific_dependencies':'Python standard library only'}
        write('TEST_RESULTS.json',results)
        return 0 if results['passed'] else 1
    except BaseException as exc:
        write('FAILURE.json',{'class':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        checkpoint('exception');raise


if __name__=='__main__':raise SystemExit(main())
