"""Isolated local unit tests for verifier, not an NCP science run."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('verify_ncp',HERE/'scripts/verify_ncp.py')
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules['verify_ncp'] = mod
SPEC.loader.exec_module(mod)

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
ORACLE = ROOT/'research/hh_phys53_20261016/results/ISOLATED_COULOMB_27_CASES.json'
# Test CLI can run against the actual original bytes recovered from a
# verified PHYS52 source capsule. Fixtures remain explicitly synthetic.


@pytest.fixture(scope='module')
def reference(tmp_path_factory):
    root=tmp_path_factory.mktemp('fake_remote_receipts')
    from wu088_hh.phys53_coulomb_tail import outgoing_cf
    saved27=None
    for radius in mod.RADII:
        rows=[]
        for ell in range(mod.FIRST,mod.LAST+1):
            z=outgoing_cf(ell,radius,1152)
            rows.append((ell,z.real,z.imag))
        for depth,workers in ((768,1),(1152,1),(1152,8)):
            path=root/f'ref_r{radius}_d{depth}_w{workers}.csv'
            with path.open('w') as f:
                f.write(','.join(mod.HEADER)+'\n')
                for ell,re,im in rows:
                    f.write(f'{ell},{radius:.9f},{re:.17e},{im:.17e}\n')
        if radius==27:saved27=rows
    assert saved27 is not None
    # This is a controlled fixture for testing verification mechanics,
    # not a fabricated claim of actual remote Rust execution.
    with (root/'bench_r27_d2048_w1_rep1.csv').open('w') as f:
        f.write(','.join(mod.HEADER)+'\n')
        ref=dict((ell,(re,im)) for ell,re,im in saved27)
        for ell in range(mod.BENCH_FIRST,mod.BENCH_LAST+1):
            re,im=ref.get(ell,(-float(ell)/27,0.0))
            f.write(f'{ell},27.000000000,{re:.17e},{im:.17e}\n')
    sample=(root/'bench_r27_d2048_w1_rep1.csv').read_bytes()
    for w in mod.BENCH_WORKERS:
        for rep in mod.BENCH_REPEATS:
            tag=f'bench_r27_d2048_w{w}_rep{rep}'
            (root/(tag+'.csv')).write_bytes(sample)
            (root/(tag+'.time')).write_text(f'wall_s={16/w+rep/100:.3f}\npeak_rss_KiB=5000\n')
    return root


def test_recovered_original_frozen_source_sha():
    assert SOURCE.is_file()
    assert mod.digest(SOURCE)==mod.ORIGINAL_SHA


def test_happy_path_simulated_csv_verification(reference):
    out=mod.verify(reference,ORACLE,SOURCE,expect_bench=True)
    assert out['status']=='PASS_SCOPE_CENTRAL_COULOMB_RUST_REFERENCE'
    assert out['highest_normalized_real_error']<2e-12
    assert out['benchmark_parity']=='ALL_12_CSV_FILES_BYTE_EQUAL'
    assert out['ncp_matched_output_performance']['speedup_over_serial']['8']>0


def test_oracle_missing_distinct_failure(reference,tmp_path):
    missing=tmp_path/'does_not_exist.json'
    with pytest.raises(mod.VerificationError,match='oracle missing'):
        mod.verify(reference,missing,SOURCE,expect_bench=True)


def test_source_tamper_rejected(reference,tmp_path):
    fake=tmp_path/'source.npz';fake.write_bytes(b'fake')
    with pytest.raises(mod.VerificationError,match='SHA256 mismatch'):
        mod.verify(reference,ORACLE,fake,expect_bench=False)


def test_parallel_byte_disagreement_rejected(reference,tmp_path):
    # Copy the synthetic suite so the shared fixture remains intact.
    dest=tmp_path/'out';dest.mkdir()
    for f in reference.iterdir(): (dest/f.name).write_bytes(f.read_bytes())
    p=dest/'ref_r27_d1152_w8.csv'
    lines=p.read_text().splitlines()
    lines[-1] += ' '  # valid numeric trailing space, but bytes differ
    p.write_text('\n'.join(lines)+'\n')
    with pytest.raises(mod.VerificationError,match='parallel/serial'):
        mod.verify(dest,ORACLE,SOURCE,expect_bench=False)


def test_truncated_grid_rejected(reference,tmp_path):
    dest=tmp_path/'out';dest.mkdir()
    for f in reference.iterdir(): (dest/f.name).write_bytes(f.read_bytes())
    p=dest/'ref_r43_d768_w1.csv'
    p.write_text('\n'.join(p.read_text().splitlines()[:-1])+'\n')
    with pytest.raises(mod.VerificationError,match='coverage'):
        mod.verify(dest,ORACLE,SOURCE,expect_bench=False)


def test_nan_rejected(reference,tmp_path):
    dest=tmp_path/'out';dest.mkdir()
    for f in reference.iterdir(): (dest/f.name).write_bytes(f.read_bytes())
    p=dest/'ref_r30_d1152_w1.csv'
    data=p.read_text()
    line=data.splitlines()[8]
    fields=line.split(',');fields[2]='NaN'
    p.write_text(data.replace(line,','.join(fields)))
    with pytest.raises(mod.VerificationError,match='nonfinite'):
        mod.verify(dest,ORACLE,SOURCE,expect_bench=False)


def test_benchmark_zero_payload_rejected(reference,tmp_path):
    dest=tmp_path/'out';dest.mkdir()
    for f in reference.iterdir(): (dest/f.name).write_bytes(f.read_bytes())
    p=dest/'bench_r27_d2048_w8_rep3.csv'
    rows=p.read_text().splitlines()
    # Keep exact row/column format but corrupt a scientific benchmark anchor.
    cols=rows[1].split(',');cols[2]='0.00000000000000000e+00'
    rows[1]=','.join(cols)
    p.write_text('\n'.join(rows)+'\n')
    with pytest.raises(mod.VerificationError,match='benchmark/science real mismatch'):
        mod.verify(dest,ORACLE,SOURCE,expect_bench=True)
