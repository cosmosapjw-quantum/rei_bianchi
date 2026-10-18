"""Only the focused frozen rate, solver and inventory acceptance checks."""
def validate(m,comparisons,diagnostics,summary):
    tests=[]
    def check(name,observed,limit):tests.append({'name':name,'observed':observed,'limit':limit,'passed':observed<=limit})
    for key,limit in [('nonfinite_or_nonpositive_alpha_count',0),('nonfinite_log_beta_count',0),('rate64_128_max_relative',1e-8),('tail60_80_max_relative',1e-12),('identity_max_relative',2e-8),('W_K_Q_max_relative',2e-8),('Decimal_formula_max_relative',1e-11),('independent_quad_max_relative',2e-8),('rate_midpoint_direct_max_relative',2e-5),('per_origin_sum_abs',2e-11),('Li_source_sum_normalized',2e-11),('ledger_max_relative',1e-12)]:check(key,m[key],limit)
    check('negative_population_violation',max(0,-m['population_min']),2e-11)
    for name,r in comparisons.items():check(name+'_absolute_charge_population_difference',r['max_absolute_per_origin'],5e-6)
    check('solver_failures',sum(not r['success'] for r in diagnostics),0)
    return {'passed':all(t['passed'] for t in tests),'checks':tests,'single_finite_validation_pass':True,'optional_expansion':'NONE'}
