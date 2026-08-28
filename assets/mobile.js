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
      });
    }

    var categorySearch = document.querySelector('[data-category-filter]');
    if (categorySearch) {
      categorySearch.addEventListener('input', function () {
        var query = categorySearch.value.trim().toLowerCase();
        document.querySelectorAll('#categoryGrid .card').forEach(function (card) {
          card.hidden = query.length > 0 && !card.textContent.toLowerCase().includes(query);
        });
      });
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
