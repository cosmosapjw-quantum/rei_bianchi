"""Small synthetic files; never an actual FULL005 physical-admission fixture."""
import csv
import hashlib
import json
from pathlib import Path
import sys

UNIT = Path(__file__).resolve().parents[1]
BASE = UNIT.parent / 'flrw_full005_postprocess_20261015'
sys.path.insert(0, str(BASE / 'vendor'))
sys.path.insert(0, str(UNIT))
import compare_histories as reader
import analyze_saved_pair as analyzer


def case(xs, ys, name='case', field='x_HII'):
    return {'id': name, 'series': {'L': list(xs), field: list(ys)}}


def write_csv(path, columns, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def descriptor(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def saved_fixture(root):
    """Receipt-shaped synthetic input testing the loader contract only."""
    root = Path(root)
    runs, bindings = root / 'runs', root / 'bindings'
    bindings.mkdir()
    prior = dict(status=analyzer.PRIOR_STATUS, input_kind='SYNTHETIC_ONLY_NOT_FULL005_ADMISSION',
                 pair_source_relation='BYTE_IDENTICAL_COMPILED_SOURCE',
                 validated_complete_inputs=[], case_checks={}, frozen_full005_checks={})
    for number in (512, 1024):
        ident = 'SYNTHETIC_Q' + str(number)
        directory = runs / ident
        directory.mkdir(parents=True)
        spec = {'id': ident, 'clock_origin': reader.CLOCK}
        history = []
        for i, a in enumerate((reader.A0, (reader.A0 * reader.A1)**0.5, reader.A1)):
            x = (0.1, 0.5, 0.9)[i]
            history.append(dict(case_id=ident, a=a, time_s=i*50,
                nH_proper_cm3=1, ne_proper_cm3=x, x_HI=1-x, x_HII=x,
                x_HeI=1, x_HeII=0, x_HeIII=0, temperature_K=10+i+(number==1024),
                J0_photon_u_eV_per_H=0, J2_photon_u_eV_per_H=0))
        write_csv(directory/'history.csv', list(history[0]), history)
        abundances=[]
        for i, x in enumerate((0.1, 0.5, 0.9)):
            for species, value in [('H_I',1-x),('H_II',x),('He_I',0.1),
                                   ('He_II',0),('He_III',0),('electron',x)]:
                abundances.append(dict(run_id=ident,time_s=i*50,species_id=species,Ybaryon=value/1.4))
        write_csv(directory/'abundances.csv',list(abundances[0]),abundances)
        (directory/'config.cfg').write_text('end_zbar=4\nq_ref=0\ntransport_cells='+str(number)+'\n')
        (directory/'source_identity.txt').write_text('SYNTHETIC_ONLY_NOT_FULL005_ADMISSION\n')
        (directory/'RETURN.txt').write_text('status=COMPLETE_REPRESENTED_INTERVAL\na=0.2\naccepted=2\n')
        for role, filename in [('history','history.csv'),('abundances','abundances.csv'),
            ('config','config.cfg'),('source_identity','source_identity.txt'),('terminal','RETURN.txt')]:
            spec[role]=descriptor(directory/filename)
        binding = bindings/(ident+'.binding.json')
        binding.write_text(json.dumps(dict(case=ident,source_identity_sha256=spec['source_identity']['sha256'],
                                          runtime_config_sha256=spec['config']['sha256'])))
        spec['binding']=descriptor(binding)
        spec['expected_source_sha256']=spec['source_identity']['sha256']
        spec['expected_config_sha256']=spec['config']['sha256']
        # Deliberately absent files prove these roles are never opened.
        for role in ('ledger','checkpoint'):
            spec[role]={'path':str(directory/('MUST_NOT_OPEN_'+role)), 'sha256':'0'*64}
        prior['validated_complete_inputs'].append(spec)
        prior['case_checks'][ident]=dict(status=analyzer.STRICT_STATUS,history_rows=3,elapsed_time_s=100,
            source_identity_sha256=spec['source_identity']['sha256'],
            config_sha256=spec['config']['sha256'],binding_sha256=spec['binding']['sha256'])
        prior['frozen_full005_checks'][ident]={'status':analyzer.FROZEN_STATUS}
    path=root/'synthetic_prior.json'
    path.write_text(json.dumps(prior,indent=2)+'\n')
    return path,prior,runs,bindings
