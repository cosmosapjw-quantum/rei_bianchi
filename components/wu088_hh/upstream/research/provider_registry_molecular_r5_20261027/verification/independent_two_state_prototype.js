const sqrt6 = Math.sqrt(6);
const times = [0,0.05,0.2,0.5,1,2,4];
function check(t,withFormation) {
  const e4=Math.exp(-4*t), c=Math.cosh(sqrt6*t), s=Math.sinh(sqrt6*t);
  let X,z,Xbar,M,U,E;
  if (!withFormation) {
    X=e4*(c+2/sqrt6*s);
    z=e4*(2/(3*sqrt6))*s;
    Xbar=Math.exp(-2*t); M=Math.exp(-t);
    U=4/15*(Math.exp(-t)-Math.exp(-6*t));
    E=2/5*(Math.exp(-t)-1.25*Math.exp(-2*t)+0.25*Math.exp(-6*t));
  } else {
    X=0.7+e4*(0.3*c+0.2/sqrt6*s);
    z=2/15+e4*(-2/15*c+7/(15*sqrt6)*s);
    Xbar=0.5+0.5*Math.exp(-2*t); M=1;
    U=(1-Math.exp(-6*t))/3;
    E=0.25-0.375*Math.exp(-2*t)+0.125*Math.exp(-6*t);
  }
  const x=[2/3*X+z, X/3-z], u=2*Math.abs(z), err=Math.abs(X-Xbar);
  const checks = {
    nonnegative_state: x.every(v=>v>=-1e-14),
    total_upper_bound: X <= M+1e-14,
    defect_envelope: u <= U+1e-14,
    aggregate_envelope: err <= E+1e-14
  };
  return {t, X, r_l1:u, r_envelope:U, aggregate_error:err, aggregate_envelope:E, checks};
}
const rows=[false,true].flatMap(flag=>times.map(t=>({formation:flag? "[1,0]":"[0,0]",...check(t,flag)})));
const pass=rows.every(r=>Object.values(r.checks).every(Boolean));
const result={implementation:"JavaScript binary64 evaluation of independent analytic two-state solution and proven envelopes",physical_source_binding:false,checks:rows.length*4,all_pass:pass,parameters:{K:[[-1,2],[1,-2]],pi:[2/3,1/3],d:[1,4],h:1,X0:1,r0:[0,0],alpha_K:3,delta_B:3,lambda:2,beta:4/3,omega:1.5},rows};
store("r5_dynamic_bound_2state_analytic_check",result);text(result);
