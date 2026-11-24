"""本文の生成元を反映し、既存canonical・計測・回遊・共通部品を保持する。"""
import json,re
from pathlib import Path
from generate_pages import ROOT, load, load_content_map, render_page, esc, update_date

def home_updates_html(updates):
    last = updates.get('updated_at', updates['checked_at'])
    cards = []
    for item in updates['items']:
        if not item.get('home'):
            continue
        day = item.get('checked_at', updates['checked_at'])
        cards.append(f'<article class="current-update"><h3><a href="{esc(item["pages"][0])}">{esc(item["title"])}</a></h3><p>{esc(item["summary"])}</p><p class="mini">確認日：<time datetime="{esc(day)}">{update_date(day)}</time></p></article>')
    return f'<section class="updates current-updates" id="current-information"><h2>暮らしの最新情報・受付期限</h2><p>この欄の最終更新：<time datetime="{esc(last)}">{update_date(last)}</time>。案内ごとに確認日と対象期間をご確認ください。</p><div class="current-updates-grid">{"".join(cards)}</div><p><a class="btn" href="https://www.city.kosai.shizuoka.jp/" target="_blank" rel="noopener">湖西市公式の新着情報を見る</a></p></section>'

def main():
    ledger,city=load(); content=load_content_map(); changed=[]
    boundary='<h2 class="sec">あわせて確認したい'
    for item in ledger:
        path=ROOT/item['href'].strip('/')/'index.html'
        old=path.read_text(encoding='utf-8')
        rendered,_=render_page(item,city,[i for i in ledger if i['category']==item['category']],content)
        body=rendered[rendered.index('<main>'):rendered.index(boundary)]
        # Optional update blocks must not create an empty line in unaffected pages.
        body=body.replace('</section>\n\n','</section>\n')
        new=old[:old.index('<main>')]+body+old[old.index(boundary):]
        if new!=old:
            path.write_text(new,encoding='utf-8',newline='\n'); changed.append(item['href'])
    updates=json.loads((ROOT/'data/current-updates.json').read_text(encoding='utf-8'))
    section=home_updates_html(updates)
    home=ROOT/'index.html'; old=home.read_text(encoding='utf-8')
    new,n=re.subn(r'<section class="updates(?: current-updates)?"[^>]*>.*?</section>',lambda _:section,old,count=1,flags=re.S)
    assert n==1
    if new!=old:home.write_text(new,encoding='utf-8',newline='\n')
    print(json.dumps({'updated_pages':changed,'count':len(changed)},ensure_ascii=False))
if __name__=='__main__': main()
