# R4: finite constructions and discriminating examples

Date: 2026-10-28 KST. New unit 4/20; original DAG working 33/88, central 28/88, delta 0. Status: COMPLETE_CONSTRUCTIVE_EXPLORATION. The examples below are direct hand algebra, not newly executed numerical tests.

## Three compatible constructions

A. Event reconstruction: D=Na+deltaN, E=c_v Na Ta+Q+W, T_hat=E/(c_v D), on D,E>0. This consumes integrated count and gas-energy ports. It does not assert that the saved endpoint has zero residual.

B. Saved endpoint: T_b=Ub/(c_v Nb), on Ub,Nb>0, with r0=Ua-c_v Na Ta, r_bal=Ub-Ua-Q-W and rN=Nb-D preserved. This trusts the supplied endpoint as an input representation, not as a certified physical solution. A and B are compared, not averaged or forced equal.

C. Conditional enclosure: supplied positive energy/count intervals, or a monotone general EOS with a verified bracket, give a set of temperatures. A missing physical uncertainty input produces an unresolved physical enclosure, not a singleton interval.

Selection: develop A and B together with their exact difference and tangent; add C only when its stated inputs are available. Do not solve a new history, reconstruct a spectrum, or import an unrelated density. A polytope alternative is retained as a mathematical improvement for correlated affine inputs; no polytope solver is required by the current implementation design.

## Heat does not alone determine the temperature sign

Let N_star and T_star be positive dimensioned scales. Keep c_v explicit.

Example H: Na=N_star, Ta=T_star, deltaN=N_star, Q=c_v N_star T_star/2, W=0. Then E=3 c_v N_star T_star/2, D=2 N_star and T_hat=3 T_star/4. Positive energy transfer accompanies a temperature decrease because the thermal count doubles.

Example C: Na=2 N_star, Ta=T_star, deltaN=-N_star, Q=-c_v N_star T_star/4, W=0. Then E=7 c_v N_star T_star/4, D=N_star and T_hat=7 T_star/4. Energy removal accompanies a temperature increase. Both examples stay in E,D>0 and compare different events, not the physical BASS source.

The exact sign discriminator is Q+W-c_v Ta deltaN. A heat-only formula would fail these examples. These statements are identities in the conditional caloric model, not claims that arbitrary count changes can be produced by a particular atomic channel.

## Correlated uncertainty alternative

For z in a compact polytope with vertices v_i, let E(z) and D(z)>0 be affine, with fixed c_v>0. If z=sum(lambda_i v_i), then

T(z)=sum(w_i T(v_i)), where w_i=lambda_i D(v_i)/sum_j(lambda_j D(v_j)).

The weights are nonnegative and sum to one. Thus the minimum and maximum occur at vertices. This respects shared uncertainty instead of combining unattainable marginal extremes. It is a statement about the specified polytope, not all physical states; nonlinear E or D and uncertain c_v need another analysis.

## Concrete failure signatures

- Treating hidden atomic storage or a retained photon as Q changes the single gas-energy ownership.
- Applying W and then multiplying the temperature by an additional adiabatic factor counts the same work twice.
- Replacing sum(deltaFine) by zero suppresses the saved stock residual.
- Adding r0 to the aggregate Ub-E a second time gives the wrong stored/event difference.
- Combining local-V1 increments directly with local-V0 increments fails extensive-count/energy conservation unless V1=V0.
- Zero or negative D,E is a domain failure, not a reason to clip the temperature.
- An empty physical radius field cannot establish a zero-error endpoint.

These signatures determine the exact algebraic controls in C1-C4. Independent verification and executable tests are not performed at R4. Source pins, old evidence, original DAG and resource holds are unchanged.
