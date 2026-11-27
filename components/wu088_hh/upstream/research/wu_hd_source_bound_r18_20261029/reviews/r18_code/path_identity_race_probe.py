"""Reproduce path replacement only on a temporary PDF, never the original.

The replacement contains one clearly different printed target mantissa.
The actual Poppler extractor runs on whichever bytes the loader gives it.
This is input-identity testing, not a Python-private/reflection attack.
"""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parent
PDF=Path('/workspace/scratch/5f3e9bf5a6d0/source_research/GL2022_CSIC_supplement.pdf')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--module',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    blobdata=args.module.read_bytes()
    spec=importlib.util.spec_from_file_location('r18_path_race_review',args.module)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    raw=PDF.read_bytes()
    writer=PdfWriter();writer.clone_document_from_reader(PdfReader(BytesIO(raw)))
    page=writer.pages[5];contents=page.get_contents();before=contents.get_data()
    old=b'3.99\\05014\\051';new=b'9.99\\05014\\051'
    assert before.count(old)==1
    contents.set_data(before.replace(old,new,1));page.replace_contents(contents)
    io=BytesIO();writer.write(io);replacement=io.getvalue()
    realrun=subprocess.run
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'swapped_source.pdf';path.write_bytes(raw)
        def swap_then_actual_extract(*a,**kw):
            path.write_bytes(replacement)
            return realrun(*a,**kw)
        with patch.object(m.subprocess,'run',side_effect=swap_then_actual_extract):
            grid=m.load_native_grid(path)
        row=grid.lookup(15)
        clean=row.original_token=='3.99(14)' and row.nominal_cm3_s==F('3.99')/10**14
        replaced_hash=hashlib.sha256(path.read_bytes()).hexdigest()
        result={'schema':'WU_R18_VERIFIED_BYTES_INPUT_IDENTITY_RACE_PROBE_V1',
                'module_sha256':hashlib.sha256(blobdata).hexdigest(),
                'module_git_blob':hashlib.sha1(b'blob '+str(len(blobdata)).encode()+b'\0'+blobdata).hexdigest(),
                'original_source_sha256':hashlib.sha256(raw).hexdigest(),
                'temporary_replacement_sha256':replaced_hash,
                'extracted_T15_token':row.original_token,
                'issued_source_sha256':grid.source_sha256,
                'temporary_path_replaced_after_hash_before_extract':True,
                'real_source_file_touched':False,
                'extractor':'actual pdftotext process; wrapper only swaps temporary input path',
                'verdict':'PASS_VERIFIED_BYTES_IMMUNE_TO_PATH_SWAP' if clean else 'FAIL_SOURCE_HASH_AND_EXTRACTED_BYTES_DIVERGE',
                'physical_rate_example':'none;9.99 mantissa is deliberately corrupted test fixture',
                'exit_code':0}
        assert hashlib.sha256(PDF.read_bytes()).hexdigest()==m.PDF_SHA256
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))

if __name__=='__main__':main()
