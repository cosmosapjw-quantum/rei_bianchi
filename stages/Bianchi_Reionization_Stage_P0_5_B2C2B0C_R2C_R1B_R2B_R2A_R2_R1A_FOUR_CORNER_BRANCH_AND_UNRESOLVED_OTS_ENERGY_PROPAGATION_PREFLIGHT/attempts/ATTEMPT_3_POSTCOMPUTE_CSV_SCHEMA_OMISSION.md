# ATTEMPT 3 — post-compute CSV schema omission

Classification: `NON_SCIENTIFIC_SERIALIZATION_FAILURE_AFTER_24_POLICY_COMPUTE`.

The 24-policy calculation reached the final CSV writer, then failed because the newly introduced `local_error_gate` field was absent from the fixed CSV field list. No result table or verdict was promoted. The traceback and empty-header partial CSV are preserved as attempt evidence.

Root-cause fix: expose one `CSV_FIELDS` tuple, include `local_error_gate`, and test that every canonical field serializes before rerunning the science matrix. No physical equation or numerical gate changed.
