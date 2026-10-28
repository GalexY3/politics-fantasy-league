function runC01(seed){
 let state=seed>>>0;function rand(){state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296}
 const nrep=600,N=16,method=["count_div12","observed_rate","beta22"],summ={seed,reps:nrep,mae:{},top_high_exposure:{},by_exposure_mae:{},errors:[]};for(let m of method){summ.mae[m]=0;summ.top_high_exposure[m]=0;summ.by_exposure_mae[m]={low:0,high:0}}
 for(let k=0;k<nrep;k++){let a=[];for(let i=0;i<N;i++){let n=i<8?3:12,p=.25+.5*rand(),succ=0;for(let j=0;j<n;j++)if(rand()<p)succ++;a.push({n,p,succ})}
 for(let m of method){let scored=a.map(x=>m==="count_div12"?x.succ/12:m==="observed_rate"?x.succ/x.n:(x.succ+2)/(x.n+4));
 summ.mae[m]+=scored.reduce((z,v,i)=>z+Math.abs(v-a[i].p),0)/N/nrep;
 summ.by_exposure_mae[m].low+=scored.slice(0,8).reduce((z,v,i)=>z+Math.abs(v-a[i].p),0)/8/nrep;
 summ.by_exposure_mae[m].high+=scored.slice(8).reduce((z,v,i)=>z+Math.abs(v-a[i+8].p),0)/8/nrep;
 }
 let b=[];for(let i=0;i<N;i++){let n=i<8?3:12,succ=0;for(let j=0;j<n;j++)if(rand()<.5)succ++;b.push({n,succ})}
 for(let m of method){let vals=b.map(x=>m==="count_div12"?x.succ/12:m==="observed_rate"?x.succ/x.n:(x.succ+2)/(x.n+4));let max=Math.max(...vals);const ties=vals.map((v,i)=>v===max?i:-1).filter(i=>i>=0),high=ties.filter(i=>i>=8).length; summ.top_high_exposure[m]+=high/ties.length/nrep;}
 }
 for(let m of method)summ.mae[m]=+summ.mae[m].toFixed(8);
 return summ;
}
