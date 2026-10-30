/** Synthetic-only research comparator for already-normalized anonymous counts.
 * A compositional gap is NOT a person's election probability or causal effect.
 * Official XLSX schemas, categories and provenance must be independently verified.
 */
function validId(s){return typeof s==='string'&&s.trim()===s&&s.length>0;}
export function compareElectionComposition(rows){
 if(!Array.isArray(rows))throw Error('ROWS_NOT_ARRAY');
 if(!rows.length)throw Error('NO_ROWS');
 const groups=new Map();
 for(const r of rows){
  if(!r||typeof r!=='object'||Array.isArray(r)||
    !validId(r.election_id)||!validId(r.district_id)||!validId(r.category)||
    !['candidates','elected'].includes(r.series))throw Error('INVALID_STRATUM');
  if(!Number.isSafeInteger(r.count)||r.count<0)throw Error('INVALID_COUNT');
  const key=JSON.stringify([r.election_id,r.district_id]);
  if(!groups.has(key))groups.set(key,{election_id:r.election_id,district_id:r.district_id,candidates:new Map(),elected:new Map()});
  const m=groups.get(key)[r.series];
  if(m.has(r.category))throw Error('DUPLICATE_CATEGORY');
  m.set(r.category,r.count);
 }
 const result=[];
 for(const s of groups.values()){
  if(!s.candidates.size||!s.elected.size)throw Error('UNMATCHED_STRATUM');
  const a=[...s.candidates.keys()].sort(),b=[...s.elected.keys()].sort();
  if(JSON.stringify(a)!==JSON.stringify(b))throw Error('CATEGORY_MISMATCH');
  const Nc=[...s.candidates.values()].reduce((u,v)=>u+v,0),Ne=[...s.elected.values()].reduce((u,v)=>u+v,0);
  if(!Nc||!Ne)throw Error('ZERO_DENOMINATOR');
  const categories=a.map(category=>{
   const candidates=s.candidates.get(category),elected=s.elected.get(category);
   if(elected>candidates)throw Error('ELECTED_GT_CANDIDATES');
   const cShare=100*candidates/Nc,eShare=100*elected/Ne;
   return {category,candidates,elected,candidate_share_pct:+cShare.toFixed(6),
           elected_share_pct:+eShare.toFixed(6),composition_gap_pp:+(eShare-cShare).toFixed(6)};
  });
  if(Ne>Nc)throw Error('ELECTED_GT_CANDIDATES');
  result.push({election_id:s.election_id,district_id:s.district_id,
               denominators:{candidates:Nc,elected:Ne},categories,
               per_person_success_probability_computable:false,
               note:'Aggregate composition; no identity links, original source or causal denominator'});
 }
 return result;
}
