(function(){
  const clickAway = (menu, btn) => (e)=>{
    if(!menu.contains(e.target) && !btn.contains(e.target)){
      menu.classList.remove('show'); document.removeEventListener('click', clickAway(menu, btn));
    }
  };
  window.toggleLangMenu = function(){
    const menu = document.getElementById('lang-menu');
    const btn = document.getElementById('lang-btn');
    const will = !menu.classList.contains('show');
    menu.classList.toggle('show', will);
    if(will){ setTimeout(()=>document.addEventListener('click', clickAway(menu, btn)), 0); }
  };
})();