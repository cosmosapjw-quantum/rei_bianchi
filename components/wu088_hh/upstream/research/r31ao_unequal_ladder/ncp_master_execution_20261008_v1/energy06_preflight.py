"""Source-bound preflight only: never issues roots or consumes a dispatch registry."""
from fractions import Fraction
from pathlib import Path
import hashlib, re, math

OWNER_SHA = '8322d79609cc535b046b6000dd27bfdfd8859ddbffb5c3adac90ba396d6d2718'
HH_OWNER_SHA = 'f47958a8e185ab02cd7d6c00cb7760be583eb769147ca4ed04ef7b1404e87830'

class LinkRefused(ValueError):
    pass


def owner_birth_measure(source: Path, hh_source: Path, t0: float, dt: float):
    if not math.isfinite(t0) or not math.isfinite(dt) or t0 < 0 or dt < 1000 or t0 + dt > 1e13:
        raise LinkRefused('ENERGY06_CLOCK')
    data, hh_data = source.read_bytes(), hh_source.read_bytes()
    if hashlib.sha256(data).hexdigest() != OWNER_SHA or hashlib.sha256(hh_data).hexdigest() != HH_OWNER_SHA:
        raise LinkRefused('ENERGY06_OWNER_SOURCE_IDENTITY')
    text, hh = data.decode('utf-8'), hh_data.decode('utf-8')
    # Values and call order belong to the pinned owner, not to this adapter.
    constant = re.search(r'const SOURCE: f64 = ([0-9.eE+-]+);', text)
    expected = ['let source_n=dt*SOURCE;', 'let (full,a1,l1)=endpoint(c,h,s,dt,&nodes)?;',
                'let (half,a2,l2)=endpoint(c,h,s,dt/2.0,&nodes)?;',
                'let (two,a3,l3)=endpoint(c,h,&half,dt/2.0,&nodes)?;']
    hh_expected = ['let source_n=dt*SOURCE;', 'hh_endpoint_state(c,s,dt,&nodes)?;',
                   'hh_endpoint_state(c,s,dt/2.0,&nodes)?;',
                   'hh_endpoint_state(c,&half,dt/2.0,&nodes)?;']
    if constant is None or any(x not in text for x in expected) or any(x not in hh for x in hh_expected):
        raise LinkRefused('OWNER_SOURCE_SEMANTICS_NOT_BOUND')
    rate = float(constant.group(1))
    if not math.isfinite(rate) or rate <= 0:
        raise LinkRefused('OWNER_SOURCE_RATE')
    half_dt = dt / 2.0
    t1, t2 = t0 + half_dt, t0 + dt
    t2_half = t1 + half_dt
    if Fraction(half_dt) * 2 != Fraction(dt) or t2_half != t2 or t1 <= t0 or t2 <= t1:
        raise LinkRefused('ENERGY06_CLOCK_ROUNDING')
    # Exact values of the actual binary64 source_n products, not decimal fits.
    full = [(Fraction(t2), Fraction(dt * rate))]
    halves = [(Fraction(t1), Fraction(half_dt * rate)),
              (Fraction(t2_half), Fraction(half_dt * rate))]
    return full, halves


def require_energy05_macro(source: Path, hh_source: Path, t0: float, dt: float):
    full, halves = owner_birth_measure(source, hh_source, t0, dt)
    if full or halves:
        raise LinkRefused('ENERGY05_NO_BIRTH_OWNER_BIRTH_MISMATCH')
    raise LinkRefused('ENERGY06_PAIRED_DEFECT_PROOF_NOT_ISSUED')
