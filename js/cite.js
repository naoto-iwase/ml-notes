// Cite popover. Data: /assets/citations.json (built by _scripts/build_citations.py).
(function () {
  const LANG = document.documentElement.lang === 'ja' ? 'ja' : 'en';
  const I18N = {
    ja: { btn: '引用', title: 'このノートを引用', citation: '引用情報', bibtex: 'BibTeX', copy: 'コピー', copied: 'コピー済み', link: 'このノートを引用' },
    en: { btn: 'Cite', title: 'Cite this note', citation: 'Citation', bibtex: 'BibTeX', copy: 'Copy', copied: 'Copied!', link: 'Cite this note' },
  };
  const t = I18N[LANG];

  function currentNoteKey() {
    const m = window.location.pathname.match(/^\/(ja|en)\/([^/]+)\//);
    if (!m) return null;
    if (document.body.classList.contains('is-404')) return null;
    return `${m[1]}/${m[2]}`;
  }

  function loadCitations() {
    return fetch('/assets/citations.json')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .catch((err) => {
        console.warn('cite.js: failed to load citations.json', err);
        return { notes: {} };
      });
  }

  function buildPopover(entry) {
    const pop = document.createElement('div');
    pop.id = 'site-cite-popover';
    pop.className = 'site-cite-popover hidden';
    pop.setAttribute('role', 'dialog');
    pop.setAttribute('aria-label', t.title);
    pop.innerHTML = `
      <div class="site-cite-title">${t.title}</div>
      <div class="site-cite-section-header">
        <span class="site-cite-section-label">${t.citation}</span>
        <button class="site-cite-copy-btn" type="button" data-cite-copy="formatted">${t.copy}</button>
      </div>
      <div class="site-cite-formatted"></div>
      <div class="site-cite-section-header">
        <span class="site-cite-section-label">${t.bibtex}</span>
        <button class="site-cite-copy-btn" type="button" data-cite-copy="bibtex">${t.copy}</button>
      </div>
      <pre class="site-cite-bibtex"><code></code></pre>
    `;
    document.body.appendChild(pop);
    const bibtexCode = pop.querySelector('.site-cite-bibtex code');
    const formattedEl = pop.querySelector('.site-cite-formatted');
    let currentFormatted;
    let currentBibtex;
    pop.refreshFormatted = () => {
      // Local TZ to match git %cs (committer-local) used for last-updated.
      const accessed = new Date().toLocaleDateString('sv-SE');
      currentFormatted = entry.formatted.replace('{accessed}', accessed);
      currentBibtex = entry.bibtex.replace('{accessed}', accessed);
      formattedEl.textContent = currentFormatted;
      bibtexCode.textContent = currentBibtex;
    };
    pop.refreshFormatted();

    const copyTargets = {
      formatted: { getText: () => currentFormatted, fallbackEl: formattedEl },
      bibtex: { getText: () => currentBibtex, fallbackEl: pop.querySelector('.site-cite-bibtex') },
    };
    pop.querySelectorAll('.site-cite-copy-btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const target = copyTargets[btn.dataset.citeCopy];
        try {
          await navigator.clipboard.writeText(target.getText());
          btn.textContent = t.copied;
          setTimeout(() => (btn.textContent = t.copy), 1200);
        } catch {
          const range = document.createRange();
          range.selectNodeContents(target.fallbackEl);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
        }
      });
    });

    return pop;
  }

  function positionPopover(pop, anchor) {
    const r = anchor.getBoundingClientRect();
    pop.style.visibility = 'hidden';
    pop.classList.remove('hidden');
    const pw = pop.offsetWidth;
    const ph = pop.offsetHeight;
    const left = Math.max(8, Math.min(window.innerWidth - pw - 8, r.right - pw));
    const above = r.top > window.innerHeight / 2 && r.top - ph - 8 >= 8;
    const top = above ? r.top - ph - 8 : r.bottom + 8;
    pop.style.left = `${left}px`;
    pop.style.top = `${top}px`;
    pop.style.visibility = '';
  }

  function injectSidebarTrigger() {
    const container = document.querySelector('.sidebar-tools-main');
    if (!container) return null;
    if (container.querySelector('.site-cite-toggle-sidebar')) return null;
    const a = document.createElement('a');
    a.href = '';
    a.className = 'site-cite-toggle-sidebar quarto-navigation-tool px-1';
    a.setAttribute('aria-haspopup', 'dialog');
    a.setAttribute('aria-label', t.title);
    a.title = t.btn;
    a.innerHTML = '<i class="bi bi-quote"></i>';
    container.appendChild(a);
    return a;
  }

  // Placed above #quarto-appendix so the bibliography stays the last block.
  function injectEndLink() {
    const main = document.querySelector('#quarto-content > main');
    if (!main) return null;
    if (main.querySelector('.site-cite-end-link')) return null;
    const p = document.createElement('p');
    p.className = 'site-cite-end-link';
    const a = document.createElement('a');
    a.href = '';
    a.className = 'site-cite-trigger';
    a.innerHTML = `<i class="bi bi-quote"></i> ${t.link}`;
    p.appendChild(a);

    const appendix = main.querySelector('#quarto-appendix');
    if (appendix) {
      appendix.parentNode.insertBefore(p, appendix);
    } else {
      main.appendChild(p);
    }
    return a;
  }

  async function init() {
    const noteKey = currentNoteKey();
    if (!noteKey) return;

    const data = await loadCitations();
    const entry = data.notes?.[noteKey];
    if (!entry) return;

    const sidebarTrigger = injectSidebarTrigger();
    const endTrigger = injectEndLink();
    if (!sidebarTrigger && !endTrigger) return;

    const pop = buildPopover(entry);

    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('.site-cite-toggle-sidebar, .site-cite-trigger');
      if (trigger) {
        e.preventDefault();
        if (pop.classList.contains('hidden')) {
          pop.refreshFormatted();
          positionPopover(pop, trigger);
        } else pop.classList.add('hidden');
        return;
      }
      if (!pop.contains(e.target)) pop.classList.add('hidden');
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') pop.classList.add('hidden');
    });
    window.addEventListener('resize', () => {
      if (pop.classList.contains('hidden')) return;
      positionPopover(pop, sidebarTrigger || endTrigger);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
