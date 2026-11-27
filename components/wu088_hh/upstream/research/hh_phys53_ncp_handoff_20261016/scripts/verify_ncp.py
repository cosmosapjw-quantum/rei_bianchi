#!/usr/bin/env python3
"""PHYS53 finite-grid Rust NCP parity: source-locked Coulomb reference only.

No mpmath or Rust runtime required for *verification*; the oracle was generated
in the earlier PHYS53 isolated high-precision run and has its own provenance.
Finite CSV comparisons do NOT certify the infinite-l screened DtN.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

ORIGINAL_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
HEADER = ['ell', 'r_Bohr', 'real_z', 'imag_f64_noncert']
RADII = (27, 30, 43)
FIRST, LAST = 21, 256
BENCH_FIRST, BENCH_LAST = 21, 4096
DEPTHS = (768, 1152)
REF_WORKERS = (1, 8)
BENCH_WORKERS = (1, 2, 4, 8)
BENCH_REPEATS = (1, 2, 3)
REAL_RTOL = 2e-12
IM_ABS_TOL = 3e-12  # Only low-l (<=29) current above resolution floor.


class VerificationError(ValueError):
    """Physical reference, input, or execution-contract mismatch."""


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(2**20), b''):
            h.update(data)
    return h.hexdigest()


def require(cond: bool, message: str) -> None:
    if not cond:
        raise VerificationError(message)


def read_csv(path: Path, first: int, last: int, radius: int) -> tuple[dict[int, tuple[float, float]], bytes]:
    require(path.is_file(), f'missing required Rust CSV {path.name}')
    raw = path.read_bytes()
    try:
        text = raw.decode('ascii')
    except UnicodeDecodeError as exc:
        raise VerificationError(f'non-ASCII Rust CSV {path.name}') from exc
    reader = csv.reader(text.splitlines())
    header = next(reader, None)
    require(header == HEADER, f'incorrect CSV header in {path.name}: {header}')
    values = {}
    for index, row in enumerate(reader, start=2):
        require(len(row) == 4, f'bad CSV row {path.name}:{index}')
        try:
            ell = int(row[0]); r = float(row[1]); real = float(row[2]); imag = float(row[3])
        except ValueError as exc:
            raise VerificationError(f'non-numeric CSV row {path.name}:{index}') from exc
        require(math.isfinite(r) and r == float(radius), f'wrong radius at {path.name}:{index}')
        require(math.isfinite(real) and math.isfinite(imag), f'nonfinite impedance {path.name}:{index}')
        require(ell not in values, f'duplicate ell {ell} in {path.name}')
        values[ell] = (real, imag)
    expected = list(range(first, last + 1))
    require(list(values) == expected, f'wrong ell coverage/order in {path.name}')
    return values, raw


def oracle_rows(path: Path, expected_source_sha: str) -> dict[tuple[int, int], dict]:
    require(path.is_file(), f'oracle missing {path}')
    obj = json.loads(path.read_text(encoding='utf-8'))
    require(obj.get('schema') == 'WU088_HH_PHYS53_COULOMB_CF_V1', 'oracle schema mismatch')
    require(obj.get('physics') == 'CENTRAL_COULOMB_ONLY', 'oracle physics scope mismatch')
    require(obj.get('source_status') == 'NOT_CHECKED_IN_ISOLATED_RUNTIME',
            'oracle source evidence status changed unexpectedly')
    data = {}
    for row in obj['rows']:
        cf, ref = row['cf'], row['reference']
        ell = cf['ell']; rad = int(cf['radius_Bohr'])
        require(ell == ref['ell'] and rad == int(ref['radius_Bohr']), 'oracle row pairing mismatch')
        require(ref['physics_scope'] == 'CENTRAL_COULOMB_ONLY', 'oracle row scope mismatch')
        require(rad in RADII and FIRST <= ell <= LAST, 'oracle out-of-contract sample')
        require((ell, rad) not in data, 'duplicate oracle sample')
        require(math.isfinite(float(ref['re_per_Bohr'])), 'nonfinite mp reference')
        data[(ell, rad)] = ref
    require(len(data) == 27, f'oracle sample count is {len(data)}, expected 27')
    # The frozen original SHA is tested independently from the oracle:
    # do NOT promote historical oracle source_status retroactively.
    require(expected_source_sha == ORIGINAL_SHA, 'source contract invalid')
    return data


def read_seconds(path: Path) -> float:
    require(path.is_file(), f'missing time evidence {path.name}')
    vals = re.findall(r'^wall_s=([0-9]+(?:\.[0-9]+)?)$', path.read_text().splitlines()[0], re.M)
    require(len(vals) == 1, f'no unique wall_seconds in {path.name}')
    x = float(vals[0]);require(0 < x <= 900, f'invalid elapsed seconds in {path.name}')
    return x


def verify(root: Path, oracle: Path, source: Path, *, expect_bench: bool = True) -> dict:
    source_sha = digest(source)
    require(source_sha == ORIGINAL_SHA, 'original frozen 1386-coefficient SHA256 mismatch')
    samples = oracle_rows(oracle, source_sha)
    measured = {}
    primary_r27 = None
    worst_real = (0.0, None)
    worst_cf_delta = (0.0, None)
    worst_low_current_abs = (0.0, None)
    for r in RADII:
        saved = {}
        for depth in DEPTHS:
            for workers in REF_WORKERS if depth == 1152 else (1,):
                label = f'ref_r{r}_d{depth}_w{workers}.csv'
                saved[(depth,workers)] = read_csv(root / label, FIRST,LAST,r)
        require(saved[(1152,1)][1] == saved[(1152,8)][1],
                f'parallel/serial f64 byte mismatch r={r}')
        cf768, cf1152 = saved[(768,1)][0], saved[(1152,1)][0]
        if r == 27: primary_r27 = cf1152
        for ell in range(FIRST, LAST + 1):
            z0, z1 = cf768[ell], cf1152[ell]
            err = abs(z0[0] - z1[0]) / max(1,abs(z1[0]))
            if err > worst_cf_delta[0]: worst_cf_delta=(err,(ell,r))
            require(err <= REAL_RTOL, f'CF two-depth real disagreement at ell={ell} r={r}: {err}')
        for (ell, rr), ref in samples.items():
            if rr != r: continue
            real, im_f64 = cf1152[ell]
            expected = float(ref['re_per_Bohr'])
            err = abs(real - expected)/max(1,abs(expected))
            if err > worst_real[0]:worst_real=(err,(ell,r))
            require(err <= REAL_RTOL,
                    f'mpmath real impedance mismatch ell={ell} r={r}: {err}')
            if ell <= 29:
                j_expected = float(ref['im_per_Bohr'])
                im_err = abs(im_f64 - j_expected)
                if im_err > worst_low_current_abs[0]:worst_low_current_abs=(im_err,(ell,r))
                require(im_err <= IM_ABS_TOL,
                        f'low-l f64 Coulomb current mismatch ell={ell} r={r}: {im_err}')
            # For high ell, the f64 imaginary part is cancellation dominated;
            # its sign must NOT be a scientific acceptance gate.
        measured[str(r)]={
            'rows_each':LAST-FIRST+1,
            'depths':[768,1152],
            'deterministic_w1_vs_w8':'BYTE_IDENTICAL',
            'mp_oracle_samples':9,
        }
    out={
        'schema':'WU088_HH_PHYS53_NCP_PARITY_V1',
        'physics_scope':'CENTRAL_COULOMB_REFERENCE_ONLY',
        'valid_source_sha256':source_sha,
        'oracle_sha256':digest(oracle),
        'radii':measured,
        'highest_normalized_real_error':worst_real[0],
        'worst_real_at':worst_real[1],
        'highest_normalized_depth_difference':worst_cf_delta[0],
        'worst_depth_at':worst_cf_delta[1],
        'highest_low_l_imag_abs_error':worst_low_current_abs[0],
        'worst_imag_at':worst_low_current_abs[1],
        'scientific_gates':['frozen source SHA256','exact indexed CSV grid','all finite floats',
            'depth 768/1152 real parity','w1/w8 complete CSV byte parity',
            'independent 27 mpmath real references','l<=29 current only'],
        'noncertified':['high-l f64 imaginary current','finite-depth continued fraction rigorous error',
            'noncentral screened DtN','infinite-angular outgoing operator','H-H sigma(E),k_HH(T)'],
    }
    if expect_bench:
        speed={}
        baseline_bytes=None
        for w in BENCH_WORKERS:
            durations=[]
            for rep in BENCH_REPEATS:
                prefix=f'bench_r27_d2048_w{w}_rep{rep}'
                bvalues,raw=read_csv(root / (prefix+'.csv'),BENCH_FIRST,BENCH_LAST,27)
                require(primary_r27 is not None,'missing primary NCP r27 science grid')
                for ell in range(FIRST,LAST+1):
                    bv=bvalues[ell][0]; reference_r27=primary_r27[ell][0]
                    rel=abs(bv-reference_r27)/max(1,abs(reference_r27))
                    require(rel<=REAL_RTOL, f'benchmark/science real mismatch ell={ell} {prefix}')
                if baseline_bytes is None:baseline_bytes=raw
                require(raw == baseline_bytes, f'benchmark outputs differ for {prefix}')
                durations.append(read_seconds(root / (prefix+'.time')))
            speed[str(w)]={'wall_s':durations,'median_wall_s':statistics.median(durations)}
        speed['speedup_over_serial']={
            str(w):speed['1']['median_wall_s']/speed[str(w)]['median_wall_s'] for w in BENCH_WORKERS}
        out['ncp_matched_output_performance']=speed
        out['benchmark_parity']='ALL_12_CSV_FILES_BYTE_EQUAL'
    out['status']='PASS_SCOPE_CENTRAL_COULOMB_RUST_REFERENCE'
    return out


def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--oracle',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--skip-bench',action='store_true',help='Only for targeted diagnostic, never complete NCP acceptance')
    args=ap.parse_args(argv)
    try:
        out=verify(args.results,args.oracle,args.source,expect_bench=not args.skip_bench)
    except (VerificationError,ValueError,KeyError,OSError,json.JSONDecodeError) as exc:
        print(f'PHYS53_VERIFICATION_FAIL: {exc}',file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':out['status'],'worst_real':out['highest_normalized_real_error'],
                      'worst_depth':out['highest_normalized_depth_difference'],
                      'bench':out.get('benchmark_parity','SKIPPED')},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
