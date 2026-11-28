        wu088::Rational margin=l_t;
        if (fmpq_cmp(l_u.value,margin.value)<0) margin=l_u;
        // On the closed real rectangle, sigma is decreasing in each variable:
        // sigma >= (1/(a+T_t)+1/(b+T_u))/2 > 0. The former guard based only
        // on lower endpoints rejected valid large real t,u regardless of precision.
        // This does not admit any complex box: unchanged callback guards still
        // test the whole computed balls before principal powers/special functions.
        wu088::Rational denominator_a,denominator_b,inverse_a,inverse_b,sigma_min;
        fmpq_add(denominator_a.value,parameters.a.value,T_t.value);
        fmpq_add(denominator_b.value,parameters.b.value,T_u.value);
        fmpq_inv(inverse_a.value,denominator_a.value);
        fmpq_inv(inverse_b.value,denominator_b.value);
        fmpq_add(sigma_min.value,inverse_a.value,inverse_b.value);
        fmpq_div_2exp(sigma_min.value,sigma_min.value,1);
        if (fmpq_cmp(sigma_min.value,margin.value)<0) margin=sigma_min;
        fmpq_div_2exp(margin.value,margin.value,20);
        if (fmpq_cmp(margin.value,contract.margin.value)<0) contract.margin=margin;
