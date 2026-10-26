import {test} from "node:test";
import {strict as assert} from "node:assert";
import {crosswalk,load} from "../scripts/audit_candidacy_crosswalk.mjs";
const boe=load("data/observatory/boe_2023_albacete_verified.json");
const atlas=load("data/observatory/electoral_atlas_2023.json");
test("all eight Albacete original BOE labels have a unique exact secondary election label",()=>{
 const r=crosswalk(boe,atlas);
 assert.equal(r.exact_unique_matches,8);assert.equal(r.ambiguities,0);
 assert.equal(r.joined_rows.length,8);assert.equal(r.legal_parties_validated,0);
 assert.equal(r.people_joined,0);
});
test("at least four options with original proclaimed list had no seats in this historical election",()=>{
 const r=crosswalk(boe,atlas);
 assert.deepEqual(r.joined_rows.filter(x=>x.national_seats_secondary===0)
    .map(x=>x.acronym),["FO","PACMA","PUM+J","RECORTES CERO"]);
 assert.equal(r.no_seat_labels_with_candidacy,4);
});
test("ambiguous acronym does not silently resolve legal identity",()=>{
 const altered=structuredClone(atlas),dup=structuredClone(altered.labels.find(x=>x.name.endsWith("_FO")));
 dup.id="fake_alias_duplicated";altered.labels.push(dup);
 const r=crosswalk(boe,altered);
 assert.equal(r.ambiguities,1);
 assert.equal(r.joined_rows.find(x=>x.acronym==="FO").national_votes,null);
 assert.equal(r.joined_rows.find(x=>x.acronym==="FO").legal_party_identity_resolved,false);
});
test("reject false original-source declaration",()=>{
 const altered=structuredClone(boe);
 altered.dataset_class="LEGAL_PARTIES_VERIFIED";
 assert.throws(()=>crosswalk(altered,atlas),/SOURCE_CLASSES_REQUIRED/);
});
