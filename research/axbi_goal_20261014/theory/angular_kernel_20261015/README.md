# Axisymmetric Bianchi I angular kernel: scoped theory/compute experiment (2026-10-15)

For `ds^2=-c^2 dt^2+a(t)^2[e^{-2b}(dx^2+dy^2)+e^{4b}dz^2]`, comoving photon covariant momenta are conserved. With `mu=p_z/|p|` at b=0, normalized photon energy is `E(t)/E(t_ref)=(a_ref/a)*K(b,mu)/K(b_ref,mu)`, where `K=sqrt((1-mu^2)exp(2b)+mu^2 exp(-4b))`.

The logarithmic geometric drift is `d ln E/d ln a=-1+(db/d ln a)*(1-3 mu_phys^2)` where `mu_phys^2=mu^2 exp(-4b)/K^2`. This kernel gives single-characteristic kinematics only; it is not a photon-conserving absorption/collision solver or a substitute for source-age tracking, gas-temperature coupling or angle-dependent emissivity. The first angular average at b=0 vanishes with isotropic mu weights; at finite b, do not equate the conserved-momentum angular weights with observed solid-angle weights without the Jacobian.

`OPENBLAS_NUM_THREADS=1 python3 research/axbi_goal_20261014/theory/angular_kernel_20261015/check_kernel.py` regenerates `results.json` (performance timings vary). 128-point Gauss-Legendre numerical derivative and first-order angular test are standalone regression checks. Throughput comparison at b=.013 uses vectorized NumPy on 200k cells vs direct math module Python loop on 2k cells, single-thread, no JIT. It quantifies an interpreter-loop saving, NOT speedup of production Rust photon transport. The code materializes one 200k-array and several temporary arrays and may not be optimal for bounded-memory Rust kernels. Numerical differentiation and quadrature tolerances in the test are scoped to these inputs, not project-wide science gates.

AX08 existing actual history comparison remains `RESOLUTION_LIMITED` and scientific response admission is not issued. SOURCE07 C7 found potentially important source-age mixing errors (reported 0.44% HI pooled reference bias in its manufactured two-impulse comparison): that counterexample prevents treating this angular speed experiment as resolving full transfer accuracy. Preserve those source-age lanes and absorption ledgers separately.

Result status: local kernel `NUMERICALLY_CHECKED`; model-specific speed `MEASURED_LOCAL_PYTHON_ONLY`; production integration `NOT_RUN`.
