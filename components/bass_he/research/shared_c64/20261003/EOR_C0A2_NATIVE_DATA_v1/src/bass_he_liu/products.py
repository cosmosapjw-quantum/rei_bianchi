"""Traceable data products and audits. No approximation to missing source data."""
from __future__ import annotations
import csv
import io
import json
import os
import tempfile
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any, Sequence
from .native import Dataset, SourceUnavailable


def _write_create_only(path: str | Path, payload: bytes) -> None:
    """Durably create a new file. Never replace an existing path, even in a race."""
    path=Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError('OUTPUT_PARENT_MISSING')
    fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(payload);f.flush();os.fsync(f.fileno())
        os.link(temp,path)  # Atomic create; existing regular files/symlinks cause failure.
        dir_fd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dir_fd)
        finally:os.close(dir_fd)
    finally:
        os.unlink(temp)


def write_json_create_only(path: str | Path, value: Any) -> None:
    payload=(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf-8')
    _write_create_only(path,payload)


def write_long_csv_create_only(path: str | Path, dataset: Dataset) -> None:
    stream=io.StringIO(newline='')
    columns=['channel_id','energy_token','sigma_token','energy_header','sigma_unit_self_declared',
             'sigma_unit_contextual','outside_paper_stated_range','source_name','source_sha256',
             'source_line','energy_column','value_column']
    writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n');writer.writeheader()
    hashes={t.name:t.sha256 for t in dataset.tables}
    for cid,c in sorted(dataset.channels.items()):
        for s in c.samples:
            writer.writerow({'channel_id':cid,'energy_token':s.energy_token,'sigma_token':s.value_token,
                'energy_header':'keV/u','sigma_unit_self_declared':'','sigma_unit_contextual':'cm^2 (PDF contextual)',
                'outside_paper_stated_range':str(not Decimal(1)<=s.energy<=Decimal(200)).lower(),
                'source_name':c.source_name,'source_sha256':hashes[c.source_name],
                'source_line':s.source_line,'energy_column':s.energy_column,'value_column':s.value_column})
    _write_create_only(path,stream.getvalue().encode('utf-8'))


def audit(dataset: Dataset, catalog: Sequence[dict[str,Any]]) -> dict[str,Any]:
    tables=[]; native_values=0;missing=0;above=0;padding_pairs=0
    for t in dataset.tables:
        values=sum(len(c.samples) for c in t.channels)
        blanks=sum(len(c.missing) for c in t.channels)
        outside=sum(s.energy>Decimal(200) for c in t.channels for s in c.samples)
        padding_pairs+=sum(len(c.padding_lines) for c in t.channels)
        native_values+=values;missing+=blanks;above+=outside
        tables.append({'name':t.name,'sha256':t.sha256,'bytes':t.bytes,'data_rows':len(t.rows),
            'channels':len(t.channels),'values':values,'explicit_missing_values':blanks,
            'outside_paper_upper_values':outside,'utf8_bom':t.bom_utf8,
            'native_unit_header':'keV/u','sigma_unit_header':None,
            'channels_detail':[{'id':c.id,'values':len(c.samples),
                'native_energy_tokens':[s.energy_token for s in c.samples],
                'min_native':str(min(s.energy for s in c.samples)),
                'max_native':str(max(s.energy for s in c.samples)),
                'max_within_paper':str(max(s.energy for s in c.samples if s.energy<=200)),
                'explicit_missing_at':[m.energy_token for m in c.missing],
                'padding_lines':list(c.padding_lines)} for c in t.channels]})
    coverage=[];counts={'DIRECT_NATIVE':0,'DERIVED_EXACT_SUM':0,'NOT_SUPPLIED':0}
    for meta in catalog:
        cid=meta['id']
        if cid in dataset.channels:
            status='DIRECT_NATIVE';members=(cid,)
        else:
            try:members=dataset.members(cid);status='DERIVED_EXACT_SUM'
            except SourceUnavailable:members=();status='NOT_SUPPLIED'
        counts[status]+=1
        energies=dataset.available_energies(cid) if members else ()
        coverage.append({'id':cid,'status':status,'figure':meta.get('figure'),
            'resolution':meta.get('resolution'),'final_center':meta.get('final_center'),
            'samples':len(energies),'native_energy_tokens':[str(e) for e in energies],
            'members':list(members),'complete_inclusive_bound_sum':False,
            'source_paper_average':'Eq9 (B1+B2+B3)/3; individual CSVs have no basis/average label',
            'error_bars':None,'physical_certificate':False})
    disagreements=[]
    for t in dataset.tables:
        if t.name=='H1s-Capture cross sections.csv':
            for line,r in enumerate(t.rows,2):
                if r[2] and Decimal(r[0])!=Decimal(r[2]):
                    disagreements.append({'source_line':line,'total_axis':r[0],'capture_1s_axis':r[2],
                                          'capture_1s_sigma_token':r[3],'resolution':'PRESERVE_SEPARATE_AXES'})
    diff_audits=[]
    for initial in ('1s','2s'):
        total_id=f'NR_CX:{initial}:total'
        partial=[cid for cid in dataset.channels if cid.startswith(f'NR_CX:{initial}:') and cid!=total_id]
        keys=set(dataset.available_energies(total_id))
        for cid in partial:keys.intersection_update(dataset.available_energies(cid))
        rows=[]
        for e in sorted(keys):
            a=dataset.sample(total_id,e,scope='payload_domain')
            p=dataset.aggregate(partial,e,scope='payload_domain')
            with localcontext() as ctx:
                ctx.prec=80
                total=Decimal(a['value']);subtotal=Decimal(p['value']);delta=total-subtotal
                frac=str(delta/total) if total else None
            rows.append({'energy':str(e),'total':str(total),'supplied_sum':str(subtotal),
                         'difference':str(delta),'difference_fraction':frac})
        diff_audits.append({'initial':initial,'partial_members':partial,'matched_native_energies':len(keys),
            'unmatched_total_energies':[str(e) for e in dataset.available_energies(total_id) if e not in keys],
            'negative_differences':sum(Decimal(x['difference'])<0 for x in rows),
            'classification':'UNASSIGNED_DIFFERENCE_NOT_IONIZATION_OR_CERTIFIED_HIGH_N',
            'inclusive_completeness_proven':False,'rows':rows})
    return {'schema':'bass-he.c0a2.native-data-audit.v1','raw_channels':len(dataset.channels),
            'native_values':native_values,'explicit_missing_values':missing,
            'structural_padding_pairs':padding_pairs,'beyond_paper_upper_values':above,
            'in_paper_values':native_values-above,'paper_stated_range':['1','200'],
            'files':tables,'catalog_coverage':coverage,'catalog_counts':counts,
            'h1s_capture_cross_axis_disagreement':disagreements,
            'total_minus_supplied_audit':diff_audits,
            'native_source_lookup_ready':True,'full_physical_source_ready':False,
            'interpolation_implemented':False,'missing_is_zero':False,
            'unit_binding':'PDF_CONTEXTUAL_CM2_NOT_CSV_HEADER',
            'unresolved':['isotope','source-native per-u divisor','provider byte identity',
                'reuse license','source uncertainty','individual basis cross sections',
                'six catalog quantities not supplied','ionization/radiative/secondary/recoil moments'],
            'new_scattering_solves':0,'new_rate_or_cosmological_histories':0}
