# Attempt 3 — grid-sampled quadratic range

A dense parameter grid was initially used to estimate fitted quadratic ranges. This is neither exact nor memory-stable for node-resolved tensors. It was replaced by the exact finite candidate set for a bivariate quadratic: four corners, admissible edge stationary points, and an admissible interior stationary point, followed by outward floating-point padding.
