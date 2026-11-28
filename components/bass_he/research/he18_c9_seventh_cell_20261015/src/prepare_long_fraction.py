#!/usr/bin/env python3
"""Allow serialization of trusted exact Fraction outputs beyond CPython's 4300 digit default.

Only use on hash-pinned, locally archived P01 inputs. This changes NO arithmetic,
rounding mode, or scientific tolerances. It is deliberately source-scoped rather
than global sitecustomize or a change to unrelated production environments.
"""
import argparse
from pathlib import Path
LIMIT=50000
def patch(runtime:Path):
    names=["src/assemble_certificate.py","checks/propagate_seventh.py",
           "checks/verify_seventh.py"]
    for rel in names:
        f=runtime/rel
        if not f.is_file():raise ValueError("MISSING_SERIALIZATION_CONSUMER:"+rel)
        s=f.read_text()
        if "set_int_max_str_digits" in s:raise ValueError("REFUSE_REPEAT_SERIALIZATION_PATCH")
        if rel.startswith("src"):
            needle="from warm_interval import *"
            new=("import sys\n"
                 "# Trusted SHA-pinned P01 source; exact-rational output only.\n"
                 "sys.set_int_max_str_digits(50000)\n"
                 "from warm_interval import *")
        else:
            needle="from fractions import Fraction as Q"
            new=("import sys\n"
                 "sys.set_int_max_str_digits(50000)\n"
                 "from fractions import Fraction as Q")
        if s.count(needle)!=1:raise ValueError("SOURCE_ANCHOR_CHANGED:"+rel)
        f.write_text(s.replace(needle,new,1))
    print("TRUSTED_BIG_FRACTION_SERIALIZATION_PATCHED",names)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--runtime",type=Path,required=True)
    a=p.parse_args()
    patch(a.runtime)
