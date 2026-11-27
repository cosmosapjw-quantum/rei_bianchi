#!/usr/bin/env python3
"""Read-only finite-grid comparisons; empirical differences stay uncertified."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from original_source import decode_output, sha, summarize, write_new

def refinement(prepared,coarse,fine_prepared,fine):
    a=summarize(prepared,coarse);b=summarize(fine_prepared,fine)
    ca=json.loads((Path(prepared)/'PREPARED.json').read_text())['binding']['request']
    cb=json.loads((Path(fine_prepared)/'PREPARED.json').read_text())['binding']['request']
    for key in ('B','k','E_Hartree','eta_C','outer','lmax','dps','phi','forcing','boundary','frozen_source_sha256','angular_rule','HH_R10'):
        if ca[key]!=cb[key]:raise ValueError('refinement physical request mismatch: '+key)
    u,v=decode_output(coarse),decode_output(fine)
    with np.load(Path(prepared)/'GRID.npz',allow_pickle=False) as ga,np.load(Path(fine_prepared)/'GRID.npz',allow_pickle=False) as gb:
        if len(gb['r'])!=2*len(ga['r'])-1 or not np.array_equal(ga['r'],gb['r'][::2]):
            raise ValueError('nested 2:1 radial grids required')
        diff=v[:,::2]-u
        weighted=float(np.sqrt(np.sum(ga['weights'][None,:]*np.abs(diff/ga['r'][None,:])**2)))
    denominator=max(float(np.max(np.abs(v))),np.finfo(float).tiny)
    return dict(schema='PHYS73_GREEN_REFINEMENT_V1',status='EMPIRICAL_NESTED_GRID_COMPARISON',
                certified=False,coarse=a,fine=b,
                max_relative_sample_difference=float(np.max(np.abs(diff)))/denominator,
                sample_Xminus_difference=weighted,
                angular_source_backend=ca['angular_rule'],
                comparison_role='radial_refinement_at_fixed_angular_projection',
                legacy_angular_node_labels=[ca['angular_nodes'],cb['angular_nodes']],
                continuum_quadrature_error_bound=None,
                comment='This difference is not a continuum residual or rigorous quadrature bound.',HH_R10='OFF')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared','coarse','fine-prepared','fine','out'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=refinement(a.prepared,a.coarse,a.fine_prepared,a.fine)
    write_new(a.out,r);print(json.dumps(r,indent=2,sort_keys=True))

if __name__=='__main__':main()
