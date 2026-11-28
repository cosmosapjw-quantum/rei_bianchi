"""Source-bound ingestion of Liu et al. (2024), Tables 1 and 2.

This module does not digitize plots, invent scattering data, interpolate, or
approve the data as a physical rate provider. Decimal strings remain strings.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Sequence

PDF_SHA256 = '522b97808ba76dbd38e5607bb8b1d50e736fa1b59d1adb57261ce7e5c6a5b1df'
ARTICLE_DOI = '10.1088/1674-1056/ad5322'
DATASET_DOI = '10.57760/sciencedb.j00113.00114'
STATES = ('1s','2s','2p','3s','3p','3d','4s','4p','4d','4f')
class SourceError(ValueError):
    """Source identity is unresolved or inconsistent."""
class SourceUnavailable(SourceError):
    """A requested quantity was not supplied by the recovered source."""
class SchemaError(SourceError):
    """A typed source contract was violated."""

_NUMBER = r'\d+(?:\.\d+)?'
_ENERGY = r'-\d+\.\d+'
_ROW = re.compile(r'(?<!\S)([1-9]\d*[spdfg])\s+('+_ENERGY+r')\s+('+_ENERGY+r')\s+('+_NUMBER+r'%)\s+('+_ENERGY+r')\s+('+_NUMBER+r'%)\s+('+_ENERGY+r')\s+('+_NUMBER+r'%)(?!\S)')


def parse_text_tables(text: str) -> dict[str, Any]:
    """Parse direct PDF text in its original reading order; fail on ambiguity."""
    text = text.replace('\u2212','-')
    if len(re.findall(r'^Table 1\.',text,re.M)) != 1 or len(re.findall(r'^Table 2\.',text,re.M)) != 1:
        raise SchemaError('Exactly one Table 1 and Table 2 caption required')
    before, levels_text = re.split(r'^Table 2\.',text,maxsplit=1,flags=re.M)
    basis_text = re.split(r'^Table 1\.',before,maxsplit=1,flags=re.M)[1]
    tokens = basis_text.split()
    try:
        tokens = tokens[tokens.index('s'):]
    except ValueError as exc:
        raise SchemaError('Missing Table 1 first data row') from exc
    if len(tokens) != 50:
        raise SchemaError(f'Table 1 needs 5x10 tokens, found {len(tokens)}')
    basis: list[dict[str, Any]] = []
    for i,l in enumerate('spdfg'):
        row = tokens[10*i:10*(i+1)]
        if row[0] != l:
            raise SchemaError('Table 1 angular row order/uniqueness mismatch')
        for j,b in enumerate(('B1','B2','B3')):
            alpha,beta,count = row[1+3*j:4+3*j]
            if not re.fullmatch(_NUMBER,alpha) or not re.fullmatch(_NUMBER,beta) or not count.isdigit():
                raise SchemaError('Invalid Table 1 numeric token')
            if Decimal(alpha)<=0 or Decimal(beta)<=1 or int(count)<=0:
                raise SchemaError('Invalid Table 1 parameter domain')
            basis.append({'basis':b,'l':l,'alpha_token':alpha,'beta_token':beta,
                          'count':int(count),'alpha_unit':'a0^-2',
                          'source_formula':'alpha_n = alpha * beta^(1-n)',
                          'data_kind':'PUBLISHED_BASIS_PARAMETER_NOT_DEPLOYED_BASIS'})
    # Heading/species markers are explicit; do not infer He from energy magnitude.
    blocks = re.split(r'(?m)^\s*(H|He\+)\s*$', levels_text)
    if len(blocks)!=5 or blocks[1]!='H' or blocks[3]!='He+':
        raise SchemaError('Table 2 species blocks missing or ambiguous')
    levels=[]
    for species,block in [('HI',blocks[2]),('HeII',blocks[4])]:
        rows = list(_ROW.finditer(block))
        if len(rows)!=10 or tuple(x.group(1) for x in rows)!=STATES:
            raise SchemaError('Table 2 states, counts or numeric tokens inconsistent')
        for match in rows:
            st,eref,b1,p1,b2,p2,b3,p3=match.groups()
            levels.append({'species':species,'state':st,'E_ref_token':eref,
                           'E_B1_token':b1,'E_B2_token':b2,'E_B3_token':b3,
                           'Delta_B1_percent_token':p1,'Delta_B2_percent_token':p2,
                           'Delta_B3_percent_token':p3,'energy_unit':'E_h',
                           'energy_kind':'signed_electronic_energy',
                           'reference_authority':'NIST_ASD_5.11_AS_QUOTED_BY_LIU2024_NOT_FRESH_NIST',
                           'data_kind':'PUBLISHED_LEVEL_TABLE_NOT_CERTIFIED_ENCLOSURE'})
    return {'basis':basis,'levels':levels,'scattering_numeric_rows':0,
            'scattering_numeric_admitted':False,'interpolation_performed':False,
            'plot_digitization_performed':False,'source_percent_scope':'LEVEL_COMPARISON_NOT_SIGMA_UNCERTAINTY'}


def parse_pdf_tables(path: str | Path, expected_sha256: str) -> dict[str, Any]:
    """Read original bytes, verify an externally pinned hash, then parse tables."""
    if not re.fullmatch(r'[0-9a-f]{64}',expected_sha256):
        raise SourceError('Expected SHA256 must be 64 lowercase hex characters')
    path=Path(path); payload=path.read_bytes()
    sha=hashlib.sha256(payload).hexdigest()
    if sha != expected_sha256:
        raise SourceError('SHA256 mismatch; refusing a different source snapshot')
    import fitz
    with fitz.open(stream=payload,filetype='pdf') as doc:
        texts=[page.get_text('text',sort=False) for page in doc]
        if ARTICLE_DOI not in '\n'.join(texts):
            raise SourceError('Article DOI absent in recovered PDF')
        tablepages=[i for i,t in enumerate(texts) if 'Table 1.' in t and 'Table 2.' in t]
        if len(tablepages)!=1:
            raise SchemaError('Unique atomic table page not found')
        result=parse_text_tables(texts[tablepages[0]])
        result['source']={'name':path.name,'bytes':len(payload),'sha256':sha,
                          'article_doi':ARTICLE_DOI,'dataset_doi':DATASET_DOI,
                          'pdf_pages':len(doc),'pdf_page_tables':tablepages[0]+1,
                          'printed_page_tables':'083401-3','extraction':'DIRECT_PDF_TEXT_NO_OCR',
                          'minus_normalized':'U+2212 to ASCII minus; all decimal digits retained',
                          'embedded_files':doc.embfile_count()}
    return result


def source_audit(data: dict[str, Any]) -> dict[str, Any]:
    """Exact-decimal consistency checks, not validation of the source physics."""
    if len(data.get('basis',[]))!=15 or len(data.get('levels',[]))!=20:
        raise SchemaError('Incomplete extracted tables')
    lower=[];percent_checks=[]
    with localcontext() as ctx:
        ctx.prec=60
        for row in data['levels']:
            er=Decimal(row['E_ref_token'])
            for b in ('B1','B2','B3'):
                val=Decimal(row[f'E_{b}_token'])
                per=Decimal(row[f'Delta_{b}_percent_token'][:-1])
                calc=100*abs(val-er)/abs(er)
                # Both energies have seven decimals. This is a display-rounding
                # allowance, never an uncertainty in the atomic calculation.
                half=Decimal('0.00000005')
                lo=100*max(Decimal(0),abs(val-er)-2*half)/(abs(er)+half)
                hi=100*(abs(val-er)+2*half)/(abs(er)-half)
                allowed=(lo<=per+Decimal('0.0005') and hi>=per-Decimal('0.0005'))
                percent_checks.append({'species':row['species'],'state':row['state'],'basis':b,
                    'computed_magnitude_percent':str(calc),'printed_percent':str(per),
                    'compatible_with_display_rounding':allowed})
                if row['state']=='1s':
                    z=1 if row['species']=='HI' else 2
                    bound=-Decimal(z*z)/2
                    if val+half<bound:
                        lower.append({'species':row['species'],'basis':b,
                            'printed_energy_au':str(val),'stated_nonrelativistic_lower_bound_au':str(bound),
                            'deficit_below_bound_au':str(bound-val),
                            'status':'SOURCE_TABLE_CONSISTENCY_FLAG_NOT_SOLVER_DIAGNOSIS'})
        counts={b:sum(r['count']*(2*'spdfg'.index(r['l'])+1) for r in data['basis'] if r['basis']==b)
                for b in ('B1','B2','B3')}
    return {'level_energy_values':80,'reported_percentages':60,'basis_triplets':15,
            'spherical_gto_counts':counts,'paper_counts':[215,240,265],
            'ground_state_lower_bound_conflicts':lower,'percent_checks':percent_checks,
            'source_values_modified':False,'physical_certificate':False,
            'note':'Source Table 2 denominator is printed signed E_Nist; percentages are positive magnitudes. Abs(E_ref) used only in the declared comparison audit.'}


def coverage_registry() -> list[dict[str, Any]]:
    """Human-reviewed figure specifications, never curve-derived numeric points."""
    rows=[]
    def add(process: str,initial: str,final: str,fig: str,page: int,kind: str='subshell') -> None:
        rows.append({'id':f'{process}:{initial}:{final}','registry_reaction_id':process,
            'projectile':'HeIII','initial_target':f'HI:{initial}',
            'final_center':'HeII' if process=='NR_CX' else 'HI',
            'final':final,'resolution':kind,'figure':fig,'pdf_page':page,
            'quantity':'cross_section','numeric_rows':0,'numeric_source_available':False,
            'native_energy_unit':'keV/amu','energy_frame':'projectile_in_target_rest_frame',
            'per_amu_divisor_definition':None,'projectile_isotope':None,
            'stated_study_energy_range':[1,200],'actual_native_grid':None,
            'figure_leftmost_labeled_tick':10 if initial=='1s' else 1,
            'declared_range_is_not_channel_grid':True,
            'plot_value_unit':'1e-16 cm^2' if process=='EXC' else 'cm^2',
            'source_curve':'Present = (B1+B2+B3)/3, Eq.(9)',
            'source_uncertainty':None,'data_kind':'FIGURE_SPECIFICATION_NO_DIGITIZED_VALUES',
            'infinite_bound_completeness':False})
    for st,fig in [('2s','2a'),('2p','2b'),('3s','2c'),('3p','2d'),('3d','2e')]:add('EXC','1s',st,fig,5)
    for n in (4,5):add('EXC','1s',f'n{n}','2f',5,'shell')
    add('NR_CX','1s','total','3',6,'source_reported_total')
    for st,fig in zip(('1s','2s','2p','3s','3p','3d'),('4a;5(n1)','4b','4c','4d','4e','4f')):add('NR_CX','1s',st,fig,6)
    for n in (2,3,4,5):add('NR_CX','1s',f'n{n}','5',7,'shell')
    for st in ('3s','3p','3d'):add('EXC','2s',st,'6a',7)
    for st in ('4s','4p','4d','4f'):add('EXC','2s',st,'6b',7)
    add('EXC','2s','n5','6c',7,'shell')
    add('NR_CX','2s','total','7',7,'source_reported_total')
    for st,fig in zip(('3s','3p','3d'),('8a','8b','8c')):add('NR_CX','2s',st,fig,8)
    add('NR_CX','2s','n3','8d',8,'shell')
    for st,fig in zip(('4s','4p','4d','4f'),('9a','9b','9c','9d')):add('NR_CX','2s',st,fig,8)
    for n in (4,5):add('NR_CX','2s',f'n{n}','10',9,'shell')
    return rows


def _covered_states(row: dict[str, Any]) -> set[str]:
    f=row['final']
    if f=='total':return {'*'}
    if f.startswith('n'):
        n=int(f[1:]);return {f'{n}{l}' for l in 'spdfg'[:n]}
    return {f}


def check_selection(ids: Sequence[str], coverage: list[dict[str, Any]]) -> dict[str, Any]:
    """Check disjoint quantities; this does not sum unavailable values."""
    if isinstance(ids,str) or not ids:
        raise SchemaError('A nonempty channel ID sequence is required')
    if len(ids)!=len(set(ids)):
        raise SchemaError('duplicate/overlap in channel selection')
    index={x['id']:x for x in coverage}
    if any(i not in index for i in ids):
        raise SourceUnavailable('Requested channel not present; absence is not zero')
    selected=[index[i] for i in ids]
    if len({r['initial_target'] for r in selected})!=1:
        raise SchemaError('Different initial states must not be combined')
    if len({r['registry_reaction_id'] for r in selected})!=1:
        raise SchemaError('Different reaction mechanisms must not be combined')
    covered:set[str]=set()
    for row in selected:
        s=_covered_states(row)
        if covered and ('*' in covered or '*' in s or covered.intersection(s)):
            raise SchemaError('aggregate/subshell overlap: would double count')
        covered |= s
    return {'ids':list(ids),'disjoint_in_source_resolution':True,
            'numeric_source_available':False,'summed_cross_section':None,
            'infinite_bound_completeness':False}


def export_quantity(data: dict[str, Any], quantity: str) -> list[dict[str, Any]]:
    if quantity=='basis_parameters':return data['basis']
    if quantity=='electronic_energies':return data['levels']
    raise SourceUnavailable(f'{quantity}: no native numeric data recovered for this quantity')


def write_json_create_only(path: str | Path, data: Any) -> None:
    """Atomic publication without clobbering an existing path."""
    path=Path(path)
    payload=(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(payload);out.flush();os.fsync(out.fileno())
        os.link(tmp,path)  # Atomic and fails if path already exists.
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        os.unlink(tmp)


def main(argv: Sequence[str] | None=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf',required=True,type=Path)
    ap.add_argument('--sha256',required=True)
    ap.add_argument('--quantity',default='tables',choices=('tables','basis_parameters','electronic_energies','cross_section','heating_rate'))
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args(argv)
    try:
        d=parse_pdf_tables(args.pdf,args.sha256)
        result={'schema':'bass-he.liu2024.intake.v1','source':d['source'],
                'data':d if args.quantity=='tables' else export_quantity(d,args.quantity),
                'audit':source_audit(d),'physical_certificate':False,
                'atomic_only':True,'consumer_hint':'rei_bianchi'}
        write_json_create_only(args.out,result)
    except (SourceError,FileExistsError,OSError) as exc:
        print(json.dumps({'status':'BLOCKED','error_type':type(exc).__name__,'message':str(exc)}),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
