"use strict";
/*
HE33 homogeneous nonrelativistic LRS pressure tensor.
SI API: pressures Pa = J/m^3; H,s,nu s^-1; dt seconds.
No chemistry, heat injection, species rate calibration, or metric feedback.
nu is the pressure-anisotropy relaxation rate (not automatically a collision frequency).
*/
function finite(name, x) {
  if (typeof x !== "number" || !Number.isFinite(x)) throw new TypeError(name + " must be finite");
  return x;
}
function nonnegative(name, x) {
  finite(name,x);
  if (x < 0) throw new RangeError(name + " must be nonnegative");
  return x;
}
function state(P) {
  if (!Array.isArray(P) || P.length !== 2) throw new TypeError("P must be [Pperp,Pparallel]");
  return [nonnegative("Pperp",P[0]),nonnegative("Pparallel",P[1])];
}
function invariants(P) {
  const [x,y]=state(P);
  const q=(y-x)/3, p=x+q;
  if (![p,1.5*p,Math.sqrt(6)*Math.abs(q)].every(Number.isFinite)) throw new RangeError("pressure invariant overflow");
  return {p,q,e:1.5*p,piF:Math.sqrt(6)*Math.abs(q),anisotropy:p===0?null:q/p};
}
function rhs(P,H,s,nu) {
  const [x,y]=state(P);
  finite("H",H); finite("s",s); nonnegative("nu",nu);
  const diff=y-x;
  const out=[(-5*H+2*s)*x+(nu/3)*diff,(-5*H-4*s)*y-(2*nu/3)*diff];
  if (!out.every(Number.isFinite)) throw new RangeError("RHS overflow");
  return out;
}
function positiveLogSum(logTerms) {
  const top=Math.max(...logTerms);
  if(top===-Infinity)return 0;
  if(!Number.isFinite(top))throw new RangeError("invalid log pressure");
  const sum=logTerms.reduce((acc,t)=>acc+Math.exp(t-top),0);
  const value=Math.exp(top+Math.log(sum));
  if(!Number.isFinite(value))throw new RangeError("pressure overflow");
  if(value===0)throw new RangeError("positive pressure below binary64 range");
  return value;
}
function step(P,H,s,nu,dt) {
  const [x,y]=state(P);
  finite("H",H);finite("s",s);nonnegative("nu",nu);nonnegative("dt",dt);
  if(dt===0 || (x===0 && y===0)) return [x,y];
  const h=H*dt, u=s*dt, v=nu*dt;
  if (![h,u,v,5*h,3*u+v/6].every(Number.isFinite)) throw new RangeError("scaled coefficients overflow");
  const d=3*u+v/6, delta=Math.hypot(d,Math.SQRT2*(v/3));
  if (!Number.isFinite(delta)) throw new RangeError("spectral gap overflow");
  const lx=x===0?-Infinity:Math.log(x),ly=y===0?-Infinity:Math.log(y);
  if(delta===0) return [positiveLogSum([lx-5*h]),positiveLogSum([ly-5*h])];
  const den=delta+u+v/2;
  const slow=8*(u/den)*u;
  const lp=-5*h+slow, lm=-5*h-(v+2*u)-slow;
  if(![den,lp,lm].every(Number.isFinite))throw new RangeError("spectral exponent overflow");
  const ratio=Math.abs(d)/delta;
  if(ratio>1)throw new RangeError("invalid spectral projector");
  // Small projector is bc/[2 delta (delta+abs(d))].
  // Keep it in log space: neither 1-ratio cancellation nor coefficient underflow.
  const logSmall=v===0?-Infinity:
    Math.log(0.5)+2*(Math.log(Math.SQRT2/3)+Math.log(v)-Math.log(delta))-Math.log1p(ratio);
  const logLarge=Math.log1p(-Math.exp(logSmall));
  const logPlus=d>=0?logLarge:logSmall,logMinus=d>=0?logSmall:logLarge;
  const logGap=Math.log(-Math.expm1(-2*delta));
  const logOff=v===0?-Infinity:Math.log(v)-Math.log(6)-Math.log(delta)+logGap;
  // Sum positive spectral contributions BEFORE the only final exponential.
  // Discarding terms below exp-range relative to the largest log term is harmless
  // at binary64 precision; physically nonzero final component underflow is explicit.
  return [
    positiveLogSum([lx+logPlus+lp,lx+logMinus+lm,ly+logOff+lp]),
    positiveLogSum([ly+logMinus+lp,ly+logPlus+lm,lx+Math.log(2)+logOff+lp])
  ];
}
function advance(P,t0,t1,n,coefficients) {
  state(P);finite("t0",t0);finite("t1",t1);
  if(t1<t0)throw new RangeError("backward time unsupported");
  if(!Number.isSafeInteger(n)||n<1)throw new RangeError("n must be positive safe integer");
  if(typeof coefficients!=="function")throw new TypeError("coefficients must be a function");
  if(t1===t0)return state(P);
  const dt=(t1-t0)/n;
  if(!Number.isFinite(dt)||dt===0)throw new RangeError("time step not representable");
  let out=state(P);
  for(let i=0;i<n;i++) {
    const mid=t0+(i+0.5)*dt;
    const c=coefficients(mid);
    if(!c||typeof c!=="object")throw new TypeError("coefficient sample missing");
    out=step(out,c.H,c.s,c.nu,dt);
  }
  return out;
}
function thermalLedger(P,H,s,T,Rpart,dTdt=0) {
  const {p,q}=invariants(P);
  finite("H",H);finite("s",s);nonnegative("T",T);finite("Rpart",Rpart);finite("dTdt",dTdt);
  if(T===0)throw new RangeError("T must be positive for an ideal-gas particle census");
  const kB=1.380649e-23;
  const npart=p/(kB*T);
  const parts={expansion:3*H*p,shear:6*s*q,particleCreation:1.5*kB*T*Rpart,temperature:1.5*kB*npart*dTdt};
  const Q=Object.values(parts).reduce((a,b)=>a+b,0);
  if(!Number.isFinite(Q))throw new RangeError("thermal ledger overflow");
  return {Q,parts,npart};
}
const HE33={invariants,rhs,step,advance,thermalLedger};
if(typeof module!=="undefined" && module.exports)module.exports=HE33;
