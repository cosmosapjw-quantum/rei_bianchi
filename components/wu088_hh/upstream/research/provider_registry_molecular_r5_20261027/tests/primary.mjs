export function runPrimary(R5) {
 const {R,Rat,sum,dot,norm,mv,coefficients,initialBounds,projectedState,envelopeStep,envelope,generatorFromEdges,contractionRate}=R5;
 let assertions=0;const groups=[],cases=[],failure=[];
 const check=(b,m)=>{assertions++;if(!b){failure.push(m);throw Error("ASSERT:"+m);}};
 const eq=(a,b,m)=>check(R(a).eq(R(b)),m);
 const rejects=(f,m)=>{let got=false;try{f();}catch(e){got=true;}check(got,m);};
 const group=(name,f)=>{const before=assertions;f();groups.push({name,assertions:assertions-before,status:"PASS"});};
 const base={scope:"DECLARED_FINITE_MODEL",K:[["-1","2"],["1","-2"]],pi:["2/3","1/3"],d:["1","4"],h:"1",f:["0","0"]};
 const c=coefficients(base),x0=["2/3","1/3"],start=initialBounds(x0,c);
 group("literal arithmetic and domain",()=>{
  eq(R("0.125").add("3/8"),"1/2","decimal+fraction");eq(R("1e-11").mul("100000000000"),"1","small rate scaling");
  eq(R("-2/3").div("-4/9"),"3/2","sign division");eq(R("0"),"0","zero canonical");
  rejects(()=>R(0.1),"binary64 rejected");rejects(()=>R("NaN"),"NaN");rejects(()=>R("1/0"),"zero divisor");rejects(()=>R("1e2000"),"exponent");
 });
 group("hand-derived projection and coefficients",()=>{
  for(const [key,val]of Object.entries({k:"1",a:"6",q:"4/3",g:"0",b0:"2",s:"3/2",F:"0",dbar:"2",beta:"4/3"}))eq(c[key],val,key);
  const p=projectedState(x0,c);eq(p.dX,"-2","total derivative");eq(p.dx[0],"-2/3","dx0");eq(p.dx[1],"-4/3","dx1");eq(p.dr[0],"2/3","dr0");eq(p.dr[1],"-2/3","dr1");eq(p.projected[0],"2/3","projected0");eq(p.projected[1],"-2/3","projected1");
  eq(start.M,"1","M0");eq(start.U,"0","U0");eq(start.E,"0","E0");eq(contractionRate(c.B),"3","B contraction");
 });
 group("nonstationary and moving pi forcing",()=>{
  const a=coefficients({...base,pi:["1/2","1/2"],piDot:["1/10","-1/10"]});eq(a.c[0],"23/20","moving c0");eq(a.c[1],"-23/20","moving c1");eq(a.q,"23/10","moving q");
  const p=projectedState(["3/2","2/3"],a);for(let i=0;i<2;i++)eq(p.dr[i],p.projected[i],"moving exact projection");eq(sum(p.r),"0","zero sum residual");
 });
 group("unbalanced formation and exact constant limits",()=>{
  const a=coefficients({...base,f:["1","0"]});eq(a.g,"2/3","Qf retained");eq(a.F,"1","F retained");
  const balanced=coefficients({...base,f:["2","1"]});eq(balanced.g,"0","balanced formation");
  for(const override of [{h:"0"},{d:["5","5"]}]){const b=coefficients({...base,...override});const e=envelope(initialBounds(["3/5","2/5"],b),b,"2",16);eq(e.E,"0","exact aggregate limit");}
  const single=coefficients({scope:"DECLARED_FINITE_MODEL",K:[["0"]],pi:["1"],d:["7"],h:"3",f:["2"]});eq(single.q,"0","one-state q");eq(single.s,"0","one-state s");eq(envelope(initialBounds(["1"],single),single,"2",8).E,"0","one-state exact");
  const edge=coefficients({...base,pi:["1","0"]});check(edge.a.cmp("0")>=0,"zero pi allowed");
 });
 group("new 3- and 9-state semantic fixtures",()=>{
  for(const n of [3,9]){
   const weights=Array.from({length:n},(_,i)=>R(String(i+1))),total=sum(weights),pi=weights.map(w=>w.div(total));
   const edges=[];for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(i!==j)edges.push({from:j,to:i,rate:R(String(1+(i+j)%3)).div(pi[j])});
   const K=generatorFromEdges(n,edges,"SUPPLIED_EDGES_ONLY"),d=Array.from({length:n},(_,i)=>String(1+i%4)),f=Array.from({length:n},(_,i)=>i===0?"1/3":"0");
   const a=coefficients({scope:"DECLARED_FINITE_MODEL",K,pi,d,h:"2/5",f}),x=Array.from({length:n},(_,i)=>R(String(n-i)).div("7")),p=projectedState(x,a);
   for(let i=0;i<n;i++){eq(mv(K,pi)[i],"0","constructed Kpi");eq(sum(a.B.map(row=>row[i])),"0","B column");eq(p.dr[i],p.projected[i],"general projection");}
   eq(sum(a.c),"0","forcing zero sum");check(a.a.cmp(a.k)>=0,"killing minimum contraction");
   check(p.signedFlux.abs().cmp(p.fluxBound)<=0,"static bound transport");
   const shifted=coefficients({scope:"DECLARED_FINITE_MODEL",K,pi,d:d.map(v=>R(v).add("7/3")),h:"2/5",f});
   eq(shifted.a.sub(a.a),"14/15","common destruction shift");eq(shifted.q,a.q,"shift q invariance");eq(shifted.s,a.s,"shift oscillation");
  }
 });
 group("rational endpoint vs interval semantics",()=>{
  const z=envelopeStep(start,c,"0");for(const key of ["M","U","E"])eq(z.endpoint[key],start[key],"zero step");
  const e=envelopeStep(start,c,"1");eq(e.interval.M,"1","whole M");eq(e.endpoint.M,"1/2","endpoint M");check(e.interval.M.cmp(e.endpoint.M)>0,"different endpoint/interval");
  eq(e.endpoint.U,"4/3","U endpoint");eq(e.endpoint.E,"2","E endpoint");
  for(const dt of ["1/100","1","20"]){const p=envelopeStep(start,c,dt);for(const v of Object.values(p.endpoint))check(v.cmp("0")>=0,"positive any step");}
  rejects(()=>envelope(start,c,"1",0),"zero steps");rejects(()=>envelope(start,c,"1",257),"step cap");rejects(()=>envelopeStep(start,c,"-1"),"negative dt");
 });
 group("input contract guards",()=>{
  const bad=[
   {...base,scope:"PHYSICAL_ADMITTED"},
   {...base,K:[["-1","1"],["1","-2"]]},
   {...base,K:[["1","0"],["-1","0"]]},
   {...base,pi:["1","1"]},
   {...base,pi:["-1","2"]},
   {...base,d:["1"]},
   {...base,d:["1","-1"]},
   {...base,h:"-1"},
   {...base,f:["0","-1"]},
   {...base,piDot:["1","0"]}
  ];for(const b of bad)rejects(()=>coefficients(b),"bad input");
  rejects(()=>generatorFromEdges(2,[{from:0,to:1,rate:"1"},{from:0,to:1,rate:"2"}],"SUPPLIED_EDGES_ONLY"),"duplicate edge");
  rejects(()=>generatorFromEdges(2,[{from:0,to:0,rate:"1"}],"SUPPLIED_EDGES_ONLY"),"self edge");
  rejects(()=>generatorFromEdges(2,[],"COMPLETE_PHYSICS"),"graph scope");
 });
 const continuous=(t,formed)=>{
  const v=Math.sqrt(6),et=Math.exp(-4*t),C=Math.cosh(v*t),S=Math.sinh(v*t);
  if(!formed){const X=et*(C+2*S/v),z=et*2*S/(3*v);return{M:Math.exp(-t),U:4/15*(Math.exp(-t)-Math.exp(-6*t)),E:2/5*(Math.exp(-t)-1.25*Math.exp(-2*t)+.25*Math.exp(-6*t)),X,actualU:2*Math.abs(z),actualE:Math.abs(X-Math.exp(-2*t))};}
  // Independent solution x=xss+exp(A*t)(x0-xss), A=[[-2,2],[1,-6]].
  const xss=[.6,.1],v0=[2/3-.6,1/3-.1],Aplus4v=[2*v0[0]+2*v0[1],v0[0]-2*v0[1]];
  const x=xss.map((q,i)=>q+et*(C*v0[i]+S/v*Aplus4v[i])),X=x[0]+x[1],xb=.5+.5*Math.exp(-2*t);
  return{M:1,U:(1-Math.exp(-6*t))/3,E:.25-.375*Math.exp(-2*t)+.125*Math.exp(-6*t),X,actualU:Math.abs(x[0]-2*X/3)+Math.abs(x[1]-X/3),actualE:Math.abs(X-xb)};
 };
 group("closed-form continuous comparisons and rational refinement",()=>{
  for(const formed of [false,true]){
   const cc=coefficients({...base,f:formed?["1","0"]:["0","0"]}),initial=initialBounds(x0,cc),rows=[];
   for(const steps of [8,16,32,64,128,256]){
    const final=envelope(initial,cc,"1",steps),ref=continuous(1,formed),display=Object.fromEntries(Object.entries(final).map(([k,v])=>[k,v.approximate()]));
    for(const key of ["M","U","E"])check(display[key]+2e-13>=ref[key],"continuous comparison enclosed");
    check(ref.actualU<=ref.U+2e-13,"actual residual bound");check(ref.actualE<=ref.E+2e-13,"actual aggregate bound");
    rows.push({steps,exact:final,display,continuous_comparison:ref,excess_E:display.E-ref.E});
   }
   check(rows[5].excess_E<rows[0].excess_E,"refinement improves bound");
   const ratio=rows[4].excess_E/rows[5].excess_E;check(ratio>1.8&&ratio<2.3,"first-order observed ratio");
   cases.push({formation:formed?"unbalanced(1,0)":"zero",rows,last_refinement_ratio_E:ratio});
  }
 });
 return {schema:"WU_R5_PRIMARY_V1",status:"PASS",assertions,groups,cases,fixture_scope:"Exact declared dimensionless finite models; analytic floating displays have2e-13 comparison allowance",source_science_replay:0,physical_IVP_runs:0,process_exit_code:null,runtime:"functions.exec V8 BigInt; actual Node/Python/C++ process not used"};
}
