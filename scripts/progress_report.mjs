#!/usr/bin/env node
/** Recompute scope V1 or any validated successor from a local JSON document.
 *
 * node scripts/progress_report.mjs product/progress_scope_v1.json
 * node scripts/progress_report.mjs product/progress_scope_v1.json product/progress_scope_v2.json
 *
 * Percentages describe maturity of work against versioned requirements,
 * not completion chance, scientific quality, probability of release or VSDS.
 */
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {evaluate,compare} from "../src/politics_fantasy/progress_model.mjs";

const args=process.argv.slice(2);
if(args.length<1||args.length>2)throw Error("Usage: progress_report.mjs SCOPE.json [NEW_SCOPE.json]");
const read=p=>{
 const raw=readFileSync(p);
 if(raw.length>200_000)throw Error("SCOPE_FILE_TOO_LARGE");
 return {scope:JSON.parse(raw.toString("utf8")),sha256:createHash("sha256").update(raw).digest("hex")};
};
const old=read(args[0]),start=evaluate(old.scope);
const payload={schema:"PFL_PROGRESS_REPORT_V1",old_scope_sha256:old.sha256,initial:start,
 metrics_are_not_success_probability:true,release_readiness_is_separate:true};
if(args[1]){
 const next=read(args[1]);
 payload.new_scope_sha256=next.sha256;
 payload.current=evaluate(next.scope);
 payload.change=compare(old.scope,next.scope);
}
process.stdout.write(JSON.stringify(payload,null,2)+"\n");
