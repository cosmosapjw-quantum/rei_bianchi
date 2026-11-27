# HE-DD target verification evidence, 2026-10-29
Current session execution probes: Python PYTHON_PASS, C++ compiler CPP_PASS, Boost header CPP_PASS.
Command: python -m unittest discover -s tests -p 'test_*.py' -q -> 20 methods, 0 failures, exit0.
Command: python -O -m unittest discover -s tests -q -> 20 methods, 0 failures, exit0.
Command: python -m compileall -q src tests -> exit0.
Command: g++ -std=c++20 -O2 -Wall -Wextra -pedantic tests/independent_cpp_rational.cpp -o independent_cpp_rational && ./independent_cpp_rational -> CPP_PASS exact-rational examples=1089; exit0.
Wolfram exact symbolic check: output {True,0,0,True,0,0,0}; one warning unused symbol, identities exact.
Local current tested source sha1(Git blob) odd_acceptance_count.py bbe49f6cb1eebc0f72c4ac69b2658a371449dbe7; tests test_odd_acceptance_count.py 73bce2904e6f5df2fd035481ccc25cc5701c1e9b; both GitHub fetched SHA matched.
No historical 4501-node LP, original IVP/science suite, physically calibrated detector, actual event rate or thermalization. Independence classification: independent algorithm C++ + CAS, not independent authors R6/C9.
