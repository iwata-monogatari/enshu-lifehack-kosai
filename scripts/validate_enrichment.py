#!/usr/bin/env python3
"""Check publication coverage, internal targets, labels and critical distinctions."""
import json,re,sys
from pathlib import Path
from urllib.parse import urlsplit,unquote
from collections import Counter
from bs4 import BeautifulSoup
from enrichment_render import LABELS
ROOT=Path(__file__).resolve().parent.parent
def load(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
topics=load('topics_master.json');aux=load('auxiliary-pages.json')
urls={'/','/terms/'}|{t['href'] for t in topics+aux};problems=[];soups={}
for u in urls:
 p=ROOT/u.strip('/')/'index.html' if u!='/' else ROOT/'index.html'
 if not p.exists():problems.append('Missing page: '+u);continue
 s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser');soups[u]=s
 if len(s.find_all('h1'))!=1:problems.append('H1 count: '+u)
 canonical=s.find('link',rel='canonical')
 if not canonical or canonical.get('href')!='https://kosai.enshu-lifehack.com'+u:problems.append('Canonical: '+u)
 ids=Counter(x['id'] for x in s.select('[id]'))
 for id,count in ids.items():
  if count>1:problems.append('Duplicate ID: '+u+'#'+id)
 if not s.select('link[href*="enrichment.css"]'):problems.append('Missing CSS: '+u)
 for el in s.select('input:not([type="hidden"]),select'):
  if not (el.get('aria-label') or el.get('aria-labelledby') or (el.get('id') and s.find('label',attrs={'for':el['id']}))):problems.append('Unlabelled input: '+u)
incoming=Counter()
for u,s in soups.items():
 for a in s.select('a[href],link[href],script[src],img[src]'):
  raw=a.get('href') or a.get('src');v=urlsplit(raw)
  if v.scheme or v.netloc:continue
  if not raw.startswith(('/','#')):continue
  path=unquote(v.path) or u
  if path.endswith('/'):
   if path not in urls:problems.append('Unknown internal page: '+u+' -> '+raw);continue
   if a.name=='a':incoming[path]+=1
   if v.fragment and not soups[path].find(id=unquote(v.fragment)):problems.append('Missing anchor: '+u+' -> '+raw)
  elif not (ROOT/path.lstrip('/')).exists():problems.append('Missing asset: '+u+' -> '+raw)
for a in aux:
 if not incoming[a['href']]:problems.append('Orphan auxiliary page: '+a['href'])
search=load('auxiliary-pages.json');index=json.loads((ROOT/'search-index.json').read_text(encoding='utf-8'))
if {t['href'] for t in index}!={t['href'] for t in topics+aux}:problems.append('Search coverage mismatch')
sitemap=set(re.findall(r'<loc>https://kosai.enshu-lifehack.com(.*?)</loc>',(ROOT/'sitemap.xml').read_text(encoding='utf-8')))
if sitemap!=urls:problems.append('Sitemap coverage mismatch')
for t in topics:
 for k in t.get('facts',{}):
  if k not in LABELS:problems.append('Missing Japanese label: '+k)
covered=[cat for h in load('hubs.json') for cat in h['categories']]
if Counter(covered)!=Counter(set(t['category'] for t in topics)):problems.append('Purpose hub category coverage mismatch')
for c in load('checklists.json'):
 for i in c['items']:
  if i['href'] not in urls:problems.append('Checklist target: '+i['href'])
centers=load('care-centers.json')['items'];districts=[d for c in centers for d in c['districts']]
if len(districts)!=len(set(districts)):problems.append('Duplicate care district')
if next(c for c in centers if '神座' in c['districts'])['phone']!='053-573-2050':problems.append('Wrong 神座 center')
if next(c for c in centers if '岡崎' in c['districts'])['phone']!='053-577-5455':problems.append('Wrong 岡崎 center')
directory=load('kosai-directory.json')['items']
library_matches=[el for el in soups['/kosai-directory/'].select('[data-filter-item]') if '図書館' in el['data-search']]
if len(library_matches)!=2:problems.append('Library keyword includes unrelated cultural facilities')
for f in directory:
 if not f['sources'] or not f['checked_at']:problems.append('Facility source/date missing: '+f['name'])
gym=next(f for f in directory if '勤労者' in f['name'])
if '体育室全面' not in ''.join(gym['details']) or 'トレーニング室・卓球室は利用可能' not in ''.join(gym['details']):problems.append('Gym closure scope wrong')
for u,s in soups.items():
 if 'トレーニングジムは2026年8月1日' in s.get_text():problems.append('Stale erroneous gym draft: '+u)
 if u=='/life/start-living/water-start-stop-fees/' and '3日前' in str(s.title):problems.append('Stale water heading')
result={'pages':len(urls),'existing_topics':len(topics),'auxiliary_pages':len(aux),'facilities':len(directory),'question_entries':len(soups['/questions/'].select('[data-filter-item]')),'internal_targets':sum(incoming.values()),'errors':problems,'status':'PASS' if not problems else 'FAIL'}
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(problems))
