"""Only fixed-form signed rational synthetic payloads; no scientific loader."""
import argparse
from fractions import Fraction
import os
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument("--output", required=True)
p.add_argument("--numerator", type=int, required=True)
p.add_argument("--denominator", type=int, required=True)
p.add_argument("--sleep-ms", type=int, default=0)
p.add_argument("--mode", choices=("ok", "fail", "partial", "timeout", "child", "memory"), default="ok")
p.add_argument("--literal", default="")
p.add_argument("--work-units", type=int, default=0)
a = p.parse_args()
Path("started.pid").write_text(str(os.getpid()))
counter = Path("invocations.txt")
counter.write_text(str(int(counter.read_text()) + 1 if counter.exists() else 1))
if a.mode == "timeout":
    time.sleep(10)
elif a.mode == "memory":
    block = bytearray(80 * 1024 * 1024)
    for i in range(0, len(block), 4096):
        block[i] = 1
    time.sleep(4)
elif a.mode == "child":
    child = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(10)"])
    Path("descendant.pid").write_text(str(child.pid))
if a.sleep_ms:
    time.sleep(a.sleep_ms / 1000)
v = Fraction(a.numerator, a.denominator)
if not 0 <= a.work_units <= 5000000:
    raise SystemExit("bounded work units required")
total = 0
for k in range(1, a.work_units + 1):
    total += k * k
raw = ("EXACT_RATIONAL_V1\n" + str(v.numerator) + "/" + str(v.denominator)
       + "\nimag=0/1\nliteral=" + a.literal + "\n").encode("utf-8")
if a.work_units:
    raw += ("exact_sum_of_squares=" + str(total) + "\n").encode("ascii")
with Path(a.output).open("xb") as f:
    f.write(b"PARTIAL" if a.mode == "partial" else raw)
if a.mode == "fail":
    raise SystemExit(7)
print("synthetic exact rational completed")
