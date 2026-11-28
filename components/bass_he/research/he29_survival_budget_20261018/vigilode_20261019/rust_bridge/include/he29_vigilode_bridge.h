#ifndef HE29_VIGILODE_BRIDGE_H
#define HE29_VIGILODE_BRIDGE_H
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* All arrays have n elements. Callbacks return zero only after filling every
 * output element with a finite value. They must not unwind or throw. */
typedef int32_t (*He29RhsCallback)(void *context, double u,
    const double *z, size_t n, double *out);
typedef int32_t (*He29JvpCallback)(void *context, double u,
    const double *z, const double *v, size_t n, double *out);

typedef struct He29Stats {
    uint32_t abi_version;
    int32_t status;
    size_t dimension;
    double final_u;
    size_t output_samples;
    size_t internal_steps;
    size_t output_clipped_steps;
    size_t attempts;
    size_t accepted_macro_steps;
    size_t rejected_macro_steps;
    uint64_t rhs_evaluations;
    uint64_t jvp_vectors;
    uint64_t linear_iterations;
    uint64_t direct_factorizations;
    uint64_t callback_rhs_calls;
    uint64_t callback_jvp_calls;
    uint64_t callback_partial_u_calls;
    size_t json_required_bytes;
} He29Stats;

enum {
    HE29_VIGILODE_OK = 0,
    HE29_VIGILODE_PARTIAL = 1,
    HE29_VIGILODE_INVALID_ARGUMENT = 2,
    HE29_VIGILODE_CALLBACK_ERROR = 3,
    HE29_VIGILODE_SOLVER_ERROR = 4,
    HE29_VIGILODE_RUST_PANIC = 5,
    HE29_VIGILODE_BUSY = 6,
    HE29_VIGILODE_JSON_BUFFER_SMALL = 7
};

uint32_t he29_vigilode_abi_version(void);
/* Integrates an already scaled state z over u in [0,1]. Tolerances are fixed:
 * rtol=1e-10, atol=1e-12. No dense interpolation is used.
 *
 * Pointers must address valid caller-owned storage of the specified lengths;
 * z_out must not overlap z0 or stats/json. On a partial solve z_out is the last
 * observed state, which can be z0 if the endpoint was not reached.
 * json_out is NUL-terminated if json_capacity > 0. 65536 bytes is recommended.
 * No callback or buffer may be released while the call is in flight.
 * Only one solve may be active in this library; concurrent calls return BUSY.
 */
int32_t he29_vigilode_segment(size_t n, const double *z0,
    He29RhsCallback rhs, He29JvpCallback jvp, He29RhsCallback partial_u,
    void *context, double initial_step, double max_step, size_t max_attempts,
    double *z_out, He29Stats *stats, char *json_out, size_t json_capacity);

#ifdef __cplusplus
}
#endif
#endif
