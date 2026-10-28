/* PFL progress index 1.0: completion against an explicit versioned scope.
 * This is not CT2/VSDS, probability of success, or independently verified %
 * of total political activity. Inputs are reviewed maturity judgements.
 */
const LEVELS=Object.freeze([0,0.1,0.4,0.6,0.85,1]);
const finite=v=>typeof v==="number"&&Number.isFinite(v);
export function validateScope(scope){
 if(!scope||typeof scope!=="object"||scope.scope_id!=="PFL-V1-20261026"
  ||!Number.isInteger(scope.revision)||scope.revision<1)throw Error("BAD_SCOPE_VERSION");
 if(!Array.isArray(scope.tracks)||!scope.tracks.length)throw Error("NO_TRACKS");
 const tracks=new Set(),milestones=new Set();let w=0;
 for(const t of scope.tracks){
  if(typeof t.id!=="string"||!t.id||tracks.has(t.id))throw Error("DUPLICATE_OR_INVALID_TRACK");
  tracks.add(t.id);
  if(typeof t.name!=="string"||!t.name)throw Error("BAD_TRACK_NAME");
  if(!finite(t.weight)||t.weight<=0)throw Error("BAD_WEIGHT");
  w+=t.weight;
  if(!Array.isArray(t.milestones)||t.milestones.length===0)throw Error("NO_MILESTONES");
  for(const m of t.milestones){
   if(typeof m.id!=="string"||!/^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$/.test(m.id)||milestones.has(m.id))throw Error("DUPLICATE_OR_INVALID_MILESTONE");
   milestones.add(m.id);
   if(!Number.isInteger(m.level)||m.level<0||m.level>5)throw Error("BAD_MATURITY");
   if(!finite(m.size)||m.size<=0||m.size>10000)throw Error("BAD_MILESTONE_SIZE");
   if(typeof m.name!=="string"||m.name.length<4||typeof m.why!=="string"||m.why.length<10
    ||typeof m.evidence_ref!=="string"||m.evidence_ref.length<5
    ||typeof m.evidence_class!=="string"||!m.evidence_class)throw Error("MILESTONE_NEEDS_EVIDENCE");
  }
 }
 if(Math.abs(w-100)>1e-8)throw Error("TRACK_WEIGHTS_MUST_TOTAL_100");
 return {ok:true,tracks:tracks.size,milestones:milestones.size,weights_total:w};
}
export function evaluate(scope){
 const valid=validateScope(scope),tracks=[],all=[];
 for(const t of scope.tracks){
  let n=0,d=0;
  const ms=t.milestones.map(m=>{
   const earned=LEVELS[m.level];n+=m.size*earned;d+=m.size;
   const entry={id:m.id,name:m.name,maturity:m.level,earned,weight_within_track:m.size,
    evidence_ref:m.evidence_ref,evidence_class:m.evidence_class,reason:m.why};
   all.push(entry);return entry;
  });
  const pct=100*n/d;
  tracks.push({id:t.id,name:t.name,weight:t.weight,progress_pct:pct,
   contribution_pp:t.weight*pct/100,achieved_units:n,scope_units:d,milestones:ms});
 }
 const globalPct=tracks.reduce((a,t)=>a+t.contribution_pp,0);
 const levels=Object.fromEntries(LEVELS.map((_,i)=>[i,all.filter(m=>m.maturity===i).length]));
 const byId=new Map(all.map(x=>[x.id,x]));
 const cannot=(id,min,reason)=>!byId.has(id)||byId.get(id).maturity<min?reason:null;
 const releaseBlockers=[
 cannot("src.registry",4,"Registro de partidos/candidaturas sin originales auditados"),
 cannot("id.real",4,"Identidades públicas reales sin reconciliar"),
 cannot("ev.person",4,"Eventos individuales reales sin atribución verificada"),
 cannot("sec.auth",4,"Autenticación y autorización multiusuario inexistentes"),
 cannot("qa.endtoend",4,"Pruebas end-to-end nativas aún no acreditadas"),
 cannot("launch.hosted",4,"No existe despliegue público seguro")
 ].filter(Boolean);
 return {schema:"PFL_PROGRESS_1",scope_id:scope.scope_id,revision:scope.revision,review_date:scope.review_date,
 objective:scope.target,method:"WEIGHTED_SCOPE_EVIDENCE_MATURITY",
 progress_pct:globalPct,progress_display_pct:Math.round(globalPct*10)/10,
 level_histogram:levels,track_count:valid.tracks,milestone_count:valid.milestones,tracks,
 global_status:releaseBlockers.length?"NOT_PUBLIC_RELEASE_READY":"RELEASE_GATES_CLEARED_FOR_FURTHER_VALIDATION",
 release_blockers:releaseBlockers,real_people_scoring_ready:false,
 scope_change_notice:"Completion can go down if requirements are added or weights change. No inference from number of AB cycles.",
 scientific_grade_separate:true,actor_influence_inferred:false};
}
function copy(x){return JSON.parse(JSON.stringify(x))}
export function revise(scope,patch){
 validateScope(scope);
 if(!patch||typeof patch!=="object"||!Number.isInteger(patch.revision)||patch.revision<=scope.revision
  ||typeof patch.reason!=="string"||patch.reason.length<12)throw Error("SCOPE_REVISION_REASON_REQUIRED");
 const n=copy(scope);n.revision=patch.revision;n.review_date=patch.review_date??scope.review_date;
 const changeLevels=patch.level_updates??{};
 for(const [id,level] of Object.entries(changeLevels)){
  const m=n.tracks.flatMap(t=>t.milestones).find(x=>x.id===id);
  if(!m)throw Error("UNKNOWN_MILESTONE_"+id);
  m.level=level;
 }
 for(const addition of patch.add_milestones??[]){
  const t=n.tracks.find(x=>x.id===addition.track_id);
  if(!t)throw Error("MISSING_TARGET_TRACK");
  t.milestones.push(copy(addition.milestone));
 }
 for(const [id,weight] of Object.entries(patch.track_weights??{})){
  const t=n.tracks.find(x=>x.id===id);
  if(!t)throw Error("UNKNOWN_WEIGHT_TRACK");t.weight=weight;
 }
 n.change_log=[...(scope.change_log??[]),{from:scope.revision,to:n.revision,reason:patch.reason,
  effective_date:patch.review_date??scope.review_date,added_milestones:(patch.add_milestones??[]).map(x=>x.milestone.id),
  maturity_revisions:Object.keys(changeLevels),weight_revisions:Object.keys(patch.track_weights??{})}];
 validateScope(n);
 return n;
}
/** Oaxaca-style sequential comparison. New levels projected onto old scope
 * yield WORK effect; then adding/reweighting new scope yields SCOPE effect.
 * Not unique decomposition: work-first order is declared.
 */
export function compare(oldScope,newScope){
 // Report a lineage mismatch before validating the individual scopes. Both
 // scopes still undergo full validation when their identifiers agree.
 if(typeof oldScope?.scope_id==="string" && typeof newScope?.scope_id==="string"
  && oldScope.scope_id!==newScope.scope_id)throw Error("SCOPE_LINEAGE_MISMATCH");
 const old=evaluate(oldScope),now=evaluate(newScope);
 if(oldScope.scope_id!==newScope.scope_id||newScope.revision<=oldScope.revision)throw Error("SCOPE_LINEAGE_MISMATCH");
 const projected=copy(oldScope),newLevels=new Map(newScope.tracks.flatMap(t=>t.milestones).map(m=>[m.id,m.level]));
 for(const t of projected.tracks)for(const m of t.milestones)if(newLevels.has(m.id))m.level=newLevels.get(m.id);
 const counter=evaluate(projected);
 const workEffect=counter.progress_pct-old.progress_pct,scopeEffect=now.progress_pct-counter.progress_pct;
 return {from_revision:oldScope.revision,to_revision:newScope.revision,old_pct:old.progress_pct,
 after_work_same_scope_pct:counter.progress_pct,new_pct:now.progress_pct,
 work_effect_pp:workEffect,scope_effect_pp:scopeEffect,
 net_change_pp:now.progress_pct-old.progress_pct,
 decomposition:"WORK_FIRST_THEN_SCOPE; same milestone ID must mean same target, changed definition must use new ID"};
}
export const maturityTable=LEVELS.map((earned,level)=>({level,earned}));
