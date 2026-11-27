"""A shared physical L2 grid for O-centered finite spherical Galerkin states.

The supplied Hamiltonian is the induced finite Galerkin operator, never a
pointwise differential Coulomb Hamiltonian or an infinite-space certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import os
import tempfile

import numpy as np
from numpy.polynomial.legendre import leggauss

from optimized_solver import angular
from projector import Representation, Role, Snapshot, StateID, StateRecord


class EmbeddingError(ValueError):
    pass


def _readonly(a):
    out = np.array(a, dtype=np.float64, copy=True)
    out.setflags(write=False)
    return out


def _positive_integer(value, name, minimum=1):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise EmbeddingError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _state_contract(state):
    if state.metadata.get("origin_center") != "O" or state.metadata.get("origin_shift_center_to_O") != 0.:
        raise EmbeddingError("only unshifted charge-center O states are supported")
    if state.metadata.get("units") != "a_A,E_A":
        raise EmbeddingError("requires explicit a_A,E_A units")
    if isinstance(state.m, (bool, np.bool_)) or state.m not in (0, 1):
        raise EmbeddingError("only real static spinless m=0 and |m|=1 providers are supported")
    scalars = np.asarray([state.R, state.ZA, state.ZB, state.energy, state.residual], dtype=float)
    if (not np.isfinite(scalars).all() or state.R < 0 or state.ZA < 0 or state.ZB < 0
            or state.ZA + state.ZB <= 0 or state.residual < 0):
        raise EmbeddingError("invalid physical parameters or finite matrix residual")
    degree = _positive_integer(state.degree, "degree", 2)
    mesh = np.asarray(state.boundaries)
    ls = np.asarray(state.ls)
    coef = np.asarray(state.coefficients)
    if (mesh.dtype != np.float64 or mesh.ndim != 1 or len(mesh) < 2
            or not np.isfinite(mesh).all() or mesh[0] != 0 or np.any(np.diff(mesh) <= 0)):
        raise EmbeddingError("requires finite increasing float64 radial knots starting at zero")
    if (ls.ndim != 1 or not len(ls) or ls.dtype.kind not in "iu" or np.any(ls < state.m)
            or np.any(np.diff(ls) <= 0)):
        raise EmbeddingError("invalid ordered angular basis")
    if (coef.dtype != np.float64 or coef.shape != (len(ls), (len(mesh)-1)*degree+1)
            or not np.isfinite(coef).all()):
        raise EmbeddingError("requires finite real float64 FEM coefficients")
    if np.any(coef[:, [0, -1]] != 0.):
        raise EmbeddingError("requires exact finite-box Dirichlet endpoint coefficients")
    if state.metadata.get("radial_quadrature", 0) < degree+1:
        raise EmbeddingError("provider mass assembly must exactly integrate FEM products")
    return mesh, int(ls[-1]), degree


def _digest_arrays(metadata, arrays):
    h = hashlib.sha256(json.dumps(metadata, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
    for a in arrays:
        b = np.ascontiguousarray(a, dtype="<f8")
        h.update(json.dumps(list(b.shape), separators=(",", ":")).encode())
        h.update(b.tobytes())
    return h.hexdigest()


@dataclass(frozen=True)
class CommonGrid:
    boundaries: np.ndarray
    r: np.ndarray
    dr: np.ndarray
    eta: np.ndarray
    deta: np.ndarray
    phi: np.ndarray
    dphi: np.ndarray
    weights: np.ndarray
    ZA: float
    ZB: float
    rmax: float
    degree_max: int
    lmax: int
    mmax: int
    radial_order: int
    eta_order: int
    phi_count: int
    embedding_id: str
    metric_id: str
    hilbert_space_id: str

    @property
    def point_count(self):
        return len(self.weights)

    @property
    def shape(self):
        return len(self.r), len(self.eta), len(self.phi)

    def allocation_estimate(self, columns):
        """Conservative array accounting, not measured process RSS.

        Snapshot copies its arrays; caller output and copied frame may coexist.
        A single meridional table avoids an l-by-full-3D-grid allocation.
        """
        columns = _positive_integer(columns, "columns")
        nr, ne, _ = self.shape
        return {"points": self.point_count, "columns": columns,
                "frame_bytes": self.point_count*columns*16,
                "two_frames_plus_weights_bytes": self.point_count*(columns*32+16),
                "single_state_meridional_bytes": nr*ne*8,
                "scope": "array accounting only; not a process memory bound"}


def build_common_grid(states, *, radial_order=None, eta_order=None, phi_count=5,
                      max_points=2_000_000, extra_radial_knots=()):
    """Build one immutable tensor grid for every supplied R and sector.

    Tensor ordering is r, eta, phi (phi fastest). All quadrature weights are
    physical r**2 dr d eta d phi and strictly positive. The coordinate origin
    is the common O origin; translated B/prolate data are deliberately rejected.
    """
    states = tuple(states)
    if not states:
        raise EmbeddingError("at least one state is required")
    specs = [_state_contract(s) for s in states]
    first = states[0]
    za, zb, rmax = float(first.ZA), float(first.ZB), float(specs[0][0][-1])
    if any((s.ZA, s.ZB, float(mesh[-1])) != (za, zb, rmax)
           for s, (mesh, _, _) in zip(states, specs)):
        raise EmbeddingError("all states must share charges, O origin, and physical rmax")
    degree_max = max(x[2] for x in specs)
    lmax = max(x[1] for x in specs)
    mmax = max(s.m for s in states)
    radial_order = degree_max+1 if radial_order is None else _positive_integer(radial_order, "radial_order", degree_max+1)
    eta_order = lmax+1 if eta_order is None else _positive_integer(eta_order, "eta_order", lmax+1)
    phi_count = _positive_integer(phi_count, "phi_count", 2*mmax+1)
    max_points = _positive_integer(max_points, "max_points")
    extra = np.asarray(extra_radial_knots, dtype=float)
    if extra.ndim != 1 or not np.isfinite(extra).all() or np.any(extra <= 0) or np.any(extra >= rmax):
        raise EmbeddingError("extra radial knots must be finite and strictly inside the common box")
    mesh = np.unique(np.concatenate([x[0] for x in specs]+[extra]))
    point_count = (len(mesh)-1)*radial_order*eta_order*phi_count
    if point_count > max_points:
        raise EmbeddingError(f"grid point budget exceeded: {point_count} > {max_points}")
    q, qw = leggauss(radial_order)
    lo, jac = mesh[:-1, None], np.diff(mesh)[:, None]/2
    r, dr = (lo+jac*(q+1)).ravel(), (jac*qw).ravel()
    eta, deta = leggauss(eta_order)
    phi = np.arange(phi_count, dtype=float)*(2*np.pi/phi_count)
    dphi = np.full(phi_count, 2*np.pi/phi_count)
    weights = ((r*r*dr)[:, None, None]*deta[None, :, None]*dphi[None, None, :]).ravel()
    if np.any(r <= 0) or not np.isfinite(weights).all() or np.any(weights <= 0):
        raise EmbeddingError("nonpositive or nonfinite physical quadrature")
    spec = {"schema": "C2g_O_physical_grid_v1", "ZA": za, "ZB": zb, "rmax": rmax,
            "coordinate_unit": "a_A", "order": "r_eta_phi", "azimuth": "exp(i*m*phi)/sqrt(2*pi); noCS"}
    digest = _digest_arrays(spec, (mesh, r, dr, eta, deta, phi, dphi, weights))
    hilbert = "L2_R3_O_zeroextended_ball:"+_digest_arrays({"ZA": za, "ZB": zb, "rmax": rmax, "unit": "a_A"}, ())
    return CommonGrid(*[_readonly(a) for a in (mesh, r, dr, eta, deta, phi, dphi, weights)],
                      za, zb, rmax, degree_max, lmax, mmax, radial_order, eta_order, phi_count,
                      "C2g_O_grid:"+digest, "C2g_positive_physical_W:"+digest, hilbert)


def embed_state(state, grid, *, m_signed=None):
    mesh, lmax, degree = _state_contract(state)
    if not isinstance(grid, CommonGrid):
        raise EmbeddingError("typed CommonGrid required")
    if ((state.ZA, state.ZB, float(mesh[-1])) != (grid.ZA, grid.ZB, grid.rmax)
            or degree > grid.degree_max or lmax > grid.lmax or state.m > grid.mmax
            or not np.isin(mesh, grid.boundaries).all()):
        raise EmbeddingError("state is not represented by this common physical grid")
    m_signed = state.m if m_signed is None else m_signed
    if isinstance(m_signed, (bool, np.bool_)) or m_signed not in ((0,) if state.m == 0 else (-1, 1)):
        raise EmbeddingError("requested m must equal the provider |m| sector")
    radial = state.radial(grid.r)
    angular_table = np.stack([angular(int(l), state.m, grid.eta) for l in state.ls])
    meridional = (radial.T @ angular_table)/grid.r[:, None]
    phase = np.exp(1j*m_signed*grid.phi)/math.sqrt(2*np.pi)
    return np.asarray((meridional[:, :, None]*phase[None, None, :]).ravel(), dtype=np.complex128)


def _verified_archives(archives):
    """Bind in-memory content to the declared bytes, including mutable metadata."""
    from multistate_provider import SectorArchive, load_sector
    verified = []
    for archive in archives:
        if not isinstance(archive, SectorArchive):
            raise EmbeddingError("typed loaded SectorArchive required")
        fresh = load_sector(archive.source_path, expected_sha256=archive.source_sha256)
        if (fresh.source_id, fresh.source_bytes, fresh.state_ids) != (archive.source_id, archive.source_bytes, archive.state_ids):
            raise EmbeddingError("archive identity differs from actual source bytes")
        a, b = archive.result, fresh.result
        if (len(a.states) != len(b.states) or a.metadata != b.metadata
                or any(not np.array_equal(getattr(a, key), getattr(b, key))
                       for key in ("projected_operator", "mass_gram", "coefficient_vectors"))):
            raise EmbeddingError("in-memory sector result differs from actual source bytes")
        for left, right in zip(a.states, b.states):
            scalar_names = ("R", "ZA", "ZB", "m", "degree", "energy", "residual", "mass_norm", "phase_probe", "metadata")
            if (any(getattr(left, name) != getattr(right, name) for name in scalar_names)
                    or any(not np.array_equal(getattr(left, name), getattr(right, name))
                           for name in ("ls", "boundaries", "coefficients"))):
                raise EmbeddingError("in-memory state differs from actual source bytes")
        verified.append(fresh)
    return tuple(verified)


def _archive_binding(archives):
    records = []
    for archive in archives:
        path = Path(archive.source_path)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != archive.source_sha256 or len(data) != archive.source_bytes:
            raise EmbeddingError("sector archive bytes changed after load")
        states = archive.result.states
        if not states or len(archive.state_ids) != len(states):
            raise EmbeddingError("invalid sector archive state identifiers")
        first = states[0]
        records.append({"source_id": archive.source_id, "sha256": digest, "bytes": len(data),
                        "state_ids": list(archive.state_ids), "m": first.m, "R": first.R,
                        "ZA": first.ZA, "ZB": first.ZB, "root_count": len(states)})
    if len({r["source_id"] for r in records}) != len(records):
        raise EmbeddingError("duplicate source IDs")
    return sorted(records, key=lambda x: (x["m"], x["source_id"]))


def _binding_bytes(archives, source_id):
    if not isinstance(source_id, str) or not source_id.strip():
        raise EmbeddingError("nonempty source binding ID required")
    obj = {"schema": "C2g_sector_source_binding_v1", "source_id": source_id,
           "archives": _archive_binding(archives)}
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def write_source_binding(archives, path, *, source_id):
    """Write create-only/fsynced actual binding bytes; never alter an archive."""
    data = _binding_bytes(_verified_archives(tuple(archives)), source_id)
    path = Path(path)
    fd, pending = tempfile.mkstemp(prefix="."+path.name+".", suffix=".pending", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(pending, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(pending):
            os.unlink(pending)
    return {"source_id": source_id, "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "path": str(path)}


@dataclass(frozen=True)
class EmbeddedSnapshot:
    snapshot: Snapshot
    provenance: dict
    selected_galerkin_operator: np.ndarray


def snapshot_from_archives(archives, grid, *, source_binding_path,
                           gram_identity_atol, selected_roots=None):
    """Make the fixed rank-five candidate and all provided exterior guards.

    m=0 roots 1,2,3 and |m|=1 root 0 are the default selected ordinals. This
    ordering is a declared finite-R candidate, not established atomic tracking.
    Every m=1 root (selected or guard) obtains explicit +m and -m partners.
    """
    archives = _verified_archives(tuple(archives))
    if (isinstance(gram_identity_atol, (bool, np.bool_)) or not np.isfinite(gram_identity_atol)
            or not 0 < gram_identity_atol <= 1e-6):
        raise EmbeddingError("explicit gram_identity_atol in (0,1e-6] required")
    if len(archives) != 2 or {a.result.states[0].m for a in archives} != {0, 1}:
        raise EmbeddingError("exactly one m=0 and one |m|=1 sector archive required")
    archives = tuple(sorted(archives, key=lambda a: a.result.states[0].m))
    binding_path = Path(source_binding_path)
    binding = binding_path.read_bytes()
    try:
        source_id = json.loads(binding)["source_id"]
    except (ValueError, KeyError, TypeError) as exc:
        raise EmbeddingError("invalid source binding bytes") from exc
    if binding != _binding_bytes(archives, source_id):
        raise EmbeddingError("source binding does not match the exact sector archives")
    selected_roots = {0: (1, 2, 3), 1: (0,)} if selected_roots is None else selected_roots
    if (set(selected_roots) != {0, 1} or len(selected_roots[0]) != 3 or len(selected_roots[1]) != 1
            or 0 in selected_roots[0]):
        raise EmbeddingError("requires ground-excluded candidate ranks (3,1,1)")
    coordinates = {(s.R, s.ZA, s.ZB) for a in archives for s in a.result.states}
    if len(coordinates) != 1:
        raise EmbeddingError("one Snapshot must have one R and charge pair")
    columns, records, source_map, blocks, gram_errors = [], [], [], [], []
    for archive in archives:
        states = archive.result.states
        m = states[0].m
        chosen = tuple(selected_roots[m])
        if (len(set(chosen)) != len(chosen) or any(isinstance(j, (bool, np.bool_))
                or not isinstance(j, (int, np.integer)) or j < 0 or j >= len(states) for j in chosen)):
            raise EmbeddingError("invalid selected root ordinals")
        if any(s.m != m for s in states):
            raise EmbeddingError("sector archive mixes |m| values")
        n = len(states)
        mass = np.asarray(archive.result.mass_gram)
        op = np.asarray(archive.result.projected_operator)
        if (mass.shape != (n, n) or op.shape != (n, n) or mass.dtype != np.float64
                or op.dtype != np.float64 or not np.isfinite(mass).all() or not np.isfinite(op).all()):
            raise EmbeddingError("invalid actual finite Galerkin matrices")
        base = np.column_stack([embed_state(s, grid) for s in states])
        measured_mass = base.conj().T @ (grid.weights[:, None]*base)
        gram_error = float(np.max(np.abs(measured_mass-mass)))
        if gram_error > gram_identity_atol:
            raise EmbeddingError("embedded Gram disagrees with provider finite mass form")
        gram_errors.append({"m_abs": m, "max_abs_error": gram_error})
        for signed_m in ((0,) if m == 0 else (1, -1)):
            start = len(columns)
            for j, state in enumerate(states):
                sid = StateID(archive.state_ids[j]+f":m={signed_m:+d}")
                partner = () if m == 0 else (StateID(archive.state_ids[j]+f":m={-signed_m:+d}"),)
                columns.append(base[:, j] if signed_m >= 0 else base[:, j].conj())
                records.append(StateRecord(sid, signed_m, float(state.energy), float(state.residual),
                                           Role.SELECTED if j in chosen else Role.GUARD,
                                           is_ground=(m == 0 and j == 0), known_degenerate_partners=partner))
                source_map.append({"state_id": sid.value, "archive_source_id": archive.source_id,
                                   "archive_sha256": archive.source_sha256, "source_root_ordinal": j,
                                   "m": signed_m, "reconstructed_conjugate": signed_m < 0,
                                   "energy_and_residual": "copied from the same real finite-sector Ritz root"})
            blocks.append((start, n, op))
    frame = np.column_stack(columns)
    full_op = np.zeros((len(columns), len(columns)), dtype=np.complex128)
    for start, n, op in blocks:
        full_op[start:start+n, start:start+n] = op
    selected = [j for j, record in enumerate(records) if record.role is Role.SELECTED]
    hsmall = full_op[np.ix_(selected, selected)]
    if np.max(np.abs(hsmall-hsmall.conj().T)) > gram_identity_atol:
        raise EmbeddingError("finite Galerkin selected operator is not Hermitian within registered tolerance")
    representation = Representation(grid.embedding_id, grid.metric_id, grid.hilbert_space_id,
        "electronic_Coulomb_E_A_zero_at_electron_infinity_nuclear_repulsion_omitted", "E_A", "a_A",
        source_id, hashlib.sha256(binding).hexdigest(), "finite_sector_subset", (0, 1, -1), True, 0.)
    snapshot = Snapshot(float(next(iter(coordinates))[0]), frame, grid.weights, tuple(records),
                        representation, selected_projected_operator=hsmall)
    hsmall = np.array(hsmall, copy=True)
    hsmall.setflags(write=False)
    provenance = {"schema": "C2g_common_embedding_provenance_v1", "source_binding_path": str(binding_path),
        "source_binding_sha256": representation.source_sha256, "source_binding_bytes": len(binding),
        "states": source_map, "grid_shape": list(grid.shape), "point_count": grid.point_count,
        "radial_order": grid.radial_order, "eta_order": grid.eta_order, "phi_count": grid.phi_count,
        "origin": "common charge-center O", "units": "a_A,E_A", "finite_box_rmax": grid.rmax,
        "mass_isometry_checks": gram_errors, "mass_isometry_atol": float(gram_identity_atol),
        "selected_root_ordinals": {str(k): list(v) for k, v in selected_roots.items()},
        "hamiltonian_scope": "actual finite Galerkin weak-form operator induced on the embedded FEM span",
        "hamiltonian_embedding_formula": "H_emb=E M^-1 H M^-1 E^dagger W; (EC)^dagger W H_emb(EC)=C^dagger H C",
        "pointwise_PDE_H_apply": False, "PDE_residual_certified": False,
        "continuum_certificate": False, "omitted_tail_certificate": False,
        "atomic_correlation_proven": False, "full_C2_closed": False,
        "azimuth_convention": "psi_m=G exp(i m phi)/sqrt(2*pi); psi_-m=conj(psi_+m); no Condon-Shortley phase",
        "real_bright": "(psi_+1+psi_-1)/sqrt(2)",
        "real_dark": "(psi_+1-psi_-1)/(i sqrt(2))",
        "residual_scope": "provider relative Euclidean finite generalized-matrix residual; copied unchanged",
        "allocation_estimate": grid.allocation_estimate(len(records))}
    return EmbeddedSnapshot(snapshot, provenance, hsmall)
