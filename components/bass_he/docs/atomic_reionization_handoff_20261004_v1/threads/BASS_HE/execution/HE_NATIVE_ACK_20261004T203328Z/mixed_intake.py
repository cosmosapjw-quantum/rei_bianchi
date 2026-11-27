"""Receipt boundary only; no native or scientific calculation."""

import math
import re

PIN = "b553698a114fbff05640ab6ecb95d260410de492"
TASK = "HE-FLRW02B_NATIVE_EXECUTION_RETURN"
TEST_SHA = "a1223f89a1c54c731df5c505415af969077ab7a94e920ce2e9efc955090dad54"
GOLDEN_SHA = "9ed50c8cc397ed63bc0c3dc1cf6ceb85854eea6bfe1659a7d5b9f7a26c5588b4"
INPUT_SHA = "2aa72f89ab8ddbf844c9704593b1953231a6bf60b70d50c2fcd183c53a97ba15"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(actual, expected, message):
    require(type(actual) is type(expected) and actual == expected, message)


def validate(contract, result, execution, stdout, comparisons, review):
    """Accept only this frozen, finite gate; inspect bytes before calling."""
    try:
        for key, expected in {"task": TASK, "native_commit": PIN, "test_sha256": TEST_SHA,
                              "golden_sha256": GOLDEN_SHA, "reference_input_sha256": INPUT_SHA,
                              "test_count": 2, "source_cases": 5,
                              "relative_tolerance": 5e-14, "absolute_tolerance": 1e-300}.items():
            equal(contract[key], expected, key)
        for key, expected in {"status": "PASS_FINITE_MIXED_NATIVE_GATE", "native_commit": PIN,
                              "native_tests_passed": 2, "comparison_count": 274,
                              "source_sha256_unchanged": True, "supplier_test_byte_identical": True,
                              "source_physical_admission": False, "history_admission": False}.items():
            equal(result[key], expected, key)
        equal(execution["production_source_mutations"], 0, "source mutation")
        commands = [c for c in execution["commands"] if c["label"] == "NATIVE_MIXED"]
        require(len(commands) == 1, "native invocation count")
        equal(commands[0]["exit_code"], 0, "native exit")
        equal(commands[0]["argv"][1:], ["test", "--manifest-path",
              "research_sync_20261005/loop1/he_mixed/harness/Cargo.toml", "--test",
              "he_flrw02_absorption", "--locked", "--offline", "--", "--nocapture",
              "--test-threads=1"], "native command")
        require("test result: ok. 2 passed; 0 failed;" in stdout, "missing test summary")
        rows = []
        for line in stdout.splitlines():
            match = re.search(r"(FLRW02_(?:RESIDUAL|REFERENCE)) (.*)$", line)
            if not match:
                continue
            kind, data = match.groups()
            fields = dict(item.split("=", 1) for item in data.split())
            keys = {"absolute", "relative", "lhs", "rhs"} if kind == "FLRW02_RESIDUAL" else {
                "absolute", "relative", "actual", "reference", "label"}
            require(set(fields) == keys, "raw row fields")
            row = {"type": kind}
            for key, value in fields.items():
                row[key] = value if key == "label" else float(value)
                if key != "label":
                    require(math.isfinite(row[key]), "nonfinite raw value")
            a, b = (row[k] for k in (("lhs", "rhs") if kind == "FLRW02_RESIDUAL" else ("actual", "reference")))
            absolute, scale = abs(a-b), max(abs(a), abs(b))
            relative = absolute / scale if scale else 0.0
            require(row["absolute"] == absolute and row["relative"] == relative, "forged raw metric")
            require(absolute <= 5e-14*scale + 1e-300, "outside frozen tolerance")
            row["acceptance"] = True
            rows.append(row)
        require(len(rows) == len(comparisons) == 274, "missing comparison")
        for raw, saved in zip(rows, comparisons):
            require(set(raw) == set(saved), "comparison fields")
            for key, value in raw.items():
                equal(saved[key], value, "comparison mismatch: " + key)
        for kind, count in [("FLRW02_RESIDUAL", 82), ("FLRW02_REFERENCE", 192)]:
            group = [row for row in rows if row["type"] == kind]
            require(len(group) == count, "comparison kind count")
            stats = result["statistics"][kind]
            equal(stats["count"], count, "reported count")
            require(stats["max_absolute"] == max(group, key=lambda r: r["absolute"]), "maximum absolute")
            require(stats["max_relative"] == max(group, key=lambda r: r["relative"]), "maximum relative")
        labels = {r["label"].split("/")[0] for r in rows if r["type"] == "FLRW02_REFERENCE"}
        equal(labels, {f"case{i}" for i in range(5)}, "finite state labels")
        equal(review["status"], "CONFIRMED", "review status")
        equal(review["decision"], "PROMOTE_SCOPED_LOOP2_INPUTS", "review scope")
        equal(review["blocking_findings"], [], "review blockers")
        decisions = [d for d in review["decisions"] if d["id"] == TASK]
        require(len(decisions) == 1, "missing scoped decision")
        for key, expected in {"decision": "PROMOTE", "native_commit": PIN, "native_tests": 2,
                              "comparisons": 274, "source_physical_admission": False,
                              "history_admission": False}.items():
            equal(decisions[0][key], expected, "review " + key)
        return {"accepted": True, "scope": "FINITE_INSTANTANEOUS_MIXED_ABSORPTION_ONLY",
                "comparisons": 274, "reference_comparisons": 192, "ledger_scale_comparisons": 82,
                "physical_admission": False, "history_admission": False,
                "whole_live_crate_admission": False, "RCT_stepper_admission": False}
    except (KeyError, TypeError, ArithmeticError) as exc:
        raise ValueError(f"malformed receipt: {exc}") from exc
