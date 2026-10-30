function runC04(seed){
let state=seed>>>0;function rand(){state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296}
const out={seed,reps:600,regimes:{}};
for(const regime of ["MCAR_10pct","MNAR_success40_failure5"])out.regimes[regime]={naive_count:0,naive_bias_sum:0,naive_mae_sum:0,gate_available_count:0,gate_bias_sum:0,full_missing_count:0,false_zero_count:0,naive_abs_error:[]};
for(let k=0;k<600;k++){
let success=Array.from({length:10},()=>rand()<.6),truth=success.filter(Boolean).length/10;
for(const regime of ["MCAR_10pct","MNAR_success40_failure5"]){
let observed=[],missing=0;
for(const s of success){let p=regime==="MCAR_10pct"?.1:(s?.4:.05);if(rand()<p)missing++;else observed.push(s)}
const r=out.regimes[regime];if(observed.length){let rate=observed.filter(Boolean).length/observed.length;r.naive_count++;r.naive_bias_sum+=rate-truth;r.naive_mae_sum+=Math.abs(rate-truth);r.naive_abs_error.push(Math.abs(rate-truth));if(rate===0&&truth>0)r.false_zero_count++}else{r.full_missing_count++}
if(missing===0){r.gate_available_count++;r.gate_bias_sum+=observed.filter(Boolean).length/10-truth}
}}
for(const r of Object.values(out.regimes)){r.naive_bias_conditional=r.naive_count?r.naive_bias_sum/r.naive_count:null;r.naive_mae_conditional=r.naive_count?r.naive_mae_sum/r.naive_count:null;r.gate_availability=r.gate_available_count/600;r.gate_bias_when_available=r.gate_available_count?r.gate_bias_sum/r.gate_available_count:null;r.false_zero_fraction=r.false_zero_count/600;delete r.naive_abs_error}
return out;
}
