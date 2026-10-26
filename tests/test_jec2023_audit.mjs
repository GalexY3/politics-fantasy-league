/* PF-BR30I regression, independent of network. No actual original JEC PDF bytes.
 * node --test tests/test_jec2023_audit.mjs
 */
import {test} from "node:test";
import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {officialTable,compareFiveBOEIII,coalitionCrosswalk,readiness} from "../scripts/jec2023_audit.mjs";
const load=p=>readFileSync(new URL("../"+p,import.meta.url),"utf8");
const raw=load("research/BRANCH30I_20261026/JEC_2023_TABLE_I_TRANSCRIPTION.psv");
const atlas=JSON.parse(load("data/observatory/electoral_atlas_2023.json"));
const coals=JSON.parse(load("research/BRANCH30I_20261026/JEC_COALITIONS_2023_TRANSCRIPTION.json"));
test("BOE Table I transcribed 52 provinces and 6 official totals",()=>{
 const r=officialTable(raw);
 assert.equal(r.rows.length,52);
 assert.deepEqual(r.national,[37469458,24952447,24688087,24487414,200673,264360]);
});
test("JEC transcription rejects altered count even if line algebra remains valid",()=>{
 const bad=raw.replace("Albacete|307988","Albacete|307989");
 assert.throws(()=>officialTable(bad),/JEC_NATIONAL_MISMATCH/);
});
test("JEC rejects a duplicate district row",()=>{
 const lines=raw.trimEnd().split("\n");
 assert.throws(()=>officialTable(raw+"\n"+lines.at(-1)),/JEC_CODE_COLLISION/);
});
test("Five official BOE Table III options without seats match secondary atlas",()=>{
 assert.equal(compareFiveBOEIII(atlas).filter(x=>x.exact).length,5);
});
test("Coalitions are typed distinct from parties and Senate-only not matched as Congress",()=>{
 const m=coalitionCrosswalk(coals,atlas);
 assert.equal(m.n_reference,16);assert.equal(m.senate_only,2);
 assert.equal(m.exact_unique_congress,10);
 assert.equal(m.records.filter(x=>x.senate_only&&x.candidates.length===0).length,2);
});
test("Original verification and as-of disabled unless evidence exists",()=>{
 const x=readiness();assert.equal(x.can_score_real_people,false);
 assert.equal(x.can_historical_forecast_asof,false);
 assert.equal(x.blockers.length,4);
});
