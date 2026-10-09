// Guide view: highlight the table-of-contents entry for the part of the guide
// that is on screen now, and keep that entry visible in the TOC panel.
(function () {
  "use strict";
  const toc = document.querySelector("nav.toc");
  if (!toc) return;
  const header = document.querySelector("header.site");
  const root = document.documentElement;
  const links = new Map();
  toc.querySelectorAll('a[href^="#"]').forEach((a) => links.set(decodeURIComponent(a.hash.slice(1)), a));
  const targets = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  let current = null;
  let clicked = null; // id chosen in the TOC; wins while the page cannot scroll further

  // One number drives both where an anchor jump stops (scroll-padding) and when a
  // heading counts as reached, so the two can never disagree.
  let pad = 0;
  function setPad() {
    pad = (header ? header.offsetHeight : 0) + 12;
    root.style.scrollPaddingTop = pad + "px";
  }

  function mark(id) {
    if (id === current) return;
    current = id;
    toc.querySelectorAll("a.current, a.current-parent").forEach((a) => a.classList.remove("current", "current-parent"));
    const a = links.get(id);
    if (!a) return;
    a.classList.add("current");
    // Bold the parent section link too when a subsection is current.
    const parentA = a.closest("ul")?.closest("li")?.querySelector(":scope > a");
    if (parentA && parentA !== a) parentA.classList.add("current-parent");
    const r = a.getBoundingClientRect(), tr = toc.getBoundingClientRect();
    if (r.top < tr.top || r.bottom > tr.bottom) toc.scrollTop += r.top - tr.top - tr.height / 3;
  }

  function update() {
    const atBottom = window.scrollY + window.innerHeight >= root.scrollHeight - 2;
    if (clicked && atBottom) return mark(clicked);
    // Last heading whose top has reached the line under the sticky header.
    let active = targets[0];
    for (const t of targets) {
      if (t.getBoundingClientRect().top <= pad + 8) active = t; else break;
    }
    if (active) mark(active.id);
  }

  toc.addEventListener("click", (ev) => {
    const a = ev.target.closest('a[href^="#"]');
    if (!a) return;
    clicked = decodeURIComponent(a.hash.slice(1));
    mark(clicked);
  });

  let ticking = false;
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { ticking = false; update(); });
  }, { passive: true });
  // A scroll by the user (wheel, keys, touch) ends the "clicked" preference.
  ["wheel", "keydown", "touchmove"].forEach((t) => window.addEventListener(t, () => { clicked = null; }, { passive: true }));
  window.addEventListener("resize", () => { setPad(); update(); });
  window.addEventListener("hashchange", () => {
    clicked = decodeURIComponent(location.hash.slice(1)) || clicked;
    update();
  });

  setPad();
  // On load with a #fragment, the browser jumped before the padding was set; redo it.
  if (location.hash) {
    const el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el) { clicked = el.id; el.scrollIntoView(); }
  }
  update();
})();
