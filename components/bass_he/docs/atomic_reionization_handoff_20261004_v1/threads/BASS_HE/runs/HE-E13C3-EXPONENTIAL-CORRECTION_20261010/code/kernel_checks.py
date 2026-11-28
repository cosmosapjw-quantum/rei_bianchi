"""Focused numerical checks of the actual E13C3 kernels, no physical solve."""
from decimal import Decimal, localcontext
import argparse
import importlib.util
import json
from pathlib import Path
import numpy as np


def main(root, output):
    path = root / 'code/exponential_correction.py'
    spec = importlib.util.spec_from_file_location('tested_correction', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    LD = np.longdouble
    checks = []
    def record(name, error, tolerance='1e-17'):
        checks.append({'name': name, 'absolute_error': str(error),
                       'tolerance': tolerance, 'pass': bool(error <= LD(tolerance))})
    def dj(a, h):
        with localcontext() as ctx:
            ctx.prec = 90
            aa, hh = Decimal(str(a)), Decimal(str(h))
            return LD(str(hh if not aa else -( (-aa*hh).exp()-1)/aa))
    for a, h in [('0','0'),('0','0.25'),('1e-30','0.25'),
                 ('1','0.25'),('2','0.5'),('100000','1')]:
        a, h = LD(a), LD(h)
        record(f'J_decimal_a={a}_h={h}', abs(m.J(a,h)-dj(a,h)))
        for t in [LD(0), LD('0.25'), LD('0.75'), LD(1)]:
            u = h*t
            rem = h-u
            w = np.exp(-a*rem)
            k0 = m.J(a,rem)
            ke = np.exp(-u)*m.J(a+1,rem)
            record(f'number_kernel_a={a}_h={h}_t={t}', abs(w+a*k0-1))
            record(f'energy_kernel_a={a}_h={h}_t={t}',
                   abs(np.exp(-h)*w+(a+1)*ke-np.exp(-u)))
    for a,h in [(-1,1),(1,-1)]:
        rejected = False
        try:
            m.J(a,h)
        except ValueError:
            rejected = True
        checks.append({'name': f'negative_kernel_argument_{a}_{h}', 'pass': rejected})

    class ConstantBatch:
        count = 3
        h = np.array(['0.5','1e-6','0'], dtype=LD)
        Lf = np.array(['0','2e6','2'], dtype=LD)
        e0 = np.ones(3, dtype=LD)
        lf = np.array([Lf/2, Lf/4, Lf/4])
        qf = np.array(['0.03','0.01','0'], dtype=LD)
        f0 = np.array(['0.1','0.1','0.1'], dtype=LD)
        def coeff(self, t):
            return self.lf, self.qf, self.e0*np.exp(-self.h*t)
        def frozen_stock(self, t):
            return self.f0*np.exp(-self.Lf*self.h*t)+self.qf*m.J(self.Lf,self.h*t)
    batch = ConstantBatch()
    for order in (8,12):
        zero, _, _ = m.correction(batch, np.zeros(3,dtype=LD), order)
        checks.append({'name': f'constant_coeff_zero_incoming_GL{order}',
                       'pass': bool(np.array_equal(zero,np.zeros_like(zero)))})
        ea = np.full(3,LD('1e-12'))
        end, _, _ = m.correction(batch,ea,order)
        ref_p, ref_i0, ref_ie = [], [], []
        for a,h in zip(batch.Lf,batch.h):
            with localcontext() as ctx:
                ctx.prec=90
                ref_p.append(LD(str((-Decimal(str(a))*Decimal(str(h))).exp())))
            ref_i0.append(dj(a,h))
            ref_ie.append(dj(a+1,h))
        record(f'constant_incoming_damping_GL{order}',max(abs(end[0]/ea-ref_p)))
        record(f'constant_incoming_energy_moment_GL{order}',max(abs(end[13]/ea-ref_ie)))
        expected = batch.lf*np.array(ref_i0,dtype=LD)*ea
        record(f'constant_incoming_species_GL{order}',max(abs((end[4:7]-expected)/ea).flat))
    passed = all(x['pass'] for x in checks)
    m.write_json(output, {'status':'PASS' if passed else 'FAIL',
                         'checks':checks, 'total':len(checks),
                         'passed':sum(x['pass'] for x in checks),
                         'producer_sha256':m.digest(__file__),
                         'tested_code_sha256':m.digest(path),
                         'scope':'actual primary kernels and synthetic constant coefficients only',
                         'old_suites_rerun':0,'physical_runs':0})
    if not passed:
        raise SystemExit(1)
    print(json.dumps({'status':'PASS','checks':len(checks)}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    main(args.root.resolve(),args.output.resolve())
