import {scoreSyntheticRound} from '../../src/politics_fantasy/synthetic_round_score.mjs';
const results=['synthetic-v1','synthetic-v2','synthetic-v999'].map(rule_version=>{try {const output=scoreSyntheticRound({round_id:'SYN-RND-probe',rule_version,verified_complete:true,evidence_id:'synthetic-fixture:probe',slots:['SYN-EVT-1'],events:[{id:'SYN-EVT-1',attempted:true,success:true}]});return {rule_version,accepted:true,scores:output.scores};}catch(e){return {rule_version,accepted:false,error:e.message};}});
console.log(JSON.stringify({results},null,2));
