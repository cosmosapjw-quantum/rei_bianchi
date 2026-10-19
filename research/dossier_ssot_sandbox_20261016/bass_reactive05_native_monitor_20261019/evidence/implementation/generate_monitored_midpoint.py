#!/usr/bin/env python3
"""Generate additive observer hooks and prove reversible exact source changes."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--unit", type=Path, required=True)
p.add_argument("--proof", type=Path, required=True)
p.add_argument("--verify-only", action="store_true")
a = p.parse_args()
source = a.unit / "crate/ap_midpoint.rs"
target = a.unit / "crate/monitored_midpoint.rs"
original = source.read_text()
text = original
edits = []


def replace(old, new, count=1):
    global text
    assert text.count(old) == count, (old[:80], text.count(old), count)
    text = text.replace(old, new)
    edits.append((old, new, count))


replace("ApMidpointBridge", "MonitoredMidpointBridge", original.count("ApMidpointBridge"))
replace(
    "//! BASS-REACTIVE-03 opt-in exponentially fitted birth-age corrector.",
    "//! BASS-REACTIVE-05 generated read-only monitor over the BR03 corrector.\n"
    "//! Generated with exact reversible edits; physics bodies remain unchanged.\n"
    "//! BASS-REACTIVE-03 opt-in exponentially fitted birth-age corrector.",
)
replace(
    "use crate::axbi_sources::SOURCE_ID;",
    "use crate::axbi_sources::SOURCE_ID;\n"
    "use crate::native_birth_monitor::{Capture, MonitorError, MonitorMode, MonitoredStep};",
)
replace(
    "#[derive(Clone, Copy, Debug, PartialEq, Eq)]\n"
    "pub enum BirthMode {\n    Off,\n    Fitted { refinement: usize },\n}",
    "pub use crate::ap_midpoint::BirthMode;",
)
old_dispatch = """    pub fn advance_with_diagnostics(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        if self.4 == BirthMode::Off {
            return self.original().advance_with_diagnostics(initial, conf, dt);
        }
        self.advance_core(initial, conf, dt, true)
    }
"""
new_dispatch = """    /// No monitoring: dispatch directly to the unchanged parent AP implementation.
    pub fn advance_with_diagnostics(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        self.parent().advance_with_diagnostics(initial, conf, dt)
    }

    pub fn from_parent(parent: crate::ap_midpoint::ApMidpointBridge) -> Self {
        Self(parent.0, parent.1, parent.2, parent.3, parent.4)
    }

    pub fn parent(&self) -> crate::ap_midpoint::ApMidpointBridge {
        crate::ap_midpoint::ApMidpointBridge(self.0.clone(), self.1, self.2, self.3, self.4)
    }

    /// Monitoring errors are diagnostics; they cannot turn accepted physics
    /// into a rejected step. Legacy birth mode is run by the original owner.
    pub fn advance_with_monitor(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
        mode: MonitorMode,
    ) -> Result<MonitoredStep, NetworkError> {
        let MonitorMode::On(controls) = mode else {
            let (step, diagnostics) = self.parent().advance_with_diagnostics(initial, conf, dt)?;
            return Ok(MonitoredStep { step, diagnostics, monitor: None });
        };
        if self.4 == BirthMode::Off {
            let (step, diagnostics) = self.parent().advance_with_diagnostics(initial, conf, dt)?;
            return Ok(MonitoredStep {
                step,
                diagnostics,
                monitor: Some(Err(MonitorError::UnsupportedBirthMode)),
            });
        }
        let mut capture = Capture::new(controls);
        let (step, diagnostics) = self.advance_core(initial, conf, dt, true, Some(&mut capture))?;
        Ok(MonitoredStep { step, diagnostics, monitor: Some(capture.finish()) })
    }
"""
replace(old_dispatch, new_dispatch)
replace(
    "        predict: bool,\n    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {",
    "        predict: bool,\n        mut monitor: Option<&mut Capture>,\n"
    "    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {",
)
replace(
    "Some(first_order.advance_core(initial, &pc, 0.5 * dt, false)?.0)",
    "Some(first_order.advance_core(initial, &pc, 0.5 * dt, false, None)?.0)",
)
replace(
    "        let births = self.emit_births(t0, dt, conf, &rate_gas)?;",
    "        let births = self.emit_births(t0, dt, conf, &rate_gas)?;\n"
    "        // BR05 read-only corrector hook; the predictor receives None.\n"
    "        if let Some(observer) = monitor.as_deref_mut() {\n"
    "            observer.observe_births(&self.parent(), initial, conf, dt, &rate_gas,\n"
    "                &births, &gm, &g1);\n"
    "        }",
)
replace(
    "        )?;\n        s.full.photon_bins.clear();",
    "        )?;\n"
    "        if let Some(observer) = monitor.as_deref_mut() {\n"
    "            observer.observe_after_photo(&s.cohorts);\n"
    "        }\n"
    "        s.full.photon_bins.clear();",
)
replace(
    "        diag.emitted_photon_energy_j_com3 = e_birth;",
    "        diag.emitted_photon_energy_j_com3 = e_birth;\n"
    "        if let Some(observer) = monitor {\n"
    "            observer.observe_accepted(&s, conf);\n"
    "        }",
)
recovered = text
for old, new, count in reversed(edits):
    assert recovered.count(new) == count, new[:80]
    recovered = recovered.replace(new, old)
assert recovered == original
if a.verify_only:
    formatted = subprocess.run(
        ["rustfmt", "--edition", "2024", "--config", "skip_children=true", "--emit", "stdout"],
        input=text, text=True, capture_output=True, check=True,
    ).stdout
    assert formatted == target.read_text(), "Generated module differs from exact edits plus scoped rustfmt"
else:
    target.write_text(text)
a.proof.parent.mkdir(parents=True, exist_ok=True)
a.proof.write_text(json.dumps({
    "status": "PASS_EXACT_REVERSIBLE_EDITS",
    "source_path": str(source),
    "source_sha256": hashlib.sha256(original.encode()).hexdigest(),
    "generated_path": str(target),
    "generated_sha256_before_rustfmt": hashlib.sha256(text.encode()).hexdigest(),
    "generated_file_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "scoped_rustfmt_verified": a.verify_only,
    "recovered_sha256": hashlib.sha256(recovered.encode()).hexdigest(),
    "edits": [{"old": old, "new": new, "count": count} for old, new, count in edits],
    "scope": "Exact reversibility plus optional deterministic scoped formatting; physics body edits are observer insertions only.",
}, indent=2) + "\n")
print(f"{'Verified' if a.verify_only else 'Generated'} {target}: {len(edits)} exact reversible edits")
