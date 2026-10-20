#!/usr/bin/env python3
"""New BR06 recovery R1 Decimal source; deleted original bytes were not recovered.

Closed-form scalar controls and J_jk references at exact binary64 input points.
This module computes reference values; it is not a rigorous interval solver.
"""
from __future__ import annotations
import argparse
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import time

VERSION = 'BR06_THEORY_RECOVERY_R1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def point(value):
    """Exactly the binary64 value represented by the input token."""
    return Decimal.from_float(float(value))


def phi(z):
    if z < 0:
        raise ValueError('nonnegative optical depth required')
    if not z:
        return Decimal(1)
    if z <= Decimal('0.5'):
        term = total = Decimal(1)
        for n in range(1, 10000):
            term *= -z / Decimal(n + 1)
            new = total + term
            if new == total:
                return total
            total = new
        raise ArithmeticError('Phi series work limit')
    return (Decimal(1) - (-z).exp()) / z


def j_jk(z, j, k):
    if z < 0 or j < 0 or k < 0 or j > 2 or k > 2:
        raise ValueError('J_jk domain: z>=0, 0<=j,k<=2')
    if z <= 1:
        term = Decimal(math.factorial(j) * math.factorial(k)) / Decimal(math.factorial(j + k + 1))
        total = term
        for m in range(1, 10000):
            term *= -z * Decimal(j + m) / Decimal(m * (j + k + m + 1))
            new = total + term
            if new == total:
                return total
            total = new
        raise ArithmeticError('J series work limit')
    ez = (-z).exp()
    def monomial(n):
        polynomial = sum((z ** m / Decimal(math.factorial(m)) for m in range(n + 1)), Decimal(0))
        return Decimal(math.factorial(n)) * (Decimal(1) - ez * polynomial) / z ** (n + 1)
    return sum((Decimal((-1) ** m * math.comb(k, m)) * monomial(j + m) for m in range(k + 1)), Decimal(0))


def normalized_inverse(z, u):
    if not z:
        return u
    # The omitted term is O(z^3); below this threshold it is beyond 400 digits.
    if z < Decimal('1e-150'):
        return u + z * u * (u - 1) / 2 + z*z*u*(1-3*u+2*u*u)/6
    return -(1 - u * z * phi(z)).ln() / z


def scalar_controls(precision=400):
    rows = []
    with localcontext() as ctx:
        ctx.prec = precision
        ctx.Emin = -999999999999999999
        ctx.Emax = 999999999999999999
        E0, h, T = point(60), point(.01), point(1)
        for token in ('0', '1e-320', '1e-300', '1e-100', '1e-20', '1e-8', '1'):
            base = point(token)
            rates = [base * q for q in (1, 2, 3, 4)]
            total_rate = sum(rates)
            tau = total_rate * T
            P = (-tau).exp()
            count_absorbed = tau * phi(tau)
            species = [q * T * phi(tau) for q in rates]
            attenuation = phi((total_rate + h) * T)
            absorbed_energy = total_rate * E0 * T * attenuation
            work = -h * E0 * T * attenuation
            surviving_energy = E0 * (-(total_rate+h)*T).exp()
            nr = P + sum(species) - 1
            er = surviving_energy + absorbed_energy - E0 - work
            if any(q < 0 for q in species) or count_absorbed < 0 or P < 0:
                raise AssertionError('negative scalar measure')
            if abs(nr) > Decimal('1e-390') or abs(er) > Decimal('1e-390'):
                raise AssertionError('closed scalar ledger mismatch')
            rows.append({
                'base_rate_token': token,
                'exact_binary64_base_rate': str(base),
                'tau': str(tau),
                'survival': str(P),
                'absorbed': str(count_absorbed),
                'species_events': list(map(str, species)),
                'surviving_energy_ev': str(surviving_energy),
                'absorbed_energy_ev': str(absorbed_energy),
                'work_ev': str(work),
                'number_residual': str(nr),
                'energy_residual_ev': str(er),
                'inverse_fractions': {str(u): str(normalized_inverse(tau, u)) for u in map(Decimal, ('0.1', '0.5', '0.9'))}
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    rows = scalar_controls()
    receipt = {
        'version': VERSION,
        'status': 'PASS_FRESH_EXECUTION_SCALAR_CLOSED_FORMS',
        'historical_pass_inherited': False,
        'source_reconstruction': 'New recovery implementation from retained formulas; not byte-identical restoration of deleted source',
        'scope': 'Seven analytic constant-hazard, exponentially redshifting single-birth controls; no native gas or Rust execution is inferred',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'precision_decimal_digits': 400,
        'python': platform.python_version(),
        'wall_s': time.perf_counter() - start,
        'source_sha256': sha(__file__),
        'cases': len(rows),
        'rows': rows
    }
    out = args.output / 'SCALAR_ORACLES_RECOVERY_R1.json'
    out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'cases': len(rows), 'output': str(out), 'sha256': sha(out), 'wall_s': receipt['wall_s']}))


if __name__ == '__main__':
    main()
