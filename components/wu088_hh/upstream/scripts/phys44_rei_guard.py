#!/usr/bin/env python3
"""Read-only HH→REI domain/authority guard and explicitly synthetic FT03 unit example."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys44_rei_guard import read_rei_guard,ft03_manufactured_response

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--rei-root",type=Path,default=Path.home()/"Dropbox/bianchi/rei_bianchi")
 p.add_argument("--wu-root",type=Path,default=ROOT)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 d=read_rei_guard(a.rei_root,a.wu_root)
 demo=ft03_manufactured_response(
  nH_cm3="1e-4",xHII=".9",yHeII=".1",yHeIII=".2",
  nHe_over_nH=".0813",w_eV_per_H="1",
  kHHeffective_cm3_s="1e-10",kB_eV_K="0.00008617333262",
  chiH_eV="13.598434599702",unit_test_only=True)
 d["manufactured_unit_demo"]=demo
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({"local_rei_read_only_revision":d["local_rei_head_read_only"],
 "local_rei_source":d["consumer_source_identity"],
 "HH_effective_rate_status":d["rate_table_status"],
 "consumer_binding":d["physical_rate_admission"],
 "synthetic_only_q_HH":demo["q_HH_per_H_s"],
 "out":str(a.out)}))
if __name__=="__main__":main()
