"""Source-bound intake of the author-distributed HM12 radiation tables.

Contract: preserve every native row, units, zeros and one-sided spectral jumps;
reject extrapolation; provide positive interpolation and analytic moments of
that interpolation.  The tables do NOT solve Bianchi radiation transfer.

Interpolation is linear in the tabulated ordinate, in ln(E/eV), and in z.
Unequal ordinates at duplicate native wavelengths are retained as zero-width
jumps.  At an exact jump, ``values(..., side='right')`` means the high-energy
limit, and ``side='left'`` means the low-energy limit.  This declared numerical
closure is nonnegative including native zeros; no log(ordinate), floor,
averaging of duplicate rows, or extrapolation is used.  Moments are exact for
this piecewise-linear closure up to floating-point roundoff, not exact HM12
continuum integrals.  Row counts come from the bytes, not header assertions.

With J_nu in erg s^-1 cm^-2 Hz^-1 sr^-1 and comoving epsilon_nu in
erg s^-1 Mpc^-3 Hz^-1, the angle-integrated proper quantities per d ln E are

    n_log = 4 pi J_nu / (c h)                 [cm^-3],
    s_log = epsilon_nu (1+z)^3 / (Mpc^3 h)    [cm^-3 s^-1].

J_nu is an initial/background photon field, NOT the emissivity source.
The comoving/proper conversion uses a=(1+z)^-1 with a(today)=1.  Importing
these FLRW-based author histories into a prescribed Bianchi model is a separate
model assumption that the consuming calculation must state explicitly.

Provenance: upstream URLs and immutable byte hashes are checked against the
adjacent sources/acquisition.json by load_hm12(); provenance() exposes the
verified identity, units, domain, native dimensions and interpolation choice.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Literal

import numpy as np

C_CM_S = 2.99792458e10
H_ERG_S = 6.62607015e-27
EV_ERG = 1.602176634e-12
# IAU parsec convention: one AU / tan(1 arcsec) is NOT used; pc = 648000 AU/pi.
MPC_CM = 648000.0 / math.pi * 149597870700.0 * 100.0 * 1.0e6
HC_EV_ANGSTROM = H_ERG_S * C_CM_S / EV_ERG * 1.0e8

Kind = Literal["uvb", "emissivity"]
NATIVE_UNITS = {
    "uvb": "erg s^-1 cm^-2 Hz^-1 sr^-1",
    "emissivity": "erg s^-1 Mpc^-3 Hz^-1 (comoving)",
}
HEADER_UNITS = {"uvb": "ergs/s/cm^2/Hz/sr", "emissivity": "ergs/s/Mpc^3/Hz"}


def _readonly(values: np.ndarray) -> np.ndarray:
    result = np.array(values, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class HM12Table:
    """One independently sampled native table; arrays retain wavelength order."""

    kind: Kind
    redshifts: np.ndarray
    wavelengths_A: np.ndarray
    spectra: np.ndarray  # shape (native wavelength rows, redshift columns)
    source_name: str = "manufactured"
    source_sha256: str | None = None
    source_url: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in NATIVE_UNITS:
            raise ValueError(f"Unknown table kind: {self.kind!r}")
        z, w, f = map(_readonly, (self.redshifts, self.wavelengths_A, self.spectra))
        if z.ndim != 1 or len(z) < 2 or not np.all(np.isfinite(z)):
            raise ValueError("Need at least two finite redshift nodes")
        if np.any(z < 0) or np.any(np.diff(z) <= 0):
            raise ValueError("Redshifts must be nonnegative and strictly increasing")
        if w.ndim != 1 or len(w) < 2 or not np.all(np.isfinite(w)):
            raise ValueError("Need at least two finite wavelength rows")
        if np.any(w <= 0) or np.any(np.diff(w) < 0) or w[0] == w[-1]:
            raise ValueError("Wavelengths must be positive and nondecreasing, with nonzero domain")
        if f.shape != (len(w), len(z)) or not np.all(np.isfinite(f)) or np.any(f < 0):
            raise ValueError("Spectra must be finite, nonnegative, and have native (wavelength,z) shape")
        object.__setattr__(self, "redshifts", z)
        object.__setattr__(self, "wavelengths_A", w)
        object.__setattr__(self, "spectra", f)

    @classmethod
    def read(cls, path: str | Path, kind: Kind, *, expected_sha256: str | None = None,
             source_url: str | None = None) -> "HM12Table":
        path = Path(path)
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {path.name}")
        body = raw.decode("ascii")
        if kind not in HEADER_UNITS or HEADER_UNITS[kind] not in body:
            raise ValueError("Header does not identify the requested native units")
        rows = []
        for lineno, line in enumerate(body.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                rows.append([float(item) for item in line.split()])
            except ValueError as exc:
                raise ValueError(f"Invalid numeric field at line {lineno}") from exc
        if len(rows) < 3:
            raise ValueError("Table has insufficient data rows")
        nredshift = len(rows[0])
        if any(len(row) != nredshift + 1 for row in rows[1:]):
            raise ValueError("Native wavelength rows have inconsistent column counts")
        data = np.array(rows[1:], dtype=float)
        return cls(kind, np.array(rows[0]), data[:, 0], data[:, 1:], path.name, digest, source_url)

    @property
    def energies_eV(self) -> np.ndarray:
        """Ascending energy nodes, including both sides of native jumps."""
        return _readonly(HC_EV_ANGSTROM / self.wavelengths_A[::-1])

    def _z_profile(self, z: float) -> np.ndarray:
        if not np.isscalar(z) or not np.isfinite(z):
            raise ValueError("z must be a finite scalar")
        if z < self.redshifts[0] or z > self.redshifts[-1]:
            raise ValueError("Redshift extrapolation is forbidden")
        index = int(np.searchsorted(self.redshifts, z, side="left"))
        if self.redshifts[index] == z:
            return self.spectra[::-1, index]
        fraction = (z - self.redshifts[index - 1]) / (self.redshifts[index] - self.redshifts[index - 1])
        return ((1.0 - fraction) * self.spectra[::-1, index - 1]
                + fraction * self.spectra[::-1, index])

    def _checked_energies(self, energies_eV: np.ndarray | float) -> np.ndarray:
        energy = np.asarray(energies_eV, dtype=float)
        native = self.energies_eV
        if not np.all(np.isfinite(energy)) or np.any(energy <= 0):
            raise ValueError("Energies must be finite and positive")
        if np.any(energy < native[0]) or np.any(energy > native[-1]):
            raise ValueError("Energy extrapolation is forbidden")
        return energy

    def values(self, energies_eV: np.ndarray | float, z: float, *, side: str = "right") -> np.ndarray | float:
        """Return native-unit J_nu or comoving epsilon_nu at specified energies."""
        if side not in ("left", "right"):
            raise ValueError("side must be left or right, in increasing energy order")
        energy = self._checked_energies(energies_eV)
        native = self.energies_eV
        profile = self._z_profile(z)
        flat = energy.ravel()
        lower = np.searchsorted(native, flat, side="right") - 1
        exact = native[lower] == flat
        out = np.empty_like(flat)
        exact_indices = np.searchsorted(native, flat[exact], side=side)
        if side == "right":
            exact_indices -= 1
        out[exact] = profile[exact_indices]
        indices = lower[~exact]
        fraction = np.log(flat[~exact] / native[indices]) / np.log(native[indices + 1] / native[indices])
        out[~exact] = (1.0 - fraction) * profile[indices] + fraction * profile[indices + 1]
        result = out.reshape(energy.shape)
        return float(result) if result.ndim == 0 else result

    def proper_photon_factor(self, z: float) -> float:
        """Native ordinate to proper angle-integrated photons per ln E.

        For uvb the result unit is cm^-3, for emissivity cm^-3 s^-1.
        This method validates z even though the uvb conversion is z-independent.
        """
        self._z_profile(z)
        if self.kind == "uvb":
            return 4.0 * math.pi / (C_CM_S * H_ERG_S)
        return (1.0 + z) ** 3 / (MPC_CM ** 3 * H_ERG_S)

    def photon_number_log(self, energies_eV: np.ndarray | float, z: float, *, side: str = "right"):
        """Initial/background n_log in cm^-3; rejects an emissivity table."""
        if self.kind != "uvb":
            raise ValueError("Photon number IC must use the UVB table, not emissivity")
        return self.values(energies_eV, z, side=side) * self.proper_photon_factor(z)

    def photon_emission_log(self, energies_eV: np.ndarray | float, z: float, *, side: str = "right"):
        """Proper s_log in cm^-3 s^-1; rejects a background-intensity table."""
        if self.kind != "emissivity":
            raise ValueError("Photon source must use the emissivity table, not UVB")
        return self.values(energies_eV, z, side=side) * self.proper_photon_factor(z)

    def moment(self, lower_eV: float, upper_eV: float, z: float, *, power: float = 0.0,
               reference_eV: float = 1.0, proper_photons: bool = False) -> float:
        """Integrate ordinate(E,z) (E/reference_eV)^power d ln E.

        Every native nonzero-width segment is integrated analytically; clipping
        a segment at either bound performs an exact threshold split. Jumps have
        zero measure. With proper_photons=True the units are cm^-3 (UVB) or
        cm^-3 s^-1 (emissivity). Multiply a power=1, reference_eV=1 moment by
        EV_ERG to obtain the corresponding energy density or source power.
        Power=-3, reference_eV=threshold is useful for E^-3 cross sections;
        no atomic cross section or physical threshold is selected by this API.
        """
        self._checked_energies(np.array([lower_eV, upper_eV]))
        profile = self._z_profile(z)
        if upper_eV < lower_eV:
            raise ValueError("Integration bounds must be increasing")
        if not np.isfinite(power) or not np.isfinite(reference_eV) or reference_eV <= 0:
            raise ValueError("Moment power must be finite and reference energy positive")
        if upper_eV == lower_eV:
            return 0.0
        native = self.energies_eV
        terms = []
        for i in range(len(native) - 1):
            left, right = max(lower_eV, native[i]), min(upper_eV, native[i + 1])
            if right <= left:  # Includes native zero-width jumps.
                continue
            width = math.log(native[i + 1] / native[i])
            t0 = math.log(left / native[i]) / width
            t1 = math.log(right / native[i]) / width
            f0 = (1.0 - t0) * profile[i] + t0 * profile[i + 1]
            f1 = (1.0 - t1) * profile[i] + t1 * profile[i + 1]
            dx = math.log(right / left)
            w0, w1 = _exponential_linear_weights(power * dx)
            terms.append(dx * math.exp(power * math.log(left / reference_eV)) * (f0 * w0 + f1 * w1))
        result = math.fsum(terms)
        if proper_photons:
            result *= self.proper_photon_factor(z)
        if not math.isfinite(result):
            raise FloatingPointError("Non-finite moment; requested power exceeds numeric range")
        return result

    def group_moments(self, edges_eV: np.ndarray, z: float, **kwargs) -> np.ndarray:
        """Moments in adjacent groups; explicit threshold edges cannot be skipped."""
        edges = np.asarray(edges_eV, dtype=float)
        if edges.ndim != 1 or len(edges) < 2 or np.any(np.diff(edges) <= 0):
            raise ValueError("Group edges must be a strictly increasing one-dimensional array")
        return np.array([self.moment(float(a), float(b), z, **kwargs) for a, b in zip(edges[:-1], edges[1:])])

    def provenance(self) -> dict:
        adjacent_equal = np.diff(self.wavelengths_A) == 0
        different_values = np.any(self.spectra[:-1] != self.spectra[1:], axis=1)
        return {
            "file": self.source_name, "sha256": self.source_sha256, "url": self.source_url,
            "kind": self.kind, "native_units": NATIVE_UNITS[self.kind],
            "native_shape_wavelength_redshift": list(self.spectra.shape),
            "redshift_domain": [float(self.redshifts[0]), float(self.redshifts[-1])],
            "energy_domain_eV": [float(self.energies_eV[0]), float(self.energies_eV[-1])],
            "duplicate_wavelength_pairs": int(np.count_nonzero(adjacent_equal)),
            "unequal_duplicate_pairs": int(np.count_nonzero(adjacent_equal & different_values)),
            "zero_ordinates": int(np.count_nonzero(self.spectra == 0)),
            "interpolation": "linear ordinate in ln(E/eV) and z; native one-sided jumps preserved",
            "exact_jump_default": "high-energy limit", "extrapolation": "forbidden",
            "claim": "source-bound table intake; exact moments of declared interpolation only",
        }


def _exponential_linear_weights(q: float) -> tuple[float, float]:
    """Integrals of (1-u)exp(q u), u exp(q u) for u=0..1.

    Stable analytic power series near zero avoids subtractive cancellation.
    Its omitted terms are below double-precision roundoff for |q|<0.5.
    """
    if abs(q) < 0.5:
        term, w0, w1 = 1.0, 0.0, 0.0
        for k in range(24):
            w0 += term / ((k + 1) * (k + 2))
            w1 += term / (k + 2)
            term *= q / (k + 1)
        return w0, w1
    expm1 = math.expm1(q)
    return (expm1 - q) / (q * q), (q * math.exp(q) - expm1) / (q * q)


def load_hm12(source_dir: str | Path | None = None) -> dict[str, HM12Table]:
    """Read both author tables independently and verify the acquisition hashes."""
    source_dir = Path(source_dir) if source_dir is not None else Path(__file__).parent / "sources"
    entries = json.loads((source_dir / "acquisition.json").read_text())
    indexed = {entry["file"]: entry for entry in entries}
    if len(indexed) != len(entries):
        raise ValueError("Duplicate filenames in acquisition manifest")
    tables = {}
    for kind, name in (("uvb", "UVB.out"), ("emissivity", "emissivity.out")):
        entry = indexed[name]
        path = source_dir / name
        if path.stat().st_size != entry["size"]:
            raise ValueError(f"Byte-size mismatch for {name}")
        tables[kind] = HM12Table.read(path, kind, expected_sha256=entry["sha256"], source_url=entry["url"])
    return tables


if __name__ == "__main__":
    print(json.dumps({name: table.provenance() for name, table in load_hm12().items()}, indent=2))
