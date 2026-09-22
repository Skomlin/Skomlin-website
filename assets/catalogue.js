/* Catalogue filtering. Cards are already in the HTML; this only hides and shows them. */
(function(){
  var search = document.getElementById('catSearch');
  var roleSel = document.getElementById('catRole');
  var seriesSel = document.getElementById('catSeries');
  var grid = document.getElementById('catGrid');
  var empty = document.getElementById('catEmpty');
  var count = document.getElementById('catCount');
  if(!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.book-card'));
  var total = cards.length;

  function draw(){
    var q = (search.value || '').trim().toLowerCase();
    var role = roleSel.value;
    var ser = seriesSel.value;
    var shown = 0;
    cards.forEach(function(card){
      var ok = true;
      if(role && (card.getAttribute('data-roles') || '').split('|').indexOf(role) === -1) ok = false;
      if(ok && ser && card.getAttribute('data-series') !== ser) ok = false;
      if(ok && q && (card.getAttribute('data-search') || '').indexOf(q) === -1) ok = false;
      card.classList.toggle('hidden', !ok);
      if(ok) shown++;
    });
    count.textContent = shown === total ? (total + ' titles') : (shown + ' of ' + total + ' titles');
    empty.classList.toggle('hidden', shown !== 0);
  }

  search.addEventListener('input', draw);
  roleSel.addEventListener('change', draw);
  seriesSel.addEventListener('change', draw);
  draw();
})();
