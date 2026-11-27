"""Exact-real interpretation of the sealed FT03 + LCS scalar source stage.

Every float literal and recorded input is interpreted as its exact binary64
value. Transcendentals are mathematical real functions enclosed by Arb.
This is not a replay of native per-operation binary64 rounding.
"""
import json
from pathlib import Path
from flint import arb


def f64(value):
    return arb(float(value))


class FrozenSource:
    def __init__(self, path, h_s=1250000000, source_scale=5e-15):
        self.data = json.loads(Path(path).read_text())
        d = self.data
        self.nh = f64(d['n_h_cm3'])
        self.nhe = f64(d['n_he_cm3'])
        self.r = self.nhe/self.nh
        self.hubble = f64(d['h_mean_per_s'])
        self.c = f64(29979245800.0)
        self.kb = f64(1.380649e-16)
        self.ev = f64(1.602176634e-12)
        self.chi = list(map(f64, [13.598434599702, 24.587389011, 54.41776]))
        self.h = arb(h_s)
        self.sstar = f64(source_scale)
        if any(sig[1] != 0 or sig[2] != 0 for sig in d['sigma_cm2']):
            raise ValueError('source extends beyond the inherited HI-only photon support')
        self.active = [j for j, sig in enumerate(d['sigma_cm2']) if sig[0] != 0]
        self.inert = [j for j, sig in enumerate(d['sigma_cm2']) if sig[0] == 0]
        self.varied = d['varied_energy_index']
        if self.varied not in self.active:
            raise ValueError('injected photon is not on the inherited active support')
        self.A = [self.c*self.nh*f64(d['sigma_cm2'][j][0]) for j in self.active]
        self.excess = [f64(d['energies_ev'][j])-self.chi[0] for j in self.active]
        self.initial = list(map(f64, d['old_gas'])) + [f64(d['old_point_photons'][j]) for j in self.active]
        self.names = ['x_HII','y_HeII','y_HeIII','w_eV_per_H']+[f'P_{j}' for j in self.active]

    def thermal(self, z):
        x, y1, y2, w = z[:4]
        pi = 1+self.r+x+self.r*(y1+2*y2)
        return 2*self.ev*w/(3*self.kb*pi), pi

    def coefficients(self, t):
        rr, kinetic, ci = [], [], []
        for a, (L, a0, p, cc, r0, d0) in enumerate(zip(
            [315614.,570670.,1263030.], [21.11,32.38,19.95],
            [-1.089,-1.146,-1.089], [.354,.416,.553],
            [.874,.987,.735], [1.101,1.056,1.275])):
            ell = f64(L)/t
            if a == 1:
                alpha = f64(3e-14)*ell**f64(.654)
                slope = f64(-.654)
            else:
                u = (ell/f64(.522))**f64(.470)
                pref = 2 if a == 2 else 1
                alpha = pref*f64(1.269e-13)*ell**f64(1.503)/(1+u)**f64(1.923)
                slope = f64(-1.503)+f64(1.923)*f64(.470)*u/(1+u)
            rr.append(alpha)
            kinetic.append(self.kb*t*alpha*(f64(1.5)+slope)/self.ev)
            beta = f64(a0)*t**f64(-1.5)*(-ell/2).exp()*ell**f64(p)/(1+(ell/f64(cc))**f64(r0))**f64(d0)
            ci.append(beta)
        dr_a = f64(1.54e-9)*f64(11605.)**f64(1.5)
        b1 = f64(40.49664394833662)*f64(11605.)
        b2 = f64(8.099328789667)*f64(11605.)
        dr = [dr_a*t**f64(-1.5)*(-b1/t).exp(),
              f64(.3)*dr_a*t**f64(-1.5)*(-(b1+b2)/t).exp()]
        dre = [self.kb*b1/self.ev, self.kb*(b1+b2)/self.ev]
        return rr, kinetic, ci, dr, dre

    def rhs(self, z, lam, source):
        """dz/dtau, tau=t/h, source=S/Sstar; includes full gas feedback."""
        x, y1, y2, w = z[:4]
        t, pi = self.thermal(z)
        ne = self.nh*x+self.nhe*(y1+2*y2)
        alpha, kinetic, beta, dr, dre = self.coefficients(t)
        low = [1-x, 1-y1-y2, y1]
        high = [x, y1, y2]
        nuc = [arb(1), self.r, self.r]
        ci = [low[a]*ne*beta[a] for a in range(3)]
        rr = [high[a]*ne*alpha[a] for a in range(3)]
        j = [ci[a]-rr[a] for a in range(3)]
        dr_events = [y1*ne*v for v in dr]
        j[1] = j[1]-sum(dr_events)
        du = -sum(nuc[a]*(self.chi[a]*ci[a]+high[a]*ne*kinetic[a]) for a in range(3))
        du = du-self.r*sum(v*e for v,e in zip(dr_events,dre))-2*self.hubble*w
        q = self.nh*(1-x)**2*f64(1.2e-17)*t**f64(1.2)*(-f64(157800.)/t).exp()
        ph = [a*(1-x)*p for a,p in zip(self.A,z[4:])]
        photo = sum(ph)
        dx = j[0]+photo+lam*q
        du = du+sum(v*e for v,e in zip(ph,self.excess))-self.chi[0]*lam*q
        pdot = [-rate + (source*self.sstar if original == self.varied else 0)
                for rate,original in zip(ph,self.active)]
        return [self.h*v for v in [dx,j[1]-j[2],j[2],du]+pdot]

    def leading(self):
        z = self.initial
        t, pi = self.thermal(z)
        neutral = 1-z[0]
        k = f64(1.2e-17)*t**f64(1.2)*(-f64(157800.)/t).exp()
        q = self.nh*neutral**2*k
        nu = f64(1.2)+f64(157800.)/t
        g = self.excess[self.active.index(self.varied)]
        tgamma = 2*self.ev*g/(3*self.kb)
        xi = neutral/pi*nu*(1-tgamma/t)
        a = self.A[self.active.index(self.varied)]
        coefficient = -self.sstar*a*q*(4+xi)*self.h**3/6
        return {'temperature_K':t,'Tgamma_K':tgamma,'Xi':xi,'q_per_s':q,
                'A_per_s':a,'c3_normalized':coefficient}
