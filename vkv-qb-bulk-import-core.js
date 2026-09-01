/* Pure parsing and validation helpers for teacher/admin QB bulk import. */

const ALIASES={
  className:['class','classname','standard','std','grade'],
  section:['section','sectionstream','stream','division','div'],
  subject:['subject','papersubject'],
  chapter:['chapter','chapterunit','unit','lesson','lessonchaptername'],
  topic:['topic','topicsubtopic','subtopic'],
  learningOutcome:['learningoutcome','competency','competencyassessed','learningoutcomecompetencyassessed'],
  marks:['marks','mark','maxmarks'],
  difficulty:['difficulty','difficultylevel'],
  questionType:['type','questiontype'],
  questionText:['question','questiontext','questionwithonlytexts'],
  answer:['answer','answerkey','expectedanswer'],
  markingScheme:['markingscheme','markingschemenotes','notes'],
  teacherCode:['teachercode','staffcode','shortcode'],
  teacherEmail:['teacheremail','email','emailaddress'],
  teacherName:['teachername','nameoftheteacher','name']
};

export const QB_IMPORT_COLUMNS=[
  'Class','Section / Stream','Subject','Chapter / Unit','Topic / Sub-topic',
  'Learning Outcome','Marks','Difficulty','Question Type','Question','Answer','Marking Scheme'
];

export const QB_QUESTION_TYPES=['Very Short Answer','Short Answer','Long Answer','MCQ','Numerical','Case-based','Competency-based'];
export const QB_DIFFICULTIES=['Easy','Moderate','Difficult'];

export function normaliseHeader(value){
  return String(value || '').trim().toLowerCase().replace(/[^a-z0-9]+/g,'');
}

function text(value){return String(value ?? '').trim()}

function findValue(row,field){
  const wanted=new Set(ALIASES[field] || []),entries=Object.entries(row || {});
  for(const [key,value] of entries) if(wanted.has(normaliseHeader(key))) return value;
  return '';
}

function normaliseDifficulty(value){
  const key=text(value).toLowerCase();
  if(!key || key === 'average' || key === 'medium' || key === 'moderate') return 'Moderate';
  if(key === 'easy') return 'Easy';
  if(key === 'hard' || key === 'difficult') return 'Difficult';
  return text(value);
}

function inferType(question,marks,value){
  const supplied=text(value);
  if(supplied){
    const match=QB_QUESTION_TYPES.find(x=>x.toLowerCase()===supplied.toLowerCase());
    return match || supplied;
  }
  if(/(^|\n)\s*(?:\(?[a-dA-D]\)|[a-dA-D][.)])\s+/.test(question)) return 'MCQ';
  if(Number(marks)<=1) return 'Very Short Answer';
  if(Number(marks)<=3) return 'Short Answer';
  return 'Long Answer';
}

export function normaliseQuestionRow(row={},defaults={}){
  const marksRaw=findValue(row,'marks') || defaults.marks || '';
  const markMatch=text(marksRaw).match(/\d+(?:\.\d+)?/);
  const questionText=text(findValue(row,'questionText') || defaults.questionText);
  const marks=markMatch ? Number(markMatch[0]) : 0;
  return {
    className:text(findValue(row,'className') || defaults.className),
    section:text(findValue(row,'section') || defaults.section),
    subject:text(findValue(row,'subject') || defaults.subject),
    chapter:text(findValue(row,'chapter') || defaults.chapter),
    topic:text(findValue(row,'topic') || defaults.topic),
    learningOutcome:text(findValue(row,'learningOutcome') || defaults.learningOutcome),
    marks,
    difficulty:normaliseDifficulty(findValue(row,'difficulty') || defaults.difficulty),
    questionType:inferType(questionText,marks,findValue(row,'questionType') || defaults.questionType),
    questionText,
    answer:text(findValue(row,'answer') || defaults.answer),
    markingScheme:text(findValue(row,'markingScheme') || defaults.markingScheme),
    teacherCode:text(findValue(row,'teacherCode') || defaults.teacherCode),
    teacherEmail:text(findValue(row,'teacherEmail') || defaults.teacherEmail).toLowerCase(),
    teacherName:text(findValue(row,'teacherName') || defaults.teacherName),
    sourceRow:Number(defaults.sourceRow || 0)
  };
}

export function parseExcelQuestionRows(rows=[],defaults={}){
  return rows.map((row,index)=>normaliseQuestionRow(row,{...defaults,sourceRow:index+2}))
    .filter((item,index)=>item.questionText || Object.values(rows[index]||{}).some(value=>text(value)));
}

function extractTrailingMarks(question,defaultMarks){
  const match=question.match(/\s*[\[(]\s*(\d+(?:\.\d+)?)\s*(?:marks?|m)\s*[\])]\s*$/i);
  if(!match) return {question:question.trim(),marks:Number(defaultMarks)||0};
  return {question:question.slice(0,match.index).trim(),marks:Number(match[1])};
}

export function parseWordQuestionText(rawText='',defaults={}){
  const paragraphs=String(rawText || '').replace(/\r/g,'').replace(/\u00a0/g,' ')
    .split(/\n+/).map(line=>line.trim()).filter(Boolean);
  const items=[];
  let current=null;
  const push=()=>{
    if(!current || !current.text.trim()) return;
    const parsed=extractTrailingMarks(current.text,defaults.marks);
    items.push(normaliseQuestionRow({}, {...defaults,questionText:parsed.question,marks:parsed.marks,sourceRow:current.no || items.length+1}));
  };
  for(const line of paragraphs){
    const match=line.match(/^\s*(?:q(?:uestion)?\s*)?(\d{1,4})\s*[.):-]\s*(.+)$/i);
    if(match){
      push();
      current={no:Number(match[1]),text:match[2].trim()};
    }else if(current){
      current.text += '\n'+line;
    }
  }
  push();
  if(!items.length){
    // A labelled Word template may use one QUESTION: block separated by ---.
    for(const block of String(rawText || '').split(/\n\s*-{3,}\s*\n/g)){
      const question=(block.match(/(?:^|\n)\s*question\s*:\s*([\s\S]*?)(?=\n\s*(?:answer|marks|type|difficulty)\s*:|$)/i)||[])[1];
      if(!question) continue;
      const answer=(block.match(/(?:^|\n)\s*answer\s*:\s*([\s\S]*?)(?=\n\s*(?:marks|type|difficulty)\s*:|$)/i)||[])[1] || '';
      const marks=(block.match(/(?:^|\n)\s*marks?\s*:\s*(\d+(?:\.\d+)?)/i)||[])[1] || defaults.marks;
      const typeValue=(block.match(/(?:^|\n)\s*(?:question\s*)?type\s*:\s*([^\n]+)/i)||[])[1] || defaults.questionType;
      const difficulty=(block.match(/(?:^|\n)\s*difficulty\s*:\s*([^\n]+)/i)||[])[1] || defaults.difficulty;
      items.push(normaliseQuestionRow({}, {...defaults,questionText:question.trim(),answer:answer.trim(),marks,questionType:typeValue,difficulty,sourceRow:items.length+1}));
    }
  }
  return items;
}

export function importFingerprint(item,teacherKey=''){
  return [teacherKey,item.className,item.section,item.subject,item.questionText]
    .map(value=>text(value).toLowerCase().replace(/\s+/g,' ')).join('|');
}

export function validateQuestionImports(items=[],subjects=[],options={}){
  const subjectMap=new Map(subjects.map(subject=>[String(subject).trim().toLowerCase(),subject]));
  const seen=new Set(),valid=[],duplicates=[];
  for(const original of items.slice(0,500)){
    const item={...original,errors:[]};
    if(!item.className) item.errors.push('Class is required');
    if(!item.subject) item.errors.push('Subject is required');
    else{
      const canonical=subjectMap.get(String(item.subject).trim().toLowerCase());
      if(!canonical) item.errors.push('Subject is not in the active QB Subjects list');
      else item.subject=canonical;
    }
    if(!item.questionText) item.errors.push('Question is required');
    if(!(Number(item.marks)>0)) item.errors.push('Marks must be greater than 0');
    if(options.requireTeacher && !(item.teacherCode || item.teacherEmail)) item.errors.push('Teacher Code or Teacher Email is required');
    const fingerprint=importFingerprint(item,item.teacherCode || item.teacherEmail || options.teacherKey || '');
    if(seen.has(fingerprint)){duplicates.push(item);continue}
    seen.add(fingerprint);
    valid.push(item);
  }
  return {items:valid,duplicates,overflow:Math.max(0,items.length-500),invalid:valid.filter(item=>item.errors.length)};
}
