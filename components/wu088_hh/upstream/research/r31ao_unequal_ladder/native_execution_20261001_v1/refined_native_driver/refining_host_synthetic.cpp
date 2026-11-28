// Bounded analytic/contract regression. No HH data, coefficients or callbacks.
#include WU088_HOST_SOURCE
#include <iostream>
#include <stdexcept>

namespace {
using namespace wu088::petras;
int reciprocal(acb_ptr out,const acb_t x,void *,slong,slong prec) {
    acb_inv(out,x,prec); return 0;
}
int refuses(acb_ptr out,const acb_t,void *,slong,slong) {
    acb_indeterminate(out); return 0;
}
int throws(acb_ptr,const acb_t,void *,slong,slong) {
    throw std::invalid_argument("synthetic invalid contract");
}
int wide_parameter(acb_ptr out,const acb_t,const acb_t outer,void *,slong,slong) {
    acb_set(out,outer); return 0;
}
bool counted_case(bool range,bool speculative,slong order,slong precision,
                  acb_calc_func_t function,bool exhausted,Status expected,bool stopped) {
    Limits limits; GlobalLimits global; SharedBudget budget(global); Ball x,out;
    acb_one(x.value);
    if (range) arb_add_error_2exp_si(acb_realref(x.value),-3);
    if (exhausted) budget.dispatched_evaluations=global.max_dispatched_evaluations;
    Counted context{function,nullptr,&limits,&budget,speculative};
    counted_callback(out.value,x.value,&context,order,precision);
    return !acb_is_finite(out.value) && budget.stopped==stopped &&
        (!stopped || budget.stop_status==expected);
}
}
int main() {
    using namespace wu088::petras;
    flint_set_num_threads(1);
    Ball a,b,result,reference,loga;
    acb_one(a.value);acb_mul_2exp_si(a.value,a.value,-8);
    acb_one(b.value);acb_mul_2exp_si(b.value,b.value,192);
    Limits limits; limits.precision=128;limits.max_precision=128;
    limits.relative_goal=32;limits.absolute_tolerance_exp=-40;
    limits.accepted_component_radius_exp=-20;limits.per_call_eval_limit=20000;
    limits.queued_panel_limit=256;limits.degree_limit=64;
    GlobalLimits global;global.max_dispatched_evaluations=20000;
    global.cooperative_wall_seconds=15;
    SharedBudget budget(global);
    auto report=integrate_1d(result.value,reciprocal,nullptr,a.value,b.value,limits,budget);
    acb_log(reference.value,b.value,128);acb_log(loga.value,a.value,128);
    acb_sub(reference.value,reference.value,loga.value,128);
    const bool matches=acb_is_finite(result.value) && acb_overlaps(result.value,reference.value);
    const bool analytic_pass=report.status==Status::RADIUS_MET && !budget.stopped && matches;
    const bool range_refinable=counted_case(true,false,0,128,refuses,false,Status::NONFINITE_CALLBACK,false);
    const bool exact_fatal=counted_case(false,false,0,128,refuses,false,Status::NONFINITE_CALLBACK,true);
    const bool speculative_refinable=counted_case(false,true,0,128,refuses,false,Status::NONFINITE_CALLBACK,false);
    const bool exception_fatal=counted_case(true,false,0,128,throws,false,Status::INVALID_CONTRACT,true);
    const bool precision_fatal=counted_case(true,false,0,64,refuses,false,Status::INVALID_CONTRACT,true);
    const bool order_fatal=counted_case(true,false,-1,128,refuses,false,Status::INVALID_CONTRACT,true);
    const bool budget_fatal=counted_case(true,false,0,128,refuses,true,Status::RESOURCE_LIMIT,true);
    // A finite uniform image can be too wide for the inner acceptance gate.
    // The outer parameter box is not a point: report refusal, never narrow it.
    Ball inner_a,inner_b,outer,out;acb_zero(inner_a.value);acb_one(inner_b.value);
    acb_one(outer.value);arb_add_error_2exp_si(acb_realref(outer.value),30);
    Bivariate fn;fn.callback=wide_parameter;fn.uniform_whole_parameter_box=true;
    fn.joint_holomorphy_proved=true;fn.proof_reference="entire linear analytic fixture";
    NestedPlan nested;nested.uniform_inner.absolute_tolerance_exp=32;
    SharedBudget outer_budget(global);
    OuterContext outer_context{&fn,inner_a.value,inner_b.value,&nested,&outer_budget};
    outer_callback(out.value,outer.value,&outer_context,0,128);
    const bool outer_refinable=!outer_budget.stopped && !acb_is_finite(out.value);
    const bool fatal_guards=exact_fatal&&exception_fatal&&precision_fatal&&order_fatal&&budget_fatal;
    std::cout << "{\"schema\":\"WU088_REFINING_HOST_SYNTHETIC_V1\",\"status\":\""
      << status_name(report.status) << "\",\"analytic_pass\":" << (analytic_pass?"true":"false")
      << ",\"matches_analytic_log\":" << (matches?"true":"false")
      << ",\"dispatched_evaluations\":" << budget.dispatched_evaluations
      << ",\"range_refinable\":" << (range_refinable?"true":"false")
      << ",\"exact_point_fatal\":" << (exact_fatal?"true":"false")
      << ",\"speculative_parameter_refinable\":" << (speculative_refinable?"true":"false")
      << ",\"invalid_exception_fatal\":" << (exception_fatal?"true":"false")
      << ",\"invalid_precision_fatal\":" << (precision_fatal?"true":"false")
      << ",\"invalid_order_fatal\":" << (order_fatal?"true":"false")
      << ",\"resource_limit_fatal\":" << (budget_fatal?"true":"false")
      << ",\"outer_width_refinable\":" << (outer_refinable?"true":"false")
      << ",\"hh_evaluations\":0,\"scientific_admission\":false}\n";
    return analytic_pass&&range_refinable&&speculative_refinable&&outer_refinable&&fatal_guards ? 0 : 2;
}
