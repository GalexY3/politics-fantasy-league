/** PF-B50: audit two named SECONDARY electoral datasets without ranking actors.
 * Input UTF-8 files, no network. Historical data ≠ updated electoral registry.
 * npx NOT required. Works under Node 18+.
 */
const FIELDS = ["Nombre de Comunidad","Código de Provincia","Nombre de Provincia"];
export function parseCSV(csv){
 if(typeof csv!=="string"||csv.length===0)throw Error("EMPTY_CSV");
 const rows=[];let row=[],field="",quoted=false;
 const s=csv.charCodeAt(0)===0xfeff?csv.slice(1):csv;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(quoted){
    if(c==='"'&&s[i+1]==='"'){field+='"';i++;}
    else if(c==='"')quoted=false;
    else field+=c;
  }else if(c==='"'){if(field!=="")throw Error("MISPLACED_QUOTE");quoted=true;}
   else if(c===','){row.push(field);field="";}
   else if(c==='\n'){row.push(field);if(row.some(x=>x!==""))rows.push(row);row=[];field="";}
   else if(c==='\r'){if(s[i+1]!=='\n'){row.push(field);rows.push(row);row=[];field="";}}
   else field+=c;
 }
 if(quoted)throw Error("UNCLOSED_QUOTE");
 if(field!==""||row.length){row.push(field);if(row.some(x=>x!==""))rows.push(row);}
 if(rows.length<2)throw Error("HEADER_WITHOUT_DATA");
 const n=rows[0].length;
 if(rows.some((r,i)=>r.length!==n))throw Error("RAGGED_CSV");
 return {header:rows[0],rows:rows.slice(1)};
}
const nat=v=>{if(typeof v!=="string"||!/^\d+$/.test(v))throw Error("NOT_NATURAL_NUMBER:"+v);const n=Number(v);if(!Number.isSafeInteger(n))throw Error("NUMBER_UNSAFE");return n};
export function audit2023(csv){
 const {header,rows}=parseCSV(csv);
 for(const f of FIELDS)if(!header.includes(f))throw Error("MISSING_BASE_FIELD_"+f);
 const votes=header.flatMap((h,i)=>h.endsWith("_votos")?[{name:h.slice(0,-6),v:i,seats:i+1}]:[]);
 if(votes.length<2)throw Error("NO_ELECTORAL_OPTIONS");
 for(let j=0;j<votes.length;j++)if(header[votes[j].seats]!==votes[j].name+"_diputados")throw Error("VOTE_SEATS_NOT_PAIRED");
 const provinces=new Set(),parties=[];
 for(let r of rows){
  const code=r[header.indexOf("Código de Provincia")],name=r[header.indexOf("Nombre de Provincia")];
  if(!code||!name)throw Error("BAD_PROVINCE");
  if(provinces.has(code))throw Error("DUPLICATE_PROVINCE");provinces.add(code);
 }
 for(let v of votes){
  const totals=rows.reduce((acc,r)=>{acc[0]+=nat(r[v.v]);acc[1]+=nat(r[v.seats]);return acc},[0,0]);
  parties.push({source_column:v.name,election:"2023-07",votes:totals[0],seats:totals[1],
   electoral_status:totals[0]===0?"NO_VOTES_RECORDED":totals[1]===0?"VOTES_WITHOUT_CONGRESS_SEAT":"CONGRESS_SEAT_RECORDED"});
 }
 return {dataset:"2023-secondary-province-columns",scope:"CANDIDACY_LABELS_NOT_VERIFIED_DISTINCT_PARTIES",provinces:provinces.size,rows:rows.length,
 labels:parties.length,with_positive_vote_no_seat:parties.filter(p=>p.votes>0&&p.seats===0).length,
 with_seat:parties.filter(p=>p.seats>0).length,labels_data:parties};
}
export function auditHistoric(csv){
 const {header,rows}=parseCSV(csv);
 const keys=["anno","mes","codigo_partido_nacional","votos","siglas","partido","denominacion"];
 if(keys.join("|")!==header.join("|"))throw Error("UNEXPECTED_HISTORIC_COLUMNS");
 const years={},codes=new Map();
 let zero=0,positive=0;
 for(const [i,r]of rows.entries()){
  const year=nat(r[0]),month=nat(r[1]);
  if(year<1970||year>2100||month<1||month>12)throw Error("BAD_ELECTION_DATE");
  const v=Number(r[3]);
  if(!Number.isFinite(v)||v<0)throw Error("BAD_VOTES");
  if(v===0)zero++;else positive++;
  years[year]=(years[year]||0)+1;
  const k=r[2];if(!k)throw Error("MISSING_PARTY_CODE");
  const cd=codes.get(k)||new Set();cd.add(r[6]);codes.set(k,cd);
 }
 return {dataset:"rOpenSpain/infoelectoral-historic",rows:rows.length,
 elections_by_year:years,distinct_dataset_codes:codes.size,positive_vote_rows:positive,zero_vote_rows:zero,
 codes_with_multiple_denominations:[...codes.values()].filter(v=>v.size>1).length,
 important_limit:"This is 1977-2019 longitudinal list, not the up-to-date RPP nor a historical person-role roster"};
}
export function crossSource(a,b){
 if(a.dataset!=="2023-secondary-province-columns"||b.dataset!=="rOpenSpain/infoelectoral-historic")throw Error("WRONG_TYPES");
 return {sources:2,overlap_years:0,historical_last_year:Math.max(...Object.keys(b.elections_by_year).map(Number)),recent_election_year:2023,
 cross_source_identity_merge:"NOT_PERFORMED",official_independent_replication:false,
 political_impact_inferred:false};
}
export function sourceGate(source){
 if(!source||source.official===true&&source.original_bytes_verified!==true)return {verified:false,reason:"OFFICIAL_UNVERIFIED"};
 if(!source.sha||!source.url)return {verified:false,reason:"PROVENANCE_INCOMPLETE"};
 if(!source.license_verified)return {verified:false,reason:"LICENSE_UNCONFIRMED"};
 return {verified:true,reason:null};
}
export function multiactorCoverage(a){return {electoral_labels:a.labels,zero_seat_labels_with_votes:a.with_positive_vote_no_seat,
 nonparliament_inclusion_factor:a.with_positive_vote_no_seat,not_a_measure_of_influence:true,
 warning:"A 2023 slate/coalition label is not necessarily a registered party; this dataset does not contain people"}}
