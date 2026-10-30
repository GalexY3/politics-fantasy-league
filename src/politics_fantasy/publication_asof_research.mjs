/** Research-only temporal as-of guard. Publisher timestamp must be attested;
 * source URLs and self-declared attestations are NOT external authentication.
 * Does not transform event time or capture time into first-public time.
 */
const TS=/^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\dZ$/;
function instant(x){
 if(typeof x!=='string'||!TS.test(x))throw Error('INVALID_INSTANT');
 const ms=Date.parse(x);
 if(!Number.isFinite(ms)||new Date(ms).toISOString()!==x.replace('Z','.000Z'))throw Error('INVALID_INSTANT');
 return ms;
}
function goodUrl(x){
 try{const u=new URL(x);return u.protocol==='https:'&&u.hostname!==''&&!u.username&&!u.password&&!u.hash;}
 catch{return false;}
}
export function eligibleAsOf(row,cutoff){
 if(!row||typeof row!=='object'||Array.isArray(row))throw Error('INVALID_ROW');
 const until=instant(cutoff);
 const captured=instant(row.captured_at);
 if(row.event_at!==undefined&&row.event_at!==null)instant(row.event_at);
 const first=row.first_public_at;
 if(first===undefined||first===null)return {status:'UNKNOWN_FIRST_PUBLIC_AT'};
 const published=instant(first);
 const attested=typeof row.verified_by==='string'&&row.verified_by.trim()!==''&&
   ['ISSUER_TIMESTAMP','VERIFIED_ARCHIVE'].includes(row.publication_evidence_type)&&
   typeof row.publication_evidence_url==='string'&&row.publication_evidence_url.trim()!=='';
 if(!attested)return {status:'UNKNOWN_FIRST_PUBLIC_AT'};
 if(!goodUrl(row.publication_evidence_url))throw Error('UNSAFE_EVIDENCE_URL');
 if(captured<published)throw Error('IMPOSSIBLE_PUBLICATION_ORDER');
 return {status:published<=until?'ELIGIBLE_ON_ATTESTED_RECORD':'NOT_YET_PUBLIC',
         note:'Attested record, not independently authenticated by this function'};
}
