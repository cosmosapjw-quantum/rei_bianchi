"""Primordial H/He/Li photo/RR chemistry with exact isotope grouping.

Nine elemental fractions (H2, He3, Li4) lift to all21 isotope/charge populations.
The reduction assumes equal electronic isotope rates, common initial fractions,
zero initial n/T and frozen nuclear sources.  Nonzero n/T controls use the
separate full21/full22 operators.  Electron density is a live charge census.

Group RHS and Jacobian are analytic extensions around the physical simplex, as
required by an implicit Newton solver.  They never clip or renormalize a state.
Use validate_fractions at initial/accepted/output states to check positivity.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.constants import atomic_mass
from scipy.special import expit

from atomic_photo_rr import AtomicPhotoRR

UNIT = Path(__file__).resolve().parents[1]
G_SI = 6.67430e-11
NEUTRON_MEAN_LIFETIME_S = 878.4
TRITIUM_HALF_LIFE_S = 4500.*86400.


def _readonly(value, dtype=float):
    a = np.asarray(value, dtype=dtype)
    # Immutable bytes also prevent a caller from resetting WRITEABLE=True.
    return np.frombuffer(a.tobytes(), dtype=a.dtype).reshape(a.shape)


class PrimordialNetwork:
    fraction_groups = (slice(0, 2), slice(2, 5), slice(5, 9))
    fraction_group_names = ("H", "He", "Li")
    nuclide_names = ("n", "H1", "D", "T", "He3", "He4", "Li6", "Li7")
    nuclide_A = _readonly([1, 1, 2, 3, 3, 4, 6, 7], int)
    nuclide_Z = _readonly([0, 1, 1, 1, 2, 2, 3, 3], int)
    nuclide_slices = (slice(0, 1), slice(1, 3), slice(3, 5), slice(5, 7),
                     slice(7, 10), slice(10, 13), slice(13, 17), slice(17, 21))
    fraction_names = ("H_q0", "H_q1", "He_q0", "He_q1", "He_q2",
                      "Li_q0", "Li_q1", "Li_q2", "Li_q3")

    def __init__(self, scenario_path=None):
        if scenario_path is None:
            scenario_path = UNIT/"data/ISOTOPE_SCENARIO.json"
        scenario_bytes = Path(scenario_path).read_bytes()
        scenario = json.loads(scenario_bytes)
        if tuple(scenario["nuclei"]) != self.nuclide_names:
            raise ValueError("scenario nuclear inventory differs from the21-state contract")
        if scenario["heavy_species_count"] != 21:
            raise ValueError("the selected atomic inventory requires21 states")
        comp = scenario["composition"]
        if comp.get("n_over_H", 0.) != 0 or comp.get("T_over_H", 0.) != 0:
            raise ValueError("grouped fast path requires n=T=0; use full21 weak-decay controls")
        y4 = float(comp["YPBBN"])
        rd, r3, r6, r7 = (float(comp[k]) for k in ("DoH", "He3oH", "Li6oH", "Li7oH"))
        if not (0 < y4 < 1 and all(math.isfinite(v) and v >= 0 for v in (rd, r3, r6, r7))):
            raise ValueError("finite nonnegative isotope ratios and0<Y4<1 required")
        r4 = y4*(1+2*rd+3*r3+6*r6+7*r7)/(4*(1-y4))
        ratios = np.array([0., 1., rd, 0., r3, r4, r6, r7])
        self.nuclide_ratios_per_H = _readonly(ratios)
        self.baryons_per_H = float(self.nuclide_A@ratios)

        cosmo_path = UNIT/"vendor/REI_BACKGROUND_FAMILY_LOCK.json"
        cosmo_bytes = cosmo_path.read_bytes()
        cosmo = json.loads(cosmo_bytes)["cosmology"]
        rho_critical = 3*cosmo["H0_per_s"]**2/(8*math.pi*G_SI)
        self.nH0_m3 = rho_critical*cosmo["Omega_b"]/(atomic_mass*self.baryons_per_H)
        self.aref = 1/(1+float(scenario["redshift"][0]))
        self.a_ref = self.aref
        self.z_end = float(scenario["redshift"][1])
        if not (self.aref > 0 and self.z_end >= 0 and self.aref < 1/(1+self.z_end)):
            raise ValueError("finite increasing-scale-factor redshift window required")

        initial = scenario["initial_charge_fractions"]
        self.initial_fractions = _readonly(np.concatenate([initial["H_D_T"],
                                    initial["He3_He4"], initial["Li6_Li7"]]))
        self.validate_fractions(self.initial_fractions, tolerance=2.e-15)

        species_names, species_a, species_q, species_nuclide = [], [], [], []
        lift = np.zeros((21, 9))
        for i, (name, mass_number, charge_number, block) in enumerate(zip(
                self.nuclide_names, self.nuclide_A, self.nuclide_Z, self.nuclide_slices)):
            for q in range(charge_number+1):
                j = block.start+q
                species_names.append(f"{name}_q{q}")
                species_a.append(mass_number)
                species_q.append(q)
                species_nuclide.append(i)
                if charge_number:
                    lift[j, self.fraction_groups[charge_number-1].start+q] = ratios[i]
        self.species_names = tuple(species_names)
        self.species_A = _readonly(species_a, int)
        self.species_charge = _readonly(species_q, int)
        self.species_nuclide_index = _readonly(species_nuclide, int)
        self.lift_matrix = _readonly(lift)
        census = np.zeros((8, 9))
        for i, block in enumerate(self.nuclide_slices):
            census[i] = self.species_charge[block]@lift[block]
        self.electron_census_matrix = _readonly(census)
        self._electron_gradient_per_H = _readonly(np.sum(census, axis=0))

        self.provider = AtomicPhotoRR()
        self.temperature_K = float(scenario["temperature_K"])
        if not 3 <= self.temperature_K <= 20000:
            raise ValueError("the selected freezeout contract requires3<=T<=20000 K")
        self.recombination_cm3_s = _readonly(self.provider.rates(self.temperature_K, 0.)["recombination_cm3_s"])
        uv = scenario["UV"]
        if list(uv["energy_eV"]) != self.provider.metadata["UV_support_eV"] or uv["photon_number_index"] != self.provider.metadata["photon_number_power_index"]:
            raise ValueError("scenario spectrum differs from source-pinned photo provider")
        self.gamma_HI_max = float(uv["Gamma_HI_max_per_s"])
        self.uv_z_center, self.uv_z_width = float(uv["z_center"]), float(uv["z_width"])
        if not (all(math.isfinite(v) for v in (self.gamma_HI_max, self.uv_z_center, self.uv_z_width))
                and 0 <= self.gamma_HI_max <= 1.e-12 and self.uv_z_width > 0):
            raise ValueError("finite UV parameters, positive width and GammaHI_max<=1e-12 required")

        photo, recomb = np.zeros((9, 9)), np.zeros((9, 9))
        # Column-vector generators: each transition transfers a signed flux.
        for pair, lower in enumerate((0, 2, 3, 5, 6, 7)):
            upper = lower+1
            photo[lower, lower] -= self.provider.photo_ratios[pair]
            photo[upper, lower] += self.provider.photo_ratios[pair]
            recomb[lower, upper] += self.recombination_cm3_s[pair]
            recomb[upper, upper] -= self.recombination_cm3_s[pair]
        self.photo_generator_per_gamma_HI = _readonly(photo)
        self.rr_generator_cm3_s = _readonly(recomb)

        transitions = []
        for Z, block in zip(self.nuclide_Z, self.nuclide_slices):
            if Z:
                pair0 = (0, 1, 3)[Z-1]
                transitions.extend((block.start+q, block.start+q+1, pair0+q) for q in range(Z))
        self.atomic_transitions = tuple(transitions)
        st = np.zeros((22, len(transitions)), dtype=int)
        for j, (lower, upper, _) in enumerate(transitions):
            st[lower, j], st[upper, j], st[21, j] = -1, 1, 1
        self.photo_stoichiometry22 = _readonly(st, int)

        # q->q+1 retains spectator bound electrons in the beta-decay control.
        weak = np.zeros((22, 22))
        self.weak_channels = ((0, 2, 1/NEUTRON_MEAN_LIFETIME_S),
                              (5, 8, math.log(2)/TRITIUM_HALF_LIFE_S),
                              (6, 9, math.log(2)/TRITIUM_HALF_LIFE_S))
        for parent, daughter, rate in self.weak_channels:
            weak[parent, parent] -= rate
            weak[daughter, parent] += rate
            weak[21, parent] += rate
        self.weak_operator22_per_s = _readonly(weak)
        self.metadata = dict(schema="he32.grouped_primordial_network.v1",
            scenario_sha256=hashlib.sha256(scenario_bytes).hexdigest(),
            cosmology_sha256=hashlib.sha256(cosmo_bytes).hexdigest(),
            atomic_data_sha256=self.provider.data_sha256,
            nH0_m3=self.nH0_m3, baryons_per_H=self.baryons_per_H,
            fraction_order=self.fraction_names, species_order=self.species_names,
            nuclide_order=self.nuclide_names,
            physical_time="per second proper time; eta derivatives divide by target H",
            density_units="cm^-3 for ne and recombination products",
            closure="photo plus total RR; isotope equality; zero n/T nuclear invariant",
            mass_convention="A*m_u baryon census", temperature_K=self.temperature_K)

    @staticmethod
    def _vector(value, size):
        a = np.asarray(value, dtype=float)
        if a.shape != (size,) or not np.all(np.isfinite(a)):
            raise ValueError(f"finite length{size} vector required")
        return a

    def validate_fractions(self, fractions, tolerance=0.):
        """Check physical simplex membership without changing the supplied state."""
        f = self._vector(fractions, 9)
        if not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError("finite nonnegative positivity tolerance required")
        totals = np.array([np.sum(f[b]) for b in self.fraction_groups])
        if np.min(f) < -tolerance or np.max(f) > 1+tolerance or np.max(np.abs(totals-1)) > tolerance:
            raise ValueError("atomic fractions violate positivity or elemental simplex conservation")
        return dict(minimum=float(np.min(f)), maximum_simplex_residual=float(np.max(np.abs(totals-1))))

    def _nH_cm3(self, a):
        if not math.isfinite(a) or a <= 0:
            raise ValueError("positive finite scale factor required")
        return self.nH0_m3*1.e-6/a**3

    def scale_factor(self, eta):
        if not math.isfinite(eta):
            raise ValueError("finite log-scale-factor time required")
        return self.aref*math.exp(eta)

    def gamma_HI_per_s(self, a):
        self._nH_cm3(a)
        return self.gamma_HI_max*float(expit((self.uv_z_center-(1/a-1))/self.uv_z_width))

    def abundance_per_H(self, fractions):
        """Return21 isotope/charge number abundances per H1 nucleus."""
        return self.lift_matrix@self._vector(fractions, 9)

    def electron_by_nuclide_cm3(self, a, fractions):
        return self._nH_cm3(a)*(self.electron_census_matrix@self._vector(fractions, 9))

    def electron_density_cm3(self, a, fractions):
        return float(self._nH_cm3(a)*np.dot(self._electron_gradient_per_H, self._vector(fractions, 9)))

    def electron_gradient_cm3(self, a):
        """Exact partial ne/partial fractions at fixed scale factor, length9."""
        return self._nH_cm3(a)*self._electron_gradient_per_H

    def rhs_per_s(self, a, fractions):
        f = self._vector(fractions, 9)
        ne = self.electron_density_cm3(a, f)
        return self.gamma_HI_per_s(a)*(self.photo_generator_per_gamma_HI@f)+ne*(self.rr_generator_cm3_s@f)

    def rhs(self, eta, fractions, H):
        if not math.isfinite(H) or H <= 0:
            raise ValueError("positive finite target H per second required")
        return self.rhs_per_s(self.scale_factor(eta), fractions)/H

    def jacobian(self, eta, fractions, H):
        """Exact9x9 chemistry Jacobian at fixed target H and eta.

        J=[Gamma P+ne R+(R f) outer grad(ne)]/H.  A coupled caller separately
        differentiates H with respect to its geometry/radiation variables.
        """
        if not math.isfinite(H) or H <= 0:
            raise ValueError("positive finite target H per second required")
        f = self._vector(fractions, 9)
        a = self.scale_factor(eta)
        ne = self.electron_density_cm3(a, f)
        fixed = self.gamma_HI_per_s(a)*self.photo_generator_per_gamma_HI+ne*self.rr_generator_cm3_s
        return (fixed+np.outer(self.rr_generator_cm3_s@f, self.electron_gradient_cm3(a)))/H

    def weak_decay_rhs_per_s(self, populations):
        """Reaction-only weak RHS on21 populations or22 including free electrons.

        Input may use any common number-density or abundance unit.  No expansion
        dilution is included.  n/T inputs need not satisfy the grouped IC.
        """
        values = np.asarray(populations, dtype=float)
        if values.shape not in ((21,), (22,)) or not np.all(np.isfinite(values)):
            raise ValueError("finite21 or22 weak population vector required")
        n = values.size
        return self.weak_operator22_per_s[:n, :n]@values

    def weak_decay_step(self, populations, dt_s):
        """Exact finite weak-only step; no clipping and no IVP solver."""
        values = np.asarray(populations, dtype=float)
        if values.shape not in ((21,), (22,)) or not np.all(np.isfinite(values)) or np.min(values) < 0:
            raise ValueError("nonnegative finite21 or22 weak population vector required")
        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError("nonnegative finite elapsed proper seconds required")
        out = values.copy()
        for parent, daughter, rate in self.weak_channels:
            loss = values[parent]*(-math.expm1(-rate*dt_s))
            out[parent] = values[parent]*math.exp(-rate*dt_s)
            out[daughter] += loss
            if values.size == 22:
                out[21] += loss
        return out

    def full_rhs_and_electron_per_s(self, a, abundances_per_H, include_weak=True):
        """Independent full21 flux assembly, d(n_i/n_H)/dt and free e/H rate.

        n_H is the fixed reference-H comoving census, not neutral HI.  Expansion
        cancels in these abundance ratios.  Arbitrary n/T and isotope-specific
        charge distributions are admitted here; the grouped shortcut is unused.
        """
        y = self._vector(abundances_per_H, 21)
        ne = self._nH_cm3(a)*float(self.species_charge@y)
        photo = self.gamma_HI_per_s(a)*self.provider.photo_ratios
        dy = np.zeros(21)
        de = 0.
        for lower, upper, pair in self.atomic_transitions:
            flux = photo[pair]*y[lower]-self.recombination_cm3_s[pair]*ne*y[upper]
            dy[lower] -= flux
            dy[upper] += flux
            de += flux
        if include_weak:
            for parent, daughter, rate in self.weak_channels:
                flux = rate*y[parent]
                dy[parent] -= flux
                dy[daughter] += flux
                de += flux
        return dy, float(de)

    def full_rhs_per_s(self, a, abundances_per_H, include_weak=True):
        return self.full_rhs_and_electron_per_s(a, abundances_per_H, include_weak)[0]

    def full_density_rhs_per_s(self, a, densities_cm3, include_weak=True):
        """Reaction-only dn_i/dt in cm^-3 s^-1; add -3H n_i for physical dilution."""
        nH = self._nH_cm3(a)
        y = self._vector(densities_cm3, 21)/nH
        return nH*self.full_rhs_per_s(a, y, include_weak)
