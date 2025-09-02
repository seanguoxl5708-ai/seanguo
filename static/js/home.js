(function(){
    // 1) 成就数字滚动
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const els = document.querySelectorAll('.metric-value');
    if(!prefersReduced && 'IntersectionObserver' in window){
      const io = new IntersectionObserver((entries)=>{
        entries.forEach(entry=>{
          if(entry.isIntersecting){
            animate(entry.target);
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.6 });
      els.forEach(el=>io.observe(el));
    }
  
    function animate(el){
      const target = parseFloat(el.getAttribute('data-target') || '0');
      const suffix = el.getAttribute('data-suffix') || '';
      let cur = 0;
      const dur = 900; // ms
      const start = performance.now();
      function tick(t){
        const p = Math.min(1, (t - start) / dur);
        const val = Math.floor(target * (0.2 + 0.8 * easeOutCubic(p)));
        el.textContent = val + suffix;
        if(p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }
  
    function easeOutCubic(x){ return 1 - Math.pow(1 - x, 3); }
  
    // 2) 可选：平滑滚动（大多数浏览器用 CSS 已支持）
    document.querySelectorAll('a[href^="#"]').forEach(a=>{
      a.addEventListener('click', (e)=>{
        const id = a.getAttribute('href');
        const el = document.querySelector(id);
        if(el){
          e.preventDefault();
          el.scrollIntoView({ behavior:'smooth', block:'start' });
        }
      });
    });
  })();
  