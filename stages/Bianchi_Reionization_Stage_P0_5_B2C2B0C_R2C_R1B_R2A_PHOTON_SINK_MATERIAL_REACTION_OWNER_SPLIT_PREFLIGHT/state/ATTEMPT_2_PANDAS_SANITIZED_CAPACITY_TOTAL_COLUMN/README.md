# Attempt 2 — pandas sanitized a unit-bearing column name

The scientific calculations completed, but summary assembly accessed
`assigned_total_cMpc-3` through `itertuples()`. Pandas sanitized that field name,
so the reporting layer raised `AttributeError`. The fix uses dictionary records
and the exact CSV column name. No numerical result or gate was changed.
