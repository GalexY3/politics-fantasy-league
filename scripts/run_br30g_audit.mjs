#!/usr/bin/env node
/** PF-BR30G C03-C30 — replay documented, secondary-source observational contrasts.
 * Run: node scripts/run_br30g_audit.mjs /path/to/pleno.jsonl --out /path/to/results.json
 * Passing --allow-other-blob changes the study population; the result is a NEW VERSION.
 * No network traffic. Produces anonymous aggregates only.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { analyze } from "./br30g_audit.mjs";
const EXPECTED = "71918bb689c7a62cfbbdafe0b9248eac6b5c4be1";
const args=process.argv.slice(2);
if (!args.length || args[0].startsWith("--")) {
  console.error("Usage: node scripts/run_br30g_audit.mjs FILE.jsonl [--out FILE.json] [--allow-other-blob]");
  process.exit(2);
}
const raw=readFileSync(args[0]);
const blobHash=createHash("sha1").update("blob "+raw.byteLength+"\0").update(raw).digest("hex");
if(blobHash!==EXPECTED && !args.includes("--allow-other-blob")){
  throw new Error("Input file is NOT the pinned audit blob; use --allow-other-blob only for a distinct analysis or fixture");
}
const result=analyze(raw.toString("utf8"));
result.input.actualGitBlobSha1=blobHash;
result.input.provenanceChecked=blobHash===EXPECTED;
result.input.isSameOriginalRevision=blobHash===EXPECTED;
const output=JSON.stringify(result,null,2)+"\n";
const oi=args.indexOf("--out");
if(oi>=0){
 if(!args[oi+1]||args[oi+1].startsWith("--"))throw new Error("Missing --out file");
 writeFileSync(args[oi+1],output,"utf8");
}else process.stdout.write(output);
