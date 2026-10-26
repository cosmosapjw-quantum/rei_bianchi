"""Isolated saved-background source projection; no atomic provider or IVP.

Draft API follows the theory worker's specified covariant-cell transform.
Scientific execution is bound separately to the frozen input contract.
"""
import hashlib
import math
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline, PchipInterpolator

KB_EV_K = 1.380649e-23 / 1.602176634e-19


@lru_cache(None)
def _rule(order):
    return np.polynomial.legendre.leggauss(order)


def gauss(order, lo, hi):
    nodes, weights = _rule(order)
    return lo+(nodes+1.)*(hi-lo)/2., weights*(hi-lo)/2.


class SavedBackground:
    """Read the actual donor arrays, preserving its declared interpolants."""
    def __init__(self, path, expected_sha256, expected_shapes):
        path = Path(path)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            raise ValueError('DONOR_INPUT_BYTE_IDENTITY_MISMATCH')
        self.sha256 = actual
        with np.load(path, allow_pickle=False) as data:
            arrays = {name: np.array(data[name],copy=True) for name in expected_shapes}
        for name, shape in expected_shapes.items():
            if list(arrays[name].shape) != list(shape) or not np.all(np.isfinite(arrays[name])):
                raise ValueError('DONOR_FIELD_SHAPE_OR_FINITE_DOMAIN: '+name)
        self.arrays = arrays
        self.eta = arrays['eta']
        H, b, s = arrays['H'], arrays['b'], arrays['s']
        if np.any(np.diff(self.eta) <= 0) or np.any(H <= 0):
            raise ValueError('INVALID_DONOR_TIME_OR_H')
        self.logH = PchipInterpolator(self.eta,np.log(H),extrapolate=False)
        self.shear = CubicHermiteSpline(self.eta,b-b[0],s/H,extrapolate=False)

    def fields(self, eta):
        eta = np.asarray(eta,dtype=float)
        if not np.all(np.isfinite(eta)) or np.any(eta < self.eta[0]) or np.any(eta > self.eta[-1]):
            raise ValueError('QUERY_OUTSIDE_DONOR_DOMAIN')
        return np.exp(self.logH(eta)), self.shear(eta), self.shear(eta,1)

    def nHref_cm3(self, eta):
        self.fields(eta)  # declared-domain check
        return self.arrays['nH_ref_cm3'][0]*np.exp(-3.*np.asarray(eta))

    def clock_integrals(self, lo, hi, sources, order):
        if not self.eta[0] <= lo <= hi <= self.eta[-1]:
            raise ValueError('CLOCK_INTERVAL_OUTSIDE_DONOR')
        cuts = np.r_[lo,self.eta[(self.eta > lo)&(self.eta < hi)],hi]
        elapsed, source_integrals = [], {s['name']:[] for s in sources}
        for left,right in zip(cuts[:-1],cuts[1:]):
            if right <= left:
                continue
            eta, weights = gauss(order,float(left),float(right))
            H = self.fields(eta)[0]
            elapsed.append(float(weights@(1./H)))
            for source in sources:
                source_integrals[source['name']].append(float(weights@(source_rate(eta,source)/H)))
        return {'proper_elapsed_s':math.fsum(elapsed),
                'source_counts_per_Href':{k:math.fsum(v) for k,v in source_integrals.items()}}


def raw_spectrum(energy, source):
    energy = np.asarray(energy,dtype=float)
    if source['spectrum'] == 'blackbody_photon_number':
        return energy**2/np.expm1(energy/(KB_EV_K*source['temperature_K']))
    if source['spectrum'] == 'cutoff_power_law':
        return (energy/source['pivot_energy_eV'])**source['power_index']*np.exp(-energy/source['cutoff_energy_eV'])
    raise ValueError('UNCONTRACTED_SOURCE_SPECTRUM')


def source_rate(eta, source):
    z = 21.*np.exp(-np.asarray(eta))-1.
    envelope = .5*(1.+np.tanh((source['z_on']-z)/source['delta_z']))
    return source['amplitude_per_Href_s']*source['escape_fraction']*envelope


def spectral_moments(source, support, order, spectral_splits):
    cuts = sorted(set([*support]+[v for v in spectral_splits if support[0] < v < support[1]]))
    numbers, energies = [], []
    for left,right in zip(cuts[:-1],cuts[1:]):
        E, weights = gauss(order,left,right)
        shape = raw_spectrum(E,source)
        numbers.append(float(weights@shape))
        energies.append(float(weights@(E*shape)))
    number,energy = math.fsum(numbers),math.fsum(energies)
    if not number > 0 or not math.isfinite(number+energy):
        raise ValueError('UNREPRESENTABLE_SPECTRAL_NORMALIZATION')
    return {'normalizer_eV_units':number,'mean_energy_eV':energy/number}


def _angular_cuts(lo, hi, Qlo, Qhi, support, radial_perp2, radial_parallel2):
    """Split where either compact-support endpoint crosses a radial face."""
    cuts = {lo,hi}
    slope = radial_parallel2-radial_perp2
    if slope != 0:
        for Qface in (Qlo,Qhi):
            if Qface == 0 or not math.isfinite(Qface):
                continue
            for endpoint in support:
                nu2 = ((endpoint/Qface)**2-radial_perp2)/slope
                if 0 < nu2 < 1:
                    nu = math.sqrt(nu2)
                    if lo < nu < hi:
                        cuts.add(nu)
    return sorted(cuts)


def project_snapshot(background, eta, sources, support, Q_edges, nu_edges,
                     angular_order, energy_order, normalization_order, spectral_splits):
    """Instantaneous number/energy column; Q tail is a separate owned row."""
    Q_edges, nu_edges = np.asarray(Q_edges,float), np.asarray(nu_edges,float)
    if (not np.all(np.isfinite(Q_edges)) or not np.all(np.isfinite(nu_edges)) or
            Q_edges[0] != 0 or nu_edges[0] != 0 or nu_edges[-1] != 1 or
            np.any(np.diff(Q_edges) <= 0) or np.any(np.diff(nu_edges) <= 0)):
        raise ValueError('INVALID_FIXED_COVARIANT_GRID')
    H,b,bprime = map(float,background.fields(eta))
    aperp,apar,V = math.exp(eta-b),math.exp(eta+2*b),math.exp(3*eta)
    rperp2,rpar2 = aperp**-2,apar**-2
    radial_cells = list(zip(Q_edges[:-1],Q_edges[1:]))+[(Q_edges[-1],math.inf)]
    output = {}
    energy_nodes, energy_weights = _rule(energy_order)
    for source in sources:
        moments = spectral_moments(source,support,normalization_order,spectral_splits)
        Z = moments['normalizer_eV_units']
        rate = float(source_rate(eta,source))
        number,energy = np.zeros((len(radial_cells),len(nu_edges)-1)),np.zeros((len(radial_cells),len(nu_edges)-1))
        for i,(Qlo,Qhi) in enumerate(radial_cells):
            for j,(nulo,nuhi) in enumerate(zip(nu_edges[:-1],nu_edges[1:])):
                cuts = _angular_cuts(nulo,nuhi,Qlo,Qhi,support,rperp2,rpar2)
                pieces_N,pieces_U = [],[]
                for left,right in zip(cuts[:-1],cuts[1:]):
                    nu,nuw = gauss(angular_order,left,right)
                    R = np.sqrt(rperp2+(rpar2-rperp2)*nu*nu)
                    Elo = np.maximum(support[0],Qlo*R)
                    Ehi = np.minimum(support[1],Qhi*R)
                    width = np.maximum(0.,Ehi-Elo)
                    E = Elo[:,None]+(energy_nodes[None,:]+1.)*width[:,None]/2.
                    shape = raw_spectrum(E,source)
                    radial_N = (shape@energy_weights)*width/2.
                    radial_U = ((E*shape)@energy_weights)*width/2.
                    factor = 1./(Z*V*R**3)
                    pieces_N.append(float(nuw@(radial_N*factor)))
                    pieces_U.append(float(nuw@(radial_U*factor)))
                number[i,j],energy[i,j] = rate*math.fsum(pieces_N),rate*math.fsum(pieces_U)
        output[source['name']] = {'number_rate_per_Href_s':number[:-1].tolist(),
                                  'energy_rate_eV_per_Href_s':energy[:-1].tolist(),
                                  'tail_number_rate_per_Href_s':number[-1].tolist(),
                                  'tail_energy_rate_eV_per_Href_s':energy[-1].tolist(),
                                  'total_number_rate_per_Href_s':float(np.sum(number)),
                                  'total_energy_rate_eV_per_Href_s':float(np.sum(energy)),
                                  'escaped_source_rate_per_Href_s':rate,
                                  'spectral_moments':moments}
    additive_keys = ['number_rate_per_Href_s','energy_rate_eV_per_Href_s',
                     'tail_number_rate_per_Href_s','tail_energy_rate_eV_per_Href_s',
                     'total_number_rate_per_Href_s','total_energy_rate_eV_per_Href_s']
    total = {key:np.sum([np.asarray(v[key]) for v in output.values()],axis=0).tolist()
             for key in additive_keys}
    return {'eta':eta,'H_per_s':H,'b':b,'bprime':bprime,'a_perp_over_ref':aperp,
            'a_parallel_over_ref':apar,'relative_volume':V,'Q_edges_eV':Q_edges.tolist(),
            'nHref_cm3':float(background.nHref_cm3(eta)),
            'physical_scale_factor':math.exp(eta)/21.,
            'nu_edges':nu_edges.tolist(),'sources':output,'total':total,
            'projection':'continuous instantaneous source column; no birth-time atoms or evolved photons'}


def amplitude_jvp(snapshot, sources, amplitude_direction):
    """Exact prescribed-source derivative; cells and tail remain separate."""
    keys = ['number_rate_per_Href_s','energy_rate_eV_per_Href_s',
            'tail_number_rate_per_Href_s','tail_energy_rate_eV_per_Href_s']
    out = {}
    for key in keys:
        pieces = []
        for source in sources:
            A = source['amplitude_per_Href_s']
            if A <= 0:
                raise ValueError('POSITIVE_BASE_AMPLITUDE_REQUIRED_FOR_C_OVER_A_JVP')
            pieces.append(np.asarray(snapshot['sources'][source['name']][key])/A*
                          amplitude_direction[source['name']])
        out[key] = np.sum(pieces,axis=0).tolist()
    return out


def gas_state_jacobian(snapshot):
    """Prescribed source has exactly zero derivative for all nine fractions."""
    return {key:np.zeros(np.asarray(value).shape+(9,)).tolist()
            for key,value in next(iter(snapshot['sources'].values())).items()
            if key in ['number_rate_per_Href_s','energy_rate_eV_per_Href_s',
                       'tail_number_rate_per_Href_s','tail_energy_rate_eV_per_Href_s']}
