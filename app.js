document.documentElement.classList.add("js");
const hd=document.getElementById('top'),nav=document.getElementById('nav'),bg=document.querySelector('.burger');
const onS=()=>hd.classList.toggle('solid',scrollY>60);onS();addEventListener('scroll',onS,{passive:true});
bg.onclick=()=>{const o=nav.classList.toggle('open');bg.setAttribute('aria-expanded',o);hd.classList.toggle('solid',o||scrollY>60)};
const io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
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
  const push=()=>{hd.style.top=flash.classList.contains('show')?flash.offsetHeight+'px':'0'};
  const show=()=>{flash.classList.add('show');push()};
  const hide=()=>{flash.classList.remove('show');push()};
  addEventListener('resize',push);
  try{if(!sessionStorage.getItem('flashDismissed'))setTimeout(show,400)}catch(e){show()}
  flash.querySelector('.flash-x').onclick=()=>{hide();try{sessionStorage.setItem('flashDismissed','1')}catch(e){}};
}
