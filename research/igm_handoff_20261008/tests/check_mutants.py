"""Verify three scientifically consequential wrong implementations are caught.

Mutations occur only in temporary copies. This is targeted fault injection,
not production implementation, a general mutation score, or physical evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    changes={
        "dropped_particle_temperature_term": {
            "bridge/vendor/source_transfer.py": [
                ("(heat-w*electron_rate/particles_per_h)","heat"),
                ("particle_T=-state.temperature*xe/state.particles","particle_T=F(0)"),
            ],
        },
        "independentized_rate_energy_generators": {
            "bridge/joint_moment.py": [
                ("generators = tuple(project(state, g, chi_ev) for g in family.generators)",
                 "generators = tuple(project(state, part, chi_ev) for g in family.generators "
                 "for part in (Moments(g.gamma, (F(0),)*3), Moments((F(0),)*3, g.energy_ev_s)))"),
            ],
        },
        "extra_h_division_on_q_ell": {
            "bridge/joint_moment.py": [
                ('dln_a["photo_q_ell_source"] = native["photo_q_ell_source"]',
                 'dln_a["photo_q_ell_source"] = tuple(v/state.hubble_s for v in native["photo_q_ell_source"])'),
            ],
        },
    }
    results=[]
    for name,files in changes.items():
        with tempfile.TemporaryDirectory(prefix="igm-moment-mutant-") as tmp:
            work=Path(tmp)
            for directory in ("bridge","tests"):
                shutil.copytree(root/directory,work/directory,
                                ignore=shutil.ignore_patterns("__pycache__","evidence"))
            (work/"inputs").mkdir()
            shutil.copyfile(root/"inputs"/"TOY_VECTORS.json",work/"inputs"/"TOY_VECTORS.json")
            for rel,replacements in files.items():
                path=work/rel
                content=path.read_text()
                for old,new in replacements:
                    if content.count(old)!=1:
                        raise RuntimeError("Mutation anchor absent or ambiguous: "+name)
                    content=content.replace(old,new)
                path.write_text(content)
            run=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_joint_moment.py","-v"],
                cwd=work,text=True,capture_output=True)
            failed=[line.split(" ... ")[0] for line in run.stderr.splitlines()
                    if " ... FAIL" in line or " ... ERROR" in line]
            results.append({"mutant":name,"exit_code":run.returncode,
                            "detected":run.returncode!=0,"failing_tests":failed,
                            "stdout":run.stdout,"stderr":run.stderr})
    report={"status":"PASS" if all(r["detected"] for r in results) else "FAIL",
            "scope":"three specified fault injections; temporary copies only",
            "source_sha256":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (root/"bridge"/"joint_moment.py",root/"bridge"/"vendor"/"source_transfer.py",root/"tests"/"test_joint_moment.py")},
            "results":results}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"mutants_detected":sum(r["detected"] for r in results)}))
    return 0 if report["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
