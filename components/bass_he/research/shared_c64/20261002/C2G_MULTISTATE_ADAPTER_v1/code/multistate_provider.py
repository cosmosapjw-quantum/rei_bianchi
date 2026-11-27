"""Create-only, pickle-free archives for finite-sector molecular Ritz states.

These archives bind actual source bytes, individual ordinal IDs, coefficient
vectors, finite Galerkin operator, and mass metric. They do not certify a PDE
residual, complete spectrum, continuum gap, or finite-R atomic correlation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

import numpy as np

from optimized_solver import MultiStateResult, PartialWaveState, RESIDUAL_DEFINITION

SCHEMA = "bass-he-c2g-finite-sector-v1"
_ARRAY_NAMES = {"metadata_json", "ls", "boundaries", "coefficients", "energies",
                "residuals", "mass_norms", "phase_probes", "projected_operator",
                "mass_gram", "coefficient_vectors"}
_MAX_ARCHIVE_BYTES = 512 * 1024**2


@dataclass(frozen=True)
class SectorArchive:
    result: MultiStateResult
    source_id: str
    source_sha256: str
    source_bytes: int
    source_path: Path
    state_ids: tuple[str, ...]
    content_sha256: str


def _source_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/+\-]{0,199}", value):
        raise ValueError("source_id must be a nonempty stable ASCII identifier (maximum 200 characters)")
    return value


def _state_ids(source_id, n):
    return tuple(f"{source_id}:root:{j:04d}" for j in range(n))


def _json_load(payload):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key")
            out[key] = value
        return out
    return json.loads(payload, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON constant")))


def _validate_result(result):
    if not isinstance(result, MultiStateResult):
        raise TypeError("result must be MultiStateResult")
    states = result.states
    first = states[0]
    if first.m not in (0, 1) or isinstance(first.m, bool):
        raise ValueError("archive sector must be m=0 or real cosine m=1")
    if first.degree < 2 or int(first.degree) != first.degree:
        raise ValueError("invalid FEM polynomial degree")
    ls = np.asarray(first.ls)
    mesh = np.asarray(first.boundaries)
    if (ls.dtype != np.dtype(np.int64) or ls.ndim != 1 or len(ls) < 1
            or not np.array_equal(ls, np.arange(first.m, int(ls[-1])+1))):
        raise ValueError("invalid contiguous angular indices")
    if (mesh.dtype != np.dtype(np.float64) or mesh.ndim != 1 or len(mesh) < 3
            or mesh[0] != 0 or np.any(np.diff(mesh) <= 0) or not np.isfinite(mesh).all()):
        raise ValueError("invalid finite radial boundaries")
    nr = (len(mesh)-1)*first.degree-1
    k = len(states)
    if result.coefficient_vectors.shape != (len(ls)*nr, k):
        raise ValueError("coefficient matrix and FEM dimensions disagree")
    last_energy = -np.inf
    for j, state in enumerate(states):
        vals = (state.R, state.ZA, state.ZB, state.energy, state.residual,
                state.mass_norm, state.phase_probe)
        if not np.isfinite(vals).all() or state.R < 0 or state.ZA < 0 or state.ZB < 0 or state.ZA+state.ZB <= 0:
            raise ValueError("state has nonfinite or invalid scalar data")
        if state.residual < 0 or state.mass_norm <= 0 or state.energy < last_energy:
            raise ValueError("states require nonnegative residual, positive norm and sorted energy")
        last_energy = state.energy
        if (state.R, state.ZA, state.ZB, state.m, state.degree) != (first.R, first.ZA, first.ZB, first.m, first.degree):
            raise ValueError("archive mixes incompatible physical parameters or sectors")
        if not np.array_equal(state.ls, ls) or not np.array_equal(state.boundaries, mesh):
            raise ValueError("archive mixes finite basis layouts")
        c = np.asarray(state.coefficients)
        if c.dtype != np.dtype(np.float64) or c.shape != (len(ls), nr+2) or not np.isfinite(c).all():
            raise ValueError("invalid state coefficient array")
        if np.any(c[:, (0, -1)] != 0):
            raise ValueError("finite-box Dirichlet endpoint coefficients must be zero")
        if not np.array_equal(c[:, 1:-1].reshape(-1), result.coefficient_vectors[:, j]):
            raise ValueError("state and returned eigenvector coefficients disagree")
        if state.metadata.get("source_ordinal") != j:
            raise ValueError("state source ordinal is missing or incorrect")
        if state.metadata.get("residual_definition") != RESIDUAL_DEFINITION:
            raise ValueError("state algebraic residual definition is missing or changed")
        if state.mass_norm != result.mass_gram[j, j]:
            raise ValueError("state norm and returned mass Gram disagree")
    if np.any(np.diag(result.mass_gram) <= 0):
        raise ValueError("mass Gram requires positive diagonal")
    for a, label in ((result.mass_gram, "mass Gram"), (result.projected_operator, "projected operator")):
        if np.max(np.abs(a-a.T)) > 1e-11*max(1., np.linalg.norm(a, ord=np.inf)):
            raise ValueError(f"{label} is not numerically symmetric")
    if result.metadata.get("residual_definition") != RESIDUAL_DEFINITION:
        raise ValueError("result algebraic residual definition is missing or changed")
    source_hashes = result.metadata.get("source_files_sha256")
    if (not isinstance(source_hashes, dict) or not source_hashes
            or any(not isinstance(v, str) or not re.fullmatch("[0-9a-f]{64}", v) for v in source_hashes.values())):
        raise ValueError("observed solver source hashes are missing or invalid")
    if result.metadata.get("backend") not in ("numpy", "native", "manufactured-test"):
        raise ValueError("explicit backend identity is missing")
    if result.metadata.get("backend") == "native":
        native = result.metadata.get("native_library")
        if not isinstance(native, dict) or not re.fullmatch("[0-9a-f]{64}", native.get("library_sha256", "")):
            raise ValueError("native library identity is missing")
    # JSON serialization below rejects NaN/Inf anywhere in nested metadata.
    json.dumps(result.metadata, allow_nan=False)
    return first


def _result_fingerprint(result):
    """Bind mutable compatibility state objects to the exact data loaded."""
    h = hashlib.sha256()
    doc = {"metadata": result.metadata, "states": [
        {"R": s.R, "ZA": s.ZA, "ZB": s.ZB, "m": s.m, "degree": s.degree,
         "energy": s.energy, "residual": s.residual, "mass_norm": s.mass_norm,
         "phase_probe": s.phase_probe, "metadata": s.metadata} for s in result.states]}
    h.update(json.dumps(doc, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    arrays = [result.projected_operator, result.mass_gram, result.coefficient_vectors]
    for state in result.states:
        arrays.extend((state.ls, state.boundaries, state.coefficients))
    for array in arrays:
        array = np.asarray(array)
        h.update(str((array.dtype.str, array.shape)).encode("ascii"))
        h.update(array.tobytes(order="C"))
    return h.hexdigest()


def save_sector(result: MultiStateResult, path, source_id: str) -> dict:
    """Persist an exact finite-sector result without overwriting any prior file.

    Writes a same-directory temporary file, fsyncs it, and atomically hardlinks
    into the create-only destination. Directory fsync makes the new name durable.
    """
    source_id = _source_id(source_id)
    first = _validate_result(result)
    path = Path(path).expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    ids = _state_ids(source_id, len(result.states))
    doc = {"schema": SCHEMA, "source_id": source_id, "state_ids": ids,
           "R": first.R, "ZA": first.ZA, "ZB": first.ZB, "m": first.m,
           "degree": first.degree, "metadata": result.metadata,
           "state_metadata": [state.metadata for state in result.states],
           "archive_writer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    metadata = np.frombuffer(json.dumps(doc, ensure_ascii=True, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8"), dtype=np.uint8)
    arrays = dict(metadata_json=metadata, ls=first.ls, boundaries=first.boundaries,
        coefficients=np.stack([s.coefficients for s in result.states]),
        energies=np.array([s.energy for s in result.states], dtype=np.float64),
        residuals=np.array([s.residual for s in result.states], dtype=np.float64),
        mass_norms=np.array([s.mass_norm for s in result.states], dtype=np.float64),
        phase_probes=np.array([s.phase_probe for s in result.states], dtype=np.float64),
        projected_operator=result.projected_operator, mass_gram=result.mass_gram,
        coefficient_vectors=result.coefficient_vectors)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".pending", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(name, path)
        dir_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    payload = path.read_bytes()
    return {"source_id": source_id, "source_sha256": hashlib.sha256(payload).hexdigest(),
            "source_bytes": len(payload), "source_path": str(path), "state_ids": list(ids)}


def load_sector(path, expected_sha256=None) -> SectorArchive:
    """Load only this exact archive schema, disallowing pickle and object arrays."""
    path = Path(path).expanduser().resolve(strict=True)
    if not path.is_file() or path.stat().st_size > _MAX_ARCHIVE_BYTES:
        raise ValueError("sector archive is absent, nonregular or over size limit")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("archive SHA-256 differs from expected source bytes")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != {k+".npy" for k in _ARRAY_NAMES}:
            raise ValueError("unexpected or duplicate archive members")
        if sum(info.file_size for info in z.infolist()) > _MAX_ARCHIVE_BYTES:
            raise ValueError("expanded archive exceeds size limit")
    with np.load(io.BytesIO(payload), allow_pickle=False) as z:
        arrays = {name: z[name] for name in _ARRAY_NAMES}
    if arrays["metadata_json"].dtype != np.dtype(np.uint8) or arrays["metadata_json"].ndim != 1:
        raise ValueError("metadata must be a UTF-8 uint8 vector")
    doc = _json_load(arrays["metadata_json"].tobytes().decode("utf-8"))
    expected_doc = {"schema", "source_id", "state_ids", "R", "ZA", "ZB", "m", "degree", "metadata", "state_metadata", "archive_writer_sha256"}
    if not isinstance(doc, dict) or set(doc) != expected_doc or doc["schema"] != SCHEMA:
        raise ValueError("unsupported archive schema")
    source_id = _source_id(doc["source_id"])
    k = len(arrays["energies"])
    if tuple(doc["state_ids"]) != _state_ids(source_id, k) or len(doc["state_metadata"]) != k:
        raise ValueError("state ordinal IDs or metadata count mismatch")
    if not re.fullmatch("[0-9a-f]{64}", doc["archive_writer_sha256"]):
        raise ValueError("archive writer digest is invalid")
    for name, value in arrays.items():
        dtype = np.uint8 if name == "metadata_json" else np.int64 if name == "ls" else np.float64
        if value.dtype != np.dtype(dtype) or not np.isfinite(value).all():
            raise ValueError(f"wrong dtype or nonfinite values for {name}")
    for name in ("energies", "residuals", "mass_norms", "phase_probes"):
        if arrays[name].shape != (k,):
            raise ValueError(f"wrong scalar array shape for {name}")
    if arrays["coefficients"].ndim != 3 or arrays["coefficients"].shape[0] != k:
        raise ValueError("coefficient state count mismatch")
    states = []
    for j in range(k):
        state = PartialWaveState(doc["R"], doc["ZA"], doc["ZB"], doc["m"],
            arrays["ls"].copy(), arrays["boundaries"].copy(), doc["degree"],
            arrays["coefficients"][j].copy(), float(arrays["energies"][j]),
            float(arrays["residuals"][j]), float(arrays["mass_norms"][j]),
            float(arrays["phase_probes"][j]), doc["state_metadata"][j])
        states.append(state)
    result = MultiStateResult(tuple(states), arrays["projected_operator"], arrays["mass_gram"],
                              arrays["coefficient_vectors"], doc["metadata"])
    _validate_result(result)
    for state in result.states:
        state.ls.setflags(write=False)
        state.boundaries.setflags(write=False)
        state.coefficients.setflags(write=False)
    return SectorArchive(result, source_id, digest, len(payload), path, tuple(doc["state_ids"]),
                         _result_fingerprint(result))


def validate_identity(archive: SectorArchive) -> None:
    """Refuse a changed or missing source archive before downstream binding."""
    if not isinstance(archive, SectorArchive):
        raise TypeError("archive must be SectorArchive")
    if _result_fingerprint(archive.result) != archive.content_sha256:
        raise ValueError("in-memory sector data changed after load")
    payload = archive.source_path.read_bytes()
    if len(payload) != archive.source_bytes or hashlib.sha256(payload).hexdigest() != archive.source_sha256:
        raise ValueError("sector archive source bytes changed after load")
