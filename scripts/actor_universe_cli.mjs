#!/usr/bin/env node
/** PF-BR20H offline CLI. Requires Node 18+. JSON fixture or authorized public-record
 * bundle. No network, no automatic actors, no individual ratings or fantasy scores.
 *
 * node scripts/actor_universe_cli.mjs bundle.json [--as-of 2026-10-25T00:00:00Z]
 */
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {createRegistry,addSource,addActor,addClaim,addEvent,
 coverageAudit,validateRegistry,timeView,minimalParliamentaryBaseline} from "../src/politics_fantasy/political_universe.mjs";
const args=process.argv.slice(2);
if(args.length===0 || args[0].startsWith("--"))throw Error("USAGE: bundle.json [--as-of offset-aware ISO datetime]");
const raw=readFileSync(args[0]);
const payload=JSON.parse(raw.toString("utf8"));
if(!payload||typeof payload!=="object"||!["FIXTURE","USER_PROVIDED_SOURCE_SNAPSHOT"].includes(payload.dataset_class))throw Error("Dataset class must be explicit");
const r=createRegistry();
for(const s of payload.sources||[])addSource(r,s);
for(const a of payload.actors||[])addActor(r,a);
for(const c of payload.claims||[])addClaim(r,c);
for(const e of payload.events||[])addEvent(r,e);
const audit=validateRegistry(r);
if(!audit.valid)throw Error("REFERENTIAL_INTEGRITY_FAILURE: "+audit.problems.length);
const o={
 schema:"PF-BR20H-v1",dataset_class:payload.dataset_class,
 source_bundle_sha256:createHash("sha256").update(raw).digest("hex"),
 source_claims_validated_against_original_raw:false,
 ...audit,coverage:coverageAudit(r),
 parlament_only_baseline:minimalParliamentaryBaseline(r),
 real_person_scores_enabled:false
};
const idx=args.indexOf("--as-of");
if(idx>=0){
 if(!args[idx+1])throw Error("MISSING_CUTOFF");
 const view=timeView(r,args[idx+1]);
 o.as_of={cutoff:view.cutoff,visible_claims:view.claims.length,visible_events:view.events.length,known_source_count:view.eligible_source_ids.length};
}
process.stdout.write(JSON.stringify(o,null,2)+"\n");
