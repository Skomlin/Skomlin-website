/* Skomlin Press, shared behaviour */
(function(){
  var t = document.getElementById('navToggle');
  var n = document.getElementById('mainNav');
  if(t && n){
    t.addEventListener('click', function(){
      var open = n.classList.toggle('open');
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
})();

function handleSignup(e){
  var form = e.target;
  var ctx = form.getAttribute('data-ctx');
  var btn = form.querySelector('button[type="submit"]');
  if(btn){ btn.disabled = true; btn.textContent = 'Submitting\u2026'; }
  setTimeout(function(){
    form.classList.add('hidden');
    var conf = document.getElementById('confirm-' + ctx);
    if(conf) conf.classList.add('show');
  }, 700);
  return true;
}

/* Old hash addresses keep working: #/book/slug becomes /books/slug/ */
(function(){
  var h = location.hash || '';
  if(h.indexOf('#/') !== 0) return;
  var parts = h.slice(2).split('/').filter(Boolean);
  var map = {catalogue:'/catalogue/', contributors:'/contributors/', trade:'/trade/', about:'/about/'};
  var dest = null;
  if(parts.length === 0) dest = '/';
  else if(parts[0] === 'book' && parts[1]) dest = '/books/' + parts[1] + '/';
  else if(parts[0] === 'contributor' && parts[1]) dest = '/people/' + parts[1] + '/';
  else if(map[parts[0]]) dest = map[parts[0]];
  if(dest && dest !== location.pathname) location.replace(dest);
})();
