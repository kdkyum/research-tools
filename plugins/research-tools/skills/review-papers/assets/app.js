/* review-papers shared behavior: KaTeX auto-render, scroll reveal, animated bars. */
(function () {
  "use strict";

  function renderMath() {
    if (typeof renderMathInElement !== "function") return;
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "\\(", right: "\\)", display: false },
          { left: "$", right: "$", display: false },
        ],
        throwOnError: false,
        // Optional convenience macros — edit/remove per topic.
        macros: { "\\neg": "\\lnot", "\\E": "\\mathbb{E}", "\\R": "\\mathbb{R}" },
      });
    } catch (e) { /* no-op */ }
  }
  if (document.readyState !== "loading") renderMath();
  else document.addEventListener("DOMContentLoaded", renderMath);

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setupReveal() {
    var els = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
    if (reduce || !("IntersectionObserver" in window)) { els.forEach(function (el) { el.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  }

  function setupBars() {
    var bars = Array.prototype.slice.call(document.querySelectorAll(".bar-fill[data-w]"));
    function fill(el) { el.style.setProperty("--w", el.getAttribute("data-w")); }
    if (reduce || !("IntersectionObserver" in window)) { bars.forEach(fill); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { fill(en.target); io.unobserve(en.target); } });
    }, { threshold: 0.5 });
    bars.forEach(function (el) { io.observe(el); });
  }

  // --- Floating section nav (auto-built table of contents) ---
  function buildTOC() {
    if (document.querySelector(".tocnav")) return;
    var main = document.querySelector("main") || document.body;
    var targets = [];
    function headingText(el) {
      if (/^H[1-4]$/.test(el.tagName)) return el.textContent;
      var h = el.querySelector(".section-head .label, h2, h3, .label");
      return h ? h.textContent : "";
    }
    var ex = document.querySelectorAll("[data-nav]");
    if (ex.length) {
      Array.prototype.forEach.call(ex, function (el) {
        targets.push({ el: el, level: parseInt(el.getAttribute("data-nav"), 10) || 1,
          title: el.getAttribute("data-nav-title") || headingText(el) });
      });
    } else { // fallback: pages without explicit data-nav (e.g. per-paper pages)
      Array.prototype.forEach.call(main.querySelectorAll("section"), function (sec) {
        var hd = sec.querySelector(".section-head .label, h2, h3");
        if (hd) targets.push({ el: sec, level: 1, title: hd.textContent });
        Array.prototype.forEach.call(sec.querySelectorAll(".paper"), function (p) {
          var h = p.querySelector("h3");
          targets.push({ el: p, level: 2, title: h ? h.textContent : "Item" });
        });
      });
    }
    targets.forEach(function (t) { t.title = (t.title || "").replace(/\s+/g, " ").trim(); });
    targets = targets.filter(function (t) { return t.title; });
    if (targets.length < 3) return;
    function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "s"; }
    targets.forEach(function (t, i) { if (!t.el.id) t.el.id = "nav-" + slug(t.title) + "-" + i; });

    var nav = document.createElement("nav");
    nav.className = "tocnav"; nav.setAttribute("aria-label", "On this page");
    var panel = document.createElement("div");
    panel.className = "tocnav-panel"; panel.id = "tocnav-panel"; panel.hidden = true;
    var head = document.createElement("div"); head.className = "tocnav-head"; head.textContent = "On this page";
    var ul = document.createElement("ul"); ul.className = "tocnav-list";
    var byId = {};
    targets.forEach(function (t) {
      var li = document.createElement("li"); li.className = "lvl-" + t.level;
      var a = document.createElement("a"); a.href = "#" + t.el.id; a.textContent = t.title; a.title = t.title;
      li.appendChild(a); ul.appendChild(li); byId[t.el.id] = a;
    });
    panel.appendChild(head); panel.appendChild(ul);
    var btn = document.createElement("button");
    btn.className = "tocnav-toggle"; btn.type = "button";
    btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-controls", "tocnav-panel");
    var ico = document.createElement("span"); ico.className = "tn-ico"; ico.setAttribute("aria-hidden", "true"); ico.textContent = "≡";
    var txt = document.createElement("span"); txt.className = "tn-txt"; txt.textContent = "Contents";
    btn.appendChild(ico); btn.appendChild(txt);
    nav.appendChild(panel); nav.appendChild(btn);
    document.body.appendChild(nav);

    var curA = null;
    function scrollActiveIntoView() {
      if (!curA || panel.hidden) return;
      var pr = panel.getBoundingClientRect(), ar = curA.getBoundingClientRect();
      panel.scrollTop += (ar.top - pr.top) - panel.clientHeight / 2 + ar.height / 2;
    }
    function setOpen(o) {
      nav.classList.toggle("open", o); panel.hidden = !o;
      btn.setAttribute("aria-expanded", o ? "true" : "false"); ico.textContent = o ? "✕" : "≡";
      if (o) scrollActiveIntoView();
    }
    btn.addEventListener("click", function (e) { e.stopPropagation(); setOpen(panel.hidden); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) setOpen(false); });
    document.addEventListener("click", function (e) { if (!nav.contains(e.target) && !panel.hidden) setOpen(false); });
    Array.prototype.forEach.call(ul.querySelectorAll("a"), function (a) {
      a.addEventListener("click", function () { if (window.matchMedia("(max-width:600px)").matches) setOpen(false); });
    });

    function updateActive() {
      var cur = targets[0], best = -Infinity;
      targets.forEach(function (t) {
        var top = t.el.getBoundingClientRect().top - 120;
        if (top <= 1 && top > best) { best = top; cur = t; }
      });
      var a = byId[cur.el.id];
      if (a === curA) return;
      if (curA) curA.classList.remove("active");
      a.classList.add("active"); curA = a; scrollActiveIntoView();
    }
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(function () { updateActive(); ticking = false; }); }
    }, { passive: true });
    window.addEventListener("resize", function () { updateActive(); }, { passive: true });
    updateActive();
  }

  if (document.readyState !== "loading") { setupReveal(); setupBars(); buildTOC(); }
  else document.addEventListener("DOMContentLoaded", function () { setupReveal(); setupBars(); buildTOC(); });
})();
