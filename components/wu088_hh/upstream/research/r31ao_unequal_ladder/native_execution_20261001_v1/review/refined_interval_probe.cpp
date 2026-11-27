// Independent analytical integrand 1/t: compare additive refined host versus direct pinned FLINT.
// A positive [2^-8,2^192] path is regular, while its first 128-bit ball query meets 0.
// This is a bounded host-behavior probe, never an actual HH integral.
#include "../../gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.hpp"
#include <flint/arb_calc.h>
#include <iostream>

namespace {
int reciprocal(acb_ptr out, const acb_t t, void *, slong order, slong precision) {
    if (order < 0 || order > 1) {
        acb_indeterminate(out);
    } else {
        acb_inv(out, t, precision);
    }
    return 0;
}
}

int main() {
    constexpr slong precision = 128;
    wu088::petras::Ball a,b,old_result,direct_result,reference;
    acb_one(a.value); acb_mul_2exp_si(a.value,a.value,-8);
    acb_one(b.value); acb_mul_2exp_si(b.value,b.value,192);
    flint_set_num_threads(1);
    wu088::petras::Limits limits;
    limits.precision=precision; limits.max_precision=precision;
    limits.relative_goal=32;
    limits.absolute_tolerance_exp=-40;
    limits.accepted_component_radius_exp=-20;
    limits.per_call_eval_limit=20000;
    limits.queued_panel_limit=256;
    limits.degree_limit=64;
    wu088::petras::GlobalLimits global;
    global.max_dispatched_evaluations=20000;
    global.cooperative_wall_seconds=15;
    wu088::petras::SharedBudget budget(global);
    const auto report=wu088::petras::integrate_1d(old_result.value, reciprocal,
        nullptr,a.value,b.value,limits,budget);

    acb_calc_integrate_opt_t options;
    acb_calc_integrate_opt_init(options);
    options->eval_limit=20000; options->depth_limit=256;
    options->deg_limit=64; options->use_heap=1;
    mag_t tolerance; mag_init(tolerance);
    mag_set_ui_2exp_si(tolerance,1,-40);
    const int direct_status=acb_calc_integrate(direct_result.value,reciprocal,
        nullptr,a.value,b.value,32,tolerance,options,precision);
    mag_clear(tolerance);
    acb_log(reference.value,b.value,precision);
    wu088::petras::Ball loga;
    acb_log(loga.value,a.value,precision);
    acb_sub(reference.value,reference.value,loga.value,precision);
    const bool direct_ok=direct_status==ARB_CALC_SUCCESS &&
        acb_is_finite(direct_result.value) && acb_overlaps(direct_result.value,reference.value);
    const bool refined_accepted=report.status==wu088::petras::Status::RADIUS_MET && !budget.stopped &&
        acb_is_finite(old_result.value) && acb_overlaps(old_result.value,reference.value) &&
        acb_overlaps(old_result.value,direct_result.value);
    std::cout << "{\"refined_status\":\"" << wu088::petras::status_name(report.status)
              << "\",\"refined_dispatched_evaluations\":" << budget.dispatched_evaluations
              << ",\"refined_globally_stopped\":" << (budget.stopped?"true":"false")
              << ",\"direct_status\":" << direct_status
              << ",\"direct_matches_analytic_log_interval\":" << (direct_ok?"true":"false")
              << ",\"refined_enclosure_matches_analytic_and_direct\":" << (refined_accepted&&direct_ok?"true":"false")
              << ",\"hh_integral\":false,\"scientific_admission\":false}\n";
    return refined_accepted && direct_ok ? 0 : 2;
}
