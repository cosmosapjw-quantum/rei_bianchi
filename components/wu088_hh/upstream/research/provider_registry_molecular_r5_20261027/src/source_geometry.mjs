export function runSourceGeometry(R5,input) {
 const {R,sum,mv,generatorFromEdges,contractionRate}=R5;
 const expected="0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb";
 if(input.source_sha256!==expected||input.temperature_K!=="100"||input.collider_id!==2)throw Error("PINNED_SOURCE_SLICE_REQUIRED");
 const n=9;if(input.energies_cm_inverse.length!==n||input.weights.length!==n||input.downward.length!==9)throw Error("PINNED_SHAPE");
 let assertions=0;const ok=(b,m)=>{assertions++;if(!b)throw Error(m);};
 // Same exact SI constants as the pinned REC adapter; exponentials are a display-precision ensemble choice.
 const c2=6.62607015e-34*299792458*100/1.380649e-23;
 const weight_literals=input.energies_cm_inverse.map((e,i)=>(Number(input.weights[i])*Math.exp(-c2*Number(e)/100)).toExponential(16));
 const weight=weight_literals.map(R),total=sum(weight),pi=weight.map(w=>w.div(total)),edges=[];
 for(const e of input.downward){
  const down=R(e.rate_cm3_s).div(input.kappa_ref_cm3_s);
  edges.push({from:e.from,to:e.to,rate:down});
  edges.push({from:e.to,to:e.from,rate:down.mul(pi[e.from]).div(pi[e.to])});
 }
 const K=generatorFromEdges(n,edges,"SUPPLIED_EDGES_ONLY");
 const exits=K.map((row,i)=>row[i].neg()),maxExit=exits.reduce((a,b)=>a.cmp(b)>0?a:b),lambda=maxExit.mul("2");
 const P=K.map((row,i)=>row.map((v,j)=>v.div(lambda).add(i===j?"1":"0")));
 const stationary=mv(K,pi);
 ok(sum(pi).eq("1"),"pi_sum");
 for(let j=0;j<n;j++){ok(sum(K.map(r=>r[j])).eq("0"),"K_col");ok(stationary[j].eq("0"),"Kpi");ok(P[j][j].cmp("1/2")>=0,"laziness");}
 const instant=contractionRate(K);ok(instant.eq("0"),"sparse_instant_overlap");
 const power=(x,k)=>{let p=R("1");for(let i=0;i<k;i++)p=p.mul(x);return p;};
 const paths=[];
 for(let j=0;j<n;j++){
  let lower=power(P[0][0],8-j);
  for(let k=j;k>=1;k--)lower=lower.mul(P[k-1][k]);
  ok(lower.cmp("0")>0,"positive_explicit_path");paths.push(lower);
 }
 const eta=paths.reduce((a,b)=>a.cmp(b)<0?a:b),poissonWeightLower=R(String(8**8)).div(String(3**8*40320)),rho=R("1").sub(eta.mul(poissonWeightLower)),blockTime=R("8").div(lambda);
 ok(eta.cmp("1")<=0,"minorization_domain");ok(rho.cmp("0")>0&&rho.cmp("1")<0,"strict_block_contraction");ok(blockTime.cmp("0")>0,"positive_block_time");
 return {schema:"WU_R5_HD_SUPPLIED_GRAPH_V1",status:"PASS",assertions,scope:"conditional rational supplied-edge model, not complete physical collision graph",source:input,
 ensemble:{kind:"normalized exact rationals from17-significant-digit binary64 Boltzmann weights",weight_literals,pi,thermal_roundoff_enclosure:false,constants:"exactSIvalues reused from REC; Math.exp representation only"},
 clock:{tau:"n_collider*kappa_ref*t",collider_density:"not physically bound",kappa_ref_cm3_s:input.kappa_ref_cm3_s},
 K_scaled:K,P,lambda,instant_L1_contraction:instant,common_row:0,steps:8,path_lower_bounds:paths,eta,poissonWeightLower,rho_upper:rho,block_time_tau:blockTime,
 display:{lambda:lambda.approximate(),eta:eta.approximate(),rho:rho.approximate(),block_time_tau:blockTime.approximate(),one_minus_rho:R("1").sub(rho).approximate()},
 claims:{column_conservation:true,stationary_for_declared_rational_pi:true,finite_block_contraction:true,physical_generator:false,physical_destruction:false,physical_relaxation_time:false,physical_consumer:false},
 old54_DB_tests_replayed:0,physical_IVP_runs:0};
}
