#!/usr/bin/env python3
"""Exact scalar check of the retrieved RICAM-Report 2018-08 Eq. (6).
This is a literature-import check; it does not call the HH source or root code.
"""
import datetime
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import resource
import time

root = Path(__file__).resolve().parent
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
t0 = time.perf_counter()
u, u_tilde, z, z_tilde = F(0), F(1), F(1), F(1)
rho = -u_tilde
dual_residual = F(1) - z_tilde
cubic = F(0)
lhs = u - u_tilde
rhs_printed = (rho * (z-z_tilde) + dual_residual * (u-u_tilde))/2 - rho*z_tilde + cubic
rhs_corrected = (rho * (z-z_tilde) + dual_residual * (u-u_tilde))/2 + rho*z_tilde + cubic
assert lhs != rhs_printed
assert lhs == rhs_corrected
elapsed = time.perf_counter() - t0
record = {
  "unit": "PHYS16_LITERATURE_IMPORT",
  "status": "EXTRACTED_PREPRINT_EQUATION_INCONSISTENT_ON_EXACT_LINEAR_CASE",
  "scope": "Retrieved RICAM-Report 2018-08 Eq.(6) together with Eq.(7); final journal body not inspected.",
  "model": {"U":"R","V":"R","A(u)(v)":"u*v","J(u)":"u","regularity":"C_infinity"},
  "values": {"u":str(u),"u_tilde":str(u_tilde),"z":str(z),"z_tilde":str(z_tilde)},
  "exact_arithmetic": "fractions.Fraction",
  "lhs": str(lhs), "rhs_printed": str(rhs_printed), "rhs_with_corrected_iteration_sign": str(rhs_corrected),
  "decision": "Do not import the retrieved Eq.(6) as a proof premise; derive the PHYS16 endpoint identity directly.",
  "hh_source_calls": 0, "hh_root_calls": 0, "hh_history_calls": 0,
  "started_utc": started,
  "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "wall_seconds": elapsed,
  "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
  "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
}
(root/"PREPRINT_SIGN_CHECK.json").write_text(json.dumps(record, ensure_ascii=False, indent=2)+"\n")
print(json.dumps({"status":record["status"],"lhs":str(lhs),"rhs_printed":str(rhs_printed),"rhs_corrected":str(rhs_corrected),"wall_seconds":elapsed}))

