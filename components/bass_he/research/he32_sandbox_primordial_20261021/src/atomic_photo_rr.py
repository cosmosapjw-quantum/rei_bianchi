"""Six source-pinned photo/RR pairs for an isotope-resolved EoR pilot.

Order: H I, He I, He II, Li I, Li II, Li III.  Photon number spectrum is
proportional to E**(-2.5) on [5.392, 60] eV.  uv_amplitude is Gamma_HI [s^-1].
Atomic isotope shifts, CI, DR, molecules, and negative ions are outside this
explicit photo/RR closure.  Coefficients depend on electronic element, not A.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

CHANNELS = ("HI", "HeI", "HeII", "LiI", "LiII", "LiIII")
UV_MIN_EV = 5.392
UV_MAX_EV = 60.0
UV_PHOTON_NUMBER_INDEX = 2.5
EV_J = 1.602176634e-19
C_CM_S = 29979245800.0


class AtomicPhotoRR:
    def __init__(self, data_path: str | Path | None = None, quadrature_order: int = 128):
        if data_path is None:
            data_path = Path(__file__).resolve().parents[1]/"data"/"ATOMIC_PHOTO_RR.json"
        payload = Path(data_path).read_bytes()
        data = json.loads(payload)
        self.data_sha256 = hashlib.sha256(payload).hexdigest()
        rows = data["rows"]
        if tuple(r["label"] for r in rows) != CHANNELS:
            raise ValueError("source table ordering differs from the six-pair contract")
        self.photo = np.array([r["photo_parameters_E0_sigma0Mb_ya_P_yw_y0_y1"] for r in rows])
        self.rr = np.array([r["rr_parameters_a_cm3_s_b_T0_K_T1_K"] for r in rows])
        self.thresholds = np.array([r["photo_threshold_eV"] for r in rows])
        self.photo_max = np.array([r["photo_max_eV"] for r in rows])
        if UV_MAX_EV > min(self.photo_max):
            raise ValueError("UV support exceeds a source photo-fit validity bound")
        if not isinstance(quadrature_order, int) or quadrature_order < 16:
            raise ValueError("quadrature_order must be an integer >= 16")
        nodes, weights = leggauss(quadrature_order)
        integrals = []
        for i, threshold in enumerate(self.thresholds):
            lo, hi = max(UV_MIN_EV, threshold), UV_MAX_EV
            if lo >= hi:
                integrals.append(0.0)
                continue
            energy = .5*(hi+lo)+.5*(hi-lo)*nodes
            integral = .5*(hi-lo)*np.dot(weights, energy**(-UV_PHOTON_NUMBER_INDEX)*self.sigma_mb(i, energy))*1e-18
            integrals.append(float(integral))
        self.integrals_cm2_evpower = np.array(integrals)
        self.photo_ratios = self.integrals_cm2_evpower/self.integrals_cm2_evpower[0]
        for a in (self.photo, self.rr, self.thresholds, self.photo_max,
                  self.integrals_cm2_evpower, self.photo_ratios):
            a.flags.writeable = False
        self.metadata = dict(schema="he32.atomic_photo_rr.v1", channels=CHANNELS,
            data_sha256=self.data_sha256, UV_support_eV=[UV_MIN_EV, UV_MAX_EV],
            photon_number_power_index=UV_PHOTON_NUMBER_INDEX,
            amplitude_definition="Gamma_HI_s_inverse", quadrature_order=quadrature_order,
            temperature_domain_K=data["temperature_domain_K"],
            photo_ratios_relative_HI=self.photo_ratios.tolist(),
            rr_case=data["rr_case"], isotope_policy="elemental electronic equality",
            closure="single photoionization plus total radiative recombination")

    def sigma_mb(self, channel: int, energy_eV):
        """Verner et al. 1996 Eq.(1), in Mb; below threshold returns zero."""
        if not 0 <= channel < 6:
            raise ValueError("unknown atomic channel")
        energy = np.asarray(energy_eV, dtype=float)
        if np.any(~np.isfinite(energy)) or np.any(energy <= 0):
            raise ValueError("positive finite photon energy required")
        if np.any(energy > self.photo_max[channel]):
            raise ValueError("photo-fit upper energy bound exceeded")
        e0, s0, ya, p, yw, y0, y1 = self.photo[channel]
        x = energy/e0-y0
        y = np.sqrt(x*x+y1*y1)
        # Only evaluate fitted expression on physical support, avoiding y=0
        # singular algebra below thresholds even if that output would be masked.
        active = energy >= self.thresholds[channel]
        ys = np.where(active, y, 1.)
        result = s0*((x-1)**2+yw*yw)*ys**(p/2-5.5)*(1+np.sqrt(ys/ya))**(-p)
        return np.where(active, result, 0.)

    def rates(self, T_K: float, uv_amplitude: float):
        if not math.isfinite(T_K) or not 3 <= T_K <= 1e9:
            raise ValueError("VF1996 total-RR temperature domain is 3..1e9 K")
        if not math.isfinite(uv_amplitude) or uv_amplitude < 0:
            raise ValueError("Gamma_HI amplitude must be finite and nonnegative")
        a, b, t0, t1 = self.rr.T
        x = np.sqrt(T_K/t0)
        recombination = a/(x*(1+x)**(1-b)*(1+np.sqrt(T_K/t1))**(1+b))
        return dict(ionization_per_s=uv_amplitude*self.photo_ratios,
                    recombination_cm3_s=recombination,
                    thresholds_eV=self.thresholds,
                    metadata=self.metadata)

    def uv_energy_density_J_m3(self, uv_amplitude: float):
        """Isotropic prescribed UV energy density, no extrapolated spectrum."""
        if not math.isfinite(uv_amplitude) or uv_amplitude < 0:
            raise ValueError("Gamma_HI amplitude must be finite and nonnegative")
        energy_integral = 2*(UV_MIN_EV**(-.5)-UV_MAX_EV**(-.5))
        normalization = uv_amplitude/self.integrals_cm2_evpower[0]
        return normalization*energy_integral/C_CM_S*EV_J*1e6


@lru_cache(maxsize=1)
def default_provider():
    return AtomicPhotoRR()


def rates(T_K: float, uv_amplitude: float):
    return default_provider().rates(T_K, uv_amplitude)
