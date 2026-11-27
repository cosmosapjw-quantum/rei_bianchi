"""Prepare a pinned sweep, use cooperative HE30 execution, render saved results."""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
import argparse
import hashlib
import json
from pathlib import Path

from bindings import UNIT, load_runner
from electron_donor import ElectronDonor
from receiver import scientific_identity, DEFAULT_NUMERICS


def prepare(args):
    path = args.donor.resolve()
    donor = ElectronDonor.load(path)
    donor.require_support(1/21., 1/(1+args.z_end))
    if donor.metadata["provenance"]["kind"] != "actual_history":
        raise ValueError("prepared scientific campaigns require an actual history")
    try:
        locator = str(path.relative_to(UNIT))
    except ValueError:
        locator = str(path)
    if args.grid == "joint175":
        sigmas = [0., .0003, .001, .003, .01, .03, .1]
        pms = [-.0003, -.0001, 0., .0001, .0003]
        prs = [-.001, -.0003, 0., .0003, .001]
    elif args.grid == "pilot18":
        sigmas, pms, prs = [0., .003], [-.0003, 0., .0003], [-.001, 0., .001]
    else:
        sigmas, pms, prs = [.003], [.0003], [-.001]
    cases = []
    for i,sigma in enumerate(sigmas):
        for j,pm in enumerate(pms):
            for k,pr in enumerate(prs):
                for opacity in (("off", "on") if args.include_off else ("on",)):
                    c = dict(case_id=f"he31_s{i}_m{j}_r{k}_{opacity}", Sigma_F=sigma,
                        P_m=pm, P_r=pr, z_end=args.z_end, opacity=opacity,
                        backend="prepared", donor_manifest=locator,
                        donor_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        numerics=dict(DEFAULT_NUMERICS), purpose="prescribed_donor_sensitivity")
                    scientific_identity(c)
                    cases.append(c)
    output = dict(schema="he31.campaign.v1", grid=args.grid, cases=cases,
                  donor_identity=donor.identity, z_start=20, z_end=args.z_end,
                  status="prepared_not_executed")
    load_runner().atomic_json(args.out, output, replace=False)
    return dict(campaign=str(args.out), cases=len(cases), donor_identity=donor.identity,
                z_end=args.z_end, status="PREPARED_NOT_EXECUTED")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--donor", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    prep.add_argument("--z-end", type=float, default=4.)
    prep.add_argument("--grid", choices=("smoke", "pilot18", "joint175"), default="pilot18")
    prep.add_argument("--include-off", action="store_true")
    run = sub.add_parser("run")
    run.add_argument("--campaign", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--dry-plan", action="store_true")
    run.add_argument("--max-workers", type=int, default=64)
    run.add_argument("--seconds", type=float, default=1800.)
    run.add_argument("--reserve-cpus", type=int, default=2)
    run.add_argument("--reserve-gib", type=float, default=16.)
    run.add_argument("--lease-dir", type=Path, default=Path("/tmp/cosmosapjw_hpc64_cpu_leases"))
    args = parser.parse_args()
    if args.action == "prepare":
        result = prepare(args)
    else:
        os.environ["HE31_CAMPAIGN"] = str(args.campaign.resolve())
        result = load_runner().run(args.out, max_workers=args.max_workers,
            seconds=args.seconds, dry_plan=args.dry_plan, lease_dir=args.lease_dir,
            reserve_cpus=args.reserve_cpus, reserve_gib=args.reserve_gib,
            api_module="receiver")
    print(json.dumps(result, indent=2))
    if args.action == "run" and not args.dry_plan:
        if any(item.get("status") not in ("COMPLETE", "REUSED_COMPLETE")
               for item in result.get("statuses", {}).values()):
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
