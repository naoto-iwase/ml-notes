// Responsive panel collapse — floating chevrons live outside the panels they hide.
(function () {
  const LANG = document.documentElement.lang === 'ja' ? 'ja' : 'en';
  const I18N = {
    ja: {
      sidebar: { open: 'サイドバーを開く', close: 'サイドバーを閉じる' },
      toc: { open: '目次を開く', close: '目次を閉じる' },
    },
    en: {
      sidebar: { open: 'Open sidebar', close: 'Close sidebar' },
      toc: { open: 'Open table of contents', close: 'Close table of contents' },
    },
  };
  const t = I18N[LANG];

  const PANELS = [
    {
      name: 'sidebar',
      target: 'quarto-sidebar',
      labels: t.sidebar,
      closeIcon: 'bi-chevron-left',
      openIcon: 'bi-chevron-right',
    },
    {
      name: 'toc',
      target: 'TOC',
      labels: t.toc,
      closeIcon: 'bi-chevron-right',
      openIcon: 'bi-chevron-left',
    },
  ];

  const root = document.documentElement;

  function initPanel(panel) {
    if (!document.getElementById(panel.target)) return;

    const state = panel.name + '-collapsed';
    const btn = document.createElement('button');
    btn.id = 'site-' + panel.name + '-toggle';
    btn.className = 'site-panel-toggle ' + btn.id;
    btn.type = 'button';
    btn.setAttribute('aria-controls', panel.target);
    btn.innerHTML =
      '<i class="bi ' + panel.closeIcon + ' site-panel-toggle-close" aria-hidden="true"></i>' +
      '<i class="bi ' + panel.openIcon + ' site-panel-toggle-open" aria-hidden="true"></i>';

    const isCollapsed = () => root.classList.contains(state);
    function syncButton() {
      const collapsed = isCollapsed();
      btn.setAttribute('aria-label', collapsed ? panel.labels.open : panel.labels.close);
      btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
    }

    syncButton();
    document.body.appendChild(btn);
    btn.addEventListener('click', () => {
      const collapsed = !isCollapsed();
      localStorage.setItem('site-' + state, collapsed ? 'true' : 'false');
      root.classList.toggle(state, collapsed);
      syncButton();
    });
  }

  function init() {
    PANELS.forEach(initPanel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
