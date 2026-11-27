#include "../gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.hpp"
#include <flint/arb_calc.h>
#include <algorithm>
#include <cmath>
#include <limits>

#if __FLINT_RELEASE != 30400
#error "This native draft is pinned to FLINT 3.4.0"
#endif
namespace wu088::petras {
namespace {
struct Magnitude {
    mag_t value;
    Magnitude() { mag_init(value); }
    ~Magnitude() { mag_clear(value); }
};
void invalidate(acb_ptr out,slong order) noexcept {
    // acb_calc currently requests 0 or 1. For an unsupported n>1, all n
    // requested Taylor coefficients must be nonfinite, not only out[0].
    const slong count=order>0 ? order : 1;
    for (slong k=0;k<count;++k) acb_indeterminate(out+k);
}
bool radius_ok(const acb_t out,slong exponent) noexcept {
    if (!acb_is_finite(out)) return false;
    return mag_cmp_2exp_si(arb_radref(acb_realref(out)),exponent)<=0 &&
           mag_cmp_2exp_si(arb_radref(acb_imagref(out)),exponent)<=0;
}
void record_returned_radii(Report &report,const acb_t out) {
    char *real=mag_dump_str(arb_radref(acb_realref(out)));
    char *imag=mag_dump_str(arb_radref(acb_imagref(out)));
    report.real_radius_dump=real;
    report.imag_radius_dump=imag;
    flint_free(real); flint_free(imag);
}
bool valid_limits(const Limits &p) noexcept {
    return p.precision>=32 && p.precision<=p.max_precision && p.max_precision<=4096 &&
        p.relative_goal>=0 && p.relative_goal<=p.precision &&
        p.absolute_tolerance_exp>=-4096 && p.absolute_tolerance_exp<=4096 &&
        p.accepted_component_radius_exp>=-4096 && p.accepted_component_radius_exp<=4096 &&
        p.per_call_eval_limit>0 && p.per_call_eval_limit<=1000000 &&
        p.queued_panel_limit>0 && p.queued_panel_limit<=4096 &&
        p.degree_limit>0 && p.degree_limit<=1024;
}
bool exact_real_endpoints(const acb_t a,const acb_t b) noexcept {
    return acb_is_finite(a) && acb_is_finite(b) && acb_is_exact(a) && acb_is_exact(b) &&
        arb_is_zero(acb_imagref(a)) && arb_is_zero(acb_imagref(b));
}
struct Counted {
    acb_calc_func_t function;
    void *param;
    const Limits *limits;
    SharedBudget *budget;
    bool speculative_parameter_trial;
};
int counted_callback(acb_ptr out,const acb_t x,void *opaque,slong order,slong prec) {
    auto &c=*static_cast<Counted *>(opaque);
    SharedBudget &budget=*c.budget;
    if (budget.callback_entries<std::numeric_limits<std::size_t>::max()) ++budget.callback_entries;
    if (budget.stopped || !budget.wall_ok()) { invalidate(out,order); return 0; }
    if (order<0 || order>1 || prec!=c.limits->precision) {
        budget.stop(Status::INVALID_CONTRACT,"unsupported_order_or_precision");
        invalidate(out,order); return 0;
    }
    if (budget.dispatched_evaluations >= budget.limits.max_dispatched_evaluations) {
        budget.stop(Status::RESOURCE_LIMIT,"max_dispatched_evaluations");
        invalidate(out,order); return 0;
    }
    ++budget.dispatched_evaluations;
    try { (void)c.function(out,x,c.param,order,prec); }
    catch (...) {
        budget.stop(Status::INVALID_CONTRACT,"callback_exception");
        invalidate(out,order); return 0;
    }
    if (!acb_is_finite(out)) {
        if ((order==1 || c.speculative_parameter_trial || !acb_is_exact(x)) && !budget.stopped) {
            // A nonexact order-0 input is a range request, not a point value.
            // Refuse the complete box so FLINT can bisect; never shrink its
            // image or replace it with the midpoint. Exact point failures and
            // all already-stopped shared budgets remain fatal.
            if (order==1) ++budget.analytic_box_refusals;
            invalidate(out,order); return 0;
        }
        budget.stop(Status::NONFINITE_CALLBACK,"callback_returned_nonfinite");
        invalidate(out,order); return 0;
    }
    if (!budget.wall_ok()) invalidate(out,order);
    return 0;
}
bool valid_bivariate(const Bivariate &b) noexcept {
    return b.callback && b.uniform_whole_parameter_box && b.joint_holomorphy_proved &&
           b.proof_reference && b.proof_reference[0]!='\0';
}
bool valid_nested(const NestedPlan &p) noexcept {
    return valid_limits(p.outer) && valid_limits(p.point_inner) && valid_limits(p.uniform_inner) &&
        p.outer.precision==p.point_inner.precision && p.outer.precision==p.uniform_inner.precision &&
        p.tight_parameter_radius_exp>=-4096 && p.tight_parameter_radius_exp<=0;
}
struct InnerContext {
    const Bivariate *bivariate=nullptr;
    Ball outer_box;
    slong outer_order=0;
};
int inner_callback(acb_ptr out,const acb_t inner,void *opaque,slong inner_order,slong prec) {
    auto &context=*static_cast<InnerContext *>(opaque);
    const slong outer_order=context.outer_order;
    const slong analytic_order=(outer_order == 1 || inner_order == 1) ? 1 : 0;
    return context.bivariate->callback(out,inner,context.outer_box.value,
                                      context.bivariate->param,analytic_order,prec);
}
struct OuterContext {
    const Bivariate *bivariate;
    acb_srcptr inner_a;
    acb_srcptr inner_b;
    const NestedPlan *plan;
    SharedBudget *budget;
};
int outer_callback(acb_ptr out,const acb_t outer_box,void *opaque,slong order,slong prec) {
    auto &context=*static_cast<OuterContext *>(opaque);
    if (prec!=context.plan->outer.precision) {
        context.budget->stop(Status::INVALID_CONTRACT,"outer_precision_mismatch");
        invalidate(out,order); return 0;
    }
    Report report=integrate_uniform_inner(out,*context.bivariate,context.inner_a,context.inner_b,
                                         outer_box,order,*context.plan,*context.budget);
    if (report.status!=Status::RADIUS_MET) {
        if ((order==1 || !acb_is_exact(outer_box)) && !context.budget->stopped &&
            (report.status==Status::NONFINITE_CALLBACK ||
             report.status==Status::INTEGRATOR_NO_CONVERGENCE || report.status==Status::RADIUS_TOO_WIDE)) {
            if (order==1) ++context.budget->analytic_box_refusals;
        } else context.budget->stop(report.status,report.reason);
        invalidate(out,order);
    }
    return 0;
}
}

bool SharedBudget::stop(Status s,const char *why) noexcept {
    if (!stopped) { stopped=true; stop_status=s; reason=why; }
    return false;
}
bool SharedBudget::wall_ok() noexcept {
    if (stopped) return false;
    if (!std::isfinite(limits.cooperative_wall_seconds) || limits.cooperative_wall_seconds<=0)
        return stop(Status::INVALID_CONTRACT,"invalid_wall_limit");
    if (std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=limits.cooperative_wall_seconds)
        return stop(Status::RESOURCE_LIMIT,"cooperative_wall_limit");
    return true;
}
Report integrate_1d(acb_t out,acb_calc_func_t callback,void *param,
                    const acb_t a,const acb_t b,const Limits &p,SharedBudget &budget,
                    bool speculative_parameter_trial) noexcept {
    acb_indeterminate(out);
    if (!callback || !valid_limits(p) || !exact_real_endpoints(a,b) || flint_get_num_threads() != 1 ||
        budget.limits.max_dispatched_evaluations==0 || budget.limits.max_dispatched_evaluations>10000000 ||
        budget.limits.max_integration_calls==0 || budget.limits.max_integration_calls>1000000 ||
        budget.limits.max_nested_integrations==0 || budget.limits.max_nested_integrations>2) {
        budget.stop(Status::INVALID_CONTRACT,"invalid_caps_endpoints_or_thread_contract");
        return {budget.stop_status,-1,false,budget.reason};
    }
    if (!budget.wall_ok()) return {budget.stop_status,-1,false,budget.reason};
    if (budget.integration_calls >= budget.limits.max_integration_calls ||
        budget.active_integrations>=budget.limits.max_nested_integrations ||
        budget.dispatched_evaluations>=budget.limits.max_dispatched_evaluations) {
        budget.stop(Status::RESOURCE_LIMIT,"global_integrator_or_dispatch_limit");
        return {budget.stop_status,-1,false,budget.reason};
    }
    ++budget.integration_calls;
    ++budget.active_integrations;
    budget.peak_active_integrations=std::max(budget.peak_active_integrations,budget.active_integrations);
    acb_calc_integrate_opt_t options;
    acb_calc_integrate_opt_init(options);
    options->eval_limit=p.per_call_eval_limit;
    options->depth_limit=p.queued_panel_limit;
    options->deg_limit=p.degree_limit;
    options->use_heap=1;
    options->verbose=0;
    Magnitude abs_tol;
    mag_set_ui_2exp_si(abs_tol.value,1,p.absolute_tolerance_exp);
    Counted context{callback,param,&p,&budget,speculative_parameter_trial};
    const int code=acb_calc_integrate(out,counted_callback,&context,a,b,
                                    p.relative_goal,abs_tol.value,options,p.precision);
    --budget.active_integrations;
    if (!budget.wall_ok()) {
        acb_indeterminate(out); return {budget.stop_status,code,false,budget.reason};
    }
    if (code!=ARB_CALC_SUCCESS) {
        acb_indeterminate(out); return {Status::INTEGRATOR_NO_CONVERGENCE,code,false,"integrator_nonconvergence"};
    }
    if (!acb_is_finite(out)) {
        acb_indeterminate(out); return {Status::NONFINITE_CALLBACK,code,false,"nonfinite_integral"};
    }
    if (!radius_ok(out,p.accepted_component_radius_exp)) {
        // Acceptance authority is the returned ball radius, not requested tol.
        Report report{Status::RADIUS_TOO_WIDE,code,false,"achieved_component_radius_too_wide"};
        record_returned_radii(report,out);
        acb_indeterminate(out); return report;
    }
    Report report{Status::RADIUS_MET,code,true,"achieved_finite_component_radii_accepted"};
    record_returned_radii(report,out);
    return report;
}
Report integrate_uniform_inner(acb_t out,const Bivariate &b,const acb_t inner_a,
    const acb_t inner_b,const acb_t outer_box,slong outer_order,
    const NestedPlan &plan,SharedBudget &budget) noexcept {
    acb_indeterminate(out);
    if (!valid_bivariate(b) || !valid_nested(plan) || !acb_is_finite(outer_box) ||
        (outer_order!=0 && outer_order!=1)) {
        budget.stop(Status::INVALID_CONTRACT,"uniform_joint_box_contract_missing");
        return {budget.stop_status,-1,false,budget.reason};
    }
    InnerContext context;
    context.bivariate=&b;
    context.outer_order=outer_order;
    acb_set(context.outer_box.value, outer_box); // whole parameter box including both radii
    const Limits &selected=(outer_order==1 || !radius_ok(outer_box,plan.tight_parameter_radius_exp))
        ? plan.uniform_inner : plan.point_inner;
    if (outer_order==1) {
        // Refuse an invalid OUTER analytic trial before an inner adaptive loop.
        // This is a full real-inner-path range query with the whole outer box.
        if (!exact_real_endpoints(inner_a,inner_b)) {
            budget.stop(Status::INVALID_CONTRACT,"nonexact_inner_endpoints");
            return {budget.stop_status,-1,false,budget.reason};
        }
        Ball inner_path,trial;
        acb_union(inner_path.value,inner_a,inner_b,selected.precision);
        Counted preflight{inner_callback,&context,&selected,&budget,true};
        counted_callback(trial.value,inner_path.value,&preflight,1,selected.precision);
        if (budget.stopped) return {budget.stop_status,-1,false,budget.reason};
        if (!acb_is_finite(trial.value))
            return {Status::NONFINITE_CALLBACK,-1,false,"outer_analytic_trial_domain_refusal"};
    }
    // Even at an exact inner node, a nonexact outer parameter remains a
    // whole-box request. A conservative refusal may be refined by the OUTER
    // integrator; shared inner/outer resource exhaustion is never cleared.
    return integrate_1d(out,inner_callback,&context,inner_a,inner_b,selected,budget,
                        outer_order==1 || !acb_is_exact(outer_box));
}
Report integrate_nested_2d(acb_t out,const Bivariate &b,const acb_t inner_a,
    const acb_t inner_b,const acb_t outer_a,const acb_t outer_b,
    const NestedPlan &plan,SharedBudget &budget) noexcept {
    acb_indeterminate(out);
    if (!valid_bivariate(b) || !valid_nested(plan) || !exact_real_endpoints(inner_a,inner_b)) {
        budget.stop(Status::INVALID_CONTRACT,"nested_contract_missing");
        return {budget.stop_status,-1,false,budget.reason};
    }
    OuterContext context{&b,inner_a,inner_b,&plan,&budget};
    return integrate_1d(out,outer_callback,&context,outer_a,outer_b,plan.outer,budget);
}
int field_bivariate(acb_ptr out,const acb_t inner,const acb_t outer_box,
                    void *opaque,slong analytic_order,slong prec) {
    if (!opaque) { invalidate(out,analytic_order); return 0; }
    auto slice=*static_cast<wu088::Slice *>(opaque);
    slice.outer_box = outer_box;
    return wu088::slice_callback(out,inner,&slice,analytic_order,prec);
}
const char *status_name(Status s) noexcept {
    switch(s) {
    case Status::RADIUS_MET: return "RADIUS_MET";
    case Status::INVALID_CONTRACT: return "INVALID_CONTRACT";
    case Status::RESOURCE_LIMIT: return "RESOURCE_LIMIT";
    case Status::NONFINITE_CALLBACK: return "NONFINITE_CALLBACK";
    case Status::INTEGRATOR_NO_CONVERGENCE: return "INTEGRATOR_NO_CONVERGENCE";
    case Status::RADIUS_TOO_WIDE: return "RADIUS_TOO_WIDE";
    }
    return "UNKNOWN";
}
}
