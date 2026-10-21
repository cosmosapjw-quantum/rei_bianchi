"""Exact stored-term source-jump report, with explicit per-birth coverage."""
from fractions import Fraction
from pathlib import Path
import argparse

from run_refinement import read_json, save


def exact(value):
    return Fraction.from_float(float(value))


def rational(value):
    return dict(numerator=str(value.numerator),denominator=str(value.denominator),float=float(value))


def diagnose_jumps(setup, payload):
    inventory=setup['source_inventory']
    records=payload.get('records',[])
    missing=[];duplicate=[];invalid=[];results=[]
    for event,source in enumerate(inventory):
        candidates=[record for record in records if record.get('event')==event]
        if not candidates:
            missing.append(event);continue
        if len(candidates)!=1:
            duplicate.append(dict(event=event,count=len(candidates)));continue
        record=candidates[0]
        if (record.get('status')!='AVAILABLE' or record.get('active_before')!=event
                or record.get('active_after')!=event+1 or record.get('source_inventory')!=source):
            invalid.append(dict(event=event,reason='STATUS_ACTIVE_OR_INVENTORY_MISMATCH'));continue
        if 'x' not in record or record['x']!=setup['births'][event]:
            invalid.append(dict(event=event,reason='BIRTH_CLOCK_MISMATCH'));continue
        try:
            pre,post=record['pre'],record['post']
            if len(pre['ledgers'])!=14 or len(post['ledgers'])!=14:
                raise ValueError('LEDGER_SHAPE')
            delta_n=exact(post['N'])-exact(pre['N'])
            delta_photo=sum((exact(post['ledgers'][i])-exact(pre['ledgers'][i]) for i in range(4,7)),Fraction())
            delta=delta_n+delta_photo-exact(source[0])
            results.append(dict(event=event,x=record['x'],active_before=event,active_after=event+1,
                                delta_N=rational(delta_n),delta_photo=rational(delta_photo),
                                delta_photon_invariant=rational(delta),exact_invariant_unchanged=delta==0,
                                unchanged_nonbirth_coordinates_bits=record.get('unchanged_nonbirth_coordinates_bits'),
                                unchanged_gas_coordinate_bits=record.get('unchanged_gas_coordinate_bits'),
                                unchanged_ledger_coordinate_bits=record.get('unchanged_ledger_coordinate_bits')))
        except (KeyError,ValueError,OverflowError,TypeError) as error:
            invalid.append(dict(event=event,reason=repr(error)))
    unexpected=[record.get('event') for record in records
                if not isinstance(record.get('event'),int) or record['event']<0 or record['event']>=len(inventory)]
    return dict(schema='rei.source_jump.exact_diagnosis.v1',
                coverage='COMPLETE' if not (missing or duplicate or invalid or unexpected) else 'INCOMPLETE',
                expected_births=len(inventory),available_unique_births=len(results),missing_events=missing,
                duplicate_events=duplicate,invalid_events=invalid,unexpected_events=unexpected,records=results,
                scope='Exact arithmetic on stored binary64 terms; no automatic accuracy gate or simulation roundoff certificate.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    path=args.data/'source_jumps.json'
    payload=read_json(path) if path.is_file() else dict(records=[])
    save(args.out,diagnose_jumps(read_json(args.data/'setup.json'),payload))


if __name__ == '__main__':
    main()
