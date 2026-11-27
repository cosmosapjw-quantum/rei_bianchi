"""Second algorithm using all vertices of row polytopes on an actual source sample."""
import argparse
import csv
import gzip
import itertools
import json
from fractions import Fraction
from pathlib import Path
from reduce_f05 import DATA, EV_ERG, E, H, HE
from rei_bianchi.microphysics.he import correlated_partition_bounds


def vertices(channels, emitted):
    pts = set(itertools.product(*channels))
    for free in range(3):
        fixed = [i for i in range(3) if i != free]
        for boundary in emitted:
            for a, b in itertools.product(channels[fixed[0]], channels[fixed[1]]):
                p = [0, 0, 0]; p[fixed[0]], p[fixed[1]], p[free] = a, b, boundary-a-b
                pts.add(tuple(p))
    return [p for p in pts if emitted[0] <= sum(p) <= emitted[1]
            and all(lo <= val <= hi for val, (lo, hi) in zip(p, channels))]


def run():
    indices = {0, 1, 46079, 46080, 92159} | set(range(43,92160,2587))
    found = []
    for i, row in enumerate(csv.DictReader(gzip.open(DATA, 'rt', newline=''))):
        if i not in indices: continue
        boxes = [tuple(Fraction(row[k+s]) for s in ('_lo','_hi')) for k in ('emitted','absorbed_H','absorbed_HeI','escaped')]
        points = vertices(boxes[1:], boxes[0]); assert points
        results = correlated_partition_bounds(*boxes)
        for key, func in (
            ('heat_erg', lambda h,he,s: EV_ERG*((E-H)*h+(E-HE)*he)),
            ('binding_erg', lambda h,he,s: EV_ERG*(H*h+HE*he)),
            ('escaped_erg', lambda h,he,s: EV_ERG*E*s),
            ('local_absorptions', lambda h,he,s: h+he)):
            values = [func(*p) for p in points]
            if (min(values),max(values)) != results[key]: raise ValueError((i,key))
        h_low,h_high=results['hydrogen_absorptions']; he_low,he_high=results['helium_absorptions']
        projected={(p[0],p[1]) for p in points}
        assert (h_low,he_high) in projected and (h_high,he_low) in projected
        found.append(i)
    if set(found) != indices: raise ValueError('missing selected rows')
    return {'status':'EXACT_AGREEMENT','method':'Enumerated box vertices and every intersection of an emission boundary with two coordinate faces. Checked four marginals and jointly attainable extreme H/He pairs using exact rationals.','selected_rows':len(found),'indices':found}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    p=parser.parse_args().output; p.write_text(json.dumps(run(),indent=2)+'\n')
