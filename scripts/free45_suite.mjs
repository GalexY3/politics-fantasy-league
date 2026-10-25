/** F45 standalone dependency-injected acceptance suite.
 * Run via scripts/run_free45.mjs with two pinned public SECONDARY CSV sources.
 * The tests are distinct software invariants, not 45 independent field studies.
 */
export function executeSuite(A,U,raw2023,rawHistoric,atlas,ui,server,adapter){
 const assert=(v,msg="assertion failed")=>{if(!v)throw Error(msg)};
 const reject=(fn,match)=>{let msg="";try{fn()}catch(e){msg=String(e.message)}assert(msg.length>0,"Expected error, no rejection");if(match)assert(match.test(msg),"Wrong rejection: "+msg)};
 const csv23=A.parseCSV(raw2023),csvHist=A.parseCSV(rawHistoric);
 const a=A.audit2023(raw2023),b=A.auditHistoric(rawHistoric);
 const rNew=()=>{const r=U.createRegistry();U.addSource(r,{id:"FX",kind:"FIXTURE",state:"FIXTURE",url:"https://fiction.example/test",observed_at:"2026-10-26T18:00:00Z",license:"SYNTHETIC"});return r};
 const actor=(r,id,kind="PARTY",name="Ficticio",props={})=>U.addActor(r,{id,kind,name,source_id:"FX",public_role_documented:true,...props});
 const claim=(r,id,rel,sub,obj=null,props={})=>U.addClaim(r,{id,relation:rel,subject_id:sub,object_id:obj,source_id:"FX",valid_from:"2026-01-01",valid_to:null,observed_at:"2026-10-26T18:00:00Z",first_public_at:"2026-01-10T12:00:00Z",...props});
 const lines=raw2023.trim().split(/\r?\n/);
 const tasks=[
 ()=>assert(a.labels>0&&b.rows>0&&a.dataset!==b.dataset,"Two sources are not different"),
 ()=>assert(["Nombre de Comunidad","Código de Provincia","Nombre de Provincia"].every(x=>csv23.header.includes(x))),
 ()=>assert(csv23.header.some((v,i)=>v.endsWith("_votos")&&csv23.header[i+1]===v.slice(0,-6)+"_diputados")),
 ()=>assert(new Set(csv23.rows.map(x=>x.length)).size===1 && csv23.rows[0].length===csv23.header.length),
 ()=>assert(a.provinces===52),
 ()=>assert(new Set(csv23.rows.map(x=>x[1])).size===52),
 ()=>assert(a.labels===59),
 ()=>assert(a.with_seat===11),
 ()=>assert(a.with_positive_vote_no_seat===48),
 ()=>assert(a.labels_data.every(x=>x.votes>0)),
 ()=>assert(a.labels_data.every(x=>Number.isSafeInteger(x.votes)&&Number.isSafeInteger(x.seats)&&x.votes>=0&&x.seats>=0)),
 ()=>assert(a.labels_data.every(x=>x.source_column.length>0)),
 ()=>assert(b.rows===1057),
 ()=>assert(Object.keys(b.elections_by_year).length===14),
 ()=>assert(b.distinct_dataset_codes===260),
 ()=>assert(b.codes_with_multiple_denominations>0&&A.crossSource(a,b).cross_source_identity_merge==="NOT_PERFORMED"),
 ()=>{let x=A.parseCSV('a,b\n"quoted, comma",z\n');assert(x.rows[0][0]==="quoted, comma")},
 ()=>{let x=A.parseCSV('a,b\n"foo""bar",z\n');assert(x.rows[0][0]==='foo"bar')},
 ()=>assert(A.parseCSV('\uFEFFa,b\n1,2\n').header[0]==="a"),
 ()=>assert(A.parseCSV('a,b\r\n1,2\r\n').rows.length===1),
 ()=>reject(()=>A.parseCSV('a,b\n1\n'),/RAGGED/),
 ()=>reject(()=>A.parseCSV('a,b\n"1,2'),/UNCLOSED/),
 ()=>reject(()=>A.parseCSV('a,b\nx"z,2\n'),/MISPLACED/),
 ()=>reject(()=>A.parseCSV('a,b\n'),/HEADER_WITHOUT_DATA/),
 ()=>reject(()=>A.audit2023(raw2023.replace("Nombre de Comunidad","Comunidad (distinta)")),/MISSING_BASE_FIELD/),
 ()=>reject(()=>A.audit2023(raw2023.replace("PARTIDO POPULAR_PP_diputados","PP_NOMALIGNED")),/VOTE_SEATS_NOT_PAIRED/),
 ()=>reject(()=>A.audit2023(raw2023.trim()+"\n"+lines[1]+"\n"),/DUPLICATE_PROVINCE/),
 ()=>reject(()=>A.audit2023(raw2023.replace(",131524,3,",",X,3,")),/NOT_NATURAL_NUMBER/),
 ()=>reject(()=>A.audit2023(raw2023.replace(",131524,3,",",999999999999999999999999,3,")),/NUMBER_UNSAFE/),
 ()=>reject(()=>A.auditHistoric(rawHistoric.replace(",1.1289335E7,",",-11,")),/BAD_VOTES/),
 ()=>{let r=rNew();actor(r,"FX:p");assert(U.representation(r,"FX:p")==="UNKNOWN")},
 ()=>{let r=rNew();reject(()=>U.addActor(r,{id:"FX:private",kind:"PERSON",name:"Persona privada",source_id:"FX",public_role_documented:false}),/PRIVATE_PERSON_EXCLUDED/)},
 ()=>{let r=rNew();reject(()=>U.addActor(r,{id:"FX:pub",kind:"PERSON",name:"Persona Pública",source_id:"FX",public_role_documented:true,private_email:"privado@ejemplo.invalid"}),/BAD_ACTOR/)},
 ()=>{let r=rNew();actor(r,"FX:interest","INTEREST_GROUP","Foro");actor(r,"FX:party","PARTY","Partido");assert(r.actors.length===2&&r.actors[0].kind!==r.actors[1].kind)},
 ()=>assert(U.stableId("ORG","external-123")==="ORG:external-123"),
 ()=>{let r=rNew();actor(r,"FX:p1","PERSON","Nombre Común");actor(r,"FX:p2","PERSON","Nombre Común");let q=U.resolveIdentity(r,{authority:"EXT",external_id:"new",name:"Nombre Común"});assert(q.status==="UNRESOLVED_HOMONYM"&&q.candidate_count===2)},
 ()=>{let r=rNew();actor(r,"FX:p","PERSON","Persona ficticia");claim(r,"FX:old","PUBLIC_SPOKESPERSON","FX:p",null,{valid_to:"2026-06-01"});assert(U.roleAt(r,"FX:p","2026-05-01").length===1&&U.roleAt(r,"FX:p","2026-09-01").length===0)},
 ()=>{let r=rNew();actor(r,"FX:p","PERSON","Portavoz");claim(r,"FX:s","PUBLIC_SPOKESPERSON","FX:p");assert(U.minimalParliamentaryBaseline(r).represented_person_count===0)},
 ()=>{let r=rNew();actor(r,"FX:p");claim(r,"FX:q","PUBLIC_ADVOCACY","FX:p");assert(U.timeView(r,"2026-06-01T00:00:00Z").claims.length===0)},
 ()=>{let r=rNew();actor(r,"FX:p");claim(r,"FX:q","PUBLIC_ADVOCACY","FX:p",null,{first_public_at:null});assert(U.timeView(r,"2026-10-27T00:00:00Z").claims.length===0)},
 ()=>{let r=rNew();actor(r,"FX:p","PERSON","Figura Pública");assert(U.realityScoringGate(r,"FX:p").eligible===false)},
 ()=>{let r=rNew();actor(r,"FX:p");claim(r,"FX:q","DECLARED_POLICY_POSITION","FX:p",null,{issue:"medioambiente",exact_statement:"Propuesta inventada sobre energía"});const q=U.issueClaims(r,"medioambiente");assert(q.length===1&&!Object.hasOwn(q[0],"ideology_score"))},
 ()=>{let r=rNew();actor(r,"FX:p","PERSON","Candidata");actor(r,"FX:party","PARTY","Partido");claim(r,"FX:c","CANDIDATE_FOR","FX:p","FX:party");assert(!r.claims.some(v=>v.relation==="REGISTERED_PARTY"))},
 ()=>{let r=rNew();actor(r,"FX:p1","PARTY","P1");actor(r,"FX:p2","PARTY","P2");actor(r,"FX:coal","COALITION","Coalición");claim(r,"FX:c1","COALITION_MEMBER","FX:p1","FX:coal");claim(r,"FX:c2","COALITION_MEMBER","FX:p2","FX:coal");assert(r.claims.length===2)},
 ()=>assert(atlas.labels.length===59 && atlas.labels.every(x=>x.seat_status&&x.name) && server.includes("'/api/electoral-atlas'")&&ui.includes("FUENTE SECUNDARIA, HISTÓRICA")&&adapter.includes('"real_person_scores_enabled": False'))
 ];
 return tasks.map((task,i)=>{
  try{task();return {id:"PF-F"+String(i+1).padStart(2,"0"),status:"PASS"}}
  catch(e){return{id:"PF-F"+String(i+1).padStart(2,"0"),status:"FAIL",error:String(e.message)}}
 });
}
