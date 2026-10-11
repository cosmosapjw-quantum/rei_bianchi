"""Create-only, two-boundary checkpoints for a single accepted-history owner.

The immutable legacy seed owns the old full prefix. Each new generation owns
exactly the two newly accepted natural boundaries, with the preceding manifest
hash in its manifest. This changes storage, not the physical representation or
the existing domain/ledger criteria. No integrator internals are serialized.

``load_latest`` reads only the compact seed and final segment arrays. On first
open it checks the manifest chain and historical member names/sizes, without
rehashing historical NPZ payloads. ``iter_states`` and ``verify_history`` check
each payload they actually read. These scopes are deliberately distinct.

A coordinator must own the run journal. A short nonblocking advisory lock also
excludes overlapping store mutations; stale coordinator instances fail closed.
An atomic accepted checkpoint can reconcile a lost journal commit, never an
unresolved numerical trial. Orphan temporary directories are preserved and
block further use until explicitly investigated.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid
from contextlib import contextmanager

import numpy as np

Q1B = Path(__file__).resolve().parents[1]
for _directory in (Q1B / "c10", Q1B / "checkpoint",
                   Q1B / "c11/integration/production"):
    if str(_directory) not in sys.path:
        sys.path.insert(0, str(_directory))
from atomic_checkpoint import _rename_no_replace
from entry_checkpoint import (COUNTERS, make_entry_snapshot, pack_entry_state,
                              unpack_entry_state, validate_entry_snapshot)
from production_journal import validate_cursor

SCHEMA = "rei.hpc.segmented_checkpoint.v1"
MEMBERS = {"arrays.npz", "metadata.json"}
STATE_ARRAYS = {"clock", "packed", "R", "support", "scales", "accepted_min",
                "accepted_max", "counter_origins"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
GENERATION = re.compile(r"gen-([0-9]{8})\Z")


class SegmentedCheckpointError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise SegmentedCheckpointError(message)


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def json_bytes(value):
    try:
        return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False,
                           default=_json_default) + "\n").encode()
    except (TypeError, ValueError) as exc:
        raise SegmentedCheckpointError("FINITE_JSON_REQUIRED") from exc


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fsync(directory):
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path, data):
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _generation(number):
    require(type(number) is int and 0 <= number <= 99999999, "GENERATION_DOMAIN")
    return f"gen-{number:08d}"


def _reference(generation, digest):
    return dict(generation=generation, manifest_sha256=digest, storage=SCHEMA)


def _binary64(array, label):
    require(isinstance(array, np.ndarray) and array.dtype == np.dtype("float64")
            and np.isfinite(array).all(), "FINITE_BINARY64_REQUIRED:" + label)
    return array.copy()


def _natural(loaded, index, shape):
    arrays, metadata = loaded["arrays"], loaded["metadata"]
    state = unpack_entry_state(arrays["prefix_state"][index], metadata["cell_count"])
    for key in ("N", "U_eV"):
        state[key] = state[key].reshape(shape)
    state.update(t_s=float(arrays["prefix_clock"][index]),
                 nH_ref=metadata["nH_ref"], nHe_ref=metadata["nHe_ref"],
                 R=np.asarray(metadata["prefix_R"][index], dtype=np.float64).reshape(shape),
                 support=np.asarray(metadata["prefix_support"][index],
                                    dtype=np.float64).reshape((*shape, 2)))
    actual_index = index if index >= 0 else len(arrays["prefix_clock"]) + index
    diagnostics = metadata.get("production_kernel_history", {}).get(str(actual_index))
    if diagnostics is not None:
        state["diagnostics"] = copy.deepcopy(diagnostics)
    return state


class SegmentedStore:
    def __init__(self, directory, *, legacy_directory=None):
        self.directory = Path(directory).resolve()
        self.legacy_directory = None if legacy_directory is None else Path(legacy_directory).resolve()
        self._head = None
        self._seed = None
        self._manifests = {}
        self._loaded = {}

    @contextmanager
    def _writer(self):
        missing = []
        ancestor = self.directory
        while not ancestor.exists():
            missing.append(ancestor)
            ancestor = ancestor.parent
        self.directory.mkdir(parents=True, exist_ok=True)
        for created in missing:
            _fsync(created)
            _fsync(created.parent)
        require(not self.directory.is_symlink(), "STORE_SYMLINK")
        with (self.directory / "WRITE.lock").open("a+b") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise SegmentedCheckpointError("ANOTHER_STORE_WRITER") from exc
            try:
                self._check_temporary()
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _check_temporary(self):
        if self.directory.exists():
            require(not any(p.name.startswith(".tmp-") for p in self.directory.iterdir()),
                    "ORPHAN_TEMP_FAILS_CLOSED")

    def _publish(self, name, arrays, metadata, manifest):
        """Only the final rename establishes a resumable accepted generation."""
        target = self.directory / name
        require(not target.exists(), "CREATE_ONLY_COLLISION:" + name)
        temporary = self.directory / (".tmp-" + name + "-" + uuid.uuid4().hex)
        temporary.mkdir()
        with (temporary / "arrays.npz").open("xb") as handle:
            # Uncompressed numeric NPZ avoids compression CPU in the coordinator.
            np.savez(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
        _write(temporary / "metadata.json", json_bytes(metadata))
        manifest = copy.deepcopy(manifest)
        manifest.update(schema=SCHEMA, files={name: dict(bytes=(temporary / name).stat().st_size,
                                                        sha256=sha(temporary / name))
                                            for name in sorted(MEMBERS)},
                        scientific_admission=False, internal_integrator_state_saved=False,
                        remote_durability="NOT_ESTABLISHED_BY_LOCAL_PUBLICATION")
        _write(temporary / "manifest.json", json_bytes(manifest))
        _fsync(temporary)
        _rename_no_replace(temporary, target)
        _fsync(self.directory)
        return _reference(manifest["generation"], sha(target / "manifest.json"))

    def initialize(self, seed_directory, seed_reference, seed_loaded, *, shape,
                   runtime_binding=None):
        """Bind an already admitted legacy seed without rerunning its old gates.

        ``seed_loaded`` is the caller's identity-checked legacy arrays/metadata.
        The original metadata and manifest reference remain authoritative. A new
        HPC allocation is stored separately as ``hpc_runtime_binding``.
        """
        seed_directory = Path(seed_directory).resolve()
        seed_reference = copy.deepcopy(seed_reference)
        shape = tuple(shape)
        require(shape and all(type(n) is int and n > 0 for n in shape), "STATE_SHAPE")
        generation = seed_reference.get("generation")
        path = seed_directory / _generation(generation)
        require(HEX.fullmatch(seed_reference.get("manifest_sha256", "")) is not None,
                "SEED_MANIFEST_HASH_FORMAT")
        require(sha(path / "manifest.json") == seed_reference["manifest_sha256"],
                "SEED_MANIFEST_IDENTITY")
        manifest = json.loads((path / "manifest.json").read_text())
        require(manifest.get("generation") == generation, "SEED_GENERATION")
        for filename in ("metadata.json", "identity.json"):
            info = manifest["files"][filename]
            require((path / filename).stat().st_size == info["bytes"] and
                    sha(path / filename) == info["sha256"], "SEED_METADATA_IDENTITY")
        require(json.loads((path / "metadata.json").read_text()) == seed_loaded["metadata"] and
                json.loads((path / "identity.json").read_text()) == seed_loaded["identity"],
                "SEED_LOADED_METADATA_MISMATCH")
        old_arrays, old_metadata = seed_loaded["arrays"], seed_loaded["metadata"]
        cursor = old_metadata["adaptive_cursor"]
        validate_cursor(cursor)
        require(cursor["accepted_macros"] == generation and
                len(old_arrays["prefix_clock"]) == cursor["accepted_boundaries"] + 1 and
                old_arrays["prefix_clock"][0] == 0.0 and
                old_arrays["prefix_clock"][-1] == cursor["accepted_clock_s"],
                "SEED_CURSOR_PREFIX")
        require(math.prod(shape) == old_metadata["cell_count"], "SEED_CELL_SHAPE")
        initial, final = _natural(seed_loaded, 0, shape), _natural(seed_loaded, -1, shape)
        arrays = self._pack_pair((initial, final), shape)
        for key in ("scales", "accepted_min", "accepted_max", "counter_origins"):
            arrays[key] = _binary64(old_arrays[key], "seed_" + key)
        base = copy.deepcopy(old_metadata)
        # Kept by reference in the legacy seed, materialized only on export.
        for key in ("prefix_R", "prefix_support", "production_kernel_history"):
            base.pop(key, None)
        metadata = dict(kind="seed", legacy_directory=str(seed_directory),
                        legacy_checkpoint=seed_reference, legacy_identity=seed_loaded["identity"],
                        seed_metadata=base, shape=list(shape), cursor=cursor,
                        prefix_count=cursor["accepted_boundaries"] + 1,
                        hpc_runtime_binding=copy.deepcopy(runtime_binding),
                        diagnostics=[initial.get("diagnostics"), final.get("diagnostics")],
                        validation_scope="INHERIT_PREVIOUSLY_VALIDATED_LEGACY_PREFIX_NO_NUMERICAL_REPLAY",
                        legacy_array_identity_scope="CALLER_VERIFIED_PAYLOAD_NOT_REHASHED_BY_INITIALIZE")
        with self._writer():
            if (self.directory / "seed").exists():
                self._scan()
                require(self._seed["metadata"] == json.loads(json_bytes(metadata)), "SEED_REINITIALIZATION_DRIFT")
                return copy.deepcopy(self._seed["checkpoint"])
            require(not any(GENERATION.fullmatch(p.name) for p in self.directory.iterdir()),
                    "SEGMENTS_WITHOUT_SEED")
            reference = self._publish("seed", arrays, metadata,
                                      dict(kind="seed", generation=generation,
                                           prefix_count=cursor["accepted_boundaries"] + 1,
                                           previous_checkpoint=None))
            self._head = None
            self._scan()
            return reference

    def _pack_pair(self, pair, shape):
        require(len(pair) == 2, "EXACTLY_TWO_STATES_REQUIRED")
        values = {"clock": [], "packed": [], "R": [], "support": []}
        for state in pair:
            require(math.isfinite(state["t_s"]), "STATE_CLOCK")
            gas = _binary64(state["gas"], "gas")
            N = _binary64(state["N"], "N")
            U = _binary64(state["U_eV"], "U_eV")
            R = _binary64(state["R"], "R")
            support = _binary64(state["support"], "support")
            require(gas.shape == (4,) and N.shape == U.shape == R.shape == shape and
                    support.shape == (*shape, 2), "NATURAL_STATE_SHAPE")
            require(set(state["counters"]) == set(COUNTERS), "COUNTER_NAMES")
            values["clock"].append(float(state["t_s"]))
            values["packed"].append(pack_entry_state(gas, N.ravel(), U.ravel(), state["counters"]))
            values["R"].append(R)
            values["support"].append(support)
        return {key: np.array(value, dtype=np.float64) for key, value in values.items()}

    def _read_manifest(self, path, expected_generation, *, expected_sha=None):
        require(path.is_dir() and not path.is_symlink(), "MISSING_OR_SYMLINK_SEGMENT")
        require({p.name for p in path.iterdir()} == MEMBERS | {"manifest.json"},
                "PARTIAL_OR_UNEXPECTED_SEGMENT_MEMBERS")
        require(all(p.is_file() and not p.is_symlink() for p in path.iterdir()),
                "SEGMENT_MEMBER_TYPE")
        digest = sha(path / "manifest.json")
        require(expected_sha is None or digest == expected_sha, "MANIFEST_HASH")
        manifest = json.loads((path / "manifest.json").read_text())
        require(manifest.get("schema") == SCHEMA and manifest.get("generation") == expected_generation and
                manifest.get("scientific_admission") is False and
                manifest.get("internal_integrator_state_saved") is False and
                set(manifest.get("files", {})) == MEMBERS, "MANIFEST_SCHEMA")
        for filename, info in manifest["files"].items():
            require(type(info.get("bytes")) is int and info["bytes"] == (path / filename).stat().st_size and
                    isinstance(info.get("sha256"), str) and HEX.fullmatch(info["sha256"]),
                    "HISTORICAL_MEMBER_SIZE_OR_IDENTITY:" + filename)
        return manifest, _reference(expected_generation, digest)

    def _read(self, path, manifest, reference):
        for filename, info in manifest["files"].items():
            require(sha(path / filename) == info["sha256"], "CORRUPT_MEMBER:" + filename)
        try:
            metadata = json.loads((path / "metadata.json").read_text())
            with np.load(path / "arrays.npz", allow_pickle=False) as archive:
                require(set(archive.files) == STATE_ARRAYS, "ARRAY_MEMBER_NAMES")
                arrays = {key: _binary64(archive[key], key) for key in archive.files}
        except (OSError, ValueError, KeyError) as exc:
            if isinstance(exc, SegmentedCheckpointError):
                raise
            raise SegmentedCheckpointError("INVALID_SERIALIZED_SEGMENT") from exc
        validate_cursor(metadata["cursor"])
        cursor = metadata["cursor"]
        require(metadata["prefix_count"] == manifest["prefix_count"] == cursor["accepted_boundaries"] + 1 and
                cursor["accepted_macros"] == reference["generation"] and
                arrays["clock"].shape == (2,) and arrays["clock"][-1] == cursor["accepted_clock_s"],
                "SEGMENT_CURSOR_SHAPE")
        require(isinstance(metadata.get("diagnostics"), list) and len(metadata["diagnostics"]) == 2,
                "DIAGNOSTIC_PAIR")
        if metadata["kind"] == "accepted_pair":
            seed = self._seed["metadata"]
            shape = tuple(seed["shape"])
            dimension = 4 + 2 * math.prod(shape) + len(COUNTERS)
            require(arrays["packed"].shape == (2, dimension) and arrays["R"].shape == (2, *shape) and
                    arrays["support"].shape == (2, *shape, 2) and
                    all(arrays[key].shape == (dimension,) for key in ("scales", "accepted_min", "accepted_max")) and
                    arrays["counter_origins"].shape == (len(COUNTERS),), "SEGMENT_ARRAY_SHAPES")
            require(metadata["hpc_runtime_binding_sha256"] ==
                    hashlib.sha256(json_bytes(seed["hpc_runtime_binding"])).hexdigest(), "HPC_BINDING_CHAIN")
        return dict(arrays=arrays, metadata=metadata, manifest=manifest, checkpoint=reference)

    def _scan(self):
        self._check_temporary()
        require((self.directory / "seed").is_dir(), "MISSING_SEED")
        seed_manifest = json.loads((self.directory / "seed/manifest.json").read_text())
        generation = seed_manifest["generation"]
        manifest, reference = self._read_manifest(self.directory / "seed", generation)
        require(manifest["kind"] == "seed" and manifest["previous_checkpoint"] is None, "SEED_CHAIN_ROOT")
        self._seed = self._read(self.directory / "seed", manifest, reference)
        self._manifests = {generation: (manifest, reference)}
        self._loaded = {generation: self._seed}
        generations = []
        for path in self.directory.iterdir():
            match = GENERATION.fullmatch(path.name)
            if match:
                generations.append(int(match.group(1)))
            else:
                require(path.name in {"seed", "WRITE.lock"}, "UNEXPECTED_STORE_ENTRY:" + path.name)
        generations.sort()
        require(generations == list(range(generation + 1, generation + 1 + len(generations))),
                "GENERATION_SEQUENCE_GAP")
        for number in generations:
            manifest, current = self._read_manifest(self.directory / _generation(number), number)
            require(manifest["kind"] == "accepted_pair" and manifest["previous_checkpoint"] == reference,
                    "BROKEN_MANIFEST_CHAIN")
            require(manifest["prefix_count"] == 2 * number + 1, "PREFIX_COUNT_CHAIN")
            self._manifests[number] = (manifest, current)
            reference = current
        self._head = reference

    def _ready(self):
        self._check_temporary()
        if self._head is None:
            self._scan()

    def _decode_state(self, loaded, index):
        arrays, metadata = loaded["arrays"], loaded["metadata"]
        seed_metadata = self._seed["metadata"]
        shape = tuple(seed_metadata["shape"])
        base = seed_metadata["seed_metadata"]
        state = unpack_entry_state(arrays["packed"][index], base["cell_count"])
        for key in ("N", "U_eV"):
            state[key] = state[key].reshape(shape)
        state.update(t_s=float(arrays["clock"][index]), R=arrays["R"][index].copy(),
                     support=arrays["support"][index].copy(), nH_ref=base["nH_ref"],
                     nHe_ref=base["nHe_ref"])
        diagnostic = metadata["diagnostics"][index]
        if diagnostic is not None:
            state["diagnostics"] = copy.deepcopy(diagnostic)
        return state

    def load(self, reference):
        self._ready()
        generation = reference.get("generation")
        require(generation in self._manifests, "UNKNOWN_CHECKPOINT")
        manifest, actual = self._manifests[generation]
        require(reference == actual, "CHECKPOINT_REFERENCE_MISMATCH")
        path = self.directory / ("seed" if generation == self._seed["checkpoint"]["generation"]
                                 else _generation(generation))
        # Verify the requested bytes even if this process previously cached them.
        manifest, actual = self._read_manifest(path, generation, expected_sha=reference["manifest_sha256"])
        loaded = self._read(path, manifest, actual)
        self._loaded = {self._seed["checkpoint"]["generation"]: self._seed, generation: loaded}
        return self._view(loaded)

    def _view(self, loaded):
        record = loaded["metadata"]
        metadata = copy.deepcopy(self._seed["metadata"]["seed_metadata"])
        metadata.update(adaptive_cursor=copy.deepcopy(record["cursor"]),
                        current_clock=record["cursor"]["accepted_clock_s"],
                        completed_segments=record["cursor"]["accepted_boundaries"],
                        next_segment_index=record["cursor"]["accepted_boundaries"],
                        current_R=loaded["arrays"]["R"][-1].ravel().tolist(),
                        current_support=loaded["arrays"]["support"][-1].reshape(-1, 2).tolist(),
                        hpc_runtime_binding=copy.deepcopy(self._seed["metadata"]["hpc_runtime_binding"]),
                        segmented_prefix_count=record["prefix_count"],
                        accepted_history_storage=SCHEMA,
                        scientific_admission=False)
        end = metadata["restart_binding"]["end_time_s"]
        metadata["next_segment"] = None if metadata["current_clock"] == end else [metadata["current_clock"], end]
        if record["kind"] == "accepted_pair":
            metadata["ledger_max"] = copy.deepcopy(record["ledger_max"])
            metadata["production_transaction"] = copy.deepcopy(record["transaction"])
            metadata["production_output_records"] = copy.deepcopy(record["all_output_records"])
        return dict(state=self._decode_state(loaded, -1),
                    initial_state=self._decode_state(self._seed, 0),
                    cursor=copy.deepcopy(record["cursor"]), metadata=metadata,
                    output_records=copy.deepcopy(metadata.get("production_output_records", [])),
                    arrays={key: value.copy() for key, value in loaded["arrays"].items()},
                    checkpoint=copy.deepcopy(loaded["checkpoint"]),
                    identity=copy.deepcopy(self._seed["metadata"]["legacy_identity"]),
                    current_validation=dict(scope="SEGMENT_HASHES_AND_PREVIOUSLY_ADMITTED_PREFIX",
                                            scientific_admission=False))

    def load_latest(self):
        self._ready()
        return self.load(self._head)

    def commit(self, pair, cursor, trial, transaction, output_records):
        """Validate/publish exactly one accepted macro; return its journal ref."""
        with self._writer():
            self._ready()
            previous = self.load_latest()
            require(not (self.directory / _generation(self._head["generation"] + 1)).exists(),
                    "STALE_COORDINATOR_RELOAD_REQUIRED")
            cursor = json.loads(json_bytes(cursor))
            trial = json.loads(json_bytes(trial))
            transaction = json.loads(json_bytes(transaction))
            output_records = json.loads(json_bytes(output_records))
            validate_cursor(cursor)
            before = previous["cursor"]
            require(cursor["accepted_macros"] == before["accepted_macros"] + 1 and
                    cursor["accepted_boundaries"] == before["accepted_boundaries"] + 2 and
                    cursor["attempts"] > before["attempts"] and
                    cursor["rejected_macros"] >= before["rejected_macros"], "ACCEPTED_CURSOR_ADVANCE")
            require(trial.get("accepted") is True and transaction.get("attempt") == cursor["attempts"] and
                    transaction.get("trial") == trial and transaction.get("output_records") == output_records and
                    isinstance(transaction.get("begin_sha256"), str) and
                    HEX.fullmatch(transaction["begin_sha256"]), "ACCEPTED_TRANSACTION")
            shape = tuple(self._seed["metadata"]["shape"])
            arrays = self._pack_pair(pair, shape)
            require(before["accepted_clock_s"] < arrays["clock"][0] < arrays["clock"][1] ==
                    cursor["accepted_clock_s"], "PAIR_CLOCK_ORDER")
            base = previous["metadata"]
            controls = base["restart_binding"]["controls"]
            require(controls["min_step_s"] <= cursor["next_step_s"] <= controls["max_step_s"] and
                    cursor["accepted_clock_s"] <= base["restart_binding"]["end_time_s"],
                    "CURSOR_STEP_OR_TARGET")
            require(all(s["nH_ref"] == base["nH_ref"] and s["nHe_ref"] == base["nHe_ref"] for s in pair),
                    "REFERENCE_DENSITY_DRIFT")
            new_validation, local_meta = self._validate_pair(previous, pair)
            arrays.update(scales=previous["arrays"]["scales"].copy(),
                          counter_origins=previous["arrays"]["counter_origins"].copy(),
                          accepted_min=np.minimum(previous["arrays"]["accepted_min"], arrays["packed"].min(axis=0)),
                          accepted_max=np.maximum(previous["arrays"]["accepted_max"], arrays["packed"].max(axis=0)))
            all_records = previous["output_records"] + output_records
            epochs = [row["epoch_index"] for row in all_records]
            require(all(type(i) is int and i >= 0 for i in epochs) and epochs == sorted(set(epochs)),
                    "OUTPUT_RECORD_ORDER_OR_DUPLICATE")
            require(all(row["time_s"] in arrays["clock"] for row in output_records), "OUTPUT_RECORD_NOT_NEW_BOUNDARY")
            ledger_max = {key: max(base["ledger_max"][key], local_meta["ledger_max"][key])
                          for key in ("number", "energy")}
            metadata = dict(kind="accepted_pair", cursor=cursor,
                            prefix_count=cursor["accepted_boundaries"] + 1,
                            diagnostics=[s.get("diagnostics") for s in pair], transaction=transaction,
                            new_output_records=output_records, all_output_records=all_records,
                            ledger_max=ledger_max, validation=new_validation,
                            hpc_runtime_binding_sha256=hashlib.sha256(json_bytes(base["hpc_runtime_binding"])).hexdigest())
            number = cursor["accepted_macros"]
            reference = self._publish(_generation(number), arrays, metadata,
                                      dict(kind="accepted_pair", generation=number,
                                           prefix_count=cursor["accepted_boundaries"] + 1,
                                           previous_checkpoint=copy.deepcopy(self._head)))
            manifest, actual = self._read_manifest(self.directory / _generation(number), number,
                                                    expected_sha=reference["manifest_sha256"])
            self._manifests[number] = (manifest, actual)
            self._head = actual
            return copy.deepcopy(actual)

    def _validate_pair(self, previous, pair):
        """Reuse the unchanged entry validator on new rows against original IC."""
        initial = previous["initial_state"]
        states = [initial]
        if previous["state"]["t_s"] != initial["t_s"]:
            states.append(previous["state"])
        states += list(pair)
        clocks = np.array([s["t_s"] for s in states], dtype=np.float64)
        arrays, metadata = make_entry_snapshot(
            clocks=clocks,
            states=np.array([pack_entry_state(s["gas"], s["N"].ravel(), s["U_eV"].ravel(), s["counters"])
                             for s in states], dtype=np.float64),
            R=np.array([s["R"].ravel() for s in states], dtype=np.float64),
            support=np.array([s["support"].reshape(-1, 2) for s in states], dtype=np.float64),
            all_boundary_clocks=clocks, nH_ref=initial["nH_ref"], nHe_ref=initial["nHe_ref"],
            scales=previous["arrays"]["scales"], physical_binding=previous["metadata"]["physical_binding"])
        validation = validate_entry_snapshot(arrays, metadata)
        validation.update(scope="UNCHANGED_ENTRY_CRITERIA_ON_NEW_PAIR_WITH_ORIGINAL_IC_AND_PREVIOUS_ENDPOINT",
                          old_full_prefix_revalidated=False, checked_new_boundaries=2)
        return validation, metadata

    def reconcile(self, begin, begin_sha256):
        """Return an exact committed acceptance receipt, or None; never run work."""
        self._ready()
        number = begin["cursor"]["accepted_macros"] + 1
        if number not in self._manifests:
            # Reopen the manifest chain in case publication preceded an I/O error.
            if not (self.directory / _generation(number)).exists():
                return None
            self._scan()
        manifest, reference = self._manifests[number]
        require(manifest["previous_checkpoint"] == begin["checkpoint"], "RECONCILIATION_PARENT")
        loaded = self.load(reference)
        transaction = loaded["metadata"]["production_transaction"]
        require(transaction["attempt"] == begin["attempt"] == begin["cursor"]["attempts"] + 1 and
                transaction["begin_sha256"] == begin_sha256, "ATOMIC_CHECKPOINT_TRANSACTION_MISMATCH")
        return dict(cursor=loaded["cursor"], trial=transaction["trial"], checkpoint=reference)

    def _legacy(self):
        self._ready()
        seed = self._seed["metadata"]
        directory = self.legacy_directory or Path(seed["legacy_directory"])
        reference = seed["legacy_checkpoint"]
        path = directory / _generation(reference["generation"])
        require(path.is_dir() and not path.is_symlink(), "LEGACY_SEED_MISSING")
        require(sha(path / "manifest.json") == reference["manifest_sha256"], "LEGACY_SEED_MANIFEST_HASH")
        manifest = json.loads((path / "manifest.json").read_text())
        for filename, info in manifest["files"].items():
            require(Path(filename).name == filename and (path / filename).is_file() and
                    not (path / filename).is_symlink() and (path / filename).stat().st_size == info["bytes"] and
                    sha(path / filename) == info["sha256"], "LEGACY_SEED_MEMBER_HASH")
        with np.load(path / "arrays.npz", allow_pickle=False) as archive:
            arrays = {key: archive[key].copy() for key in archive.files}
        return dict(arrays=arrays, metadata=json.loads((path / "metadata.json").read_text()),
                    identity=json.loads((path / "identity.json").read_text()))

    def iter_states(self, reference=None):
        """Stream exact full history; payload hashes are checked as each is read."""
        self._ready()
        reference = self._head if reference is None else reference
        require(reference == self._manifests.get(reference["generation"], (None, None))[1],
                "CHECKPOINT_REFERENCE_MISMATCH")
        legacy = self._legacy()
        shape = tuple(self._seed["metadata"]["shape"])
        for index in range(len(legacy["arrays"]["prefix_clock"])):
            yield _natural(legacy, index, shape)
        start = self._seed["checkpoint"]["generation"] + 1
        for generation in range(start, reference["generation"] + 1):
            manifest, item_reference = self._manifests[generation]
            path = self.directory / _generation(generation)
            manifest, item_reference = self._read_manifest(path, generation,
                                                            expected_sha=item_reference["manifest_sha256"])
            loaded = self._read(path, manifest, item_reference)
            for index in (0, 1):
                yield self._decode_state(loaded, index)

    def verify_history(self, reference=None):
        """Explicit byte integrity scan; not a scientific or numerical replay."""
        count = sum(1 for _ in self.iter_states(reference))
        reference = self._head if reference is None else reference
        require(count == 2 * reference["generation"] + 1, "VERIFIED_PREFIX_COUNT")
        return dict(checkpoint=copy.deepcopy(reference), states=count,
                    scope="ALL_REFERENCED_PAYLOAD_BYTES_READ", scientific_admission=False,
                    numerical_replays=0)

    def export_legacy_snapshot(self, reference=None):
        """Materialize one complete legacy-shaped snapshot only when requested.

        The old binding is retained and the separate HPC runtime binding remains
        explicit. This does not publish under the old physical-validator identity
        or grant whole-history admission.
        """
        self._ready()
        reference = self._head if reference is None else reference
        current = self.load(reference)
        states = list(self.iter_states(reference))
        metadata = current["metadata"]
        clocks = np.array([s["t_s"] for s in states], dtype=np.float64)
        end = metadata["restart_binding"]["end_time_s"]
        edges = clocks.copy() if clocks[-1] == end else np.r_[clocks, end]
        arrays, physical = make_entry_snapshot(
            clocks=clocks,
            states=np.array([pack_entry_state(s["gas"], s["N"].ravel(), s["U_eV"].ravel(), s["counters"])
                             for s in states], dtype=np.float64),
            R=np.array([s["R"].ravel() for s in states]),
            support=np.array([s["support"].reshape(-1, 2) for s in states]),
            all_boundary_clocks=edges, nH_ref=metadata["nH_ref"], nHe_ref=metadata["nHe_ref"],
            scales=current["arrays"]["scales"], physical_binding=metadata["physical_binding"])
        physical.update({key: copy.deepcopy(value) for key, value in metadata.items()
                         if key not in physical})
        physical["schema"] = metadata["schema"]
        physical["production_kernel_history"] = {
            str(index): copy.deepcopy(state["diagnostics"]) for index, state in enumerate(states)
            if "diagnostics" in state}
        physical["exported_segmented_checkpoint"] = copy.deepcopy(reference)
        return dict(arrays=arrays, metadata=physical, identity=current["identity"],
                    scientific_admission=False)
