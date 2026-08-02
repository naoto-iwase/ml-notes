// Moves prev/next page-navigation above #quarto-appendix so the bibliography stays last.
(function () {
  function init() {
    const main = document.querySelector('#quarto-content > main');
    if (!main) return;
    const appendix = main.querySelector('#quarto-appendix');
    const pageNav = document.querySelector('#quarto-content > nav.page-navigation');
    if (!appendix || !pageNav) return;
    appendix.parentNode.insertBefore(pageNav, appendix);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
