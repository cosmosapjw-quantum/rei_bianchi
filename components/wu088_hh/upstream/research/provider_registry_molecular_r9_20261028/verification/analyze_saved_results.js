function analyzeSavedR9(primary, reference, baseline, saved){
 function q(s){const a=String(s).split("/");return[BigInt(a[0]),a.length===2?BigInt(a[1]):1n];}
 function number(s){const a=q(s);return Number(a[0])/Number(a[1]);}
 function compare(x,y){const a=q(x),b=q(y),d=a[0]*b[1]-b[0]*a[1];return d<0n?-1:d>0n?1:0;}
 function changePercent(old,now){const a=q(old),b=q(now);return a[0]===0n?null:100*Number(a[0]*b[1]-b[0]*a[1])/Number(a[0]*b[1]);}
 function compareArrays(now,old){
  const out={total:0,smaller:0,equal:0,larger:0,first_larger:[]};
  for(let n=0;n<old.length;n++)for(let k=0;k<2;k++){
   const c=compare(now[n][k],old[n][k]);out.total++;out[c<0?"smaller":c>0?"larger":"equal"]++;
   if(c>0&&out.first_larger.length<4)out.first_larger.push({cell_or_endpoint:n,component:k,produced:now[n][k],baseline:old[n][k]});
  }return out;
 }
 const groups={};
 for(const group of ["hd_cases","controls"]){
  groups[group]=primary[group].map((row,i)=>{
   const old=baseline[group][i].certificate;
   const ref=group==="hd_cases"?saved.hd_cases.find(x=>x.id==="HD:"+row.id):null;
   const last=ref?ref.R_E.at(-1):null;
   const final=row.capped.endpoints.at(-1),prior=old.endpoints.at(-1);
   const refs=reference[group].find(x=>x.id===row.id);
   return{id:row.id,cells:old.cells,D:number(row.raw.D),inverse_D:1/number(row.raw.D),
    final:{R8:prior.map(number),raw:row.raw.endpoints.at(-1).map(number),capped:final.map(number),
     R8_exact:prior,raw_exact:row.raw.endpoints.at(-1),capped_exact:final,
     capped_reduction_percent:prior.map((v,k)=>changePercent(v,final[k])),
     saved_sample:last,
     capped_to_saved_sample:last?last.map((v,k)=>v===0?null:number(final[k])/v):null},
    exact_comparison:{raw_whole:compareArrays(row.raw.whole_cells,old.whole_cells),capped_whole:compareArrays(row.capped.whole_cells,old.whole_cells),raw_endpoints:compareArrays(row.raw.endpoints,old.endpoints),capped_endpoints:compareArrays(row.capped.endpoints,old.endpoints)},
    reference_max_budget:Math.max(...refs.modes.map(x=>Number(x.max_propagated_rounding_budget)))};
  });
 }
 const residualChecks=reference.checks.filter(x=>x.evidence&&x.evidence.max_difference!==undefined);
 return{schema:"WU_R9_SAVED_RESULTS_ANALYSIS_V1",operation:"Read-only exact-rational comparison and approximate display of saved results; no solver, producer, ODE, or scientific replay",...groups,
  max_observed_positive_rounding_difference:Math.max(...residualChecks.map(x=>Number(x.evidence.max_difference))),
  min_observed_rounding_difference:Math.min(...residualChecks.map(x=>Number(x.evidence.min_difference))),
  max_propagated_rounding_budget:Math.max(...residualChecks.map(x=>Number(x.evidence.max_rounding_budget))),
  display_convention:"Decimals are approximate display values; exact rational certificates remain in raw results.",
  limits:["One fixed delta grid and128bits; no empirical refinement-order study","Saved binary64 observations are not new continuous enclosures","Raw no-worse is case-dependent; capped no-worse is source-certified","Conditional comparison, no physical rate/consumer admission"]};
}
