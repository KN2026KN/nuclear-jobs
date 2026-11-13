(function(){
var $=function(i){return document.getElementById(i)};
var D=JSON.parse($('kz-dane').textContent),R=D.rekordy||[],Z=D.zawody||{},KU=D.kursy||{},EBC=(KU.ebc||{}).kursy||{'EUR':1},PPP=((KU.ppp||{}).kraje)||{},WK=KU.waluty_krajow||{};
var KRAJ={PL:'Polska',GB:'Wielka Brytania',US:'USA',CA:'Kanada',FR:'Francja',DE:'Niemcy',SE:'Szwecja',FI:'Finlandia',CZ:'Czechy',SK:'Słowacja',RO:'Rumunia',BG:'Bułgaria',HU:'Węgry',IT:'Włochy',ES:'Hiszpania',BE:'Belgia',NL:'Holandia',CH:'Szwajcaria',AT:'Austria',CN:'Chiny',KR:'Korea Płd.',JP:'Japonia',AE:'ZEA',TR:'Turcja',IN:'Indie',RU:'Rosja',BY:'Białoruś',UA:'Ukraina',SI:'Słowenia',LT:'Litwa',NO:'Norwegia',EG:'Egipt',ZA:'RPA',AU:'Australia',EMU:'strefa euro'};
var WALUTY=['EUR','PLN','GBP','USD','SEK','CZK','CHF','RON','HUF','BGN','NOK','DKK','CAD','TRY','CNY','KRW','JPY','INR','AED'].filter(function(w){return EBC[w]});Object.keys(EBC).sort().forEach(function(w){if(WALUTY.indexOf(w)<0)WALUTY.push(w)});
var kr=function(k){return KRAJ[k]||k},fl=function(k){return /^[A-Z]{2}$/.test(k)?'<img src="https://flagcdn.com/w40/'+k.toLowerCase()+'.png" alt="">':''};
var esc=function(s){return String(s==null?'':s).replace(/[<>"]/g,function(c){return {'<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
// domyślna waluta z języka przeglądarki
var JW={pl:'PLN',en:'EUR','en-gb':'GBP','en-us':'USD',sv:'SEK',cs:'CZK',ro:'RON',hu:'HUF',bg:'BGN',de:'EUR',fr:'EUR',it:'EUR',es:'EUR',fi:'EUR',sk:'EUR',nb:'NOK',da:'DKK',tr:'TRY',zh:'CNY',ko:'KRW',ja:'JPY'};
var jl=(navigator.language||'en').toLowerCase(),dw=JW[jl]||JW[jl.slice(0,2)]||'EUR';
var KJ={PLN:'PL',GBP:'GB',USD:'US',SEK:'SE',CZK:'CZ',CHF:'CH',RON:'RO',HUF:'HU',BGN:'BG',NOK:'NO',DKK:'DK',CAD:'CA',TRY:'TR',CNY:'CN',KRW:'KR',JPY:'JP',INR:'IN',AED:'AE',EUR:'EMU'};
function opt(id,list,sel){$(id).innerHTML=list.map(function(x){return '<option value="'+esc(x[0])+'"'+(x[0]===sel?' selected':'')+'>'+esc(x[1])+'</option>'}).join('')}
opt('cur',WALUTY.map(function(w){return [w,w]}),dw);
opt('cur2',[['','bez drugiej waluty']].concat(WALUTY.map(function(w){return [w,w]})),dw==='EUR'?'':'EUR');
var refs=Object.keys(KJ).filter(function(w){return PPP[KJ[w]]}).map(function(w){return [KJ[w],kr(KJ[w])+' ('+w+')']});
opt('ref',refs,KJ[dw]||'EMU');
var obs={};R.forEach(function(r){obs[r.ob]=1});opt('ob',[['','wszystkie obszary']].concat(Object.keys(obs).sort().map(function(o){return [o,o]})),'');
var Y=new Date().getFullYear();opt('lata',[['2','ostatnie 2 lata'],['5','ostatnie 5 lat'],['0','wszystkie lata'],['1','tylko bieżący rok']],'2');
// podpowiedzi zawodów
var zl=Object.keys(Z).map(function(k){return Z[k].pl});$('zl').innerHTML=zl.map(function(n){return '<option value="'+esc(n)+'">'}).join('');
var licz={};R.forEach(function(r){licz[r.z]=(licz[r.z]||0)+1});
var top=Object.keys(licz).filter(function(k){return k!=='inne'}).sort(function(a,b){return licz[b]-licz[a]}).slice(0,14);
$('chips').innerHTML=top.map(function(k){return '<button data-z="'+k+'">'+esc((Z[k]||{}).pl||k)+' <span class="mut">'+licz[k]+'</span></button>'}).join('');
var stan={q:'',z:'',t:'kraje',cmp:[],jez:'',wRecz:false};
var SL=D.slownik||{},JZ=D.jezyki||{},JW2=D.jezyk_waluta||{};
var norm=function(x){return String(x||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ё/g,'е').replace(/[^a-z0-9а-яіїєґ&\s-]/g,' ').replace(/\s+/g,' ').trim()};
var IDX=[];Object.keys(SL).forEach(function(k){Object.keys(SL[k]).forEach(function(j){SL[k][j].forEach(function(w){IDX.push({k:k,j:j,w:w,n:norm(w)})})})});
Object.keys(Z).forEach(function(k){[['pl',Z[k].pl],['en',Z[k].en]].forEach(function(p){IDX.push({k:k,j:p[0],w:p[1],n:norm(p[1])})})});
function szukaj(q){var n=norm(q);if(n.length<3)return [];var wyn=[];
  IDX.forEach(function(e){var sc=0;if(e.n===n)sc=100;else if(e.n.indexOf(n)===0)sc=80-Math.min(30,e.n.length-n.length);else if(n.indexOf(e.n)===0&&e.n.length>=4)sc=60;else if((' '+e.n).indexOf(' '+n)>=0)sc=50;else if(n.length>=5&&e.n.length>=5&&n.slice(0,5)===e.n.slice(0,5))sc=35;
   if(sc)wyn.push({k:e.k,j:e.j,w:e.w,sc:sc+(e.k==='inzynier'||e.k==='specjalista'||e.k==='kierownik'?-15:0)})});
  wyn.sort(function(a,b){return b.sc-a.sc});var by={},out=[];wyn.forEach(function(x){if(!by[x.k]){by[x.k]=1;out.push(x)}});return out.slice(0,5)}
function jezykZ(q,traf){if(/[а-яё]/i.test(q)){if(/[іїєґ]/i.test(q))return 'uk';if(traf&&(traf.j==='bg'||traf.j==='uk'||traf.j==='ru'))return traf.j;return 'ru'}return traf?traf.j:''}
function ustawWalute(j){if(stan.wRecz||!j)return;var w=JW2[j];if(w&&EBC[w]&&WALUTY.indexOf(w)>=0)$('cur').value=w}
// przeliczenia
function naEUR(v,w){return EBC[w]?v/EBC[w]:null}
function ppKraj(r){var k=r.k;return PPP[k]?PPP[k].ppp:null}
function wartosc(r,v){ // v w walucie r.w, roczna -> w walucie wyświetlania
  var cur=$('cur').value;
  if($('pp').checked){var ref=$('ref').value,wk=WK[r.k]||r.w,p=ppKraj(r),pr=PPP[ref]?PPP[ref].ppp:null;if(!p||!pr)return null;
    var vl=r.w===wk?v:(naEUR(v,r.w)*(EBC[wk]||NaN)); return vl/p*pr;}
  var e=naEUR(v,r.w);return e==null?null:e*(EBC[cur]||1);
}
function walPP(){if(!$('pp').checked)return $('cur').value;var ref=$('ref').value;for(var w in KJ)if(KJ[w]===ref)return w;return 'EUR'}
function fmt(v,w){if(v==null||isNaN(v))return '-';var a=Math.abs(v);var s=a>=1e6?(v/1e6).toFixed(1).replace('.',',')+' mln':a>=10000?Math.round(v/1000)+' tys.':Math.round(v).toLocaleString('pl-PL');return s+' '+w}
function w2(vEUR){var c2=$('cur2').value;if(!c2||$('pp').checked||vEUR==null)return '';return fmt(vEUR*EBC[c2],c2)}
function pasuje(r){
  if(!$('wa').checked&&r.s==='o')return false;if(!$('wz').checked&&r.s==='c')return false;if(!$('wr').checked&&r.s==='a')return false;
  if(!$('wx').checked&&r.a)return false;var ob=$('ob').value;if(ob&&r.ob!==ob)return false;
  var l=+$('lata').value;if(l&&r.y<Y-l+1)return false;
  if(stan.z&&r.z!==stan.z)return false;
  if(stan.q&&!stan.z){var q=stan.q.toLowerCase();if((r.t+' '+r.e).toLowerCase().indexOf(q)<0)return false}
  return true;
}
function kw(a,p){if(!a.length)return null;var i=(a.length-1)*p,lo=Math.floor(i),hi=Math.ceil(i);return a[lo]+(a[hi]-a[lo])*(i-lo)}
function grupuj(klucz){var g={};R.forEach(function(r){if(!pasuje(r))return;var v=wartosc(r,(r.lo+r.hi)/2);if(v==null||v<1000)return;var k=klucz(r);(g[k]=g[k]||{v:[],e:[],r:[]}).v.push(v);g[k].e.push(naEUR((r.lo+r.hi)/2,r.w));g[k].r.push(r)});
  return Object.keys(g).map(function(k){var a=g[k].v.sort(function(x,y){return x-y}),e=g[k].e.sort(function(x,y){return x-y});return {k:k,n:a.length,min:a[0],max:a[a.length-1],p25:kw(a,.25),med:kw(a,.5),p75:kw(a,.75),medE:kw(e,.5),r:g[k].r}}).sort(function(a,b){return b.med-a.med})}
function lista(gr,nazwa){
  if(!gr.length)return '<div class="pusto">Brak ofert z wynagrodzeniem dla tych warunków.</div>';
  var mx=0;gr.forEach(function(g){mx=Math.max(mx,g.p75*1.15,g.med*1.3)});gr.forEach(function(g){if(g.max<mx*1.6)mx=Math.max(mx,g.max)});
  var W=walPP(),p=function(v){return Math.min(100,v/mx*100)+'%'};
  var h='<div class="skala"><span>0</span><span>'+fmt(mx/2,W)+'</span><span>'+fmt(mx,W)+'</span></div><div class="lst">';
  gr.forEach(function(g){h+='<div class="nm" title="'+esc(nazwa(g.k,1))+'">'+nazwa(g.k,0,g)+(g.n<5?'<span class="mal">mało danych</span>':'')+'</div>'+
   '<div class="bar"><div class="ax"></div><div class="mm" style="left:'+p(g.min)+';width:calc('+p(g.max)+' - '+p(g.min)+')"></div><div class="iq" style="left:'+p(g.p25)+';width:calc('+p(g.p75)+' - '+p(g.p25)+')"></div><div class="md" style="left:'+p(g.med)+'" title="mediana '+fmt(g.med,W)+'"></div></div>'+
   '<div class="val">'+fmt(g.med,W)+'<small>'+(w2(g.medE)?w2(g.medE)+' · ':'')+g.n+' ofert</small></div>'});
  return h+'</div>';
}
function nKraj(k,raw){return raw?kr(k):fl(k)+esc(kr(k))}
function nFirma(k,raw,g){return raw?k:(g&&g.r[0]?fl(g.r[0].k):'')+esc(k)}
function nZaw(k,raw){return raw?((Z[k]||{}).pl||k):esc((Z[k]||{}).pl||k)}
function render(){
  var o='',t=stan.t;
  if(t==='kraje')o=lista(grupuj(function(r){return r.k}),nKraj);
  else if(t==='firmy')o=lista(grupuj(function(r){return r.e||'?'}).slice(0,40),nFirma);
  else if(t==='zaw')o=lista(grupuj(function(r){return r.z}),nZaw);
  else if(t==='cmp')o=porownanie();
  else if(t==='jaw')o=jawnosc();
  else o=tabela();
  $('out').innerHTML=o;$('leg').style.display=(t==='lista'||t==='cmp'||t==='jaw')?'none':'block';
  var n=R.filter(pasuje).length;
  $('sub').innerHTML='Ofert z wynagrodzeniem w wyborze: <b>'+n+'</b> z '+R.length+' · '+(stan.z?'zawód: <b>'+esc((Z[stan.z]||{}).pl)+'</b>':stan.q?'szukane: <b>'+esc(stan.q)+'</b>':'wszystkie zawody')+' · dane z '+esc(D.wygenerowano)+' · kursy EBC z '+esc((KU.ebc||{}).data||'-');
  [].forEach.call(document.querySelectorAll('#chips button'),function(b){b.classList.toggle('on',b.getAttribute('data-z')===stan.z)});
  $('pppinfo').style.display=$('pp').checked?'block':'none';$('refw').style.display=$('pp').checked?'inline':'none';$('cur').disabled=$('pp').checked;$('cur2').disabled=$('pp').checked;
  if($('pp').checked){var ref=$('ref').value,pr=PPP[ref]||{};$('pppinfo').innerHTML='<b>Siła nabywcza (parytet siły nabywczej, PPP)</b> pokazuje, ile pensja jest naprawdę warta po uwzględnieniu cen w kraju, w którym się ją dostaje. Ta sama kwota w złotych kupuje w Polsce więcej niż jej równowartość w funtach w Londynie, bo ceny w Wielkiej Brytanii są wyższe. Po włączeniu przeliczamy każdą pensję tak, jakby wydawać ją przy cenach w kraju: <b>'+esc(kr(ref))+'</b>. Przykład: „90 tys. '+esc(walPP())+'” przy ofercie z innego kraju oznacza, że ta pensja daje tam taki poziom życia, jak '+'90 tys. '+esc(walPP())+' w kraju: '+esc(kr(ref))+'. Źródło: Bank Światowy, wskaźnik PA.NUS.PPP (rok '+esc(pr.rok||'-')+(ref==='EMU'?', strefa euro = mediana krajów strefy euro':'')+'). To porównanie poziomu życia, a nie kwota do wypłaty: do przeliczenia samej kwoty służy wybór waluty (kurs EBC).'}
}
function porownanie(){
  var gk=grupuj(function(r){return 'K:'+r.k}),gf=grupuj(function(r){return 'F:'+(r.e||'?')}),all=gk.concat(gf),W=walPP();
  var opts=all.filter(function(g){return g.n>=1}).map(function(g){return [g.k,(g.k[0]==='K'?'Kraj: '+kr(g.k.slice(2)):'Firma: '+g.k.slice(2))+' ('+g.n+')']});
  var sel=stan.cmp.length?stan.cmp:all.slice(0,3).map(function(g){return g.k});
  var h='<p class="mut" style="margin:0 0 10px">Wybierz do 3 krajów lub pracodawców (przy wybranym zawodzie lub frazie porównanie dotyczy tylko jej).</p><div class="fl" style="grid-template-columns:repeat(3,1fr);margin:0 0 12px">';
  for(var i=0;i<3;i++)h+='<div><select data-c="'+i+'">'+'<option value="">-</option>'+opts.map(function(o){return '<option value="'+esc(o[0])+'"'+(o[0]===sel[i]?' selected':'')+'>'+esc(o[1])+'</option>'}).join('')+'</select></div>';
  h+='</div><div class="cmp">';var baza=null;
  sel.forEach(function(k){var g=all.filter(function(x){return x.k===k})[0];if(!g)return;if(baza==null)baza=g.med;var d=baza?Math.round((g.med/baza-1)*100):0;
    h+='<div class="k"><span class="mut">'+(k[0]==='K'?fl(k.slice(2))+' '+esc(kr(k.slice(2))):esc(k.slice(2)))+'</span><b>'+fmt(g.med,W)+'</b><span class="mut">mediana · połowa ofert: '+fmt(g.p25,W)+' - '+fmt(g.p75,W)+'</span><br><span class="mut">'+g.n+' ofert'+(g.n<5?' <span class="mal">mało danych</span>':'')+(w2(g.medE)?' · '+w2(g.medE):'')+'</span>'+(d?'<br><b style="font-size:16px;color:'+(d>0?'#0f7c78':'#b42318')+'">'+(d>0?'+':'')+d+'% wobec pierwszego</b>':'')+'</div>'});
  return h+'</div>';
}
function jawnosc(){
  var JA=D.jawnosc||{k:{},f:{}},Y0=Y-5,ys=[];for(var y=Y0;y<=Y;y++)ys.push(String(y));
  function wiersz(nazwa,L,n){var tn=0,tz=0;ys.forEach(function(y){var a=L[y];if(a){tn+=a[0];tz+=a[1]}});if(tn<n)return null;
    return {h:'<tr><td>'+nazwa+'</td>'+ys.map(function(y){var a=L[y];if(!a||!a[0])return '<td class="n mut">-</td>';var p=Math.round(a[1]/a[0]*100);return '<td class="n" title="'+a[1]+' z '+a[0]+' ofert"><span class="proc" style="color:'+(p>=50?'#0f7c78':p>=10?'#0b2b3c':'#94a3b8')+'">'+p+'%</span></td>'}).join('')+'<td class="n"><b>'+Math.round(tz/tn*100)+'%</b><br><span class="mut">'+tz+' z '+tn+'</span></td></tr>',p:tz/tn,n:tn}}
  var kr2=Object.keys(JA.k).map(function(k){return wiersz(fl(k)+' '+esc(kr(k)),JA.k[k],5)}).filter(Boolean).sort(function(a,b){return b.p-a.p||b.n-a.n});
  var fi=Object.keys(JA.f).map(function(f){return wiersz(fl(JA.f[f].k)+' '+esc(f),JA.f[f].y,10)}).filter(Boolean).sort(function(a,b){return b.p-a.p||b.n-a.n}).slice(0,40);
  var th='<tr><th></th>'+ys.map(function(y){return '<th class="n">'+y+'</th>'}).join('')+'<th class="n">Razem</th></tr>';
  return '<p class="mut" style="margin:0 0 10px">Jaki odsetek ofert podaje wynagrodzenie (wszystkie oferty jądrowe, także bez kwoty; lata przed bieżącym - z archiwów). Dyrektywa (UE) 2023/970 wymaga podania płacy w ogłoszeniu albo przed rozmową, więc wzrost w krajach UE pokaże, jak pracodawcy ją stosują.</p><h3 style="margin:6px 0">Kraje (min. 5 ofert)</h3><div style="overflow-x:auto"><table>'+th+kr2.map(function(x){return x.h}).join('')+'</table></div><h3 style="margin:16px 0 6px">Pracodawcy (min. 10 ofert, 40 pierwszych)</h3><div style="overflow-x:auto"><table>'+th+fi.map(function(x){return x.h}).join('')+'</table></div>';
}
function tabela(){
  var rr=R.filter(pasuje).map(function(r){return {r:r,v:wartosc(r,(r.lo+r.hi)/2)}}).filter(function(x){return x.v}).sort(function(a,b){return b.v-a.v}).slice(0,300),W=walPP();
  if(!rr.length)return '<div class="pusto">Brak ofert.</div>';
  var S={o:'otwarta',c:'zamknięta',a:'archiwum'};
  return '<div style="overflow-x:auto"><table><thead><tr><th>Stanowisko</th><th>Pracodawca</th><th>Kraj</th><th>Rok</th><th>Wynagrodzenie roczne</th><th>W ofercie</th></tr></thead><tbody>'+rr.map(function(x){var r=x.r,lo=wartosc(r,r.lo),hi=wartosc(r,r.hi);
   return '<tr><td><a href="'+esc(r.u)+'" target="_blank" rel="noopener">'+esc(r.t)+'</a><br><span class="mut">'+esc((Z[r.z]||{}).pl||'')+' · '+S[r.s]+'</span></td><td>'+esc(r.e)+'</td><td>'+fl(r.k)+' '+esc(kr(r.k))+'</td><td>'+r.y+'</td><td class="n">'+(Math.round(lo)===Math.round(hi)?fmt(lo,W):fmt(lo,W)+' - '+fmt(hi,W))+(w2(naEUR(r.lo,r.w))?'<br><small class="mut">'+w2(naEUR((r.lo+r.hi)/2,r.w))+'</small>':'')+'</td><td class="mut">'+Math.round(r.lo).toLocaleString('pl-PL')+(r.hi!==r.lo?' - '+Math.round(r.hi).toLocaleString('pl-PL'):'')+' '+esc(r.w)+'/rok<br>(podano: '+({rok:'rocznie',mies:'miesięcznie',godz:'za godzinę'}[r.per]||r.per)+')</td></tr>'}).join('')+'</tbody></table></div>';
}
// zdarzenia
function zQ(v){v=(v||'').trim();stan.q=v;stan.z='';stan.jez='';var t=szukaj(v);
  if(t.length&&t[0].sc>=50){stan.z=t[0].k;stan.jez=jezykZ(v,t[0]);ustawWalute(stan.jez)}else if(v){stan.jez=jezykZ(v,null)}
  var h='';if(stan.z){h='Rozpoznano: <b>'+esc(Z[stan.z].pl)+'</b> ('+esc(Z[stan.z].en)+')'+(stan.jez?' · język: '+esc(JZ[stan.jez]||stan.jez):'')+(stan.jez&&JW2[stan.jez]&&!stan.wRecz?' · waluta: '+esc($('cur').value):'');
   var inne=t.slice(1).filter(function(x){return x.sc>=60}).slice(0,3);if(inne.length)h+=' · może chodzi o: '+inne.map(function(x){return '<button data-z="'+x.k+'">'+esc(Z[x.k].pl)+'</button>'}).join(', ')}
  else if(v.length>=3)h='Nie rozpoznano zawodu - szukam frazy w tytułach ofert.';
  $('jez').innerHTML=h;render()}
$('jez').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;stan.z=b.getAttribute('data-z');$('jez').innerHTML='Wybrano: <b>'+esc(Z[stan.z].pl)+'</b>';render()});
$('cur').addEventListener('change',function(){stan.wRecz=true});
var tq;$('q').addEventListener('input',function(){clearTimeout(tq);var v=this.value;tq=setTimeout(function(){zQ(v)},200)});
$('chips').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var z=b.getAttribute('data-z');stan.z=stan.z===z?'':z;stan.q='';$('q').value=stan.z?(Z[z]||{}).pl:'';render()});
$('tabs').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;stan.t=b.getAttribute('data-t');[].forEach.call(this.children,function(x){x.classList.toggle('on',x===b)});render()});
['cur','cur2','ob','lata','pp','ref','wa','wz','wr','wx'].forEach(function(i){$(i).addEventListener('change',render)});
$('out').addEventListener('change',function(e){var s=e.target;if(s.getAttribute('data-c')==null)return;var i=+s.getAttribute('data-c');var sel=stan.cmp.length?stan.cmp:[].map.call(document.querySelectorAll('#out select'),function(x){return x.value});sel[i]=s.value;stan.cmp=sel;render()});
var G=KU.godziny_rok||{};
$('zas').innerHTML='<b>Jak liczymy.</b> Tylko oferty, w których pracodawca sam podał wynagrodzenie (otwarte, zamknięte i z archiwów Internet Archive z poprzednich lat). Kwoty sprowadzone do rocznych brutto: miesięczne × 12, godzinowe × godziny pracy w roku przyjęte dla kraju ('+Object.keys(G).filter(function(k){return k!=='_'}).map(function(k){return k+' '+G[k]}).join(', ')+', pozostałe '+(G['_']||2000)+'). Dodatki, premie i zakwaterowanie pomijane. Środek widełek liczy się jako jedna oferta. Przeliczenie walut: kursy referencyjne EBC z '+esc((KU.ebc||{}).data||'-')+(KU.kursy_przez_usd?' (dla '+KU.kursy_przez_usd.join(', ')+' przez USD, Bank Światowy)':'')+'. Starsze oferty liczone po dzisiejszym kursie, bez inflacji. Zarobki w krajach, w których pracodawcy rzadko publikują stawki (np. Francja, Szwecja, Niemcy), opierają się na niewielu ofertach - patrz liczba ofert.';
render();
})();
