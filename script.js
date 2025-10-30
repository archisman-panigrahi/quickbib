document.addEventListener('DOMContentLoaded', function(){
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  toggle?.addEventListener('click', function(){
    if(!nav) return;
    if(getComputedStyle(nav).display === 'flex'){
      nav.style.display = 'none';
    } else {
      nav.style.display = 'flex';
      nav.style.flexDirection = 'column';
    }
  });
});
