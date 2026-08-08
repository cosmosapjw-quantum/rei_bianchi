# Attempt 2 — scalar-only quadratic fit

The first quadratic endpoint helper assumed scalar outputs. The real endpoint object has tensor shape `(field,node)`, so the fit silently had the wrong interface. A RED test reproduced the shape failure; the implementation now flattens only the output tail, solves the common design matrix, and restores the original tensor shape.
