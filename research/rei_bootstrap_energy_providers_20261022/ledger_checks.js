function runChecks() {
  "use strict";
  const kB = 1.380649e-23, tolerance = 1e-13;
  let comparisons = 0;
  const maxResiduals = { contraction: 0, thermalChainRule: 0, eventLedger: 0, photonBoundary: 0 };
  const claims = [];
  function check(group, actual, expected, scale = 1) {
    const residual = Math.abs(actual - expected) / Math.max(scale, Math.abs(actual), Math.abs(expected));
    comparisons++;
    maxResiduals[group] = Math.max(maxResiduals[group], residual);
    if (!Number.isFinite(residual) || residual > tolerance) throw Error(group + ": " + residual);
  }
  function contraction(s, p) {
    return [-s, -s, 2*s].reduce((sum, value, i) => sum + value * [-p, -p, 2*p][i], 0);
  }
  const stressCases = [[0.17, 2.3], [-0.8, 0.6], [1.9, -2.7], [0, 4]];
  for (const [i, species] of ["gas", "massive", "radiation"].entries()) {
    for (const [s, p] of stressCases) check("contraction", contraction(s, p), 6*s*p);
    claims.push({ id: "C" + (i+1), scope: species + " LRS contraction arithmetic" });
  }
  const thermalCases = [
    [2.5e6, 6500, 1.5e-5, 100, 2.1e9, 1.7e-5, 9e8],
    [7.2, 13, -0.03, -0.4, -8.1, -0.2, 4.2],
    [91, 2.7, 0.08, 1.3, -3.6, 0.12, -7.4],
    [3.1e10, 4e5, -2e-7, 0, 0, 0, 0]
  ];
  for (const [n, T, H, S, QoverKB, s, poverKB] of thermalCases) {
    const u = 1.5*n*kB*T, Q = kB*QoverKB;
    const sigmaPiGas = contraction(s, kB*poverKB);
    const ndot = -3*H*n + S, udot = -5*H*u + Q - sigmaPiGas;
    const direct = udot/(1.5*kB*n) - T*ndot/n;
    const formula = -2*H*T - T*S/n + 2*(Q-sigmaPiGas)/(3*kB*n);
    check("thermalChainRule", direct, formula);
  }
  claims.push({ id: "C4", scope: "gas temperature chain rule with particle source" });
  const eventCases = [[17, 13.6, 2.5], [80, 24.6, 0.07], [13.6, 13.6, 9]];
  for (const [E, chi, R] of eventCases) {
    const ledger = [(E-chi)*R, chi*R, -E*R];
    check("eventLedger", ledger.reduce((a,b) => a+b, 0), 0, Math.max(...ledger.map(Math.abs)));
  }
  claims.push({ id: "C5", scope: "photoionization event energy closure" });
  for (const [Ekin, chi, R] of [[0.5, 13.6, 2.5], [8, 24.6, 0.07], [0, 13.6, 9]]) {
    const ledger = [-Ekin*R, -chi*R, (Ekin+chi)*R];
    check("eventLedger", ledger.reduce((a,b) => a+b, 0), 0, Math.max(...ledger.map(Math.abs)));
  }
  claims.push({ id: "C6", scope: "radiative recombination event energy closure" });
  for (const [i, p] of [-1, 0, 1].entries()) {
    for (const [A, H, lo, hi] of [[2.3, 0.17, 0.4, 7.2], [0.031, 1.2, 1.1, 3.6]]) {
      const U = A*(hi**(p+2)-lo**(p+2))/(p+2);
      const Udot = (p-2)*H*U;
      const boundary = H*A*(hi**(p+2)-lo**(p+2));
      check("photonBoundary", Udot+4*H*U, boundary);
    }
    claims.push({ id: "C" + (i+7), scope: "fixed-bin photon energy boundary identity, p=" + p });
  }
  check("eventLedger", (17-13.6)*2.5+13.6*2.5-17*2.5-0.5*2.5-13.6*2.5+(0.5+13.6)*2.5, 0, 100);
  claims.push({ id: "C10", scope: "combined manufactured PI and RR energy closure" });
  return {
    status: "CHECKED_MANUFACTURED_ALGEBRA",
    runtime: "functions.exec V8; no Node or Python",
    tolerance: { mixedRelative: tolerance, residual: "abs(a-b)/max(scale,abs(a),abs(b)); default scale=1" },
    comparisons, maxResiduals, claims, old83Reruns: 0, physicalIVPs: 0,
    limitations: ["Pure ledger arithmetic only", "No provider or general quadrature validation",
      "Complete cascade and no recoil assumed; no spectral emission claim", "No independent science review"]
  };
}
