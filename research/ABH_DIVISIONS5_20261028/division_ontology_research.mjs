/** PFL AB-H DIVISIONS5 C05. Research-only source-record schema; not a publisher or temporal authentication. */
export function validateVote(r){
  if(!r || typeof r!=="object" || Array.isArray(r)) throw new Error("INVALID_RECORD");
  if(!["commons","lords"].includes(r.house)) throw new Error("UNKNOWN_HOUSE");
  if(typeof r.division_id!=="string" || !/^(commons|lords):\d+$/.test(r.division_id) || !r.division_id.startsWith(r.house+":")) throw new Error("INVALID_STABLE_ID");
  if(!Number.isSafeInteger(r.division_number) || r.division_number<=0) throw new Error("INVALID_DIVISION_NUMBER");
  if(typeof r.date!=="string" || !/^\d{4}-\d{2}-\d{2}$/.test(r.date) || !Number.isFinite(Date.parse(r.date+"T00:00:00Z")) || new Date(r.date+"T00:00:00Z").toISOString().slice(0,10)!==r.date) throw new Error("INVALID_DATE");
  for(const s of ["motion","stage","source_url"]){if(typeof r[s]!=="string" || r[s].trim()!==r[s] || !r[s]) throw new Error("MISSING_"+s);}
  if(!/^https:\/\/votes\.parliament\.uk\/(?:votes\/(?:commons|lords)\/division\/\d+)?$/i.test(r.source_url))throw new Error("INVALID_SOURCE_URL");
  if(r.source_type!=="OFFICIAL_HTML_INDEX")throw new Error("UNSUPPORTED_PROVENANCE");
  if(r.first_public_at!==null)throw new Error("UNVERIFIED_FIRST_PUBLIC_AT");
  if(r.physical_attendance_inferred!==false)throw new Error("ATTENDANCE_NOT_OBSERVED");
  const votes=r.votes;
  if(!votes || typeof votes!=="object" || Array.isArray(votes))throw new Error("INVALID_VOTES");
  const keys=r.house==="commons"?["aye","no"]:["content","not_content"];
  if(Object.keys(votes).length!==2 || keys.some(k=>!Object.hasOwn(votes,k)))throw new Error("CHAMBER_CATEGORY_MISMATCH");
  if(keys.some(k=>!Number.isSafeInteger(votes[k]) || votes[k]<0))throw new Error("INVALID_COUNT");
  if(!Number.isSafeInteger(r.reported_total) || r.reported_total!==votes[keys[0]]+votes[keys[1]])throw new Error("COUNT_IDENTITY_FAIL");
  return {ok:true,key:r.division_id,house:r.house,recorded_total:r.reported_total,source_authenticated_bytes:false,persons_observed:false};
}
export function uniqueDivisionKeys(rows){
  if(!Array.isArray(rows))throw new Error("ROWS_REQUIRED");
  const keys=new Set();
  for(const row of rows){
    const key=validateVote(row).key;
    if(keys.has(key))throw new Error("DUPLICATE_DIVISION_ID");
    keys.add(key);
  }
  return keys.size;
}
