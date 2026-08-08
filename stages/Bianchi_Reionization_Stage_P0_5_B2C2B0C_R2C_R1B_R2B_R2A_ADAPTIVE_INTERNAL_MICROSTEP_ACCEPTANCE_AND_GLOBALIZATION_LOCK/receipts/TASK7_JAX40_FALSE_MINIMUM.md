# JAX root iteration false minimum

The exploratory full-batch residual probe suggested 40 bisection iterations.
The independent NumPy-oracle parity test falsified that setting: maximum
relative temperature parity was 1.6608923011431727e-11, above the pre-existing
1e-11 parity gate. The locked candidate was therefore increased by one
iteration to 41 before production use. No science run used the rejected
40-iteration setting.
