(function(){
// Tablica ofert pracy keura.eu/praca i /en/ (10.11.2026, rozbudowa świat 11.2026). Dane: robot nocny (repozytorium nuclear-jobs) -> JSON w <script id="kp-dane">.
// Uwaga: skrypt trafia na stronę jako base64 (WordPress psuje „&&” w treści) - pisać normalnie, generator koduje.
var D=JSON.parse(document.getElementById('kp-dane').textContent);
var J=D.oferty, EN=D.jez==='en', LOC=EN?'en-GB':'pl-PL';
var $=function(i){return document.getElementById(i)};
var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
var IC={bud:'<path d="M3 21h18M5 21V10l7-5 7 5v11M9 21v-6h6v6"/>',eks:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/>',dos:'<path d="M3 21V9l6 4V9l6 4V5h6v16z"/>',doz:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',nau:'<path d="M10 3v6L4 19a1.5 1.5 0 001.3 2h13.4A1.5 1.5 0 0020 19l-6-10V3M8 3h8"/>',odp:'<path d="M4 7h16M6 7l1 13h10l1-13M9 7V4h6v3"/><circle cx="12" cy="13.5" r="2.2"/>',pin:'<path d="M12 21s-7-6.2-7-11.5A7 7 0 0119 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',brief:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2"/>',lvl:'<path d="M4 20V14M10 20V9M16 20V4"/>',cal:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'};
var svg=function(k){return '<svg viewBox="0 0 24 24">'+IC[k]+'</svg>'};
var T=EN?{
 sect:{bud:'Nuclear new build',eks:'Operating plants',dos:'Suppliers and manufacturing',doz:'Regulators and institutions',nau:'Research and fusion',odp:'Waste and decommissioning'},
 mode:{st:'On-site',hy:'Hybrid',zd:'Remote',np:'Work mode: not stated'},per:{mies:'month',rok:'year',godz:'hour'},
 f:{s:'Sector',k:'Country',l:'Job ad language',p:'Project',c:'City',e:'Employer',fn:'Area',lv:'Level',m:'Work mode',sal:'Salary'},
 salY:'Salary stated only',salN:'Salary not stated',noSal:'Salary not stated',gross:'gross',see:'View job →',added:'added',valid:'valid until',src:'Source',
 all:'All',more:'Show all',less:'Show less',empty:'No jobs match the selected filters.',stan:'as of',
 n:function(n){return n===1?'job':'jobs'},allC:'All countries',allL:'All languages',labC:'Country',labL:'Ad language'
}:{
 sect:{bud:'Budowa elektrowni jądrowych',eks:'Eksploatacja elektrowni',dos:'Dostawcy i produkcja',doz:'Dozór i instytucje',nau:'Nauka i fuzja',odp:'Odpady i wycofywanie'},
 mode:{st:'Stacjonarnie',hy:'Hybrydowo',zd:'Zdalnie',np:'Tryb pracy: nie podano'},per:{mies:'miesiąc',rok:'rok',godz:'godzinę'},
 f:{s:'Sektor',k:'Kraj',l:'Język ogłoszenia',p:'Projekt',c:'Miasto',e:'Pracodawca',fn:'Obszar',lv:'Poziom',m:'Tryb pracy',sal:'Wynagrodzenie'},
 salY:'Tylko z podanym wynagrodzeniem',salN:'Bez podanego wynagrodzenia',noSal:'Wynagrodzenie nie podane',gross:'brutto',see:'Zobacz ofertę →',added:'dodano',valid:'ważna do',src:'Źródło',
 all:'Wszystkie',more:'Pokaż wszystkie',less:'Pokaż mniej',empty:'Brak ofert dla wybranych filtrów.',stan:'stan na',
 n:function(n){return n===1?'oferta':(n%10>=2 && n%10<=4 && (n%100<12 || n%100>14)?'oferty':'ofert')},allC:'Wszystkie kraje',allL:'Wszystkie języki',labC:'Kraj',labL:'Język ogłoszenia'
};
var LV_EN={'Praktyka lub staż':'Internship','Kierownik':'Manager','Senior lub ekspert':'Senior or expert','Junior / wykonawczy':'Junior / operative','Specjalista':'Specialist'};
var FN_EN={'Zarządzanie projektem i planowanie':'Project management and planning','Zakupy i kontrakty':'Procurement and contracts','Administracja, HR i finanse':'Administration, HR and finance','BHP i ochrona środowiska (EHS)':'Health, safety and environment (EHS)','Budowa i montaż':'Construction and installation','Inżynieria i projektowanie':'Engineering and design','Jakość i kontrola (QA/QC)':'Quality (QA/QC)','IT i systemy':'IT and systems','Dozór i licencjonowanie':'Regulation and licensing','Bezpieczeństwo jądrowe i ochrona radiologiczna':'Nuclear safety and radiation protection','Szkolenie personelu eksploatacji':'Operator training','Produkcja i spawalnictwo':'Manufacturing and welding'};
var tr=function(m,v){return EN?(m[v]||v):v};
var NA_MIES={mies:1,rok:1/12,godz:168};
var K=D.kursy||{PLN:1};
var pln=function(s){if(!s)return 0;var k=K[s.cur]||(s.cur==='PLN'?1:0);return Math.round(((s.min+(s.max||s.min))/2)*NA_MIES[s.per]*k)};
var fmt=function(n){return Math.round(n).toLocaleString(LOC).replace(/[  ]/g,' ').replace(/,/g,EN?',':' ')};
var dd=function(iso){return iso?iso.slice(8,10)+'.'+iso.slice(5,7)+'.'+iso.slice(0,4):''};
var WAL={PLN:EN?'PLN':'zł',EUR:'EUR',GBP:'GBP',USD:'USD',CZK:'CZK',BGN:'BGN',RON:'RON',SEK:'SEK',AED:'AED',CAD:'CAD',CHF:'CHF'};
function salHtml(s){if(!s)return '<div class="sal no">'+T.noSal+'</div>';
 var r=s.max && s.max!==s.min?fmt(s.min)+' - '+fmt(s.max):fmt(s.min);
 var w=WAL[s.cur]||s.cur||'';
 var eq=(s.cur==='PLN' && s.per!=='mies')?(EN?' · approx. ':' · ok. ')+fmt(Math.round(s.min*NA_MIES[s.per]/100)*100)+' - '+fmt(Math.round((s.max||s.min)*NA_MIES[s.per]/100)*100)+(EN?' PLN / month':' zł / mies.'):'';
 var typ=s.cur==='PLN'?(s.typ||T.gross)+' / ':'/ ';
 return '<div class="sal">'+r+' '+w+'<small>'+typ+T.per[s.per]+eq+'</small></div>'}
var flag=function(k){return k?'<img src="https://flagcdn.com/w40/'+(k==='GB'?'gb':k.toLowerCase())+'.png" alt="" width="18" height="13" loading="lazy">':''};
var kraj=function(k){return (D.kraje||{})[k]||k};
var FACETS=[
 {id:'s',v:function(j){return j.s},lab:function(v){return T.sect[v]},open:1},
 {id:'p',v:function(j){return j.p},open:1,limit:8},
 {id:'c',v:function(j){return j.c},limit:6},
 {id:'e',v:function(j){return j.e},limit:6},
 {id:'fn',v:function(j){return j.fn},lab:function(v){return tr(FN_EN,v)},limit:6},
 {id:'lv',v:function(j){return j.lv},lab:function(v){return tr(LV_EN,v)}},
 {id:'m',v:function(j){return j.m},lab:function(v){return T.mode[v]}},
 {id:'sal',v:function(j){return j.sal?'z':'b'},lab:function(v){return v==='z'?T.salY:T.salN}}];
var TOP=[{id:'k',v:function(j){return j.k},lab:function(v){return flag(v)+esc(kraj(v))},all:T.allC,first:'PL',name:T.labC},
 {id:'l',v:function(j){return j.l},lab:function(v){return esc(v)},all:T.allL,first:EN?'EN':'PL',name:T.labL}];
var sel={},more={};FACETS.concat(TOP).forEach(function(f){sel[f.id]=new Set()});
var q='',sort='sal';
function pasuje(j,pomin){if(q && (j.t+' '+j.e+' '+j.c+' '+j.fn+' '+j.p+' '+kraj(j.k)).toLowerCase().indexOf(q)<0)return false;
 return FACETS.concat(TOP).every(function(f){return f.id===pomin || !sel[f.id].size || sel[f.id].has(f.v(j))})}
function wartosci(f){var m={};J.forEach(function(j){var v=f.v(j);if(v)m[v]=(m[v]||0)+1});return m}
function renderTop(){$('topf').innerHTML=TOP.map(function(f){var w=wartosci(f),vs=Object.keys(w);if(vs.length<2)return '';
 vs.sort(function(a,b){return (b===f.first)-(a===f.first)||w[b]-w[a]||String(a).localeCompare(String(b))});
 var ch=vs.map(function(v){var c=J.filter(function(j){return f.v(j)===v && pasuje(j,f.id)}).length;if(!c && !sel[f.id].has(v))return '';
  return '<button class="chip'+(sel[f.id].has(v)?' on':'')+'" data-t="'+f.id+'" data-v="'+esc(v)+'">'+f.lab(v)+' <small>'+c+'</small></button>'}).join('');
 return '<div class="row"><span class="lab">'+f.name+'</span><button class="chip'+(sel[f.id].size?'':' on')+'" data-t="'+f.id+'" data-v="">'+f.all+'</button>'+ch+'</div>'}).join('');
 $('topf').querySelectorAll('.chip').forEach(function(b){b.onclick=function(){var s=sel[b.dataset.t];if(!b.dataset.v)s.clear();else s.has(b.dataset.v)?s.delete(b.dataset.v):s.add(b.dataset.v);render()}})}
function renderFacets(){$('facets').innerHTML=FACETS.map(function(f){var w=wartosci(f),vs=Object.keys(w).filter(function(v){return J.some(function(j){return f.v(j)===v && pasuje(j,f.id)}) || sel[f.id].has(v)});
 if(vs.length<2 && !sel[f.id].size)return '';
 var cnt={};vs.forEach(function(v){cnt[v]=J.filter(function(j){return f.v(j)===v && pasuje(j,f.id)}).length});
 vs.sort(function(a,b){return cnt[b]-cnt[a]||String(a).localeCompare(String(b),LOC)});var lim=f.limit && !more[f.id]?f.limit:999;
 var rows=vs.slice(0,lim).map(function(v){
  return '<label class="opt'+(cnt[v]||sel[f.id].has(v)?'':' zero')+'"><input type="checkbox" data-f="'+f.id+'" value="'+esc(v)+'"'+(sel[f.id].has(v)?' checked':'')+'>'+esc(f.lab?f.lab(v):v)+'<span class="c">'+cnt[v]+'</span></label>'}).join('');
 var mo=f.limit && vs.length>f.limit?'<button class="more" data-more="'+f.id+'">'+(more[f.id]?T.less:T.more+' ('+vs.length+')')+'</button>':'';
 return '<details class="fg"'+(f.open || sel[f.id].size?' open':'')+'><summary>'+T.f[f.id]+(sel[f.id].size?' · '+sel[f.id].size:'')+'</summary>'+rows+mo+'</details>'}).join('');
 $('facets').querySelectorAll('input').forEach(function(i){i.onchange=function(){var s=sel[i.dataset.f];i.checked?s.add(i.value):s.delete(i.value);render()}});
 $('facets').querySelectorAll('[data-more]').forEach(function(b){b.onclick=function(){more[b.dataset.more]=!more[b.dataset.more];renderFacets()}})}
function renderSectors(){var w={};J.forEach(function(j){if(pasuje(j,'s'))w[j.s]=(w[j.s]||0)+1});
 $('sectors').innerHTML=Object.keys(T.sect).filter(function(k){return w[k] || sel.s.has(k)}).map(function(k){var n=w[k]||0;return '<button class="sec'+(sel.s.has(k)?' on':'')+'" data-s="'+k+'"><span class="ic">'+svg(k)+'</span><span><b>'+T.sect[k]+'</b><span class="n">'+n+' '+T.n(n)+'</span></span></button>'}).join('');
 $('sectors').querySelectorAll('.sec').forEach(function(b){b.onclick=function(){var k=b.dataset.s;sel.s.has(k)?sel.s.delete(k):sel.s.add(k);render()}})}
function karta(j){var src=j.u.replace(/^https?:\/\/(www\.)?/,'').split('/')[0];
 return '<article class="job"><div class="h"><div><h3>'+esc(j.t)+'</h3><div class="firm">'+esc(j.e)+'</div></div><div class="right">'+salHtml(j.sal)+'<a class="btn" href="'+esc(j.u)+'" target="_blank" rel="noopener">'+T.see+'</a></div></div>'
 +'<div class="meta"><span>'+flag(j.k)+esc((j.c?j.c+', ':'')+kraj(j.k))+'</span>'+(j.l?'<span class="lng" title="'+T.f.l+'">'+esc(j.l)+'</span>':'')+'<span class="mode '+j.m+'">'+T.mode[j.m]+'</span><span>'+svg('brief')+esc(tr(FN_EN,j.fn))+'</span><span class="muted">'+svg('lvl')+esc(tr(LV_EN,j.lv))+'</span></div>'
 +'<div class="tags"><span class="tag">'+esc(T.sect[j.s])+'</span>'+(j.p?'<span class="tag st">'+esc(j.p)+'</span>':'')+'</div>'
 +'<div class="foot"><span>'+svg('cal')+(j.pub?T.added+' '+dd(j.pub):'')+(j.dl?(j.pub?' · ':'')+T.valid+' '+dd(j.dl):'')+'</span><span>'+T.src+': <a href="'+esc(j.u)+'" target="_blank" rel="noopener">'+esc(src)+'</a></span></div></article>'}
function render(){var L=J.filter(function(j){return pasuje(j)});
 L.sort(sort==='sal'?function(a,b){return pln(b.sal)-pln(a.sal)}:sort==='new'?function(a,b){return (b.pub||'').localeCompare(a.pub||'')}:function(a,b){return (a.dl||'9').localeCompare(b.dl||'9')});
 $('count').innerHTML=L.length+' '+T.n(L.length)+' <small>· '+T.stan+' '+dd(D.stan)+'</small>';
 $('list').innerHTML=L.length?L.map(karta).join(''):'<div class="empty">'+T.empty+'</div>';
 var a=[];FACETS.concat(TOP).forEach(function(f){sel[f.id].forEach(function(v){a.push('<button class="pill" data-f="'+f.id+'" data-v="'+esc(v)+'">'+(f.id==='k'?esc(kraj(v)):esc(f.lab && f.id!=='l'?String(f.lab(v)).replace(/<[^>]+>/g,''):v))+' ×</button>')})});
 $('active').innerHTML=a.join('');$('active').querySelectorAll('.pill').forEach(function(p){p.onclick=function(){sel[p.dataset.f].delete(p.dataset.v);render()}});
 renderTop();renderSectors();renderFacets()}
$('fN').textContent=J.length;$('fE').textContent=new Set(J.map(function(j){return j.e})).size;$('fK').textContent=new Set(J.map(function(j){return j.k})).size;$('fS').textContent=J.filter(function(j){return j.sal}).length;$('fD').textContent=dd(D.stan);
$('q').oninput=function(){q=this.value.trim().toLowerCase();render()};$('qbtn').onclick=function(){q=$('q').value.trim().toLowerCase();render()};
['sort','sortM'].forEach(function(id){$(id).onchange=function(){sort=this.value;$('sort').value=$('sortM').value=sort;render()}});
$('reset').onclick=function(){FACETS.concat(TOP).forEach(function(f){sel[f.id].clear()});q='';$('q').value='';render()};
$('openF').onclick=function(){$('panel').classList.add('open')};$('apply').onclick=function(){$('panel').classList.remove('open')};
render();
})();
