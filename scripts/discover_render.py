"""Sourced editorial articles. Called by build_enrichment, which owns the registry."""
import json,re
from html import escape
from pathlib import Path

COLORS={'街道と宿場':('#eae2d5','#755638','街道を歩く'),'寺社と文化財':('#e5ece0','#496545','歴史を読む'),'人物と地域文化':('#f4e5d9','#865332','地域を知る'),'湖・海・山の自然':('#dcecf0','#286576','自然を訪ねる'),'地域を歩く':('#e6e5f0','#5e547f','土地をつなぐ')}

ALBUM_ORIGIN = 'https://kosaialb.atawi.link'
ALBUM_FEATURES = (
 ('/features/arai-shuku/', '新居宿・新居関所の古写真'),
 ('/features/shirasuka/', '白須賀宿・潮見坂の昔の写真'),
 ('/features/aerial/', '鷲津・新居など湖西市の空中写真'),
 ('/features/kosai-station/', '新所原・鷲津・新居町の駅前写真'),
)

def album_link(path, label, placement):
 target = path.strip('/').rsplit('/', 1)[-1].replace('-', '_') or 'top'
 event = f'album_referral_{placement}_{target}'
 return f'<a href="{escape(ALBUM_ORIGIN+path)}" data-track-click="{escape(event)}">{escape(label)}</a>'

def album_feature_links():
 links = ''.join(f'<li>{album_link(path, label, "discover_index")}</li>' for path, label in ALBUM_FEATURES)
 return ('<aside class="story-summary" aria-label="湖西懐かし写真館の特集">'
         '<h2>湖西の昔を、写真で見比べる</h2>'
         '<p>'+album_link('/','湖西懐かし写真館','discover_index')+
         'で、新居と白須賀の旧東海道、駅舎、浜名湖西岸をたどります。写真ごとに撮影時期や出典を確認できます。</p>'
         f'<ul>{links}</ul></aside>')

def article_album_link(photo):
 return ('<aside class="story-summary" aria-label="湖西懐かし写真館の関連写真">'
         '<h2>湖西懐かし写真館で見比べる</h2>'
         f'<p>{escape(photo["description"])}</p>'
         f'<p>{album_link(photo["path"], photo["label"], "discover_article")}</p></aside>')

def build(g):
 data=g.load('discover-articles.json'); by={a['slug']:a for a in data}; e=g.e
 def url(a):return '/discover/'+a['slug']+'/'
 def card(a):
  bg,fg,k=COLORS[a['category']]
  return f'<article class="story-card" data-filter-item data-category="{e(a["category"])}" data-search="{e(a["title"]+" "+a["area"]+" "+a["lead"])}"><div class="story-card-top" style="--story-bg:{bg};--story-ink:{fg}"><span>{e(k)}</span><strong>{e(a["area"])}</strong></div><div class="story-card-body"><h2><a href="{url(a)}">{e(a["title"])}</a></h2><p>{e(a["lead"])}</p><a class="story-read" href="{url(a)}">記事を読む <span aria-hidden="true">→</span></a></div></article>'
 def refs(a,ns):
  return '<p class="story-cite">出典：'+ ' ／ '.join(f'<a href="{e(a["sources"][n]["url"])}" target="_blank" rel="noopener">{e(a["sources"][n]["label"])}</a>' for n in ns)+'</p>'
 def photograph(p):
  small,large=p['images']; license_url=p['licenseUrl'].replace('http://','https://',1)
  inherited=' この掲載画像にも同じ表示・継承ライセンスを適用します。' if '/by-sa/' in license_url else ''
  return '<figure class="story-photo"><a href="'+e(p['album_url'])+'" aria-label="'+e(p['title'])+'を湖西懐かし写真館で見る"><img src="'+e(large['url'])+'" srcset="'+e(small['url'])+' '+str(small['width'])+'w, '+e(large['url'])+' '+str(large['width'])+'w" sizes="(max-width: 820px) 92vw, 780px" width="'+str(large['width'])+'" height="'+str(large['height'])+'" alt="'+e(p['alt'])+'" loading="lazy" decoding="async"></a><figcaption><p class="photo-caption">'+e(p['caption'])+'</p><p class="photo-date">'+e(p['dateLabel'])+'</p><p class="photo-credit">出典：<a href="'+e(p['source'])+'">'+e(p['credit'])+'</a><br>利用条件：<a href="'+e(license_url)+'">'+e(p['license'])+'</a></p><p class="photo-album"><a href="'+e(p['album_url'])+'">湖西懐かし写真館で、この写真を詳しく見る →</a></p><details class="photo-reuse"><summary>画像の加工・利用について</summary><p>原作品名：'+e(p['source_title'])+'</p><p>'+e(p['change'])+' 湖西懐かし写真館の掲載用画像を使用し、本記事では追加の切り抜き・着色はしていません。'+inherited+'</p></details></figcaption></figure>'
 def enrich(href,title,lead,body,icon='📚',category='観光・歴史・地域情報',synonyms=None,article=None):
  g.write(href,title,lead,body,category,icon,synonyms)
  p=g.ROOT/href.strip('/')/'index.html';s=p.read_text(encoding='utf-8')
  s=s.replace('暮らしに合わせて、次の一歩へ','湖西を知る、歩く、楽しむ')
  s=s.replace('<body class="enriched-page">','<body class="enriched-page story-page">')
  s=s.replace('</head>','<link rel="stylesheet" href="/assets/discover.css?v=20261121photos"></head>')
  s=s.replace(g.nav(),'<nav class="utility-nav" aria-label="湖西の記事を探す"><a href="/discover/">観光・歴史の記事一覧</a><a href="/kosai-directory/">施設・窓口検索</a><a href="/for-visitors/">お出かけの準備</a><a href="/guides/">暮らしのガイド</a></nav>')
  if article:
   s=re.sub(r'<aside class="editorial-note">.*?</aside>','',s,flags=re.S)
   s=s.replace('／ '+e(title)+'</p>','／ <a href="/discover/">観光・歴史</a> ／ '+e(article['area'])+'</p>',1)
   schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':lead,'inLanguage':'ja','datePublished':'2026-11-21','dateModified':article['checked_at'],'author':{'@type':'Organization','name':'湖西ライフハック'},'mainEntityOfPage':g.SITE+href,'citation':[x['url'] for x in article['sources']]}
   if article.get('photos'):
    schema['image']=[{'@type':'ImageObject','contentUrl':g.SITE+p['images'][-1]['url'],'caption':p['caption'],'creditText':p['credit'],'license':p['licenseUrl'],'isBasedOn':p['source']} for p in article['photos']]
   s=s.replace('</head>','<meta property="og:type" content="article"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(lead)+'"><meta property="og:url" content="'+g.SITE+href+'"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
  p.write_text(s,encoding='utf-8',newline='\n')
 for a in data:
  bg,fg,k=COLORS[a['category']]
  body=f'<article class="story-body"><div class="story-meta"><span>{e(a["category"])} · {e(a["area"])}</span><time datetime="{a["checked_at"]}">資料確認：2026年11月21日</time></div>'
  body+='<aside class="story-summary"><h2>訪ねる前の基本情報</h2><dl>'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(v)+'</dd></div>' for k,v in a['facts'].items())+'</dl></aside>'
  body+='<nav class="page-toc story-toc" aria-label="記事の目次"><strong>この記事でわかること</strong>'+''.join(f'<a href="#section-{i+1}">{i+1:02d}　{e(sec["heading"])}</a>' for i,sec in enumerate(a['sections']))+'<a href="#questions">よくある質問</a><a href="#sources">出典と確認範囲</a></nav>'
  if a['timeline']:
   body+='<section class="story-timeline"><h2>年代をたどる</h2><ol>'+''.join('<li><strong>'+e(y)+'</strong><span>'+e(t)+'</span></li>' for y,t in a['timeline'])+'</ol><p class="mini">下記の公式資料に基づく年代整理。建物の創建・再建・復元を区別しています。</p></section>'
  for i,sec in enumerate(a['sections']):
   body+=f'<section class="story-section" id="section-{i+1}"><p class="story-number" aria-hidden="true">{i+1:02d}</p><h2>{e(sec["heading"])}</h2>'+''.join('<p>'+e(p)+'</p>' for p in sec['paragraphs'])+refs(a,sec['sources'])+'</section>'
   body+=''.join(photograph(p) for p in a.get('photos',[]) if p['after_section']==i+1)
   if a.get('related_archive') and a['related_archive']['after_section']==i+1:
    body+=article_album_link(a['related_archive'])
  if a.get('photo_archive') and not a.get('photos'):
   photo=a['photo_archive']
   body+='<aside class="story-summary" aria-label="昔の写真から地域をたどる"><h2>写真で、昔の景色をたどる</h2><p>この場所が写る写真も見てみませんか。<a href="'+e(photo['url'])+'">'+e(photo['label'])+'</a>を、湖西懐かし写真館で紹介しています。写真の出典や撮影時期も確認できます。</p></aside>'
  body+='<section id="questions" class="story-faq"><h2>よくある質問</h2>'+''.join('<details><summary>'+e(q['q'])+'</summary><p>'+e(q['a'])+'</p></details>' for q in a['qa'])+'</section>'
  body+='<section id="sources" class="story-sources"><h2>出典と確認範囲</h2><p>2026年11月21日に確認した市・観光協会・運営者の公開資料を基に編集しています。現地の実踏・体験記ではありません。由来や伝承と、現在の利用案内を分けて記載しました。季節の花・当日の営業・次回の祭礼日程は各公式案内でご確認ください。</p><ul>'+''.join('<li><a href="'+e(x['url'])+'" target="_blank" rel="noopener">'+e(x['label'])+'</a></li>' for x in a['sources'])+'</ul></section></article>'
  body+='<section class="story-related"><h2>この地域を、もう少し読む</h2><div class="story-grid">'+''.join(card(by[r]) for r in a['related'])+'</div></section>'
  enrich(url(a),a['title'],a['lead'],category=a['category'],body=body,article=a,synonyms=[a['area'],a['category'],a['title'].split('：')[0]])
 g.REGISTRY[:]=[x for x in g.REGISTRY if x['href']!='/discover/']
 body='<section class="story-intro"><p class="eyebrow">まちの背景を知ると、いつもの景色が変わる</p><h2>街道から山寺へ。湖から暮らしへ。</h2><p>新居関所と白須賀宿の歴史、寺社に伝わる文化財、豊田佐吉の発明、浜名湖の自然と食。由来を読む記事と、訪ねるための情報を一緒にまとめました。</p><div class="story-topics">'+''.join(f'<span>{e(c)}</span>' for c in COLORS)+'</div></section>'
 body+=album_feature_links()
 body+='<aside class="story-now"><h2>秋冬に出かける前に</h2><ul><li>本興寺の庭園は木曜定休、冬季拝観は15:30までの案内があります。<a href="/discover/honkouji/">拝観条件を確認</a></li><li>新居関所の企画展は11月23日まで、次回は11月28日から。<a href="/discover/arai-sekisho/">会期を見る</a></li><li>おちばの里親水公園は12月4日にトイレ等の一時休止予定。<a href="/discover/ochiba-haiji/">登山前の確認</a></li></ul><p class="mini">2026年11月21日確認。花の見頃や終了済みの夏の催しを、現在開催中とは案内していません。</p></aside>'
 body+='<section id="story-list"><h2>地域・関心から記事を探す</h2><div data-filter-list data-page-size="30">'+g.search_controls('stories','場所・人物・知りたいこと','例：新居、白須賀、豊田佐吉、食',list(COLORS))+'<div class="story-grid">'+''.join(card(a) for a in data)+'</div><button type="button" class="load-more" data-filter-more hidden>続きを表示</button></div></section>'
 body+='<section><h2>訪問の準備と暮らしの情報</h2>'+g.cards([('/kosai-directory/','施設の所在地・連絡先','住所や電話、利用条件を施設名で検索。'),('/for-visitors/','移動・駐車・出発前の確認','公共交通と気象・避難の確認先へ。'),('/hub/enjoy/','公園・文化・地域活動','施設予約や暮らしのガイドも確認。')])+'</section>'
 enrich('/discover/','湖西の観光・歴史・地域情報','新居・白須賀の宿場、寺社と古代遺跡、豊田佐吉、浜名湖・湖西連峰、食と祭り。湖西を深く知る読み物と、訪問前に役立つ案内を探せます。',body,icon='🌿',synonyms=['観光','歴史','地域情報','記事一覧'])
 home=g.ROOT/'index.html';s=home.read_text(encoding='utf-8')
 s=re.sub(r'<!-- DISCOVER:START -->.*?<!-- DISCOVER:END -->','',s,flags=re.S)
 featured=['arai-sekisho','sakichi-toyoda','kosai-food']
 block='<section class="home-discover"><p class="eyebrow">観光・歴史・地域の読み物</p><h2>湖西のことを、もっと知る</h2><p>宿場の面影、山寺の遺跡、発明家の足跡、湖と海が育てた食。場所の背景まで読める記事をまとめました。</p>'+g.cards([(url(by[k]),by[k]['title'],by[k]['lead']) for k in featured])+'<p class="all-tools-link"><a href="/discover/">観光・歴史・地域情報の記事一覧へ →</a></p><p>昔の景色も見てみたい方は、'+album_link('/','湖西懐かし写真館','home')+'へ。新居の水辺や駅前など、写真に残るまちの記憶をたどれます。</p></section>'
 pos=s.index('<section id="category-links"');s=s[:pos]+'<!-- DISCOVER:START -->'+block+'<!-- DISCOVER:END -->'+s[pos:];home.write_text(s,encoding='utf-8',newline='\n')
 return len(data)
