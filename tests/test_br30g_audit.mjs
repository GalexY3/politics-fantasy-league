/** Pure analyser regression checks using wholly SYNTHETIC records.
 * Run: node --test tests/test_br30g_audit.mjs
 */
import { test } from "node:test";
import { strict as assert } from "node:assert";
import { analyze } from "../scripts/br30g_audit.mjs";
function make(id,fecha,sesion,n,yes,no,nomYes,nomNo,category="Voto ordinario"){
  return {id,fecha,sesion,numero:n,fuente:"https://fixture.invalid",tipo:category,texto:"fixture",
    totales:{si:yes,no,abstencion:0,noVota:0},
    votos:{S:Array.from({length:nomYes},(_,i)=>"a"+i).join(" "),
           N:Array.from({length:nomNo},(_,i)=>"b"+i).join(" ")},
    grupos:{"GTEST":[yes,no,0,0]},di:"",asentimiento:false};
}
const cases=[
 make("s1-v001","2024-01-03",1,1,5,4,2,4),
 make("s1-v002","2024-01-03",1,2,2,7,2,6),
 make("s2-v001","2025-01-03",2,1,9,0,9,0)
];
const output=analyze(cases.map(JSON.stringify).join("\n")+"\n");
test("28 distinct numbered effects emitted",()=>assert.deepEqual(Object.keys(output.cycles),Array.from({length:28},(_,i)=>"C"+String(i+3).padStart(2,"0"))));
test("synthetic cross-option miss counter preserves total",()=>assert.equal(output.cycles.C06.summary.allMissing,4));
test("C13 identifies one strict reversal only in close margins",()=>assert.equal(output.cycles.C13.summary.bins["0-5"].strict,1));
test("C14 conservative certification has no false sign proof",()=>assert.equal(output.cycles.C14.summary.mismatchesAmongRobust,0));
test("C29 no false group count mismatch in complete fixture",()=>assert.equal(output.cycles.C29.summary.groupAggregateMismatchedVotes,0));
test("C30 does not claim official certification even with complete fixtures",()=>{
 assert.equal(output.cycles.C30.summary.eligibleForRealPersonFantasyScores,0);
 assert.equal(output.cycles.C30.summary.nominalOriginalIndependentlyMatched,0);
});
test("future-derived prediction is declared retrospective",()=>assert.match(output.cycles.C27.summary.warning,/Retrospective/));
