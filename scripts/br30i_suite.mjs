/* PF-BR30I A–J discrimination harness (30 distinct acceptance endpoints).
 * Evidence classes: BOE/JEC manual official documentary transcriptions, third
 * party election CSV, prior synthetic actor engine, static product integration.
 * This is exploratory post-exposure, NOT 30 independent confirmatory trials.
 */
export function execute30({J,P,U,officialPsv,secondaryCsv,atlas,coalitions,historicCsv,
 pythonAdapter,serverPython,html,appJS,cliJS,nodeTest}){
 const assert=(condition,msg)=>{if(!condition)throw Error(msg||"ASSERTION_FAILED");};
 const fail=(fn,pattern)=>{let e=null;try{fn()}catch(ex){e=String(ex.message)}assert(e!==null,"NEGATIVE_CONTROL_DID_NOT_FAIL");if(pattern)assert(pattern.test(e),"UNEXPECTED_ERROR_"+e);};
 const official=J.officialTable(officialPsv),csv=P.parseCSV(secondaryCsv),report=J.compareJEC(official,csv),five=J.compareFiveBOEIII(atlas),match=J.coalitionCrosswalk(coalitions,atlas),coverage=J.optionCoverage(csv,atlas),history=P.auditHistoric(historicCsv),gate=J.readiness();
 const byCode=new Map(official.rows.map(x=>[x.code,x]));
 const m=(name)=>report.counts[name]?.equal;
 const equal52=name=>{assert(m(name)===52&&report.counts[name].different===0,"JEC_"+name+"_MISMATCH");return{cells_equal:52};};
 const tests=[
 ["C01","documentary",()=>{assert(official.rows.length===52&&report.paired===52,"SOURCE_PROVINCES");assert(new Set(official.rows.map(x=>x.code)).size===52,"DUPLICATE_CODE");return{paired:52}}],
 ["C02","external_counts",()=>equal52("electors")],
 ["C03","external_counts",()=>equal52("voters")],
 ["C04","external_counts",()=>equal52("valid")],
 ["C05","external_counts",()=>equal52("candidatures")],
 ["C06","external_counts",()=>{let a=equal52("blank"),b=equal52("null");return{cells_equal:a.cells_equal+b.cells_equal}}],
 ["C07","conservation",()=>{assert(official.rows.every(x=>x.valid===x.candidatures+x.blank),"OFFICIAL_INVALID_BALANCE");return{identities:52}}],
 ["C08","conservation",()=>{assert(official.rows.every(x=>x.voters===x.valid+x.null),"OFFICIAL_VOTERS_INVALID");return{identities:52}}],
 ["C09","source_totals",()=>{assert(report.province_options.length===52&&report.province_options.every(x=>x.difference===0),"SLATE_VOTES_NOT_EXHAUSTIVE");return{district_sums_equal:52}}],
 ["C10","seats",()=>{const sums=atlas.labels.reduce((a,x)=>a+x.seats,0);assert(sums===350,"SEAT_TOTAL_MISMATCH");return{seats:sums,labels_with_seats:atlas.labels.filter(x=>x.seats>0).length}}],
 ["C11","external_party_totals",()=>{assert(five.length===5&&five.every(x=>x.exact),"BOE_III_UNMATCHED");return{verified_official_party_totals:5}}],
 ["C12","official_coalition",()=>{assert(coalitions.entries.length===16&&coalitions.entries.filter(x=>x.id.startsWith("C")).length===12,"JEC_COALITION_COUNT");return{JEC:12,JEP:4}}],
 ["C13","entity_mapping",()=>{assert(match.exact_unique_congress===10 && match.ambiguous_ids.length===0,"COALITION_MATCH");return{unique_exact_candidates:10,unresolved:match.records.filter(x=>x.match_state==="NO_EXACT_ACRONYM_MATCH").length}}],
 ["C14","chamber_scope",()=>{assert(match.senate_only===2 && match.records.filter(x=>x.senate_only).every(x=>x.candidates.length===0),"SENATE_CONFLATION");return{senate_only_excluded:2}}],
 ["C15","territorial_scope",()=>{assert(match.records.filter(x=>x.source_level==="JUNTA_PROVINCIAL").length===4,"JEP_LOST");assert(match.records.every(x=>x.territorial_scope&&x.official_name),"SCOPE_LOST");return{provincial_scope_count:4}}],
 ["C16","identity_safety",()=>{assert(match.records.every(x=>x.match_state!=="AUTO_LEGAL_PARTY_IDENTITY"),"PARTY_IDENTITY_ASSUMED");return{party_legal_ids_produced:0}}],
 ["C17","historical_distinction",()=>{assert(Math.max(...Object.keys(history.elections_by_year).map(Number))===2019,"HIST_DATE");assert(P.crossSource(P.audit2023(secondaryCsv),history).cross_source_identity_merge==="NOT_PERFORMED","AUTO_MERGE");return{historical_rows:history.rows,manual_merges:0}}],
 ["C18","no_seat",()=>{assert(atlas.labels.length===59 && atlas.labels.filter(x=>x.seat_status==="VOTES_WITHOUT_CONGRESS_SEAT").length===48,"NONSEAT_LOST");return{labels:59,positive_no_seat:48}}],
 ["C19","geographic_observation",()=>{assert(coverage.provinces===52&&coverage.low>=1&&coverage.high<=59,"OPTION_COUNT_INVALID");return{range:[coverage.low,coverage.high]}}],
 ["C20","measurement_caution",()=>{assert(coverage.noSeatShare>0&&coverage.noSeatShare<1,"INVALID_SHARE");assert(coverage.noSeatVotes===606450,"NOSEAT_AGGREGATION");return{nonseat_label_votes:coverage.noSeatVotes,share:coverage.noSeatShare,causal_inference:false}}],
 ["C21","provenance",()=>{assert(official.trace.includes("MANUAL_TRANSCRIPTION")&&!gate.can_score_real_people,"WRONG_RAW_CLAIM");return{raw_official_bytes_validated:false,manual:true}}],
 ["C22","asof",()=>{assert(!gate.can_historical_forecast_asof&&gate.blockers.includes("FIRST_PUBLIC_AT_UNKNOWN"),"UNSAFE_ASOF");return{asof_certified:false}}],
 ["C23","mutation_control",()=>{assert(J.mutationCheck(official,csv),"UNDETECTED_TAMPERING");return{corruption_detected:true}}],
 ["C24","identity_negative",()=>{const lines=officialPsv.trimEnd().split("\n");fail(()=>J.officialTable(officialPsv+"\n"+lines.at(-1)),/JEC_CODE_COLLISION/);return{duplicate_rejected:true}}],
 ["C25","person_privacy",()=>{const r=U.createRegistry();U.addSource(r,{id:"test",kind:"FIXTURE",state:"FIXTURE",url:"https://fixture.invalid/test",observed_at:"2026-10-26T00:00:00Z",license:"FIXTURE"});fail(()=>U.addActor(r,{id:"TEST:private",kind:"PERSON",name:"Private",source_id:"test",public_role_documented:false}),/PRIVATE_PERSON_EXCLUDED/);assert(!J.readiness().can_score_real_people,"RATING_GATE_OPEN");return{private_person_rejected:true,real_ratings_allowed:false}}],
 ["C26","python_adapter",()=>{assert(pythonAdapter.includes("ATLAS_PROVENANCE_INVALID")&&pythonAdapter.includes('"real_person_scores_enabled": False')&&pythonAdapter.includes("HISTORICAL_SECONDARY_AGGREGATE"),"BAD_ADAPTER_CONTRACT");return{reviewed_static_code:true,node_or_python_runtime_executed:false}}],
 ["C27","frontend",()=>{assert(html.includes('data-tab="atlas"')&&appJS.includes("FUENTE SECUNDARIA, HISTÓRICA")&&appJS.includes("name.localeCompare(y.name,'es')"),"UNINTEGRATED_ATLAS");return{navigation_present:true,disclaimer_present:true,reviewed_static_code:true}}],
 ["C28","server",()=>{assert(serverPython.includes("route == '/api/electoral-atlas'")&&serverPython.includes("('127.0.0.1',port)")&&serverPython.includes("return self.reply(200,atlas_status())"),"SERVER_ROUTE_MISSING");return{read_only_get_route:true,loopback_only:true,HTTP_E2E_executed:false}}],
 ["C29","replay",()=>{assert(cliJS.includes("compareJEC")&&cliJS.includes("parseCSV")&&cliJS.includes("process.exitCode=1")&&nodeTest.includes('test("Five official BOE'),"REPLAY_MISSING");return{runner_written:true,clean_node_run:false}}],
 ["C30","ab_governance",()=>{assert(report.different_cells.length===0&&gate.blockers.length>=4&&match.ambiguous_ids.length===0,"NEEDS_REPAIR");return{original_field_persons_validated:0,actual_source_documentary_cells:312,AB_grade_not_inferred:true}}]
 ];
 return {summary:{prepared:tests.length,source_scope:"JEC transcription + 2023 secondary CSV + official coalition HTML transcription; field provenance imperfect"},
  outcomes:tests.map(([id,branch,fn])=>{try{return {id:"PF-BR30I-"+id,branch,outcome:"PASS",result:fn()}}catch(e){return{id:"PF-BR30I-"+id,branch,outcome:"FAIL",error:String(e.message)}}})};
}
