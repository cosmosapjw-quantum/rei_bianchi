#!/usr/bin/env python3
"""New postloss source: finite-birth/GL8, prescribed-gas optical-layer response.

This is not a reconstruction of the lost RUN15 enclosure kernel.  It never
calls GasServer or solve_ivp.  Archived RUN13 checkpoint gas is used to define
a PCHIP path; its difference from the true IVP path remains unbounded here.
Only the first owner-cell energy distribution is integrated continuously.
Numerical core quadrature and the conditional analytic tail bound are reported
separately.  Binary64 extrema padding is not directed-rounding certification.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
import time

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np
import scipy
from numpy.polynomial import Polynomial
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

H_FIT = 13.6
H_BINDING = 13.598434599702
D_GATE = 13.602134599702
CELL_HI = H_FIT * (24.59 / H_FIT) ** (1.0 / 16.0)
# Operation order of the actual owner_src/axbi_sources.rs source shape.
KT_EV = 1.380649e-16 / 1.602176634e-12 * 50000.0
C_M_S = 299792458.0
EXTREMA_PAD = 2.0e-11
CORE_OPTICAL_CUTOFF = 32.0
SCHEMA = "rei.run15.postloss.fixed_gas_optical_response.v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number_shape(energy):
    energy = np.asarray(energy)
    return energy * energy / np.expm1(energy / KT_EV)


def polynomial_extrema(coefficients, left, right):
    """All real critical points of an explicitly supplied cubic or lower.

    Coefficients are ascending powers about zero, as in Polynomial.  This
    computes extrema of the binary64 polynomial, without interval arithmetic.
    """
    if not np.isfinite([left, right]).all() or left > right:
        raise ValueError("ordered finite polynomial interval required")
    poly = Polynomial(np.asarray(coefficients, dtype=float))
    points = [float(left), float(right)]
    for root in poly.deriv().roots():
        if abs(float(np.imag(root))) <= 128 * np.finfo(float).eps * max(1.0, abs(root)):
            root = float(np.real(root))
            if left < root < right:
                points.append(root)
    values = np.asarray(poly(points), dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("nonfinite polynomial extrema")
    return float(values.min()), float(values.max())


def hermite_coefficients(y0, y1, d0, d1, span):
    return np.array([y0, span*d0,
                     -3*y0-2*span*d0+3*y1-span*d1,
                     2*y0+span*d0-2*y1+span*d1])


def exponential_integral(rate, left, right):
    """Integral of exp(-rate*t), stable for a narrow positive interval."""
    if not rate > 0 or not 0 <= left <= right:
        raise ValueError("positive rate and ordered nonnegative interval required")
    return math.exp(-rate*left) * (-math.expm1(-rate*(right-left))) / rate


class ArchiveInputs:
    """Load and hash immutable files from an explicit restored source root."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        manifest = self.root / "SHA256SUMS.txt"
        self.expected = {}
        for line in manifest.read_text().splitlines():
            sha, relative = line.split(maxsplit=1)
            self.expected[relative.strip()] = sha
        self.files = {"SHA256SUMS.txt": {"sha256": digest(manifest),
                                         "bytes": manifest.stat().st_size,
                                         "verification": "MANIFEST_HASH_RECORDED"}}

    def verify(self, relative):
        path = self.root / relative
        sha = digest(path)
        if relative not in self.expected or sha != self.expected[relative]:
            raise ValueError(f"archive file identity mismatch: {relative}")
        self.files[relative] = {"sha256": sha, "bytes": path.stat().st_size,
                                "verification": "MATCHES_RESTORED_MANIFEST"}
        return path


class FixedResponse:
    def __init__(self, source_root, profile):
        if profile not in ("tight", "standard"):
            raise ValueError("profile must be tight or standard")
        self.profile = profile
        self.inputs = ArchiveInputs(source_root)
        src = self.inputs
        for relative in (
            "scripts/retarded_integrator.py", "scripts/gas_integrator_parent.py",
            "scripts/spectral_joint11.py", "inputs/source_table.py",
            "inputs/bass164/PRODUCER_RECEIPT.json",
            "inputs/bass164/PROPOSED_REI_BACKGROUND.csv",
            "code/rei_bass_coupled/owner_src/axbi_sources.rs",
            "code/rei_bass_coupled/owner_src/atomic_provider.rs",
            "code/rei_bass_coupled/src/spectral_edge_support.rs",
            "code/rei_bass_coupled/src/spectral_native.rs",
        ):
            src.verify(relative)
        sys.path.insert(0, str(src.root / "scripts"))
        native = importlib.import_module("retarded_integrator")
        if Path(native.ROOT).resolve() != src.root:
            raise ValueError("different archive module already imported in this process")
        self.native = native
        m0_path = src.verify("inputs/spectral11/m0.json")
        m2_path = src.verify("inputs/spectral11/m2.json")
        m0 = json.loads(m0_path.read_text())
        m2 = json.loads(m2_path.read_text())
        for field in ("case", "x0", "x1", "a0", "state", "chi_eV"):
            if m0[field] != m2[field]:
                raise ValueError(f"historical M0/M2 physical mismatch: {field}")
        if (m0["case"] != "SIGNED_MINUS" or m0["x0"] != 0.7 or
                m0["x1"] != 0.7004 or m0["chi_eV"][0] != H_BINDING or
                m0["chi_eV"][3] != D_GATE):
            raise ValueError("unsupported original physical configuration")
        first = dict(m0)
        first["cohorts"] = [row for row in m0["cohorts"] if row[7] == 0]
        self.original_first_cell_rows = len(first["cohorts"])
        self.model = native.RetardedModel(native.coalesce_reflections(first))
        self.rows = self.model.coh
        if self.rows.shape != (640, 9) or len(np.unique(self.rows[:, 0])) != 160:
            raise ValueError("expected original 160-birth GL8 reflection quotient")
        self.zbirth = self.model.birth
        self.weights_com3 = self.rows[:, 6] * self.model.a0**3
        self.mu2 = self.rows[:, 5]**2
        self.nh = self.model.nh
        self.dx = self.model.dx
        self.source_normalizations = {}
        for order in (64, 96):
            node, weight = leggauss(order)
            en = H_FIT + 0.5*(node+1)*(CELL_HI-H_FIT)
            self.source_normalizations[order] = float(
                0.5*(CELL_HI-H_FIT)*np.dot(weight, number_shape(en)))
        self.source_norm = self.source_normalizations[96]
        if not self.source_norm > 0:
            raise ValueError("positive original source measure required")

        rtol_label = "6e-12" if profile == "tight" else "3e-11"
        directory = f"evidence/joint11_sided_m2_{rtol_label}"
        meta_path = src.verify(directory + "/checkpoint.json")
        self.metadata = json.loads(meta_path.read_text())
        meta = self.metadata
        if (meta["status"] != "COMPLETE" or meta["next_segment"] != 6241 or
                meta["dimension"] != 40357 or
                meta["packet_sha256"] != digest(m2_path)):
            raise ValueError("complete original M2 endpoint required")
        self.zknots = [0.0]
        gas = [self.model.y0[:14].copy()]
        numbered = []
        for path in (src.root / directory).glob("checkpoint_*.npz"):
            match = re.fullmatch(r"checkpoint_(\d+)\.npz", path.name)
            if match:
                numbered.append((int(match.group(1)), path))
        self.checkpoint_receipts = []
        for segment, path in sorted(numbered):
            relative = str(path.relative_to(src.root))
            src.verify(relative)
            if segment < 1 or segment > meta["next_segment"]:
                raise ValueError("checkpoint beyond committed complete history")
            z = float(meta["segments"][segment-1][1])
            with np.load(path, allow_pickle=False) as saved:
                state = saved["state"]
                if state.shape != (40357,) or not np.isfinite(state).all():
                    raise ValueError("invalid archived M2 state")
                gas.append(state[:14].copy())
            self.zknots.append(z)
            self.checkpoint_receipts.append({"segment": segment, "z": z,
                                             "file": relative})
        self.zknots = np.asarray(self.zknots)
        self.gas_knots = np.asarray(gas)
        if (len(self.zknots) != (13 if profile == "tight" else 18) or
                not np.all(np.diff(self.zknots) > 0) or self.zknots[-1] != 1.0 or
                (self.gas_knots[:, [1, 3]] <= 0).any()):
            raise ValueError("complete positive archived gas knot sequence required")
        final_file = src.root / directory / meta["state_file"]
        if digest(final_file) != meta["state_sha256"]:
            raise ValueError("endpoint commit-marker hash mismatch")
        self.gas = PchipInterpolator(self.zknots, self.gas_knots[:, [1, 3]],
                                    axis=0, extrapolate=False)
        self._geometry_coefficients()
        self.rend = self.ratio(np.ones(640), np.arange(640))[0]
        self.upper = np.minimum(CELL_HI, H_FIT/self.rend)
        self.binding_cut = H_BINDING/self.rend
        if not ((self.rend > 0).all() and (self.rend < 1).all() and
                (self.upper > H_FIT).all()):
            raise ValueError("positive redshifted first-cell sub-H support required")
        self.bounds = self._tail_constants()
        self.optical_scale = 1.0/self.bounds["lambda_min_per_eV"]
        self.global_core_hi = H_FIT + CORE_OPTICAL_CUTOFF*self.optical_scale
        if not self.global_core_hi < D_GATE:
            raise ValueError("core reaches D gate; this bounded diagnostic is inapplicable")
        self.core_hi = np.minimum(self.upper, self.global_core_hi)
        geometry_knots = (self.model.xnodes-self.model.x0)/self.dx
        self.time_knots = np.unique(np.r_[0.0, 1.0, self.zknots,
                geometry_knots[(geometry_knots > 0) & (geometry_knots < 1)]])

    def _geometry_coefficients(self):
        segs = self.model.segs
        self.geom_left = np.array([seg.left.x for seg in segs])
        self.geom_span = np.array([seg.span for seg in segs])
        self.b_coeff = np.asarray([hermite_coefficients(seg.b0, seg.b1,
                  seg.bprime0, seg.bprime1, seg.span) for seg in segs])
        self.h_coeff = np.asarray([hermite_coefficients(seg.logh0, seg.logh1,
                  seg.dh0, seg.dh1, seg.span) for seg in segs])

    def geometry(self, z):
        """Vector evaluation of the actual restored Hermite geometry data."""
        z = np.asarray(z, dtype=float)
        x = self.model.x0 + self.dx*z
        j = np.clip(np.searchsorted(self.model.xnodes, x, side="right")-1,
                    0, len(self.geom_span)-1)
        u = (x-self.geom_left[j])/self.geom_span[j]
        b = self.b_coeff[j]
        lh = self.h_coeff[j]
        bv = ((b[..., 3]*u+b[..., 2])*u+b[..., 1])*u+b[..., 0]
        bx = ((3*b[..., 3]*u+2*b[..., 2])*u+b[..., 1])/self.geom_span[j]
        hv = np.exp(((lh[..., 3]*u+lh[..., 2])*u+lh[..., 1])*u+lh[..., 0])
        a = self.model.a0*np.exp(self.dx*z)
        return a, bv, hv, bx

    def ratio(self, z, ray):
        a, b, h, bx = self.geometry(z)
        row = self.rows[np.asarray(ray)]
        perpendicular = (1-row[..., 5]**2)*(row[..., 2]/a)**2*np.exp(2*(b-row[..., 3]))
        parallel = row[..., 5]**2*(row[..., 2]/a)**2*np.exp(-4*(b-row[..., 3]))
        total = perpendicular+parallel
        q = ((1-bx)*perpendicular+(1+2*bx)*parallel)/total
        return np.sqrt(total), h, q

    def _tail_constants(self):
        bmin, bmax = math.inf, -math.inf
        lhmin, lhmax = math.inf, -math.inf
        for i, seg in enumerate(self.model.segs):
            left = max(seg.left.x, self.model.x0)
            right = min(seg.right.x, self.model.x1)
            if right <= left:
                continue
            lo, hi = (left-seg.left.x)/seg.span, (right-seg.left.x)/seg.span
            bc = self.b_coeff[i]
            derivative = np.array([bc[1], 2*bc[2], 3*bc[3]])/seg.span
            mn, mx = polynomial_extrema(derivative, lo, hi)
            bmin, bmax = min(bmin, mn), max(bmax, mx)
            mn, mx = polynomial_extrema(self.h_coeff[i], lo, hi)
            lhmin, lhmax = min(lhmin, mn), max(lhmax, mx)
        bmin -= EXTREMA_PAD
        bmax += EXTREMA_PAD
        # q=1+b_X(3w-1), 0<=w<=1.  This global angular envelope is
        # conservative; no conclusion follows merely from the endpoint ratio.
        qmin = min(1-bmax, 1+2*bmin)
        qmax = max(1-bmin, 1+2*bmax)
        ymax, ymin = -math.inf, math.inf
        for i, span in enumerate(np.diff(self.zknots)):
            mn, mx = polynomial_extrema(self.gas.c[:, i, 0][::-1], 0, span)
            ymin, ymax = min(ymin, mn), max(ymax, mx)
        density_min = self.nh*ymin*math.exp(-3*self.dx)*(1-EXTREMA_PAD)
        hmax = math.exp(lhmax)*(1+EXTREMA_PAD)
        upper = float(self.upper.max())
        sigma = float(self.native.sigma_native_formula(
            np.array([upper]), self.model.chi)[0, 0])
        # For H, x=E/e0>1.  d ln(sigma/E)/d ln E is bounded above by
        # 2*x/(x-1)+p/2-6.5.  The omitted last term is nonpositive.
        _, e0, _, _, p, _, _, _ = self.native.PARAMETERS[0]
        monotone_log_derivative_upper = 2*(H_FIT/e0)/(H_FIT/e0-1)+p/2-6.5
        if not (qmin > 0 and density_min > 0 and sigma > 0 and
                monotone_log_derivative_upper < 0 and H_FIT > 2*KT_EV):
            raise ValueError("positive monotone H-only tail prerequisites failed")
        lam = C_M_S*density_min/(hmax*qmax)*sigma/upper*(1-EXTREMA_PAD)
        return {"b_X_min_padded": bmin, "b_X_max_padded": bmax,
                "q_min_global": qmin, "q_max_global": qmax,
                "H_max_per_s_padded": hmax,
                "Y_HI_min_polynomial": ymin, "Y_HI_max_polynomial": ymax,
                "n_HI_min_m3_padded": density_min,
                "energy_upper_for_sigma_eV": upper,
                "sigma_over_E_log_derivative_upper": float(monotone_log_derivative_upper),
                "lambda_min_per_eV": lam, "binary64_extrema_pad": EXTREMA_PAD,
                "directed_rounding_certificate": False}

    def energy_rule(self, order):
        nodes, weights = leggauss(order)
        if (weights <= 0).any():
            raise ValueError("positive energy weights required")
        energies, measures, rays, bins = [], [], [], []
        panel_count = 0
        fixed = H_FIT + self.optical_scale*np.array([0, 2, 6, 14, 30, 32])
        for ray in range(640):
            hi = self.core_hi[ray]
            cuts = [H_FIT, hi]
            cuts += [float(v) for v in fixed if H_FIT < v < hi]
            bind = self.binding_cut[ray]
            if H_FIT < bind < hi:
                cuts.append(float(bind))
            cuts = sorted(set(cuts))
            for left, right in zip(cuts[:-1], cuts[1:]):
                en = left + 0.5*(nodes+1)*(right-left)
                measure = 0.5*(right-left)*weights*number_shape(en)
                if (measure <= 0).any() or not (en > left).all() or not (en < right).all():
                    raise ValueError("strict positive core energy panel failed")
                energies.extend(en.tolist())
                measures.extend((measure*self.weights_com3[ray]/self.source_norm).tolist())
                rays.extend([ray]*order)
                bins.extend([int(0.5*(left+right) >= bind)]*order)
                panel_count += 1
        return (np.asarray(energies), np.asarray(measures), np.asarray(rays),
                np.asarray(bins), panel_count)

    def crossings(self, energies, rays):
        left = self.zbirth[rays].copy()
        right = np.ones_like(left)
        if not (energies*self.ratio(left, rays)[0] > H_FIT).all():
            raise ValueError("core node not H-active at birth")
        if not (energies*self.ratio(right, rays)[0] < H_FIT).all():
            raise ValueError("core node not below H fit edge at endpoint")
        for _ in range(48):
            mid = 0.5*(left+right)
            above = energies*self.ratio(mid, rays)[0] > H_FIT
            left = np.where(above, mid, left)
            right = np.where(above, right, mid)
        root = 0.5*(left+right)
        residual = energies*self.ratio(root, rays)[0]-H_FIT
        if np.max(np.abs(residual)) > 5e-12:
            raise ValueError("H crossing residual exceeds fixed diagnostic guard")
        return root, {"bisection_iterations": 48,
                      "max_z_bracket_width": float(np.max(right-left)),
                      "max_energy_residual_eV": float(np.max(np.abs(residual)))}

    def optical_depths(self, energies, rays, crossings, order):
        nodes, weights = leggauss(order)
        tau = np.zeros(len(energies))
        evaluations, panels = 0, 0
        min_q, min_above = math.inf, math.inf
        for lower, upper in zip(self.time_knots[:-1], self.time_knots[1:]):
            left = np.maximum(self.zbirth[rays], lower)
            right = np.minimum(crossings, upper)
            ids = np.flatnonzero(right > left)
            if not len(ids):
                continue
            span = right[ids]-left[ids]
            z = left[ids, None] + 0.5*(nodes[None, :]+1)*span[:, None]
            ratio, h, q = self.ratio(z, rays[ids, None])
            energy = energies[ids, None]*ratio
            sigma = self.native.sigma_native_formula(energy.ravel(), self.model.chi)[:, 0]
            sigma = sigma.reshape(energy.shape)
            # The entire retained core is born below D and then redshifts.
            # D therefore contributes exactly zero here under the archived gate.
            if not (energy < D_GATE).all() or (sigma <= 0).any():
                raise ValueError("H-only retained core branch guard failed")
            y_hi = self.gas(z)[..., 0]
            hazard = C_M_S*self.dx/h * (self.nh*y_hi*np.exp(-3*self.dx*z))*sigma
            if not np.isfinite(hazard).all() or (hazard <= 0).any() or (q <= 0).any():
                raise ValueError("positive finite optical response required")
            tau[ids] += 0.5*span*np.dot(hazard, weights)
            evaluations += len(ids)*order
            panels += len(ids)
            min_q = min(min_q, float(q.min()))
            min_above = min(min_above, float((energy-H_FIT).min()))
        if (tau < 0).any() or not np.isfinite(tau).all():
            raise ValueError("invalid integrated optical depth")
        return tau, {"time_energy_evaluations": evaluations, "smooth_time_panels": panels,
                     "minimum_sampled_q": min_q,
                     "minimum_sampled_energy_above_H_fit_eV": min_above}

    def tail_bounds(self):
        bins = np.zeros(2)
        lam = self.bounds["lambda_min_per_eV"]
        gmax = float(number_shape(H_FIT))
        for ray in range(640):
            v, u, bind = self.core_hi[ray], self.upper[ray], self.binding_cut[ray]
            intervals = [(v, min(u, bind)), (max(v, bind), u)]
            for index, (left, right) in enumerate(intervals):
                if right > left:
                    bins[index] += self.weights_com3[ray]/self.source_norm*gmax*exponential_integral(
                        lam, left-H_FIT, right-H_FIT)
        return {"below_H_binding_com3": float(bins[0]),
                "H_binding_to_H_fit_com3": float(bins[1]),
                "all_below_H_fit_com3": float(bins.sum()),
                "lower_bound": 0.0,
                "meaning": "conditional H-only analytic upper bound on omitted energy tail; D opacity is nonnegative",
                "core_quadrature_error_included": False,
                "directed_rounding_certificate": False}

    def calculate(self, energy_order, time_order):
        start = time.perf_counter()
        energies, measures, rays, bins, panel_count = self.energy_rule(energy_order)
        crossings, crossing_receipt = self.crossings(energies, rays)
        tau, time_receipt = self.optical_depths(energies, rays, crossings, time_order)
        values = measures*np.exp(-tau)
        binned = np.bincount(bins, weights=values, minlength=2)
        result = {"gas_profile": self.profile, "energy_GL_order": energy_order,
                  "time_GL_order": time_order, "energy_panels": panel_count,
                  "energy_nodes": len(energies),
                  "core_survivor_com3": {"below_H_binding": float(binned[0]),
                     "H_binding_to_H_fit": float(binned[1]),
                     "all_below_H_fit": float(values.sum())},
                  "bin_additivity_absolute_com3": float(binned.sum()-values.sum()),
                  "crossings": crossing_receipt, "time_quadrature": time_receipt,
                  "wall_seconds": time.perf_counter()-start}
        return result

    def independent_checks(self):
        geometry_error = np.zeros(4)
        for z in np.linspace(0, 1, 17):
            old = np.asarray(self.model.geometry(float(z)))
            new = np.asarray(self.geometry(float(z)))
            geometry_error = np.maximum(geometry_error, np.abs(new-old)/np.maximum(np.abs(old), 1e-30))
        ray_parity = 0.0
        for z in (0.0, 0.271828, 0.731, 1.0):
            native_energy = self.model.rays(z, 640)[0]
            ours = self.rows[:, 4]*self.ratio(np.full(640, z), np.arange(640))[0]
            ray_parity = max(ray_parity, float(np.max(np.abs(ours/native_energy-1))))
        if geometry_error.max() > 2e-10 or ray_parity > 3e-14:
            raise ValueError("vector geometry disagrees with original scalar implementation")
        probes = []
        for ray, fraction in ((0, 0.17), (193, 0.53), (417, 0.79), (639, 0.37)):
            eb = H_FIT + fraction*(self.core_hi[ray]-H_FIT)
            row = self.rows[ray]
            def scalar_energy(z):
                a, b, _, _ = self.model.geometry(float(z))
                return eb*math.sqrt((row[2]/a)**2*((1-row[5]**2)*math.exp(2*(b-row[3]))+
                                                   row[5]**2*math.exp(-4*(b-row[3]))))
            crossing = brentq(lambda z: scalar_energy(z)-H_FIT,
                              float(self.zbirth[ray]), 1.0, xtol=5e-15,
                              rtol=4*np.finfo(float).eps)
            def integrand(z):
                _, _, h, _ = self.model.geometry(float(z))
                en = scalar_energy(z)
                sigma = self.native.sigma_native_formula(np.array([en]), self.model.chi)[0, 0]
                return C_M_S*self.dx/h*self.nh*float(self.gas(z)[0])*math.exp(-3*self.dx*z)*sigma
            knots = [float(self.zbirth[ray]), *[float(k) for k in self.time_knots
                          if self.zbirth[ray] < k < crossing], float(crossing)]
            terms = [quad(integrand, left, right, epsabs=2e-11, epsrel=2e-11, limit=100)
                     for left, right in zip(knots[:-1], knots[1:])]
            independent = math.fsum(t[0] for t in terms)
            en_array, ray_array = np.array([eb]), np.array([ray])
            roots, _ = self.crossings(en_array, ray_array)
            ours, _ = self.optical_depths(en_array, ray_array, roots, 24)
            rel = float(ours[0]/independent-1)
            if abs(rel) > 2e-8:
                raise ValueError("independent scalar optical-depth discrepancy")
            probes.append({"ray": ray, "birth_energy_eV": eb,
                           "scalar_native_quad_tau": independent,
                           "vector_GL24_tau": float(ours[0]), "relative_difference": rel,
                           "quad_reported_absolute_error": math.fsum(t[1] for t in terms)})
        return {"status": "IMPLEMENTATION_VERIFIED_WITHIN_REPORTED_TOLERANCES",
                "geometry_max_relative_differences_a_b_H_bX": geometry_error.tolist(),
                "native_ray_energy_max_relative_difference": ray_parity,
                "source_GL64_over_GL96_minus1": self.source_normalizations[64]/self.source_norm-1,
                "scalar_native_optical_depth_probes": probes}

    def identity(self):
        return {"profile": self.profile, "archived_rtol": self.metadata["rtol"],
                "gas_knots_including_IC": len(self.zknots),
                "gas_path_definition": "PCHIP of archived dimensionless comoving HI and DI coordinates, multiplied by nH_initial*exp(-3*dx*z) for proper densities",
                "checkpoint_gas_data_sha256": hashlib.sha256(
                    np.ascontiguousarray(np.column_stack((self.zknots, self.gas_knots)), dtype="<f8").tobytes()).hexdigest(),
                "input_files": self.inputs.files,
                "checkpoint_knots": self.checkpoint_receipts,
                "birth_samples": 160, "angular_rule": "GL8; exact +/-mu scalar reflection quotient",
                "finite_rays": 640, "original_first_cell_rows": self.original_first_cell_rows,
                "first_cell_birth_com3": float(self.weights_com3.sum()),
                "source_measure": "original M0 first-cell count for each birth/angular pair times BB50K g(E)/integral_first_cell(g)",
                "source_energy_integral_GL96": self.source_norm,
                "source_energy_integral_GL64": self.source_normalizations[64],
                "cell_edges_eV": [H_FIT, CELL_HI], "kT_eV": KT_EV,
                "physical_H_binding_eV": H_BINDING, "H_fit_edge_eV": H_FIT,
                "D_gate_eV": D_GATE, "D_model": "archived threshold-gated H-equality approximation",
                "core_upper_eV": self.global_core_hi,
                "core_upper_below_D_gate": self.global_core_hi < D_GATE,
                "core_optical_cutoff": CORE_OPTICAL_CUTOFF,
                "analytic_tail_constants": self.bounds,
                "tail_upper_bounds": self.tail_bounds()}


def finite_difference(left, right, name):
    return {"comparison": name,
            "relative_change_using_right_denominator": {
                key: (right["core_survivor_com3"][key]-left["core_survivor_com3"][key])/
                     right["core_survivor_com3"][key]
                for key in right["core_survivor_com3"]}}


def write_new(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True,
                        help="restored run13/recovered root containing SHA256SUMS.txt")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; this work unit uses add-only receipts")
    start = time.perf_counter()
    tight = FixedResponse(args.source_root, "tight")
    tight_checks = tight.independent_checks()
    runs = []
    for energy, time_order in ((6, 16), (8, 16), (12, 16), (12, 24)):
        result = tight.calculate(energy, time_order)
        runs.append(result)
        print(json.dumps({"completed": "tight", "energy": energy, "time": time_order,
                          "core": result["core_survivor_com3"], "wall_s": result["wall_seconds"]}), flush=True)
    # Separate archive knot grid: this is not a same-grid ODE tolerance study.
    standard = FixedResponse(args.source_root, "standard")
    standard_checks = standard.independent_checks()
    result = standard.calculate(12, 24)
    runs.append(result)
    print(json.dumps({"completed": "standard", "energy": 12, "time": 24,
                      "core": result["core_survivor_com3"], "wall_s": result["wall_seconds"]}), flush=True)
    receipt = {"schema": SCHEMA, "status": "NUMERICALLY_CHECKED",
        "source_status": "NEW_POSTLOSS_IMPLEMENTATION_NOT_LOST_SOURCE_RECONSTRUCTION",
        "script_sha256": digest(Path(__file__).resolve()),
        "exact_command_argv": sys.argv, "execution_environment": {
            "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
            "platform": platform.platform(), "native_IVP_runs": 0},
        "scope": {"gas_path": "prescribed archive checkpoint PCHIP only",
            "geometry": "actual original prescribed BASS121 SIGNED_MINUS Hermite table",
            "source": "fixed original 160 births and GL8; first-cell continuous energy diagnostic",
            "quadrature_claim": "finite refinement differences only",
            "tail_claim": "conditional analytic positive H-only omitted-tail estimate, binary64 implementation with explicit padding",
            "unresolved": ["true gas IVP path between archived checkpoints", "nonlinear spectral opacity feedback",
                "rigorous core quadrature error enclosure", "birth-time continuum", "angular continuum",
                "whole donor domain", "full EoR", "Einstein feedback", "FLRW-CONV", "BI-SIGNED",
                "ISO-COUPLE full", "Li/Be and nuclear T1-T8"]},
        "inputs": {"tight": tight.identity(), "standard": standard.identity()},
        "implementation_checks": {"tight": tight_checks, "standard": standard_checks},
        "results": runs,
        "comparisons": [finite_difference(runs[0], runs[1], "tight E6 to E8, time16"),
            finite_difference(runs[1], runs[2], "tight E8 to E12, time16"),
            finite_difference(runs[2], runs[3], "tight time16 to time24, E12"),
            finite_difference(runs[3], runs[4], "tight13 to standard18 PCHIP-defined gas path, E12 time24; combines checkpoint grid and finite solver differences")],
        "wall_seconds": time.perf_counter()-start,
        "next_existing_DAG_node": "P4-S4C-SPECTRAL-EDGE-SUPPORT remains incomplete: coupled continuum error and gas-path control"}
    write_new(args.output, receipt)
    print(json.dumps({"output": str(args.output), "sha256": digest(args.output),
                      "wall_seconds": receipt["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
