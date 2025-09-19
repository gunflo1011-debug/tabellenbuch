
// Mobile nav toggle + small UX niceties
(function(){
  function ready(fn){/in/.test(document.readyState)?setTimeout(fn,9):fn()}
  ready(function(){
    // Toggle nav
    var toggle = document.getElementById('menuToggle');
    var nav = document.getElementById('siteNav');
    if(toggle && nav){
      toggle.addEventListener('click', function(){
        var open = nav.getAttribute('data-open') === 'true';
        nav.setAttribute('data-open', String(!open));
        toggle.setAttribute('aria-expanded', String(!open));
      });
    }
    // Ensure all images are lazy if not specified
    document.querySelectorAll('img:not([loading])').forEach(function(img){
      img.setAttribute('loading','lazy');
      img.setAttribute('decoding','async');
    });
    // Wrap tables if needed
    document.querySelectorAll('table').forEach(function(tbl){
      if(!tbl.parentElement || !tbl.parentElement.classList.contains('table-responsive')){
        var wrap = document.createElement('div');
        wrap.className = 'table-responsive';
        tbl.parentNode.insertBefore(wrap, tbl);
        wrap.appendChild(tbl);
      }
    });
  });
})();
