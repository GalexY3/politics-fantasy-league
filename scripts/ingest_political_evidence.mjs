#!/usr/bin/env node
/**
 * PF-BR30J source-first offline ingestion.
 *
 * Usage: node scripts/ingest_political_evidence.mjs /path/to/bundle.json [--as-of 2026-10-01T00:00:00Z]
 *
 * JSON bundle: {dataset_class:"ORIGINAL_SNAPSHOT_UNCERTIFIED"|"FULLY_FICTIONAL_ENGINEERING_FIXTURE",
 * sources:[{id,kind,state,url,observed_at,first_public_at,rights,raw_relpath?,sha256_expected?}],
 * entities:[...], roles:[...], events:[...], claims:[...]}
 *
 * RAW_CAPTURED source: raw_relpath is relative to bundle JSON directory, and its
 * SHA256 is cryptographically recomputed. Verified checksum DOES NOT prove
 * download from that URL, publisher identity, licence or first-public date.
 * This tool NEVER publishes individual identities or political ratings.
 */
import {readFileSync,statSync,realpathSync} from "node:fs";
import {dirname,resolve,relative,isAbsolute,sep} from "node:path";
import {createHash} from "node:crypto";
import * as W from "../src/politics_fantasy/evidence_warehouse.mjs";

const input=process.argv[2];
if(!input||input.startsWith("--"))throw Error("Usage: ingest_political_evidence.mjs PATH_BUNDLE.json [--as-of OFFSET_ISO]");
const rawBundle=readFileSync(input);
if(rawBundle.length>4_000_000)throw Error("BUNDLE_TOO_LARGE");
const bundle=JSON.parse(rawBundle.toString("utf8"));
if(!["ORIGINAL_SNAPSHOT_UNCERTIFIED","FULLY_FICTIONAL_ENGINEERING_FIXTURE"].includes(bundle.dataset_class))throw Error("UNKNOWN_EVIDENCE_CLASS");
const parent=realpathSync(dirname(resolve(input))),reg=W.empty(),captures=[];
for(const v of bundle.sources||[]){
 const o={...v};
 if(o.state==="RAW_CAPTURED"){
   if(typeof o.raw_relpath!=="string"||!o.raw_relpath||isAbsolute(o.raw_relpath))throw Error("RAW_FILE_RELATIVE_PATH_REQUIRED");
   const rawpath=realpathSync(resolve(parent,o.raw_relpath)),rel=relative(parent,rawpath);
   if(!rel||rel===".."||rel.startsWith(".."+sep)||isAbsolute(rel))throw Error("RAW_FILE_ESCAPES_BUNDLE_DIRECTORY");
   if(!statSync(rawpath).isFile()||statSync(rawpath).size>25_000_000)throw Error("RAW_FILE_NOT_REGULAR_OR_TOO_LARGE");
   const body=readFileSync(rawpath),sha=createHash("sha256").update(body).digest("hex");
   if(sha!==o.sha256_expected)throw Error("RAW_SHA256_DISAGREEMENT");
   o.sha256=sha;o.digest_recomputed=true;
   captures.push({source_id:o.id,sha256:sha,bytes:body.length,original_publisher_not_verified:true});
 }else if(o.raw_relpath!==undefined||o.sha256_expected!==undefined)throw Error("UNVERIFIED_SOURCE_RAW_FIELDS");
 W.source(reg,o);
}
for(const o of bundle.entities||[])W.entity(reg,o);
for(const o of bundle.roles||[])W.role(reg,o);
for(const o of bundle.events||[])W.event(reg,o);
for(const o of bundle.claims||[])W.claim(reg,o);
const audit=W.auditBundle(reg),asofIx=process.argv.indexOf("--as-of");
const result={
 campaign:"PF-BR30J",schema:"SOURCE_FIRST_BUNDLE_V1",
 dataset_class:bundle.dataset_class,sha256_bundle:createHash("sha256").update(rawBundle).digest("hex"),
 original_publisher_authenticated:false,
 source_captures:captures,
 audit,
 any_private_profiles_exported:false,
 real_people_scoring_enabled:false
};
if(asofIx>=0){
 if(!process.argv[asofIx+1])throw Error("MISSING_ASOF_VALUE");
 const x=W.asOf(reg,process.argv[asofIx+1]);
 result.as_of={cutoff:x.as_of,sources_available:x.source_count,
  documented_roles_visible:x.roles.length,events_visible:x.events.length,claims_visible:x.claims.length};
}
process.stdout.write(JSON.stringify(result,null,2)+"\n");
if(!audit.ok)process.exitCode=1;
