"""Content-pinned H/He electron donor for the existing proper-cm^-3 API.

Interpolation is PCHIP of comoving electron number versus ln(a). The
uniform-knot scalar fast path uses prepared polynomial coefficients;
no source files or scipy interpolator are called in an ODE RHS.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
from scipy.interpolate import PchipInterpolator

SCHEMA = "he31.hhe_electron_donor.v1"
INTERPOLATION = "pchip_comoving_ne_in_ln_a_v1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
C_CGS = 2.99792458e10
SIGMA_T_CM2 = 6.6524587051e-25  # original PR147, not a replacement constant
GAMMA_PER_NE = C_CGS * SIGMA_T_CM2
NUCLEUS_RTOL = 1e-9
CENSUS_RTOL = 1e-10


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def immutable(values):
    array = np.ascontiguousarray(values, dtype=np.float64)
    return np.frombuffer(array.tobytes(), dtype=np.float64).reshape(array.shape)


@dataclass(frozen=True, eq=False)
class ElectronDonor:
    """Immutable physical table; scalar and vector ``density(a)`` return cm^-3."""

    _a: np.ndarray
    _x: np.ndarray
    _c: np.ndarray
    _comoving_ne: np.ndarray
    _dx: float | None
    _identity: str
    _metadata_json: bytes
    _nH0: float
    _nHe0: float
    _nucleus_drift: float
    _census_error: float | None

    @classmethod
    def from_arrays(cls, *, a, nH, nHe, xHII, xHeII, xHeIII,
                    density_unit, density_frame, provenance, ne_reference=None):
        if density_unit not in ("cm^-3", "m^-3"):
            raise ValueError("density_unit must explicitly be cm^-3 or m^-3")
        if density_frame not in ("proper", "comoving_a3"):
            raise ValueError("density_frame must be proper or comoving_a3")
        if not isinstance(provenance, dict) or not provenance.get("closure"):
            raise ValueError("source closure/provenance is required")
        if provenance.get("kind") not in ("actual_history", "manufactured_control"):
            raise ValueError("explicit actual_history or manufactured_control kind required")
        if not SHA256.fullmatch(str(provenance.get("source_sha256", ""))):
            raise ValueError("the source bytes must have an explicit SHA256")
        vals = [np.asarray(v, dtype=np.float64) for v in
                (a, nH, nHe, xHII, xHeII, xHeIII)]
        aa, hh, he, xh, xhe2, xhe3 = vals
        if aa.ndim != 1 or len(aa) < 2 or any(v.shape != aa.shape for v in vals):
            raise ValueError("all six columns must be equal-length one-dimensional arrays")
        if any(not np.isfinite(v).all() for v in vals):
            raise ValueError("nonfinite donor column")
        if np.any(aa <= 0) or np.any(np.diff(aa) <= 0):
            raise ValueError("scale factor must be positive and strictly increasing")
        if np.any(hh <= 0) or np.any(he < 0):
            raise ValueError("positive H and nonnegative He nuclei are required")
        if (np.any(xh < 0) or np.any(xh > 1) or np.any(xhe2 < 0)
                or np.any(xhe3 < 0) or np.any(xhe2 + xhe3 > 1)):
            raise ValueError("ionic fractions violate the H/He simplex")
        unit_scale = 1. if density_unit == "cm^-3" else 1e-6
        volume_scale = aa**3 if density_frame == "proper" else np.ones_like(aa)
        NH, NHe = hh * unit_scale * volume_scale, he * unit_scale * volume_scale
        H0, He0 = float(NH[0]), float(NHe[0])
        drift_H = float(np.max(abs(NH / H0 - 1)))
        drift_He = (float(np.max(abs(NHe / He0 - 1))) if He0 > 0
                    else (0. if np.all(NHe == 0) else math.inf))
        drift = max(drift_H, drift_He)
        if drift > NUCLEUS_RTOL:
            raise ValueError("donor nuclei are not conserved as a^-3 in this homogeneous contract")
        # The conserved first-row nuclei define the interpolated model.
        # Measured drift is reported rather than silently fitting a new abundance.
        comoving = H0 * xh + He0 * (xhe2 + 2*xhe3)
        census_error = None
        if ne_reference is not None:
            reference = np.asarray(ne_reference, dtype=np.float64)
            if (reference.shape != aa.shape or not np.isfinite(reference).all()
                    or np.any(reference < 0)):
                raise ValueError("invalid reference electron column")
            reference_comoving = reference * unit_scale * volume_scale
            scale = np.maximum(np.maximum(abs(comoving), abs(reference_comoving)),
                               (H0 + 2*He0) * 1e-12)
            census_error = float(np.max(abs(reference_comoving-comoving) / scale))
            if census_error > CENSUS_RTOL:
                raise ValueError("electron column disagrees with H/He ionic census")
        xx = np.log(aa)
        if np.any(np.diff(xx) <= 0):
            raise ValueError("scale-factor knots are indistinguishable in ln(a)")
        coeff = PchipInterpolator(xx, comoving, extrapolate=False).c
        dx = np.diff(xx)
        uniform = float(dx[0]) if np.allclose(dx, dx[0], rtol=2e-10, atol=0.) else None
        metadata = dict(schema=SCHEMA, interpolation=INTERPOLATION,
                        density_unit=density_unit, density_frame=density_frame,
                        provenance=provenance, nucleus_rtol=NUCLEUS_RTOL,
                        census_rtol=CENSUS_RTOL, endpoint_roundoff_ulps=8,
                        constants=dict(c_cgs=C_CGS, sigma_T_cm2=SIGMA_T_CM2))
        identity = hashlib.sha256(canonical_bytes(metadata))
        for v in vals:
            identity.update(np.ascontiguousarray(v, dtype="<f8").tobytes())
        if ne_reference is not None:
            identity.update(np.ascontiguousarray(ne_reference, dtype="<f8").tobytes())
        return cls(immutable(aa), immutable(xx), immutable(coeff), immutable(comoving),
                   uniform, identity.hexdigest(), canonical_bytes(metadata),
                   H0, He0, drift, census_error)

    @classmethod
    def load(cls, manifest_path):
        path = Path(manifest_path)
        manifest = json.loads(path.read_text())
        if manifest.get("schema") != SCHEMA or manifest.get("interpolation") != INTERPOLATION:
            raise ValueError("unsupported donor schema/interpolation")
        name = manifest.get("data_file")
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError("donor data_file must be a sibling basename")
        data = path.parent / name
        expected = manifest.get("data_sha256", "")
        if not SHA256.fullmatch(str(expected)) or sha256_file(data) != expected:
            raise ValueError("donor data SHA256 mismatch")
        with np.load(data, allow_pickle=False) as table:
            required = ("a", "nH", "nHe", "xHII", "xHeII", "xHeIII")
            extra = set(table.files) - set(required) - {"ne_reference"}
            if extra or not set(required).issubset(table.files):
                raise ValueError("unexpected or missing donor columns")
            donor = cls.from_arrays(**{k: table[k] for k in required},
                density_unit=manifest["density_unit"], density_frame=manifest["density_frame"],
                provenance=manifest["provenance"],
                ne_reference=table["ne_reference"] if "ne_reference" in table.files else None)
        if donor.identity != manifest.get("identity_sha256"):
            raise ValueError("donor metadata/content identity mismatch")
        return donor

    @property
    def identity(self):
        return self._identity

    @property
    def support(self):
        return float(self._a[0]), float(self._a[-1])

    @property
    def metadata(self):
        return json.loads(self._metadata_json)

    def require_support(self, a_start, a_end):
        if not (math.isfinite(a_start) and math.isfinite(a_end) and 0 < a_start < a_end):
            raise ValueError("positive ordered integration interval required")
        self._bounded_scalar(a_start)
        self._bounded_scalar(a_end)

    def _bounded_scalar(self, a):
        a = float(a)
        lo, hi = self.support
        if (not math.isfinite(a) or a <= 0 or a < lo-8*math.ulp(lo)
                or a > hi+8*math.ulp(hi)):
            raise ValueError("electron donor queried outside its physical support")
        return min(hi, max(lo, a))

    def density(self, a):
        if np.ndim(a) == 0:
            aa = self._bounded_scalar(a)
            x = math.log(aa)
            index = (int(math.floor((x-self._x[0])/self._dx)) if self._dx is not None
                     else int(np.searchsorted(self._x, x, side="right")-1))
            index = min(len(self._x)-2, max(0, index))
            if x < self._x[index] or x > self._x[index+1]:
                # Almost-uniform knots and binary64 logarithms can put a
                # floor estimate beside the actual interval at a knot.
                index = min(len(self._x)-2, max(0, int(np.searchsorted(self._x, x, side="right")-1)))
            u = x-self._x[index]
            c = self._c[:, index]
            value = ((c[0]*u+c[1])*u+c[2])*u+c[3]
            # Shape-preserving polynomial plus final binary64 roundoff only.
            if value < -16*np.finfo(float).eps*(self._nH0+2*self._nHe0):
                raise FloatingPointError("negative interpolated comoving electrons")
            return float(max(0., value)/(aa*aa*aa))
        aa = np.asarray(a, dtype=np.float64)
        lo, hi = self.support
        if (not np.isfinite(aa).all() or np.any(aa <= 0)
                or np.any(aa < lo-8*math.ulp(lo)) or np.any(aa > hi+8*math.ulp(hi))):
            raise ValueError("electron donor queried outside its physical support")
        aa = np.clip(aa, lo, hi)
        x = np.log(aa)
        index = np.clip(np.searchsorted(self._x, x, side="right")-1, 0, len(self._x)-2)
        u = x-self._x[index]
        coeff = self._c[:, index]
        value = ((coeff[0]*u+coeff[1])*u+coeff[2])*u+coeff[3]
        if np.any(value < -16*np.finfo(float).eps*(self._nH0+2*self._nHe0)):
            raise FloatingPointError("negative interpolated comoving electrons")
        return np.maximum(value, 0.)/aa**3

    def rate(self, a):
        return GAMMA_PER_NE*self.density(a)

    def report(self):
        lo, hi = self.support
        return dict(identity_sha256=self.identity, rows=len(self._a),
                    a_start=lo, a_end=hi, z_start=1/lo-1, z_end=1/hi-1,
                    nH0_cm3=self._nH0, nHe0_cm3=self._nHe0,
                    nucleus_relative_drift=self._nucleus_drift,
                    census_relative_error=self._census_error,
                    zero_knots=int(np.count_nonzero(self._comoving_ne == 0)),
                    uniform_ln_a_scalar_index=self._dx is not None,
                    prepared_array_bytes=sum(a.nbytes for a in
                                             (self._a,self._x,self._c,self._comoving_ne)),
                    **self.metadata)
