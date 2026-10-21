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

// Copy-link button on each section and subsection heading.
(function () {
  "use strict";
  const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>';
  const heads = [...document.querySelectorAll(".guide section[id] > h2, .guide h3[id]")];
  heads.forEach((h) => {
    const id = h.id || h.parentElement.id;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "anchor-copy";
    btn.title = "Copy link to this section";
    btn.setAttribute("aria-label", "Copy link to section: " + h.textContent.trim());
    btn.innerHTML = ICON;
    btn.addEventListener("click", async () => {
      const url = location.origin + location.pathname + "#" + encodeURIComponent(id);
      let ok = true;
      try { await navigator.clipboard.writeText(url); } catch (e) {
        // Older browsers or blocked Clipboard API: copy from a hidden textarea.
        const ta = document.createElement("textarea");
        ta.value = url;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { ok = document.execCommand("copy"); } catch (e2) { ok = false; }
        ta.remove();
      }
      history.replaceState(null, "", "#" + encodeURIComponent(id));
      btn.classList.add("copied");
      const msg = document.createElement("span");
      msg.className = "anchor-msg";
      msg.textContent = ok ? "Copied" : "Link in address bar";
      btn.appendChild(msg);
      setTimeout(() => { btn.classList.remove("copied"); msg.remove(); }, 1500);
    });
    h.appendChild(btn);
  });
})();
