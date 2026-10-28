"""Resolve the user-selected current case without importing or invoking a solver."""
import argparse
import json
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]


def resolve_case(requested_case=None):
    config=json.loads(Path(__file__).with_name('current_defaults.json').read_text())
    case=config['default_case'] if requested_case is None else requested_case
    if case not in config['allowed_cases']:raise ValueError('unknown explicit requested case')
    path=UNIT.parent/config['saved_case_unit']/'outputs'/(case+'.npz')
    return {'requested_case':requested_case,'resolved_case':case,
        'selection_reason':'USER_SELECTED_DEFAULT' if requested_case is None else 'EXPLICIT_REQUEST_OVERRIDE',
        'settings':config['case_settings'][case],'saved_case_path':str(path),
        'preserved_initial_profile':config['preserved_initial_profile'],
        'source_model_status':config['source_model_status'],'solver_invoked':False,
        'historical_results_mutated':False,'source_default_file':str(Path(__file__).with_name('current_defaults.json'))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=['OFF_base','ON_base','ON_refined'],default=None)
    args=parser.parse_args()
    print(json.dumps(resolve_case(args.case),indent=2))


if __name__=='__main__':main()
