/* Local-only progressive enhancements. No entered terms or checklist states are sent. */
(() => {
  'use strict';
  const norm = value => value.normalize('NFKC').toLocaleLowerCase('ja').replace(/[\s　]+/g, ' ').trim();
  document.querySelectorAll('[data-filter-list]').forEach(root => {
    const query = root.querySelector('[data-filter-query]');
    const category = root.querySelector('[data-filter-category]');
    const items = [...root.querySelectorAll('[data-filter-item]')];
    const more = root.querySelector('[data-filter-more]');
    const size = Number(root.dataset.pageSize) || 20;
    const prepared = items.map(el => ({ el, text: norm(el.dataset.search || el.textContent), category: el.dataset.category }));
    let limit = size;
    function render() {
      const words = norm(query.value).split(' ').filter(Boolean);
      const matches = prepared.filter(item => (!category.value || item.category === category.value) && words.every(word => item.text.includes(word)));
      const visible = new Set(matches.slice(0, limit).map(item => item.el));
      items.forEach(el => { el.hidden = !visible.has(el); });
      root.querySelector('[data-filter-count]').textContent = `${matches.length}件が該当・${Math.min(limit, matches.length)}件を表示（全${items.length}件）`;
      root.querySelector('[data-filter-empty]').hidden = matches.length !== 0;
      more.hidden = matches.length <= limit;
    }
    query.addEventListener('input', () => { limit = size; render(); });
    category.addEventListener('change', () => { limit = size; render(); });
    root.querySelector('[data-filter-reset]').addEventListener('click', () => { query.value = ''; category.value = ''; limit = size; render(); query.focus(); });
    more.addEventListener('click', () => {
      const previous = limit;
      limit += size; render();
      const firstNew = items.filter(el => !el.hidden)[previous];
      const target = firstNew?.querySelector('summary, a, button');
      target?.focus();
    });
    // A copied facility anchor reveals its card even beyond the first page.
    if (location.hash) {
      const target = items.find(el => '#' + el.id === location.hash);
      if (target) limit = Math.ceil((items.indexOf(target) + 1) / size) * size;
    }
    render();
  });

  document.querySelectorAll('[data-checklist]').forEach(root => {
    const boxes = [...root.querySelectorAll('[data-check-item]')];
    const key = `kosai-checklist:${root.dataset.checklist}:${root.dataset.version}`;
    const status = root.querySelector('[data-save-status]');
    let storageAvailable = true;
    try {
      const stored = JSON.parse(localStorage.getItem(key) || '[]');
      if (Array.isArray(stored)) boxes.forEach(box => { box.checked = stored.includes(box.id); });
    } catch (_) { storageAvailable = false; }
    function update(save) {
      const selected = boxes.filter(box => box.checked).map(box => box.id);
      root.querySelector('[data-check-progress]').textContent = `${selected.length} / ${boxes.length} 項目をチェック済み`;
      if (save && storageAvailable) {
        try { localStorage.setItem(key, JSON.stringify(selected)); } catch (_) { storageAvailable = false; }
      }
      status.textContent = storageAvailable ? 'チェックはこのブラウザーに保存します。共有端末では使い終わったらチェックを外してください。' : 'このブラウザーでは保存できません。現在の画面でチェック・印刷はできます。';
    }
    boxes.forEach(box => box.addEventListener('change', () => update(true)));
    root.querySelector('[data-check-reset]').addEventListener('click', () => { boxes.forEach(box => { box.checked = false; }); update(true); });
    root.querySelector('[data-print]').addEventListener('click', () => window.print());
    update(false);
  });

  const selector = document.querySelector('[data-care-select]');
  if (selector) {
    const cards = [...document.querySelectorAll('[data-care-center]')].map(el => ({el, districts: JSON.parse(el.dataset.districts)}));
    selector.addEventListener('change', () => {
      let selected = '';
      cards.forEach(({el, districts}) => {
        el.hidden = Boolean(selector.value) && !districts.includes(selector.value);
        if (selector.value && !el.hidden) selected = el.querySelector('h3').textContent;
      });
      document.querySelector('[data-care-status]').textContent = selector.value ? `${selector.value}の担当：${selected}` : '未選択時は4センターすべてを表示します。';
    });
  }
})();
