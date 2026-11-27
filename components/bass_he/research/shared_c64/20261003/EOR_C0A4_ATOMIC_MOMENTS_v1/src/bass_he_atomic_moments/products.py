"""Deterministic, source-bound native moment products with create-only storage."""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
import os
from pathlib import Path
from typing import Any
from bass_he_liu import load_dataset
from bass_he_liu.products import write_json_create_only
from .core import MODEL_ID, MomentProvider, coefficients, validate_provider


def load_at_root(root: str | Path):
    root=Path(root)
    binding=validate_provider(root/'raw',root/'provenance/provider_snapshot/ScienceDB_ldjson_0.json')
    data=load_dataset(root/'raw',root/'vendor/c0a3/provenance/INPUT_LOCK.json')
    return data,binding


def build_products(root: str | Path) -> dict[str,Any]:
    """All supplied resolved nodes. This export includes flagged outside-paper nodes."""
    data,binding=load_at_root(root)
    provider=MomentProvider(data,model_id=MODEL_ID,scope='payload_domain')
    ids=sorted(c for c in data.channels if not c.endswith(':total'))
    records=[provider.sample(c,s.energy_token) for c in ids for s in data.channels[c].samples]
    signs=Counter()
    for r in records:
        q=Fraction(r['moments']['internal']['exact_fraction'])
        signs['positive' if q>0 else 'negative' if q<0 else 'zero']+=1
    coefficients_out={c:{k:str(v) for k,v in coefficients(c,model_id=MODEL_ID).items()} for c in ids}
    native={'schema':'bass-he.c0a4.native-internal-moments.v1','energy_model_id':MODEL_ID,
            'channels':ids,'records':records,'sign_counts':dict(signs),
            'source_sigma_samples_modified':False,'data_kind':'EXACT_MODEL_WEIGHTED_SOURCE_TOKENS',
            'scope':'payload_domain; source bounds preserved; no extrapolation',
            'physical_certificate':False,'heat':None,'unweighted_total_samples_excluded':57}
    shells={c:[provider.sample(c,e) for e in data.available_energies(c)] for c in
            ('NR_CX:1s:n2','NR_CX:1s:n3','NR_CX:2s:n3','NR_CX:2s:n4')}
    examples=[]
    for process,initial in [('NR_CX','1s'),('NR_CX','2s'),('EXC','1s'),('EXC','2s')]:
        subset=[c for c in ids if c.startswith(f'{process}:{initial}:')]
        for theta in (10.,30.,100.):
            out=MomentProvider(data,model_id=MODEL_ID,method='linear_E').functional(
                subset,'25','196',theta_native=theta)
            out['diagnostic_only']=True;examples.append(out)
    return {'PROVIDER_BINDING.json':binding,'ENERGY_COEFFICIENTS.json':{
                'schema':'bass-he.c0a4.coefficients.v1','energy_model_id':MODEL_ID,
                'unit':'E_h','coefficients':coefficients_out,'not_source_finite_basis_energies':True},
            'RESOLVED_NATIVE_MOMENTS.json':native,
            'DERIVED_SUBSET_SHELL_MOMENTS.json':{'schema':'bass-he.c0a4.derived-shells.v1',
                'energy_model_id':MODEL_ID,'shells':shells,'physical_certificate':False},
            'FINITE_SUPPORT_DIAGNOSTICS.json':{'schema':'bass-he.c0a4.functional-diagnostics.v1',
                'cases':examples,'native_theta_not_gas_temperature':True,'physical_rates_computed':0}}


def write_products(root: str | Path, output: str | Path) -> list[str]:
    """Create one new directory; partial output on I/O failure is retained, never reused."""
    output=Path(output)
    if output.exists() or output.is_symlink():raise FileExistsError(str(output))
    products=build_products(root)  # Validate all inputs before creating output.
    output.mkdir(parents=False,exist_ok=False)
    names=[]
    for name,value in products.items():
        write_json_create_only(output/name,value);names.append(name)
    fd=os.open(output.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return names
