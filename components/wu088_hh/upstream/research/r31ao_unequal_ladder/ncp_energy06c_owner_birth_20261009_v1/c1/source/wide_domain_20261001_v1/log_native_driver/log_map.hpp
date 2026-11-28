#pragma once
#include "../../gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.hpp"
#include <regex>
#include <stdexcept>
#include <string>

namespace wu088::log2map {
struct EndpointInteger {
    fmpz_t value;
    EndpointInteger() { fmpz_init(value); }
    ~EndpointInteger() { fmpz_clear(value); }
    EndpointInteger(const EndpointInteger &)=delete;
};
inline Rational exact_log_endpoint(const char *s,acb_t out) {
    const std::string token(s);
    if (token.size()>320 || !std::regex_match(token,std::regex("[1-9][0-9]*(/[1-9][0-9]*)?")))
        throw std::invalid_argument("positive power-of-two endpoint required");
    Rational q(s);
    if (fmpz_bits(fmpq_numref(q.value))>512 || fmpz_bits(fmpq_denref(q.value))>512)
        throw std::invalid_argument("endpoint bit cap exceeded");
    char *canonical=fmpq_get_str(nullptr,10,q.value);
    if (!canonical) throw std::bad_alloc();
    const std::string canonical_token(canonical);flint_free(canonical);
    if (canonical_token!=token) throw std::invalid_argument("noncanonical endpoint");
    EndpointInteger reduced,numerator;
    const auto denominator_power=fmpz_val2(fmpq_denref(q.value));
    const auto numerator_power=fmpz_val2(fmpq_numref(q.value));
    fmpz_tdiv_q_2exp(reduced.value,fmpq_denref(q.value),denominator_power);
    fmpz_tdiv_q_2exp(numerator.value,fmpq_numref(q.value),numerator_power);
    if (!fmpz_is_one(reduced.value) || !fmpz_is_one(numerator.value))
        throw std::invalid_argument("endpoint is not a power of two");
    acb_set_si(out,static_cast<slong>(numerator_power)-static_cast<slong>(denominator_power));
    if (!acb_is_exact(out)) throw std::runtime_error("exact log endpoint construction failed");
    return q;
}

// A fixed-precision enclosure of log(2), computed once per invocation.
// The physical callback owns all source-function and domain authority.
struct Context {
    petras::Bivariate physical;
    petras::Ball log_two;
    slong precision;
    Context(const petras::Bivariate &b,slong p):physical(b),precision(p) {
        acb_zero(log_two.value);
        arb_const_log2(acb_realref(log_two.value),p);
    }
};
inline int callback(acb_ptr out,const acb_t x,const acb_t y,void *opaque,
                    slong order,slong precision) {
    if (!opaque || order<0 || order>1) {
        for (slong k=0;k<(order>0?order:1);++k) acb_indeterminate(out+k);
        return 0;
    }
    auto &context=*static_cast<Context *>(opaque);
    if (!context.physical.callback || precision!=context.precision ||
        !context.physical.uniform_whole_parameter_box || !context.physical.joint_holomorphy_proved) {
        acb_indeterminate(out); return 0;
    }
    petras::Ball t,u,jacobian;
    acb_mul(t.value,x,context.log_two.value,precision);
    acb_exp(t.value,t.value,precision);
    acb_mul(u.value,y,context.log_two.value,precision);
    acb_exp(u.value,u.value,precision);
    // Neither input is replaced with its midpoint. In particular the entire
    // outer complex parameter image is passed to the uniform-inner callback.
    context.physical.callback(out,t.value,u.value,context.physical.param,order,precision);
    if (!acb_is_finite(out)) { acb_indeterminate(out); return 0; }
    acb_mul(jacobian.value,context.log_two.value,context.log_two.value,precision);
    acb_mul(jacobian.value,jacobian.value,t.value,precision);
    acb_mul(jacobian.value,jacobian.value,u.value,precision);
    acb_mul(out,out,jacobian.value,precision);
    return 0;
}
}
