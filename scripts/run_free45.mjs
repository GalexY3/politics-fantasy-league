#!/usr/bin/env node
/** Reproduce PF-F45 tests using pinned secondary source CSVs downloaded separately.
 * From project root:
 *   node scripts/run_free45.mjs /absolute/202307.csv /absolute/partidos_generales.csv
 *
 * Requires Node 18+. No network. The output is NOT field verification.
 */
import {readFileSync} from "node:fs";
import {parseCSV,audit2023,auditHistoric,crossSource,sourceGate,multiactorCoverage} from "./electoral_source_audit.mjs";
import * as universe from "../src/politics_fantasy/political_universe.mjs";
import {executeSuite} from "./free45_suite.mjs";
if(process.argv.length!==4)throw Error("Usage: node scripts/run_free45.mjs PATH_202307.csv PATH_partidos_generales.csv");
const base=new URL("../",import.meta.url);
const text=path=>readFileSync(path,"utf8");
const a=text(process.argv[2]),b=text(process.argv[3]);
const atlas=JSON.parse(text(new URL("data/observatory/electoral_atlas_2023.json",base)));
const ui=text(new URL("src/politics_fantasy/web/app.js",base)),server=text(new URL("src/politics_fantasy/server.py",base)),adapter=text(new URL("src/politics_fantasy/electoral_atlas.py",base));
const res=executeSuite({parseCSV,audit2023,auditHistoric,crossSource,sourceGate,multiactorCoverage},universe,a,b,atlas,ui,server,adapter);
console.log(JSON.stringify({results:res,passed:res.filter(x=>x.status==="PASS").length,total:res.length,kind:"SOURCE_PINNED_SECONDARY_AND_SYNTHETIC_QA"},null,2));
if(res.some(x=>x.status!=="PASS"))process.exitCode=1;
