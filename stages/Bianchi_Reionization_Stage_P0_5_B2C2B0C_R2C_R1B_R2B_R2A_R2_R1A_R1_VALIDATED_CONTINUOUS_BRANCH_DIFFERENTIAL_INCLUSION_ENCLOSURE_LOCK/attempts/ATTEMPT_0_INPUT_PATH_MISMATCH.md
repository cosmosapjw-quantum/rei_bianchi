# Attempt 0 — input path mismatch

The first pre-calculation lock generator referenced `thermal_backends.py` under the R2A-R1 thermochemistry stage. The authoritative file actually lives under the preceding R2A adaptive-globalization stage. The generator stopped before writing `INPUT_LOCK.json`, before any science calculation, and before any commit. The corrected path is used in the locked input manifest.
