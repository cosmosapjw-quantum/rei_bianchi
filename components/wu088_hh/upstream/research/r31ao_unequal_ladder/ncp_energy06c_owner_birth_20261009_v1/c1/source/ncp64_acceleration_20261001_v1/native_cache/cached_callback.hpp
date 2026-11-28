#ifndef WU088_CACHED_CALLBACK_HPP
#define WU088_CACHED_CALLBACK_HPP
#include "../../gap_closure_20261001_g0_g6_v1/validated_callback/callback.hpp"

namespace wu088 {
// Counts attempted helper calls and successful reuse, never estimated FLOPs.
// One invocation resets the counters. They are not shared between threads.
struct CacheStats {
    unsigned long terms_started=0, terms_completed=0;
    unsigned long left_requests=0, right_requests=0, spatial_requests=0;
    unsigned long left_evaluations=0, right_evaluations=0, spatial_evaluations=0;
    unsigned long left_hits=0, right_hits=0, spatial_hits=0;
};
int polynomial_field_cached(acb_t out,const std::vector<Term> &,Orbital,Field,
                            const acb_t t,const acb_t u,const Parameters &,
                            Contract &,CacheStats &) noexcept;
struct CachedSlice {
    Slice source;
    CacheStats *stats=nullptr;
};
int cached_slice_callback(acb_ptr out,const acb_t inner,void *param,
                          slong order,slong prec);
}
#endif
