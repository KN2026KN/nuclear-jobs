(function(){
var D=JSON.parse(document.getElementById('kp-stat').textContent),$=function(i){return document.getElementById(i)};
var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
var KR={PL:'Polska',CZ:'Czechy',SK:'Słowacja',BG:'Bułgaria',RO:'Rumunia',SI:'Słowenia',FR:'Francja',GB:'Wielka Brytania',FI:'Finlandia',SE:'Szwecja',NL:'Holandia',BE:'Belgia',ES:'Hiszpania',CH:'Szwajcaria',DE:'Niemcy',IT:'Włochy',AT:'Austria',UA:'Ukraina',AE:'ZEA',US:'USA',CA:'Kanada',IN:'Indie',CN:'Chiny',KR:'Korea Płd.',JP:'Japonia',TR:'Turcja',EG:'Egipt',BD:'Bangladesz',IR:'Iran',HU:'Węgry'};
var fl=function(k){return /^[A-Z]{2}$/.test(k)?'<img src="https://flagcdn.com/w40/'+k.toLowerCase()+'.png" alt="">':''};
var kr=function(k){return KR[k]||k};
var dd=function(s){return s?s.slice(8,10)+'.'+s.slice(5,7)+'.'+s.slice(0,4):''};
var P=D.pokrycie||{},K=Object.keys(P),N=0,E={};
var rows=K.map(function(k){var em=P[k],t=0;Object.keys(em).forEach(function(e){t+=em[e].n;E[e]=1});N+=t;
 return '<tr><td><span class="fl">'+fl(k)+esc(kr(k))+'</span></td><td class="n">'+t+'</td><td>'+Object.keys(em).map(function(e){return '<span class="em" title="'+esc(em[e].zrodla.join(', '))+'">'+esc(e)+' <i>'+em[e].n+'</i></span>'}).join('')+'</td></tr>'});
$('tP').innerHTML=rows.join('');
var Z=D.zrodla||{},zk=Object.keys(Z),zok=zk.filter(function(k){return Z[k].ok}).length;
$('kN').textContent=N;$('kK').textContent=K.length;$('kE').textContent=Object.keys(E).length;$('kZ').textContent=zok+' / '+zk.length;$('kA').textContent=D.tylko_analiza_otwarte||0;
$('sub').textContent='Stan na '+dd(D.dzien)+' · dane robota nocnego keura-praca · strona widoczna tylko dla administratora';
var nn=function(n){return Array.isArray(n)?n.join(' / '):(n==null?'-':n)};
$('tZ').innerHTML=zk.map(function(k){var z=Z[k];return '<tr><td><b>'+esc(z.nazwa)+'</b> <span class="mut">'+k+'</span></td><td>'+esc(z.kraj)+'</td><td class="'+(z.ok?'ok':'bad')+'">'+(z.ok?'działa':'błąd')+'</td><td>'+(z.ok?nn(z.n):'<span class="bad">'+esc(z.blad||'')+'</span>')+'</td><td class="n">'+(z.s||0)+' s</td></tr>'}).join('');
var R=D.rotacja||{};$('rot').textContent=(R.pominiete||[]).length?'Tej nocy w rotacji pominięte: '+R.pominiete.join(', ')+' (zbierane co 2. noc).':'';
$('tX').innerHTML=(D.niepodlaczone||[]).map(function(x){return '<tr><td><b>'+esc(x[0])+'</b></td><td><span class="fl">'+fl(x[1])+esc(kr(x[1]))+'</span></td><td class="mut">'+esc(x[2])+'</td></tr>'}).join('');
var W=(D.wynagrodzenia||{}).kraj||{},wr=[];
Object.keys(W).forEach(function(k){W[k].forEach(function(w){wr.push([k,w])})});wr.sort(function(a,b){return b[1].n-a[1].n});
var per={mies:'mies.',rok:'rok',godz:'godz.'};
$('tW').innerHTML=wr.map(function(x){var w=x[1];return '<tr><td><span class="fl">'+fl(x[0])+esc(kr(x[0]))+'</span></td><td>'+esc(w.waluta)+' / '+(per[w.okres]||w.okres)+'</td><td class="n">'+w.n+'</td><td class="n">'+w.mediana.toLocaleString('pl-PL')+'</td><td class="mut">'+w.min.toLocaleString('pl-PL')+' - '+w.max.toLocaleString('pl-PL')+'</td></tr>'}).join('');
var KAT={regulator:'dozór / regulator',operator:'operator / inwestor',dostawca:'dostawca',inzynieria:'inżynieria',badania:'badania',medycyna:'medycyna nuklearna',fuzja:'fuzja',odpady:'odpady i wycofywanie',instytucja:'instytucja międzynarodowa'};
var C=D.kandydaci||[],st={};C.forEach(function(k){st[k.stan]=(st[k.stan]||0)+1});
$('kpo').textContent=C.length+' firm i instytucji w '+new Set(C.map(function(k){return k.kraj})).size+' krajach: '+Object.keys(st).map(function(k){return k+' '+st[k]}).join(' · ');
var kol={'podłączony':'ok','strona kariery':'','strona dostępna':'mut','brak dostępu z runnera':'bad'};
$('tC').innerHTML=C.map(function(k){var u=k.kariera||k.www;return '<tr><td><span class="fl">'+fl(k.kraj)+esc(kr(k.kraj))+'</span></td><td><a href="'+esc(k.www)+'" target="_blank" rel="noopener"><b>'+esc(k.nazwa)+'</b></a></td><td class="mut">'+esc(KAT[k.kategoria]||k.kategoria)+'</td><td class="'+(kol[k.stan]||'')+'">'+esc(k.stan)+'</td><td><a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(u.replace(/^https?:\/\/(www\.)?/,'').slice(0,45))+'</a>'+(k.platforma.length?' <span class="mut">'+esc(k.platforma.join(', '))+'</span>':'')+'</td></tr>'}).join('');
function rysuj(){if(!window.Chart){setTimeout(rysuj,300);return}
 Chart.defaults.font.family='Manrope';
 var ks=K.slice().sort(function(a,b){var s=function(k){var t=0;Object.keys(P[k]).forEach(function(e){t+=P[k][e].n});return t};return s(b)-s(a)});
 new Chart($('cK'),{type:'bar',data:{labels:ks.map(kr),datasets:[{data:ks.map(function(k){var t=0;Object.keys(P[k]).forEach(function(e){t+=P[k][e].n});return t}),backgroundColor:'#0f7c78',borderRadius:6}]},options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{display:false}}}});
 var dni=Object.keys(D.nowe||{}).concat(Object.keys(D.zamkniete||{})).filter(function(x){return x.length===10});dni=dni.filter(function(x,i){return dni.indexOf(x)===i}).sort();
 new Chart($('cT'),{type:'bar',data:{labels:dni.map(dd),datasets:[{label:'nowe',data:dni.map(function(d){return (D.nowe||{})[d]||0}),backgroundColor:'#0f7c78'},{label:'zamknięte',data:dni.map(function(d){return -((D.zamkniete||{})[d]||0)}),backgroundColor:'#c9d3da'}]},options:{maintainAspectRatio:false,scales:{x:{stacked:true},y:{stacked:true}}}});
}
rysuj();
})();
