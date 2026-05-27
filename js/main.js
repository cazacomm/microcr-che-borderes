/* ==========================================================================
   Micro-crèche Le Jardin des Merveilles - JS principal
   - Smooth scroll
   - Mobile menu toggle
   - Animations (pulse géré en CSS)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Mobile menu ----------
  const burger = document.getElementById('burger');
  const menu = document.getElementById('mobile-menu');
  const closeBtn = document.getElementById('menu-close');

  if (burger && menu) {
    burger.addEventListener('click', () => {
      menu.classList.add('open');
      document.body.style.overflow = 'hidden';
    });
  }
  if (closeBtn && menu) {
    closeBtn.addEventListener('click', () => {
      menu.classList.remove('open');
      document.body.style.overflow = '';
    });
  }
  if (menu) {
    menu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        menu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // ---------- Smooth scroll pour les ancres internes ----------
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId.length <= 1) return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  // ---------- Active link in header ----------
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.site-header nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
  });

  // ---------- Pulse stagger (decale l'animation des 2 family cards pour effet visuel) ----------
  const familyCards = document.querySelectorAll('.family-card');
  familyCards.forEach((c, i) => {
    c.style.animationDelay = `${i * 0.6}s`;
  });

  // ---------- Boutons "Accéder aux préinscriptions" ----------
  // Quand le lien de la plateforme externe sera disponible, le mettre ci-dessous.
  // Il s'ouvrira automatiquement dans un nouvel onglet.
  const PREINSCRIPTION_URL = '';
  document.querySelectorAll('a[data-link="preinscription"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (PREINSCRIPTION_URL) {
        window.open(PREINSCRIPTION_URL, '_blank', 'noopener');
      }
    });
  });
});
