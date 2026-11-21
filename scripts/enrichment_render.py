"""Small reusable renderers for existing life pages."""
import json,re
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parent.parent
def e(value):return escape(str(value),quote=True)
LABELS={
'address':'所在地','allergy':'アレルギー対応','application':'申請方法','application_deadline':'申請期限','branch':'支所','branches':'支所・窓口','bus_fare':'バス運賃','challenge_room':'チャレンジルーム','checkup_period':'健診期間','child_dental':'子どもの歯科健診','child_fee':'子どもの費用','consult_center':'相談窓口','content':'内容','core_hospital':'基幹病院','cost':'費用','deadline':'期限','dental_checkup':'歯科健診','districts':'対象地区','due':'納期限','elementary':'小学校','fax':'FAX','fees':'料金','flood_rivers':'洪水の想定河川','gappei':'合併','handbook_types':'手帳の種類','hashtag_dial':'短縮ダイヤル','hospital_er':'救急外来','hotlines':'相談電話','hours':'受付・利用時間','how_to_search':'探し方','hpv':'HPVワクチン','ijyu_shugyo_amount':'移住・就業支援金','junior_high':'中学校','kokoro_denwa':'こころの相談電話','kouki_koureisha':'後期高齢者医療','map_editions':'地図の版・種類','method':'方法','mileage':'マイレージ','no_duty_day':'当番医のない日','note':'確認事項','period':'期間','phone_consult':'電話相談','plan_name':'計画名','pneumococcal_65':'高齢者肺炎球菌','psych_handbook_renewal':'精神障害者保健福祉手帳の更新','rail':'鉄道','schedule':'日程','schedule_change_2026':'2026年度の日程変更','seats':'席・定員','service_types':'サービスの種類','shingles':'帯状疱疹','sougou_soudan':'総合相談','target':'対象','teiju_shorei_target':'定住奨励金の対象','tel':'電話','tel_adult':'大人の相談電話','tel_child':'子どもの相談電話','tenshutsu_deadline':'転出届の期限','tenyu_deadline':'転入届の期限','tokutei_kenshin':'特定健診','tsunami_height':'津波の想定','tsunami_note':'津波についての注意','window':'担当窓口','window_adult':'大人の相談窓口','window_child':'子どもの相談窓口'}
def practical_html(href):
 data=json.loads((ROOT/'data/practical-guides.json').read_text(encoding='utf-8'));parts=[]
 for g in data['items']:
  if href not in g['pages']:continue
  rows=''.join(f'<dt>{e(r["label"])}</dt><dd>{e(r["text"])}</dd>' for r in g['rows'])
  steps=''.join(f'<li>{e(s)}</li>' for s in g['steps'])
  sources=''.join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a>' for s in g['sources'])
  parts.append(f'<section class="practical-guide"><h2>{e(g["title"])}</h2><p class="mini">この確認表の照合日：{e(g["checked_at"])}。以下の項目を公式掲載内容と照合しました。</p><dl class="practical-facts">{rows}</dl><h3>準備の順番</h3><ol>{steps}</ol><div class="source-list">{sources}</div></section>')
 return ''.join(parts)
def guide_navigation():
 return '<nav class="utility-nav" aria-label="ほかの探し方"><a href="/guides/">全ガイド</a><a href="/questions/">質問から探す</a><a href="/checklist/">準備チェック</a><a href="/kosai-directory/">施設・窓口</a><a href="/tools/care-center/">介護の相談先</a></nav>'
def add_toc(html):
 start=html.index('<main>');end=html.index('<h2 class="sec">あわせて確認したい')
 fragment=html[start:end];headings=[]
 def heading(m):
  number=len(headings)+1;label=re.sub('<[^>]+>','',m[2]);id=f'guide-section-{number}';headings.append((id,label))
  return f'<h2{m[1]} id="{id}">{m[2]}</h2>'
 fragment=re.sub(r'<h2([^>]*)>(.*?)</h2>',heading,fragment,flags=re.S)
 nav='<nav class="page-toc" aria-label="このページの目次"><strong>このページで確認できること</strong>'+''.join(f'<a href="#{id}">{label}</a>' for id,label in headings)+'</nav>'
 marker='<!-- LIFE:TOC -->';fragment=fragment.replace(marker,nav)
 return html[:start]+fragment+html[end:]
