"""Recompute the two qualified source tables from one central checkout."""
import json
from pathlib import Path
from rei_bianchi.microphysics import cr


def main():
    dest = Path(__file__).resolve().parent
    result = cr.axbi_source_experiment()
    (dest/'AXBI_PRIMARY_SOURCE.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    rows = [cr.integrate_phys02(population=name) for name in
            ('direct_0p1_10','direct_10_900','selected_total')]
    (dest/'PHYS02_REPRODUCTION.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
