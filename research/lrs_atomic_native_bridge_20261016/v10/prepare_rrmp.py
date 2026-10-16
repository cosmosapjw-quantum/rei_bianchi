"""Bind the isolated four-channel V8 RR/DR midpoint stage around V10 BE."""
from __future__ import annotations

import argparse
from pathlib import Path


def once(s: str, old: str, new: str) -> str:
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"RRMP seam count {n}: {old[:80]!r}")
    return s.replace(old, new, 1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("owner_copy", type=Path)
    a = p.parse_args()
    path = a.owner_copy / "rust/rei_microphysics/src/axbi_driver.rs"
    s = path.read_text()
    s = once(s, "    half_opacity: bool,\n", "    half_opacity: bool,\n    v10_omit_recomb: bool,\n")
    s = once(s, "        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;\n        let mut residual", '''        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;
        let mut rhs = point.rhs;
        if self.v10_omit_recomb { v10_strip_recomb(&mut rhs, nh, nhe); }
        let mut residual''')
    s = once(s, "dt * point.rhs.fraction_dt[i]", "dt * rhs.fraction_dt[i]")
    s = once(s, "dt * point.rhs.w_dt_erg_per_h_s / c.ev_erg", "dt * rhs.w_dt_erg_per_h_s / c.ev_erg")
    s = once(s, "Ok((residual, stocks, point.rhs))", "Ok((residual, stocks, rhs))")
    s = once(s, "    v10_half_opacity: bool,\n", "    v10_half_opacity: bool,\n    v10_rrmp: bool,\n")
    s = once(s, "            v10_half_opacity: false,\n", "            v10_half_opacity: false,\n            v10_rrmp: false,\n")
    s = once(s, "        no_radiation: bool, half_opacity: bool) {", "        no_radiation: bool, half_opacity: bool, rrmp: bool) {")
    s = once(s, "        self.v10_half_opacity = half_opacity;\n", "        self.v10_half_opacity = half_opacity;\n        self.v10_rrmp = rrmp;\n")
    s = once(s, "            half_opacity: self.v10_half_opacity,\n", "            half_opacity: self.v10_half_opacity,\n            v10_omit_recomb: self.v10_rrmp,\n")
    s = once(s, "        self.geometry_map(&mut s, mid)?;\n        if self.v10_no_radiation {", "        self.geometry_map(&mut s, mid)?;\n        if self.v10_rrmp { self.v10_rrdr_stage(&mut s, 0.5 * dt)?; }\n        if self.v10_no_radiation {")
    s = once(s, "        self.geometry_map(&mut s, to)?;\n        self.validate(&s, 1e-8)?;", "        if self.v10_rrmp { self.v10_rrdr_stage(&mut s, 0.5 * dt)?; }\n        self.geometry_map(&mut s, to)?;\n        self.validate(&s, 1e-8)?;")
    s += '\ninclude!("v10_rrmp.rs");\n'
    path.write_text(s)
    rr = Path(__file__).with_name("v10_rrmp.rs")
    (path.parent / "v10_rrmp.rs").write_bytes(rr.read_bytes())


if __name__ == "__main__":
    main()
