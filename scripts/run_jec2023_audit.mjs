#!/usr/bin/env node
/** PF-BR30I official documentary audit against an explicitly supplied 2023
 * secondary source CSV. No network, no credentials, and no real-person ratings.
 *
 * node scripts/run_jec2023_audit.mjs /path/to/202307.csv
 * The 52x6 official reference is a MANUAL TRANSCRIPTION of BOE-A-2023-18907
 * (1 Sep 2023, Table I), not downloaded original PDF bytes. Outputs JSON.
 */
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {parseCSV} from "./electoral_source_audit.mjs";
import {officialTable,compareJEC,compareFiveBOEIII,coalitionCrosswalk,optionCoverage,mutationCheck,readiness} from "./jec2023_audit.mjs";
const base=new URL("../",import.meta.url);
const get=(name)=>readFileSync(new URL(name,base),"utf8");
if(process.argv.length!==3)throw Error("Usage: node scripts/run_jec2023_audit.mjs /path/to/202307.csv");
const raw=readFileSync(process.argv[2]);
const transcription=get("research/BRANCH30I_20261026/JEC_2023_TABLE_I_TRANSCRIPTION.psv");
const coalitions=JSON.parse(get("research/BRANCH30I_20261026/JEC_COALITIONS_2023_TRANSCRIPTION.json"));
const atlas=JSON.parse(get("data/observatory/electoral_atlas_2023.json"));
const tab=officialTable(transcription),csv=parseCSV(raw.toString("utf8")),comparison=compareJEC(tab,csv);
const result={schema:"PF-BR30I-JEC-2023-v1",secondary_sha256:createHash("sha256").update(raw).digest("hex"),
 official_reference_kind:"JEC_TABLE_I_MANUAL_TRANSCRIPTION_NOT_PDF_BYTES",
 official_document:"https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907",
 comparison,nonseatOfficialFive:compareFiveBOEIII(atlas),
 coalitionMatch:coalitionCrosswalk(coalitions,atlas),
 coverage:optionCoverage(csv,atlas),negativeMutationDetected:mutationCheck(tab,csv),
 readiness:readiness()};
process.stdout.write(JSON.stringify(result,null,2)+"\n");
if(comparison.different_cells.length||!result.nonseatOfficialFive.every(x=>x.exact)||!result.negativeMutationDetected)process.exitCode=1;
