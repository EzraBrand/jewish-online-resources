// Table view: loads data/resources.json, renders a filterable, sortable table.
// State is kept in the URL hash so filtered views can be linked.
(function () {
  "use strict";
  const ACCESS = { open: "Open access", registration: "Free, registration", freemium: "Freemium",
    subscription: "Subscription", purchase: "Purchase", unknown: "Unknown" };
  const LANG = { he: "Hebrew", en: "English", arc: "Aramaic", yi: "Yiddish", de: "German",
    fr: "French", ar: "Arabic", jrb: "Judeo-Arabic", grc: "Greek", la: "Latin", es: "Spanish",
    ru: "Russian", it: "Italian", lad: "Ladino" };
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  // Fold Hebrew niqqud/cantillation and case so searches match loosely.
  const fold = (s) => String(s ?? "").normalize("NFD").replace(/[֑-ׇ̀-ͯ]/g, "").toLowerCase();

  let rows = [], sortKey = null, sortDir = 1;

  function where(e) {
    return [e.section, e.subsection].filter(Boolean).join(" › ");
  }

  function fillSelect(sel, values, label) {
    const el = $(sel);
    values.forEach(([v, n]) => {
      const o = document.createElement("option");
      o.value = v; o.textContent = `${label ? label(v) : v} (${n})`;
      el.appendChild(o);
    });
  }

  function counts(list) {
    const m = new Map();
    list.forEach((v) => m.set(v, (m.get(v) || 0) + 1));
    return [...m.entries()];
  }

  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    $("#q").value = p.get("q") || "";
    $("#f-section").value = p.get("section") || "";
    $("#f-access").value = p.get("access") || "";
    $("#f-lang").value = p.get("lang") || "";
    $("#f-tag").value = p.get("tag") || "";
    $("#t-new").checked = p.get("new") === "1";
    $("#t-hidedead").checked = p.get("hidedead") === "1";
  }

  function writeHash() {
    const p = new URLSearchParams();
    const add = (k, v) => { if (v) p.set(k, v); };
    add("q", $("#q").value.trim());
    add("section", $("#f-section").value);
    add("access", $("#f-access").value);
    add("lang", $("#f-lang").value);
    add("tag", $("#f-tag").value);
    if ($("#t-new").checked) p.set("new", "1");
    if ($("#t-hidedead").checked) p.set("hidedead", "1");
    const h = p.toString();
    history.replaceState(null, "", h ? "#" + h : location.pathname);
  }

  function nameCell(e) {
    let name = esc(e.name);
    if (e.url && e.link_verdict === "hijacked") name = `<span class="link-removed">${name}</span>`;
    else if (e.url) name = `<a href="${esc(e.url)}" class="${e.link_verdict === "dead" ? "dead" : ""}" target="_blank" rel="noopener">${name}</a>`;
    const he = e.name_he ? `<span class="he" dir="rtl" lang="he">${esc(e.name_he)}</span>` : "";
    const b = [];
    if (e.edition === "2026") b.push('<span class="badge new">New 2026</span>');
    if (e.link_verdict === "dead" || e.link_verdict === "hijacked") {
      b.push('<span class="badge bad">dead link</span>');
      if (e.link_archive) b.push(`<a class="archive" href="${esc(e.link_archive)}" target="_blank" rel="noopener">[archive]</a>`);
    } else if (e.link_verdict === "moved") b.push(`<span class="badge moved" title="${esc(e.link_note)}">link updated</span>`);
    return `${name}${he}<div>${b.join(" ")}</div>`;
  }

  function render() {
    writeHash();
    const q = fold($("#q").value.trim());
    const fs = $("#f-section").value, fa = $("#f-access").value, fl = $("#f-lang").value, ft = $("#f-tag").value;
    const onlyNew = $("#t-new").checked, hideDead = $("#t-hidedead").checked, expand = $("#t-expand").checked;
    let list = rows.filter((e) =>
      (!fs || e.section === fs) && (!fa || e.access === fa) &&
      (!fl || e.languages.includes(fl)) && (!ft || e.tags.includes(ft)) &&
      (!onlyNew || e.edition === "2026") &&
      (!hideDead || !["dead", "hijacked"].includes(e.link_verdict)) &&
      (!q || e._text.includes(q)));
    if (sortKey) {
      const val = (e) => sortKey === "where" ? where(e) : sortKey === "langs" ? e.languages.join(",") : (e[sortKey] || "");
      list = [...list].sort((a, b) => String(val(a)).localeCompare(String(val(b))) * sortDir);
    }
    $("#count").textContent = `${list.length} of ${rows.length} resources`;
    const out = [];
    for (const e of list) {
      const hasMore = e.annotation_html || e.footnotes_html || e.status_note;
      out.push(`<tr class="row" id="r-${esc(e.id)}">
        <td class="name">${nameCell(e)}</td>
        <td class="where">${esc(where(e))}${e.group ? `<br><i>${esc(e.group)}</i>` : ""}</td>
        <td><span class="badge acc-${esc(e.access)}">${esc(ACCESS[e.access] || e.access)}</span></td>
        <td class="langs" title="${esc(e.languages.map((l) => LANG[l] || l).join(", "))}">${esc(e.languages.join(" "))}</td>
        <td>${esc(e.summary)}<div>${e.tags.map((t) => `<span class="tag">#${esc(t)}</span>`).join("")}</div>
          ${hasMore ? `<button class="more" data-id="${esc(e.id)}" aria-expanded="${expand}">${expand ? "Hide notes" : "Notes"}</button>` : ""}</td></tr>`);
      if (hasMore) {
        out.push(`<tr class="detail" data-for="${esc(e.id)}" ${expand ? "" : "hidden"}><td colspan="5">
          ${e.status_note ? `<p class="status-note">${esc(e.status_note)}</p>` : ""}
          <div class="annotation">${e.annotation_html}</div>${e.footnotes_html}
          <p><a href="guide.html#${esc(e.id)}">View in full guide</a></p></td></tr>`);
      }
    }
    $("#tbl tbody").innerHTML = out.join("");
  }

  document.addEventListener("click", (ev) => {
    const btn = ev.target.closest("button.more");
    if (btn) {
      const d = document.querySelector(`tr.detail[data-for="${CSS.escape(btn.dataset.id)}"]`);
      const open = d.hidden;
      d.hidden = !open;
      btn.textContent = open ? "Hide notes" : "Notes";
      btn.setAttribute("aria-expanded", String(open));
      return;
    }
    const th = ev.target.closest("th[data-k]");
    if (th) {
      const k = th.dataset.k;
      sortDir = sortKey === k ? -sortDir : 1;
      sortKey = k;
      document.querySelectorAll("th[data-k]").forEach((h) => h.removeAttribute("aria-sort"));
      th.setAttribute("aria-sort", sortDir === 1 ? "ascending" : "descending");
      render();
    }
  });

  fetch("data/resources.json?v=" + (document.querySelector("meta[name=data-version]")?.content || Date.now())).then((r) => r.json()).then((data) => {
    rows = data.entries.map((e) => ({
      ...e,
      _text: fold([e.name, e.name_he, e.summary, e.tags.join(" "), e.section, e.subsection, e.group,
        e.annotation_html.replace(/<[^>]+>/g, " ")].join(" ")),
    }));
    // Table view: the "Existing Guides" meta-list (section "Intro") goes last.
    const secOrder = [...data.sections.filter((s) => s !== "Intro"), "Intro"];
    const rank = (e) => { const i = secOrder.indexOf(e.section); return i < 0 ? 99 : i; };
    rows = rows.map((e, i) => ({ ...e, _i: i })).sort((a, b) => rank(a) - rank(b) || a._i - b._i);
    const secs = counts(rows.map((e) => e.section)).sort((a, b) => secOrder.indexOf(a[0]) - secOrder.indexOf(b[0]));
    fillSelect("#f-section", secs);
    fillSelect("#f-access", counts(rows.map((e) => e.access)).sort((a, b) => b[1] - a[1]), (v) => ACCESS[v] || v);
    fillSelect("#f-lang", counts(rows.flatMap((e) => e.languages)).sort((a, b) => b[1] - a[1]), (v) => LANG[v] || v);
    fillSelect("#f-tag", counts(rows.flatMap((e) => e.tags)).sort((a, b) => a[0].localeCompare(b[0])));
    readHash();
    ["#q", "#f-section", "#f-access", "#f-lang", "#f-tag", "#t-new", "#t-hidedead", "#t-expand"].forEach((s) =>
      $(s).addEventListener(s === "#q" ? "input" : "change", render));
    render();
  }).catch((err) => {
    $("#count").textContent = "Could not load data/resources.json (open the site through a web server, not file://). " + err;
  });
})();
