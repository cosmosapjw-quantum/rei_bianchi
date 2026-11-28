# R7 portability design record: O_A and O_B

Status: design only. The PR15 exact stored/fresh matching-error hex comparison and verifier-owned policy remain unchanged. Cross-host portability is unresolved; the same-host OpenBLAS 1-to-4-thread success is not cross-host evidence.

O_A is the immutable original certificate bytes plus trusted SHA256. A destination environment may initiate a separate explicit revalidation to create O_B; it must never mutate O_A or catch validation errors and silently replace the certificate.

Minimum O_B input: parent O_A raw SHA256; canonical exact endpoint identity (state_a, state_b, R, p, lambda, depth, Z1, Z2); policy ID and parameters; verifier/scientific source revision and hash; destination numerical environment identity. Minimum output: fresh spectral simple-fold result, fresh pair-membership result, fresh matching-error hex value, stored canonical binding and digest, decision, UTC, and parent link. Python/NumPy/SciPy/BLAS versions, build hashes, thread count and architecture are provenance, not admission authority. The new record must be constructed from fresh local semantics and then pass the unchanged strict validator.

Likely impacted files for a separately approved implementation: `src/bass_he/spectral.py` producer/revalidator interface, a new explicit certificate revalidation wrapper, and focused tests for provenance, failure isolation, exact identity, and destination false rejection. This closeout creates no wrapper or new admission path and does not extend CODE-I02 closure to a future implementation.
