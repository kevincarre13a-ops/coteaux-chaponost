document.documentElement.classList.add("js");
const hd=document.getElementById('top'),nav=document.getElementById('nav'),bg=document.querySelector('.burger');
const onS=()=>hd.classList.toggle('solid',scrollY>60);onS();addEventListener('scroll',onS,{passive:true});
bg.onclick=()=>{const o=nav.classList.toggle('open');bg.setAttribute('aria-expanded',o);hd.classList.toggle('solid',o||scrollY>60)};
const rv=[...document.querySelectorAll('.reveal')],showAll=()=>rv.forEach(el=>el.classList.add('in'));
if(!('IntersectionObserver' in window))showAll();
else{
  const io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});
  rv.forEach(el=>io.observe(el));
  /* filet de sécurité : certains navigateurs (ouverture d'un QR code, aperçus) ne signalent rien ; on affiche alors le contenu quand même */
  const sweep=()=>rv.forEach(el=>{if(!el.classList.contains('in')&&el.getBoundingClientRect().top<innerHeight*.95)el.classList.add('in')});
  addEventListener('scroll',sweep,{passive:true});addEventListener('resize',sweep);
  setTimeout(sweep,300);setTimeout(sweep,1200);setTimeout(showAll,4000);
}
const filterBtns=[...document.querySelectorAll('[data-f]')];
filterBtns.forEach(b=>b.onclick=()=>{
  if(b.dataset.f==='vid'){const v=document.querySelector('.videos');if(v){v.scrollIntoView({behavior:'smooth',block:'start'});v.classList.remove('pulse');void v.offsetWidth;v.classList.add('pulse')}return}
  filterBtns.forEach(x=>x.classList.remove('on'));b.classList.add('on');
  document.querySelectorAll('.tile').forEach(t=>t.classList.toggle('hide',b.dataset.f!=='all'&&t.dataset.cat!==b.dataset.f));
});
const lb=document.getElementById('lb');if(lb){document.querySelectorAll('.tile').forEach(t=>t.onclick=e=>{e.preventDefault();lb.querySelector('img').src=t.href;lb.querySelector('p').textContent=t.dataset.cap;lb.classList.add('on')});lb.onclick=()=>lb.classList.remove('on')}
if(location.hash){const k=location.hash.slice(1),btn=document.querySelector(`[data-f="${k}"]`);if(btn)btn.click()}
const flash=document.getElementById('flash');
if(flash){
  const show=()=>flash.classList.add('show');
  const hide=()=>flash.classList.remove('show');
  try{if(!sessionStorage.getItem('flashDismissed'))setTimeout(show,400)}catch(e){show()}
  flash.querySelector('.flash-x').onclick=()=>{hide();try{sessionStorage.setItem('flashDismissed','1')}catch(e){}};
}
document.addEventListener('click',e=>{const i=e.target.closest&&e.target.closest('img.pimg');if(i&&!document.body.classList.contains('editing')&&!i.classList.contains('empty'))window.open(i.src,'_blank')});
