/** Published model-level ForecastBench aggregates ONLY. No person rows. */
function csvRows(s){
 if(typeof s!=='string')throw Error('CSV_TEXT_REQUIRED');const rows=[];let row=[],field='',quote=false;
 for(let i=0;i<s.length;i++){const x=s[i];if(x==='"'){if(quote&&s[i+1]==='"'){field+='"';i++}else if(!quote&&field!=='')throw Error('BAD_CSV_QUOTE');else quote=!quote}else if(x===','&&!quote){row.push(field);field=''}else if((x==='\n'||x==='\r')&&!quote){if(x==='\r'&&s[i+1]==='\n')i++;row.push(field);if(row.some(f=>f!==''))rows.push(row);row=[];field=''}else field+=x}
 if(quote)throw Error('UNTERMINATED_CSV_QUOTE');row.push(field);if(row.some(x=>x!==''))rows.push(row);return rows
}
const required=['Rank','Team','Model Organization','Model','Dataset','N dataset','Market','N market','Overall','N','Brier Dataset','Brier Market','Brier Overall'];
function number(x){if(typeof x!=='string'||!x.trim()||!/^-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(x.trim()))return null;const z=Number(x);return Number.isFinite(z)?z:null}
export function inspectAggregateLeaderboard(csv){
 const rows=csvRows(csv);if(!rows.length)throw Error('EMPTY_PUBLIC_LEADERBOARD');const head=rows.shift();
 for(const k of required)if(!head.includes(k))throw Error('MISSING_PUBLIC_AGGREGATE_COLUMN:'+k);
 if(new Set(head).size!==head.length)throw Error('DUPLICATE_COLUMN');
 const idx=k=>head.indexOf(k),records=[],duplicates=new Set(),seen=new Set();
 for(const row of rows){if(row.length!==head.length)throw Error('CSV_WIDTH_MISMATCH');
  const k=['Team','Model Organization','Model'].map(f=>row[idx(f)].trim());if(k.some(x=>!x))continue;
  const key=JSON.stringify(k);if(seen.has(key))duplicates.add(key);seen.add(key);
  const obs={key,n:number(row[idx('N')]),nd:number(row[idx('N dataset')]),nm:number(row[idx('N market')]),overall:number(row[idx('Overall')]),dataset:number(row[idx('Dataset')]),market:number(row[idx('Market')]),brierOverall:number(row[idx('Brier Overall')]),rank:number(row[idx('Rank')])};
  if([obs.n,obs.nd,obs.nm].some(x=>x!==null&&(!Number.isInteger(x)||x<0)))throw Error('INVALID_AGGREGATE_SAMPLE_COUNT');
  records.push(obs);
 }
 return {records,duplicates,source_rows:rows.length,parseable_records:records.length};
}
export function comparePublishedAggregateLeaderboards(baseCsv,otherCsv,{minN=20}={}){
 if(!Number.isInteger(minN)||minN<0)throw Error('BAD_MIN_N');
 const a=inspectAggregateLeaderboard(baseCsv),b=inspectAggregateLeaderboard(otherCsv),map=new Map(b.records.map(r=>[r.key,r]));
 const comp=[];
 for(const r of a.records){const s=map.get(r.key);if(!s||a.duplicates.has(r.key)||b.duplicates.has(r.key))continue;
  if([r.n,s.n,r.overall,s.overall,r.rank,s.rank].some(x=>x===null)||r.n<minN||s.n<minN)continue;
  comp.push({baseline_N:r.n,comparison_N:s.n,delta_reported_Overall:s.overall-r.overall,delta_rank:s.rank-r.rank})
 }
 const sum=k=>comp.reduce((a,b)=>a+b[k],0);
 return {schema:'pfl.external.forecastbench.aggregate_panel.v1',unit:'public_model_level_aggregates_not_people',baseline_rows:a.source_rows,comparison_rows:b.source_rows,baseline_nonempty_models:a.parseable_records,comparison_nonempty_models:b.parseable_records,baseline_duplicate_keys:a.duplicates.size,comparison_duplicate_keys:b.duplicates.size,eligible_matched_models:comp.length,median_delta_reported_Overall:comp.length?[...comp].map(x=>x.delta_reported_Overall).sort((a,b)=>a-b)[Math.floor((comp.length-1)/2)]:null,mean_delta_reported_Overall:comp.length?sum('delta_reported_Overall')/comp.length:null,mean_delta_rank:comp.length?sum('delta_rank')/comp.length:null,mean_delta_N:comp.length?sum('comparison_N')/comp.length-sum('baseline_N')/comp.length:null,compared_with_equal_sample_sizes:comp.filter(x=>x.baseline_N===x.comparison_N).length,panel_uses_only_published_aggregates:true,identities_returned:false,causal_effect:false,benchmark_populations_same_proven:false,science_grade:'0/3'};
}
