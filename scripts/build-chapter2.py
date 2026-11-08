from pathlib import Path
import json,re
s=Path('index.html').read_text();dec=json.JSONDecoder();original=dec.raw_decode(s.split('const ELEMENTS = ',1)[1])[0];oldrecipes=dec.raw_decode(s.split('const RECIPES_RAW = ',1)[1])[0];origmap=dec.raw_decode(s.split('const IMG_MAP = ',1)[1])[0];items=json.loads(Path('docs/Chapter2/elements.json').read_text());game=json.loads(Path('docs/Chapter2/recipes.json').read_text());newnames={x['n'].lower() for x in items};
# Тимофей пока использует карточку первой главы.
newnames.add('тимофей')
groups={
'people':['Арсений','Данил','Вадим','Матвей','Виталик','Дриггерт','Витя','Дианка','Меллстрой','Хакер','Космонавт'],
'incidents':['Задержание','Задержание Арсения','Задержание убийцы Арсения','Розыск','Розыск Арсения','Инцидент со снежком','Взлом YouTube','Взлом Гта 6','Уголовное Преследование'],
'content':['Канал Hi 3000','Разбан канала Hi 3000','YouTube','YouPrime','Игры','Гта 6','Арсен-Gta','Фильм про убийцу 2 не выйдет','Арсений God','Стендофф','Стрим','АрсенTube','Космический ЭЖП','Коллаба Арсения и Меллстроя','Статьи Виталика'],
'ai':['Арсений Инопланетянин','Арсений Киборг','КиберЕленка','Инопланетянин','ИноАрмия','ИноЧекушка','Арсемус','КриптоАрсений','КриптоВиталик','КриптоМатвей','КриптоВадим','КриптоДанил','КриптоДриггерт','КриптоТимофей'],
'school':['7 класс','8 класс','Космическая Школа'],
'memes':['Мемы','Энергичный Арсений'],
'places':['Земля','Космический Сергиополь','Сергиополь 2.0','Вселенная','Космос','Деревня','Страна Арсения','Чёрная Дыра','Солнце','Банк','АрсенБанк','КриптоИмперия','Арсениус-3000']}
cat={x:g for g,names in groups.items() for x in names}
cosmic=[{'n':e['n'],'g':cat.get(e['n'],'concepts'),'s':e['n'] in game['starters']} for e in items]
cosmic.append({'n':'Тимофей','g':'people','s':True})
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
#chapter2-button{border-color:rgba(193,209,207,.55)}
#start-logo-txt::after{content:'ГЛАВА 2 · КОСМОС';display:block;margin-top:9px;font-size:12px;letter-spacing:.16em;color:#d0dcd7}
/* Light surfaces retain their own readable text colours. */
#intro{--ink:#30271c;--gold-d:#725d3a}
#qgame{--ink:#30271c;--ink2:#625747;--paper:#e9dfc8}
#qgame .btn{color:#f5f4ec} #qgame .btn.q{color:#172320}
.qcard.done h3{color:#234b32}.qcard.done .qd{color:#455c46}
#start-art{display:none!important} #start-logo-txt{display:flex!important;flex-direction:column;align-items:center;justify-content:center;margin:18px 0 8px;min-height:0!important}
body:has(#start:not(.hide)) #cheat-fab,body:has(.ovl.show) #cheat-fab,body:has(#qgame.show) #cheat-fab,body:has(#intro[style*="flex"]) #cheat-fab{display:none!important}
</style>'''
s=s.replace('</head>',css+'\n</head>',1)
# Prevent chapter-1 completion modal on this page; start directly in the same game view.
needle='loadPrefs(); syncPrefsUI(); load(); layout(); setTimeout(offerChapter2, 1200); try{ cheatGApply(); }catch(e){} try{ syncSaveNameUI(); }catch(e){} renderAll();'
assert needle in s
s=s.replace(needle,'''loadPrefs(); syncPrefsUI(); load();
if (!chapter2Unlocked()){ location.replace('index.html'); } else {
 trackIdx=0; introSeen=true; document.getElementById('start').classList.add('hide'); document.querySelector('.ttl .t1').innerHTML='Арсений <em>God</em> · Глава 2';
 layout(); try{cheatGApply()}catch(e){} try{syncSaveNameUI()}catch(e){} renderAll();
 document.addEventListener('pointerdown',()=>{if(musicOn&&!musicStarted){startMusic()}},{once:true});
}''',1)
# Restart always returns to chapter one; the first chapter performs the reset.
a=s.index('function newGame(confirmed){');b=s.index('\n\n/* ---------- код ---------- */',a)
s=s[:a]+"function newGame(){ if (!confirm('Начать заново? Весь прогресс будет стёрт.')) return; location.replace('index.html?newgame=1'); }"+s[b:]
s=s.replace("if (new URLSearchParams(location.search).get('newgame') === '1'){ history.replaceState(null, '', location.pathname); newGame(true); }",'')
# Chapter switching stays explicit in the main menu.
s=s.replace('🌌 Глава 2: Космос</button>','🌍 Первая глава</button>',1)
Path('docs/chapter2.html').write_text(s)
print('Глава 2:',len(cosmic),'элементов,',len(game['recipes']),'рецептов')
