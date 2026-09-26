(function(){
  function fixFrame(){
    if (window.innerWidth > 900) return;
    var p = document.querySelector('.phone');
    if (p) {
      p.style.setProperty('width', '100vw', 'important');
      p.style.setProperty('max-width', '100vw', 'important');
      p.style.setProperty('height', '100vh', 'important');
      p.style.setProperty('border-radius', '0', 'important');
      p.style.setProperty('box-shadow', 'none', 'important');
      p.style.setProperty('margin', '0', 'important');
      p.style.setProperty('background', '#fff', 'important');
    }
    var n = document.querySelector('.notch');
    if (n) n.style.setProperty('display', 'none', 'important');
    var s = document.querySelector('.status');
    if (s) s.style.setProperty('display', 'none', 'important');
    document.body.style.setProperty('padding', '0', 'important');
    document.body.style.setProperty('margin', '0', 'important');
    document.body.style.setProperty('background', '#f2f2f7', 'important');
    document.body.style.setProperty('display', 'block', 'important');
    document.body.style.setProperty('align-items', 'initial', 'important');
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixFrame);
  } else {
    fixFrame();
  }
  window.addEventListener('resize', fixFrame);
})();