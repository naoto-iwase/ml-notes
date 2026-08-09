// Per-tab category sidebar + URL hash tab switching + RSS link relocation.
document.addEventListener('DOMContentLoaded', function() {
  var tabs = document.querySelectorAll('.panel-tabset .nav-link');
  var categoryContainer = document.querySelector('.quarto-listing-category');
  var languageStorageKey = 'site-listing-language';

  function detectLang(el) {
    var t = el ? el.textContent : '';
    return (t.toLowerCase().includes('japanese') || t.includes('日本語')) ? 'ja' : 'en';
  }

  if (categoryContainer && tabs.length > 0) {
    var initialLang = detectLang(document.querySelector('.panel-tabset .nav-link.active'));
    var currentLang = initialLang;

    function dataFor(listingId) {
      var listing = document.getElementById(listingId);
      var items = listing ? listing.querySelectorAll('.quarto-post') : [];
      var cats = {};
      items.forEach(function(item) {
        item.querySelectorAll('.listing-category').forEach(function(d) {
          var m = (d.getAttribute('onclick') || '').match(/quartoListingCategory\('([^']*)'\)/);
          var code = m ? m[1] : '';
          if (!cats[code]) cats[code] = { name: d.textContent.trim(), count: 0 };
          cats[code].count++;
        });
      });
      return { categories: cats, total: items.length };
    }

    var langData = { ja: dataFor('listing-listing-ja'), en: dataFor('listing-listing-en') };

    function row(code, name, count, active) {
      return '<div class="category' + (active ? ' active' : '') +
        '" data-category="' + code + '">' + name +
        ' <span class="quarto-category-count">(' + count + ')</span></div>';
    }

    function renderCategories(lang) {
      var data = langData[lang];
      var active = categoryContainer.querySelector('.category.active');
      var activeCode = active ? active.getAttribute('data-category') : '';
      var html = row('', 'All', data.total, !activeCode);
      Object.keys(data.categories)
        .sort(function(a, b) { return data.categories[a].name.localeCompare(data.categories[b].name); })
        .forEach(function(code) {
          html += row(code, data.categories[code].name, data.categories[code].count, activeCode === code);
        });
      categoryContainer.innerHTML = html;
    }

    categoryContainer.addEventListener('click', function(e) {
      var cat = e.target.closest('.category');
      if (!cat) return;
      window.quartoListingCategory(cat.getAttribute('data-category'));
      categoryContainer.querySelectorAll('.category').forEach(function(c) {
        c.classList.toggle('active', c === cat);
      });
    });

    renderCategories(initialLang);

    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var lang = detectLang(tab);
        localStorage.setItem(languageStorageKey, lang);
        if (lang !== currentLang) {
          currentLang = lang;
          renderCategories(lang);
        }
        history.replaceState(null, null, '#' + lang);
      });
    });

    function activate() {
      var hash = location.hash.slice(1);
      var hasLanguageHash = hash === 'ja' || hash === 'en';
      var lang = hasLanguageHash ? hash : localStorage.getItem(languageStorageKey);
      if (lang !== 'ja' && lang !== 'en') return;
      tabs.forEach(function(tab) {
        if (detectLang(tab) === lang) tab.click();
      });
      // A remembered preference should not add a fragment to a clean URL.
      if (!hasLanguageHash) {
        history.replaceState(null, null, location.pathname + location.search);
      }
    }
    activate();
    addEventListener('hashchange', activate);
  }

  // Reveal category sidebar after build (CSS hides it until .ready, avoiding FOUC).
  if (categoryContainer) categoryContainer.classList.add('ready');

  document.querySelectorAll('.rss-link').forEach(function(link) {
    var listing = link.nextElementSibling;
    if (listing && listing.classList.contains('quarto-listing')) {
      var actions = listing.querySelector('.listing-actions-group');
      if (actions) actions.insertBefore(link, actions.firstChild);
    }
  });
});
