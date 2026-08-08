from __future__ import annotations
import csv
import json
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]


def _results():
    return json.loads((STAGE / "results.json").read_text())


def test_event_topology_and_photon_ownership_are_promoted():
    r = _results()
    assert r["event_population_topology_pass"] is True
    assert r["photon_number_ownership_pass"] is True
    assert r["direct_HeI_to_HeIII_event_count"] == 0
    assert r["duplicate_event_id_count"] == 0


def test_energy_closes_only_with_unresolved_ots_ledger():
    r = _results()
    assert r["energy_ownership_contract_pass_with_unresolved_OTS_ledger"] is True
    assert r["fully_resolved_OTS_heating_identified"] is False
    assert r["production_history_authorized"] is False


def test_source_identical_branch_kernel_fails_closed():
    r = _results()
    audit = r["numerical_replay"]["branch_closure_audit"]
    assert r["source_identical_branch_kernel_pass"] is False
    assert r["legacy_v_formula_source_table_identified"] is False
    assert audit["legacy_f_below_published_0p1_count"] == 44904
    assert 0.97 < audit["legacy_f_below_published_0p1_fraction"] < 0.98


def test_all_source_event_vectors_preserve_nuclei_exactly():
    exact = _results()["exact_algebra"]
    for item in exact["invariant_residuals"].values():
        assert item == {"H": "0", "He": "0"}
    for vector in exact["vector_residuals"].values():
        assert vector == ["0"] * 5


def test_registry_has_exactly_one_typed_owner_per_event():
    rows = list(csv.DictReader((STAGE / "data/EVENT_REGISTRY.csv").open()))
    assert len(rows) == 26
    assert len({r["event_id"] for r in rows}) == 26
    for row in rows:
        assert row["photon_owner"]
        assert row["energy_owner"]
        assert row["population_owner"]
        assert row["direct_HeI_to_HeIII"] == "False"
