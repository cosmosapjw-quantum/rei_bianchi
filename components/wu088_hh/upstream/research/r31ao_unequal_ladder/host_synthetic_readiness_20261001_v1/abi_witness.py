#!/usr/bin/env python3
"""Evidence-only NumPy witness: fixed synthetic inputs; never historical admission.

Run with the Python executable to be identified. No installer, subprocess,
network, arbitrary array loader, scientific imports, or native build is used.
All numerical decoding is confined to the eight arrays generated below.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import importlib.util
import io
import json
import os
import platform
import re
import stat
import sys
import sysconfig
import time
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

LINK_SCHEMA = 'WU088_HISTORICAL_ABI_LINK_REFERENCES_V1'
PRODUCER_RUNTIME = '/root/WU088_R31AL_Z075_RUNTIME_20260930'
OUTPUT_PINS = {
    'OD': '7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df',
    'independent_JVP': '53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87',
}
PRODUCER_PINS = {
    'completion/mixed_h/od_run.py': '63c0925ff938340feceb5768aba40da348b3afe323214a9792012e9d0bbc664d',
    'completion/mixed_h/native.py': '44f784c895730d07e5a40ccc5369534f6a8e81798689a27c98a0bf5fd0a2d778',
    'completion/mixed_derivative/native.py': '247c9eca3c8cfa35a437f48b4ba72aac98d24dff1bc336b008058141b591a22d',
    'completion/mixed_derivative/run.py': 'd092d3e81a952d90488f25922c57ea3148b9f036d15a884f7efe51ade09de935',
}
REQUIRED_ROLES = (
    'contemporaneous_environment', 'preserved_numpy_binary_chain',
    'serializer_to_output_binding', 'layout_capture_under_identified_runtime',
)
OLD = Path(__file__).resolve().parent.parent / 'gap_closure_20261001_g0_g6_v1'
DECODER_SHA256 = 'bf1867616af07a670d61cd75c7ca0655c99e0be13fd6a73e9a4654f5fc0986f1'
AUTHORITY_SHA256 = '0a710864e659f0c02483649b2267055b7c5f37b7d7cfe604bd1286b422cc888d'
MAX_MANIFEST_BYTES = 65536
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_SENTINEL_BYTES = 4096


class Refusal(ValueError):
    """Explicit bounded refusal; no installation or scientific fallback."""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + '\n').encode()


@dataclass
class Budget:
    max_file_bytes: int = 128 * 1024 * 1024
    max_total_bytes: int = 512 * 1024 * 1024
    max_files: int = 64
    max_wall_seconds: int = 60
    hashed_bytes: int = 0
    hashed_files: int = 0
    started: float = 0.0

    def __post_init__(self):
        self.started = time.monotonic()

    def check(self):
        if time.monotonic() - self.started > self.max_wall_seconds:
            raise Refusal('cooperative wall budget exceeded')

    def identity(self, path, role):
        self.check()
        p = Path(path).resolve(strict=True)
        before = p.stat()
        if not stat.S_ISREG(before.st_mode):
            raise Refusal('identity target is not a regular file')
        if before.st_size > self.max_file_bytes or self.hashed_bytes + before.st_size > self.max_total_bytes:
            raise Refusal('identity byte budget exceeded')
        if self.hashed_files >= self.max_files:
            raise Refusal('identity file count exceeded')
        h, count = hashlib.sha256(), 0
        with p.open('rb') as f:
            opened = os.fstat(f.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns) != (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns):
                raise Refusal('identity target changed before open')
            while True:
                self.check()
                b = f.read(65536)
                if not b:
                    break
                count += len(b)
                if count > before.st_size:
                    raise Refusal('identity file changed while hashing')
                h.update(b)
        after = p.stat()
        if count != before.st_size or (before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_size):
            raise Refusal('identity file changed while hashing')
        self.hashed_bytes += count
        self.hashed_files += 1
        return {'role': role, 'path': str(p), 'bytes': count, 'sha256': h.hexdigest()}


class CappedText(io.StringIO):
    def __init__(self, cap=262144):
        super().__init__()
        self.cap, self.used = cap, 0

    def write(self, text):
        self.used += len(text.encode('utf-8'))
        if self.used > self.cap:
            raise Refusal('show_config output cap exceeded')
        return super().write(text)


def read_link_manifest(path):
    p = Path(path)
    if p.suffix != '.json' or not p.is_file() or p.is_symlink():
        raise Refusal('historical links require a regular .json metadata manifest')
    if p.stat().st_size > MAX_MANIFEST_BYTES:
        raise Refusal('historical linkage manifest too large')
    with p.open('rb') as f:
        raw = f.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise Refusal('historical linkage manifest grew past cap')
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Refusal('invalid JSON historical linkage metadata') from exc


def assess_historical_linkage(document, current_hashes):
    """Validate references only. Even perfect-looking refs NEVER close B03.

    Caller statements/hashes/URLs do not prove independence or historical
    linkage. Contents and custody require separately recorded human/project
    review. This function has no admit=True path.
    """
    result = {'status': 'MISSING_HISTORICAL_LINKAGE',
              'B03': 'RAW_ABI_AUTHORITY_BLOCKED',
              'historical_layout_admitted': False,
              'reference_contents_verified': False,
              'independent_review_admitted': False, 'reasons': [], 'references': []}
    if document is None:
        result['reasons'] = ['independently supplied historical linkage references absent']
        return result
    reasons = result['reasons']
    required = {'schema', 'producer_runtime', 'output_archive_sha256', 'producer_source_sha256', 'references'}
    if type(document) is not dict or set(document) != required:
        reasons.append('exact reference schema required; booleans are not authority')
    else:
        if document['schema'] != LINK_SCHEMA or document['producer_runtime'] != PRODUCER_RUNTIME:
            reasons.append('schema or recorded producer runtime mismatch')
        if document['output_archive_sha256'] != OUTPUT_PINS or document['producer_source_sha256'] != PRODUCER_PINS:
            reasons.append('recorded original output/source identity mismatch')
        refs = document['references']
        if type(refs) is not list or not 4 <= len(refs) <= 16:
            reasons.append('four required roles and at most sixteen references required')
        else:
            roles = set()
            for ref in refs:
                if type(ref) is not dict or set(ref) != {'role', 'uri', 'sha256', 'origin'}:
                    reasons.append('invalid reference fields')
                    continue
                if not all(type(v) is str for v in ref.values()):
                    reasons.append('reference fields must be text')
                    continue
                roles.add(ref['role'])
                if ref['role'] not in REQUIRED_ROLES or ref['origin'] != 'INDEPENDENT_HISTORICAL_RECORD':
                    reasons.append('unrecognized evidence role or origin claim')
                if not re.fullmatch('[0-9a-f]{64}', ref['sha256']):
                    reasons.append('reference SHA256 malformed')
                if ref['sha256'] in current_hashes:
                    reasons.append('current probe self-hash cannot be historical linkage')
                if not ref['uri'].startswith('https://') or len(ref['uri']) > 2048:
                    reasons.append('bounded independently resolvable HTTPS reference required')
            if roles != set(REQUIRED_ROLES):
                reasons.append('missing required historical linkage role')
            result['references'] = refs
    result['status'] = ('INVALID_HISTORICAL_LINKAGE_REFERENCES' if reasons
                        else 'REFERENCES_STRUCTURALLY_COMPLETE_REVIEW_REQUIRED')
    return result


def load_decoder():
    p = OLD / 'exact_raw_decoder' / 'decoder.py'
    b = Budget().identity(p, 'frozen_synthetic_decoder')
    if b['sha256'] != DECODER_SHA256:
        raise Refusal('frozen decoder SHA256 mismatch')
    name = '_wu088_pinned_synthetic_decoder'
    spec = importlib.util.spec_from_file_location(name, p)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return sys.modules[name]


def dyadic(mantissa, exponent):
    return Fraction(mantissa << exponent, 1) if exponent >= 0 else Fraction(mantissa, 1 << -exponent)


def real_sentinel_spec(nmant, minexp):
    if type(nmant) is not int or type(minexp) is not int or not 1 <= nmant <= 112 or not -16382 <= minexp <= -1:
        raise Refusal('unsupported bounded finfo metadata')
    names = ['positive_zero', 'negative_zero', 'one', 'negative_two',
             'one_plus_ulp', 'minimum_normal', 'minimum_subnormal', 'negative_minimum_subnormal']
    values = [Fraction(0), Fraction(0), Fraction(1), Fraction(-2),
              1 + dyadic(1, -nmant), dyadic(1, minexp),
              dyadic(1, minexp - nmant), -dyadic(1, minexp - nmant)]
    return names, values, [False, True, False, False, False, False, False, False]


def exact_record(value):
    if isinstance(value, tuple):
        return {'real': exact_record(value[0]), 'imag': exact_record(value[1])}
    d = value.denominator
    if d & (d - 1):
        raise Refusal('expected dyadic denominator')
    return {'numerator_hex': hex(value.numerator), 'denominator_power_of_two': d.bit_length() - 1}


def dtype_metadata(np, dtype):
    d = np.dtype(dtype)
    real = np.empty((), dtype=d).real.dtype
    f = np.finfo(real)
    return {'str': d.str, 'name': d.name, 'itemsize': int(d.itemsize), 'alignment': int(d.alignment),
            'byteorder': d.byteorder, 'real_component_bytes': int(real.itemsize),
            'finfo': {k: int(getattr(f, k)) for k in ('bits', 'nmant', 'iexp', 'minexp', 'maxexp')}}


def fixed_sentinels(np, metadata):
    """Construct fixed eight-value matrices, without parsing any payload input."""
    perm = [2, 3, 0, 1, 6, 7, 4, 5]
    for label, dtype in [('float64', np.float64), ('longdouble', np.longdouble),
                         ('complex128', np.complex128), ('clongdouble', np.clongdouble)]:
        info = metadata[label]['finfo']
        nmant, minexp = info['nmant'], info['minexp']
        labels, expected_real, negative_zero = real_sentinel_spec(nmant, minexp)
        d = np.dtype(dtype)
        rd = np.empty((), dtype=d).real.dtype.type
        with np.errstate(under='ignore'):
            v = np.array([rd(0), np.copysign(rd(0), rd(-1)), rd(1), rd(-2),
                rd(1) + np.ldexp(rd(1), -nmant), np.ldexp(rd(1), minexp),
                np.ldexp(rd(1), minexp - nmant), -np.ldexp(rd(1), minexp - nmant)], dtype=rd)
        complex_kind = d.kind == 'c'
        expected = ([(expected_real[i], expected_real[perm[i]]) for i in range(8)]
                    if complex_kind else expected_real)
        signs = ([(negative_zero[i], negative_zero[perm[i]]) for i in range(8)]
                 if complex_kind else [(x,) for x in negative_zero])
        for order in ('C', 'F'):
            array = np.zeros((2, 4), dtype=d, order=order)
            if complex_kind:
                array.real[...] = v.reshape((2, 4))
                array.imag[...] = v[perm].reshape((2, 4))
            else:
                array[...] = v.reshape((2, 4))
            out = io.BytesIO()
            np.save(out, array, allow_pickle=False)
            raw = out.getvalue()
            if len(raw) > MAX_SENTINEL_BYTES:
                raise Refusal('synthetic NPY output cap exceeded')
            yield label + '_' + order, raw, expected, signs, labels, metadata[label]


def decode_generated(decoder, raw, expected, signs, metadata, evidence_hash):
    """Only called on local fixed_sentinels output. No CLI decode operation."""
    header = decoder.inspect_npy_header(raw, max_elements=8)
    authority = None
    candidate = 'IEEE_BINARY64'
    if metadata['real_component_bytes'] == 16:
        finfo = metadata['finfo']
        if (finfo['nmant'], finfo['iexp'], finfo['minexp'], finfo['maxexp']) == (63, 15, -16382, 16384) and header.byte_order == 'little':
            candidate = 'x87_80'
        elif (finfo['nmant'], finfo['iexp'], finfo['minexp'], finfo['maxexp']) == (112, 15, -16382, 16384):
            candidate = 'ieee_binary128'
        else:
            raise Refusal('no supported synthetic extended-layout candidate')
        authority = decoder.LayoutAuthority(layout=candidate, byte_order=header.byte_order,
            component_bytes=16, value_offset=0, complex_component_order='real_imag',
            scope='SYNTHETIC_FIXTURE_ONLY', evidence_id='CURRENT_FIXED_SYNTHETIC_SENTINELS',
            evidence_sha256=(evidence_hash,), bound_npy_sha256=sha(raw))
    decoded = decoder.decode_npy_bytes(raw, authority=authority, max_elements=8)
    if decoded.values_c_order != tuple(expected) or decoded.negative_zero_c_order != tuple(signs):
        raise Refusal('current synthetic bytes disagree with independent exact values or signed zero')
    return decoded, candidate


def collect(output_dir, *, historical_manifest=None, numpy_loader=None):
    output = Path(output_dir)
    if output.exists() or output.is_symlink():
        raise Refusal('output directory must be create-only')
    if not output.parent.is_dir():
        raise Refusal('output parent must already exist')
    output.mkdir(mode=0o700)
    budget = Budget()
    written = 0

    def save(name, data):
        nonlocal written
        if written + len(data) > MAX_OUTPUT_BYTES:
            raise Refusal('total output cap exceeded')
        with (output / name).open('xb') as f:
            f.write(data)
        written += len(data)

    r = {'schema': 'WU088_CURRENT_NUMPY_SYNTHETIC_ABI_WITNESS_V1',
         'status': 'PROBE_INCOMPLETE', 'scope': 'CURRENT_ENVIRONMENT_FIXED_SYNTHETIC_ONLY',
         'historical_layout_admitted': False, 'B03': 'RAW_ABI_AUTHORITY_BLOCKED',
         'actual_HH_payloads_read': 0, 'native_builds': 0,
         'synthetic_payloads_generated': 0, 'identities': [], 'sentinels': [],
         'limits': {'hash_files': 64, 'hash_file_bytes': budget.max_file_bytes,
                    'hash_total_bytes': budget.max_total_bytes, 'show_config_bytes': 262144,
                    'sentinel_count': 8, 'elements_per_sentinel': 8, 'output_bytes': MAX_OUTPUT_BYTES,
                    'cooperative_wall_seconds': 60, 'hard_wall_limit': False,
                    'hard_memory_limit': False,
                    'limitation': 'NumPy import/calls may not return; use an external process guard for hard wall/address-space limits.'},
         'recorded_historical_producer': {'runtime': PRODUCER_RUNTIME,
             'output_archive_sha256': OUTPUT_PINS, 'producer_source_sha256': PRODUCER_PINS}}
    try:
        r['identities'].append(budget.identity(__file__, 'collector_source'))
        r['identities'].append(budget.identity(sys.executable, 'python_executable'))
        r['python'] = {'invoked_executable': sys.executable, 'version': sys.version,
                       'byteorder': sys.byteorder, 'platform': platform.platform()}
        r['python_config'] = {k: sysconfig.get_config_var(k) for k in
            ('CONFIG_ARGS', 'SOABI', 'MULTIARCH', 'Py_ENABLE_SHARED', 'LDLIBRARY', 'LIBDIR', 'CC', 'CFLAGS')}
        for role, path in [('python_sysconfig', sysconfig.__file__),
                           ('python_config_header', sysconfig.get_config_h_filename()),
                           ('python_config_makefile', sysconfig.get_makefile_filename())]:
            r['identities'].append(budget.identity(path, role))
        libdir, libname = sysconfig.get_config_var('LIBDIR'), sysconfig.get_config_var('LDLIBRARY')
        if isinstance(libdir, str) and isinstance(libname, str) and (Path(libdir) / libname).is_file():
            r['identities'].append(budget.identity(Path(libdir) / libname, 'python_configured_shared_library'))
        cfg = json_bytes(r['python_config'])
        save('python_config.json', cfg)
        r['python_config_sha256'] = sha(cfg)
        try:
            np = (numpy_loader or (lambda: importlib.import_module('numpy')))()
        except (ImportError, OSError) as exc:
            r['status'] = 'NUMPY_UNAVAILABLE'
            r['blocker'] = type(exc).__name__ + ': ' + str(exc)[:2000]
            r['installation_attempted'] = False
        else:
            r['numpy_version'] = str(np.__version__)
            cfgout = CappedText()
            with contextlib.redirect_stdout(cfgout), contextlib.redirect_stderr(cfgout):
                np.show_config()
            budget.check()
            config_data = cfgout.getvalue().encode()
            save('numpy_show_config.txt', config_data)
            r['numpy_show_config_sha256'] = sha(config_data)
            modules = [('numpy', np), ('numpy_config', np.__config__),
                       ('numpy_format', importlib.import_module('numpy.lib.format'))]
            seen = set()
            for role, module in modules:
                p = Path(module.__file__).resolve()
                if p not in seen:
                    r['identities'].append(budget.identity(p, role)); seen.add(p)
            # NumPy decorates public __module__ names. Hash the code object's
            # source file, not just numpy.lib.format's re-export wrapper.
            for role, function in [('numpy_write_array_implementation', np.lib.format.write_array),
                                   ('numpy_save_implementation', getattr(np.save, '__wrapped__', np.save))]:
                code = getattr(function, '__code__', None)
                filename = getattr(code, 'co_filename', None)
                if not isinstance(filename, str):
                    raise Refusal('NumPy serializer implementation source cannot be identified')
                r['identities'].append(budget.identity(filename, role))
            for name, module in sorted(tuple(sys.modules.items())):
                p = getattr(module, '__file__', None)
                if name.startswith('numpy.') and isinstance(p, str) and p.endswith(('.so', '.pyd', '.dylib')):
                    p = Path(p).resolve()
                    if p not in seen:
                        r['identities'].append(budget.identity(p, 'loaded_numpy_extension:' + name)); seen.add(p)
            if not any(x['role'].startswith('loaded_numpy_extension:') for x in r['identities']):
                raise Refusal('no NumPy extension identity captured')
            for name in ('_numpyconfig.h', 'numpyconfig.h'):
                r['identities'].append(budget.identity(Path(np.get_include()) / 'numpy' / name, 'numpy_header:' + name))
            authority = budget.identity(OLD / 'RAW_ABI_AUTHORITY.json', 'prior_authority_record')
            if authority['sha256'] != AUTHORITY_SHA256:
                raise Refusal('prior authority record SHA256 mismatch')
            r['identities'].append(authority)
            r['identities'].append(budget.identity(OLD / 'exact_raw_decoder' / 'decoder.py', 'frozen_exact_decoder'))
            r['dtype_metadata'] = {name: dtype_metadata(np, dtype) for name, dtype in
                [('float64', np.float64), ('complex128', np.complex128),
                 ('longdouble', np.longdouble), ('clongdouble', np.clongdouble)]}
            meta_bytes = json_bytes(r['dtype_metadata'])
            save('dtype_metadata.json', meta_bytes)
            r['dtype_metadata_sha256'] = sha(meta_bytes)
            decoder = load_decoder()
            for name, raw, expected, signs, labels, meta in fixed_sentinels(np, r['dtype_metadata']):
                budget.check()
                # Exact NPY bytes in text transport for additive Git publication.
                # This is reversible encoding, not a reconstruction of values.
                save(name + '.npy.hex', raw.hex().encode('ascii') + b'\n')
                r['synthetic_payloads_generated'] += 1
                decoded, candidate = decode_generated(decoder, raw, expected, signs, meta, sha(meta_bytes))
                r['sentinels'].append({'name': name, 'file': name + '.npy.hex', 'file_encoding': 'hex', 'bytes': len(raw),
                    'raw_npy_sha256': decoded.raw_npy_sha256, 'payload_sha256': decoded.payload_sha256,
                    'canonical_sha256': decoded.canonical_sha256, 'header': asdict(decoded.header),
                    'labels_real_c_order': labels, 'tested_candidate': candidate,
                    'authority_scope': 'CURRENT_SYNTHETIC_ONLY_NOT_HISTORICAL',
                    'expected_values': [exact_record(x) for x in expected],
                    'decoded_values': [exact_record(x) for x in decoded.values_c_order],
                    'negative_zero_c_order': decoded.negative_zero_c_order,
                    'padding_hex_c_order': decoded.padding_hex_c_order,
                    'verification': 'EXACT_DYADICS_AND_SIGNED_ZERO_MATCH'})
            r['status'] = 'CURRENT_SYNTHETIC_WITNESS_CAPTURED'
    except (Refusal, OSError, ValueError, AttributeError, ImportError) as exc:
        r['status'] = 'PROBE_REFUSED_OR_UNSUPPORTED'
        r['blocker'] = type(exc).__name__ + ': ' + str(exc)[:2000]
    current_hashes = {x['sha256'] for x in r['identities']}
    current_hashes.update(x['raw_npy_sha256'] for x in r['sentinels'])
    current_hashes.update(v for k, v in r.items() if k.endswith('_sha256') and type(v) is str)
    r['historical_linkage'] = assess_historical_linkage(historical_manifest, current_hashes)
    r['measurements'] = {'hashed_bytes': budget.hashed_bytes, 'hashed_files': budget.hashed_files,
                         'wall_seconds': time.monotonic() - budget.started,
                         'bytes_written_before_report': written}
    # Normalize tuples to JSON lists so the returned value equals stored bytes.
    r = json.loads(json_bytes(r))
    save('WITNESS.json', json_bytes(r))
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', required=True, type=Path, help='new directory under an existing parent')
    p.add_argument('--historical-links', type=Path, help='bounded JSON references only; never admission')
    args = p.parse_args(argv)
    try:
        links = read_link_manifest(args.historical_links) if args.historical_links else None
        r = collect(args.output_dir, historical_manifest=links)
    except (Refusal, OSError) as exc:
        print(json.dumps({'status': 'REFUSED', 'reason': str(exc), 'B03': 'RAW_ABI_AUTHORITY_BLOCKED'}))
        return 2
    print(json.dumps({'status': r['status'], 'B03': r['B03'],
                      'historical_layout_admitted': False, 'output_dir': str(args.output_dir)}))
    return 0 if r['status'] == 'CURRENT_SYNTHETIC_WITNESS_CAPTURED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
