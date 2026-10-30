function runC02(seed){
let state=seed>>>0;function rand(){state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296}
const m=["raw_count","observed_rate","beta22","scheduled_rate"];const out={seed,reps:500,expected:{},empirical:{},optimal_policy:{}};for(let method of m){out.empirical[method]={all:0,only_easy:0,var_all:0,var_only_easy:0,paired_difference:0}}
function val(method,success,attempted){return method==="raw_count"?success:method==="observed_rate"?success/attempted:method==="beta22"?(success+2)/(attempted+4):success/20}
for(let method of m){const a=val(method,9.8,20),b=val(method,3.4,4);out.expected[method]={all:a,only_easy:b,cherry_minus_all:b-a};out.optimal_policy[method]=a>b?"all":"only_easy"}
let worlds=[];for(let i=0;i<500;i++){let e=0,h=0;for(let j=0;j<4;j++)if(rand()<.85)e++;for(let j=0;j<16;j++)if(rand()<.4)h++;worlds.push({e,h})}
for(let method of m){let arrA=worlds.map(({e,h})=>val(method,e+h,20)),arrB=worlds.map(({e})=>val(method,e,4));let mean=x=>x.reduce((s,v)=>s+v,0)/x.length;let av=mean(arrA),bv=mean(arrB);out.empirical[method]={all:av,only_easy:bv,var_all:mean(arrA.map(x=>(x-av)**2)),var_only_easy:mean(arrB.map(x=>(x-bv)**2)),paired_difference:bv-av}}
return out;
}
