/** PF-BR30I pure data audit. Inputs: manually transcribed JEC 2023 Table I;
 * independent 2023 secondary source CSV; JEC coalition HTML transcription.
 * NO automatic certification of PDF bytes, no current party/person registry.
 */
const METRICS=[
 ["electors","Total censo electoral"],["voters","Total votantes"],
 ["valid","Votos válidos"],["candidatures","Votos a candidaturas"],
 ["blank","Votos en blanco"],["null","Votos nulos"]];
const TOTAL_OFFICIAL=[37469458,24952447,24688087,24487414,200673,264360];
export function officialTable(psv){
 const raw=psv.split(/\r?\n/).filter(x=>x.trim()&&!x.startsWith("#"));
 const head=raw.shift()?.split("|");
 if(!head||head.join("|")!=="province_code|boe_province|electors|voters|valid|candidatures|blank|null")throw Error("WRONG_JEC_HEADER");
 const seen=new Set(),out=[];
 for(const line of raw){
  const v=line.split("|");if(v.length!==8)throw Error("JEC_RAGGED");
  if(!/^\d{2}$/.test(v[0])||seen.has(v[0]))throw Error("JEC_CODE_COLLISION");seen.add(v[0]);
  const vals=v.slice(2).map(x=>{if(!/^\d+$/.test(x)||!Number.isSafeInteger(Number(x)))throw Error("JEC_BAD_NUMBER");return Number(x)});
  if(vals[2]!==vals[3]+vals[4]||vals[1]!==vals[2]+vals[5])throw Error("JEC_ACCOUNTING_INCONSISTENT");
  out.push({code:v[0],name:v[1],...Object.fromEntries(METRICS.map((m,j)=>[m[0],vals[j]]))});
 }
 if(out.length!==52)throw Error("JEC_NOT_52");
 const national=METRICS.map(([k])=>out.reduce((acc,x)=>acc+x[k],0));
 if(national.some((x,i)=>x!==TOTAL_OFFICIAL[i]))throw Error("JEC_NATIONAL_MISMATCH");
 return {rows:out,national,trace:"MANUAL_TRANSCRIPTION_NOT_CERTIFIED_PDF_BYTES"};
}
export function compareJEC(jec,parsedCsv){
 const head=parsedCsv.header,rows=parsedCsv.rows;
 const codeCol=head.indexOf("Código de Provincia"),candidateCol=head.indexOf("Votos a candidaturas");
 if(codeCol<0||candidateCol<0)throw Error("SECONDARY_REQUIRED_COLUMNS");
 const prov=new Map();
 for(const r of rows){const k=String(r[codeCol]).padStart(2,"0");if(prov.has(k))throw Error("SECONDARY_DUPLICATE_PROVINCE");prov.set(k,r);}
 const partyCols=head.flatMap((k,i)=>k.endsWith("_votos")?[i]:[]);
 if(partyCols.length!==59)throw Error("SECONDARY_EXPECTED_59_LABELS");
 const byMetric=Object.fromEntries(METRICS.map(([m])=>[m,{equal:0,different:0}]));
 const diff=[],perProvince=[];
 for(const p of jec.rows){
   const row=prov.get(p.code);if(!row){diff.push({code:p.code,field:"missing_province"});continue}
   for(const [k,sourceHeader] of METRICS){
     const idx=head.indexOf(sourceHeader);
     if(idx<0)throw Error("SECONDARY_MISSING_METRIC_"+k);
     const val=Number(row[idx]);
     if(!Number.isSafeInteger(val)||val<0)throw Error("SECONDARY_BAD_NUMERIC");
     const matches=val===p[k];byMetric[k][matches?"equal":"different"]++;
     if(!matches)diff.push({code:p.code,field:k,official:p[k],secondary:val});
   }
   let votesOptions=0,positive=0;
   for(const col of partyCols){let val=Number(row[col]);if(!Number.isSafeInteger(val)||val<0)throw Error("BAD_PARTY_COUNT");votesOptions+=val;if(val>0)positive++}
   const byOptionDiff=votesOptions-p.candidatures;
   if(byOptionDiff!==0)diff.push({code:p.code,field:"sum_59_options",official:p.candidatures,secondary:votesOptions});
   perProvince.push({code:p.code,name:p.name,options_with_votes:positive,all_candidates_votes:p.candidatures,recorded_options_votes:votesOptions,difference:byOptionDiff});
 }
 return {official_provinces:jec.rows.length,secondary_provinces:rows.length,paired:perProvince.length,
  counts:byMetric,comparisons:jec.rows.length*METRICS.length,party_sum_comparisons:perProvince.length,
  different_cells:diff,province_options:perProvince, official_total:jec.national,
  source_notes:"Independent JEC Table I transcription, NOT raw PDF parsed. Atlas raw third party, NOT original election Excel."};
}
export function compareFiveBOEIII(atlas){
 const refs=[
 {acronym:"PACMA",official:169237},
 {acronym:"CUP-PR",official:99644},
 {acronym:"FO",official:46274},
 {acronym:"NC-bc",official:45595},
 {acronym:"PDeCAT-E-CiU",official:32016}
 ];
 return refs.map(x=>{
 const m=atlas.labels.filter(p=>p.name.split("_").at(-1).toLowerCase()===x.acronym.toLowerCase());
 return {acronym:x.acronym,official_votes:x.official,match_count:m.length,
    matched_votes:m.length===1?m[0].votes:null,
    exact:m.length===1&&m[0].votes===x.official&&m[0].seats===0};
 });
}
const norm=s=>s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/\s+/g," ").trim();
export function coalitionCrosswalk(jecCoalitions,atlas){
 const collisions=[],mapped=[];
 for(const q of jecCoalitions.entries){
  let m=atlas.labels.filter(p=>norm(p.name.split("_").at(-1))===norm(q.acronym));
  const state=q.senateOnly?"SENATE_ONLY_NOT_CONGRESS_REFERENCE":m.length===1?"ACRONYM_EXACT_UNIQUE_NOT_IDENTITY":m.length===0?"NO_EXACT_ACRONYM_MATCH":"AMBIGUOUS";
  if(m.length>1)collisions.push(q.id);
  mapped.push({jec_id:q.id,official_acronym:q.acronym,official_name:q.officialName,
    source_level:q.registration_level,territorial_scope:q.scope,senate_only:q.senateOnly,
    n_candidate_labels:m.length,match_state:state,candidates:m.length===1&& !q.senateOnly?m.map(x=>x.name):[]});
 }
 return {n_reference:jecCoalitions.entries.length,records:mapped,
  exact_unique_congress:mapped.filter(x=>x.match_state==="ACRONYM_EXACT_UNIQUE_NOT_IDENTITY").length,
  senate_only:mapped.filter(x=>x.senate_only).length,ambiguous_ids:collisions,
  warning:"Matching election acronym is NOT proof of constituent party identity, party registration, or membership."};
}
export function optionCoverage(parsed,atlas){
 const header=parsed.header,rows=parsed.rows;
 const columns=header.flatMap((x,i)=>x.endsWith("_votos")?[{name:x.slice(0,-6),v:i,seats:i+1}]:[]);
 const statuses=new Map(atlas.labels.map(x=>[x.name,x.seat_status]));
 if(columns.length!==59 || statuses.size!==59)throw Error("ATLAS_COVERAGE_MISMATCH");
 const byProvince=rows.map(r=>{
  const options=columns.filter(x=>Number(r[x.v])>0);
  const noSeat=options.filter(x=>statuses.get(x.name)==="VOTES_WITHOUT_CONGRESS_SEAT");
  const noSeatVotes=noSeat.reduce((t,x)=>t+Number(r[x.v]),0);
  const totalCandidateVotes=Number(r[header.indexOf("Votos a candidaturas")]);
  return {code:String(r[header.indexOf("Código de Provincia")]).padStart(2,"0"),
   number_options_with_votes:options.length, number_no_seat_options_with_votes:noSeat.length,
   no_seat_option_votes:noSeatVotes,all_candidate_votes:totalCandidateVotes,
   no_seat_share:totalCandidateVotes?noSeatVotes/totalCandidateVotes:null};
 });
 const totalVotes=byProvince.reduce((a,x)=>a+x.all_candidate_votes,0),
 noSeatTotal=byProvince.reduce((a,x)=>a+x.no_seat_option_votes,0);
 return {provinces:byProvince.length,byProvince,totalCandidateVotes:totalVotes,noSeatVotes:noSeatTotal,
  noSeatShare:totalVotes?noSeatTotal/totalVotes:null,
  low:Math.min(...byProvince.map(x=>x.number_options_with_votes)),
  high:Math.max(...byProvince.map(x=>x.number_options_with_votes)),
  warning:"NO inference of party merits or influence from votes. Distinct election options are not always legal parties."};
}
export function mutationCheck(jec,parsed){
 const corrupted={...parsed,rows:parsed.rows.map(x=>x.slice())};
 const h=corrupted.header.indexOf("Votos válidos");
 corrupted.rows[0][h]=String(Number(corrupted.rows[0][h])+1);
 return compareJEC(jec,corrupted).different_cells.some(x=>x.field==="valid");
}
export function readiness({independent_raw_document_verified=false,first_public_at_verified=false,identity_history_verified=false,official_data_licenses_verified=false}={}){
 const blockers=[];
 if(!independent_raw_document_verified)blockers.push("RAW_OFFICIAL_BYTES_NOT_CERTIFIED");
 if(!first_public_at_verified)blockers.push("FIRST_PUBLIC_AT_UNKNOWN");
 if(!identity_history_verified)blockers.push("ACTOR_IDENTITIES_NOT_HISTORICALLY_RECONCILED");
 if(!official_data_licenses_verified)blockers.push("LICENSE_OF_EACH_PAYLOAD_NOT_VERIFIED");
 return {can_score_real_people:false,can_historical_forecast_asof: blockers.length===0,
 blockers,read_only_aggregates_permitted:true};
}
