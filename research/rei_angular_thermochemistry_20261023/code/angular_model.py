"""ANGTHERM01 implementation of the controller's frozen THEORY.md.

Exact source fits are imported; donor models and donor IVPs are never imported.
The full oracle shares only frozen atomic data, geometry, and constitutive fits
with the reduced model. It assembles all isotope/packet events independently.
"""
from __future__ import annotations
import sys
from pathlib import Path
import math
import numpy as np
from scipy.interpolate import CubicHermiteSpline, PchipInterpolator
from scipy.optimize import brentq

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'vendor/c22'))
from atomic_network import AtomicNetwork21, CHANNELS, CHANNEL_NAMES
from rr_energy_moment import rr_energy_factor

KB = 1.380649e-23 / 1.602176634e-19
CT = 1.5 * KB
C = 29979245800.0
SIGMA_T = 6.6524587051e-25  # cm², exact pinned C13 THOMSON_CGS; owner-frozen
END = math.log(7.0)
ENERGIES = np.array([10., 20., 40., 60., 100., 150.])
UV = np.array([.05, .25, .003, .0002, .00001, .000001])
ATOM = AtomicNetwork21(electronic_isotope_equality=True)
CHI = np.array([c['chi_eV'] for c in CHANNELS])
PARAM = np.array([ATOM.provider.rows[k]['RR'] for k in CHANNEL_NAMES])
TOTALS = np.array([1.000025, .08201, 5.0001e-10])
WEIGHTS = np.repeat(TOTALS, [2, 3, 4])
CHARGE = np.array([0, 1, 0, 1, 2, 0, 1, 2, 3.])
VGRAD = WEIGHTS * CHARGE
LOW = np.array([0, 2, 3, 5, 6, 7])
UP = LOW + 1
NN = sum(ATOM.initial_nucleus_totals.values())
BIND9 = np.zeros(9)
for l, u, chi in zip(LOW, UP, CHI):
    BIND9[u] = BIND9[l] + chi
BIND21 = np.zeros(21)
for l, u, ch in ATOM.edges:
    BIND21[u] = BIND21[l] + CHI[ch]
ELEMENT_INDICES = {'H': slice(0, 2), 'He': slice(2, 5), 'Li': slice(5, 9)}


def lift(f):
    """Scaled 21-state lift, retaining structural zero n/T faces."""
    x = np.zeros(21)
    for name, block in ATOM.blocks.items():
        total = ATOM.initial_nucleus_totals[name]
        if total == 0:
            continue
        sl = ELEMENT_INDICES['H' if len(block) == 2 else 'He' if len(block) == 3 else 'Li']
        x[list(block)] = total * f[sl] / ATOM.scales[list(block)]
    return x


def quotient(x, tolerance=1e-13):
    """Reject unequal isotope fractions; never project them onto equality."""
    f = np.zeros(9)
    done = set()
    for name, block in ATOM.blocks.items():
        total = ATOM.initial_nucleus_totals[name]
        if total == 0:
            if np.any(np.asarray(x)[list(block)] != 0):
                raise ValueError('NONZERO_N_T_REQUIRES_NEW_CONTRACT')
            continue
        key = 'H' if len(block) == 2 else 'He' if len(block) == 3 else 'Li'
        frac = ATOM.scales[list(block)] * np.asarray(x)[list(block)] / total
        if key in done and np.max(abs(f[ELEMENT_INDICES[key]] - frac)) > tolerance:
            raise ValueError('ISOTOPE_QUOTIENT_INELIGIBLE')
        f[ELEMENT_INDICES[key]] = frac
        done.add(key)
    return f


def geometry(eta, b, bp, mu0, e0):
    delta = (1-mu0*mu0)*np.expm1(2*b) + mu0*mu0*np.expm1(-4*b)
    logd = .5*np.log1p(delta)
    energy = e0*np.exp(-eta + logd)
    mu = mu0*np.exp(-2*b-logd)
    p2 = (3*mu*mu-1)/2
    return energy, mu, p2, -(1+2*bp*p2)*energy


class Background:
    def __init__(self, case='grid044', sign=1):
        self.case, self.sign = case, sign
        with np.load(BASE/'inputs/background'/f'{case}_history.npz', allow_pickle=False) as d:
            self.eta = d['eta'].copy()
            self.saved_n = d['nH_ref_cm3'].copy()
            self.saved_H = d['H'].copy()
            self.saved_b = d['b'].copy()
            self.saved_bp = d['s']/d['H']
        self.n0 = self.saved_n[0]
        self.bfun = CubicHermiteSpline(self.eta, self.saved_b-self.saved_b[0], self.saved_bp)
        self.hfun = PchipInterpolator(self.eta, np.log(self.saved_H))

    def fields(self, eta):
        return (float(np.exp(self.hfun(eta))), self.n0*np.exp(-3*eta),
                self.sign*float(self.bfun(eta)), self.sign*float(self.bfun(eta, 1)))


def thermal(temp):
    if not np.isfinite(temp) or not 3 <= temp <= 1e9:
        raise ValueError(f'RR_T_DOMAIN: {temp!r}')
    # Exact provider calls; derivatives are closed-form derivatives of this fit.
    alpha = np.array([ATOM.provider.rr(k, temp) for k in CHANNEL_NAMES])
    r0, r1 = np.sqrt(temp/PARAM[:, 2]), np.sqrt(temp/PARAM[:, 3])
    b = PARAM[:, 1]
    dalpha = -.5-.5*(1-b)*r0/(1+r0)-.5*(1+b)*r1/(1+r1)
    factor = np.array([rr_energy_factor(p, temp) for p in PARAM])
    dfactor = -((1-b)*r0/(1+r0)**2+(1+b)*r1/(1+r1)**2)/(4*temp)
    capture = KB*temp*factor
    return alpha, alpha*dalpha/temp, capture, KB*(factor+temp*dfactor)


class Reduced:
    oracle = False
    def __init__(self, M=4, background='grid044', sign=1, zero_uv=False, ionized=False):
        self.M, self.bg = M, Background(background, sign)
        mu, weight = np.polynomial.legendre.leggauss(M)
        self.nodes, self.weights = (mu+1)/2, weight/2
        self.mu0 = np.tile(self.nodes, 6)
        self.e0 = np.repeat(ENERGIES, M)
        self.g0 = (UV[:, None]*self.weights).ravel() * (0 if zero_uv else 1)
        self.J = 6*M
        self.ax, self.gx = slice(0, 9), slice(9, 9+self.J)
        self.iu, self.iesc, self.iwg, self.iwm, self.iws, self.irr, self.iabs, self.itau = range(9+self.J, 17+self.J)
        self.size = 17+self.J
        self.logg0 = np.full(self.J, -np.inf)
        nz = self.g0 > 0
        self.logg0[nz] = np.log(self.g0[nz])
        self.y0 = np.zeros(self.size)
        f = quotient(ATOM.initial_state())
        if ionized:
            f[:] = 0
            f[[1, 4, 8]] = 1
        self.y0[self.ax] = f
        self.y0[self.iu] = CT*(NN+VGRAD@f)*(10000 if ionized else 300)
        self.segment = None
        self._cache = None

    def photons(self, y):
        return np.exp(self.logg0-y[self.gx])

    def temperature(self, y):
        return y[self.iu]/(CT*(NN+VGRAD@y[self.ax]))

    def coefficients(self, eta):
        key = (float(eta), self.segment)
        if self._cache is not None and self._cache[0] == key:
            return self._cache[1]
        h, n, b, bp = self.bg.fields(eta)
        e, mu, p2, ep = geometry(eta, b, bp, self.mu0, self.e0)
        # Cross sections alone may use the segment's one-sided endpoint value.
        # Actual eta energies, directions, and work always retain actual eta.
        esigma = e
        if self.segment is not None:
            lo, hi = self.segment
            if eta == lo or eta == hi:
                toward = hi if eta == lo else lo
                step = min(1e-12, (hi-lo)*1e-8)
                tin = float(eta) + math.copysign(step, toward-eta)
                if tin == eta:
                    tin = np.nextafter(float(eta), toward)
                _, _, bin_, bpin = self.bg.fields(tin)
                esigma = geometry(tin, bin_, bpin, self.mu0, self.e0)[0]
                # nextafter(t) can round to identical E. Move E one ULP toward
                # the exact segment's interior energy only at its endpoint.
                mid = (lo+hi)/2
                _, _, bm, bpm = self.bg.fields(mid)
                em = geometry(mid, bm, bpm, self.mu0, self.e0)[0]
                esigma = np.nextafter(esigma, em)
        sigma = np.array([ATOM.provider.sigma(k, esigma)*1e-18 for k in CHANNEL_NAMES])
        logsigma = np.full_like(sigma, -np.inf)
        np.log(sigma, out=logsigma, where=sigma > 0)
        result = h, n, bp, e, mu, p2, ep, sigma, logsigma
        self._cache = key, result
        return result

    def data(self, eta, y):
        h, n, bp, e, mu, p2, ep, sigma, logsigma = self.coefficients(eta)
        f = y[self.ax]
        v = VGRAD@f
        temp = self.temperature(y)
        alpha, alphaT, cap, capT = thermal(temp)
        ell = self.logg0-y[self.gx]
        # The photon-scaled coefficient is evaluated before population multiply.
        photo_coeff = np.exp(math.log(C*n/h)+logsigma+ell[None, :])
        yp = WEIGHTS[LOW]*f[LOW]
        photo = yp[:, None]*photo_coeff
        rr = (n/h)*v*WEIGHTS[UP]*f[UP]*alpha
        g = np.exp(ell)
        return h, n, bp, e, p2, sigma, f, v, temp, alpha, alphaT, cap, capT, photo_coeff, photo, rr, g

    def rhs(self, eta, y):
        h,n,bp,e,p2,sigma,f,v,temp,alpha,alphaT,cap,capT,coeff,photo,rr,g = self.data(eta,y)
        dy = np.zeros(self.size)
        p = photo.sum(axis=1)
        net = p-rr
        dy[LOW] -= net/WEIGHTS[LOW]
        dy[UP] += net/WEIGHTS[UP]
        dy[self.gx] = C*n/h*((WEIGHTS[LOW]*f[LOW])@sigma)
        dy[self.iu] = -2*y[self.iu] + np.sum((e[None,:]-CHI[:,None])*photo) - cap@rr
        dy[self.iesc] = (CHI+cap)@rr
        dy[self.iwg] = 2*y[self.iu]
        dy[self.iwm] = e@g
        dy[self.iws] = 2*bp*((e*p2)@g)
        dy[self.irr], dy[self.iabs] = rr.sum(), p.sum()
        dy[self.itau] = C*SIGMA_T*n/h*v
        return dy

    def jacobian(self, eta, y):
        h,n,bp,e,p2,sigma,f,v,temp,alpha,alphaT,cap,capT,coeff,photo,rr,g = self.data(eta,y)
        j = np.zeros((self.size,self.size))
        dt = np.zeros(self.size)
        dt[:9] = -temp*VGRAD/(NN+v)
        dt[self.iu] = 1/(CT*(NN+v))
        dp = np.zeros((6,self.size))
        dp[np.arange(6),LOW] = WEIGHTS[LOW]*coeff.sum(axis=1)
        dp[:,self.gx] = -photo
        dr = np.outer(n/h*WEIGHTS[UP]*f[UP]*alpha, np.r_[VGRAD,np.zeros(self.size-9)])
        dr[np.arange(6),UP] += n/h*v*WEIGHTS[UP]*alpha
        dr += np.outer(n/h*v*WEIGHTS[UP]*f[UP]*alphaT, dt)
        dn = dp-dr
        j[LOW] -= dn/WEIGHTS[LOW,None]
        j[UP] += dn/WEIGHTS[UP,None]
        j[self.gx,LOW] = (C*n/h*sigma*WEIGHTS[LOW,None]).T
        heatgrad = np.zeros(self.size)
        heatgrad[LOW] = WEIGHTS[LOW]*np.sum((e[None,:]-CHI[:,None])*coeff,axis=1)
        heatgrad[self.gx] = -np.sum((e[None,:]-CHI[:,None])*photo,axis=0)
        j[self.iu] = heatgrad-cap@dr-(capT@rr)*dt
        j[self.iu,self.iu] -= 2
        j[self.iesc] = (CHI+cap)@dr+(capT@rr)*dt
        j[self.iwg,self.iu] = 2
        j[self.iwm,self.gx] = -e*g
        j[self.iws,self.gx] = -2*bp*e*p2*g
        j[self.irr] = dr.sum(axis=0)
        j[self.iabs] = dp.sum(axis=0)
        j[self.itau,:9] = C*SIGMA_T*n/h*VGRAD
        return j

    def boundaries(self):
        result = [0., END]
        crossings = []
        for ray,(e0,mu0) in enumerate(zip(self.e0,self.mu0)):
            def ef(t):
                _,_,b,bp = self.bg.fields(t)
                return float(geometry(t,b,bp,mu0,e0)[0])
            for chi in list(CHI)+[64.39]:
                if ef(0)>chi and ef(END)<chi:
                    t = brentq(lambda x:ef(x)-chi,0,END,xtol=5e-16,rtol=9e-16)
                    result.append(t)
                    crossings.append({'ray':ray,'initial_energy_eV':float(e0),'mu0':float(mu0),'threshold_eV':float(chi),'eta':t,'energy_at_root_eV':ef(t)})
        self.crossings = crossings
        return sorted(set(result))

    def observables(self, eta, Y):
        f = Y[self.ax]
        x = np.stack([lift(fi) for fi in f.T],axis=1)
        g = np.exp(self.logg0[:,None]-Y[self.gx])
        return common_observables(self,eta,Y,x,g, f)


class FullOracle(Reduced):
    """Independent 21-state / 48M direct-count event oracle."""
    oracle = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        old = self.y0.copy()
        self.mu0 = np.repeat(self.mu0,8)*np.tile([1,1,1,1,-1,-1,-1,-1],self.J)
        self.phi = np.tile(np.arange(4)*np.pi/2,2*self.J)
        self.e0 = np.repeat(self.e0,8)
        self.g0 = np.repeat(self.g0/8,8)
        self.J *= 8
        self.ax, self.gx = slice(0,21),slice(21,21+self.J)
        self.iu,self.iesc,self.iwg,self.iwm,self.iws,self.irr,self.iabs,self.itau = range(21+self.J,29+self.J)
        self.size = 29+self.J
        self.y0 = np.zeros(self.size)
        self.y0[self.ax], self.y0[self.gx] = lift(old[:9]),self.g0
        self.y0[self.iu] = old[-8]
        self._cache = None

    def photons(self,y):
        return y[self.gx]

    def temperature(self,y):
        return y[self.iu]/(CT*(NN+ATOM.q@(ATOM.scales*y[self.ax])))

    def rhs(self,eta,y):
        h,n,bp,e,mu,p2,ep,sigma,_ = self.coefficients(eta)
        physical = ATOM.scales*y[self.ax]
        v = ATOM.q@physical
        alpha,_,cap,_ = thermal(self.temperature(y))
        photons = y[self.gx]
        dy = np.zeros(self.size)
        dy[self.iu] = -2*y[self.iu]
        dy[self.iwg] = 2*y[self.iu]
        dy[self.iwm] = e@photons
        dy[self.iws] = 2*bp*((e*p2)@photons)
        # All per-isotope/per-packet events assembled here, independently.
        for lower,upper,ch in ATOM.edges:
            absorption = (C*n/h)*physical[lower]*sigma[ch]*photons
            rr = (n/h)*v*physical[upper]*alpha[ch]
            total = absorption.sum()
            net = total-rr
            dy[lower] -= net/ATOM.scales[lower]
            dy[upper] += net/ATOM.scales[upper]
            dy[self.gx] -= absorption
            dy[self.iu] += (e-CHI[ch])@absorption-cap[ch]*rr
            dy[self.iesc] += (CHI[ch]+cap[ch])*rr
            dy[self.irr] += rr
            dy[self.iabs] += total
        dy[self.itau] = C*SIGMA_T*n/h*v
        return dy

    def boundaries(self):
        # +/- and azimuth copies have exactly shared threshold times.
        olde, oldmu = self.e0, self.mu0
        self.e0,self.mu0 = olde[::8],oldmu[::8]
        try:
            return super().boundaries()
        finally:
            self.e0,self.mu0 = olde,oldmu

    def observables(self,eta,Y):
        x = Y[self.ax]
        f = np.vstack((x[list(ATOM.blocks['H1'])],x[list(ATOM.blocks['He4'])],x[list(ATOM.blocks['Li7'])]))
        return common_observables(self,eta,Y,x,Y[self.gx],f)


def common_observables(model,eta,Y,x,g,f):
    energies, p2s, bps, hs, ns = [],[],[],[],[]
    for t in eta:
        h,n,b,bp = model.bg.fields(t)
        e,mu,p2,ep = geometry(t,b,bp,model.mu0,model.e0)
        energies.append(e);p2s.append(p2);bps.append(bp);hs.append(h);ns.append(n)
    e,p2 = np.array(energies).T,np.array(p2s).T
    physical = ATOM.scales[:,None]*x
    v = ATOM.q@physical
    uv = np.sum(e*g,axis=0)
    Q = np.sum(e*g*p2,axis=0)
    total = Y[model.iu]+BIND21@physical+uv+sum(Y[k] for k in [model.iesc,model.iwg,model.iwm,model.iws])
    photons = np.sum(g,axis=0)
    energy_scale = abs(total[0])
    count_scale = max(float(np.sum(model.g0)),float(v[0]))
    nucleus = np.zeros(len(eta))
    for name,block in ATOM.blocks.items():
        initial = ATOM.initial_nucleus_totals[name]
        values = np.sum(physical[list(block)],axis=0)
        if initial:
            nucleus = np.maximum(nucleus,abs(values-initial)/initial)
        elif not model.oracle and np.any(values != 0):
            raise ArithmeticError('ZERO_N_T_FACE_CHANGED')
    zero_ids=list(ATOM.blocks['n'])+list(ATOM.blocks['T'])
    zero_face_scaled_max_abs=float(np.max(abs(x[zero_ids])))
    if model.oracle and zero_face_scaled_max_abs>64*np.finfo(float).eps:
        raise ArithmeticError('ZERO_FACE_NUMERICAL_ROUNDOFF_LIMIT_EXCEEDED')
    r = {'eta':np.array(eta),'Y':Y,'fractions':f,'atomic_scaled':x,'photon_groups':g,
         'photon_log_counts': np.log(model.g0,where=model.g0>0,out=np.full_like(model.g0,-np.inf))[:,None]-Y[model.gx] if not model.oracle else np.log(g,where=g>0,out=np.full_like(g,-np.inf)),
         'temperature_K':Y[model.iu]/(CT*(NN+v)),'electron_per_Href':v,'photon_per_Href':photons,
         'UV_energy':uv,'Q':Q,'U':Y[model.iu],'Eesc':Y[model.iesc],'Wgas':Y[model.iwg],
         'Wmean':Y[model.iwm],'Wshear':Y[model.iws],'CRR':Y[model.irr],'Cabs':Y[model.iabs],
         'tauT':Y[model.itau],'energy_total':total,'energy_residual':(total-total[0])/energy_scale,
         'charge_residual':(v+Y[model.irr]-Y[model.iabs]-v[0])/count_scale,
         'photon_residual':(photons+Y[model.iabs]-photons[0])/count_scale,
         'nucleus_residual':nucleus,'energy_scale_eV_per_Href':np.array(energy_scale),
         'count_scale_per_Href':np.array(count_scale),'bprime':np.array(bps),'H':np.array(hs),'nHref':np.array(ns),
         'zero_face_scaled_max_abs':np.array(zero_face_scaled_max_abs)}
    return r
