#ifndef WU088_PETRAS_HOST_HPP
#define WU088_PETRAS_HOST_HPP
#include <flint/acb.h>
#include <flint/acb_calc.h>
#include <chrono>
#include <cstddef>
#include "../validated_callback/callback.hpp"

// NATIVE DRAFT: pinned-header/static checks only. No compiled/runtime claim.
namespace wu088::petras {
struct Ball {
    acb_t value;
    Ball() { acb_init(value); }
    ~Ball() { acb_clear(value); }
    Ball(const Ball &)=delete;
    Ball &operator=(const Ball &)=delete;
};
struct Limits {
    slong precision=128;
    slong max_precision=512;
    slong relative_goal=64;
    slong absolute_tolerance_exp=-64;
    slong accepted_component_radius_exp=-48;
    slong per_call_eval_limit=2000;
    slong queued_panel_limit=64; // FLINT depth_limit means queued intervals!
    slong degree_limit=64;
};
struct GlobalLimits {
    std::size_t max_dispatched_evaluations=20000;
    std::size_t max_integration_calls=1024;
    unsigned max_nested_integrations=2;
    double cooperative_wall_seconds=10.0;
};
enum class Status {
    RADIUS_MET, INVALID_CONTRACT, RESOURCE_LIMIT, NONFINITE_CALLBACK,
    INTEGRATOR_NO_CONVERGENCE, RADIUS_TOO_WIDE
};
struct SharedBudget {
    GlobalLimits limits;
    std::chrono::steady_clock::time_point start=std::chrono::steady_clock::now();
    std::size_t callback_entries=0, dispatched_evaluations=0, integration_calls=0;
    std::size_t analytic_box_refusals=0;
    unsigned active_integrations=0, peak_active_integrations=0;
    bool stopped=false;
    Status stop_status=Status::INVALID_CONTRACT;
    const char *reason="not_stopped";
    explicit SharedBudget(GlobalLimits l={}) : limits(l) {}
    bool stop(Status,const char *) noexcept;
    bool wall_ok() noexcept;
};
struct Report {
    Status status=Status::INVALID_CONTRACT;
    int flint_status=-1;
    bool achieved_radius_accepted=false;
    const char *reason="uninitialized";
    std::string real_radius_dump;
    std::string imag_radius_dump;
    Report(Status s=Status::INVALID_CONTRACT,int f=-1,bool accepted=false,
           const char *why="uninitialized") : status(s),
           achieved_radius_accepted(accepted),reason(why) { flint_status=f; }
};
// Callback return code is reserved by FLINT; finite output balls are mandatory.
Report integrate_1d(acb_t out,acb_calc_func_t callback,void *param,
                    const acb_t a,const acb_t b,const Limits &,SharedBudget &,
                    bool speculative_parameter_trial=false) noexcept;

using BivariateCallback=int (*)(acb_ptr out,const acb_t inner,const acb_t outer,
                               void *param,slong analytic_order,slong prec);
struct Bivariate {
    BivariateCallback callback=nullptr;
    void *param=nullptr;
    bool uniform_whole_parameter_box=false;
    bool joint_holomorphy_proved=false;
    const char *proof_reference=nullptr;
};
struct NestedPlan {
    Limits outer;
    Limits point_inner;
    Limits uniform_inner;
    // Policy selector only; NOT a mathematical error or Lipschitz estimate.
    slong tight_parameter_radius_exp=-80;
    NestedPlan() {
        point_inner.accepted_component_radius_exp=-48;
        uniform_inner.absolute_tolerance_exp=20;
        uniform_inner.accepted_component_radius_exp=20;
    }
};
// Finite real exact endpoints. All values in outer_box pass unchanged to inner.
Report integrate_uniform_inner(acb_t out,const Bivariate &,const acb_t inner_a,
    const acb_t inner_b,const acb_t outer_box,slong outer_order,
    const NestedPlan &,SharedBudget &) noexcept;
Report integrate_nested_2d(acb_t out,const Bivariate &,const acb_t inner_a,
    const acb_t inner_b,const acb_t outer_a,const acb_t outer_b,
    const NestedPlan &,SharedBudget &) noexcept;
// Adapter to G4 Slice; caller owns Parameters/Term/Contract lifetime.
// A fresh stack Slice is made on each dispatch; the whole outer box is bound.
int field_bivariate(acb_ptr out,const acb_t inner,const acb_t outer_box,
                    void *slice_template,slong analytic_order,slong prec);
const char *status_name(Status) noexcept;
}
#endif
