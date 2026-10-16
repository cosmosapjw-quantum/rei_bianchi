"""Add opt-in 1e-13 Newton diagnostic to the isolated V10 copy."""
from __future__ import annotations

import argparse
from pathlib import Path


def once(s: str, old: str, new: str) -> str:
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"tight seam count {n}: {old[:80]!r}")
    return s.replace(old, new, 1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("owner_copy", type=Path)
    a = p.parse_args()
    path = a.owner_copy / "rust/rei_microphysics/src/axbi_driver.rs"
    s = path.read_text()
    s = once(s, "    v10_rrmp: bool,\n", "    v10_rrmp: bool,\n    v10_tight_newton: bool,\n")
    s = once(s, "            v10_rrmp: false,\n", "            v10_rrmp: false,\n            v10_tight_newton: false,\n")
    s = once(s, "        no_radiation: bool, half_opacity: bool, rrmp: bool) {", "        no_radiation: bool, half_opacity: bool, rrmp: bool, tight: bool) {")
    s = once(s, "        self.v10_rrmp = rrmp;\n", "        self.v10_rrmp = rrmp;\n        self.v10_tight_newton = tight;\n")
    s = once(s, "            if norm <= self.research_numerics.tolerance() {", "            if norm <= if self.v10_tight_newton { 1e-13 } else { self.research_numerics.tolerance() } {")
    path.write_text(s)


if __name__ == "__main__":
    main()
