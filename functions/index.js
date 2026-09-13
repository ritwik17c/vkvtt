const {onCall,HttpsError}=require('firebase-functions/v2/https');
const {defineSecret}=require('firebase-functions/params');
const admin=require('firebase-admin');
const OpenAI=require('openai');

admin.initializeApp();
const db=admin.firestore();
const OPENAI_API_KEY=defineSecret('OPENAI_API_KEY');
const REGION='asia-south1';
const ALLOWED_MODELS=new Set(['gpt-5.6-luna','gpt-5.6-terra','gpt-5.6-sol']);

const schema={
  type:'object',additionalProperties:false,
  required:['overallScore','verdict','factualAccuracy','answerQuality','syllabusAlignment','clarity','ambiguityRisk','pedagogicalValue','cognitiveDemand','markSuitability','issues','strengths','suggestedRevision','confidence','needsHumanReview'],
  properties:{
    overallScore:{type:'number',minimum:0,maximum:100},
    verdict:{type:'string',enum:['excellent','strong','acceptable','revise','reject_or_recheck']},
    factualAccuracy:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    answerQuality:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    syllabusAlignment:{type:'object',additionalProperties:false,required:['score','comment','evidenceLevel'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'},evidenceLevel:{type:'string',enum:['strong','partial','insufficient']}}},
    clarity:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    ambiguityRisk:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    pedagogicalValue:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    cognitiveDemand:{type:'object',additionalProperties:false,required:['level','score','comment'],properties:{level:{type:'string',enum:['remember','understand','apply','analyse','evaluate','create','mixed','unclear']},score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    markSuitability:{type:'object',additionalProperties:false,required:['score','comment'],properties:{score:{type:'number',minimum:0,maximum:100},comment:{type:'string'}}},
    issues:{type:'array',items:{type:'string'},maxItems:8},
    strengths:{type:'array',items:{type:'string'},maxItems:8},
    suggestedRevision:{type:'string'},
    confidence:{type:'number',minimum:0,maximum:1},
    needsHumanReview:{type:'boolean'}
  }
};

async function assertAdmin(uid){
  const snap=await db.doc(`authorizedUsers/${uid}`).get();
  if(!snap.exists||snap.data().active!==true||String(snap.data().role||'').toLowerCase()!=='admin') throw new HttpsError('permission-denied','Principal/Admin access is required.');
  return snap.data();
}

function promptFor(q){
  return `You are reviewing a school examination question for Vivekananda Kendra Vidyalaya, Nalbari. Judge the question conservatively and academically. Do not invent syllabus coverage that is not supplied. If exact syllabus evidence is unavailable, say so and lower only syllabus-confidence, not unrelated criteria. Check factual correctness of the question and supplied answer, clarity, ambiguity, age/class appropriateness, pedagogical value, cognitive demand, mark allocation, and whether the expected answer actually answers the question. Flag anything that requires a subject expert.\n\nCLASS: ${q.className||''}\nSUBJECT: ${q.subject||''}\nCHAPTER: ${q.chapter||''}\nTOPIC: ${q.topic||''}\nLEARNING OUTCOME: ${q.learningOutcome||''}\nQUESTION TYPE: ${q.questionType||''}\nDIFFICULTY: ${q.difficulty||''}\nMARKS: ${q.marks??''}\nQUESTION: ${q.questionText||''}\nANSWER: ${q.answer||''}\nMARKING SCHEME: ${q.markingScheme||''}`;
}

exports.reviewQuestionWithAI=onCall({region:REGION,secrets:[OPENAI_API_KEY],timeoutSeconds:120,memory:'512MiB'},async req=>{
  if(!req.auth) throw new HttpsError('unauthenticated','Sign in first.');
  const profile=await assertAdmin(req.auth.uid);
  const questionId=String(req.data?.questionId||'').trim();
  if(!questionId) throw new HttpsError('invalid-argument','questionId is required.');
  const ref=db.doc(`qbQuestions/${questionId}`),snap=await ref.get();
  if(!snap.exists) throw new HttpsError('not-found','Question not found.');
  const q=snap.data();
  if(!['submitted','approved','returned'].includes(String(q.status||''))) throw new HttpsError('failed-precondition','Only non-draft workflow questions can be AI reviewed.');

  const cfgSnap=await db.doc('qbConfig/current').get(),cfg=cfgSnap.exists?cfgSnap.data():{};
  const configured=String(cfg.aiReviewModel||'gpt-5.6-terra');
  const model=ALLOWED_MODELS.has(configured)?configured:'gpt-5.6-terra';
  const client=new OpenAI({apiKey:OPENAI_API_KEY.value()});
  const response=await client.responses.create({
    model,
    reasoning:{effort:'low'},
    input:[
      {role:'system',content:'Return only the requested structured academic review. Be cautious with factual claims and explicitly flag uncertainty.'},
      {role:'user',content:promptFor(q)}
    ],
    text:{format:{type:'json_schema',name:'question_quality_review',strict:true,schema}}
  });
  let review;
  try{review=JSON.parse(response.output_text)}catch(e){throw new HttpsError('internal','AI review returned invalid structured data.');}
  const now=Date.now();
  const stored={...review,model,reviewedAtMs:now,reviewedAt:admin.firestore.FieldValue.serverTimestamp(),reviewedByUid:req.auth.uid,reviewedByName:profile.name||req.auth.token.name||'Principal',engineVersion:'ai-v1'};
  await ref.set({aiQualityReview:stored,updatedAtMs:Math.max(Number(q.updatedAtMs)||0,now)},{merge:true});
  await db.collection('qbAiReviewAudit').add({questionId,teacherUid:q.teacherUid||'',teacherCode:q.teacherCode||'',subject:q.subject||'',className:q.className||'',model,overallScore:review.overallScore,verdict:review.verdict,needsHumanReview:review.needsHumanReview,reviewedAtMs:now,reviewedAt:admin.firestore.FieldValue.serverTimestamp(),reviewedByUid:req.auth.uid});
  return {questionId,review:stored};
});
