export function runRoundtripRepair(R5,saved){
 const {R,coefficients,envelopeStep}=R5;let checks=0;const results=[];
 const assert=(x,m)=>{checks++;if(!x)throw Error(m);};
 for(const c of saved.cases){
  const row=c.rows.find(r=>r.steps===256),coef=coefficients({scope:"DECLARED_FINITE_MODEL",K:[["-1","2"],["1","-2"]],pi:["2/3","1/3"],d:["1","4"],h:"1",f:c.formation==="zero"?["0","0"]:["1","0"]});
  const restored=envelopeStep(row.exact,coef,"0").endpoint;
  for(const key of ["M","U","E"]){assert(restored[key].toString()===row.exact[key],"saved zero-step "+c.formation+key);assert(R(row.exact[key]).toString()===row.exact[key],"scalar roundtrip");results.push({case:c.formation,key,chars:row.exact[key].length,exact_roundtrip:true});}
 }
 const large="1"+"0".repeat(3000);assert(R(large).toString()===large,"long canonical integer");
 assert(R("000123").eq("123"),"canonical normalization");
 assert(R("-2/-4").eq("1/2"),"fraction signs");
 for(const value of [0.1,"NaN","1/0","1e2000","1."+("2".repeat(2100))]){let rejected=false;try{R(value);}catch(e){rejected=true;}assert(rejected,"retained guard");}
 return{schema:"WU_R5_ROUNDTRIP_REPAIR_V1",status:"PASS",checks,results,old_primary_replayed:false,repair:"Canonical integer/fraction rehydration precedes decimal/exponent length guard"};
}
