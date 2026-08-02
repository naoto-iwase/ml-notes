// Language switcher + 404 back-link. Static hreflang tags come from _filters/hreflang.lua.
var I18N = {
  // switchLink reads in the *target* language because clicking takes you there.
  ja: { switchLink: '🌐 Read in English', back404: '← ML Notes トップに戻る' },
  en: { switchLink: '🌐 日本語で読む',     back404: '← Back to ML Notes' },
};

document.addEventListener('DOMContentLoaded', function() {
  var path = window.location.pathname;
  var match = path.match(/^\/(ja|en)\//);
  var is404 = document.body.classList.contains('is-404');
  var container = document.querySelector('#quarto-content > main');

  if (!match) {
    if (is404 && container) {
      container.insertAdjacentHTML('beforeend',
        '<p><a href="/">' + I18N.en.back404 + '</a></p>');
    }
    return;
  }

  var currentLang = match[1];
  var targetLang = currentLang === 'ja' ? 'en' : 'ja';
  var t = I18N[currentLang];
  // On 404 the mirrored path is also missing — point at the language root instead.
  var targetPath = is404
    ? '/' + targetLang + '/'
    : path.replace('/' + currentLang + '/', '/' + targetLang + '/');
  if (container) {
    container.insertAdjacentHTML('afterbegin',
      '<div class="lang-switch"><a href="' + targetPath + '">' + t.switchLink + '</a></div>');
    if (is404) {
      container.insertAdjacentHTML('beforeend',
        '<p><a href="/' + currentLang + '/">' + t.back404 + '</a></p>');
    }
  }
});
