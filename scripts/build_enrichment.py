#!/usr/bin/env python3
"""Purpose hubs, preparation checklists, searchable Q&A and verified local directory.

Source data stays in data/*.json. Existing life pages are refreshed separately by
refresh_current_information.py, preserving canonical tags and shared footer content.
"""
import json,re
from pathlib import Path
from html import escape,unescape
from urllib.parse import quote
from generate_pages import load_content_map

ROOT=Path(__file__).resolve().parent.parent
SITE='https://kosai.enshu-lifehack.com'
DATE='2026-11-21'
def load(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
def e(s):return escape(str(s),quote=True)
def decorated(s):
 for icon in [h['icon'] for h in HUBS]:
  if s.startswith(icon+' '):return f'<span aria-hidden="true">{icon}</span> '+e(s[len(icon)+1:])
 return e(s)
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
def part(name):return (ROOT/'parts'/f'{name}.html').read_text(encoding='utf-8').strip()
def block(name):return f'<!-- PART:{name}:START -->{part(name)}<!-- PART:{name}:END -->'
TOPICS=load('topics_master.json'); CONTENT=load_content_map(); HUBS=load('hubs.json'); CHECKS=load('checklists.json')
PRACTICAL=load('practical-guides.json'); DIRECTORY=load('kosai-directory.json'); CENTERS=load('care-centers.json')
BY_HREF={t['href']:t for t in TOPICS}; REGISTRY=[]
def link(h,label=None,cls=''):
 if label is None:label=BY_HREF[h]['title']
 return f'<a'+(f' class="{cls}"' if cls else '')+f' href="{e(h)}">{e(label)}</a>'
def sources(items):return '<div class="source-list">'+''.join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a>' for s in items)+'</div>'
def cards(items):
 return '<div class="guide-grid">'+''.join(f'<a class="guide-card" href="{e(h)}"><h3>{decorated(t)}</h3><p>{e(d)}</p><span class="card-next" aria-hidden="true">詳しく見る →</span></a>' for h,t,d in items)+'</div>'
def topiccards(items):
 return cards([(t['href'],t['title'],CONTENT.get(t['href'],{}).get('lead',t.get('lead','関連する窓口・手順・公式案内を確認できます。'))) for t in items])
def nav():return '<nav class="utility-nav" aria-label="暮らしの探し方">'+''.join(link(h,t) for h,t in [('/guides/','全ガイド'),('/questions/','質問から探す'),('/checklist/','準備チェック'),('/kosai-directory/','施設・窓口'),('/tools/care-center/','介護の相談先')])+'</nav>'
def write(href,title,lead,body,category='暮らしの便利ガイド',icon='📖',synonyms=None):
 description=lead[:150]
 html='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
 html+=f'<title>{e(title)} | 湖西ライフハック</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{SITE}{href}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">'+block('head-css')
 html+='</head><body class="enriched-page">'+block('header')+block('disclaimer')+'<main id="main-content"><div class="wrap">'
 html+='<p class="breadcrumb"><a href="/">湖西ライフハック</a> ／ '+e(title)+'</p>'
 html+=f'<section class="hero"><p class="eyebrow">暮らしに合わせて、次の一歩へ</p><h1><span aria-hidden="true">{icon}</span> {e(title)}</h1><p class="lead">{e(lead)}</p></section>'+nav()+body
 html+='<aside class="editorial-note"><h2>この案内の確認範囲</h2><p>掲載情報の確認日は項目ごとに示しています。制度の対象・期限・予約状況は公式窓口で確認してください。リンク先の既存ガイド全体を一律に再確認したことを示す日付ではありません。</p><p><a href="/#current-information">期限のある最新情報</a>・<a href="https://www.city.kosai.shizuoka.jp/">湖西市公式サイト</a>・<a href="/terms/">利用について</a></p></aside>'
 html+='</div></main><script src="/assets/life-tools.js" defer></script>'+block('footer')+'</body></html>\n'
 out=ROOT/href.strip('/')/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html,encoding='utf-8',newline='\n')
 REGISTRY.append(dict(href=href,title=title,category=category,icon=icon,synonyms=synonyms or [],status='published'))

def search_controls(id,label,placeholder,categories):
 return f'<div class="filter-controls"><label for="{id}-query">{label}<input id="{id}-query" type="search" placeholder="{e(placeholder)}" data-filter-query autocomplete="off"></label><label for="{id}-category">分類<select id="{id}-category" data-filter-category><option value="">すべて</option>'+''.join(f'<option>{e(c)}</option>' for c in categories)+f'</select></label><button type="button" data-filter-reset>絞り込みを解除</button></div><p class="filter-count" data-filter-count role="status" aria-live="polite"></p><p data-filter-empty hidden>該当する項目がありません。短い言葉にするか、分類を「すべて」に戻してお試しください。</p>'

def build_hubs():
 for hub in HUBS:
  body='<section><h2>まず確認したいこと</h2>'
  if hub['id']=='care':body+=cards([('/tools/care-center/','担当の地域包括支援センターを探す','自治会を選んで、相談先・電話番号を確認。'),('/checklist/care/','介護の準備をチェック','相談、申請、調査、費用の確認を順に整理。')])
  elif hub['id']=='family':body+=cards([('/checklist/baby/','妊娠・出産の準備','出生届と手当は別申請。期限と書類をチェック。'),('/life/family-grow/nursery-childcare/','保育園・認定こども園の申込','翌年度4月と年度途中の入園手続きを確認。'),('/life/education/school-expense-support/','学校にかかる費用の相談','就学援助などの対象・申請・相談先を確認。')])
  elif hub['id']=='enjoy':body+=cards([('/discover/','湖西を訪ねる','新居宿・白須賀・浜名湖の文化と自然。'),('/kosai-directory/','施設・窓口を検索','所在地、電話、利用条件、公式案内。')])
  elif hub['id']=='trouble':body+=cards([('/emergency/','急いで連絡したい','救急・火事、犯罪、避難の入口。'),('/questions/','困りごとを質問から探す','制度名がわからなくても、言葉から検索。')])
  else:body+=cards([('/checklist/'+i+'/',next(c['title'] for c in CHECKS if c['id']==i),next(c['lead'] for c in CHECKS if c['id']==i)) for i in hub['checklists']])
  body+='</section><nav class="page-toc" aria-label="このページの目次"><strong>テーマ別に進む</strong>'+''.join(f'<a href="#category-{n}">{e(c)}</a>' for n,c in enumerate(hub['categories']))+'</nav>'
  for n,cat in enumerate(hub['categories']):
   topics=[t for t in TOPICS if t['category']==cat]; sub=[t for t in topics if t['href'].count('/')>3]
   body+=f'<section id="category-{n}"><h2>{e(cat)}</h2>'+topiccards(sub)+'</section>'
  write('/hub/'+hub['id']+'/',hub['title'],hub['lead'],body,icon=hub['icon'])

def build_catalog():
 body='<div data-filter-list data-page-size="24">'+search_controls('guides','知りたいこと','例：水道、保育園、相続',[h['title'] for h in HUBS])+'<div class="guide-grid">'
 for t in TOPICS:
  if t['href'].count('/')<=3:continue
  hub=next(h for h in HUBS if t['category'] in h['categories']);lead=CONTENT.get(t['href'],{}).get('lead','公式窓口と関連する手続きを確認できます。')
  search=' '.join([t['title'],t['category'],*t.get('synonyms',[]),lead])
  body+=f'<article class="guide-card" data-filter-item data-category="{e(hub["title"])}" data-search="{e(search)}"><p class="eyebrow">{e(t["category"])}</p><h2>{link(t["href"])}</h2><p>{e(lead)}</p></article>'
 body+='</div><button type="button" class="load-more" data-filter-more hidden>続きを表示</button></div>'
 write('/guides/','湖西の暮らしガイドを探す','住所・税金・子育て・介護・住まい・防災まで、公開済みの詳細ガイドを横断して探せます。',body,synonyms=['手続き一覧','全記事','索引'])

def build_checklists():
 body='<p>チェックした状態はこのブラウザーだけに保存します。氏名・住所などを入力する欄はありません。紙に印刷して使うこともできます。</p>'+cards([('/checklist/'+c['id']+'/',c['title'],c['lead']) for c in CHECKS])
 write('/checklist/','暮らしの準備チェックリスト','転居、出産、退職、介護、相続など、状況に合わせて必要な準備を整理します。',body,icon='✅',synonyms=['持ち物','やること','準備'])
 for c in CHECKS:
  body=f'<section class="checklist-panel" data-checklist="{c["id"]}" data-version="20261121"><h2>準備すること</h2><p>該当しない項目は飛ばして使えます。チェックは申請完了や受給資格を判定するものではありません。</p><p class="check-progress" data-check-progress role="status" aria-live="polite"></p><p data-save-status class="mini">チェックの保存にはJavaScriptが必要です。</p><ol class="checklist-items">'
  for i in c['items']:
   body+=f'<li><div class="check-line"><input type="checkbox" id="{i["id"]}" data-check-item><label for="{i["id"]}"><span class="check-when">{e(i["when"])}</span><strong>{e(i["text"])}</strong></label></div><p>{e(i["tip"])}</p>{link(i["href"],"手順・条件・公式出典を確認 →")}</li>'
  body+='</ol><div class="tool-actions"><button type="button" data-check-reset>チェックをすべて外す</button><button type="button" data-print>このページを印刷</button></div></section>'
  body+='<h2>準備のあとに確認する</h2>'+cards([('/questions/','質問で確かめる','必要書類・条件・申請先を言葉から検索。'),('/kosai-directory/','窓口を探す','所在地や電話番号を調べてから出かける。')])
  write('/checklist/'+c['id']+'/',c['title']+'：準備チェック',c['lead'],body,icon='✅',synonyms=['チェックリスト','持ち物','期限'])

def build_questions():
 questions=[];seen={}
 for t in TOPICS:
  for qa in CONTENT.get(t['href'],{}).get('qa',[]):
   q=qa.get('question','');a=qa.get('answer','');key=(plain(q),plain(a))
   if key in seen:seen[key]['hrefs'].append(t['href']);continue
   row=dict(question=q,answer=a,category=t['category'],hrefs=[t['href']],date=t.get('verified_date') or t.get('ai_checked_date') or '元ページを参照',kind='既存ガイドのQ&A',sources=t.get('sources_kosai',[]));seen[key]=row;questions.append(row)
 for g in PRACTICAL['items']:
  for row in g['rows']:
   questions.append(dict(question=g['title']+'：'+row['label'],answer=e(row['text']),category=BY_HREF[g['pages'][0]]['category'],hrefs=g['pages'],date=g['checked_at'],kind='今回照合した実務情報',sources=g['sources']))
 questions.sort(key=lambda q:q['kind']!='今回照合した実務情報')
 body='<p>既存ガイドのQ&Aと、今回公式情報に照合した実務情報をまとめました。各回答の確認日・範囲と、詳細ページの最新案内も確認してください。</p><div data-filter-list data-page-size="20">'+search_controls('qa','質問・回答を検索','例：委任状、15日、介護、保育園',sorted({q['category'] for q in questions}))
 for n,q in enumerate(questions):
  body+=f'<details class="question-card" data-filter-item data-category="{e(q["category"])}" data-search="{e(q["question"]+" "+plain(q["answer"])+" "+q["category"])}"><summary>{e(q["question"])}</summary><div class="question-answer"><p>{q["answer"]}</p><p class="mini">{e(q["kind"])} ／ 確認日：{e(q["date"])}</p><p>'+ ' ・ '.join(link(h,'詳細ガイド'+(' '+str(i+1) if len(q['hrefs'])>1 else '')) for i,h in enumerate(q['hrefs']))+'</p>'+sources(q['sources'])+'</div></details>'
 body+='<button type="button" class="load-more" data-filter-more hidden>続きを表示</button></div>'
 write('/questions/','質問から探す湖西の暮らし','制度名がわからないときも、質問や回答の言葉から手続き・相談先を探せます。',body,icon='💬',synonyms=['よくある質問','Q&A','相談'])
 return len(questions)

def build_directory():
 body='<p>'+e(DIRECTORY['scope'])+'</p><p class="confirmed">掲載項目の照合日：'+e(DIRECTORY['checked_at'])+'。電話は施設の一般窓口の場合があり、個別手続きの担当番号とは異なります。</p><p>年末年始は通常の休館日と異なります。<a href="https://www.city.kosai.shizuoka.jp/shiseijoho/chosha_shisetsuannai/7539.html" target="_blank" rel="noopener">市公式の2026〜2027年末年始業務表</a>もあわせて確認してください。</p><div data-filter-list data-page-size="18">'+search_controls('directory','施設名・地区・目的','例：新居、図書館、テニス、介護',sorted({f['category'] for f in DIRECTORY['items']}))+'<div class="directory-grid">'
 for f in DIRECTORY['items']:
  # The broad official category also contains museums: "図書館" must not match all of them.
  info=' '.join([f['name'],f['address'],f['category'].replace('文化・図書館','文化'),*f['details']]);phone=re.search(r'0\d{2,3}-\d{2,3}-\d{4}',f['phone'])
  body+=f'<article id="{f["id"]}" class="facility-card" data-filter-item data-category="{e(f["category"])}" data-search="{e(info)}"><p class="eyebrow">{e(f["category"])}</p><h2>{e(f["name"])}</h2><p class="facility-address">{e(f["address"])}</p>'
  if phone:body+=f'<p><a class="phone-link" href="tel:{phone[0].replace("-","")}">{e(f["phone"])}</a></p>'
  else:body+='<p class="mini">個別の連絡先は公式案内をご確認ください。</p>'
  body+=''.join('<p>'+e(d)+'</p>' for d in f['details'])
  if not f['details']:body+='<p class="mini">この項目は所在地・電話番号を照合しました。開館日・利用条件は公式案内で確認してください。</p>'
  body+=sources(f['sources'])+'</article>'
 body+='</div><button type="button" class="load-more" data-filter-more hidden>続きを表示</button></div>'
 body+='<section><h2>予約・窓口で迷ったら</h2>'+cards([('/life/play-out/rent-public-facilities/','施設の予約方法','登録に必要な書類と、オンライン予約できる区画を確認。'),('/life/start-living/city-hall-branches/','市役所・支所の取扱い','証明書や住所変更を受け付ける窓口を確認。')])+'</section>'
 write('/kosai-directory/','湖西の施設・窓口を探す','行政・福祉、文化・観光、図書館、公園、スポーツ施設の所在地・電話・利用案内を検索できます。',body,icon='📍',synonyms=['電話番号','住所','施設一覧','図書館','公園'])

def build_care_tool():
 options=''.join(f'<optgroup label="{e(c["name"])}">'+''.join(f'<option value="{e(d)}">{e(d)}</option>' for d in c['districts'])+'</optgroup>' for c in CENTERS['items'])
 body='<section class="care-lookup"><h2>自治会名から担当を選ぶ</h2><p>住所の町名だけでは担当を決められない場合があります。自治会名を選んでください。神座は湖西白萩、岡崎は光湖苑の担当です。</p><label for="care-district">お住まいの自治会<select id="care-district" data-care-select><option value="">選択してください</option>'+options+'</select></label><p data-care-status role="status" aria-live="polite">未選択時は4センターすべてを表示します。</p>'
 for c in CENTERS['items']:
  body+=f'<article class="center-card" data-care-center data-districts="{e(json.dumps(c["districts"],ensure_ascii=False))}"><h3>{e(c["name"])}</h3><p>{e(c["address"])}</p><p><a class="phone-link" href="tel:{c["phone"].replace("-","")}">{c["phone"]}</a></p><p><strong>担当自治会：</strong>{e("、".join(c["districts"]))}</p></article>'
 body+='<aside class="editorial-note"><h3>自治会がわからないとき</h3><p>担当を推測せず、湖西市高齢者福祉課 高齢者支援係（<a href="tel:0535761212">053-576-1212</a>）に地区を伝えて確認してください。相談先を探すための案内で、介護認定や受給資格を判定するものではありません。</p></aside><p class="mini">担当自治会・連絡先の確認日：2026年11月21日。</p>'+sources(CENTERS['sources'])+'</section>'
 body+='<h2>相談するときに用意すること</h2><ul><li>本人の希望と、食事・入浴・移動など困っている場面</li><li>家族の連絡先、かかりつけ医、介護認定の有無</li><li>急いで対応が必要なことと、今後相談したいこと</li></ul>'+cards([('/checklist/care/','介護の準備チェック','申請・認定・費用の確認へ。'),('/life/parents-care/care-certification-support-center/','介護認定の申請','申請窓口・持ち物を確認。')])
 write('/tools/care-center/','自治会から介護の相談先を探す','湖西市の4つの地域包括支援センターから、自治会に対応する担当窓口と電話番号を表示します。',body,icon='☎️',synonyms=['地域包括支援センター','高齢者','神座','岡崎','介護相談'])
 write('/tools/','湖西の暮らしに使えるツール','相談先を選ぶ、やることを整理する、質問や施設を検索するための道具をまとめました。',cards([('/tools/care-center/','自治会別・介護の相談先','住所から推測せず自治会から担当を選択。'),('/checklist/','準備チェックリスト','このブラウザーにチェック状態を保存・印刷。'),('/questions/','質問の横断検索','回答と根拠、詳細ガイドを確認。'),('/kosai-directory/','施設・窓口検索','名前・地区・目的で絞り込み。')]),icon='🧰')

def build_emergency():
 body='<section class="urgent-panel"><h2>緊急の通報</h2><div class="guide-grid"><article><h3>火事・救急・救助</h3><p class="urgent-number"><a href="tel:119">119</a></p><p>意識がない、呼吸が苦しいなど緊急のときは、相談窓口の返答を待たず119へ。場所・何が起きたか・人数などを伝えてください。</p></article><article><h3>事件・事故の緊急通報</h3><p class="urgent-number"><a href="tel:110">110</a></p><p>今起きている事件・事故で警察の対応が必要なとき。場所と状況を伝えてください。</p></article></div></section>'
 body+='<h2>受診・避難・被害後の手続き</h2>'+topiccards([BY_HREF[h] for h in ['/life/health-medical/holiday-night-emergency-care/','/life/emergency/evacuation-hazard-map/','/life/emergency/disaster-mail-line/','/life/emergency/disaster-certificates-procedures/','/life/troubles-consult/consumer-fraud/']])
 body+='<p class="mini">119・110の使い方は各公式案内も確認してください。</p>'+sources([{'label':'湖西市消防：119番通報の仕方','url':'https://www.city.kosai.shizuoka.jp/shobo/shobo_119/15119.html'},{'label':'静岡県警察：110番','url':'https://www.pref.shizuoka.jp/police/about/110kinkyu/tadashikuriyo.html'}])
 write('/emergency/','急病・災害・緊急時の連絡先','緊急通報、休日夜間の受診、避難情報、災害後の手続きを分けて確認できます。',body,icon='⚠️',synonyms=['119','110','救急','火災','避難'])

def build_audiences():
 # Editorial routes connect sourced guides; no invented travel times or personal experiences.
 body='<section><h2>新居宿で歴史を知る</h2><p>新居関所は9:00〜16:30、大人400円・小中学生150円。紀伊国屋資料館との共通券は大人500円・小中学生200円です。紀伊国屋は関所から西へ約170m、専用駐車場がないため関所駐車場を利用します。</p><p>小松楼は9:00〜17:00、入館無料。3施設とも通常の月曜休館がありますが、祝日と年末年始の扱いは施設ごとに確認してください。</p>'+sources([{'label':'新居関所・史料館','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/araisekiato/10304.html'},{'label':'紀伊国屋資料館','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/8958.html'},{'label':'小松楼','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/8959.html'}])+'</section>'
 body+='<section><h2>白須賀宿と潮見坂</h2><p>おんやど白須賀は10:00〜16:00、入館無料。駐車場は4台なので、満車時の周辺への無断駐車は避けてください。道の駅潮見坂では売店・食堂・足湯の営業時間がそれぞれ異なります。一般道側駐車場からは階段があるため、移動のしやすさも確認して計画します。</p>'+sources([{'label':'おんやど白須賀','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/shirasukashuku/1221.html'},{'label':'道の駅潮見坂','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/michinoeki/12187.html'}])+'</section>'
 body+='<section><h2>浜名湖と公園を楽しむ前に</h2><p>海湖館の体験は実施日・予約条件を確認してから訪問。海釣公園駐車場は24時間ごと400円、30分以内の出庫は無料で、現金のみです。2026年の新居弁天海水浴場の開設は8月30日で終了しています。</p><p>おちばの里親水公園ではバーベキュー・キャンプは利用できません。12月4日はトイレ等の一時休止があります。トキワマンサクは例年4月中旬の花で、今回の秋冬の開花情報としては案内していません。</p>'+sources([{'label':'海湖館','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/7641.html'},{'label':'海釣公園駐車場','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/10535.html'},{'label':'海水浴場','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/10260.html'},{'label':'おちばの里親水公園','url':'https://www.city.kosai.shizuoka.jp/shiseijoho/chosha_shisetsuannai/3564.html'},{'label':'トキワマンサク','url':'https://www.city.kosai.shizuoka.jp/soshikiichiran/kanko/spot/1278.html'}])+'</section>'
 body+='<p class="confirmed">上記の利用情報は2026年11月21日に市公式の掲載内容を照合しました。当日の天候・臨時休館・混雑は別途確認が必要です。</p>'+cards([('/kosai-directory/','施設の所在地・連絡先を見る','開館時間や休止情報を施設名で検索。'),('/life/play-out/cultural-facilities/','直近の展示情報を見る','新居関所の開催中・次回の企画展。'),('/life/start-living/public-transit/','公共交通を確認','バスや鉄道の公式時刻表へ。')])
 write('/discover/','湖西の歴史・自然を訪ねる','新居宿、白須賀宿、浜名湖周辺。場所の魅力と、出かける前に確認したい利用条件をまとめました。',body,icon='🌿',synonyms=['観光','新居関所','紀伊国屋','潮見坂','白須賀'])
 visitors='<h2>行き先を決める</h2>'+cards([('/discover/','歴史・自然の見どころ','新居宿・白須賀・浜名湖周辺の訪問案内。'),('/kosai-directory/','営業時間と所在地','施設名や地区で検索して公式案内へ。')])+'<h2>出発前に確認する</h2>'+topiccards([BY_HREF[h] for h in ['/life/play-out/parking-access/','/life/start-living/public-transit/','/life/emergency/evacuation-hazard-map/','/life/health-medical/holiday-night-emergency-care/']])+'<p>入館料・駐車料金・体験料金は別々です。日帰りの予定でも、休館日、帰りの便、海岸周辺の警報を確認しておきましょう。</p>'
 write('/for-visitors/','湖西に出かける方へ','観光、公共施設、公園、移動、急な体調不良の確認先をひとつの入口から探せます。',visitors,icon='🧳')
 parents='<h2>親の暮らしを確認する</h2><p>最初に、本人が望む暮らしと、家族が心配していることを分けて整理します。介護・交通・家の管理は、それぞれ相談先が異なります。</p>'+cards([('/tools/care-center/','担当の介護相談窓口','親の自治会から地域包括支援センターを選択。'),('/checklist/care/','介護が始まるときの準備','申請からサービスの費用確認まで。'),('/checklist/inheritance/','家・土地の相続準備','登記、税、農地、管理を切り分ける。')])+'<h2>気になることから読む</h2>'+topiccards([BY_HREF[h] for h in ['/life/parents-care/check-parents/','/life/parents-care/dementia-consultation/','/life/parents-care/elderly-transportation/','/life/housing/clean-parents-house/','/life/housing/vacant-house/','/life/end-of-life/bereavement-procedures/']])
 write('/for-parents/','湖西に親・実家がある方へ','離れて暮らす親の介護、通院、住まい、実家の管理と相続を順に確認するための案内です。',parents,icon='🏡')
 moving='<h2>住む地区を決める前に</h2><p>家賃や間取りだけでなく、通勤・買い物・通学・受診の移動と災害リスクを同じ住所で確認します。補助金は対象となる人や契約時期が決まっているので、申請前の購入・転居で対象外にならないか確かめてください。</p>'+topiccards([BY_HREF[h] for h in ['/life/living-soon/transportation/','/life/living-soon/school-districts/','/life/living-soon/disaster-risk/','/life/living-soon/want-to-live/']])+'<h2>引っ越しが決まったら</h2>'+cards([('/checklist/moving-in/','転入の準備チェック','水道は2営業日前、住所・子どもの申請は期限を分けて。'),('/hub/family/','子育て・学校の入口','園の申込、学校、放課後の相談。'),('/kosai-directory/','窓口・施設の場所','生活圏の施設を地区名で探す。')])
 write('/for-moving/','湖西で暮らすことを考える方へ','移住・住み替えの検討から、引っ越し前後の具体的な準備へ進めます。',moving,icon='🚚',synonyms=['移住','転居','定住','引っ越し'])

def update_home():
 home=ROOT/'index.html';text=home.read_text(encoding='utf-8')
 purpose='<section class="home-purpose"><p class="eyebrow">暮らしの場面から</p><h2>何から始めるか、ここから探す</h2>'+cards([('/hub/'+h['id']+'/',h['icon']+' '+h['title'],h['lead']) for h in HUBS])+'</section>'
 purpose+='<section class="audience-section"><h2>あなたに合う入口</h2>'+cards([('/for-visitors/','湖西に出かける','見どころ、施設、交通、出発前の確認。'),('/for-parents/','湖西に親・実家がある','介護の相談先、家の管理、相続の準備。'),('/for-moving/','湖西で暮らしたい','通学区、移動、防災、転入の手続き。')])+'</section>'
 purpose+='<section class="home-tools"><h2>調べる・準備する・連絡する</h2>'+cards([('/questions/','質問から探す','制度名がわからなくても、言葉から回答へ。'),('/checklist/','準備チェックリスト','転居・出産・退職・介護・相続などを整理。'),('/kosai-directory/','施設・窓口を探す','所在地・電話・営業時間・利用条件。'),('/tools/care-center/','介護の担当窓口を選ぶ','自治会から地域包括支援センターを表示。')])+'</section>'
 purpose+='<section class="frequent-links"><h2>よく使う手続きへ</h2><div class="quick-links">'+''.join(link(h,t) for h,t in [('/life/start-living/certificates/','住民票・戸籍'),('/life/start-living/garbage-sorting-calendar/','ごみの収集日'),('/life/start-living/water-start-stop-fees/','水道の開始・中止'),('/life/family-grow/nursery-childcare/','保育園の申込'),('/life/parents-care/care-certification-support-center/','介護認定'),('/life/end-of-life/bereavement-procedures/','おくやみ手続き')])+'</div></section>'
 purpose+='<p class="all-tools-link"><a href="/guides/">すべての暮らしガイドを見る →</a>　<a href="/tools/">便利ツール一覧 →</a></p>'
 wrapped='<!-- ENRICHMENT:START -->'+purpose+'<!-- ENRICHMENT:END -->'
 text=re.sub(r'<!-- ENRICHMENT:START -->.*?<!-- ENRICHMENT:END -->','',text,flags=re.S)
 pos=text.index('<section id="category-links"');text=text[:pos]+wrapped+text[pos:]
 emergency='<nav class="emergency-strip" aria-label="緊急時の入口"><strong>急いでいるとき</strong><a href="tel:119">火事・救急 119</a><a href="tel:110">事件・事故 110</a><a href="/emergency/">受診・避難・相談先 →</a></nav>'
 text=re.sub(r'<nav class="emergency-strip".*?</nav>','',text,flags=re.S)
 pos=text.index('<section class="site-search"');text=text[:pos]+emergency+text[pos:]
 text=re.sub(r'<!-- CURRENT:QUICK:START -->.*?<!-- CURRENT:QUICK:END -->','',text,flags=re.S)
 current=load('current-updates.json')
 # Keep the brief alert separate from the complete list below.
 quick='<!-- CURRENT:QUICK:START --><aside class="current-quick"><strong>'+e(current.get('updated_at',current['checked_at']))+'更新の主な案内</strong>'+''.join(link(i['pages'][0],i['title']) for i in [i for i in current['items'] if i.get('home')][:2])+'<a href="#current-information">休止・受付期限・お出かけの最新情報をまとめて見る →</a></aside><!-- CURRENT:QUICK:END -->'
 pos=text.index('<!-- ENRICHMENT:START -->');text=text[:pos]+quick+text[pos:]
 text=text.replace('住民票、税金、ごみ、子育て、介護、空き家、おくやみなど、湖西市の公式情報へ進むための入口を整理しています。','手続きの期限や持ち物、子育て、親の介護、住まい、休日のお出かけ。質問検索・準備チェック・施設案内から、必要な公式情報へ進めます。')
 text=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="湖西市の手続き・子育て・介護・住まい・観光を目的別に案内。最新の受付期限、必要書類、準備チェックリスト、施設・窓口検索、自治会別の介護相談先を調べられる非公式ナビです。">',text,count=1)
 home.write_text(text,encoding='utf-8',newline='\n')

def main():
 build_hubs();build_catalog();build_checklists();n=build_questions();build_directory();build_care_tool();build_emergency();build_audiences();update_home()
 import sys
 from discover_render import build as build_discover
 stories=build_discover(sys.modules[__name__])
 (ROOT/'data/auxiliary-pages.json').write_text(json.dumps(REGISTRY,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'pages':len(REGISTRY),'articles':stories,'questions':n,'facilities':len(DIRECTORY['items']),'checklists':len(CHECKS)},ensure_ascii=False))
if __name__=='__main__':main()
