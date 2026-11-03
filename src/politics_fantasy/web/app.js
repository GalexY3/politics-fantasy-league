'use strict';
// Front-end for a LOCAL, FICTIONAL demo. No political measurements are scored here.
const ui = { tab:'overview', guest:false, scienceOnly:false, club:'demo', state:null, lab:null, field:null, atlas:null, candidacies:null, nominations:null, evidence:null, scientificSources:null, parcanCohorts:null, proceduralCoverage:null, siapCoverage:null, populationReadiness:null, institutionalLineage:null, progress:null, picks:null, message:'', session:null, csrf:null, scientific:null, scientificError:null, scientificLoading:false, scienceCut:'late', scienceScenario:'baseline', scienceValid:'2026-09-15', scienceChronicleValid:'2026-10-10', scienceFirstPublic:'as_of', scienceCandidate:'baseline', scienceAdmission:null, scienceAdmissionError:null, scienceAdmitting:false, scienceRequest:0, scienceExportGeneration:0, scienceRegistry:null, scienceRegistryLoading:false, scienceRegistryError:null, scienceRegistryRequest:0, scienceRegistryExportGeneration:0, scienceRegistryValid:'2026-09-15', scienceRegistryFamily:'all', scienceRegistryPublished:'as_of', scienceRegistryTab:'sources', scienceRegistryKind:'ALL' };
const el = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Escape alone does not make an untrusted URL safe to navigate.
function boeSourceLink(value){
 try {
  const url=new URL(value);
  if(url.protocol==='https:' && ['boe.es','www.boe.es'].includes(url.hostname)
     && !url.username && !url.password && !url.port)
   return `<a href='${esc(url.href)}' target='_blank' rel='noopener noreferrer'>BOE-A-2023-15066</a>`;
 } catch (_) { /* Invalid or missing URLs are rendered as text. */ }
 return 'BOE-A-2023-15066 (enlace no disponible)';
}
const count = n => new Intl.NumberFormat('es-ES').format(n);
const day = iso => new Intl.DateTimeFormat('es-ES',{day:'2-digit',month:'short',year:'numeric'}).format(new Date(iso));
const money = n => `${count(n)} CR`;
function notice(msg, error=false){ const t=el('toast'); t.textContent=msg; t.className=error?'visible error':'visible'; clearTimeout(notice.timer); notice.timer=setTimeout(()=>t.className='',3600); }
async function call(route, body){
 if(ui.guest)throw new Error('Operaciones de cuenta no disponibles en modo visitante');
 const headers={'Content-Type':'application/json','X-PFL-Request':'1'};
 if(ui.csrf)headers['X-PFL-CSRF']=ui.csrf;
 const response=await fetch(route,{method:'POST',headers,credentials:'same-origin',body:JSON.stringify(body)});
 const result=await response.json();
 if(!response.ok)throw new Error(result.message||result.error||'Error');
 return result.result;
}
async function refresh(){
 const endpoints=['state','lab','field','electoral-atlas','evidence-readiness',
  'progress','verified-candidacies','official-nominations','scientific-sources',
  'spanish-process-cohorts','procedural-coverage','siap-index-coverage','procedural-population-readiness','institutional-lineage-lab'];
 const responses=await Promise.all(endpoints.map(id=>fetch('/api/'+id,{cache:'no-store'})));
 if(!responses[0].ok||!responses[1].ok||!responses[2].ok)throw new Error('Servicio no disponible');
 const results=await Promise.all(responses.map(async(r,i)=>
  r.ok?await r.json():{ok:false,error:'UNAVAILABLE_'+endpoints[i].toUpperCase()}));
 [ui.state,ui.lab,ui.field,ui.atlas,ui.evidence,ui.progress,ui.candidacies,
  ui.nominations,ui.scientificSources,ui.parcanCohorts,ui.proceduralCoverage,
  ui.siapCoverage,ui.populationReadiness,ui.institutionalLineage]=results;
 if(!ui.state.clubs.some(c=>c.id===ui.club))ui.club=ui.state.clubs[0]?.id;
 draw();
}
function selected(){return ui.state.clubs.find(x=>x.id===ui.club);}
function own(){return ui.state.figures.filter(x=>x.owner_id===ui.club);}
function available(){return ui.state.figures.filter(x=>!x.owner_id);}
function past(){return ui.state.rounds.filter(x=>x.is_locked&&x.coverage_state==='SYNTHETIC_COMPLETE').at(-1);}
function upcoming(){return ui.state.rounds.filter(x=>x.coverage_state==='NOT_AVAILABLE').at(-1) || ui.state.rounds.at(-1);}
function actionButton(label,kind,id='',disabled=false){return `<button class="btn small ${kind==='sell'?'danger':kind==='select'?'secondary':''}" data-action="${kind}" data-id="${esc(id)}" ${disabled?'disabled':''}>${esc(label)}</button>`;}
function avatar(f){return `<span class="avatar ${f.id.charCodeAt(2)%3===0?'gold':f.id.charCodeAt(2)%2===0?'blue':''}">${esc(f.id.slice(1))}</span>`;}
function stat(title,value,explanation){return `<article class="card metric"><label>${esc(title)}</label><strong>${esc(value)}</strong><small>${esc(explanation)}</small></article>`;}
function heading(kicker,title,desc){return `<header class="head"><div><p class="eyebrow">${esc(kicker)}</p><h1>${esc(title)}</h1><p>${esc(desc)}</p></div></header>`;}
function row(f,act){return `<div class="listrow">${avatar(f)}<div class="identity"><strong>${esc(f.display_name)}</strong><small>${esc(f.role)} · ${esc(f.group_name)}</small></div><div class="amount">${money(f.price)}</div>${act||''}</div>`;}
function warning(){return `<div class="warning"><strong>ENTORNO EXPERIMENTAL.</strong> Las figuras, transacciones y puntuaciones de fantasy son ficticias. El piloto de votaciones manuales es exploratorio; los CSV de iniciativas oficiales únicamente acreditan metadatos capturados, no resultados históricos ni puntuaciones de personas.</div>`;}
function scienceUrl(route){return '/api/'+route+'?cut='+encodeURIComponent(ui.scienceCut)+'&scenario='+encodeURIComponent(ui.scienceScenario);}
function sciencePublishedLimit(){
 const max=ui.scienceCut==='early'?'2026-10-15T12:00:00Z':'2026-11-01T12:00:00Z';
 return ['2026-09-19T12:00:00Z','2026-10-30T12:00:00Z'].includes(ui.scienceFirstPublic)
    && ui.scienceFirstPublic<=max?ui.scienceFirstPublic:max;
}
function validSciencePayload(x){
 const e=x?.explorer;
 return x?.schema==='pfl.synthetic_scientific_integration_lab.v1'
   && x.evidence_class==='SYNTHETIC_LAB_ONLY'
   && x.cut===ui.scienceCut && x.scenario===ui.scienceScenario
   && x.R5==='STOP_R5' && x.scientific_AB_cycles===0
   && x.release_gates_passed===0 && x.real_corpus_ingestion_allowed===false
   && x.scientific_estimator_admitted===false
   && x.independent_all_received_denominator===null
   && e?.schema==='pfl.synthetic_scientific_explorer.v1'
   && e.admission?.R5==='STOP_R5' && e.admission?.real_denominator===null
   && e.admission?.real_distribution_rights_admitted===false
   && e.catalog?.schema==='pfl.synthetic_distribution_catalog.v1'
   && e.catalog?.witness_distributions_redacted===true
   && Array.isArray(e.catalog.distributions)
   && e.catalog.distributions.every(d=>d.empirical_distribution_admitted===false
      && d.rights_for_requested_purpose_admitted===false)
   && e.observatory?.schema==='pfl.synthetic_bitemporal_observatory.v1'
   && e.observatory.real_actor_identity_verified===false
   && x.warehouse?.b0_b3_witness_sets?.schema==='pfl.synthetic_b0_b3_witness_sets_oracle.v1'
   && x.warehouse.b0_b3_witness_sets.real_rights_admitted===false
   && x.warehouse.b0_b3_witness_sets.real_denominator===null;
}
const REGISTRY_VALID_DAYS=['2026-09-11','2026-09-15','2026-10-10'];
const REGISTRY_FAMILIES=['all','PP04','CHAIN','CHRONICLE'];
const REGISTRY_PUBLICATION=['as_of','2026-09-19T12:00:00Z','2026-10-30T12:00:00Z'];
const REGISTRY_KINDS=['ALL','ACTOR','ORGANIZATION','COMMUNICATION','DECISION','PROCESS','ROLE','EVENT'];
function validRegistryPayload(x,cut,validAt,family,published){
 const at=cut==='early'?'2026-10-15T12:00:00Z':'2026-11-01T12:00:00Z';
 const ceiling=published==='as_of'?at:published;
 const r=x?.registry,s=x?.snapshot,g=s?.graph,m=x?.models;
 const distributionFields=new Set(['public_id','family','revision','descriptor_recipe',
  'sha256_public_descriptor','descriptor_byte_length','issuer_fixture',
  'first_public_at_fixture','captured_at_fixture','real_first_public_at',
  'real_publisher_authenticated','coverage_temporal','quality_gate','provenance',
  'requested_purpose','rights_for_public_display','empirical_admitted','immutable_revision']);
 const graphIsSafe=part=>part===null||(part&&typeof part==='object'
  &&Array.isArray(part.nodes)&&Array.isArray(part.edges)
  &&part.node_count===part.nodes.length&&part.edge_count===part.edges.length
  &&part.amendments_count_as_new_people_or_decisions===false
  &&part.nodes.every(n=>REGISTRY_KINDS.includes(n.kind)
    &&typeof n.label==='string'&&/^S9:(CHAIN|CHRONICLE):NODE_[0-9]{2}$/.test(n.id)
    &&Number.isSafeInteger(n.documentary_revision_count))
  &&part.edges.every(e=>typeof e.kind==='string'
    &&part.nodes.some(n=>n.id===e.from)&&part.nodes.some(n=>n.id===e.to)));
 return x?.schema==='pfl.synthetic_scientific_registry.v1'
  &&x.evidence_class==='SYNTHETIC_LAB_ONLY'
  &&x.cut===cut&&x.as_of===at&&x.valid_at===validAt
  &&x.family===family&&x.published_until===ceiling
  &&x.R5==='STOP_R5'&&x.release_gates_passed===0
  &&x.scientific_ab_cycles===0&&x.independent_denominator===null
  &&x.real_source_ingestion_allowed===false
  &&r?.schema_version===4&&r.persistent===true
  &&Array.isArray(r.migration_history)
  &&r.migration_history.join(',')==='1,2,3,4'
  &&r.source_catalog_kind==='FIXED_PUBLIC_DESCRIPTORS_ONLY'
  &&r.source_bytes_exposed===false&&r.private_source_ids_exposed===false
  &&r.originals_accepted===false&&r.fixture_bytes_sha256_checked_at_read===true
  &&r.recorded_distribution_count===6&&r.internal_uncatalogued_fixture_receipts===1
  &&Array.isArray(r.distributions)&&r.visible_distribution_count===r.distributions.length
  &&r.distributions.every(d=>d&&typeof d==='object'
    &&Object.keys(d).every(k=>distributionFields.has(k))
    &&/^S9:PUBLIC_0[1-6]$/.test(d.public_id)
    &&['PP04','CHAIN','CHRONICLE'].includes(d.family)
    &&(family==='all'||d.family===family)
    &&/^fixture_v[12]$/.test(d.revision)
    &&d.descriptor_recipe==='S9_PUBLIC_SYNTHETIC_DESCRIPTOR_V1'
    &&/^[a-f0-9]{64}$/.test(d.sha256_public_descriptor)
    &&Number.isSafeInteger(d.descriptor_byte_length)&&d.descriptor_byte_length>0
    &&d.first_public_at_fixture<=ceiling&&d.captured_at_fixture<=at
    &&d.real_first_public_at===null&&d.real_publisher_authenticated===false
    &&d.coverage_temporal==='DISTRIBUTION_COVERAGE_UNATTESTED'
    &&d.provenance==='AUTHORED_SYNTHETIC_FIXTURE_NOT_OFFICIAL'
    &&d.requested_purpose==='PUBLIC_AGGREGATE_DISPLAY'
    &&d.rights_for_public_display===false&&d.empirical_admitted===false
    &&d.immutable_revision===true)
  &&s?.knowledge_as_of===at&&s.valid_at===validAt
  &&g?.cross_issuer_links_created===false
  &&graphIsSafe(g.chain)&&graphIsSafe(g.chronicle)
  &&s.episodes?.right_censor_independently_attested===false
  &&s.episodes?.unobserved_is_negative===false
  &&s.episodes?.source_local_all_received_denominator===null
  &&s.pp04?.unplanned_is_a_terminal_negative===false
  &&s.pp04?.independent_crosswalk_between_pan_iaen===false
  &&s.admission_assessments?.schema==='pfl.synthetic_admission_assessments.v1'
  &&Array.isArray(s.admission_assessments.assessments)
  &&s.admission_assessments.assessment_count===s.admission_assessments.assessments.length
  &&s.admission_assessments.source_rows_ingested===0
  &&s.admission_assessments.real_admission_allowed===false
  &&s.admission_assessments.independent_denominator===null
  &&s.admission_assessments.assessments.every(a=>
   /^S9:ASSESS_0[1-8]$/.test(a.assessment_id)
   &&a.status==='ASSESSED_REJECTED_R5'
   &&Array.isArray(a.blockers)&&a.blockers.length>0
   &&Array.isArray(a.history)&&a.history.length===2
   &&a.history[0].status==='REGISTERED'
   &&a.history[1].status==='ASSESSED_REJECTED_R5'
   &&a.rights_for_public_display===false
   &&a.real_original_admitted===false&&a.source_rows_imported===0
   &&/^[a-f0-9]{64}$/.test(a.public_receipt_sha256))
  &&s.synthetic_intake?.schema==='pfl.synthetic_intake_overlay.v1'
  &&Array.isArray(s.synthetic_intake.entries)
  &&s.synthetic_intake.intake_count===s.synthetic_intake.entries.length
  &&Number.isSafeInteger(s.synthetic_intake.registered_count)
  &&Number.isSafeInteger(s.synthetic_intake.validated_count)
  &&Number.isSafeInteger(s.synthetic_intake.rejected_count)
  &&s.synthetic_intake.validated_count+s.synthetic_intake.rejected_count===s.synthetic_intake.intake_count
  &&s.synthetic_intake.history_event_count===2*s.synthetic_intake.intake_count
  &&s.synthetic_intake.logical_decisions_count===0
  &&s.synthetic_intake.source_rows_added_to_canonical===0
  &&s.synthetic_intake.independent_denominator===null
  &&s.synthetic_intake.real_source_ingestion_allowed===false
  &&s.synthetic_intake.source_local_identifiers_exposed===false
  &&s.synthetic_intake.rights_for_public_display===false
  &&s.synthetic_intake.scientific_admission_allowed===false
  &&s.synthetic_intake.real_enrollment_at===null
  &&s.synthetic_intake.temporal_axis==='AUTHOR_STIPULATED_FIXTURE_CLOCKS_NOT_REAL_ENROLLMENT_TIME'
  &&s.synthetic_intake.entries.every(e=>
   /^S9:INTAKE_0[1-4]$/.test(e.intake_id)
   &&typeof e.label==='string'
   &&['SANDBOX_VALIDATED','SANDBOX_REJECTED'].includes(e.status)
   &&['NONE','ISSUER_NOT_ALLOWLISTED'].includes(e.reason_code)
   &&/^fixture_v[12]$/.test(e.revision)
   &&(e.amendment_of===null||/^S9:INTAKE_0[1-4]$/.test(e.amendment_of))
   &&e.quality_gate==='AUTHOR_CLOSED_SANDBOX_ONLY'
   &&typeof e.captured_at_fixture==='string'&&e.captured_at_fixture<=at
   &&typeof e.receipt_first_public_at_fixture==='string'
   &&e.receipt_first_public_at_fixture<=ceiling
   &&typeof e.source_first_public_at_fixture==='string'
   &&typeof e.valid_from==='string'
   &&Array.isArray(e.history)&&e.history.length===2
   &&e.history[0].status==='SANDBOX_REGISTERED'
   &&e.history[1].status===e.status
   &&e.history.every(h=>typeof h.recorded_at_fixture==='string')
   &&e.rights_for_public_display===false
   &&e.empirical_admitted===false
   &&e.real_first_public_at===null&&e.real_issuer_authenticated===false
   &&e.canonical_source_rows_imported===0
   &&/^[a-f0-9]{64}$/.test(e.public_descriptor_sha256))
  &&s.synthetic_intake.graph?.cross_issuer_links_created===false
  &&Array.isArray(s.synthetic_intake.graph?.nodes)
  &&Array.isArray(s.synthetic_intake.graph?.edges)
  &&s.synthetic_intake.graph.node_count===s.synthetic_intake.graph.nodes.length
  &&s.synthetic_intake.graph.edge_count===s.synthetic_intake.graph.edges.length
  &&s.synthetic_intake.graph.revisions_are_not_new_actors_or_decisions===true
  &&s.synthetic_intake.graph.nodes.every(n=>
   /^S9:INTAKE_0[1-4]:N_(ACTOR|ORGANIZATION|PROCESS)$/.test(n.id)
   &&['ACTOR','ORGANIZATION','PROCESS'].includes(n.kind)
   &&typeof n.label==='string'
   &&Number.isSafeInteger(n.documentary_revision_count)
   &&n.logical_identity_count===1)
  &&s.synthetic_intake.graph.edges.every(e=>
   ['AUTHOR_CLOSED_DOCUMENTARY_ASSOCIATION','AUTHOR_CLOSED_DOCUMENTARY_PROCESS_LINK'].includes(e.kind)
   &&s.synthetic_intake.graph.nodes.some(n=>n.id===e.from)
   &&s.synthetic_intake.graph.nodes.some(n=>n.id===e.to))
  &&m?.s3_s7_endpoint==='/api/scientific-integration-lab'
  &&m.computed_from_registry===false
  &&m.separate_existing_python_node_oracle===true
  &&m.empirical_model_admitted===false;
}
function registryCanonicalJson(value){
 return JSON.stringify(value,(_key,item)=>item&&!Array.isArray(item)
  &&typeof item==='object'?Object.fromEntries(Object.keys(item).sort()
   .map(key=>[key,item[key]])):item);
}
async function verifyRegistryReceipt(x){
 const receipt=x?.snapshot_receipt;
 if(!globalThis.crypto?.subtle
    ||receipt?.schema!=='pfl.synthetic_registry_snapshot_receipt.v1'
    ||receipt.canonicalization!=='JSON_UTF8_SORTED_KEYS_COMPACT_V1'
    ||receipt.content_scope!=='CLOSED_PUBLIC_SYNTHETIC_QUERY_ONLY'
    ||receipt.external_authenticity_certified!==false
    ||typeof receipt.canonical_json!=='string'
    ||typeof receipt.bytes!=='number'
    ||!/^[a-f0-9]{64}$/.test(receipt.sha256)
    ||x.snapshot_receipt_sha256!==receipt.sha256)return false;
 const bytes=new TextEncoder().encode(receipt.canonical_json);
 if(bytes.length!==receipt.bytes)return false;
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))
  .map(b=>b.toString(16).padStart(2,'0')).join('');
 if(hash!==receipt.sha256)return false;
 let parsed;
 try{parsed=JSON.parse(receipt.canonical_json);}catch(_){return false;}
 const expected={
  schema:'pfl.synthetic_scientific_registry_snapshot.v1',
  cut:x.cut,as_of:x.as_of,valid_at:x.valid_at,
  family:x.family,published_until:x.published_until,
  distributions:x.registry.distributions,snapshot:x.snapshot
 };
 // Content agreement is necessary even when the independently computed digest matches.
 // The local SHA is NOT proof of publisher identity, first-public date or reuse rights.
 return registryCanonicalJson(parsed)===registryCanonicalJson(expected);
}
function invalidateScientificRegistry(){
 ++ui.scienceRegistryRequest;
 ++ui.scienceRegistryExportGeneration;
 ui.scienceRegistry=null;ui.scienceRegistryLoading=false;ui.scienceRegistryError=null;
}
async function loadScientificRegistry(){
 const ticket=++ui.scienceRegistryRequest;
 ++ui.scienceRegistryExportGeneration;
 const cut=ui.scienceCut,validAt=ui.scienceRegistryValid;
 const family=ui.scienceRegistryFamily,published=ui.scienceRegistryPublished;
 ui.scienceRegistry=null;ui.scienceRegistryError=null;ui.scienceRegistryLoading=true;
 if(ui.guest||ui.tab==='scientific')draw();
 try{
  if(!ui.scientific||ui.scientificLoading||ui.scientificError
     ||!validSciencePayload(ui.scientific))throw new Error('Laboratorio no validado; registro bloqueado');
  const url='/api/scientific-registry?cut='+encodeURIComponent(cut)
   +'&valid_at='+encodeURIComponent(validAt)
   +'&family='+encodeURIComponent(family)
   +'&published_until='+encodeURIComponent(published);
  const response=await fetch(url,{cache:'no-store',credentials:'same-origin'});
  if(!response.ok)throw new Error('Registro persistente rechazado (HTTP '+response.status+')');
  const data=await response.json();
  if(!validRegistryPayload(data,cut,validAt,family,published)
    ||!await verifyRegistryReceipt(data))
   throw new Error('Registro incongruente o SHA de recibo incompatible');
  if(ticket===ui.scienceRegistryRequest&&ui.scienceCut===cut
    &&ui.scienceRegistryValid===validAt&&ui.scienceRegistryFamily===family
    &&ui.scienceRegistryPublished===published&&ui.scientific
    &&validSciencePayload(ui.scientific))ui.scienceRegistry=data;
 }catch(e){
  if(ticket===ui.scienceRegistryRequest)ui.scienceRegistryError=String(e.message);
 }finally{
  if(ticket===ui.scienceRegistryRequest){
   ui.scienceRegistryLoading=false;
   if(ui.guest||ui.tab==='scientific')draw();
  }
 }
}
async function exportScientificRegistry(){
 if(ui.guest&&ui.tab!=='observatory')return;
 const cut=ui.scienceCut,validAt=ui.scienceRegistryValid;
 const family=ui.scienceRegistryFamily,published=ui.scienceRegistryPublished;
 const registryTicket=ui.scienceRegistryRequest,scienceTicket=ui.scienceRequest;
 const exportTicket=++ui.scienceRegistryExportGeneration;
 const data=ui.scienceRegistry;
 if(!data||ui.scienceRegistryLoading||ui.scienceRegistryError
    ||!ui.scientific||ui.scientificLoading||ui.scientificError
    ||!validSciencePayload(ui.scientific)||!globalThis.crypto?.subtle){
  notice('Snapshot S9 no exportable: primero verifica el registro y el Laboratorio',true);
  return;
 }
 try{
  if(!validRegistryPayload(data,cut,validAt,family,published)
     ||!await verifyRegistryReceipt(data))throw new Error('Recibo SHA o contrato S9 inválido');
  // Recheck after the asynchronous digest: a filter A→B→A or a later 503
  // must invalidate even an otherwise perfectly hashed old snapshot.
  if(registryTicket!==ui.scienceRegistryRequest
     ||scienceTicket!==ui.scienceRequest
     ||exportTicket!==ui.scienceRegistryExportGeneration
     ||data!==ui.scienceRegistry||ui.scienceRegistryLoading||ui.scienceRegistryError
     ||cut!==ui.scienceCut||validAt!==ui.scienceRegistryValid
     ||family!==ui.scienceRegistryFamily||published!==ui.scienceRegistryPublished
     ||!ui.scientific||ui.scientificLoading||ui.scientificError
     ||!validSciencePayload(ui.scientific))throw new Error('Corte S9 obsoleto tras cambiar la selección o fallar la recarga');
  const receipt=data.snapshot_receipt;
  const exportBody={
   schema:'pfl.synthetic_scientific_registry_browser_export.v1',
   evidence_class:'SYNTHETIC_LAB_ONLY',
   query:{cut,as_of:data.as_of,valid_at:validAt,family,published_until:data.published_until},
   source_contract:data.schema,
   receipt_schema:receipt.schema,
   snapshot_receipt:receipt,
   R5:'STOP_R5',release_gates_passed:0,scientific_ab_cycles:0,
   external_authenticity_certified:false,rights_for_public_display_admitted:false
  };
  const blob=new Blob([JSON.stringify(exportBody,null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;
  a.download='pfl-s9-registry-'+cut+'-'+validAt+'-'+receipt.sha256.slice(0,12)+'.json';
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  notice('Snapshot S9 sintético exportado; SHA-256 público '+receipt.sha256);
 }catch(e){notice('Exportación S9 bloqueada: '+e.message,true);}
}
async function loadScientific(){
 const ticket=++ui.scienceRequest;
 invalidateScientificRegistry();
 ui.scientific=null;ui.scientificError=null;ui.scientificLoading=true;
 if(ui.guest||ui.tab==='scientific')draw();
 try{
  const response=await fetch(scienceUrl('scientific-integration-lab'),{cache:'no-store',credentials:'same-origin'});
  if(!response.ok)throw new Error('Contrato HTTP '+response.status+'; laboratorio rechazado');
  const data=await response.json();
  if(!validSciencePayload(data))throw new Error('Contrato científico incongruente; vista bloqueada');
  if(ticket===ui.scienceRequest)ui.scientific=data;
 }catch(e){if(ticket===ui.scienceRequest)ui.scientificError=String(e.message);}
 finally{if(ticket===ui.scienceRequest){ui.scientificLoading=false;if(ui.guest||ui.tab==='scientific')draw();}}
}
async function exportScientific(){
 if(ui.guest)return;
 const cut=ui.scienceCut,scenario=ui.scienceScenario;
 const knowledgeTicket=ui.scienceRequest;
 const exportTicket=++ui.scienceExportGeneration;
 const selectedPublication=ui.scienceFirstPublic;
 const publishedUntil=sciencePublishedLimit();
 if(!ui.scientific||ui.scientificLoading||ui.scientificError
    ||!validSciencePayload(ui.scientific)||!globalThis.crypto?.subtle){
  notice('Exportación no verificable en este entorno',true);return;
 }
 try{
  // Snapshot all three server parameters: UI changes must not retarget an in-flight receipt.
  const route='/api/scientific-lab-export?cut='+encodeURIComponent(cut)
   +'&scenario='+encodeURIComponent(scenario)
   +'&published_until='+encodeURIComponent(publishedUntil);
  const response=await fetch(route,{cache:'no-store',credentials:'same-origin'});
  if(!response.ok)throw new Error('Exportación rechazada (HTTP '+response.status+')');
  const receipt=await response.json();
  if(receipt?.schema!=='pfl.synthetic_scientific_export_receipt.v1'
    ||receipt.canonicalization!=='JSON_UTF8_SORTED_KEYS_COMPACT_V1'
    ||receipt.R5!=='STOP_R5'||receipt.empirical_data_exported!==false
    ||!(/^[a-f0-9]{64}$/.test(receipt.sha256))
    ||typeof receipt.canonical_json!=='string')throw new Error('Recibo inválido');
  const bytes=new TextEncoder().encode(receipt.canonical_json);
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))
   .map(b=>b.toString(16).padStart(2,'0')).join('');
  const data=JSON.parse(receipt.canonical_json);
  // A correct SHA alone cannot authorize a download for a now-obsolete UI selection.
  if(hash!==receipt.sha256||bytes.length!==receipt.bytes
     ||knowledgeTicket!==ui.scienceRequest
     ||exportTicket!==ui.scienceExportGeneration
     ||cut!==ui.scienceCut||scenario!==ui.scienceScenario
     ||selectedPublication!==ui.scienceFirstPublic
     ||publishedUntil!==sciencePublishedLimit()
     ||ui.scientificLoading||ui.scientificError||!ui.scientific
     ||!validSciencePayload(ui.scientific)
     ||data?.explorer?.catalog?.publication_filter_fixture!==publishedUntil
     ||!validSciencePayload(data))throw new Error('Recibo obsoleto o contrato SHA/selección incompatible');
  const blob=new Blob([JSON.stringify(receipt,null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;
  a.download='pfl-s8-'+cut+'-'+scenario+'-'+hash.slice(0,12)+'.json';
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  const target=el('science-export-status');if(target)target.textContent='SHA-256 del contenido canónico: '+hash+' · '+bytes.length+' bytes. Recibo y JSON incluidos en la descarga.';
  notice('Recibo SHA-256 verificado y exportado');
 }catch(e){notice('Exportación bloqueada: '+e.message,true);}
}

async function probeScientificAdmission(){
 if(ui.guest)return;
 ui.scienceAdmitting=true;ui.scienceAdmission=null;ui.scienceAdmissionError=null;draw();
 const candidate=ui.scienceCandidate;
 try{
  const response=await fetch('/api/scientific-lab-admission?candidate='+encodeURIComponent(candidate),{cache:'no-store',credentials:'same-origin'});
  if(!response.ok)throw new Error('Rechazo del contrato HTTP '+response.status);
  const result=await response.json();
  if(result.schema!=='pfl.synthetic_distribution_admission_dry_run.v1'
    ||result.evidence_class!=='SYNTHETIC_LAB_ONLY'||result.candidate!==candidate
    ||result.status!=='REJECTED_R5'||result.R5!=='STOP_R5'
    ||result.real_original_admitted!==false||result.source_rows_imported!==0
    ||result.real_person_scoring!==false||!Array.isArray(result.blockers)
    ||!result.blockers.length)throw new Error('Validación de admisión incompatible');
  if(candidate===ui.scienceCandidate)ui.scienceAdmission=result;
 }catch(e){ui.scienceAdmissionError=String(e.message);}
 finally{ui.scienceAdmitting=false;if(ui.tab==='scientific')draw();}
}
function voteBar(r,i){
 const label=`Votación ${i+1}: sí ${r.yes}, no ${r.no}, abstención ${r.abstain}. Total ${r.total}.`;
 const pct=n=>r.total>0?100*n/r.total:0;
 const yes=pct(r.yes),no=pct(r.no),abs=pct(r.abstain);
 return `<div class="statbar"><label>Vot. ${String(i+1).padStart(2,'0')}</label><div class="track"><svg class="vote-stack" viewBox="0 0 100 12" preserveAspectRatio="none" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title><rect class="yes" x="0" y="0" width="${yes}" height="12"></rect><rect class="no" x="${yes}" y="0" width="${no}" height="12"></rect><rect class="abs" x="${yes+no}" y="0" width="${abs}" height="12"></rect></svg></div><b>${r.total}</b></div>`;
}
function insightsPanel(){
 const x=ui.state?.insights?.[ui.club];
 if(!x)return '<p class="footnote">Sin indicadores para el club.</p>';
 const fmt=n=>n===null||n===undefined?'—':Number(n).toFixed(2);
 const val=n=>n===null||n===undefined?'—':count(n);
 const entries=[
  ['C17 · Valor contable',money(x.c17.portfolio_book_value),'Saldo y activos ficticios de precio fijo'],
  ['C18 · Fichajes posibles',val(x.c18.affordable_unowned_count),'Disponibilidad + créditos + huecos'],
  ['C19 · Diversidad de roles',fmt(x.c19.entropy_normalized),'Entropía normalizada de roles inventados'],
  ['C20 · Concentración',fmt(x.c20.hhi),'HHI de grupos ficticios'],
  ['C21 · Valor titulares',x.c21.status==='SAVED_VALID_LINEUP'?money(x.c21.starter_value):'—','No son puntos futuros'],
  ['C22 · Flujo registrado',money(x.c22.cash_delta_bounded),'Historial parcial, no caja inicial'],
  ['C23 · Activos con rotación',val(x.c23.figures_traded_multiple_times),'Historial limitado de compras/ventas'],
  ['C24 · Alineación preparada',esc(x.c24.status),'Jornada pendiente; sin pronóstico'],
  ['C25 · Media de puntos',fmt(x.c25.mean_scored),'Solo jornadas cerradas puntuadas'],
  ['C26 · HHI de aportaciones',fmt(x.c26.hhi),'Solo recibos por figura congelados']
 ];
 return '<section class="card" aria-label="Diez indicadores del club ficticio"><div class="section-title"><h2>Economía y rendimiento · ficción</h2><span>10 CONTROLES LOCALES</span></div><div class="metrics">'
  +entries.map(t=>stat(t[0],t[1],t[2])).join('')
  +'</div><p class="footnote">Todos los indicadores pertenecen a la cuenta local y utilizan únicamente figuras ficticias. Ausente no equivale a cero. No es una medición ni una predicción de política real.</p></section>';
}
function overview(){let s=ui.state,c=selected(),r=past();let points=r?.scores?.[ui.club];return `
${heading('CUADRO DE MANDO / EDICIÓN 00','El parlamento, convertido en tablero.','Un espacio para explorar datos legislativos y experimentar con un juego de gestión transparente. Separación estricta entre evidencia y simulación.')}
<div class="hero"><div><div class="tag">◉ POLITICAL DATA SCIENCE / GAME LAB</div><h2>Más allá del pronóstico.<br>La política como sistema.</h2><p>Explora decisiones institucionales documentadas. Gestiona un equipo ficticio de prueba. El observatorio y la competición están aislados hasta validar datos nominales.</p><button class="btn" data-nav="observatory">EXPLORAR OBSERVATORIO →</button></div><div class="hero-index">15</div></div>
<section class="metrics">${stat('Tu presupuesto',money(c?.credits??0),'Créditos de demostración')}${stat('Tu plantilla',`${own().length} / ${s.roster_limit}`,'Figuras disponibles')}${stat('Última jornada',points===null?'—':`${points} pt`,'Puntos sintéticos')}${stat('Votos observados',count(s.observatory.votes.length),'Transcripción agregada')}</section>
  <div class="cols"><section class="card"><div class="section-title"><h2>Tu equipo</h2><span>${esc(c?.name||'Sin club')}</span></div>${own().length?own().slice(0,4).map(f=>row(f)).join(''):'<p class="empty">Todavía no has fichado figuras.</p>'}<div class="team-actions"><button class="btn secondary" data-nav="club">GESTIONAR PLANTILLA →</button></div></section>
  <section class="card"><div class="section-title"><h2>Estado de investigación</h2><span>AB 3.2.1</span></div><p class="eyebrow text-amber">SIN DESCUBRIMIENTOS EMPÍRICOS CONFIRMADOS</p><p class="help"><strong>Preparación para publicación: NO VERIFICADA.</strong> La existencia de una demo local no equivale a completar los gates ni a demostrar validez científica. Consulta los hitos documentados en la pestaña Progreso.</p><button class="btn secondary" data-nav="progress">CONSULTAR PROGRESO Y GATES →</button><p class="help">Motor local, mercado y jornadas operativos con datos sintéticos. Ingesta nominal, validación independiente, calibración predictiva y despliegue seguros siguen pendientes.</p><p class="footnote">CT2 predicción parlamentaria (corte histórico 25/10/2026): 24/100. CT2 identidad multifuente (28/10/2026): 29/100. Son ramas distintas y escalas ordinales, no probabilidades. No atribuir mérito político a los puntos del juego.</p></section></div>${insightsPanel()}${warning()}`;}
function club(){const c=selected(),f=own(),r=upcoming(),chosen=r.lineups[ui.club]||[];if(ui.picks===null)ui.picks=[...chosen];return `${heading('DIRECCIÓN DEPORTIVA','Mi club','Una plantilla de hasta cinco figuras ficticias. Elige tres titulares para la próxima jornada antes del cierre.')}
<div class="metrics">${stat('Saldo',money(c.credits),'Sin dinero real')}${stat('Fichajes',`${f.length}/5`,'Máximo de plantilla')}${stat('Alineación',`${chosen.length}/3`,'Guardada en servidor')}${stat('Cierre',day(r.lock_at),'Plazo de demostración')}</div>
<div class="cols"><section class="card"><div class="section-title"><h2>Plantilla bajo contrato</h2><span>${f.length} activos</span></div>${f.length?f.map(x=>row(x,actionButton('Vender','sell',x.id))).join(''):'<p class="empty">Ve al mercado para iniciar tu equipo.</p>'}<button class="btn secondary" data-nav="market">IR AL MERCADO →</button></section>
<section class="card"><div class="section-title"><h2>Preparar alineación</h2><span>${esc(r.name)}</span></div><p class="help">Selecciona exactamente tres figuras que pertenezcan a tu club. La alineación guardada no se altera por fichajes posteriores cuando la jornada esté cerrada.</p><div class="lineup-picks">${f.map(x=>`<button class="pick ${ui.picks.includes(x.id)?'selected':''}" data-action="pick" data-id="${esc(x.id)}" aria-pressed="${ui.picks.includes(x.id)}">${esc(x.display_name)} ${ui.picks.includes(x.id)?'✓':'+'}</button>`).join('')||'<span class="empty">Sin figuras</span>'}</div><button class="btn" data-action="save-lineup" ${(ui.picks.length!==3||r.is_locked)?'disabled':''}>GUARDAR TITULARES (${ui.picks.length}/3)</button><p class="footnote">${r.is_locked?'Jornada bloqueada.':'Alineación editable hasta '+day(r.lock_at)+'.'}</p></section></div>`;}
function tradeHistory(s, clubId){
 const records=(Array.isArray(s.trades)?s.trades:[]).filter(x=>x.club_id===clubId).slice(0,40);
 if(!records.length)return '<p class="footnote">Todavía no hay movimientos registrados para este club. El inventario inicial de demostración no es una compra registrada.</p>';
 const rows=records.map(x=>{
   const fig=s.figures.find(f=>f.id===x.figure_id);
   const action=x.action==='buy'?'FICHAJE':x.action==='sell'?'VENTA':'MOVIMIENTO DESCONOCIDO';
   const change=Number.isFinite(x.credits_delta)?(x.credits_delta>0?'+':'')+x.credits_delta:'DESCONOCIDO';
   return `<tr><td>${esc(action)}</td><td>${esc(fig?.display_name||x.figure_id)}</td><td>${esc(change)} CR</td><td>${esc(x.occurred_at)}</td></tr>`;
 }).join('');
 return `<div class="tablewrap"><table><thead><tr><th>Operación</th><th>Figura ficticia</th><th>Créditos</th><th>Fecha del registro</th></tr></thead><tbody>${rows}</tbody></table></div><p class="footnote">Últimos 40 movimientos conservados por la demo. No es un extracto completo ni reconstruye el saldo histórico.</p>`;
}
function market(){const c=selected(),free=available(),f=own();return `${heading('SCOUTING / FICHAJES','Mercado de figuras','Gestiona el capital, decide las incorporaciones y compite por la disponibilidad de activos ficticios. Precios fijos en este prototipo; sin pujas todavía.')}
<div class="metrics">${stat('Créditos libres',money(c.credits),'Capital del club')}${stat('Mercado abierto',count(free.length),'Figuras sin propietario')}${stat('Tamaño plantilla',`${f.length}/5`,'Límite estricto')}${stat('Precio medio',money(Math.round(safeAverage(ui.state.figures.map(f=>f.price)))),'Solo fixture sintético')}</div><div class="grid-players">${ui.state.figures.map(x=>`<article class="card player-card">${x.owner_id?`<span class="chip grey">${x.owner_id===ui.club?'EN TU CLUB':'FICHADO'}</span>`:'<span class="chip">DISPONIBLE</span>'}${avatar(x)}<h3>${esc(x.display_name)}</h3><p>${esc(x.role)} · ${esc(x.group_name)}</p><div class="player-bottom"><div><span>VALOR DE MERCADO</span><strong>${money(x.price)}</strong></div>${x.owner_id===ui.club?actionButton('Vender','sell',x.id):actionButton('Fichar','buy',x.id,!!x.owner_id||c.credits<x.price||f.length>=5)}</div></article>`).join('')}</div><section class="card"><div class="section-title"><h2>Registro de fichajes y ventas</h2><span>CLUB ACTIVO</span></div>${tradeHistory(ui.state,ui.club)}</section><p class="footnote">Precios y atributos son parámetros inventados de la demo; no pretenden valorar personas reales. Todas las compras y ventas quedan registradas en SQLite.</p>`;}
function safeAverage(arr){return arr.length?arr.reduce((a,b)=>a+b,0)/arr.length:0;}
function roundBreakdown(r,clubId){
 const detail=r.score_details?.[clubId];
 if(!detail||detail.status==='NOT_SETTLED')return '<p class="footnote">Desglose no disponible antes del cierre.</p>';
 if(detail.status==='NO_VALID_LINEUP')return '<p class="footnote">Sin alineación válida: puntuación no disponible, no equivale a cero.</p>';
 if(detail.status==='LEGACY_UNAVAILABLE')return '<p class="footnote">Jornada anterior sin desglose histórico verificable; no se reconstruye.</p>';
 if(detail.status!=='FROZEN_COMPONENTS'||!Array.isArray(detail.components))return '<p class="warning">Desglose no verificable.</p>';
 const list=detail.components.map(p=>{
   const figure=ui.state.figures.find(f=>f.id===p.figure_id);
   return `<li>${esc(figure?.display_name||p.figure_id)}: <strong>${esc(p.points)} puntos sintéticos</strong></li>`;
 }).join('');
 return `<details class="score-breakdown"><summary>Desglose de mi club · regla ${esc(detail.rule_version)}</summary><ul>${list}</ul><small>Contribuciones congeladas al cerrar la jornada; no valoran personas reales.</small></details>`;
}
function seasonTable(s){
 const rows=s.season_standings||[];
 if(!rows.length)return '<p class="footnote">Clasificación acumulada todavía no disponible.</p>';
 const body=rows.map(v=>{
  const rank=v.rank===null?'—':v.rank;
  const points=v.total_points===null?'NO DISPONIBLE':count(v.total_points)+' pt';
  const status=v.status==='RANKED'?'Cobertura completa':v.status==='INCOMPLETE_COVERAGE'?'Faltan jornadas puntuables':'Sin jornadas cerradas';
  return `<tr><td>${esc(rank)}</td><td>${esc(v.club_name)}</td><td>${esc(points)}</td><td>${esc(v.rounds_scored)} / ${esc(v.rounds_settled)}</td><td>${esc(status)}</td></tr>`;
 }).join('');
 return `<section class="card"><div class="section-title"><h2>Clasificación acumulada</h2><span>SOLO JORNADAS LIQUIDADAS</span></div><div class="tablewrap"><table><thead><tr><th>Pos.</th><th>Club</th><th>Total</th><th>Jornadas válidas</th><th>Estado</th></tr></thead><tbody>${body}</tbody></table></div><p class="footnote">No se otorga clasificación cuando faltan resultados. Las cifras son del juego ficticio y no valoran políticos reales.</p></section>`;
}
function rounds(){const s=ui.state,r=upcoming(),clock=s.demo_clock;return `${heading('COMPETICIÓN / CALENDARIO','Jornadas y clasificación','El motor contabiliza eventos con límite por categoría y fecha de publicación. Las pruebas muestran solo eventos ficticios.')}${warning()}${seasonTable(s)}
<section class="card"><div class="section-title"><h2>Simulación local</h2><span>${clock.simulated?'RELOJ DE JUEGO ADELANTADO':'RELOJ DE JUEGO'}</span></div><p class="help">Fecha de juego: ${day(clock.now)}. Simular cierra la jornada pendiente, genera eventos ficticios y adelanta solo el reloj de esta demo; no cambia la hora de tu equipo.</p>${r&&r.coverage_state==='NOT_AVAILABLE'?`<button class="btn" data-action="simulate-round" data-id="${esc(r.id)}">SIMULAR Y CERRAR JORNADA</button>`:'<p class="help">No hay jornada pendiente.</p>'}</section>
<div class="two-panels">${s.rounds.map(r=>`<article class="card round-card"><div class="round-flag">${r.is_locked?'● JORNADA CERRADA':'● INSCRIPCIONES ABIERTAS'}</div><h2>${esc(r.name)}</h2><p class="help">${day(r.starts_at)} — ${day(r.ends_at)}<br>Cierre de alineación: ${day(r.lock_at)}</p><div class="tablewrap"><table><thead><tr><th>Club</th><th>Titulares</th><th>Puntos</th></tr></thead><tbody>${s.clubs.slice().sort((a,b)=>(r.scores[b.id]??-1)-(r.scores[a.id]??-1)).map(c=>`<tr><td>${esc(c.name)}</td><td>${count(r.lineups[c.id].length)} / 3</td><td>${r.scores[c.id]===null?'NO DISPONIBLE':count(r.scores[c.id])+' (SINTÉTICOS)'}</td></tr>`).join('')}</tbody></table></div>${roundBreakdown(r,ui.club)}<p class="footnote">${r.coverage_state==='SYNTHETIC_COMPLETE'?'Fixture sintético completo, no institución pública.':'Puntuación desconocida hasta cierre y disponibilidad verificada.'}</p></article>`).join('')}</div>`;}
function labPanel(){const l=ui.lab;if(!l)return '<p class="warning">Laboratorio no disponible</p>';return `<section class="card" aria-label="Laboratorio de indicadores sintéticos"><div class="section-title"><h2>Laboratorio: métricas nominales de demostración</h2><span>VSDS ${l.value_grade.grade}/3 · valor instrumental</span></div><p class="warning"><strong>SINTÉTICO, NO POLÍTICOS REALES.</strong> Datos nominales simulados únicamente para verificar contratos estadísticos, nunca para puntuar figuras del fantasy. No medir calidad democrática.</p><div class="metrics">${stat('Registros sintéticos',count(l.records),'No son votos parlamentarios reales')}${stat('Oportunidades',count(l.opportunities),'Censo sintético por actor')}${stat('Acuerdo observado',Math.round((l.pair_comparison.observed??0)*100)+'%','Una pareja ficticia')}${stat('Acuerdo esperado',Math.round((l.pair_comparison.chance??0)*100)+'%','Comparador por marginales')}</div><div class="tablewrap"><table><thead><tr><th>Actor ficticio</th><th>Expuestos</th><th>Voto explícito</th><th>No-voto declarado</th><th>Desconocido</th><th>Participación</th></tr></thead><tbody>${l.participation.map(x=>`<tr><td>${esc(x.actor)}</td><td>${x.eligible}</td><td>${x.expressed}</td><td>${x.explicit_no_vote}</td><td>${x.unknown}</td><td>${x.participation===null?'DESCONOCIDA':Math.round(x.participation*100)+'%'}</td></tr>`).join('')}</tbody></table></div><p class="footnote">Par analizado: SYN-P01 / SYN-P02 · exposición conjunta ${l.pair_comparison.joint_n} · acuerdo corregido por azar ${Math.round((l.pair_comparison.excess??0)*100)} puntos porcentuales. Descriptivo; no indica influencia interpersonal.</p><p class="footnote">Huella SHA-256 del reporte: ${esc(l.report_sha256)}. VSDS es una escala interna de valor para sociología/data science, independiente del grado científico de novedad AB.</p></section>`;}
function observatory(){const o=ui.state.observatory,rows=o.votes,tot=rows.reduce((a,x)=>a+x.total,0),med=rows.length?[...rows].map(x=>x.total).sort((a,b)=>a-b)[Math.floor(rows.length/2)]:null;return `${heading('CIENCIA DE DATOS / INFRAESTRUCTURA','Observatorio parlamentario','Evidencia documental y análisis descriptivo, separados del videojuego. Primer corte exploratorio: 23 de julio de 2026, Congreso de los Diputados.')}
${warning()}<section class="metrics">${stat('Recuentos',count(rows.length),'Una sesión')}${stat('Votos acumulados',count(tot),'Suma de 20 votaciones, NO personas únicas')}${stat('Mediana por voto',med??'—','Sí + no + abstención')}${stat('Origen','Congreso','Captura visual manual')}</section>
  <div class="cols"><section class="card"><div class="section-title"><h2>Distribución de cada votación</h2><span>Recuentos publicados</span></div><div class="legend"><span><i class="vote-yes"></i> Sí</span><span><i class="vote-no"></i> No</span><span><i class="vote-abs"></i> Abstención</span></div>${rows.slice(0,12).map(voteBar).join('')}<p class="footnote">Solo las primeras 12 de las 20 votaciones. La longitud de cada segmento es proporcional al reparto en su votación, no al tamaño del Congreso.</p></section>
<section class="card"><div class="section-title"><h2>Contrato de evidencia</h2><span>Transparencia</span></div><p class="eyebrow text-amber">AGREGADO, NO NOMINAL</p><p class="help">${esc(o.provenance||'Sin datos fuente incorporados.')}</p><p class="help">No hay rastreo certificado de la fecha de primera publicación ni instantáneas JSON oficiales verificadas. Por ello no se atribuyen votos a personas, no se entrenan modelos políticos y los votos no generan puntos.</p><div class="section-title"><h2>Control de calidad</h2><span>Solo aritmética</span></div><div class="listrow"><div class="identity"><strong>Recuentos ≤ 350</strong><small>Verificación de límite superior, no de ausencia</small></div><span class="amount">${count(rows.filter(v=>v.total<=350).length)}/${rows.length}</span></div><div class="listrow"><div class="identity"><strong>Fuente nominal</strong><small>Necesaria para atribución individual</small></div><span class="amount text-amber">NO VERIFICADA</span></div><p class="footnote">Datos abiertos del Congreso: <a href="https://www.congreso.es/es/opendata/votaciones" target="_blank" rel="noopener noreferrer">portal oficial</a>. Conectar a un payload JSON nominal requiere validar su estructura y hash de origen.</p></section></div>
${labPanel()}
${fieldPanel()}
${evidencePanel()}
<section class="card"><div class="section-title"><h2>Datos agregados registrados</h2><span>${rows.length} observaciones</span></div><div class="tablewrap"><table><thead><tr><th>Votación</th><th>A favor</th><th>En contra</th><th>Abstenciones</th><th>Total</th><th>Categoría</th></tr></thead><tbody>${rows.map((r,i)=>`<tr><td>${String(i+1).padStart(2,'0')} / ${esc(r.id.slice(-3))}</td><td>${r.yes}</td><td>${r.no}</td><td>${r.abstain}</td><td>${r.total}</td><td class="text-amber">TRANSCRIPCIÓN</td></tr>`).join('')}</tbody></table></div></section>`;}
function scientificSourcesPanel(){
 const x=ui.scientificSources||{};
 if(!x.ok)return '<section class="card"><h2>Fuentes históricas españolas</h2><p class="warning">El manifiesto de fuentes no está disponible o no supera el control; no se sustituye con datos sintéticos.</p></section>';
 const items=(x.source_data||[]).map(s=>'<tr><td>'+esc(s.id)+'</td><td>'+count(s.bytes)+'</td><td><code>'+esc(s.sha256.slice(0,16))+'…</code></td><td>'+((s.metadata_audit||{}).rows_in_document===undefined?'Sin auditoría de filas':count(s.metadata_audit.rows_in_document)+' filas administrativas')+'</td></tr>').join('');
 const sources=x.source_data||[];
 const elected=sources.find(s=>s.id==='INTERIOR_CONGRESO_ELECTED')?.metadata_audit||{};
 const results=sources.find(s=>s.id==='INTERIOR_CONGRESO_RESULTS')?.metadata_audit||{};
 const years=Object.keys(elected.rows_by_year||{}).sort();
 const yearsTable=x.source_aggregate_metadata_reproduced&&years.length
 ? '<details><summary>Explorar cobertura documental por año (1977–2023)</summary>'
   +'<p class="footnote">Son frecuencias de filas, no elecciones únicas ni escaños. Los dos ficheros tienen granos diferentes y no deben sumarse como una población política.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Año</th><th>Filas de cargos</th><th>Filas de resultados</th></tr></thead><tbody>'
   +years.map(y=>'<tr><td>'+esc(y)+'</td><td>'+count(elected.rows_by_year[y])+'</td><td>'+count(results.rows_by_year?.[y]??0)+'</td></tr>').join('')
   +'</tbody></table></div></details>'
 : '<p class="warning">La auditoría agregada de cobertura no está disponible o su hash no coincide con el recibo. No se utilizan cifras sustitutas.</p>';
 return '<section class="card" aria-label="Fuentes oficiales con metadatos de captura"><div class="section-title"><h2>Fuentes históricas españolas · captura real</h2><span>NO ADMITIDAS PARA INFERENCIA NOMINAL</span></div>'
 +'<div class="metrics">'+stat('Distribuciones capturadas',count(x.distribution_count),'Originales fuera de Git')+stat('Filas de metadatos',x.source_aggregate_metadata_reproduced?count(x.metadata_rows_scanned):'NO VALIDADO','Dos ficheros: conteos por separado, no personas únicas')+stat('Iniciativas elegibles','DESCONOCIDAS','La fuente electoral no sustituye al Congreso')+'</div>'
 +'<div class="tablewrap"><table><thead><tr><th>Distribución</th><th>Bytes</th><th>SHA-256 (prefijo)</th><th>Estado</th></tr></thead><tbody>'+items+'</tbody></table></div>'
 +yearsTable
 +'<p class="help">Origen: <a href="https://datos.gob.es/es/catalogo/e00003801-resultados-electorales" target="_blank" rel="noopener noreferrer">Ministerio del Interior / datos.gob.es</a>. Capturas del 31/10/2026; bytes reproducidos. El catálogo indica CC BY 4.0. Las filas individuales, los mandatos y las fechas as-of siguen sin validar.</p>'
 +'<div class="warning"><strong>CONTROL CIENTÍFICO.</strong> Los datos electorales no equivalen al universo de procesos políticos. Falta el censo completo de expedientes del Congreso; la fecha HTTP no prueba primera publicación, ni la captura autoriza puntuaciones de políticos reales.</div></section>';
}
function spanishProcessesPanel(){
 const c=ui.parcanCohorts||{};
 if(!c.ok||c.status!=='AUDITED_METADATA_CURRENT_CAPTURE'){
   return '<section class="card"><h2>Procesos políticos · Canarias</h2><p class="warning">Los metadatos de expedientes no están admitidos o su recibo original es distinto del auditado. El observatorio no genera cifras sustitutivas.</p></section>';
 }
 const rows=(c.source_cohorts||[]).map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.initiative_type)+'</td><td>'+esc(s.legislature)+'</td><td>'+esc(s.year)+'</td><td>'+count(s.rows_in_captured_distribution)+'</td><td>'+esc(s.capture_sha256.slice(0,16))+'…</td></tr>').join('');
 const sourceCount=(c.source_cohorts||[]).length;
 const peYears=(c.source_cohorts||[]).filter(s=>s.initiative_type==='PE').map(s=>s.year).sort((a,b)=>a-b);
 const monthRows=(c.creation_monthly_status==='SOURCE_CREATION_MONTHS_AUDITED_ONLY'&&Array.isArray(c.creation_monthly_observed_entries))?c.creation_monthly_observed_entries:[];
 const monthTable=monthRows.length
   ?'<details><summary>Meses con registros observados en las cuatro distribuciones ('+count(monthRows.length)+')</summary>'
    +'<p class="help">Mes de creación declarado en la fotografía actual de origen; no acredita primera publicación histórica. Los meses sin filas no se convierten en meses sin iniciativas, y el recuento no es la población elegible certificada.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Estrato fuente</th><th>Mes indicado</th><th>Filas observadas</th></tr></thead><tbody>'
    +monthRows.map(m=>'<tr><td>'+esc(m.scope)+'</td><td>'+esc(m.source_reported_created_month)+'</td><td>'+count(m.observed_entries)+'</td></tr>').join('')
    +'</tbody></table></div></details>'
   :'';
 const w=ui.proceduralCoverage||{};
 const crossview=w.status==='CONCORDANT_SOURCE_COUNTERS_NOT_CENSUS'
   ?'<details><summary>Comprobación editorial de preguntas escritas: '+count(w.editorial_count_total)+' observadas</summary>'
    +'<p class="help">El Árbol oficial de iniciativas y tres CSV del Parlamento de Canarias coinciden en recuentos para 2024, 2025 y 2026, pero podrían usar la misma base de datos. No se verificó un censo independiente, transiciones ni versiones históricas. La auditoría solo tiene fecha de observación de día; su corte seguro es el día siguiente, no una primera publicación.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Año</th><th>Árbol</th><th>CSV</th><th>Conclusión</th></tr></thead><tbody>'
    +w.source_strata.map(s=>'<tr><td>'+esc(s.year)+'</td><td>'+count(s.publisher_editorial_count)+'</td><td>'+count(s.local_original_rows)+'</td><td>Coinciden; integridad longitudinal no certificada</td></tr>').join('')
    +'</tbody></table></div><p class="footnote">Puertas pendientes: '+esc((w.missing_for_survival||[]).join(' · '))+'. Denominador de riesgo: desconocido.</p></details>'
   :'<p class="footnote">Cotejo editorial independiente del CSV no disponible en este corte o en cuarentena; no se inventan denominadores.</p>';
 return '<section class="card" aria-label="Cohortes documentales de iniciativas autonómicas"><div class="section-title"><h2>Iniciativas parlamentarias · fuentes originales</h2><span>METADATOS REALES · SIN OUTCOMES ADMITIDOS</span></div>'
 +'<div class="metrics">'+stat('Filas capturadas',count(c.observed_rows),sourceCount+' distribuciones observadas, no un censo de la Cámara')+stat('Población elegible','SIN CERTIFICAR','Exhaustividad y estados finales pendientes')+'</div>'
 +'<p class="help">Distribuciones del <a href="https://datos.parcan.es/" target="_blank" rel="noopener noreferrer">Parlamento de Canarias</a>, licencia de catálogo Open Data Commons PDDL. PPL: proposiciones de ley; PE: preguntas con respuesta escrita. Años PE documentados en este corte: '+esc(peYears.join(', ')||'ninguno')+'. Esta sucesión de ficheros no demuestra cobertura exhaustiva, ni publicaciones históricas as-of.</p>'
 +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Clase</th><th>Leg.</th><th>Año</th><th>Filas</th><th>SHA-256 (prefijo)</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
 +monthTable
 +crossview
 +'<p class="footnote">Fecha de la auditoría local: '+esc(c.local_snapshot_audited_at)+'. La API local /api/spanish-process-cohorts?as_of= permite consultar qué estaba documentado por este observatorio en un corte temporal dado. No reconstruye la fecha de primera publicación de cada expediente.</p>'
 +'<div class="warning">No se admitieron estados de aprobación, rechazo o contestación, ni trazas de transiciones fechadas. Fechas de creación no son fechas de primera publicación. Ausencia de una distribución o respuesta no equivale a cero ni a fracaso, y ningún registro puede puntuar a personas reales.</div></section>';
}
function siapIndexPanel(){
 const s=ui.siapCoverage||{};
 if(s.status!=='ONE_INDEX_PAGE_OF_UNCERTIFIED_POPULATION')
  return '<section class="card"><h2>Parlament de Catalunya · índice SIAP</h2><p class="help">Sin metadatos de captura admisibles en el corte solicitado. No se crea una población ficticia de expedientes.</p></section>';
 return '<section class="card" aria-label="Índice legislativo catalán capturado localmente"><div class="section-title"><h2>Parlament de Catalunya · índice SIAP</h2><span>FUENTE REAL · UNA PÁGINA</span></div>'
 +'<div class="metrics">'+stat('Índice capturado',count(s.source_pages_captured)+' / '+count(s.source_index_pages),'Páginas oficiales indexadas en la captura')+stat('Enlaces observados',count(s.observed_links),'Solo primera página; no expedientes censados')+stat('Denominador longitudinal','DESCONOCIDO','Preadmisión, censura, estados y 43 páginas sin verificar')+'</div>'
 +'<p class="help">Página de <a href="https://www.parlament.cat/web/activitat-parlamentaria/iniciatives-legislatives/proposicions-llei/index.html" target="_blank" rel="noopener noreferrer">proposiciones de ley (SIAP)</a>; índice HTML original preservado exclusivamente fuera de Git. SHA-256 prefijo: '+esc(s.original_sha256.slice(0,16))+'… . Conservación: '+esc(s.safe_local_observation_by)+'. Esa fecha es de observación local, nunca primera publicación histórica.</p>'
 +'<div class="warning">No hay historial longitudinal ni desenlaces admitidos. No se fusiona esta familia catalana con las preguntas escritas de Canarias, ni se infieren estados no visibles o permisos de tratamiento personal.</div></section>';
}
function populationReadinessPanel(){
 const p=ui.populationReadiness||{};
 if(p.schema!=='pfl.spanish_procedural_population_readiness.v1'
    ||p.reusable_scientific_cohort!==false||!Array.isArray(p.coverage_gates)
    ||!Array.isArray(p.institutional_sources)){
   return '<section class="card"><h2>Admisión de poblaciones longitudinales</h2><p class="warning">No se dispone de un informe de procedencia admisible. No se inventan expedientes ni transiciones.</p></section>';
 }
 const sources=p.institutional_sources.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.unit)+'</td><td>'+(s.observed_metadata_rows===null||s.observed_metadata_rows===undefined?'Desconocido':count(s.observed_metadata_rows))+'</td><td>'+esc(s.provenance_status)+'</td><td>Sin denominador certificado</td></tr>').join('');
 const gates=p.coverage_gates.map(g=>'<tr><td>'+esc(g.gate)+'</td><td>'+esc(g.scientific_admission)+'</td></tr>').join('');
 const candidates=(Array.isArray(p.documentary_candidate_sources)&&p.documentary_candidate_status==='DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION')
   ?p.documentary_candidate_sources:[];
 const candidatePanel=candidates.length
   ?'<details><summary>Nuevas rutas documentales sin captura autorizada ('+count(candidates.length)+')</summary>'
    +'<p class="help">El catálogo de estas fuentes no es una población de entradas. No se han aceptado sus términos de uso ni descargado sus ficheros originales. No se presentan recuentos de expedientes ni estados políticos.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Activo editorial</th><th>Derechos/acceso</th></tr></thead><tbody>'
    +candidates.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.catalogue_asset)+'</td><td>'+esc(s.access_gate)+'</td></tr>').join('')
    +'</tbody></table></div></details>'
   :'';
 const methods=p.linkage_and_identification||{};
 const selectionPanel=methods.event_by_cut_status==='NOT_IDENTIFIABLE_ON_CURRENT_REAL_SOURCES'
  ?'<details><summary>Identificabilidad de entradas y sesgo de selección</summary>'
    +'<p class="help">Todavía no se ha acreditado un enlace asiento de Registro General → expediente con testigo documental oficial y bytes originales cotejados. Los expedientes sin vínculo no se consideran inadmitidos, y las publicaciones no definen todas las oportunidades de entrada.</p>'
    +'<p class="help">Sin denominador registral independiente, ni estados/eventos completos en un mismo corte, no son identificables tasas ni intervalos numéricos de los desenlaces. Las pruebas de límites existentes son exclusivamente sintéticas, no estimaciones de la política española.</p>'
    +'<p class="footnote">Estado: '+esc(methods.event_by_cut_status)+' · enlace: '+esc(methods.register_to_expediente)+'</p></details>'
  :'';
 const newRegions=p.r8_documentary_status==='R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION'&&Array.isArray(p.r8_regional_routes)
  ?p.r8_regional_routes:[];
 const newNational=p.r8_documentary_status==='R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION'&&Array.isArray(p.r8_national_core_routes)
  ?p.r8_national_core_routes:[];
 const r8Panel=(newRegions.length||newNational.length)
  ?'<details><summary>R8 · nuevas fuentes regionales y consultas del Consejo de Estado</summary>'
    +'<p class="help">Son descripciones documentales, no originales adquiridos ni registros de iniciativas. Las entradas anuales al Consejo de Estado son una población distinta; dictámenes aprobados y asuntos despachados no son el libro completo de consultas recibidas.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Recurso</th><th>Bloqueo de cobertura</th></tr></thead><tbody>'
    +newRegions.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.asset)+'</td><td>'+esc(s.limitation)+'</td></tr>').join('')
    +newNational.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.unit)+'</td><td>'+esc(s.limitation)+'</td></tr>').join('')
    +'</tbody></table></div><p class="footnote">Sin permisos automáticos de descarga, sin denominador independiente, sin eventos ni primera publicación certificada. Corte documental seguro: '+esc(p.r8_audit_safe_by)+'</p></details>'
  :'';
 const integrity=p.retained_original_integrity||{};
 const integrityPanel=integrity.status==='PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED'
  ?'<details><summary>R9 · integridad de originales y derivados conservados</summary>'
    +'<p class="help">Comprobación binaria local anterior: '+count(integrity.official_originals_byte_checked)+' originales capturados y '+count(integrity.private_derivatives_byte_checked)+' derivados privados coincidían por tamaño y SHA-256. No se decodificaron sus registros durante esta auditoría.</p>'
    +'<p class="help">Esto NO acredita censo completo, derechos para nuevos usos, primera disponibilidad histórica ni secuencias de decisiones. La integridad refleja un único control anterior, no una monitorización permanente.</p>'
    +'<p class="footnote">Corte seguro de auditoría local: '+esc(integrity.local_audit_safe_by)+' · API /api/retained-source-integrity?as_of=</p></details>'
  :integrity.status==='INTEGRITY_RECEIPT_QUARANTINED'
   ?'<p class="warning">Recibo de integridad en cuarentena: no se presentan comprobaciones ni conteos.</p>'
   :'';
 const r9Regions=p.r9_documentary_status==='R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED'
  &&Array.isArray(p.r9_regional_highlights)?p.r9_regional_highlights:[];
 const r9National=p.r9_documentary_status==='R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED'
  &&Array.isArray(p.r9_national_highlights)?p.r9_national_highlights:[];
 const r9Panel=(r9Regions.length||r9National.length)
  ?'<details><summary>R9 · Galicia, ILP autonómicas y otros registros institucionales</summary>'
    +'<p class="help">Nuevas fuentes documentales candidatas con límites de cobertura. Las memorias retrospectivas no representan versiones públicas contemporáneas; los asuntos jurisdiccionales, escritos de registro, quejas y acuerdos pertenecen a poblaciones distintas. Ningún nuevo original admitido.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Unidad o problema</th><th>Estado</th></tr></thead><tbody>'
    +r9Regions.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.documentary_limit)+'</td><td>Solo índice editorial</td></tr>').join('')
    +r9National.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.documentary_unit)+'</td><td>Derechos y censo no verificados</td></tr>').join('')
    +'</tbody></table></div>'
    +'<p class="warning">El índice de Galicia presenta encabezados de categorías procesales conocidos antes de congelar A–J. Su reutilización como confirmación de una hipótesis formulada después quedaría contaminada.</p>'
    +'<p class="footnote">Metadatos R9 visibles localmente desde '+esc(p.r9_documentary_safe_by)+'. Sin identificación causal, sin censos independientes y sin identificadores fuente-local publicados.</p></details>'
  :'';
 const r10Regions=p.r10_documentary_status==='R10_DOCUMENTARY_ONLY_NO_RISK_FRAME'
  &&Array.isArray(p.r10_regional_highlights)?p.r10_regional_highlights:[];
 const r10National=p.r10_documentary_status==='R10_DOCUMENTARY_ONLY_NO_RISK_FRAME'
  &&Array.isArray(p.r10_national_highlights)?p.r10_national_highlights:[];
 const r10Panel=(r10Regions.length||r10National.length)
  ?'<details><summary>R10 · fases ILP, discontinuidades de registro y consultas</summary>'
    +'<p class="help">Andalucía: las ILP remitidas a la Junta Electoral están condicionadas a una actuación previa de Mesa; no abarcan todas las entradas. Castilla y León: pendientes a la disolución son una fotografía seleccionada de supervivientes, no una cohorte de todas las iniciativas anteriores.</p>'
    +'<p class="help">Cambio administrativo declarado de canal aGruPa en marzo de 2026: fecha normativa conocida por índice, no verificada mediante replay original. La coexistencia transitoria de registro electrónico y papel es un riesgo de medición, no un efecto político demostrado.</p>'
    +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Unidad o problema</th><th>Bloqueo documental</th></tr></thead><tbody>'
    +r10Regions.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.source_id)+'</td><td>'+esc(s.scope_failure)+'</td></tr>').join('')
    +r10National.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.entry_unit)+'</td><td>'+esc(s.scope_failure)+'</td></tr>').join('')
    +'</tbody></table></div>'
    +'<p class="footnote">CTBG: resolución no necesariamente equivale a reclamación individual; CNMC: documento publicado no equivale a aportación recibida. Derechos y registros originales pendientes. Corte documental seguro: '+esc(p.r10_asof_safe_by)+'.</p></details>'
  :'';
 const r11Candidates=(p.r11_documentary_status==='R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED'
   &&Array.isArray(p.r11_documentary_routes))?p.r11_documentary_routes:[];
 const r11Panel=r11Candidates.length
  ?'<details><summary>R11 · registros municipales, contratación y subvenciones</summary>'
   +'<p class="help">Madrid AIP: el registro público de solicitudes de información y sus agregados históricos son del mismo editor, no dos denominadores independientes. El catálogo declara CC BY 4.0, pero las condiciones generales vinculan por mero uso: no se han aceptado ni descargado originales. Decide Madrid y Canòdrom son ámbitos y permisos distintos.</p>'
   +'<p class="help">Contratación estatal: una revisión ATOM no es una licitación adicional; hay incidencias editoriales de cobertura/actualización documentadas en 2026 que requieren cotejo de origen. BDNS: convocatoria, extracto BOE y concesión son etapas/unidades distintas. Convenios Rioja: varias filas por partes firmantes pueden referirse a un mismo convenio.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Fuente</th><th>Unidad formal</th><th>Problema de delimitación</th><th>Derechos</th></tr></thead><tbody>'
   +r11Candidates.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.institutional_entry_unit)
      +'</td><td>'+esc(s.classification)+'</td><td>'+esc(s.rights_gate)+'</td></tr>').join('')
   +'</tbody></table></div>'
   +'<p class="footnote">Documentación R11 conocida en el archivo local solo desde '+esc(p.r11_documentary_safe_by)+'. Sin censos independientes, sin outcomes examinados, sin first_public_at ni uso de personas identificables. Instrumentos de contabilidad de etapas y reintroducción: solo QA sintética.</p></details>'
  :'';
 const r12Candidates=(p.r12_documentary_status==='R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION'
   &&Array.isArray(p.r12_documentary_routes))?p.r12_documentary_routes:[];
 const r12Panel=r12Candidates.length
  ?'<details><summary>R12 · producción normativa y recursos de contratación</summary>'
   +'<p class="help">Plan Anual Normativo: agenda de instrumentos previstos, no todas las consultas ni actos presentados. Consulta previa y audiencia son etapas distintas; las excepciones legales pueden omitir convocatorias sin que exista un rechazo. Normas en tramitación: índice editorial seleccionado después de entrar en una fase concreta.</p>'
   +'<p class="help">TACRC: el recurso presentado y la resolución publicada no tienen correspondencia uno a uno; resoluciones pueden acumular recursos de otros años. TARCJA: la licencia CC BY 4.0 del CSV de resoluciones no proporciona un libro de recursos recibidos, y no se extiende al PDF de memoria. TEA: la selección doctrinal no equivale a todos los recursos tributarios.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Fuente</th><th>Unidad documental</th><th>Fallo de marco registral</th><th>Permiso</th></tr></thead><tbody>'
   +r12Candidates.map(s=>'<tr><td>'+esc(s.source_id)+'</td><td>'+esc(s.documentary_unit)
      +'</td><td>'+esc(s.risk_frame_limitation)+'</td><td>'+esc(s.specific_rights_scope)+'</td></tr>').join('')
   +'</tbody></table></div><p class="footnote">Relojes: acto, documento, captura de cada revisión y primera disponibilidad pública acreditada NO son equivalentes. El replay de revisiones R12 solo utiliza fuentes ficticias y no verifica vintages de casos reales. Corte documental seguro: '+esc(p.r12_documentary_safe_by)+'.</p></details>'
  :'';
 const r13Candidates=(p.r13_documentary_status==='R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED'
   &&Array.isArray(p.r13_documentary_sources))?p.r13_documentary_sources:[];
 const r13Panel=r13Candidates.length
  ?'<details><summary>R13 · peticiones Senado, solicitudes SAIP y revisión GAIP</summary>'
   +'<p class="help">Senado: petición firmada registrada, expediente 870, informe de la Comisión 871 y dictamen admitido son unidades y etapas distintas; los informes no son peticiones recibidas. No existe un libro íntegro reutilizable de entradas preclasificación acreditado. El registro de peticiones generales AGE es otra institución.</p>'
   +'<p class="help">Catalunya: las solicitudes iniciales SAIP de Generalitat y su sector público (yjpn-vcw8) no son todas las reclamaciones GAIP. El dataset GAIP mpbu-t5zh contiene resoluciones que finalizan reclamaciones y sus actas son reuniones de Pleno, no recursos de entrada. La ficha SAIP anuncia versiones anteriores pero NO hay dos originales capturados legalmente y comparados. Navarra es otra cohorte jurídica y editorial.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Ruta documental</th><th>Unidad</th><th>Selección/incompletitud</th><th>Derechos</th></tr></thead><tbody>'
   +r13Candidates.map(s=>'<tr><td>'+esc(s.source_id)+'</td><td>'+esc(s.unit)
      +'</td><td>'+esc(s.identification_limit)+'</td><td>'+esc(s.rights_gate)+'</td></tr>').join('')
   +'</tbody></table></div>'
   +'<p class="footnote">Dos fechas de acontecimiento y una sola captura de conocimiento no certifican stock real; sin testigo positivo contemporáneo pendiente significa desconocido. Auditoría documental R13 solo desde '+esc(p.r13_documentary_safe_by)+', no fecha de primera publicación del caso. Ensayo stock/flujo únicamente sintético, R5 bloqueado.</p></details>'
  :'';
 const r14Candidates=(p.r14_documentary_status==='R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED'
   &&Array.isArray(p.r14_documentary_routes))?p.r14_documentary_routes:[];
 const r14Saip=(r14Candidates.length&&p.r14_saip_enrichment_not_additive)
   ?p.r14_saip_enrichment_not_additive:null;
 const r14Panel=r14Candidates.length
  ?'<details><summary>R14 · SAIP y registros autonómicos: derechos, vintages y sesgo de selección</summary>'
   +'<p class="help">SAIP Generalitat yjpn-vcw8 ya estaba en R13: R14 añade documentación, NO una segunda cohorte. La interfaz editorial declara 35 columnas y sólo 15 nombres confirmados mediante índice; el total aproximado de 23,4 mil filas no es un censo externo. Restore points del catálogo NO son dos archivos históricos originales y la licencia general catalana puede vincular por mero acceso, sin permiso de cada distribución acreditado.</p>'
   +(r14Saip?'<p class="help">SAIP enriquecida: '+esc(r14Saip.source_declared_columns)+' columnas anunciadas, '
     +esc(r14Saip.column_names_visible_in_index)+' nombres visibles y '
     +esc(r14Saip.column_names_not_verified)+' desconocidos. Versiones editoriales anunciadas: '
     +esc(r14Saip.restore_point_metadata_entries_visible)+'. Originales cotejados: '
     +esc(r14Saip.original_snapshots_compared)+'. Este último cero documenta una ausencia de adquisición, NO ausencia de expedientes.</p>':'')
   +'<p class="help">Ciudad Real: asiento municipal general no identifica una iniciativa política ni acredita el puente hacia expediente. Castilla-La Mancha: estadísticas de acceso general y ambiental, dos familias jurídicas diferentes. Aragón: registro descrito normativamente, contador e informes, pero sin libro individual reutilizable. Un historial de revisiones de catálogo no certifica instantáneas históricas de los originales.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Ruta documental adicional</th><th>Unidad</th><th>Bloqueo de población</th><th>Derechos</th></tr></thead><tbody>'
   +r14Candidates.map(s=>'<tr><td>'+esc(s.source_id)+'</td><td>'+esc(s.documentary_unit)
     +'</td><td>'+esc(s.limitation)+'</td><td>'+esc(s.rights_scope)+'</td></tr>').join('')
   +'</tbody></table></div><p class="footnote">Relojes separados: fecha jurídica, fecha de edición, conocimiento local y primera disponibilidad pública acreditada. Gate documental desde '
   +esc(p.r14_documentary_safe_by)+'. Pendientes, decisiones y denominador real desconocidos; sin acceso a casos ni ciclos AB.</p></details>'
  :'';
 const r16Candidates=(p.r16_documentary_status==='R16_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED'
   &&Array.isArray(p.r16_documentary_routes))?p.r16_documentary_routes:[];
 const r16Panel=r16Candidates.length
  ?'<details><summary>R16 · registro, admisión y revisión: tres familias documentales nuevas</summary>'
   +'<p class="help">Las solicitudes iniciales, las quejas recibidas, los expedientes admitidos y las resoluciones seleccionadas no son el mismo universo. El Síndic valenciano distingue registro y admisión, pero dos instrucciones oficiales discrepan sobre los días de acuse y el momento de asignación del número. CTCyL registra reclamaciones posteriores a la solicitud inicial. CTPDA publica resoluciones seleccionadas de diversas familias, no un padrón de entrada.</p>'
   +'<p class="help">CTPDA anuncia CC BY 4.0 en la ficha de determinadas resoluciones y metadatos de recursos; esta etiqueta NO certifica derechos por cada archivo CSV/ODS/XLS/XML, tratamientos personales ni condiciones de mero uso. Las tres rutas carecen de originales individuales, denominadores independientes, testigos de pendientes y dos vintages auténticos del mismo activo.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Ruta oficial</th><th>Unidad / selección</th><th>Conflicto o límite</th><th>Derechos</th></tr></thead><tbody>'
   +r16Candidates.map(s=>'<tr><td>'+esc(s.source_id)+'</td><td>'+esc(s.documentary_unit)
      +'</td><td>'+esc(s.editorial_conflict)+'</td><td>'+esc(s.rights_scope)+'</td></tr>').join('')
   +'</tbody></table></div>'
   +'<p class="footnote">Conocimiento local de esta auditoría desde '+esc(p.r16_documentary_safe_by)+
     '. Sin identificación de fuente futura antes de ese corte, sin testigos externos de publicación histórica y sin nuevos ciclos empíricos AB.</p></details>'
  :'';
 const r17Candidates=(p.r17_documentary_status==='R17_DOCUMENTARY_ONLY_CONFIDENTIAL_NO_CASE_COHORT'
   &&Array.isArray(p.r17_documentary_routes))?p.r17_documentary_routes:[];
 const r17Panel=r17Candidates.length
  ?'<details><summary>R17 · protección del informante: registro obligatorio no es registro público</summary>'
   +'<p class="help">OAAF Andalucía está obligada jurídicamente a registrar las denuncias externas recibidas, pero ese libro es confidencial y no está disponible como población reutilizable. AIPI registra comunicaciones del canal externo antes de la admisión y asigna un código de seguimiento; no se ha probado su equivalencia con el asiento o el expediente. AVAF recibe denuncias por diversos canales, mientras que la investigación se abre posteriormente de oficio.</p>'
   +'<p class="help">AIPI presenta condiciones de reutilización y aceptación vinculada al mero uso según aviso indexado: no se aceptaron términos ni se accedió a casos. La reforma valenciana de junio de 2025 y el funcionamiento parcial estatal en 2025 rompen comparaciones ingenuas de series. Ningún conjunto aporta N externo de entradas, originales históricos, negativas/pending/censura, derechos por distribución o vínculos oficiales verificados. Las tres rutas son evidencia documental no aditiva, no tres cohortes adicionales.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Fuente documental</th><th>Unidad jurídica</th><th>Bloqueo</th><th>Derechos</th></tr></thead><tbody>'
   +r17Candidates.map(s=>'<tr><td>'+esc(s.institution)+'</td><td>'+esc(s.documentary_unit)
     +'</td><td>'+esc(s.limitation)+'</td><td>'+esc(s.rights_scope)+'</td></tr>').join('')
   +'</tbody></table></div><p class="footnote">Conocimiento documental conservador desde '+esc(p.r17_documentary_safe_by)
   +'. El contraejemplo de selección R17 es exclusivamente sintético; no demuestra persistencia o retroalimentación causal en España. R5 continúa STOP.</p></details>'
  :'';
 const den=p.denominator_evidence||{};
 const denRows=Array.isArray(den.reported_sources)?den.reported_sources:[];
 // A valid historical response may preserve an ISO timezone offset (+01:00)
 // rather than normalize it to Z. Never turn a malformed *historical* cut into
 // an unscoped CURRENT link: that would silently reveal a different snapshot.
 const historicalCut=p.as_of!==null&&p.as_of!==undefined;
 const validCut=(typeof p.as_of==='string'&&p.as_of.length<=42
   &&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:(?:0\d|1[0-3]):[0-5]\d|14:00))$/.test(p.as_of)
   &&Number.isFinite(Date.parse(p.as_of)));
 const scopedCut=!historicalCut?'':validCut?'&amp;as_of='+encodeURIComponent(p.as_of):null;
 const denomPanel=den.schema==='pfl.denominator_evidence_nonadditive.v1'
  ?'<details><summary>R10 · comparación de denominadores y censura no observada</summary>'
   +'<p class="help">La coincidencia entre filas y contador editorial NO certifica todas las entradas. Dos contadores del mismo organismo o base pueden ser reiteraciones; registros, expedientes, dictámenes, acuerdos y escritos no comparten automáticamente unidad de riesgo.</p>'
   +'<div class="tablewrap"><table><thead><tr><th>Fuente verificable</th><th>Institución</th><th>Unidad capturada o descrita</th><th>Observaciones locales</th><th>Bloqueo identificable</th></tr></thead><tbody>'
   +denRows.map(s=>'<tr><td>'+(typeof s.source_id==='string'&&/^[A-Za-z0-9_.:/-]{1,160}$/.test(s.source_id)
      ?scopedCut===null?esc(s.source_id)+' (corte no válido)'
       :'<a href="/api/registration-readiness?source_id='+encodeURIComponent(s.source_id)+scopedCut+'" target="_blank" rel="noopener noreferrer">'+esc(s.source_id)+'</a>'
      :'Identificador no disponible')+'</td><td>'+esc(s.institution)+'</td><td>'+esc(s.observable_unit)+'</td><td>'
      +(s.observed_source_local_items===null?'Desconocidas':esc(count(s.observed_source_local_items)))+'</td><td>'
      +esc(s.principal_identification_block)+'</td></tr>').join('')
   +'</tbody></table></div>'
   +'<p class="footnote">N independiente: desconocido · Terminales: desconocidos · Pendientes: desconocidos · Censurados: desconocidos. Ninguna fila se suma entre instituciones. En cada enlace: /api/registration-readiness?source_id=...&amp;as_of=... reúne registro, estados, derechos por activo, relojes, denominador y enlaces oficiales; conserva el corte as_of de esta vista y no revela fuentes futuras.</p></details>'
  :'';
 return '<section class="card" aria-label="Puertas científicas de población longitudinal"><div class="section-title"><h2>Población longitudinal · admisión científica</h2><span>NO CERTIFICADA</span></div>'
 +'<p class="help">La consistencia de un índice documental, incluso con paginación completa, no prueba que estén presentes todas las iniciativas registradas. Las cifras pertenecen a familias e instituciones diferentes; no deben sumarse.</p>'
 +'<div class="tablewrap"><table><thead><tr><th>Institución</th><th>Unidad observada</th><th>Registros visibles</th><th>Procedencia</th><th>Elegibilidad</th></tr></thead><tbody>'+sources+'</tbody></table></div>'
 +candidatePanel
 +r8Panel
 +r9Panel
 +r10Panel
 +r11Panel
 +r12Panel
 +r13Panel
 +r14Panel
  +r16Panel
	 +r17Panel
 +denomPanel
 +integrityPanel
 +selectionPanel
 +'<details><summary>Requisitos para estimar persistencia, riesgos competitivos y censura ('+count(p.coverage_gates.length)+')</summary><div class="tablewrap"><table><thead><tr><th>Puerta</th><th>Estado</th></tr></thead><tbody>'+gates+'</tbody></table></div></details>'
 +'<p class="footnote">API local /api/procedural-population-readiness?as_of=. El corte indica conocimiento documentado del observatorio, no una primera publicación histórica. Denominador de riesgo desconocido; sin datos personales ni desenlaces admitidos.</p></section>';
}
function institutionalLineagePanel(){
 const p=ui.institutionalLineage||{};
 if(p.schema!=='pfl.synthetic_institutional_lineage.v1'
    ||p.evidence_class!=='SYNTHETIC_LAB_ONLY'
    ||p.legal_identity_authenticated!==false
    ||p.registered_at_risk_certified!==false
    ||p.source_reuse_rights_verified!==false
    ||p.scientific_AB_cycles!==0)
  return '<section class="card"><h2>C15 · identidad institucional</h2><p class="warning">El laboratorio local de identidad no ha superado sus contratos. No se muestran identidades, enlaces ni inferencias.</p></section>';
 const ready=p.status==='SYNTHETIC_LINEAGE_DOCUMENTARY_ONLY';
 const g=ready?p.stage_graph:null;
 const classes=ready&&p.link_classes&&typeof p.link_classes==='object'?p.link_classes:{};
 const fmt=n=>Number.isInteger(n)&&n>=0?count(n):'Desconocido';
 const jsonLink=(cut)=>'/api/institutional-lineage-lab?cut_on=2023-12-31&amp;as_of='+esc(encodeURIComponent(cut));
 const safeStatus=ready?'Coherencia del fixture comprobada':p.status==='SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED'?'Conflicto documental en cuarentena':'Sin afirmaciones disponibles';
 const figures=ready
   ?'<div class="metrics">'+stat('Claves jurídicas activas alegadas',fmt(p.distinct_active_legal_key_claims),'No son entidades reales')
    +stat('Aristas institucionales expresas',fmt(p.complete_explicit_lineage_links),'Alegaciones, no autenticaciones')
    +stat('Registros procesales documentales',fmt(g?.visible_stages?.REGISTRATION),'No es el denominador de entradas')+'</div>'
   :'<p class="warning">El número de identidades, enlaces y etapas se oculta al entrar en cuarentena. Ningún enlace incierto se convierte en negativo ni en decisión.</p>';
 const details=ready?'<details><summary>Separación de cambios institucionales y procedencia</summary><div class="tablewrap"><table><thead><tr><th>Clase alegada</th><th>Enlaces ficticios</th><th>Lectura admisible</th></tr></thead><tbody>'
   +'<tr><td>Renombre, misma clave jurídica</td><td>'+fmt(classes.LEGAL_RENAME_SAME_KEY)+'</td><td>Continuidad jurídica no autenticada</td></tr>'
   +'<tr><td>Fusión (N:1)</td><td>'+fmt(classes.MERGER_PREDECESSOR)+'</td><td>Predecesores distintos, no duplicar entradas</td></tr>'
   +'<tr><td>Escisión (1:N)</td><td>'+fmt(classes.SPLIT_SUCCESSOR)+'</td><td>Sucesores distintos, no inferir causalidad</td></tr>'
   +'<tr><td>Traslado competencial/jurisdiccional</td><td>'+fmt((classes.COMPETENCE_TRANSFER??0)+(classes.JURISDICTION_TRANSFER??0))+'</td><td>No equivale a identidad jurídica</td></tr>'
   +'<tr><td>Referencia puramente documental</td><td>'+fmt(classes.DOCUMENTARY_REFERENCE)+'</td><td>No se promueve por coincidencia nominal</td></tr>'
   +'</tbody></table></div><p class="help">Grupos de reorganización incompletos: '+fmt(p.incomplete_reorganization_groups)+'. Enlaces procesales tipados y exactos: '+fmt(g?.visible_claimed_edges)+'. Dos nombres iguales no crean puente jurídico ni funcional; cualquier conflicto de fuente o cardinalidad se pone en cuarentena.</p></details>':'';
 return '<section class="card" aria-label="Identidad institucional temporal, únicamente sintética">'
   +'<div class="section-title"><h2>C15 · identidad institucional y cambios de competencia</h2><span>LABORATORIO SINTÉTICO · R5 STOP</span></div>'
   +'<p class="help">'+esc(safeStatus)+'. Este panel es un ensayo local de identidad documental, jurídica y funcional, separado del observatorio de fuentes reales. Sus entidades, fechas y enlaces son inventados; no autentica continuidad, reproducción ni autorregulación política.</p>'
   +'<p class="footnote">Modo '+esc(p.snapshot_mode)+' · corte jurídico '+esc(p.cut_on)+' · conocimiento '+esc(p.as_of)+' · calendario '+esc(p.legal_calendar_zone)+'. CURRENT designa la consulta de este ensayo, no una fotografía histórica de una fuente externa.</p>'
   +figures+details
   +'<p class="help">Comparaciones cerradas del mismo fixture: <a href="'+jsonLink('2026-04-01T00:00:00Z')+'" target="_blank" rel="noopener noreferrer">antes del puente documental tardío</a> y <a href="'+jsonLink('2026-08-01T00:00:00Z')+'" target="_blank" rel="noopener noreferrer">después de la constatación local</a>. No contienen registros auténticos.</p>'
   +'<p class="warning">No existe denominador independiente, permiso de distribución, primera publicación histórica certificada, pendientes/censura observados ni A–J admitido. R5 STOP; 0 AB científicos. Los informes de Luhmann, Easton y Deutsch siguen hipótesis rivales, no resultados.</p></section>';
}
function scientificRegistryPanel(){
 const option=(value,label,selected)=>'<option value="'+esc(value)+'" '
  +(value===selected?'selected':'')+'>'+esc(label)+'</option>';
 const validOptions=REGISTRY_VALID_DAYS.map(d=>option(d,d,ui.scienceRegistryValid)).join('');
 const familyNames={all:'Todas las familias',PP04:'PP04 · dos universos',
  CHAIN:'Cadena institucional',CHRONICLE:'Crónica de rol y evento'};
 const familyOptions=REGISTRY_FAMILIES.map(f=>option(f,familyNames[f],ui.scienceRegistryFamily)).join('');
 const pubs=REGISTRY_PUBLICATION.filter(d=>d==='as_of'
  ||d<=(ui.scienceCut==='early'?'2026-10-15T12:00:00Z':'2026-11-01T12:00:00Z'));
 const publishedOptions=pubs.map(v=>option(v,v==='as_of'?'Hasta as_of':v,ui.scienceRegistryPublished)).join('');
 const toolbar='<div class="science-toolbar science-registry-toolbar">'
  +'<label for="science-registry-valid">Vigencia del registro (valid_at)<select id="science-registry-valid">'+validOptions+'</select></label>'
  +'<label for="science-registry-family">Familia de fuente<select id="science-registry-family">'+familyOptions+'</select></label>'
  +'<label for="science-registry-publication">Primera publicación ficticia<select id="science-registry-publication">'+publishedOptions+'</select></label>'
  +'<button class="btn secondary" data-action="science-registry-load" '
  +(!ui.scientific||ui.scienceRegistryLoading?'disabled':'')+'>Consultar registro persistente</button>'
  +'<button class="btn secondary" data-action="science-registry-export" '
  +(!ui.scienceRegistry||ui.scienceRegistryLoading||ui.scienceRegistryError||!ui.scientific||ui.scientificLoading||ui.scientificError?'disabled':'')
  +'>Exportar snapshot S9 + SHA</button></div>';
 const intro='<section class="card science-registry" aria-label="Registro persistente del Observatorio">'
  +'<div class="section-title"><h2>S9 · Registro persistente de fuentes y relaciones</h2>'
  +'<span>SQLITE LOCAL · 100% SINTÉTICO · R5 STOP</span></div>'
  +'<p class="help">Consulta bitemporal a un registro local de distribuciones y hechos ficticios con revisión y SHA verificados en el servidor. '
  +'El identificador mostrado es del descriptor público sintético; no es un ID fuente-local ni un original. '
  +'Ni el registro ni sus revisiones acreditan autoridades reales, censo completo, derechos de distribución o inferencia causal.</p>'
  +toolbar;
 if(ui.scienceRegistryLoading)return intro+'<p role="status" class="help">Comprobando la integridad del registro…</p></section>';
 if(ui.scienceRegistryError)return intro+'<p role="alert" class="warning">'
  +esc(ui.scienceRegistryError)+'. No se muestran datos sustitutivos.</p></section>';
 const p=ui.scienceRegistry;
 if(!p)return intro+'<p class="help" role="status">Pulsa «Consultar registro persistente» para cargar un corte sintético sin originales.</p></section>';
 if(!validRegistryPayload(p,ui.scienceCut,ui.scienceRegistryValid,
    ui.scienceRegistryFamily,ui.scienceRegistryPublished))
  return intro+'<p role="alert" class="warning">El contrato del registro es incompatible; vista bloqueada.</p></section>';
 const tabs={sources:'Distribuciones y revisiones',chain:'Actor, organización y proceso',
  chronicle:'Roles y eventos',episodes:'Estados de episodios',
  admission:'Preadmisión y rechazos',intake:'Incorporación sintética',quality:'Calidad y límites'};
 const navigation='<nav class="science-registry-nav" aria-label="Contenido del registro">'
  +Object.entries(tabs).map(([id,label])=>'<button class="btn secondary '
   +(id===ui.scienceRegistryTab?'registry-active':'')+'" data-action="science-registry-tab" '
   +'data-registry="'+esc(id)+'" aria-pressed="'+(id===ui.scienceRegistryTab?'true':'false')+'">'
   +esc(label)+'</button>').join('')+'</nav>';
 const r=p.registry,s=p.snapshot,graph=s.graph;
 let content='';
 if(ui.scienceRegistryTab==='sources'){
  const rows=r.distributions.map(d=>'<tr><td><code>'+esc(d.public_id)+'</code>'
   +'<small class="science-minor">'+esc(d.family)+' · '+esc(d.revision)+'</small></td>'
   +'<td>'+esc(d.first_public_at_fixture)+'</td><td>'+esc(d.captured_at_fixture)+'</td>'
   +'<td><details><summary>SHA de descriptor público</summary><code class="science-digest">'
   +esc(d.sha256_public_descriptor)+'</code><small class="science-minor">'
   +esc(d.descriptor_byte_length)+' bytes · '+esc(d.quality_gate)+'</small></details></td>'
   +'<td>NO ADMITIDA<small class="science-minor">'
   +esc(d.coverage_temporal)+' · derechos NO acreditados</small></td></tr>').join('');
  content='<p class="help">'+count(r.visible_distribution_count)+' de '
   +count(r.recorded_distribution_count)+' descriptores públicos presentes en la base. '
   +'Las revisiones no son nuevas decisiones, personas o entradas iniciales.</p>'
   +'<div class="tablewrap"><table class="science-table"><thead><tr><th>Descriptor / revisión</th>'
   +'<th>Publicación inventada</th><th>Captura inventada</th>'
   +'<th>Integridad</th><th>Calidad y derechos</th></tr></thead><tbody>'+rows
   +'</tbody></table></div>';
 }else if(ui.scienceRegistryTab==='chain'||ui.scienceRegistryTab==='chronicle'){
  const g=graph[ui.scienceRegistryTab];
  const kinds=REGISTRY_KINDS.filter(k=>k==='ALL'||(g?.nodes||[]).some(n=>n.kind===k));
  const kindButtons='<div class="science-registry-kinds">'+kinds.map(k=>
   '<button class="btn small secondary '+(ui.scienceRegistryKind===k?'registry-active':'')
   +'" data-action="science-registry-kind" data-kind="'+esc(k)+'">'+esc(k)+'</button>').join('')+'</div>';
  if(!g)content='<p class="help">Esta familia no se incluye en el filtro seleccionado; no se construyen enlaces entre emisores.</p>';
  else{
   const shown=g.nodes.filter(n=>ui.scienceRegistryKind==='ALL'||n.kind===ui.scienceRegistryKind);
   const visibleIds=new Set(shown.map(n=>n.id));
   const links=g.edges.filter(e=>visibleIds.has(e.from)&&visibleIds.has(e.to));
   content=kindButtons+'<p class="help">'+count(shown.length)+' nodos tipados · '
    +count(links.length)+' relaciones explícitas del mismo emisor; 0 enlaces externos autenticados.</p>'
    +'<div class="science-graph"><div class="science-graph-nodes">'
    +shown.map(n=>'<span class="science-node"><small>'+esc(n.kind)+'</small><strong>'
      +esc(n.label)+'</strong><small>Revisiones documentales: '
      +count(n.documentary_revision_count)+'</small></span>').join('')
    +'</div><ul class="science-relations">'+links.map(e=>'<li>'
      +esc(shown.find(n=>n.id===e.from)?.label)+' → '
      +esc(shown.find(n=>n.id===e.to)?.label)+' <small>'
      +esc(e.kind)+'</small></li>').join('')+'</ul></div>';
  }
 }else if(ui.scienceRegistryTab==='episodes'){
  const e=s.episodes,pp=s.pp04;
  content='<div class="metrics">'
   +stat('Proceso de cadena',e.chain_process_state,'Pendencia, aprobación y censura son estados distintos')
   +stat('Inadmisión explícita',count(e.explicit_negative_documented),'Solo testigo sintético de etapa')
   +stat('Pendencia documentada',count(e.pending_documented_not_negative),'Nunca equivale a negativa')
   +stat('Aprobación explícita',count(e.explicit_approval_documented),'No es un estimando empírico')
   +'</div><p class="help">PP04, universo fuente-local separado: planificadas aprobadas '
   +esc(pp.included_planned_approved)+', pendientes '+esc(pp.included_pending_not_negative)
   +', NO INCLUIDAS '+esc(pp.not_included_source_local_not_negative)
   +'. No se interpreta una no inclusión como rechazo ni como episodio censurado.</p>'
   +'<p class="warning">Censura derecha independiente: NO acreditada. Denominador inicial independiente: DESCONOCIDO.</p>';
 }else if(ui.scienceRegistryTab==='admission'){
  const a=s.admission_assessments;
  const rows=a.assessments.map(x=>'<tr><td><code>'+esc(x.assessment_id)
   +'</code><small class="science-minor">'+esc(x.candidate)
   +' · '+esc(x.revision)+'</small></td><td>'
   +x.history.map(h=>'<div>'+esc(h.status)+' · '+esc(h.recorded_at)+'</div>').join('')
   +'</td><td>'+esc(x.status)+'</td><td>'
   +x.blockers.map(b=>'<div>'+esc(b)+'</div>').join('')
   +'</td><td><details><summary>Recibo público de evaluación</summary><code class="science-digest">'
   +esc(x.public_receipt_sha256)+'</code></details></td></tr>').join('');
  content='<p class="help">'+count(a.assessment_count)
   +' evaluaciones ficticias visibles; registro y evaluación son etapas separadas. '
   +'Estas pruebas comparten un único identificador de distribución en el laboratorio S8: '
   +'NO son ocho fuentes, ocho decisiones ni ocho revisiones documentales. '
   +'Ninguna ha superado R5 ni autoriza publicación.</p>'
   +'<div class="tablewrap"><table class="science-table"><thead><tr>'
   +'<th>Evaluación</th><th>Historial sintético</th><th>Resultado</th>'
   +'<th>Bloqueos</th><th>Integridad</th></tr></thead><tbody>'+rows
   +'</tbody></table></div><p class="warning">'
   +'La admisión científica y los derechos externos siguen NO acreditados; '
   +'la primera publicidad es un dato del fixture, no una fecha histórica.</p>';
 }else if(ui.scienceRegistryTab==='intake'){
  const intake=s.synthetic_intake,graph=intake.graph;
  const rows=intake.entries.map(x=>'<tr><td><code>'+esc(x.intake_id)
   +'</code><small class="science-minor">'+esc(x.label)+' · '+esc(x.revision)
   +'</small></td><td>'+esc(x.status)+'<small class="science-minor">'
   +esc(x.reason_code)+'</small></td><td>'+x.history.map(h=>'<div>'
   +esc(h.status)+' · '+esc(h.recorded_at_fixture)+'</div>').join('')
   +'</td><td>'+esc(x.receipt_first_public_at_fixture)
   +'<small class="science-minor">Fuente ficticia: '+esc(x.source_first_public_at_fixture)+'</small>'
   +'<small class="science-minor">Captura ficticia: '+esc(x.captured_at_fixture)
   +'</small></td><td><details><summary>SHA del descriptor</summary>'
   +'<code class="science-digest">'+esc(x.public_descriptor_sha256)
   +'</code></details></td></tr>').join('');
  const nodes=graph.nodes.map(n=>'<li><strong>'+esc(n.kind)+'</strong> '
   +esc(n.label)+' <small>Revisiones documentales: '
   +count(n.documentary_revision_count)+'</small></li>').join('');
  const links=graph.edges.map(e=>'<li>'+esc(graph.nodes.find(n=>n.id===e.from)?.label)
   +' → '+esc(graph.nodes.find(n=>n.id===e.to)?.label)
   +' <small>'+esc(e.kind)+'</small></li>').join('');
  content='<p class="help">'+count(intake.intake_count)+' incorporaciones ficticias registradas en el ledger aislado; '
   +count(intake.validated_count)+' validadas SOLO para el sandbox de ingeniería, '
   +count(intake.rejected_count)+' rechazadas por controles internos. '
   +'No existe ingesta de originales externos ni admisión científica o licencia de difusión.</p>'
   +'<div class="tablewrap"><table class="science-table"><thead><tr>'
   +'<th>Referencia pública</th><th>Control sandbox</th><th>Historial</th>'
   +'<th>Primera publicidad inventada</th><th>Huella SHA</th></tr></thead><tbody>'
   +rows+'</tbody></table></div><p class="help">Grafo fuente-local del sandbox: '
   +count(graph.nodes.length)+' nodos · '+count(graph.edges.length)
   +' relaciones; las revisiones no son nuevas decisiones o personas.</p>'
   +'<ul class="science-relations">'+nodes+links+'</ul>'
   +'<p class="warning">La incorporación se realiza exclusivamente con fixtures internos autorizados '
   +'por CLI local. El Observatorio consulta, no acepta archivos ni promueve declaraciones de derechos. '
   +'Las marcas temporales de estas incorporaciones son imaginarias.</p>';
 }else{
  content='<div class="metrics">'
   +stat('Migración del esquema',r.schema_version,'Base SQLite del fixture, no fuente administrativa')
   +stat('Distribuciones públicas',r.recorded_distribution_count,'Una fuente interna queda oculta')
   +stat('Recibos internos ocultos',r.internal_uncatalogued_fixture_receipts,'No pasan a HTTP')
   +stat('Puertas R5',p.release_gates_passed+' / 6','Bloqueadas')
   +'</div><p class="help">Integridad de bytes del fixture al consultar: '
   +esc(r.fixture_bytes_sha256_checked_at_read)+'. Derechos para PUBLIC_AGGREGATE_DISPLAY: '
   +'NO acreditados. El registro persistente no alimenta los oráculos S3/S7 y no acredita '
   +'independencia de fuente, resultado causal ni puntuaciones de personas reales.</p>';
 }
 return intro+navigation+'<p class="footnote">as_of='+esc(p.as_of)+' · valid_at='
  +esc(p.valid_at)+' · publicación inventada hasta '+esc(p.published_until)
  +' · familia '+esc(p.family)+' · hash público ≠ SHA de bytes internos.</p>'
  +content+'</section>';
}
function scientificLaboratory(){
 const intro=heading('INFRAESTRUCTURA / CIENCIA DE DATOS SOCIALES','Laboratorio científico · S8','Exploración ejecutable de fuentes sintéticas, cortes temporales, rivales B0/B3, sensibilidad S3 y conjuntos de testigos S7.');
 const control=`<section class="science-toolbar card" aria-label="Controles del laboratorio"><label for="science-cut">Conocimiento (as_of)<select id="science-cut"><option value="early" ${ui.scienceCut==='early'?'selected':''}>15 oct 2026 · temprano</option><option value="late" ${ui.scienceCut==='late'?'selected':''}>1 nov 2026 · tardío</option></select></label><label for="science-first-public">Publicación del fixture hasta<select id="science-first-public"><option value="as_of" ${ui.scienceFirstPublic==='as_of'?'selected':''}>Fecha de conocimiento</option><option value="2026-09-19T12:00:00Z" ${ui.scienceFirstPublic==='2026-09-19T12:00:00Z'?'selected':''}>19 sep 2026</option>${ui.scienceCut==='late'?'<option value="2026-10-30T12:00:00Z" '+(ui.scienceFirstPublic==='2026-10-30T12:00:00Z'?'selected':'')+'>30 oct 2026</option>':''}</select></label><label for="science-scenario">Prueba de robustez<select id="science-scenario"><option value="baseline" ${ui.scienceScenario==='baseline'?'selected':''}>Base</option><option value="rights_spoof" ${ui.scienceScenario==='rights_spoof'?'selected':''}>Derechos fingidos</option><option value="privacy_probe" ${ui.scienceScenario==='privacy_probe'?'selected':''}>Sondeo de privacidad</option></select></label><button class="btn secondary" data-action="science-reload">Recalcular</button><button class="btn" data-action="science-export" ${!ui.scientific||ui.scientificLoading?'disabled':''}>Exportar JSON + SHA</button></section>`;
 const stop='<p class="warning"><strong>R5 STOP · 0/6 puertas.</strong> El ensayo no contiene expedientes o actores políticos españoles reales. No hay denominador independiente, autenticación oficial, derechos por finalidad, crosswalk externo ni primera publicación histórica acreditados.</p>';
 if(ui.scientificLoading)return intro+control+stop+'<section class="card" role="status">Ejecutando la paridad Python–Node…</section>';
 if(ui.scientificError)return intro+control+stop+'<section class="card" role="alert"><h2>Servicio científico rechazado</h2><p class="warning">'+esc(ui.scientificError)+'</p><p>Sin sustituciones automáticas.</p></section>';
 const p=ui.scientific;
 if(!p)return intro+control+stop+'<section class="card"><button class="btn" data-action="science-reload">Cargar el laboratorio</button></section>';
 if(!validSciencePayload(p))return intro+control+stop+'<p class="warning">Contratos no verificables.</p>';
 const e=p.explorer,w=p.warehouse,s3=w.partial_identification_oracle,b=w.b0_b3_observational_equivalence,s7=w.b0_b3_witness_sets;
 const cases=s7.sets_by_knowledge_cut?.[ui.scienceCut]?.sets;
 if(!Array.isArray(cases)||cases.length!==20||b?.all_published_source_sha_and_typed_revisions_equal!==true)return intro+control+stop+'<p class="warning">Falta el oráculo S7/B0/B3 de veinte conjuntos. Vista rechazada.</p>';
 const labels={INCONCLUSIVE:'No concluyente',B0_ONLY:'Solo B0',B3_ONLY:'Solo B3',NEITHER:'Ninguno',CONFLICT:'Conflicto',INADMISSIBLE:'Inadmisible'};
 const publicationLimit=sciencePublishedLimit();
 const visibleDistributions=e.catalog.distributions.filter(d=>d.first_public_at_fixture<=publicationLimit&&d.captured_at_fixture<=p.as_of);
 const metrics='<section class="metrics">'+stat('Distribuciones visibles',visibleDistributions.length+' / '+e.catalog.visible_distribution_count,'Filtro editorial ficticio y corte de conocimiento')+stat('Conjuntos S7',cases.length,'Escenarios alternativos, no casos reales')+stat('Modelos rivales','B0 / B3','Mismo conjunto publicado')+stat('Puertas científicas','0 / 6','R5 STOP')+'</section>';
 const compare=`<section class="card"><div class="section-title"><h2>B0 calendario frente a B3 selección</h2><span>EQUIVALENCIA OBSERVACIONAL HIPOTÉTICA</span></div><div class="science-rivals"><article><strong>B0 · calendario</strong><p>E3 no tiene decisión terminal al corte tardío. La publicación se estipula por calendario.</p><p>N = ${esc(b.hypothetical_all_received_by_mechanism.B0_CALENDAR)} · cobertura publicada ${esc(b.hypothetical_publication_coverage.B0_CALENDAR)}</p></article><article><strong>B3 · selección</strong><p>E3 fue rechazado ficticiamente el 10/10 y quedó sin publicar.</p><p>N = ${esc(b.hypothetical_all_received_by_mechanism.B3_SELECTION_PUBLICATION)} · cobertura publicada ${esc(b.hypothetical_publication_coverage.B3_SELECTION_PUBLICATION)}</p></article></div><p class="footnote">Las dos hipótesis generan idénticas revisiones, entidades y procesos publicados. La igualdad del N supuesto no distingue mecanismos. E2 pendiente y E4 censurado no constituyen rechazos.</p></section>`;
 const sens=s3?`<section class="card"><h2>S3 · identificación parcial bajo selección</h2><p class="help">Las cuotas observadas pasan de ${esc(s3.observed_positive_share.before)} a ${esc(s3.observed_positive_share.after)}, con razón de selección supuesta ${esc(s3.selection_ratio_positive_to_negative.lower)}–${esc(s3.selection_ratio_positive_to_negative.upper)} (no odds ratio).</p><div class="metrics">${stat('Antes',s3.prevalence_bounds.before.lower+' a '+s3.prevalence_bounds.before.upper,'Intervalo condicional')}${stat('Después',s3.prevalence_bounds.after.lower+' a '+s3.prevalence_bounds.after.upper,'Intervalo condicional')}${stat('Cambio',s3.change_bounds.lower+' a '+s3.change_bounds.upper,'No causal')}</div><p class="footnote">Sin supuesto de selección: cambio compatible ${esc(s3.without_ratio_restriction.trivial_change_closure.lower)} a ${esc(s3.without_ratio_restriction.trivial_change_closure.upper)}. Negativos binarios inventados, no decisiones administrativas.</p></section>`:'<section class="card"><h2>S3 · identificación parcial</h2><p class="warning">Aún no conocida en el corte temprano. No se adelanta la evidencia tardía.</p></section>';
 const counts=Object.keys(labels).map(k=>labels[k]+': '+cases.filter(c=>c.status===k).length).join(' · ');
 const setRows=cases.map(c=>`<tr><td><code>${esc(c.case)}</code></td><td>${esc(labels[c.status]||'RECHAZADO')}</td><td>${esc((c.compatible_mechanisms||[]).join(' / ')||'Sin adjudicar')}</td><td>${esc(c.reason)}</td><td><details><summary>${(c.witness_admissibility||[]).length} testigos</summary>${(c.witness_admissibility||[]).map(t=>'<p class="footnote"><strong>'+esc(t.case)+'</strong> · '+esc(t.status)+' · '+esc(t.reason)+'</p>').join('')||'<p class="footnote">Ninguno</p>'}${c.contradiction?'<p class="footnote">Conflicto: '+esc(c.contradiction.kind)+'; '+count(c.contradiction.evidence_rows_retained)+' declaraciones conservadas.</p>':''}</details></td></tr>`).join('');
 const sets=`<section class="card"><div class="section-title"><h2>S7 · conjuntos de testigos diferenciales</h2><span>SEIS ESTADOS · 20 ESCENARIOS</span></div><p class="help">${esc(counts)}</p><p class="help"><strong>NEITHER</strong>: un testigo sintético admisible refuta ambos DGP estipulados; no es fallo HTTP. <strong>CONFLICT</strong>: dos testimonios incompatibles quedan retenidos sin elegir. <strong>INADMISSIBLE</strong>: evidencia insuficiente, no resolución científica.</p><div class="tablewrap"><table class="science-table"><thead><tr><th>Conjunto</th><th>Estado</th><th>Compatibilidad</th><th>Justificación</th><th>Testigos</th></tr></thead><tbody>${setRows}</tbody></table></div></section>`;
 const validDays=['2026-09-11','2026-09-15'];const valid=validDays.includes(ui.scienceValid)?ui.scienceValid:validDays[1];
 const chronDays=['2026-09-15','2026-10-10'];const chronValid=chronDays.includes(ui.scienceChronicleValid)?ui.scienceChronicleValid:chronDays[1];
 const graph=e.observatory.typed_graph_by_valid_day?.[valid],chron=e.observatory.chronicle_by_valid_day?.[chronValid];
 const graphHTML=graph&&Array.isArray(graph.nodes)&&Array.isArray(graph.edges)?`<div class="science-graph"><div class="science-graph-nodes">${graph.nodes.map(n=>'<span class="science-node"><small>'+esc(n.kind)+'</small><strong>'+esc(n.label)+'</strong></span>').join('')}</div><ul class="science-relations">${graph.edges.map(r=>'<li>'+esc(graph.nodes.find(n=>n.id===r.from)?.label||'')+' → '+esc(graph.nodes.find(n=>n.id===r.to)?.label||'')+' <small>'+esc(r.kind)+'</small></li>').join('')}</ul></div>`:'<p class="warning">Grafo no verificable</p>';
 const time=`<section class="card"><div class="section-title"><h2>Observatorio bitemporal sintético</h2><span>AS_OF ≠ VALID_AT</span></div><div class="science-toolbar"><label for="science-valid">Vigencia · cadena institucional<select id="science-valid">${validDays.map(d=>'<option value="'+d+'" '+(d===valid?'selected':'')+'>'+d+'</option>').join('')}</select></label><label for="science-chronicle">Vigencia · roles y eventos<select id="science-chronicle">${chronDays.map(d=>'<option value="'+d+'" '+(d===chronValid?'selected':'')+'>'+d+'</option>').join('')}</select></label></div><p class="help">Conocimiento ${esc(p.as_of)}; vigencia de la cadena ${esc(valid)}. Actor, organización, comunicación, proceso y decisión se proyectan mediante identificadores tipados; las dos cronologías no comparten un crosswalk real.</p>${graphHTML}<p class="footnote">Proceso ${esc(graph?.process_state)} · revisiones conocidas de una comunicación ${esc(graph?.communication_documentary_revisions)} · comunicaciones lógicas ${esc(graph?.logical_communications)} · 0 rechazos inferidos.</p>${chron?'<p class="science-chronicle">Crónica '+esc(chronValid)+': rol '+esc(chron.role_observation_state)+' · '+esc(chron.event_documentary_revisions_known)+' revisiones de evento · '+esc(chron.logical_events_after_typed_amendment)+' evento lógico · versión '+esc(chron.selected_revision)+'.</p>':'<p class="warning">Crónica no disponible</p>'}</section>`;
 const sourceRows=visibleDistributions.map(d=>`<tr><td><code>${esc(d.distribution_id)}</code><small class="science-minor">${esc(d.family)} · ${esc(d.revision_or_asset_kind)}</small></td><td>${esc(d.issuer_fixture)}</td><td>${esc(d.captured_at_fixture)}</td><td>${esc(d.first_public_at_fixture)}</td><td><details><summary>SHA y calidad</summary><code class="science-digest">${esc(d.sha256)}</code><p>${count(d.byte_length)} bytes · ${esc(d.quality_gate)}</p><p>Cobertura temporal: ${esc(d.coverage_temporal?.state)}</p></details></td><td><strong>NO ADMITIDA</strong><small class="science-minor">${esc(d.admissibility_reason)}</small></td></tr>`).join('');
 const sources=`<section class="card"><div class="section-title"><h2>Catálogo de fuentes sintéticas</h2><span>PROCEDENCIA, CALIDAD Y DERECHOS</span></div><p class="help">Filtro de primera publicación <em>inventada</em> ≤ ${esc(publicationLimit)}, sin exceder as_of ni adelantar capturas. Cobertura temporal de cada distribución: <strong>no acreditada</strong>. La validación SHA solo prueba bytes del fixture local; no demuestra integridad externa, completitud o derechos. Los recibos adversariales S7 permanecen ocultos.</p><div class="tablewrap"><table><thead><tr><th>Distribución / revisión</th><th>Emisor ficticio</th><th>Captura inventada</th><th>Publicación inventada</th><th>SHA / calidad / cobertura</th><th>Admisibilidad y derechos</th></tr></thead><tbody>${sourceRows}</tbody></table></div></section>`;
 const exportPanel=`<section class="card"><h2>Exportación y reproducción</h2><p class="help">La descarga incluye el contenido JSON canónico, su recibo SHA-256 y los metadatos de canonicalización. WebCrypto verifica el SHA del contenido antes de permitir la descarga. Una deriva entre Node/Python devuelve 503, sin resultados sustitutivos.</p><p id="science-export-status" class="science-digest footnote" role="status">Exportación pendiente; datos sintéticos exclusivamente.</p><p class="footnote">${esc(e.admission.R5)} · ${p.scientific_AB_cycles} ciclos científicos · sin permiso de distribución externa acreditado.</p></section>`;
 const candidateOptions={baseline:'Fixture coherente (sin autoridad real)',sha_spoof:'SHA incompatible',issuer_spoof:'Emisor no autorizado',rights_missing:'Sin propósito declarado',first_public_missing:'Sin publicación declarada',crosswalk_missing:'Sin enlace tipado',denominator_missing:'Sin registro completo',coverage_missing:'Cobertura incompleta'};
 const admission=ui.scienceAdmission;
 const candidatePanel=`<section class="card"><div class="section-title"><h2>Admisión de una distribución nueva · dry-run</h2><span>SIEMPRE R5 STOP</span></div><p class="help">Ensaya ocho variantes cerradas de un único documento enteramente inventado. El validador coteja SHA, emisor, fecha, crosswalk, universo y alcance de derechos; nunca importa archivos ni habilita datos reales.</p><div class="science-toolbar"><label for="science-candidate">Candidato sintético<select id="science-candidate">${Object.entries(candidateOptions).map(([v,label])=>'<option value="'+v+'" '+(v===ui.scienceCandidate?'selected':'')+'>'+esc(label)+'</option>').join('')}</select></label><button class="btn secondary" data-action="science-probe" ${ui.scienceAdmitting?'disabled':''}>Comprobar incorporación</button></div>${ui.scienceAdmissionError?'<p role="alert" class="warning">'+esc(ui.scienceAdmissionError)+'</p>':admission&&admission.candidate===ui.scienceCandidate?'<p class="warning"><strong>'+esc(admission.status)+'</strong> · '+admission.blockers.length+' bloqueos; '+count(Object.values(admission.checks).filter(Boolean).length)+' de '+count(Object.keys(admission.checks).length)+' coherencias internas del fixture.</p><details><summary>Detalle de bloqueos y validaciones</summary><p class="help">'+admission.blockers.map(esc).join(' · ')+'</p><div class="tablewrap"><table><tbody>'+Object.entries(admission.checks).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td>'+(v?'PASA (SOLO FIXTURE)':'FALLA')+'</td></tr>').join('')+'</tbody></table></div></details>':'<p class="footnote" role="status">Selecciona un escenario y ejecuta el validador de admisión.</p>'}</section>`;
 return intro+control+stop+metrics+compare+sens+sets+time+scientificRegistryPanel()+sources+candidatePanel+exportPanel;
}
function evidencePanel(){const x=ui.evidence||{};
const t=x.entities_by_type||{};
const groups=Object.keys(t).sort().map(k=>esc(k)+': '+count(t[k])).join(' · ');
return populationReadinessPanel()+institutionalLineagePanel()+spanishProcessesPanel()+siapIndexPanel()+scientificSourcesPanel()+`<section class="card"><div class="section-title"><h2>Universo político ampliado</h2><span>FUENTE NO CERTIFICADA</span></div>
<p class="help">Partidos, coaliciones, agrupaciones, plataformas y personas con roles públicos documentados no necesitan escaños para ser representables. Datos actuales: solo fixtures del laboratorio.</p>
${stat('Entidades de ejemplo',count(x.entities||0),'Ficticias')}${stat('Eventos de ejemplo',count(x.events||0),'No son influencia')}
<p class="help">${groups||'Sin registro de entidades verificable'}</p>
<div class="warning">0 personas reales verificadas. Sin puntuaciones de mérito político. Las fuentes oficiales están inventariadas, pero sus ficheros originales y las fechas as-of necesitan comprobación.</div>
</section>`;}
function fieldPanel(){const f=ui.field||{};
const imported=f.mode==='USER_SUPPLIED_CSV_UNCERTIFIED';
const status=imported?'CSV LOCAL · SIN CERTIFICAR':f.mode==='FIELD_REPORT_REJECTED'?'INFORME RECHAZADO':'SIN CSV NOMINALES IMPORTADOS';
const g=f.group_audit;const gh=imported&&g?`<div class="metrics">${stat('Filas por grupo',count(g.group_rows),'Recuentos por votación y grupo')}${stat('Grupos registrados',count(g.group_labels),'Etiquetas históricas sin verificar')}${stat('Conciliación de grupo',g.aggregate_consistent?'COINCIDE':'INCOMPLETA','Solo consistencia entre CSV')}</div><p class="footnote">Votos nominales y grupos: ${g.nominal_group_complete?'consistencia interna':'faltantes o discrepancias detectadas'} · ${count(g.nominal_group_undercounts)} filas de grupo subcontadas. No mide disciplina partidista.</p>`:'';return `<section class="card" aria-label="Auditoría CSV nominal — solo lectura"><div class="section-title"><h2>Auditoría CSV · Fuentes nominales</h2><span>VSDS 1/3</span></div><p class="eyebrow text-amber">${esc(status)}</p><p class="help">${esc(f.message||'Origen no disponible.')}</p>${imported?`<div class="metrics">${stat('Filas nominales',count(f.n_nominal_rows),'Datos de archivo aportado')}${stat('Votaciones',count(f.n_votations),'Sin censo completo acreditado')}${stat('No vota',count(f.explicit_no_vote),'Únicamente elecciones explícitas')}</div><p class="footnote">Reconciliación: ${f.reconciliation_complete?'los recuentos coinciden':'no hay coincidencia completa'}. Esto NO certifica autenticidad.</p>`:''}${gh}<p class="footnote">Sin puntos para personas reales. Importación offline: python -m politics_fantasy.field_cli. Atribución y licencia: <a href="https://congresoabierto.org/datos/" target="_blank" rel="noopener noreferrer">Congreso Abierto (CC BY 4.0)</a>. Requiere auditoría externa.</p></section>`;
}
function officialNominationAtlas(){const a=ui.nominations||{};
if(!a.ok)return `<section class='card'><h2>Más circunscripciones · BOE original</h2><p class='warning'>No se dispone de un documento verificado: ${esc(a.error||'sin fuente')}. No se crean datos sustitutos.</p></section>`;
const lines=(a.provinces||[]).map(p=>`<details class='card'><summary><strong>${esc(p.province)}</strong> · ${count(p.n_candidacies)} candidaturas${p.requires_non_proclamation_review?' · revisión documental pendiente':''}</summary><p class='help'>Identificadores electorales de 2023, no del Registro de Partidos.</p><p class='help'>${p.lists.map(x=>esc(x.acronym)).join(' · ')}</p></details>`).join('');
return `<section class='card'><div class='section-title'><h2>Fuente original · otras circunscripciones</h2><span>BOE 2023 · parcial</span></div><div class='metrics'>${stat('Secciones extraídas',count(a.n_provinces),'de '+count(a.detected_provincial_sections)+' detectadas')}${stat('Listas electorales',count(a.n_candidacies),'No partidos legales')}${stat('Secciones pendientes',count(a.unresolved_provincial_sections),'Numeración incompleta')}${stat('Avisos adicionales',count(a.extracted_with_review_notices),'Candidaturas no proclamadas')}</div><p class='warning'>Cobertura incompleta y estrictamente histórica. No se atribuyen escaños, militancia ni influencia. Las provincias pendientes no se completan por suposición.</p><p class='help'>${boeSourceLink(a.source_url)}; huella SHA-256 ${esc(a.original_sha256)}.</p>${lines}</section>`;
}
function officialListPanel(){const c=ui.candidacies||{};
if(!c.ok)return `<section class='card'><h2>Candidaturas BOE · original</h2><p class='warning'>Sin fuente válida disponible: ${esc(c.error||'sin información')}</p></section>`;
return `<section class='card'><div class='section-title'><h2>Candidaturas proclamadas · fuente original</h2><span>Albacete · Congreso 2023</span></div>
<div class='metrics'>${stat('Listas proclamadas',count(c.proclaimed_candidacy_lists),'Solo Albacete')}${stat('Partidos legales comprobados',count(c.verified_legal_parties),'No procede inferirlos')}${stat('Personas evaluadas',count(c.people_joined),'Ninguna')}</div>
<p class='help'>Siglas publicadas: ${(c.lists||[]).map(x=>esc(x.acronym)).join(' · ')}.</p>
<p class='warning'>Una lista electoral no equivale necesariamente a un partido inscrito. Proclamación no demuestra militancia, escaño posterior o influencia.</p>
<p class='footnote'>Fuente ${boeSourceLink(c.source_url)}; SHA-256 original ${esc(c.source_sha256)}. Extracción institucional de una circunscripción, no un registro nacional de personas.</p></section>`;}
function atlas(){const a=ui.atlas||{};if(!a.ok)return heading('DATOS REALES · HISTÓRICOS','Atlas electoral',a.error||'Catálogo histórico no disponible.');
const rows=(a.labels||[]).slice().sort((x,y)=>x.name.localeCompare(y.name,'es'));

return `${heading('ELECCIONES GENERALES / JULIO 2023','Atlas electoral · todas las candidaturas','59 etiquetas electorales del archivo secundario, incluidas opciones que recibieron votos sin obtener escaños. No es el Registro de Partidos ni una comparación de calidad política.')}
${officialListPanel()}
${officialNominationAtlas()}
<div class="warning"><strong>FUENTE SECUNDARIA, HISTÓRICA.</strong> Las etiquetas pueden referirse a partidos, coaliciones u otras candidaturas. Ausencia de escaños no es ausencia de influencia. No se atribuyen posiciones ideológicas ni puntuaciones.</div>
<div class="metrics">${stat('Etiquetas electorales',count(a.electoral_labels),'Archivo provincial de 2023')}${stat('Con votos, sin escaños',count(a.labels_with_votes_no_congress_seat),'No implica ausencia de actividad')}${stat('Con escaños',count(a.labels_with_congress_seat),'Representación solo para esta elección')}${stat('Celdas conciliadas JEC',count(a.jec_documentary_check?.aggregate_comparisons??0),'312 cifras BOE original contrastadas')}${stat('Siglas de coalición',count(a.jec_documentary_check?.official_coalition_acronyms_matched??0),'Coincidencia única, no identidad jurídica')}</div>
<section class="card"><div class="section-title"><h2>Catálogo de opciones electorales</h2><span>Orden alfabético</span></div>
<p class="help">Votos y escaños son recuentos históricos del dataset; no son una valoración, pronóstico ni una clasificación de influencia. Las etiquetas no se han conciliado individualmente con el registro jurídico de partidos.</p>
<div class="tablewrap"><table><thead><tr><th>Etiqueta publicada</th><th>Votos registrados</th><th>Escaños</th><th>Estado descriptivo</th><th>Referencia JEC</th></tr></thead><tbody>${rows.map(x=>`<tr><td>${esc(x.name)}</td><td>${count(x.votes)}</td><td>${count(x.seats)}</td><td>${esc(x.seat_status==='VOTES_WITHOUT_CONGRESS_SEAT'?'Votos sin escaño':x.seat_status==='CONGRESS_SEAT_RECORDED'?'Con representación':'Sin votos registrados')}</td><td>${esc(x.coalition_acronym_documented?'Sigla de coalición JEC documentada':x.official_national_votes_documentarily_checked?'Total contrastado BOE':'Sin cotejo nominal de etiqueta')}</td></tr>`).join('')}</tbody></table></div>
<p class="footnote">Fuente: <a href="https://github.com/anerodata/data-elecciones-congreso-espana/blob/main/202307.csv" target="_blank" rel="noopener noreferrer">anerodata, 202307.csv</a>, instantánea con SHA Git ${esc(a.source_blob_sha)}. Agregados contrastados documentalmente con <a href="https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907" target="_blank" rel="noopener noreferrer">JEC / BOE 2023</a> (52 circunscripciones × 6 magnitudes); las siglas no prueban identidad legal o pertenencia a una coalición. Cifras BOE originales contrastadas y validación adicional con <a href="https://datos.gob.es/es/catalogo/e00003801-resultados-electorales" target="_blank" rel="noopener noreferrer">Ministerio del Interior</a>.</p></section>`;}

function progress(){
 const p=ui.progress||{};
 if(!p.ok)return heading('ESTADO DEL PROYECTO','Progreso no disponible','El manifiesto versionado de alcance no ha superado la validación.');
 const fmt=x=>Number(x).toLocaleString('es-ES',{minimumFractionDigits:1,maximumFractionDigits:1});
 const bar=(pct)=>{const x=Math.max(0,Math.min(100,Number(pct)||0));return `<progress class='scope-progress' max='100' value='${x}' aria-label='Progreso ${fmt(x)} por ciento'>${fmt(x)} %</progress>`};
 const evidenceUrl=x=>'https://github.com/GalexY3/politics-fantasy-league/blob/main/'+encodeURI(x);
 const lanes=p.tracks.map(t=>`<details class='card scope-detail'><summary class='scope-summary'><strong>${esc(t.name)}</strong> · ${fmt(t.progress_pct)} % · peso ${fmt(t.weight)} %</summary><div class='scope-track'>${bar(t.progress_pct)}</div><p class='help'>Aporta ${fmt(t.contribution_pp)} puntos al resultado global; ${t.milestones.length} hitos definidos.</p><div class='tablewrap'><table><thead><tr><th>Hito</th><th>Madurez</th><th>Evidencia</th></tr></thead><tbody>${t.milestones.map(m=>`<tr><td>${esc(m.name)}</td><td>${esc(String(m.maturity))}/5</td><td><a href='${esc(evidenceUrl(m.evidence_ref))}' target='_blank' rel='noopener noreferrer'>Referencia</a></td></tr>`).join('')}</tbody></table></div></details>`).join('');
 const critical=p.release_blockers.map(t=>`<li>${esc(t)}</li>`).join('');
 return `${heading('MADUREZ POR ALCANCE · REV. '+p.revision,'Progreso del proyecto','Estimación trazable de hitos cumplidos en un alcance explícito. No es la probabilidad de terminar ni el nivel VSDS/CT2.')}
 <section class='card'><div class='section-title'><h2>Índice global</h2><span>${esc(p.scope_id)}</span></div><p class='progress-total'>${fmt(p.progress_pct)} %</p>${bar(p.progress_pct)}<p class='help'>${p.track_count} vías · ${p.milestone_count} hitos · alcance fijado el ${esc(p.review_date)}. La fórmula pondera las vías y la madurez demostrada de sus hitos.</p><p class='footnote'>Escala: 0 ausente; 1 diseñado; 2 implementado; 3 probado localmente; 4 validado en campo documental; 5 operativo verificado. Es una adjudicación revisable, nunca una tasa objetiva de trabajo restante.</p></section>
 <section class='card'><h2>Preparación de lanzamiento</h2><p class='warning'>El proyecto NO está listo para publicación multiusuario ni para puntuar figuras políticas reales.</p><ul>${critical}</ul><p class='help'>Progreso y preparación de lanzamiento son métricas diferentes: una puerta crítica pendiente puede impedir operar aunque el índice global aumente.</p></section>
 <h2>Detalle de las sublíneas y sus fuentes</h2>${lanes}<section class='card'><h2>Cuando crece el alcance</h2><p class='help'>Cada revisión conserva el indicador anterior y separa los puntos ganados por trabajo de los puntos ganados o perdidos por una ampliación/reponderación de objetivos. Ejemplo histórico hipotético, calculado sobre la revisión 1 (no sobre el porcentaje actual): añadir cobertura municipal nacional completa sin construirla cambiaba 33,725 % a 32,330 % (−1,395 puntos de alcance, 0 de trabajo). El avance actual de la revisión 2 incorpora trabajo verificado y sigue sin ampliar el alcance.</p></section>`;
}
const pages={overview,club,market,rounds,observatory,scientific:scientificLaboratory,atlas,progress};
const GUEST_TABS=['observatory','scientific'];
function navigationMode(mode){
 el('navigation').hidden=mode==='login';
 document.querySelectorAll('[data-tab]').forEach(n=>{
  n.hidden=mode==='guest'&&!GUEST_TABS.includes(n.dataset.tab);
  const active=mode!=='login'&&n.dataset.tab===ui.tab;
  n.classList.toggle('active',active);
  if(active)n.setAttribute('aria-current','page');else n.removeAttribute('aria-current');
 });
 el('club-select').hidden=mode!=='account';
 el('guest-exit').hidden=mode!=='guest'||ui.scienceOnly;
}
function guestScienceView(){
 const p=ui.scientific,e=p.explorer,w=p.warehouse;
 const cases=w?.b0_b3_witness_sets?.sets_by_knowledge_cut?.[ui.scienceCut]?.sets;
 const b=w?.b0_b3_observational_equivalence;
 const states=['INCONCLUSIVE','B0_ONLY','B3_ONLY','NEITHER','CONFLICT','INADMISSIBLE'];
 if(!Array.isArray(cases)||cases.length!==20
    ||!cases.every(c=>c&&states.includes(c.status)&&typeof c.case==='string')
    ||b?.all_published_source_sha_and_typed_revisions_equal!==true)
  return '<section class="card" role="alert"><p class="warning">El contrato de escenarios S7 no es verificable. Vista bloqueada.</p></section>';
 const counts=states.map(s=>'<tr><td>'+esc(s)+'</td><td>'+count(cases.filter(c=>c.status===s).length)+'</td></tr>').join('');
 const rows=cases.map(c=>'<tr><td><code>'+esc(c.case)+'</code></td><td>'+esc(c.status)
  +'</td><td>'+esc((c.compatible_mechanisms||[]).join(' / ')||'Sin adjudicar')
  +'</td><td>'+esc(c.reason)+'</td></tr>').join('');
 return heading('CONSULTA ABIERTA · S8','Laboratorio científico',
  'Comparación de mecanismos, censura y conjuntos de testigos con datos íntegramente sintéticos.')
  +'<section class="science-toolbar card" aria-label="Corte de laboratorio para visitantes">'
  +'<label for="science-cut">Conocimiento (as_of)<select id="science-cut"><option value="early" '
  +(ui.scienceCut==='early'?'selected':'')+'>15 oct 2026</option><option value="late" '
  +(ui.scienceCut==='late'?'selected':'')+'>1 nov 2026</option></select></label>'
  +'<label for="science-scenario">Escenario sintético<select id="science-scenario">'
  +['baseline','rights_spoof','privacy_probe'].map(v=>'<option value="'+v+'" '
  +(ui.scienceScenario===v?'selected':'')+'>'+esc(v)+'</option>').join('')+'</select></label>'
  +'<button class="btn secondary" data-action="guest-reload">Actualizar consulta</button></section>'
  +'<section class="metrics">'+stat('Corte conocido',ui.scienceCut==='early'?'Temprano':'Tardío','Reloj del fixture')
  +stat('Escenarios S7',cases.length,'Conjuntos estipulados')
  +stat('Distribuciones',e.catalog.distributions.length,'Sin originales publicados')
  +stat('Puertas R5','0 / 6','Admisión detenida')+'</section>'
  +'<section class="card"><h2>B0 y B3 · mecanismos rivales</h2>'
  +'<p class="help">Los mecanismos de calendario (B0) y selección de publicación (B3) son observacionalmente equivalentes en los materiales publicados por este fixture. La ausencia de un resultado no demuestra rechazo.</p>'
  +'<p class="footnote">Corte: '+esc(p.as_of)+' · escenario: '+esc(p.scenario)+' · sin denominador independiente ni derechos de difusión empírica acreditados.</p>'
  +'<div class="tablewrap"><table><thead><tr><th>Estado S7</th><th>Conjuntos</th></tr></thead><tbody>'+counts+'</tbody></table></div></section>'
  +'<section class="card"><h2>Testigos diferenciales sintéticos</h2>'
  +'<p class="help">INADMISSIBLE significa evidencia insuficiente. CONFLICT conserva testimonios incompatibles. NEITHER indica incompatibilidad con ambos mecanismos estipulados, nunca una refutación empírica.</p>'
  +'<div class="tablewrap"><table><thead><tr><th>Conjunto</th><th>Estado</th><th>Mecanismos compatibles</th><th>Justificación del fixture</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>';
}
function guestView(){
 const banner='<p class="warning"><strong>VISITA CIENTÍFICA · SOLO LECTURA · R5 STOP.</strong> '
  +'Exploración sintética sin cuenta ni datos de clubes. No hay evidencia real admitida, puntuaciones políticas ni predicciones validadas.</p>';
 if(ui.scientificError||ui.scienceRegistryError)
  return banner+heading('CONSULTA BLOQUEADA','Datos científicos no disponibles',
   'El servidor rechazó el contrato o la verificación de integridad. No se muestran resultados antiguos.')
   +'<section class="card" role="alert"><p class="warning">'
   +esc(ui.scientificError||ui.scienceRegistryError)+'</p><button class="btn secondary" data-action="guest-reload">Reintentar consulta</button></section>';
 if(ui.scientificLoading||ui.scienceRegistryLoading||!ui.scientific||!ui.scienceRegistry)
  return banner+heading('CONSULTA ABIERTA','Cargando Observatorio y Laboratorio',
   'Validando los contratos científicos y el recibo SHA-256 antes de mostrar resultados.')
   +'<section class="card" role="status">Consulta en curso…</section>';
 if(!validSciencePayload(ui.scientific)
    ||!validRegistryPayload(ui.scienceRegistry,ui.scienceCut,ui.scienceRegistryValid,
      ui.scienceRegistryFamily,ui.scienceRegistryPublished))
  return banner+'<section class="card" role="alert">Contratos científicos incompatibles; vista bloqueada.</section>';
 if(ui.tab==='observatory')return banner
  +heading('CONSULTA ABIERTA · S9','Observatorio documental sintético',
   'Fuentes, versiones, grafos y cronologías con trazabilidad temporal de un registro local cerrado.')
  +scientificRegistryPanel();
 return banner+guestScienceView();
}
function drawGuest(){
 navigationMode('guest');
 el('account-name').textContent='VISITANTE';
 el('account-logout').hidden=true;
 el('crumb').textContent=ui.tab==='observatory'?'OBSERVATORIO · VISITANTE':'LABORATORIO · VISITANTE';
 el('content').innerHTML=guestView();
}
async function reloadGuest(){
 if(!ui.guest)return;
 const previous=ui.scienceRequest;
 await loadScientific();
 // A return to login or a newer request invalidates the old response.
 if(!ui.guest||ui.scienceRequest!==previous+1||!ui.scientific)return;
 await loadScientificRegistry();
}
async function enterGuest(){
 if(ui.state||ui.session)return;
 ui.guest=true;ui.tab='observatory';ui.picks=null;
 ui.scienceScenario='baseline';ui.scienceCut='late';
 ui.scienceRegistryFamily='all';ui.scienceRegistryValid='2026-09-15';
 ui.scienceRegistryPublished='as_of';ui.scienceRegistryTab='sources';
 drawGuest();
 await reloadGuest();
}
function authScreen(){
 ui.guest=false;++ui.scienceRequest;++ui.scienceExportGeneration;
 invalidateScientificRegistry();ui.scientific=null;ui.scientificError=null;
 ui.scientificLoading=false;ui.state=null;ui.picks=null;ui.csrf=null;ui.session=null;
 el('account-logout').hidden=true;el('account-name').textContent='';
 el('club-select').innerHTML='';navigationMode('login');
 el('crumb').textContent='CUENTA LOCAL';
 el('content').innerHTML=`<section class="card" aria-label="Acceso a la demostración ficticia">
 <div class="section-title"><h2>Cuenta local del prototipo</h2></div>
 <p>Los clubes, fichajes, alineaciones y jornadas de cada cuenta se guardan en una base independiente.
 Esta pantalla es exclusivamente para pruebas locales; no publiques el servidor en internet.</p>
 <form id="auth-form" autocomplete="on">
 <label>Usuario (3–24 caracteres, letras, números y _)<input name="username" required pattern="[a-zA-Z][a-zA-Z0-9_]{2,23}" maxlength="24" autocomplete="username"></label>
 <label>Contraseña (12 caracteres mínimo)<input name="password" type="password" required minlength="12" maxlength="128" autocomplete="current-password"></label>
 <div class="auth-actions">
 <button class="btn" type="submit" name="intent" value="login">Iniciar sesión</button>
 <button class="btn secondary" type="submit" name="intent" value="register">Crear cuenta</button>
 </div></form><p id="auth-error" class="help" role="status"></p></section>
 <section class="card" aria-label="Acceso científico como visitante">
 <div class="section-title"><h2>Explorar sin cuenta</h2><span>SOLO LECTURA</span></div>
 <p class="help">Consulta el Observatorio y el Laboratorio científicos con datos sintéticos y recibos de integridad. No accederás a clubes, mercado, jornadas ni información de cuentas.</p>
 <button class="btn secondary" type="button" data-action="guest-enter">Entrar al Observatorio y Laboratorio</button></section>`;
}
async function bootstrap(){
 const response=await fetch('/api/session',{cache:'no-store',credentials:'same-origin'});
 if(response.status===404){return refresh();} // Explicit legacy handler test mode.
 if(response.status===401){
  // The isolated --science-only server declares itself without creating a game
  // session. An ordinary unauthorized account server still shows the login.
  try{
   const mode=await response.json();
   if(mode?.science_only===true&&mode.authenticated===false){
    ui.scienceOnly=true;
    return enterGuest();
   }
  }catch(_){/* Missing/malformed mode declarations do not open a guest session. */}
 }
 if(!response.ok){authScreen();return;}
 const session=await response.json();
 if(!session.authenticated){return refresh();} // Legacy test-mode endpoint.
 ui.session=session.username;ui.csrf=session.csrf;ui.club='demo';ui.picks=null;
 el('account-name').textContent=session.username;el('account-logout').hidden=false;
 await refresh();
}

function draw(){if(ui.guest){drawGuest();return;}if(!ui.state)return;navigationMode('account');let c=el('club-select'); c.innerHTML=ui.state.clubs.map(x=>`<option value="${esc(x.id)}" ${x.id===ui.club?'selected':''}>${esc(x.name)}</option>`).join('')+'<option value="__new">+ Crear club…</option>';el('crumb').textContent=({'overview':'VISIÓN GENERAL','club':'MI CLUB','market':'MERCADO','rounds':'JORNADAS','observatory':'OBSERVATORIO','scientific':'LABORATORIO CIENTÍFICO','atlas':'ATLAS ELECTORAL','progress':'PROGRESO DEL PROYECTO'})[ui.tab];el('content').innerHTML=pages[ui.tab]();}
async function perform(kind,id){if(kind==='pick'){ui.picks=ui.picks.includes(id)?ui.picks.filter(x=>x!==id):ui.picks.length<3?[...ui.picks,id]:ui.picks;draw();return;}
 if(ui.guest)return;
try{const c=selected();if(['buy','sell'].includes(kind)){await call('/api/'+kind,{club_id:c.id,figure_id:id});notice(kind==='buy'?'Fichaje registrado.':'Venta registrada.');}else if(kind==='save-lineup'){await call('/api/lineup',{club_id:c.id,round_id:upcoming().id,figures:ui.picks});notice('Alineación guardada en SQLite.');}else if(kind==='simulate-round'){await call('/api/simulate-round',{round_id:id});ui.picks=null;notice('Jornada ficticia simulada y cerrada.');}await refresh();}catch(e){notice(e.message,true);}}
document.addEventListener('submit',async e=>{
 if(e.target.id!=='auth-form')return;
 e.preventDefault();
 if(ui.guest)return;
 const fields=new FormData(e.target);
 const username=String(fields.get('username')||'');
 const password=String(fields.get('password')||'');
 const register=e.submitter?.value==='register';
 try {
  if(register)await call('/api/register',{username,password});
  const a=await call('/api/login',{username,password});
  ui.session=a.username;ui.csrf=a.csrf;ui.club='demo';ui.picks=null;
  el('account-name').textContent=a.username;el('account-logout').hidden=false;
  await refresh();notice(register?'Cuenta creada y sesión iniciada.':'Sesión iniciada.');
 } catch(err){el('auth-error').textContent=String(err.message);}
});
document.addEventListener('click',async e=>{
 if(e.target.closest('#guest-exit')&&ui.guest){
  if(ui.scienceOnly)return;
  ui.tab='overview';authScreen();return;
 }
 if(e.target.closest('#account-logout')){
  if(ui.guest)return;
  try{await call('/api/logout',{});}catch(_){/* A failed logout cannot authorize access. */}
  authScreen();return;
 }
 const nav=e.target.closest('[data-nav],[data-tab]');if(nav){
  const tab=nav.dataset.nav||nav.dataset.tab;
  if(ui.guest){if(GUEST_TABS.includes(tab)){ui.tab=tab;draw();}return;}
  if(!ui.state||!Object.hasOwn(pages,tab))return;
  ui.tab=tab;ui.picks=null;draw();
  if(ui.tab==='scientific'&&!ui.scientific&&!ui.scientificLoading)await loadScientific();
  return;
 }
 const act=e.target.closest('[data-action]');if(!act)return;
 if(act.dataset.action==='guest-enter'){await enterGuest();return;}
 if(ui.guest){
  if(act.dataset.action==='guest-reload'){await reloadGuest();return;}
  if(act.dataset.action==='science-registry-load'){await loadScientificRegistry();return;}
  if(act.dataset.action==='science-registry-export'&&ui.tab==='observatory'){
   await exportScientificRegistry();return;
  }
  if(act.dataset.action==='science-registry-tab'){
   if(['sources','chain','chronicle','episodes','admission','intake','quality'].includes(act.dataset.registry)){
    ui.scienceRegistryTab=act.dataset.registry;ui.scienceRegistryKind='ALL';draw();
   }
   return;
  }
  if(act.dataset.action==='science-registry-kind'){
   if(REGISTRY_KINDS.includes(act.dataset.kind)){ui.scienceRegistryKind=act.dataset.kind;draw();}
  }
  return;
 }
 if(act.dataset.action==='science-reload'){await loadScientific();return;}
 if(act.dataset.action==='science-export'){await exportScientific();return;}
 if(act.dataset.action==='science-probe'){await probeScientificAdmission();return;}
 if(act.dataset.action==='science-registry-load'){await loadScientificRegistry();return;}
 if(act.dataset.action==='science-registry-export'){await exportScientificRegistry();return;}
 if(act.dataset.action==='science-registry-tab'){
  if(['sources','chain','chronicle','episodes','admission','intake','quality'].includes(act.dataset.registry)){
   ui.scienceRegistryTab=act.dataset.registry;ui.scienceRegistryKind='ALL';draw();
  }
  return;
 }
 if(act.dataset.action==='science-registry-kind'){
  if(REGISTRY_KINDS.includes(act.dataset.kind)){ui.scienceRegistryKind=act.dataset.kind;draw();}
  return;
 }
 perform(act.dataset.action,act.dataset.id);});
document.addEventListener('change',async e=>{
 if(ui.guest&&!['science-cut','science-scenario','science-registry-valid',
   'science-registry-family','science-registry-publication'].includes(e.target.id))return;
 if(e.target.id==='science-cut'&&['early','late'].includes(e.target.value)){
  ui.scienceCut=e.target.value;
  if(ui.scienceCut==='early'){
   if(ui.scienceFirstPublic==='2026-10-30T12:00:00Z')ui.scienceFirstPublic='as_of';
   if(ui.scienceRegistryPublished==='2026-10-30T12:00:00Z')ui.scienceRegistryPublished='as_of';
  }
  if(ui.guest)await reloadGuest();else await loadScientific();
 }else if(e.target.id==='science-first-public'&&['as_of','2026-09-19T12:00:00Z','2026-10-30T12:00:00Z'].includes(e.target.value)){
  if(e.target.value==='2026-10-30T12:00:00Z'&&ui.scienceCut==='early')return;
  ui.scienceFirstPublic=e.target.value;++ui.scienceExportGeneration;draw();
 }else if(e.target.id==='science-scenario'&&['baseline','rights_spoof','privacy_probe'].includes(e.target.value)){
  ui.scienceScenario=e.target.value;
  if(ui.guest)await reloadGuest();else await loadScientific();
 }else if(e.target.id==='science-registry-valid'&&REGISTRY_VALID_DAYS.includes(e.target.value)){
  ui.scienceRegistryValid=e.target.value;await loadScientificRegistry();
 }else if(e.target.id==='science-registry-family'&&REGISTRY_FAMILIES.includes(e.target.value)){
  ui.scienceRegistryFamily=e.target.value;ui.scienceRegistryKind='ALL';await loadScientificRegistry();
 }else if(e.target.id==='science-registry-publication'&&REGISTRY_PUBLICATION.includes(e.target.value)){
  if(e.target.value==='2026-10-30T12:00:00Z'&&ui.scienceCut==='early')return;
  ui.scienceRegistryPublished=e.target.value;await loadScientificRegistry();
 }else if(e.target.id==='science-candidate'&&['baseline','sha_spoof','issuer_spoof','rights_missing','first_public_missing','crosswalk_missing','denominator_missing','coverage_missing'].includes(e.target.value)){
  ui.scienceCandidate=e.target.value;ui.scienceAdmission=null;ui.scienceAdmissionError=null;draw();
 }else if(e.target.id==='science-valid'&&['2026-09-11','2026-09-15'].includes(e.target.value)){
  ui.scienceValid=e.target.value;draw();
 }else if(e.target.id==='science-chronicle'&&['2026-09-15','2026-10-10'].includes(e.target.value)){
  ui.scienceChronicleValid=e.target.value;draw();
 }
});
el('club-select').addEventListener('change',async e=>{if(ui.guest||!ui.state)return;if(e.target.value==='__new'){const name=prompt('Nombre de tu nuevo club (3–36 caracteres)');if(!name){draw();return;}try{const c=await call('/api/clubs',{name});ui.club=c.id;ui.picks=null;notice('Club creado con 100 créditos.');await refresh();}catch(err){notice(err.message,true);draw();}}else{ui.club=e.target.value;ui.picks=null;draw();}});
bootstrap().catch(e=>{el('content').innerHTML=`<p class="warning">No se ha podido cargar la demo: ${esc(e.message)}</p>`;});
