import {fictionalTransferItems} from '/materials.mjs';
const items=fictionalTransferItems();
const arm=document.querySelector('#arm'),tutorial=document.querySelector('#tutorial');
const competition=document.querySelector('#competition'),questions=document.querySelector('#questions');
const progress=document.querySelector('#progress'),reset=document.querySelector('#reset');
function paragraph(parent,text){const p=document.createElement('p');p.textContent=text;parent.append(p)}
function renderCondition(){
 const t=arm.value==='transparency'||arm.value==='both';
 const l=arm.value==='leaderboard'||arm.value==='both';
 tutorial.replaceChildren();competition.replaceChildren();
 const h=document.createElement('h3');h.textContent=t?'Cómo se contabilizan las oportunidades':'Cómo navegar por el calendario';tutorial.append(h);
 paragraph(tutorial,t?'Una puntuación debe distinguir oportunidades anunciadas, intentos registrados y datos que aún no se han publicado. Un registro incompleto no demuestra cero actividad.':'Las jornadas de este juego corresponden a periodos del calendario inventado. Cada ficha describe un expediente y los actos registrados en la jornada. Lee las condiciones antes de interpretar cifras.');
 const lh=document.createElement('h3');lh.textContent=l?'Tabla de avatares simulados':'Actividad agregada de la jornada';competition.append(lh);
 paragraph(competition,l?'Ámbar: 8 puntos; Nube: 6 puntos; Prisma: 4 puntos. Son avatares imaginarios sin identidad política y cifras inventadas.':'Se han registrado 3 fichas ficticias en esta jornada de ejemplo. Sus valores no se atribuyen a personas y no se utilizan para juzgar méritos.');
}
function build(){
 for(const item of items){
  const fieldset=document.createElement('fieldset');const legend=document.createElement('legend');
  legend.textContent=item.id+' · '+item.question;fieldset.append(legend);
  paragraph(fieldset,item.scenario);
  for(let i=0;i<item.options.length;i++){
   const row=document.createElement('div');row.className='choice';
   const input=document.createElement('input');input.type='radio';input.name=item.id;
   input.id=item.id+'-'+i;input.value=String.fromCharCode(65+i);
   const label=document.createElement('label');label.htmlFor=input.id;label.textContent=item.options[i];
   row.append(input,label);fieldset.append(row)
  }
  questions.append(fieldset)
 }
}
function updateProgress(){
 const n=new Set([...questions.querySelectorAll('input:checked')].map(x=>x.name)).size;
 progress.textContent='Respuestas marcadas: '+n+' de '+items.length+'. Nada se envía ni se guarda.'
}
arm.addEventListener('change',renderCondition);
questions.addEventListener('change',updateProgress);
reset.addEventListener('click',()=>{
 for(const radio of questions.querySelectorAll('input:checked'))radio.checked=false;
 updateProgress()
});
build();renderCondition();
