/** PFL research-only vote-key guard, 2026-10-28.
 * Internal observation_seq is a documented order in the sampled source extraction.
 * It is NOT asserted to be the Congreso's original vote id or first-public timestamp.
 * No real-person voting data. Do not turn this into a scoring pipeline.
 */
export function canonicalVoteKey(row){
 const required=['institution','legislature','session_id','session_date','observation_seq','expediente'];
 for(const k of required)if(row[k]===undefined||row[k]===null||String(row[k]).trim()==='')throw Error('MISSING_'+k);
 if(!Number.isSafeInteger(row.observation_seq)||row.observation_seq<1)throw Error('INVALID_OBSERVATION_SEQ');
 if(!/^\d{4}-\d{2}-\d{2}$/.test(row.session_date))throw Error('DATE_NOT_ISO');
 const key=[row.institution,row.legislature,row.session_id,row.session_date,String(row.observation_seq)].join('|');
 if(!/^[a-zA-Z0-9_|./:-]+$/.test(key))throw Error('UNSAFE_KEY_CHARS');
 return key;
}
export function indexVotes(rows){
 if(!Array.isArray(rows))throw Error('ROWS_NOT_ARRAY');
 const seen=new Map(),byExpediente=new Map();
 for(const row of rows){
  const k=canonicalVoteKey(row);
  if(seen.has(k))throw Error('DUPLICATE_VOTE_KEY '+k);
  const counts=['yes','no','abstain'].map(z=>row[z]);
  if(counts.some(n=>!Number.isSafeInteger(n)||n<0))throw Error('INVALID_AGGREGATE '+k);
  const total=counts.reduce((a,b)=>a+b,0);
  if(row.total!==total)throw Error('INCONSISTENT_TOTAL '+k);
  seen.set(k,{...row,key:k});
  const scope=row.institution+'|'+row.legislature+'|'+row.expediente;
  byExpediente.set(scope,[...(byExpediente.get(scope)||[]),k]);
 }
 return {votes:[...seen.values()],multiVoteExpedientes:[...byExpediente.entries()].filter(([,v])=>v.length>1).map(([scope,vote_keys])=>({scope,vote_keys})),count:seen.size};
}
