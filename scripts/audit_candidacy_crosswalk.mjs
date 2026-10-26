/** Exact 2023 list acronym join: BOE Albacete proclaimed vs secondary national aggregate labels.
 * Same election, different data source. This is NOT a legal-party identity
 * join, not a provincial vote calculation, and never a people join.
 */
import {readFileSync} from "node:fs";
const root=new URL("../",import.meta.url);
export const load=(rel)=>JSON.parse(readFileSync(new URL(rel,root),"utf8"));
export function crosswalk(original,secondary){
 if(original.dataset_class!=="OFFICIAL_2023_SINGLE_PROVINCE_CANDIDACY_LIST_LABELS"
   ||secondary.dataset_class!=="HISTORICAL_SECONDARY_AGGREGATE")
   throw Error("SOURCE_CLASSES_REQUIRED");
 const lookup=new Map();
 for(const a of secondary.labels){
  const acronym=a.name.split("_").at(-1);
  const list=lookup.get(acronym)||[];list.push(a);lookup.set(acronym,list);
 }
 const rows=original.lists.map(a=>{
  const found=lookup.get(a.acronym)||[];
  if(found.length!==1)return {acronym:a.acronym,status:"UNRESOLVED_NO_UNIQUE_EXACT_ACRONYM",
    legal_party_identity_resolved:false,national_votes:null,national_seats:null};
  const x=found[0];
  return {acronym:a.acronym,status:"UNIQUE_EXACT_ACRONYM_SAME_ELECTION",
    source_atlas_id:x.id,source_official_document:original.source_document,
    national_votes_secondary:x.votes,national_seats_secondary:x.seats,
    has_national_congress_seat_in_secondary_dataset:x.seats>0,
    legal_party_identity_resolved:false,person_identity_resolved:false};
 });
 return {campaign:"PF-BR8N",scope:"ALBACETE_CANDIDACY_VS_NATIONAL_2023_SECONDARY_TOTALS",
  original_boe_sha256:original.original_sha256,
  joined_rows:rows,exact_unique_matches:rows.filter(x=>x.status.startsWith("UNIQUE")).length,
  no_seat_labels_with_candidacy:rows.filter(x=>x.national_seats_secondary===0).length,
  ambiguities:rows.filter(x=>x.status.startsWith("UNRESOLVED")).length,
  legal_parties_validated:0,people_joined:0,
  disclaimer:"Link is an exact acronym across two electoral datasets. National total votes/seats, NOT Albacete-only totals and NOT parties' legal identities; never infer political influence."};
}
if(process.argv[1] && /audit_candidacy_crosswalk\.mjs$/.test(process.argv[1])){
 const result=crosswalk(load("data/observatory/boe_2023_albacete_verified.json"),load("data/observatory/electoral_atlas_2023.json"));
 console.log(JSON.stringify(result,null,2));
 if(result.ambiguities)process.exitCode=2;
}
