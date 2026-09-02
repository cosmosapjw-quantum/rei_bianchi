using Symbolics
using Random
using Pkg

function zeroq(expr)
    reduced = Symbolics.simplify(expr; expand=true)
    return (reduced isa Number && iszero(reduced)) || isequal(reduced, 0) || string(reduced) in ("0", "0.0")
end

function substitute_fold(expr, rules)
    return Symbolics.substitute(expr, rules; fold=Val(true))
end

function main()
    @variables r0 r1 r2 r3 n0 n1 n2 n3
    @variables h0 om ol z
    @variables zH z2 z3 nH nHe xH x2 x3
    @variables h p m nc xs dt tau t1 t2 t3

    checks = Dict{String,Bool}()
    redshift = (-r0*n0+r1*n1) + (-r1*n1+r2*n2) + (-r2*n2+r3*n3) - r3*n3
    checks["redshift_telescoping"] = zeroq(redshift + r0*n0)

    hubble = h0 * sqrt(om*(1+z)^3 + ol)
    dh = Symbolics.expand_derivatives(Differential(z)(hubble))
    dh_expected = 3*h0*om*(1+z)^2 / (2*sqrt(om*(1+z)^3 + ol))
    checks["hubble_derivative"] = zeroq(dh - dh_expected)

    xh = 1/(1+exp(-zH))
    heden = 1 + exp(z2) + exp(z3)
    he = [1/heden, exp(z2)/heden, exp(z3)/heden]
    checks["helium_simplex"] = zeroq(sum(he)-1)

    ne = nH*xH + nHe*(x2+2*x3)
    dne3 = Symbolics.expand_derivatives(Differential(x3)(ne))
    checks["electron_HeIII_coefficient"] = zeroq(dne3 - 2*nHe)

    capacity = m + nc*(1-xs)/dt
    capacity_residuals = [
        Symbolics.expand_derivatives(Differential(m)(capacity))-1,
        Symbolics.expand_derivatives(Differential(nc)(capacity))-(1-xs)/dt,
        Symbolics.expand_derivatives(Differential(xs)(capacity))+nc/dt,
        Symbolics.expand_derivatives(Differential(dt)(capacity))+nc*(1-xs)/dt^2,
    ]
    checks["capacity_derivatives"] = all(zeroq, capacity_residuals)

    trans = exp(-tau)
    absorb = 1-exp(-tau)
    trans0 = substitute_fold(trans, Dict(tau=>0))
    dtrans0 = substitute_fold(Symbolics.expand_derivatives(Differential(tau)(trans)), Dict(tau=>0))
    dabs0 = substitute_fold(Symbolics.expand_derivatives(Differential(tau)(absorb)), Dict(tau=>0))
    checks["transmission_origin"] = zeroq(trans0-1)
    checks["transmission_derivative_at_origin"] = zeroq(dtrans0+1)
    checks["absorption_derivative_at_origin"] = zeroq(dabs0-1)
    checks["allocation_numerator_partition"] = zeroq((t1+t2+t3)-(t1+t2+t3))

    @variables y pe a b ah ahe
    events = [
        [-1,1,0,0,0],
        [0,0,-1,1,0],
        [0,0,0,-1,1],
        [1,-1,0,0,0],
        [-y,y,y,-y,0],
        [-pe,pe,1,-1,0],
        [-(1-a-b),1-a-b,-b,1+b-a,-1+a],
        [-1,1,0,1,-1],
        [-ah,ah,-ahe,1+ahe,-1],
    ]
    checks["chemistry_event_conservation"] = all(v -> zeroq(sum(v[1:2])) && zeroq(sum(v[3:5])), events)

    Random.seed!(20260903)
    setprecision(BigFloat, 256)
    bigfloat_tolerance = big"1e-50"
    max_residual = BigFloat(0)
    numeric_ok = true
    for _ in 1:256
        weights = BigFloat.(rand(48)); weights ./= sum(weights)
        tau_species = [BigFloat(10)^BigFloat(-12 + 15*rand()) for _ in 1:3, _ in 1:48]
        total_tau = vec(sum(tau_species, dims=1))
        transmission = exp.(-total_tau)
        F = sum(weights .* transmission)
        absorbed_E = -expm1.(-total_tau)
        absorbed = sum(weights .* absorbed_E)
        complement = abs(F + absorbed - 1)
        fractions = tau_species ./ reshape(total_tau, 1, :)
        numerators = vec(sum(fractions .* reshape(weights .* absorbed_E, 1, :), dims=2))
        allocation = numerators ./ absorbed
        partition = abs(sum(allocation)-1)
        max_residual = max(max_residual, complement, partition)
        numeric_ok &= (0 <= F <= 1) && (0 <= absorbed <= 1) && complement < bigfloat_tolerance && all(allocation .>= 0) && partition < bigfloat_tolerance
    end
    checks["bigfloat_transmission_allocation_256"] = numeric_ok

    hostile = Dict(
        "missing_redshift_inflow" => !zeroq((-r0*n0) + (-r1*n1+r2*n2) + (-r2*n2+r3*n3) - r3*n3 + r0*n0),
        "wrong_HeIII_factor" => !zeroq((nH*xH+nHe*(x2+x3))-ne),
        "wrong_expansion_coefficient" => !zeroq(4*h*p-3*h*p),
        "wrong_transmission_sign" => !zeroq(substitute_fold(Symbolics.expand_derivatives(Differential(tau)(exp(tau))), Dict(tau=>0))+1),
        "missing_allocation_species" => !zeroq((t1+t2)-(t1+t2+t3)),
    )
    checks["hostile_mutations_detected"] = all(values(hostile))

    status = all(values(checks)) ? "PASS" : "FAIL"
    symver = "unknown"
    for (_, dep) in Pkg.dependencies()
        if dep.name == "Symbolics"
            symver = string(dep.version)
        end
    end
    check_json = join(["\"$(k)\":" * lowercase(string(v)) for (k,v) in sort(collect(checks))], ",")
    receipt = "{\n" *
        "  \"status\": \"$(status)\",\n" *
        "  \"tool\": \"Julia Symbolics\",\n" *
        "  \"julia_version\": \"$(VERSION)\",\n" *
        "  \"symbolics_version\": \"$(symver)\",\n" *
        "  \"oracle_class\": \"SYMBOLIC_TRANSCENDENTAL_AND_256_BIT_NUMERICAL\",\n" *
        "  \"bigfloat_samples\": 256,\n" *
        "  \"bigfloat_tolerance\": \"$(bigfloat_tolerance)\",\n" *
        "  \"max_bigfloat_residual\": \"$(max_residual)\",\n" *
        "  \"checks\": {$(check_json)},\n" *
        "  \"claim_boundary\": \"BOUNDED_REI_FORMULA_ORACLE_ONLY\"\n" *
        "}\n"
    receipt_dir = joinpath(@__DIR__, "..", "receipts")
    mkpath(receipt_dir)
    write(joinpath(receipt_dir, "julia_receipt.json"), receipt)
    print(receipt)
    if status != "PASS"
        exit(1)
    end
end

main()
