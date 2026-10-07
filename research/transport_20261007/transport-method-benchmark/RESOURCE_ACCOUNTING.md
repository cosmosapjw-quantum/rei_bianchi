Publication note: quoted hashes identify archived original bytes; current publication hashes are listed in ../PROVENANCE.json.

# Array and point accounting
Implementation is one Rust process and one test thread. Python oracle/assessment runs are serial; every execution is recorded by budget.py. Rust compilation uses one codegen unit and one linker thread after a captured default-linker thread-creation failure under the 512 MiB process limit. No package installation occurred.

At n=256:
- Fixed quadrature tables: 8 + 16 pairs, 48 scalars. These are reference-rule coordinates, not extra simultaneously evaluated physical sites.
- Init.cells: n structs * (Eleft,Eright,a,b) = 1,024 doubles.
- Init.panels: n triples = 768 doubles.
- Init.nodes: 8n pairs (comoving x,weight) = 4,096 doubles, representing 2,048 distinct physical quadrature sites.
- PDE initialization additionally clones n cells = 1,024 doubles. Before time stepping, all Init vectors are dropped. Peak initialization is 27n = 6,912 doubles (55,296 payload bytes), excluding capacities/allocator metadata.
- PDE stepping: state n cells (4n doubles), stage n cells (4n), flux0 n+1 and flux1 n+1 (2n+2), totaling 10n+2 = 2,562 doubles (20,496 payload bytes). No separate RHS vector exists; slopes are evaluated into stack scalars.
- Cell energy faces are fields in Cell, not a hidden additional face vector. Their duplication between state and stage is included above.
- Per-output bins: 32 doubles; output epochs: 9 doubles; diagnostic evaluation streams a rule, at most 16 mapped physical sites per cell, without a full-grid sample array.
- Characteristic cases retain Init vectors while diagnostics stream. Conservative upper bound on concurrently live distinct physical quadrature sites = 2,048 + 16 = 2,064, below 4,096. A/B moment reductions and bins do not allocate a second quadrature-site grid.
- Python oracle: scalar adaptive mpmath quadrature plus 9 epoch dictionaries and 32 masses each, in a separate serial process. Original cross-interval caching was audited and failed at4,369>4,096 sites. The single cache-policy fix clears each integral and its audited complete replay peaks at2,157 cached/active distinct abscissae, including a conservative previous-rule allowance. The original failure is retained; final bounded reference is byte-identical.
- Projection-split analysis holds one initial grid at a time, at most2,048 stock sites; no additional PDE history is evaluated.

All numbers above are owned numeric-array payloads, not whole-process RSS. Recorded process peak RSS/address-space bound and task output bytes are in BUDGET.json. No workload complexity conclusion should be based on these small wall timings alone.
