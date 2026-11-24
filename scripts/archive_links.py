"""Contextual links to individual Kosai archive photos."""
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ALBUM = 'https://kosaialb.atawi.link'
DATA = Path(__file__).resolve().parents[1] / 'data' / 'photo-guide-referrals.json'
PANEL = 'data-archive-photo-links'
LOCATIONS = re.compile(
    r'<section\b[^>]*(?:class="(?:story-related|feedback-box)"|id="story-list")[^>]*>'
    r'|<aside class="editorial-note">'
)


@lru_cache(maxsize=1)
def load_referrals():
    return json.loads(DATA.read_text(encoding='utf-8'))


class LinkedPhotos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.existing = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith(ALBUM+'/photos/'):
                self.existing.add(href)


def add_photo_links(html, path):
    if PANEL in html:
        return html
    sections = load_referrals().get(path, ())
    if not sections:
        return html
    parser = LinkedPhotos()
    parser.feed(html)
    blocks = []
    for section in sections:
        links = []
        for href, label in section['photos']:
            dest = ALBUM+href
            if dest in parser.existing:
                continue
            parser.existing.add(dest)
            links.append(f'<li><a href="{escape(dest)}" data-track-click="album_referral_context_photo">{escape(label)}</a></li>')
        if links:
            blocks.append(
                f'<aside class="editorial-note" {PANEL}><h2 class="sec">{escape(section["heading"])}</h2>'
                '<p>湖西懐かし写真館で、撮影時期や出典を確認できます。</p><ul>'
                +''.join(links)+'</ul></aside>'
            )
    if not blocks:
        return html
    match = LOCATIONS.search(html)
    index = match.start() if match else html.index('</div></main>')
    return html[:index]+''.join(blocks)+html[index:]
