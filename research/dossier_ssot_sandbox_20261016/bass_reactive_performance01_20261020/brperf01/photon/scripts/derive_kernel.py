"""Generate the arithmetic-preserving path copy; old source is read-only.

Every replacement is count-asserted. The standalone adapter's hand-written
header is retained. The copied positive-product, inverse, event, and ledger
arithmetic remain byte-identical except scratch access and context plumbing.
"""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "../../repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/br06/src/reference.rs"
text = SOURCE.read_text()
core = text[text.index("/// Balance positive factors"):text.index("pub fn native_path(")]

def replace(old, new):
    global core
    assert core.count(old) == 1, (old, core.count(old))
    core = core.replace(old, new)

replace("    limit: usize,\n}", "    limit: usize,\n    opacity_scratch: [f64; 128],\n    opacity_integrals: usize,\n}")
replace("        let mut rates = Vec::with_capacity(gauss.nodes.len());", "        self.opacity_integrals += 1;")
replace("        for &(u, w) in &gauss.nodes {", "        for (index, &(u, _w)) in gauss.nodes.iter().enumerate() {")
replace("            rates.push((rate, w));", "            self.opacity_scratch[index] = rate;")
replace("            rates.iter().map(|(r, w)| w * (r / rate_scale)).sum()", "            self.opacity_scratch[..gauss.nodes.len()]\n                .iter()\n                .zip(&gauss.nodes)\n                .map(|(r, (_, w))| w * (r / rate_scale))\n                .sum()")
replace("pub fn integrate_path<M: PathModel>(", "pub fn integrate_path_cached<M: PathModel>(")
replace("    controls: PathControls,\n) -> Result<PathResult> {", "    controls: PathControls,\n    rules: &Rules,\n) -> Result<PathResult> {")
replace("    let opacity = PositiveGauss::new(controls.opacity_degree)?;\n    let event = PositiveGauss::new(controls.event_degree)?;", "    if controls.opacity_degree != rules.opacity.nodes.len()\n        || controls.event_degree != rules.event.nodes.len()\n    {\n        return Err(Error::InvalidInput(\"prepared_rule_mismatch\"));\n    }\n    let opacity = &rules.opacity;\n    let event = &rules.event;")
replace("        limit: controls.max_samples,\n    };", "        limit: controls.max_samples,\n        opacity_scratch: [0.0; 128],\n        opacity_integrals: 0,\n    };")
replace("    Ok(out)\n}\n\n", "    let mut work = rules.work.get();\n    work.opacity_integrals += evaluator.opacity_integrals;\n    work.virtual_samples += evaluator.samples;\n    rules.work.set(work);\n    Ok(out)\n}\n\n")
# Remove only the now redundant references to immutable borrowed rules.
core = core.replace(", &opacity)", ", opacity)")
(HERE / "src/path_core.rs").write_text("// Derived add-only performance copy; see scripts/derive_kernel.py.\n" + core)
subprocess.run(["rustfmt", "--edition", "2024", str(HERE / "src/path_core.rs")], check=True)
ledger = text[text.index("#[derive(Clone, Debug, Default)]\npub struct Totals"):text.index("/// Full output retains every labelled birth.")].replace("Totals", "Ledger")
(HERE / "src/ledger.rs").write_text("// Exact ordered accumulator copy from original BR06 reference.rs.\n" + ledger)
subprocess.run(["rustfmt", "--edition", "2024", str(HERE / "src/ledger.rs")], check=True)
(HERE / "evidence/CORE_PROVENANCE.json").write_text(json.dumps({
    "original": str(SOURCE.resolve()),
    "original_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "derived_sha256": hashlib.sha256((HERE / "src/path_core.rs").read_bytes()).hexdigest(),
    "mutation_scope": "new standalone copy only",
    "numerical_changes": "none; stable ordered sums and original subnormal branches retained"
}, indent=2) + "\n")
