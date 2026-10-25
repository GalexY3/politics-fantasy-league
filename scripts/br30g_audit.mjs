/** Pure audit suite PF-BR30G C03-C30. Replay on pinned secondary JSONL. All outputs secondary-source exploratory. */
export const analyze = function analyze(textSource){
const round=(v,p=6)=>Number.isFinite(v)?Number(v.toFixed(p)):null;
const div=(a,b)=>b? a/b:null;
const sign=x=>(x>0)-(x<0);
const sum=a=>a.reduce((t,x)=>t+x,0);
const mean=a=>a.length?sum(a)/a.length:null;
const ranking=a=>{const ix=a.map((v,i)=>[v,i]).sort((x,y)=>x[0]-y[0]);const ranks=Array(a.length);for(let j=0;j<ix.length;){let k=j+1;while(k<ix.length&&ix[k][0]===ix[j][0])k++;const av=(j+1+k)/2;for(let t=j;t<k;t++)ranks[ix[t][1]]=av;j=k}return ranks};
const spearman=(x,y)=>{if(x.length!==y.length||x.length<3)return null;const a=ranking(x),b=ranking(y),am=mean(a),bm=mean(b),vx=sum(a.map(v=>(v-am)**2)),vy=sum(b.map(v=>(v-bm)**2));return vx&&vy?sum(a.map((v,i)=>(v-am)*(b[i]-bm)))/Math.sqrt(vx*vy):null};
const gini=values=>{const a=values.slice().sort((x,y)=>x-y);let ss=sum(a);if(!ss)return 0;return (2*sum(a.map((v,i)=>(i+1)*v)))/(a.length*ss)-(a.length+1)/a.length};
const entropy3=counts=>{let t=sum(counts.slice(0,3));if(t===0)return null;return -sum(counts.slice(0,3).filter(x=>x).map(x=>{let p=x/t;return p*Math.log(p)/Math.log(3)}))};
const grouped=(items,key)=>{const m=new Map();for(const x of items){const k=key(x);if(!m.has(k))m.set(k,[]);m.get(k).push(x)}return m};
const R=textSource.trim().split(/\r?\n/).filter(Boolean).map(JSON.parse).sort((a,b)=>a.fecha.localeCompare(b.fecha)||a.sesion-b.sesion||a.numero-b.numero);
for(const r of R){
r._g=Object.entries(r.grupos||{}).map(([code,ct])=>({code,ct,expr:sum(ct.slice(0,3)),total:sum(ct)}));
r._n={};for(const k of "SNAX")r._n[k]=(r.votos?.[k]||"").trim().split(/\s+/).filter(Boolean).length;
r._total=sum([r.totales.si,r.totales.no,r.totales.abstencion,r.totales.noVota]);
r._nom=sum(Object.values(r._n));r._miss=r._total-r._nom;r._cov=div(r._nom,r._total);
r._year=r.fecha.slice(0,4);r._month=r.fecha.slice(0,7);r._margin=r.totales.si-r.totales.no;
r._nommargin=r._n.S-r._n.N;
r._status=r._nom===0?"NO_NOMINAL":sign(r._margin)===sign(r._nommargin)?"SAME_SIGN":sign(r._margin)===0||sign(r._nommargin)===0?"TIE_INVOLVED":"STRICT_REVERSAL";
}
const groups=grouped(R,r=>String(r.sesion)), years=grouped(R,r=>r._year);
const results={};
const put=(n,summary,unit="vote",exposure="same_secondary_blob")=>{results["C"+String(n).padStart(2,"0")]={summary,unit,exposure,source_n:R.length,distinct_sources:1}};
const summaryCov=arr=>({n:arr.length,totalPositions:sum(arr.map(r=>r._total)),nominal:sum(arr.map(r=>r._nom)),weightedCoverage:round(div(sum(arr.map(r=>r._nom)),sum(arr.map(r=>r._total)))),voteMeanCoverage:round(mean(arr.map(r=>r._cov)))});
const byYear=fn=>Object.fromEntries([...years].map(([y,a])=>[y,fn(a)]));
{
 const m=grouped(R,r=>r._month), out=[...m].map(([month,a])=>({month,...summaryCov(a)}));
 const eligible=out.filter(x=>x.n>=10).sort((a,b)=>a.weightedCoverage-b.weightedCoverage);
 put(3,{monthsTotal:out.length,months10OrMore:eligible.length,bottomMonths:eligible.slice(0,4),topMonths:eligible.slice(-4),weightedMonthlyRange:round(eligible.at(-1)?.weightedCoverage-eligible[0]?.weightedCoverage)},"month");
}
{
 const out=[...groups].map(([session,a])=>({session,n:a.length,r:Math.max(...a.map(x=>x._cov))-Math.min(...a.map(x=>x._cov))})).filter(x=>x.n>=2);
 put(4,{sessionsWithMultipleVotes:out.length,shareVariable:round(div(out.filter(x=>x.r>0).length,out.length)),meanMaxMin:round(mean(out.map(x=>x.r))),maxRange:round(Math.max(...out.map(x=>x.r))),top:out.sort((a,b)=>b.r-a.r).slice(0,5)},"session");
}
 put(5,{years:byYear(a=>({weighted:round(summaryCov(a).weightedCoverage),unweighted:round(summaryCov(a).voteMeanCoverage),difference_pp:round(100*(summaryCov(a).weightedCoverage-summaryCov(a).voteMeanCoverage)),votes:a.length}))});
{
 const q=R.slice().sort((a,b)=>b._miss-a._miss), k=Math.ceil(R.length*.10);
 put(6,{topDecileN:k,shareAllMissingTopDecile:round(div(sum(q.slice(0,k).map(r=>r._miss)),sum(q.map(r=>r._miss)))),giniOfMissingPerVote:round(gini(R.map(x=>x._miss))),allMissing:sum(R.map(r=>r._miss)),maxMissingVote:q[0]?{id:q[0].id,missing:q[0]._miss}:null});
}
{
 const key={S:"si",N:"no",A:"abstencion",X:"noVota"};
 const all=Object.fromEntries([...years].map(([year,a])=>[year,Object.fromEntries(Object.entries(key).map(([cat,k])=>{const total=sum(a.map(r=>r.totales[k])),visible=sum(a.map(r=>r._n[cat]));return[cat,{total,missing:total-visible,rate:round(div(total-visible,total))}]}))]));
 put(7,{years:all});
}
{
 const by=byYear(a=>{const s=sum(a.map(r=>r.totales.si)),n=sum(a.map(r=>r.totales.no));const misss=s-sum(a.map(r=>r._n.S)),missn=n-sum(a.map(r=>r._n.N));return{missingRateYes:round(div(misss,s)),missingRateNo:round(div(missn,n)),yesMinusNo_pp:round(100*(misss/s-missn/n))}});
 put(8,{byYear:by});
}
{
 const z=R.filter(r=>r._nom===0);put(9,{zeroNominalVotes:z.map(r=>({id:r.id,date:r.fecha,totals:r._total,type:r.tipo.slice(0,90)})),n:z.length,positionsMissing:sum(z.map(r=>r._miss))});
}
{
 const cats=[...grouped(R,r=>r.tipo)].map(([tipo,a])=>({tipo:tipo.slice(0,110),...summaryCov(a)})).filter(o=>o.n>=25).sort((a,b)=>a.weightedCoverage-b.weightedCoverage);
 put(10,{qualifyingTypes:cats.length,lowest:cats.slice(0,5),highest:cats.slice(-5)},"type");
}
{
 put(11,{spearmanNumberOfGroupRowsVsCoverage:round(spearman(R.map(r=>r._g.length),R.map(r=>r._cov))),minimumGroups:Math.min(...R.map(r=>r._g.length)),maximumGroups:Math.max(...R.map(r=>r._g.length))});
 put(12,{spearmanNormalizedAbsYesNoMarginVsCoverage:round(spearman(R.map(r=>Math.abs(r._margin)/r._total),R.map(r=>r._cov))),n:R.length});
}
{
 const bins={"0-5":[],"6-20":[],">20":[]};
 for(const r of R){let d=Math.abs(r._margin),k=d<=5?"0-5":d<=20?"6-20":">20";bins[k].push(r)}
 put(13,{bins:Object.fromEntries(Object.entries(bins).map(([k,a])=>[k,{n:a.length,strict:a.filter(r=>r._status==="STRICT_REVERSAL").length,tie:a.filter(r=>r._status==="TIE_INVOLVED").length,noNominal:a.filter(r=>r._status==="NO_NOMINAL").length,strictRate:round(div(a.filter(r=>r._status==="STRICT_REVERSAL").length,a.filter(r=>r._nom>0).length))}]))});
}
{
 const a=R.filter(r=>r._nom>0);const robust=a.filter(r=>Math.abs(r._nommargin)>r._miss);
 put(14,{included:a.length,robustCertified:robust.length,shareRobust:round(div(robust.length,a.length)),mismatchesAmongRobust:robust.filter(r=>r._status!=="SAME_SIGN").length,ambiguous:a.length-robust.length,ambiguousActuallyStrict:a.filter(r=>Math.abs(r._nommargin)<=r._miss&&r._status==="STRICT_REVERSAL").length},"vote");
}
{
 const ss=[...groups].map(([sess,a])=>({sess,strict:a.filter(r=>r._status==="STRICT_REVERSAL").length,all:a.length})).sort((a,b)=>b.strict-a.strict);const tot=sum(ss.map(s=>s.strict)),p=ss.filter(s=>s.strict).map(s=>s.strict/tot);
 put(15,{sessionsContainingStrict:ss.filter(s=>s.strict>0).length,top5OfStrict:round(div(sum(ss.slice(0,5).map(s=>s.strict)),tot)),herfindahl:round(sum(p.map(x=>x*x))),topSessions:ss.slice(0,5)},"session");
}
const gs=R.flatMap(r=>r._g.map(g=>({...g,year:r._year,date:r.fecha,voteId:r.id,session:r.sesion}))),ge=gs.filter(g=>g.expr>=2);
{
 const unanimous=g=>g.ct.slice(0,3).filter(x=>x>0).length===1;
 put(16,{rowsAtLeastTwoExpressed:ge.length,unanimityUnweighted:round(mean(ge.map(g=>unanimous(g)?1:0))),unanimityByExpressedVotes:round(div(sum(ge.filter(unanimous).map(g=>g.expr)),sum(ge.map(g=>g.expr)))),note:"Size-dependent descriptive statistic"},"group_vote");
}
{
 const byY=grouped(ge,g=>g.year);
 put(17,{overallMeanEntropyNormalized:round(mean(ge.map(g=>entropy3(g.ct)))),meanEntropyByYear:Object.fromEntries([...byY].map(([y,a])=>[y,{n:a.length,meanEntropy:round(mean(a.map(g=>entropy3(g.ct))))}]))},"group_vote");
}
{
 put(18,{byYear:Object.fromEntries([...grouped(gs.filter(g=>g.expr>=10),g=>g.year)].map(([y,a])=>[y,{n:a.length,unanimous:round(mean(a.map(g=>g.ct.slice(0,3).filter(x=>x>0).length===1?1:0)))}]))},"group_vote");
}
const coalitions=new Map(), pairVotes=[];
for(const r of R){
 const major=r._g.map(g=>{let xs=g.ct.slice(0,3),max=Math.max(...xs);return{code:g.code,maj:max>0&&xs.filter(x=>x===max).length===1?xs.indexOf(max):null}}).filter(x=>x.maj!==null);
 for(let i=0;i<major.length;i++)for(let j=i+1;j<major.length;j++){
  let c=[major[i].code,major[j].code].sort();const key=c.join("::");const rec={key,year:r._year,agreement:major[i].maj===major[j].maj?1:0};
  pairVotes.push(rec);let by=coalitions.get(key);if(!by){by={pair:c,n:0,agree:0,byYear:{}};coalitions.set(key,by)}
  by.n++;by.agree+=rec.agreement;let yy=by.byYear[r._year]||(by.byYear[r._year]={n:0,agree:0});yy.n++;yy.agree+=rec.agreement;
 }
}
{
 put(19,{pairsCompared:pairVotes.length,overallShareSameClearMode:round(mean(pairVotes.map(x=>x.agreement))),distinctGroupPairs:coalitions.size,excluded:"ties and group-vote with zero S/N/A"},"group_pair_vote");
}
{
 const qualified=[...coalitions.values()].map(o=>{const a=o.byYear["2024"],b=o.byYear["2025"];if(!a||!b||a.n<20||b.n<20)return null;return{pair:o.pair,n2024:a.n,n2025:b.n,agree2024:round(a.agree/a.n),agree2025:round(b.agree/b.n),delta:round(b.agree/b.n-a.agree/a.n)}}).filter(Boolean).sort((a,b)=>Math.abs(b.delta)-Math.abs(a.delta));
 put(20,{qualifyingPairs:qualified.length,largestChanges:qualified.slice(0,10),warning:"Does not identify individual affiliation or influence"},"group_pair_year");
}
{
 const changes=[];
 for(const r of R)for(const g of r._g){const newSign=sign(r._margin-(g.ct[0]-g.ct[1]));if(newSign!==sign(r._margin))changes.push({g:g.code,v:r.id,newSign,sign:sign(r._margin)})}
 const count=grouped(changes,x=>x.g);
 put(21,{groupExclusionSignChanges:changes.length,distinctVotesAffected:new Set(changes.map(x=>x.v)).size,topGroups:[...count].map(([g,a])=>({group:g,n:a.length})).sort((a,b)=>b.n-a.n).slice(0,10),warning:"Mechanical leave-group-out arithmetic, NOT a causal pivotal-voter estimate"},"group_vote");
}
{
 const cats=[...grouped(R,r=>r.tipo)].filter(([,a])=>a.length>=25).map(([tipo,a])=>({tipo:tipo.slice(0,105),n:a.length,yes:round(mean(a.map(r=>sign(r._margin)===1?1:0))),no:round(mean(a.map(r=>sign(r._margin)===-1?1:0))),tie:round(mean(a.map(r=>sign(r._margin)===0?1:0)))})).sort((a,b)=>a.yes-b.yes);
 put(22,{types:cats.length,lowestYes:cats.slice(0,5),highestYes:cats.slice(-5)},"type");
}
{
 const withD=R.filter(r=>typeof r.di==="string"&&r.di.trim().length>0),without=R.filter(r=>!r.di||!r.di.trim());
 put(23,{withDissentCodes:summaryCov(withD),withoutDissentCodes:summaryCov(without),differenceCoverage_pp:round(100*(summaryCov(withD).weightedCoverage-summaryCov(without).weightedCoverage)),warning:"di derived from current-roster subset, not independent measure of discipline"},"vote");
}
{
 const a=R.filter(r=>r.asentimiento===true),b=R.filter(r=>r.asentimiento!==true);
 put(24,{assent:summaryCov(a),other:summaryCov(b),assentCount:a.length},"vote");
}
{
 const present=new Map();
 for(const r of R){for(const k of "SNAX"){for(const code of (r.votos?.[k]||"").trim().split(/\s+/).filter(Boolean)){const p=present.get(code)||{first:r._year,last:r._year,years:new Set()};p.last=r._year;p.years.add(r._year);present.set(code,p)}}}
 const first={},last={},span={};for(const c of present.values()){first[c.first]=(first[c.first]||0)+1;last[c.last]=(last[c.last]||0)+1;span[c.years.size]=(span[c.years.size]||0)+1}
 put(25,{uniqueCodes:present.size,firstSeenYear:first,lastSeenYear:last,observedInNYears:span,warning:"First/last observation is not membership start/end"},"code_year");
}
{
 let yes=0,no=0,se1=0,se2=0,n=0,yearsR={};for(const r of R){if(r._margin===0)continue;const target=r._margin>0?1:0,p=(yes+1)/(yes+no+2);const baseline=1;se1+=(p-target)**2;se2+=(baseline-target)**2;n++;const y=yearsR[r._year]||(yearsR[r._year]={n:0,lossLaplace:0,lossAlwaysYes:0});y.n++;y.lossLaplace+=(p-target)**2;y.lossAlwaysYes+=(baseline-target)**2;if(target)yes++;else no++}
 put(26,{n,brierExpandingBaseRate:round(se1/n),brierAlwaysYes:round(se2/n),targetYesFraction:round(yes/n),byYear:Object.fromEntries(Object.entries(yearsR).map(([k,v])=>[k,{n:v.n,expanding:round(v.lossLaplace/v.n),alwaysYes:round(v.lossAlwaysYes/v.n)}])),warning:"Retrospective replay on archive snapshot, NO as-of certified"},"vote");
}
{
 let yes=0,no=0,errType=0,errGlobal=0,n=0,byType=new Map();
 for(const r of R){if(!r._margin)continue;const z=r._margin>0?1:0,o=byType.get(r.tipo)||{yes:0,no:0};const p=(o.yes+1)/(o.yes+o.no+2),q=(yes+1)/(yes+no+2);errType+=(p-z)**2;errGlobal+=(q-z)**2;n++; if(z){o.yes++;yes++}else{o.no++;no++}byType.set(r.tipo,o)}
 put(27,{n,types:byType.size,brierByType:round(errType/n),brierGlobal:round(errGlobal/n),deltaTypeMinusGlobal:round((errType-errGlobal)/n),warning:"Retrospective same-source, model sees archived vote ordering not field release timestamps"},"vote");
}
{
 const ss=[...groups].map(([sesion,a])=>({sesion,date:a[0].fecha,nom:sum(a.map(x=>x._nom)),total:sum(a.map(x=>x._total))})).sort((a,b)=>a.date.localeCompare(b.date)||Number(a.sesion)-Number(b.sesion));
 let histNom=0,histTot=0,prev=null,loss1=0,loss2=0,n=0;
 for(const s of ss){const actual=s.nom/s.total;if(prev!==null){loss1+=Math.abs(prev-actual);loss2+=Math.abs(histNom/histTot-actual);n++}prev=actual;histNom+=s.nom;histTot+=s.total}
 put(28,{sessions: ss.length,holdoutSessions:n,MAE_lastSession:round(loss1/n),MAE_expandingHistorical:round(loss2/n),deltaPersistenceMinusHistorical:round((loss1-loss2)/n),warning:"Retrospective archival snapshot, not live predictability"},"session");
}
{
 const mandatory=["id","fuente","fecha","sesion","numero","tipo","totales","votos","grupos"];
 const missingKeys=Object.fromEntries(mandatory.map(k=>[k,R.filter(r=>!(k in r)).length]));const badHttps=R.filter(r=>!/^https:\/\//.test(r.fuente||"")).length;
 const unknownGroups=gs.filter(g=>g.code==="?"||g.code==="").length;
 const duplicateIds=R.length-new Set(R.map(r=>r.id)).size;
 const groupedDisagree=R.filter(r=>{const x=[r.totales.si,r.totales.no,r.totales.abstencion,r.totales.noVota];return x.some((v,i)=>v!==sum(r._g.map(g=>g.ct[i])))}).length;
 put(29,{missingKeys,badHttps,unknownGroupRows:unknownGroups,duplicateVoteIds:duplicateIds,groupAggregateMismatchedVotes:groupedDisagree,sourceRows:R.length},"schema");
}
{
 const full=R.filter(r=>r._nom===r._total).length;
 const groupOk=R.filter(r=>[r.totales.si,r.totales.no,r.totales.abstencion,r.totales.noVota].every((v,i)=>v===sum(r._g.map(g=>g.ct[i])))).length;
 put(30,{fullNominalCoverageVotes:full,groupTotalsConsistent:groupOk,nominalOriginalIndependentlyMatched:0,historicalRosterWithAsOfVerified:0,eligibleForRealPersonFantasyScores:0,sourceVotes:R.length,AB_DECIDE:"COMPLETE_RETROSPECTIVE_CYCLES; REPAIR_SOURCE_BEFORE_REAL_PERSON_PREDICTION_OR_POINTS",VSDS:"1/3",CT2_predictive:24},"governance");
}
return {campaign:"PF-BR30G",method:"28 distinct A-J retrospective post-exposure secondary-source contrasts",input:{n:R.length,minDate:R[0]?.fecha,maxDate:R.at(-1)?.fecha,source:"MarcoAnarmo/CongresoAbierto data/raw/votaciones/pleno.jsonl",git_blob_sha1:"71918bb689c7a62cfbbdafe0b9248eac6b5c4be1"},cycles:results};
};
