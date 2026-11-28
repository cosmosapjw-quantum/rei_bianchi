#include "cached_callback.hpp"
#include <optional>

// Compile this TU instead of separately compiling callback.cpp. This imports
// the immutable baseline, including its exact helper expression trees, once.
// SOURCE_LOCK.json binds both original files. No copied/reimplemented formula.
#include "../../gap_closure_20261001_g0_g6_v1/validated_callback/callback.cpp"

namespace wu088 {
int polynomial_field_cached(acb_t out,const std::vector<Term> &terms,
                            Orbital ell,Field field,const acb_t t,const acb_t u,
                            const Parameters &par,Contract &c,CacheStats &stats) noexcept {
    stats=CacheStats{};
    try {
        check(c);
        if (terms.empty() || terms.size()>107)
            throw std::domain_error("nonempty finite polynomial <=107 terms required");
        Ball bt(c.precision,t,true),bu(c.precision,u,true),sum(c.precision,0);
        // Slots belong to this invocation only; no quantized/midpoint cache key.
        std::array<std::optional<Ball>,9> left{},right{},space{};
        auto get_left=[&](unsigned i)->const Ball & {
            ++stats.left_requests;
            if (i>8) {
                ++stats.left_evaluations;
                (void)density(i,bt,par.mu,c.margin); // original failure message
                throw std::logic_error("unreachable invalid density degree");
            }
            if (!left[i]) {
                ++stats.left_evaluations;
                left[i].emplace(density(i,bt,par.mu,c.margin));
            } else ++stats.left_hits;
            return *left[i];
        };
        auto get_right=[&](unsigned j)->const Ball & {
            ++stats.right_requests;
            if (j>8) {
                ++stats.right_evaluations;
                (void)density(j,bu,par.mu,c.margin);
                throw std::logic_error("unreachable invalid density degree");
            }
            if (!right[j]) {
                ++stats.right_evaluations;
                right[j].emplace(density(j,bu,par.mu,c.margin));
            } else ++stats.right_hits;
            return *right[j];
        };
        auto get_spatial=[&](unsigned k)->const Ball & {
            ++stats.spatial_requests;
            if (k>8) {
                ++stats.spatial_evaluations;
                (void)spatial(k,ell,field,bt,bu,par,c.margin);
                throw std::logic_error("unreachable invalid spatial degree");
            }
            if (!space[k]) {
                ++stats.spatial_evaluations;
                space[k].emplace(spatial(k,ell,field,bt,bu,par,c.margin));
            } else ++stats.spatial_hits;
            return *space[k];
        };
        for (const auto &term:terms) {
            ++stats.terms_started;
            // Same left-associated multiplication tree and same term/sum order
            // as the imported baseline; no reassociation or zero screening.
            Ball value=Ball(c.precision,term.coefficient)
                *get_left(term.i)*get_right(term.j)*get_spatial(term.k);
            sum=sum+value;
            ++stats.terms_completed;
        }
        finite(sum); acb_set(out,sum.v); return 0;
    } catch (const std::exception &e) { return fail(out,c,e.what()); }
    catch (...) { return fail(out,c,"unknown callback exception"); }
}

int cached_slice_callback(acb_ptr out,const acb_t inner,void *param,
                          slong order,slong prec) {
    CachedSlice *cached=static_cast<CachedSlice *>(param);
    if (cached && cached->stats) *cached->stats=CacheStats{};
    if (!cached || !cached->stats || !cached->source.parameters ||
        !cached->source.terms || !cached->source.contract || !cached->source.outer_box) {
        invalidate_requested_coefficients(out,order); return 0;
    }
    Slice &slice=cached->source;
    Contract &c=*slice.contract;
    if (order!=0 && order!=1) {
        fail(out,c,"unsupported acb_calc order; order is not a radial derivative");
        invalidate_requested_coefficients(out,order); return 0;
    }
    if (prec!=c.precision) {
        fail(out,c,"integration precision must equal declared callback precision"); return 0;
    }
    polynomial_field_cached(out,*slice.terms,slice.orbital,slice.field,
                            inner,slice.outer_box,*slice.parameters,c,*cached->stats);
    return 0;
}
}
