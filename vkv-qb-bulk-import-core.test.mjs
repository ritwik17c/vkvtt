import assert from 'node:assert/strict';
import {parseWordQuestionText,validateQuestionImports} from './vkv-qb-bulk-import-core.js';

const defaults={className:'VII',subject:'English',marks:1,difficulty:'Moderate',questionType:'Short Answer'};

{
  const source=`Class: VIII\nSubject: Science\nChapter: Coal and Petroleum\nTopic: Fossil Fuels\n\n1. What is coal? (2 marks)\nAnswer: Coal is a fossil fuel.\n2. Why should fossil fuels be conserved?`;
  const items=parseWordQuestionText(source,defaults);
  assert.equal(items.length,2);
  assert.equal(items[0].className,'VIII');
  assert.equal(items[0].subject,'Science');
  assert.equal(items[0].chapter,'Coal and Petroleum');
  assert.equal(items[0].topic,'Fossil Fuels');
  assert.equal(items[0].marks,2);
  assert.equal(items[0].answer,'Coal is a fossil fuel.');
  assert.equal(items[1].chapter,'Coal and Petroleum');
}

{
  const source=`Class: IX\nSubject: English\n\n1. Explain the title.\nChapter: The Fun They Had\nTopic: Theme\nAnswer: The title refers to the old kind of school.\n2. Write a character sketch of Margie.`;
  const items=parseWordQuestionText(source,defaults);
  assert.equal(items.length,2);
  assert.equal(items[0].chapter,'The Fun They Had');
  assert.equal(items[0].topic,'Theme');
  assert.equal(items[1].chapter,'');
  assert.equal(items[1].topic,'');
  assert.equal(items[1].className,'IX');
  assert.equal(items[1].subject,'English');
}

{
  const source=`Class: VIII\nSubject: Science\nChapter: Coal and Petroleum\nTopic: Fossil Fuels\n\n1. What is coal?\nAnswer: Coal is a fossil fuel.\n\nChapter: Combustion and Flame\nTopic: Types of Combustion\n\n2. Define rapid combustion.\n3. Give one example of rapid combustion.`;
  const items=parseWordQuestionText(source,defaults);
  assert.equal(items.length,3);
  assert.equal(items[0].chapter,'Coal and Petroleum');
  assert.equal(items[0].topic,'Fossil Fuels');
  assert.equal(items[1].chapter,'Combustion and Flame');
  assert.equal(items[1].topic,'Types of Combustion');
  assert.equal(items[2].chapter,'Combustion and Flame');
  assert.equal(items[2].topic,'Types of Combustion');
  assert.equal(items[0].questionText,'What is coal?');
}

{
  const source=`Class: X\nSubject: Science\nChapter: Light\n\n1. State the laws of reflection.\n\nChapter: Human Eye\n\n2. What is accommodation?\n3. Name one defect of vision.`;
  const items=parseWordQuestionText(source,defaults);
  assert.equal(items.length,3);
  assert.equal(items[0].chapter,'Light');
  assert.equal(items[1].chapter,'Human Eye');
  assert.equal(items[2].chapter,'Human Eye');
}

{
  const source=`1. What is photosynthesis?\n2. State one product of photosynthesis.`;
  const items=parseWordQuestionText(source,defaults);
  assert.equal(items.length,2);
  assert.equal(items[0].className,'VII');
  assert.equal(items[0].subject,'English');
}

{
  const items=parseWordQuestionText(`Class: VIII\nSubject: Science\n\n1. Define combustion.`,defaults);
  const result=validateQuestionImports(items,['Science','English'],{teacherKey:'TEST'});
  assert.equal(result.invalid.length,0);
}

console.log('QB Word metadata parser regression tests passed.');
