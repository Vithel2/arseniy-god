from pathlib import Path
import json,re
s=Path('index.html').read_text();dec=json.JSONDecoder();original=dec.raw_decode(s.split('const ELEMENTS = ',1)[1])[0];oldrecipes=dec.raw_decode(s.split('const RECIPES_RAW = ',1)[1])[0];origmap=dec.raw_decode(s.split('const IMG_MAP = ',1)[1])[0];items=json.loads(Path('docs/Chapter2/elements.json').read_text());game=json.loads(Path('docs/Chapter2/recipes.json').read_text());newnames={x['n'].lower() for x in items};
groups={
'people':['Арсений','Данил','Вадим','Матвей','Виталик','Дриггерт','Витя','Тимофей','Дианка','Меллстрой','Хакер','Космонавт'],
'incidents':['Задержание','Задержание Арсения','Задержание убийцы Арсения','Розыск','Розыск Арсения','Инцидент со снежком','Взлом YouTube','Взлом Гта 6','Уголовное Преследование'],
'content':['Канал Hi 3000','Разбан канала Hi 3000','YouTube','YouPrime','Игры','Гта 6','Арсен-Gta','Фильм про убийцу 2 не выйдет','Арсений God','Стендофф','Стрим','АрсенTube','Космический ЭЖП','Коллаба Арсения и Меллстроя','Статьи Виталика'],
'ai':['Арсений Инопланетянин','Арсений Киборг','КиберЕленка','Инопланетянин','ИноАрмия','ИноЧекушка','Арсемус','КриптоАрсений','КриптоВиталик','КриптоМатвей','КриптоВадим','КриптоДанил','КриптоДриггерт','КриптоТимофей'],
'school':['7 класс','8 класс','Космическая Школа'],
'memes':['Мемы','Энергичный Арсений'],
'places':['Земля','Космический Сергиополь','Сергиополь 2.0','Вселенная','Космос','Деревня','Страна Арсения','Чёрная Дыра','Солнце','Банк','АрсенБанк','КриптоИмперия','Арсениус-3000']}
cat={x:g for g,names in groups.items() for x in names}
cosmic=[{'n':e['n'],'g':cat.get(e['n'],'concepts'),'s':e['n'] in game['starters']} for e in items]
# Первые элементы остаются доступны для квестов первой главы, но не входят в коллекцию второй.
fallback=[{**e,'q':True,'s':False} for e in original if e['n'].lower() not in newnames]
core=[e['n'] for e in original if not e.get('q') and e['n'] not in ('Пинок Серёги','Нож','Англичанка осталась')];assert len(core)==303
fullmap={**origmap,**{e['n'].lower():'../'+e['img'] for e in items}}
for name,data in [('ELEMENTS',cosmic+fallback),('RECIPES_RAW',[[[a,b],r] for a,b,r in game['recipes']]),('IMG_MAP',fullmap)]:
 pattern=r'const '+name+r' = .*?;\s*\n';m=re.search(pattern,s);assert m,name;s=s[:m.start()]+'const '+name+' = '+json.dumps(data,ensure_ascii=False)+';\n'+s[m.end():]
# Quest recipes are the originals; chapter-two collection uses only its own recipes.
first='const FIRST_RECIPES = '+json.dumps(oldrecipes,ensure_ascii=False)+';\n'
s=s.replace('const RM = {}, RLIST = [];', first+'''const FIRST_RM = {};
for (const [pair,result] of FIRST_RECIPES){ const a=norm(pair[0]),b=norm(pair[1]),v=CANON[norm(result)]; if (!v) continue; for (const k of [a+'|'+b,b+'|'+a]){ if(!FIRST_RM[k]) FIRST_RM[k]=[]; if(!FIRST_RM[k].includes(v)) FIRST_RM[k].push(v); } }
const RM = {}, RLIST = [];''',1)
a=s.index('function resList(a, b){');b=s.index('\nfunction findResult(',a)
s=s[:a]+'''function resList(a, b){
  const k=norm(a)+'|'+norm(b);
  if (qId){ const arr=FIRST_RM[k]; if (arr && arr.length) return arr; const fallback=ruleResult(a,b); return fallback ? [fallback] : []; }
  if ((norm(a)==='работа' && isPeople(b)) || (norm(b)==='работа' && isPeople(a))) return [CANON['деньги']];
  return RM[k] || [];
}''' +s[b:]
# Keep the first chapter's collection and save chapter-two progress independently in the same backup.
a=s.index('function save(){\n  const savedChapter2');b=s.index('\nfunction load(){',a)
s=s[:a]+'''function save(){
  try {
    const base=JSON.parse(localStorage.getItem('ag_v5')||'{}');
    const old=(base.c2 && typeof base.c2==='object') ? base.c2 : {};
    base.c2={...old,owned:[...order],tried:[...tried],nw:[...newSet],r:reactions,h:hist,hidden:[...hideSet],ach:achGot,announced:true,visited:true};
    Object.assign(base,{k:keys,kc:lastClaim,hi:hints,e:energy,ob:ownedBlue?1:0,od:ownedDash?1:0,om:ownedMusic?1:0,rl:lastRoulette,so:searchOn?1:0,tu:tutorSeen?1:0,qd:questDone,qp:questProg,ee:energyEarned,ku:keysUsed,sp:spins,mb:miniBest,mo:miniOn?1:0,fb:funBest,mz:mazeBest,qz:quizBest,ct:createdAt,ps:playSec,sn:ownedSense?1:0,sl:simLvl,st:simLast,sb:simBank,cu:cups});
    localStorage.setItem('ag_v5',JSON.stringify(base));
  } catch(e){ toast('Не удалось сохранить прогресс'); }
  fileAutoSave();
}''' +s[b:]
needle='  order = [...new Set([...STARTERS, ...order])];\n  discovered = new Set(order);'
assert needle in s
s=s.replace(needle,'''  const c2=(d && d.c2 && typeof d.c2==='object') ? d.c2 : {};
  order = [...new Set([...STARTERS, ...(Array.isArray(c2.owned)?c2.owned:[]).map(n=>CANON[norm(n)]).filter(n=>n && !EL_MAP[n].q)])];
  newSet=new Set((Array.isArray(c2.nw)?c2.nw:[]).filter(n=>EL_MAP[n] && !EL_MAP[n].q));
  tried=new Set(Array.isArray(c2.tried)?c2.tried:[]); reactions=Number(c2.r)||0; hist=Array.isArray(c2.h)?c2.h:[];
  hideSet=new Set(Array.isArray(c2.hidden)?c2.hidden:[]); achGot=(c2.ach && typeof c2.ach==='object')?c2.ach:{};
  discovered = new Set(order);''',1)
a=s.index('const CHAPTER1_NEW =');b=s.index('\nfunction renderAll(){',a)
s=s[:a]+'''const CHAPTER1_CORE = '''+json.dumps(core,ensure_ascii=False)+''';
function chapter2Unlocked(){ try{const d=JSON.parse(localStorage.getItem('ag_v5')||'{}');const set=new Set((d.o||[]).map(norm));return CHAPTER1_CORE.every(n=>set.has(norm(n)));}catch(e){return false} }
function openChapter2(){ save(); if(music){music.pause();music=null;musicStarted=false;} location.href='index.html'; }
function offerChapter2(){}
function deferChapter2(){document.getElementById('chapter2-complete').classList.remove('show');}
''' + s[b:]
s=s.replace("c2btn.textContent = chapter2Unlocked() ? '🌌 Глава 2: Космос' : '🔒 Глава 2: Космос';", "c2btn.textContent = '🌍 Первая глава';")
# Chapter-specific group icons; original chapter assets are untouched.
a=s.index('function gIcon(gid, sz){'); b=s.index('\nfunction buildSidebar()',a)
s=s[:a]+"function gIcon(gid, sz){ const name=['all','people','incidents','content','ai','school','memes','places','concepts'].includes(gid)?gid:'all'; return '<img src=\"Chapter2/groups/'+name+'.webp\" alt=\"\" style=\"border-color:'+(gid==='all'?'var(--gold)':GROUPS[gid].color)+'\">'; }"+s[b:]
# Chapter-two sound effects, keeping chapter-one sounds intact.
for name,path in [('click','element.wav'),('btn','button.wav'),('grp','group.wav'),('wrong','wrong.wav')]:
 s=re.sub(r'('+name+r':\s*A\()([^,]+)',lambda m:m.group(1)+"'Chapter2/sounds/"+path+"'",s,count=1)
s=s.replace("function skipIntro(){\n  if (!introPlaying) return;", "function skipIntro(){\n  if (!introPlaying) return; snd('skipChapter');")
s=s.replace('const SFX = {', "const SFX = {\n  skipChapter: A('Chapter2/sounds/skip.wav', .22),",1)
# Same game controls and layout, chapter-two soundtrack.
a=s.index('const TRACKS = [');b=s.index('\nconst TRACK_NAMES',a)
s=s[:a]+"const TRACKS = ['Chapter2/music/elements.mp3','Chapter2/music/city.mp3','Chapter2/music/main.mp3','Chapter2/music/store-1.mp3','Chapter2/music/store-2.mp3','Chapter2/music/main.mp3','Chapter2/music/city.mp3'];"+s[b:]
s=s.replace("const TRACK_NAMES = ['Трек 1', 'Музыка', 'Страшная', 'Музыка 2', 'Магазин', 'Менюшка', 'Музыка 3'];", "const TRACK_NAMES = ['Элементы', 'Город', 'Главная тема', 'Магазин 1', 'Магазин 2', 'Главная тема', 'Город'];")
# Match original spatial layout while replacing only the paper palette/background.
s=s.replace("'ag_rank'","'ag_rank_ch2'")
css='''<style id="chapter2-style">
:root{--paper:#28343b;--surf:#38434a;--surf-hi:#566168;--surf-lo:#29343b;--panel:rgba(45,56,62,.94);--panel2:rgba(45,56,62,.8);--ink:#f5f4ec;--ink2:#d0d4d2;--line:rgba(224,230,223,.16);--line2:rgba(224,230,223,.32);--gold:#e4c695;--gold-d:#eee1c7;--amber-1:#a9b7b0;--amber-2:#778b87;--amber-edge:#9ea9a3;--amber-deep:#536664}
#bg{background:#26343b url('Chapter2/backgrounds/space-portrait.png') center/cover fixed!important;opacity:1!important}
@media(min-aspect-ratio:1/1){#bg{background-image:url('Chapter2/backgrounds/space-landscape.png')!important}}
#app{background:rgba(30,39,43,.25)}
#hdr,.bar,.phead{background:linear-gradient(180deg,rgba(71,83,86,.97),rgba(41,52,57,.97))!important;color:var(--ink)}
.pill{background:rgba(34,43,48,.7);color:var(--ink);box-shadow:none}
.logo,.btn.hint{color:#172320}.btn.tab{color:var(--ink)}.btn.tab.q{color:#26362f}
.gbadge{background:linear-gradient(180deg,rgba(75,87,90,.92),rgba(41,52,57,.93));color:var(--ink)}
.gbadge .gname,.gbadge .gprog,.phead,.slot .sn{color:var(--ink)}
.gbadge img,.phead img,.ec img{background:rgba(30,40,44,.5)}
.slot,.rslot{background:rgba(36,46,51,.7);border-color:rgba(222,226,214,.5);color:var(--ink)}
.slot .pl,.rslot .pl{color:var(--ink2)}
#msg{color:var(--ink)}
.hdr-actions{display:flex!important;justify-content:center;gap:8px!important} .hdr-actions .tab{flex:0 1 100px!important} #chapter2-button{animation:menuappear .55s both!important}
#hdr,#qhdr{box-shadow:0 12px 24px -16px rgba(0,0,0,.45)!important}
#hdr h1,.hdr-actions .tab[onclick="openShop()"],.hdr-actions .tab[onclick="openAch()"],.hdr-actions .tab[onclick="openQuests()"]{display:none!important}
.rslot.nw{background:linear-gradient(#526b68,#344d50);color:#fff} .rslot.ok{background:linear-gradient(#4a6a5a,#304a40);color:#fff} .rslot.no{background:linear-gradient(#765252,#4e363b);color:#fff}
.rslot .rn,.rslot .rs{color:#fff} .rslot.no span{font-size:10px!important;line-height:1.1;text-align:center;overflow-wrap:anywhere;color:#fff!important}
#t2048 .t2048.lv{background:linear-gradient(#607573,#394f53)!important;box-shadow:0 0 0 2px #9aaead}
#funmenu{justify-items:center;align-content:center!important} #funmenu h2{text-align:center}
.shop-more summary{list-style:none;cursor:pointer;padding:14px;border-radius:14px;background:#405557;margin-bottom:10px;font-weight:900} .shop-more[open] summary{margin-bottom:12px}
.rank-celebration{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;background:rgba(9,17,23,.75);animation:appin .3s ease} .rank-celebration>div{display:flex;flex-direction:column;align-items:center;gap:12px;padding:28px;border-radius:28px;background:linear-gradient(#607b79,#30424a);box-shadow:0 0 45px #d0c39988;text-align:center;color:white;animation:pop .5s ease}.rank-celebration img{width:110px;height:110px;object-fit:contain}.rank-celebration strong{font-size:24px}
#settings details[open]>:not(summary){animation:appin .23s ease}
@media(max-width:600px){.bar{gap:4px!important;padding-left:6px!important;padding-right:6px!important}.bar .slot{width:clamp(42px,14vw,56px);min-width:0;flex:0 1 56px}.bar .rslot{width:clamp(58px,19vw,74px);min-width:0;flex:0 1 74px}.bar .btn.hint{min-width:0;flex:1;padding:4px;font-size:10px}.bar .rslot .rn{font-size:9px}}

#start{background:#26343b url('Chapter2/backgrounds/space-portrait.png') center/cover!important}
#fun{background:#26343b url('Chapter2/backgrounds/space-portrait.png') center/cover!important}
#newbanner .box{background:radial-gradient(circle at 50% 20%,#61747b,#34454b 70%)!important}
#newbanner .box::before{opacity:.35}
.btn.tab.q{background:linear-gradient(#5e7876,#405955)!important;color:#fff!important}
#t2048 .t2048,#ezgrid .ez{background:#58696b;color:#fff}
#t2048 .t2048{background:#3e555a;color:#fff}
#settings .srow:has(#theme-row){display:none}
#quests.ovl.show,#shop.ovl.show{animation:none!important}
#quests.ovl.show.fadeout,#shop.ovl.show.fadeout{animation:appout .2s ease forwards!important}
#chapter2-button{animation:appin .6s ease both;animation-delay:.18s}

#chapter2-button{border-color:rgba(193,209,207,.55)}
#start-logo-txt::after{content:'ГЛАВА 2 · КОСМОС';display:block;margin-top:9px;font-size:12px;letter-spacing:.16em;color:#d0dcd7}
/* Light surfaces retain their own readable text colours. */
#intro{--ink:#30271c;--gold-d:#725d3a}
#qgame{--ink:#f5f4ec;--ink2:#d0d4d2;--paper:#28343b;background:#26343b url('Chapter2/backgrounds/space-portrait.png') center/cover!important}
#qgame .qwrap{background:rgba(30,40,44,.3)} #qhdr{background:linear-gradient(#56676a,#34464a)!important} #qtodo{background:#34464a!important;color:#eff5ee} #qgoal{background:#415b58;color:#fff} #qgame .qs{background:#485b5c;color:#f5f4ec} #qgame .qs.done{background:#315f4d;color:#e8fff0}
#funmenu .mbtn{width:100%} #funmenu{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-content:start;gap:8px;padding:24px 16px;overflow:auto}
#funmenu h2,#funmenu button:last-child{grid-column:1/-1} #funmenu button:nth-last-child(2){grid-column:1/-1;width:calc(50% - 4px);justify-self:center} #funmenu .mbtn{margin:0;min-height:62px;font-size:14px}
#ach details{margin:8px 0} #ach summary{cursor:pointer;list-style:none} #settings details{border-bottom:1px solid var(--line);padding:6px 0} #settings summary{cursor:pointer;list-style:none;font-weight:900;padding:12px 4px} #settings summary::after{content:'▾';float:right}
#qgame .btn{color:#f5f4ec} #qgame .btn.q{color:#172320}
.qcard.done h3{color:#234b32}.qcard.done .qd{color:#455c46}
#start-art{display:none!important} #start-logo-txt{display:flex!important;flex-direction:column;align-items:center;justify-content:center;margin:18px 0 8px;min-height:0!important}
body:has(#start:not(.hide)) #cheat-fab,body:has(.ovl.show:not(#cheat)) #cheat-fab,body:has(#qgame.show) #cheat-fab,body:has(#intro[style*="flex"]) #cheat-fab{display:none!important}
</style>'''
s=s.replace('</head>',css+'\n</head>',1)
# Prevent chapter-1 completion modal on this page; start directly in the same game view.
needle='loadPrefs(); syncPrefsUI(); load(); layout(); setTimeout(offerChapter2, 1200); try{ cheatGApply(); }catch(e){} try{ syncSaveNameUI(); }catch(e){} renderAll();'
assert needle in s
s=s.replace(needle,'''loadPrefs(); syncPrefsUI(); document.body.dataset.theme=''; load();
if (!chapter2Unlocked()){ location.replace('index.html'); } else {
 trackIdx=0; introSeen=true; document.getElementById('start').classList.remove('hide'); document.querySelector('.ttl .t1').innerHTML='Арсений <em>God</em> · Глава 2';
 layout(); try{cheatGApply()}catch(e){} try{syncSaveNameUI()}catch(e){} renderAll();
 if (!localStorage.getItem('ag_c2_intro')) { const story=document.createElement('div'); story.className='ovl show'; story.id='c2-story'; story.innerHTML='<div class="box"><h2>🌌 Глава 2</h2><p>Все привычные элементы открыты, но за пределами Сергиополя ждёт целая вселенная.</p><p>Арсений и друзья отправляются в космос. Новые встречи, открытия и неожиданные реакции уже рядом!</p><button class="bigbtn" id="c2-story-go">Начать приключение</button></div>'; document.body.appendChild(story); document.getElementById('c2-story-go').onclick=()=>{localStorage.setItem('ag_c2_intro','1');story.remove();}; }
 document.addEventListener('pointerdown',()=>{if(musicOn&&!musicStarted){startMusic()}},{once:true});
}''',1)
# Restart always returns to chapter one; the first chapter performs the reset.
a=s.index('function newGame(confirmed){');b=s.index('\n\n/* ---------- код ---------- */',a)
s=s[:a]+"function newGame(){ if (!confirm('Начать заново? Весь прогресс будет стёрт.')) return; location.replace('index.html?newgame=1'); }"+s[b:]
s=s.replace("if (new URLSearchParams(location.search).get('newgame') === '1'){ history.replaceState(null, '', location.pathname); newGame(true); }",'')
# Group achievements in collapsible sections to keep the list manageable.
a=s.index('function renderAch(){'); b=s.index('\nfunction openAch()',a)
section=s[a:b].replace("const h = document.createElement('div');", "const section=document.createElement('details'); const h = document.createElement('summary');")
section=section.replace("box.appendChild(h);", "section.appendChild(h); box.appendChild(section);").replace("box.appendChild(d);", "section.appendChild(d);")
s=s[:a]+section+s[b:]
s=s.replace('dragTimer = setTimeout(() => { dragTimer = null; dragBegin(); }, 350);','dragTimer = setTimeout(() => { dragTimer = null; dragBegin(); }, 180);')
# Organize optional purchases under a compact section, leaving daily rewards visible.
s=s.replace("function openShop(){\n  snd('store');", "function openShop(){\n  compactShop(); snd('store');")
s=s.replace("function openShop(){", "function compactShop(){ const box=document.querySelector('#shop .box'); if(!box || box.dataset.compact) return; box.dataset.compact='1'; const items=[...box.querySelectorAll(':scope > .shop-item')]; if(items.length<3)return; const section=document.createElement('details'); section.className='shop-more'; const title=document.createElement('summary');title.textContent='🛍️ Улучшения и покупки';section.appendChild(title);items[2].before(section);items.slice(2).forEach(el=>section.appendChild(el)); }\nfunction openShop(){",1)
s=s.replace("snd('quest'); toast('🎖 Новое звание: ' + rankIcon(discovered.size) + ' ' + rankName(discovered.size) + '!');", "snd('quest'); showRankCelebration();")
s=s.replace('function checkRank(){', "function showRankCelebration(){ const overlay=document.createElement('div');overlay.className='rank-celebration';overlay.innerHTML='<div><span>✨ Новое звание ✨</span><img alt=\"\"><strong></strong><small>Нажми, чтобы закрыть</small></div>';overlay.querySelector('img').src=rankImg(discovered.size);overlay.querySelector('strong').textContent=rankIcon(discovered.size)+' '+rankName(discovered.size);document.body.appendChild(overlay);let closing=false;const close=()=>{if(closing)return;closing=true;overlay.style.animation='appout .3s ease forwards';setTimeout(()=>overlay.remove(),300)};overlay.onclick=close;setTimeout(close,3800); }\nfunction checkRank(){")
# Fold settings into sections while keeping the original controls and event handlers.
s=s.replace("function openSettings(){ snd('btn');", "function openSettings(){ compactSettings(); snd('btn');")
s=s.replace("function openSettings(){", "function compactSettings(){ const box=document.querySelector('#settings .box'); if(!box || box.dataset.compact) return; box.dataset.compact='1'; let section=null; [...box.children].forEach(el=>{ if(el.classList.contains('sgroup')){ section=document.createElement('details'); const title=document.createElement('summary'); title.textContent=el.textContent; section.appendChild(title); el.replaceWith(section); } else if(section){ section.appendChild(el); } }); }\nfunction openSettings(){",1)
# The first chapter retains its original art; these replacements apply only inside mini-games.
s=s.replace('function mafImg(n){', "const MINI_ART={'демон арсения':'demon','анджелика':'andzhelika','бурик':'burik','еленка':'elenka','саша':'sasha','vithel':'vithel'};\nfunction miniImg(n){const f=MINI_ART[norm(n)];return f?'Chapter2/minigames/'+f+'.webp':imgP(n)}\nfunction mafImg(n){")
s=s.replace('imgP(mafImg(', 'miniImg(mafImg(')
s=s.replace("imgP('Еленка')", "miniImg('Еленка')").replace("imgP('Саша')", "miniImg('Саша')").replace("imgP('Демон Арсения')", "miniImg('Демон Арсения')")
s=s.replace('if (!rnImgs[nm]){ const im = new Image(); im.src = encodeURI(imgP(nm));', 'if (!rnImgs[nm]){ const im = new Image(); im.src = encodeURI(miniImg(nm));')
# Chapter switching stays explicit in the main menu.
s=s.replace('🌌 Глава 2: Космос</button>','🌍 Первая глава</button>',1)
Path('docs/chapter2.html').write_text(s)
print('Глава 2:',len(cosmic),'элементов,',len(game['recipes']),'рецептов')
