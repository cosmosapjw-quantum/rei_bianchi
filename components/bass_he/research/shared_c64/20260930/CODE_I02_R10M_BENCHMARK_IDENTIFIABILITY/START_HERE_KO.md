# BASS_HE R10M / R10N start

Basis: R10L cb6d35cabc3cdbcad4f4dab01a3c30fca81e20d8.
R10M result: R10M_ARCHIVED_RANK_REVERSAL_VERIFIED.
Physical verdict remains PHYSICAL_SUPPORT_UNRESOLVED.

At 5 keV/u n=2, fixed B=1.624481683794208e-15 and C=1.0086606432823275e-15 cm^2 tie in logarithmic loss at sqrt(B*C)=1.2800588815270274e-15 cm^2. The entire recorded S1 extraction interval is below this value and S2's rounding interval is above it. Finer reading within those intervals does not remove the ranking reversal. Neither interval bounds physical theory error.

This GitHub namespace is a delivery subset: START_HERE_KO.md, DECISION.json and DELIVERY_RECEIPT.json. Full runnable code, tests, raw small fixtures, report and handoff are in BASS_HE_R10M_BENCHMARK_IDENTIFIABILITY_20260930_v1.zip. Read DELIVERY_RECEIPT.json for exact archive SHA256, size and provider IDs. Do not treat this subset as the full package.

After ZIP/MANIFEST verification, read HANDOFF_KO.md and run:

    python -m unittest discover -s tests -v
    python identifiability.py --out return/IDENTIFIABILITY.json

Python >=3.11, standard library only. Expected 21 tests and eight archived comparison rows. This is not a BASS_HE scientific replay. No NumPy/SciPy installation is required.

The next R10N task is a bounded source-authority intake, not new C/Delta/rotation/transport calculations. Only if an actually available new primary S3 table exists, preserve all method columns, exact energy/species/observable identity and unknown theory uncertainty. Do not repeat failed URLs or fill table values from abstracts. With no new primary row, return BENCHMARK_AUTHORITY_OPEN_NO_NEW_DATA and end normally.

Do not average S1/S2, treat correlated rows as votes, or relabel WH/CTF columns quoted in S2 as newly admitted independent sources. The low-energy n=1 discrepancy is a separate future theory question; no new mechanism implementation is authorized here.

PR15 expected source: b8b2fe47a367459f6faf6796eb2f251feacbbd7c. Fresh-read root AGENTS.md and refs. Use append-only/nonforce publication on the existing PR17 research branch; do not create a new branch or modify production.

Gates unchanged: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
