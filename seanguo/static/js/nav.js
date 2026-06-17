(function(){
    // 在移动端点击“服务”展开/收起
    const dd = document.querySelector('.nav-item.dropdown');
    if(!dd) return;
    const link = dd.querySelector('.nav-link');
    link.addEventListener('click', function(e){
      // 仅在小屏下阻止直接跳转，进行展开
      if (window.matchMedia('(max-width: 900px)').matches) {
        e.preventDefault();
        dd.classList.toggle('open');
      }
    });
    // 点击外部收起
    document.addEventListener('click', function(e){
      if (!dd.contains(e.target)) dd.classList.remove('open');
    });
  })();
  