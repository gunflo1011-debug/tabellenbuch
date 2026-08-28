(function () {
  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    var toggle = document.getElementById('menuToggle');
    var nav = document.getElementById('siteNav');

    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.getAttribute('data-open') === 'true';
        nav.setAttribute('data-open', String(!open));
        toggle.setAttribute('aria-expanded', String(!open));
        toggle.setAttribute('aria-label', open ? 'Open navigation' : 'Close navigation');
      });

      nav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
          nav.setAttribute('data-open', 'false');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.setAttribute('aria-label', 'Open navigation');
        });
      });
    }

    var categorySearch = document.querySelector('[data-category-filter]');
    if (categorySearch) {
      var params = new URLSearchParams(window.location.search);
      var initialQuery = params.get('q') || '';
      if (initialQuery) categorySearch.value = initialQuery;

      function filterCategories() {
        var query = categorySearch.value.trim().toLowerCase();
        document.querySelectorAll('#categoryGrid .card').forEach(function (card) {
          card.hidden = query.length > 0 && !card.textContent.toLowerCase().includes(query);
        });
      }

      categorySearch.addEventListener('input', filterCategories);
      filterCategories();
      if (initialQuery) categorySearch.focus();
    }

    document.querySelectorAll('img:not([loading])').forEach(function (img) {
      img.setAttribute('loading', 'lazy');
      img.setAttribute('decoding', 'async');
    });

    document.querySelectorAll('table').forEach(function (table) {
      if (!table.parentElement || !table.parentElement.classList.contains('table-responsive')) {
        var wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      }
    });
  });
})();
