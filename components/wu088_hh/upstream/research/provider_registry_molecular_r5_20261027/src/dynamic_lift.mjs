// Exact finite-model comparison certificates. No physical rate is inferred.
export const R5 = (() => {
  const fail = m => { throw new Error(m); };
  const gcd = (a,b) => { a=a<0n?-a:a; b=b<0n?-b:b; while(b){ const t=a%b; a=b;b=t; } return a; };
  class Rat {
    constructor(n,d=1n){ if(typeof n!=="bigint"||typeof d!=="bigint"||d===0n)fail("RATIONAL_DOMAIN"); if(d<0n){n=-n;d=-d;} const g=gcd(n,d); this.n=n/g;this.d=d/g;Object.freeze(this); }
    static of(v){
      if(v instanceof Rat)return v;
      if(typeof v==="bigint")return new Rat(v);
      if(typeof v!=="string")fail("EXACT_STRING_REQUIRED");
      if(/^[+-]?\d+$/.test(v))return new Rat(BigInt(v));
      if(/^[+-]?\d+\/[+-]?\d+$/.test(v)){const [n,d]=v.split("/");return new Rat(BigInt(n),BigInt(d));}
      if(v.length>2048)fail("DECIMAL_LITERAL_SIZE");
      const m=/^([+-]?)(\d+)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(v);if(!m)fail("INVALID_RATIONAL_LITERAL");
      const ex=Number(m[4]||0)-(m[3]||"").length;if(!Number.isSafeInteger(ex)||Math.abs(ex)>1024)fail("EXPONENT_LIMIT");
      let n=BigInt(m[2]+(m[3]||""));if(m[1]==="-")n=-n;
      return ex>=0?new Rat(n*10n**BigInt(ex)):new Rat(n,10n**BigInt(-ex));
    }
    add(v){v=Rat.of(v);return new Rat(this.n*v.d+v.n*this.d,this.d*v.d);}
    sub(v){return this.add(Rat.of(v).neg());}
    mul(v){v=Rat.of(v);return new Rat(this.n*v.n,this.d*v.d);}
    div(v){v=Rat.of(v);if(v.n===0n)fail("DIVISION_BY_ZERO");return new Rat(this.n*v.d,this.d*v.n);}
    neg(){return new Rat(-this.n,this.d);}
    abs(){return this.n<0n?this.neg():this;}
    cmp(v){v=Rat.of(v);const q=this.n*v.d-v.n*this.d;return q<0n?-1:q>0n?1:0;}
    eq(v){return this.cmp(v)===0;}
    toString(){return this.d===1n?String(this.n):this.n+"/"+this.d;}
    toJSON(){return this.toString();}
    approximate(){if(!this.n)return 0;const a=(this.n<0n?-this.n:this.n).toString(),b=this.d.toString();const u=a.slice(0,16),v=b.slice(0,16);return (this.n<0n?-1:1)*(Number(u)/Number(v))*10**(a.length-u.length-b.length+v.length);}
  }
  const R=Rat.of,Z=R("0"),O=R("1"),sum=a=>a.reduce((s,v)=>s.add(v),Z);
  const dot=(a,b)=>sum(a.map((v,i)=>v.mul(b[i])));
  const norm=a=>sum(a.map(v=>v.abs()));
  const minimum=a=>a.reduce((p,v)=>p.cmp(v)<=0?p:v);
  const maximum=a=>a.reduce((p,v)=>p.cmp(v)>=0?p:v);
  const nonnegative=(v,name)=>{v=R(v);if(v.cmp(Z)<0)fail("NEGATIVE_"+name);return v;};
  const vec=(a,n,name,positive=false)=>{if(!Array.isArray(a)||a.length!==n)fail("DIMENSION_"+name);return a.map(v=>positive?nonnegative(v,name):R(v));};
  const mv=(A,x)=>A.map(row=>dot(row,x));
  function validateGenerator(A){
    if(!Array.isArray(A)||A.length<1||A.length>9)fail("STATE_COUNT_1_TO_9");
    const n=A.length,K=A.map(row=>vec(row,n,"GENERATOR"));
    for(let j=0;j<n;j++){if(!sum(K.map(row=>row[j])).eq(Z))fail("COLUMN_SUM");for(let i=0;i<n;i++)if(i!==j&&K[i][j].cmp(Z)<0)fail("OFFDIAGONAL_SIGN");}
    return K;
  }
  function contractionRate(A){
    const K=validateGenerator(A),n=K.length;if(n===1)return Z;
    const values=[];
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
      let a=K[i][j].add(K[j][i]);
      for(let k=0;k<n;k++)if(k!==i&&k!==j)a=a.add(minimum([K[k][i],K[k][j]]));
      values.push(a);
    }
    return minimum(values);
  }
  function coefficients(input){
    if(input.scope!=="DECLARED_FINITE_MODEL")fail("SCOPE_REQUIRED");
    const K=validateGenerator(input.K),n=K.length,pi=vec(input.pi,n,"PI",true),d=vec(input.d,n,"D",true);
    const f=vec(input.f,n,"F",true),h=nonnegative(input.h,"H"),piDot=vec(input.piDot||Array(n).fill("0"),n,"PI_DOT");
    if(!sum(pi).eq(O))fail("PI_SUM");if(!sum(piDot).eq(Z))fail("PI_DOT_SUM");
    const dbar=dot(d,pi),betaVector=pi.map((p,i)=>p.mul(d[i].sub(dbar)));
    const B=pi.map((p,i)=>d.map((v,j)=>p.mul(v).sub(i===j?d[i]:Z)));
    const L=K.map((row,i)=>row.map((v,j)=>v.add(h.mul(B[i][j]))));
    const c=mv(K,pi).map((v,i)=>v.sub(piDot[i]).sub(h.mul(betaVector[i])));
    const F=sum(f),Qf=f.map((v,i)=>v.sub(pi[i].mul(F))),omega=maximum(d).sub(minimum(d)).div("2");
    return {scope:input.scope,n,K,pi,d,f,h,piDot,B,L,c,Qf,dbar,beta:norm(betaVector),omega,
      k:h.mul(minimum(d)),a:contractionRate(L),q:norm(c),g:norm(Qf),b0:h.mul(dbar),s:h.mul(omega),F,
      physical_source_binding:false,units:"K,a,k,b0:s^-1; h:cm^-3; d:cm^3/s; f:cm^-3/s"};
  }
  function initialBounds(x,c,Xbar=null){
    x=vec(x,c.n,"X",true);const X=sum(x),r=x.map((v,i)=>v.sub(c.pi[i].mul(X)));
    return {M:X,U:norm(r),E:Xbar===null?Z:X.sub(nonnegative(Xbar,"XBAR")).abs()};
  }
  function projectedState(x,c){
    x=vec(x,c.n,"X",true);const X=sum(x),r=x.map((v,i)=>v.sub(c.pi[i].mul(X)));
    const dx=mv(c.K,x).map((v,i)=>v.sub(c.h.mul(c.d[i]).mul(x[i])).add(c.f[i]));
    const dX=sum(dx),dr=dx.map((v,i)=>v.sub(c.pi[i].mul(dX)).sub(c.piDot[i].mul(X)));
    const projected=mv(c.L,r).map((v,i)=>v.add(c.c[i].mul(X)).add(c.Qf[i]));
    const signedFlux=c.h.mul(dot(c.d,r)),fluxBound=c.s.mul(norm(r));
    return {X,r,dx,dX,dr,projected,signedFlux,fluxBound};
  }
  function envelopeStep(bound,c,dt){
    dt=nonnegative(dt,"DT");
    const M=nonnegative(bound.M,"M"),U=nonnegative(bound.U,"U"),E=nonnegative(bound.E,"E");
    const v={};for(const key of ["k","a","q","g","b0","s","F"])v[key]=nonnegative(c[key],key);
    const Mstar=M.add(v.F.mul(dt)),C=v.q.mul(Mstar).add(v.g),Ustar=U.add(C.mul(dt)),Estar=E.add(v.s.mul(Ustar).mul(dt));
    const endpoint={M:M.div(O.add(v.k.mul(dt))).add(v.F.mul(dt)),U:U.div(O.add(v.a.mul(dt))).add(C.mul(dt)),E:E.div(O.add(v.b0.mul(dt))).add(v.s.mul(Ustar).mul(dt))};
    return {endpoint,interval:{M:Mstar,U:Ustar,E:Estar},scheme:"RATIONAL_UPPER_ENCLOSURE_CONSTANT_COEFFICIENT_INTERVAL"};
  }
  function envelope(bound,c,duration,steps){
    if(!Number.isSafeInteger(steps)||steps<1||steps>256)fail("STEPS_1_TO_256");
    const dt=nonnegative(duration,"DURATION").div(BigInt(steps));let value=bound;
    for(let i=0;i<steps;i++)value=envelopeStep(value,c,dt).endpoint;
    return value;
  }
  function generatorFromEdges(n,edges,scope){
    if(scope!=="SUPPLIED_EDGES_ONLY")fail("EDGE_SCOPE_REQUIRED");if(!Number.isSafeInteger(n)||n<1||n>9)fail("STATE_COUNT_1_TO_9");
    if(!Array.isArray(edges))fail("EDGE_ARRAY");
    const K=Array.from({length:n},()=>Array(n).fill(Z)),seen=new Set();
    for(const e of edges){const {from,to}=e;if(!Number.isSafeInteger(from)||!Number.isSafeInteger(to)||from<0||to<0||from>=n||to>=n||from===to)fail("EDGE_INDEX");
      const key=from+":"+to;if(seen.has(key))fail("DUPLICATE_EDGE");seen.add(key);const rate=nonnegative(e.rate,"RATE");K[to][from]=K[to][from].add(rate);K[from][from]=K[from][from].sub(rate);}
    return validateGenerator(K);
  }
  return {Rat,R,sum,dot,norm,mv,contractionRate,coefficients,initialBounds,projectedState,envelopeStep,envelope,generatorFromEdges};
})();
