"""Read-only Hex v2.02 SQL intake; represented-coefficient Chebyshev tools.

Never executes SQL. Generic ionf decoder and H1-only availability catalogue are
separate interfaces. Manufactured controls provide no physical-provider evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import lzma
import math
from pathlib import Path
import re
import struct

IONF_COLUMNS = ('ni', 'li', 'mi', 'L', 'S', 'Ei', 'l1', 'l2', 'cheb')
TMAT_COLUMNS = ('ni', 'li', 'mi', 'nf', 'lf', 'mf', 'L', 'S', 'Ei', 'ell', 'Re_T_ell', 'Im_T_ell')
MAX_BYTES = 128 * 1024**2
MAX_STATEMENT = 8 * 1024**2
IDENT = r'(?:"[A-Za-z_][A-Za-z_0-9]*"|\'[A-Za-z_][A-Za-z_0-9]*\'|`[A-Za-z_][A-Za-z_0-9]*`|[A-Za-z_][A-Za-z_0-9]*)'
INSERT = re.compile(r'^INSERT\s+(?:OR\s+REPLACE\s+)?INTO\s+('+IDENT+r')\s*(?:\(([^)]*)\))?\s*VALUES\s*\((.*)\)\s*;?$', re.I | re.S)
TABLE = re.compile(r'^(?:CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?|INSERT\s+(?:OR\s+REPLACE\s+)?INTO\s+)('+IDENT+r')', re.I)
SPECIAL = re.compile(rb"['\"`;#/-]")
NUMBER_PATTERN = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
NUMERIC_LITERAL = re.compile(NUMBER_PATTERN)
NUMERIC_ROW = re.compile(r'\s*'+NUMBER_PATTERN+r'(?:\s*,\s*'+NUMBER_PATTERN+r')*\s*')
HEX_LITERAL = re.compile(r"[xX]'(?:[0-9a-fA-F]{2})*'")


def identifier(token):
    return token.strip().strip('"\'`').lower()


def parse_insert(statement):
    """One literal numeric/BLOB VALUES row, matching the generated Hex SQL."""
    match = INSERT.fullmatch(statement.strip())
    if not match:
        raise ValueError('unsupported INSERT syntax; expected one literal VALUES row')
    table, columns, body = match.groups()
    # Actual source fields are numeric literals or hex BLOB, never expressions.
    tokens = tuple(t.strip() for t in body.split(','))
    if not NUMERIC_ROW.fullmatch(body):
        for token in tokens:
            if not (NUMERIC_LITERAL.fullmatch(token) or HEX_LITERAL.fullmatch(token) or token.upper() == 'NULL'):
                raise ValueError('unsupported or malformed VALUES literal')
    return identifier(table), (tuple(identifier(c) for c in columns.split(',')) if columns else None), tokens


def integer(token):
    if isinstance(token, bool):
        raise ValueError('boolean is not a quantum number')
    if isinstance(token, int):
        return token
    if not isinstance(token, str) or not re.fullmatch(r'[+-]?\d+', token.strip()):
        raise ValueError('quantum number must be an integer literal')
    return int(token)


def finite_real(token):
    if isinstance(token, bool) or not isinstance(token, (str, int, float)):
        raise ValueError('invalid real literal')
    if isinstance(token, str) and not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', token.strip()):
        raise ValueError('invalid real literal')
    value = float(token)
    if not math.isfinite(value):
        raise ValueError('nonfinite real')
    return value


def checked_coefficients(coefficients):
    coefficients = tuple(complex(c) for c in coefficients)
    if not coefficients or any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in coefficients):
        raise ValueError('finite nonempty coefficients required')
    return coefficients


def decode_blob(blob, *, endian, layout):
    """ABI must be declared externally: binary64 pairs (real, imaginary)."""
    if endian not in ('little', 'big') or layout != 'binary64-real-imag':
        raise ValueError('explicit little/big endian and binary64-real-imag layout required')
    if isinstance(blob, str):
        if not re.fullmatch(r"[xX]'(?:[0-9a-fA-F]{2})+'", blob):
            raise ValueError('expected nonempty hexadecimal SQL BLOB')
        blob = bytes.fromhex(blob[2:-1])
    if not isinstance(blob, bytes) or not blob or len(blob) % 16:
        raise ValueError('BLOB must contain a positive multiple of 16 bytes')
    values = tuple(complex(a, b) for a, b in struct.iter_unpack(('<' if endian == 'little' else '>')+'dd', blob))
    checked_coefficients(values)
    return values


@dataclass(frozen=True)
class IonfRow:
    ni: int
    li: int
    mi: int
    L: int
    S: int
    Ei: float
    l1: int
    l2: int
    coefficients: tuple[complex, ...]

    def normalized_coordinate(self, k1):
        """Upstream polynomial argument k1 lies in [0,sqrt(Ei-1/ni²)]."""
        k1 = finite_real(k1)
        high = math.sqrt(self.Ei - 1.0 / self.ni**2)
        if not 0 <= k1 <= high:
            raise ValueError('k1 outside physical polynomial interval')
        return k1 / high


def decode_ionf_row(row, *, endian, layout):
    """Generic source-schema decoder; does not restrict the initial state to H1."""
    if row is None:
        raise ValueError('SOURCE_INPUT_PENDING: ionf row absent')
    if len(row) != 9:
        raise ValueError('ionf requires nine fields in upstream order')
    ni, li, mi, L, S = (integer(v) for v in row[:5])
    Ei = finite_real(row[5])
    l1, l2 = (integer(v) for v in row[6:8])
    if ni < 1 or not 0 <= li < ni or abs(mi) > li or L < 0 or S not in (0, 1) or min(l1, l2) < 0:
        raise ValueError('invalid quantum numbers')
    if not abs(l1-l2) <= L <= l1+l2:
        raise ValueError('final angular momenta cannot couple to L')
    if Ei <= 1.0 / ni**2:
        raise ValueError('incident energy must exceed threshold 1/ni² Ry')
    return IonfRow(ni, li, mi, L, S, Ei, l1, l2, decode_blob(row[8], endian=endian, layout=layout))


def exact_tail(coefficients, m):
    """Exact L1 bound for omitted represented coefficients, m >= 1.

    |T_j(t)| <= 1 on [-1,1]. No floating evaluation or physical uncertainty
    certificate is implied. Components are exact fractions of binary64 values.
    """
    coefficients = checked_coefficients(coefficients)
    if type(m) is not int or not 1 <= m <= len(coefficients):
        raise ValueError('m must retain C0 and not exceed coefficient count')
    return sum((Fraction.from_float(abs(z.real)) + Fraction.from_float(abs(z.imag)) for z in coefficients[m:]), Fraction(0))


def select_terms(coefficients, absolute_tolerance):
    """Smallest prefix satisfying an explicit exact entire-suffix tolerance."""
    coefficients = checked_coefficients(coefficients)
    if isinstance(absolute_tolerance, bool):
        raise ValueError('invalid tolerance')
    if isinstance(absolute_tolerance, float):
        if not math.isfinite(absolute_tolerance):
            raise ValueError('nonfinite tolerance')
        tolerance = Fraction.from_float(absolute_tolerance)
    else:
        tolerance = Fraction(absolute_tolerance)
    if tolerance < 0:
        raise ValueError('negative tolerance')
    suffix, m = Fraction(0), len(coefficients)
    for j in range(len(coefficients)-1, 0, -1):
        z = coefficients[j]
        proposed = suffix + Fraction.from_float(abs(z.real)) + Fraction.from_float(abs(z.imag))
        if proposed > tolerance:
            break
        suffix, m = proposed, j
    return m


def evaluate(coefficients, x, *, m=None):
    """Floating Clenshaw; C0/2 convention, normalized x in [0,1], full default."""
    coefficients = checked_coefficients(coefficients)
    x = finite_real(x)
    if not 0 <= x <= 1:
        raise ValueError('normalized x outside [0,1]')
    m = len(coefficients) if m is None else m
    if type(m) is not int or not 1 <= m <= len(coefficients):
        raise ValueError('invalid retained coefficient count')
    t, b1, b2 = 2*x-1, 0j, 0j
    for c in reversed(coefficients[1:m]):
        b0 = c + 2*t*b1 - b2
        b2, b1 = b1, b0
    return coefficients[0]/2 + t*b1 - b2


class StatementStream:
    """Run-scanning bounded generated-SQL lexer, not a general SQL executor.

    Compiled searches skip ordinary text in bulk; bytes.find skips literal and
    comment runs. Supports #/-- line comments, /* */ comments, quoted literals,
    quoted identifiers and semicolons, including chunk boundaries.
    """
    def __init__(self):
        self.buffer = bytearray()
        self.quote = None
        self.line_comment = False
        self.block_comment = False
        self.carry = b''

    def append(self, run):
        if len(self.buffer) + len(run) > MAX_STATEMENT:
            raise ValueError('statement exceeds bounded parser capacity')
        self.buffer.extend(run)

    def feed(self, chunk):
        chunk = self.carry + chunk
        self.carry = b''
        i, n = 0, len(chunk)
        while i < n:
            if self.line_comment:
                end = chunk.find(b'\n', i)
                if end < 0:
                    return
                self.line_comment, i = False, end+1
                continue
            if self.block_comment:
                end = chunk.find(b'*/', i)
                if end < 0:
                    if chunk.endswith(b'*'):
                        self.carry = b'*'
                    return
                self.block_comment, i = False, end+2
                continue
            if self.quote:
                end = chunk.find(self.quote, i)
                if end < 0:
                    self.append(chunk[i:])
                    return
                self.append(chunk[i:end+1])
                self.quote, i = None, end+1
                continue
            match = SPECIAL.search(chunk, i)
            if not match:
                self.append(chunk[i:])
                return
            end = match.start()
            self.append(chunk[i:end])
            char = chunk[end:end+1]
            i = end+1
            if char in (b'-', b'/'):
                if i == n:
                    self.carry = char
                    return
                pair = chunk[end:end+2]
                if pair == b'--':
                    self.append(b' ')
                    self.line_comment, i = True, end+2
                    continue
                if pair == b'/*':
                    self.append(b' ')
                    self.block_comment, i = True, end+2
                    continue
            if char == b'#':
                self.append(b' ')
                self.line_comment = True
                continue
            self.append(char)
            if char in (b"'", b'"', b'`'):
                self.quote = char
            elif char == b';':
                statement = self.buffer.decode('utf-8').strip()
                self.buffer.clear()
                if statement:
                    yield statement

    def finish(self):
        if self.carry and not self.line_comment and not self.block_comment:
            self.append(self.carry)
        self.carry = b''
        if self.quote or self.block_comment or self.buffer.strip():
            raise ValueError('unterminated SQL statement/literal/comment')


class HashReader:
    def __init__(self, stream):
        self.stream, self.digest, self.count = stream, hashlib.sha256(), 0

    def read(self, size=-1):
        block = self.stream.read(size)
        self.digest.update(block)
        self.count += len(block)
        return block


class HexLinesStream:
    """Explicit upstream hex_import_ getline dialect; one record per line.

    Only literal INSERTs, full-line comments, source transaction markers and
    one-line known-table CREATE TABLE records are admitted. No multiline SQL.
    """
    def __init__(self):
        self.buffer = bytearray()

    def line(self, raw):
        text = raw.decode('utf-8').strip()
        if not text or text.startswith(('#', '--')):
            return None
        if re.match(r'INSERT(?:\s|$)', text, re.I):
            # The catalogue's parse_insert performs the literal/schema check.
            return text
        if re.fullmatch(r'(?:BEGIN(?:\s+TRANSACTION)?|COMMIT|END(?:\s+TRANSACTION)?)\s*;?', text, re.I):
            return text
        match = TABLE.match(text)
        if (text.upper().startswith('CREATE TABLE') and match
                and identifier(match[1]) in ('tmat', 'ionf')
                and text.rstrip(';').rstrip().endswith(')')
                and ';' not in text.rstrip(';')
                and text.count('(') == text.count(')')):
            return text
        raise ValueError('unsupported/multiline hex-lines record')

    def feed(self, chunk):
        parts = chunk.split(b'\n')
        for index, part in enumerate(parts):
            if len(self.buffer)+len(part) > MAX_STATEMENT:
                raise ValueError('line exceeds bounded parser capacity')
            self.buffer.extend(part)
            if index < len(parts)-1:
                statement = self.line(bytes(self.buffer))
                self.buffer.clear()
                if statement is not None:
                    yield statement

    def finish(self):
        if self.buffer:
            statement = self.line(bytes(self.buffer))
            self.buffer.clear()
            if statement is not None:
                yield statement


def catalogue(path, *, max_bytes=MAX_BYTES, dialect='semicolon'):
    """One raw catalogue. Availability decision is specifically H1 initial 100."""
    if not 0 < max_bytes <= MAX_BYTES:
        raise ValueError('invalid decompressed byte cap')
    if dialect not in ('semicolon', 'hex-lines'):
        raise ValueError('unsupported SQL dialect')
    statements, tables, insert_rows = Counter(), Counter(), Counter()
    h1 = {name: {'rows': 0, 'Ei_min_Ry': None, 'Ei_max_Ry': None} for name in ('tmat', 'ionf')}
    parser = StatementStream() if dialect == 'semicolon' else HexLinesStream()
    digest, count = hashlib.sha256(), 0

    def record(statement):
        verb = statement.split(None, 1)[0].upper().rstrip(';')
        statements[verb] += 1
        table_match = TABLE.match(statement)
        if table_match:
            tables[identifier(table_match[1])] += 1
        if verb != 'INSERT':
            return
        table, columns, values = parse_insert(statement)
        insert_rows[table] += 1
        if table not in h1:
            return
        expected = IONF_COLUMNS if table == 'ionf' else TMAT_COLUMNS
        if len(values) != len(expected) or (columns and columns != tuple(c.lower() for c in expected)):
            raise ValueError('unexpected '+table+' source schema')
        if tuple(integer(v) for v in values[:3]) == (1, 0, 0):
            energy = finite_real(values[5 if table == 'ionf' else 8])
            stats = h1[table]
            stats['rows'] += 1
            stats['Ei_min_Ry'] = energy if stats['Ei_min_Ry'] is None else min(energy, stats['Ei_min_Ry'])
            stats['Ei_max_Ry'] = energy if stats['Ei_max_Ry'] is None else max(energy, stats['Ei_max_Ry'])
    with open(path, 'rb') as raw:
        source = HashReader(raw)
        plain = lzma.LZMAFile(source, 'rb') if str(path).endswith('.xz') else source
        try:
            while True:
                block = plain.read(min(65536, max_bytes-count+1))
                if not block:
                    break
                count += len(block)
                if count > max_bytes:
                    raise ValueError('decompressed input exceeds 128 MiB/caller cap')
                digest.update(block)
                for statement in parser.feed(block):
                    record(statement)
            final = parser.finish()
            if final is not None:
                for statement in final:
                    record(statement)
        finally:
            if plain is not source:
                plain.close()
    return {'status': 'RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED' if h1['ionf']['rows'] else 'SOURCE_INPUT_PENDING',
            'input_path': str(Path(path).resolve()), 'dialect': dialect, 'compression': 'xz' if str(path).endswith('.xz') else 'none',
            'compressed_sha256': source.digest.hexdigest(), 'compressed_bytes': source.count,
            'uncompressed_sha256': digest.hexdigest(), 'uncompressed_bytes': count,
            'statement_counts': dict(statements), 'table_statement_counts': dict(tables),
            'insert_row_counts': dict(insert_rows), 'H1_initial_100': h1,
            'ionf_rows': insert_rows['ionf'], 'sql_executed': False,
            'physical_provider_values_inferred': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('sql_path', type=Path)
    ap.add_argument('--dialect', choices=('semicolon', 'hex-lines'), default='semicolon')
    args = ap.parse_args()
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    print(json.dumps(catalogue(args.sql_path, dialect=args.dialect), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
