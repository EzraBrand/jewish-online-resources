// Guide view: highlight the table-of-contents entry for the part of the guide
// that is on screen now, and keep that entry visible in the TOC panel.
(function () {
  "use strict";
  const toc = document.querySelector("nav.toc");
  if (!toc) return;
  const links = new Map();
  toc.querySelectorAll('a[href^="#"]').forEach((a) => links.set(decodeURIComponent(a.hash.slice(1)), a));
  const targets = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  const offset = () => (document.querySelector("header.site")?.offsetHeight || 0) + 16;
  let current = null;

  function update() {
    const y = offset();
    // Last heading whose top has scrolled above the line just under the sticky header.
    let active = targets[0];
    for (const t of targets) {
      if (t.getBoundingClientRect().top - y <= 1) active = t; else break;
    }
    if (!active || active === current) return;
    current = active;
    toc.querySelectorAll("a.current, a.current-parent").forEach((a) => a.classList.remove("current", "current-parent"));
    const a = links.get(active.id);
    a.classList.add("current");
    // Bold the parent section link too when a subsection is current.
    const parentLi = a.closest("ul")?.closest("li");
    const parentA = parentLi?.querySelector(":scope > a");
    if (parentA && parentA !== a) parentA.classList.add("current-parent");
    const r = a.getBoundingClientRect(), tr = toc.getBoundingClientRect();
    if (r.top < tr.top || r.bottom > tr.bottom) {
      toc.scrollTop += r.top - tr.top - tr.height / 3;
    }
  }

  let ticking = false;
  window.addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; update(); }); }
  }, { passive: true });
  window.addEventListener("hashchange", update);
  update();
})();
