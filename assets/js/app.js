/* 기탄사고력교실 검단아라학원 — 화면 동작
   외부 라이브러리 없이 동작합니다. */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ------------------------------------------------------------ toast --- */
  var toastEl = $("#toast");
  var toastTimer = null;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2400);
  }

  /* ------------------------------------------------------- reveal anim --- */
  var revealables = $$(".reveal");
  if ("IntersectionObserver" in window) {
    var roi = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); roi.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealables.forEach(function (el) { roi.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("in"); });
  }

  /* --------------------------------------------------- active nav state --- */
  var navLinks = $$("[data-nav]");
  var deskLinks = $$(".desktop-nav a");
  var sections = ["home", "grades", "library", "notice", "contact"]
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);

  function setActive(id) {
    navLinks.forEach(function (a) { a.classList.toggle("active", a.getAttribute("data-nav") === id); });
    deskLinks.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + id); });
  }

  if ("IntersectionObserver" in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) setActive(e.target.id);
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ----------------------------------------------------- absence rules --- */
  var RULES = {
    personal:
      "<strong>개인 사정으로 인한 결석은 보강이 어렵습니다.</strong> " +
      "가족 일정·병원·컨디션 조절로 결석하시면, 아이가 다음 진도에 맞춰 따라갈 수 있도록 수업 중에 다시 짚어 드립니다. " +
      "결석한 수업의 원비 차감은 어렵습니다.",
    sick:
      "<strong>전염병(독감·수족구·눈병 등)은 보강해 드립니다.</strong> " +
      "2일(2회) 결석당 1회, 최대 2회까지 보강이 가능합니다. " +
      "아이 컨디션이 회복된 뒤에 보강 날짜를 정해 드리니, 신청서에 희망 시간대를 남겨 주세요.",
    travel:
      "<strong>연 1회 가족여행은 미리 알려 주시면 보강해 드립니다.</strong> " +
      "전염병과 같은 기준으로 2일(2회) 결석당 1회, 최대 2회까지 가능합니다. " +
      "여행 날짜를 아실 때 미리 남겨 주시면 교재와 진도를 맞춰 준비하겠습니다.",
    etc:
      "<strong>그 밖의 사정은 원장이 함께 살펴봅니다.</strong> " +
      "아래 신청서에 상황을 적어 주시면, 아이에게 가장 알맞은 방법을 찾아 안내드립니다."
  };

  var ruleNote = $("#ruleNote");
  $$(".reason").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var key = btn.getAttribute("data-reason");
      $$(".reason").forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
      if (ruleNote && RULES[key]) { ruleNote.innerHTML = RULES[key]; }
      if (ruleNote) {
        ruleNote.style.borderColor = "var(--coral)";
        ruleNote.style.background = "var(--coral-soft)";
      }
    });
  });

  /* --------------------------------------------------------- embeds ----- */
  function wireEmbed(btnSel, boxSel, url, height) {
    var btn = $(btnSel), box = $(boxSel);
    if (!btn || !box) return;
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      if (open) {
        btn.setAttribute("aria-expanded", "false");
        box.hidden = true;
        return;
      }
      if (!box.dataset.loaded) {
        var frame = document.createElement("iframe");
        frame.src = url + "?embedded=true";
        frame.height = String(height);
        frame.title = "구글 설문지";
        frame.loading = "lazy";
        frame.setAttribute("allowfullscreen", "");
        box.appendChild(frame);
        var hint = document.createElement("p");
        hint.className = "embed-hint";
        hint.innerHTML = "화면이 잘 안 보이면 <a href=\"" + url +
          "\" target=\"_blank\" rel=\"noopener\">새 창에서 열기</a>를 눌러 주세요.";
        box.appendChild(hint);
        box.dataset.loaded = "1";
      }
      box.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      box.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  wireEmbed("#absenceEmbedBtn", "#absenceEmbed",
    "https://docs.google.com/forms/d/e/1FAIpQLSe3UJRa4yRVtruL1eiyrCl4P_P3JU2_Mr3i02pisarl5KZjUw/viewform", 980);
  wireEmbed("#feedbackEmbedBtn", "#feedbackEmbed",
    "https://docs.google.com/forms/d/e/1FAIpQLScRNKHqzgmw22P15QFCeG_HR1OmqL4lxMpe6J4qELiqbyCjqg/viewform", 900);

  /* --------------------------------------------------------- data load --- */
  function loadJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " " + r.status);
      return r.json();
    });
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  /* ------------------------------------------------------------ notices --- */
  var noticeList = $("#noticeList");
  if (noticeList) {
    loadJSON("data/notices.json").then(function (data) {
      var items = (data.items || []).slice(0, 6);
      if (!items.length) { noticeList.innerHTML = '<p class="embed-hint">등록된 공지가 없습니다.</p>'; return; }
      noticeList.innerHTML = items.map(function (n) {
        return '<div class="notice-item">' +
          '<span class="date">' + esc(n.date) + "</span>" +
          '<span class="txt"><strong>' + esc(n.title) +
          (n.isNew ? '<span class="new">NEW</span>' : "") + "</strong>" +
          "<p>" + esc(n.body) + "</p></span></div>";
      }).join("");
    }).catch(function () {
      noticeList.innerHTML =
        '<div class="notice-item"><span class="date">11.16</span><span class="txt">' +
        "<strong>12월 겨울방학 특강 안내</strong><p>특강 시간표와 학습지는 학원에서 안내드립니다.</p></span></div>";
    });
  }

  /* -------------------------------------------------------- Q&A board ---- */
  var board = $("#board");
  function renderBoard(items) {
    if (!items.length) {
      board.innerHTML = '<div class="empty-state"><strong>아직 남겨 주신 이야기가 없습니다.</strong>' +
        "첫 이야기를 기다리고 있습니다.</div>";
      return;
    }
    board.innerHTML = items.map(function (q) {
      var answered = q.answer && String(q.answer).trim();
      return '<article class="qa' + (answered ? "" : " pending") + '">' +
        '<div class="q-head"><span class="kind">' + esc(q.kind || "문의") + "</span>" +
        '<span class="who">' + esc(q.who || "학부모") + " · " + esc(q.asked_at || "") + "</span></div>" +
        "<h4>" + esc(q.title) + "</h4>" +
        '<p class="q-text">' + esc(q.question) + "</p>" +
        '<div class="a-wrap"><span class="a-mark" aria-hidden="true">답</span><div class="a-body">' +
        "<p>" + (answered ? esc(q.answer) : "확인하고 있습니다. 조금만 기다려 주세요.") + "</p>" +
        (answered && q.answered_at ? "<time>" + esc(q.answered_at) + "</time>" : "") +
        "</div></div></article>";
    }).join("");
  }

  if (board) {
    loadJSON("data/feedback.json").then(function (data) {
      renderBoard(data.items || []);
    }).catch(function () {
      board.innerHTML = '<div class="empty-state"><strong>게시판을 열 수 없습니다.</strong>' +
        "아래 <b>의견 남기기</b>로 이야기를 보내 주세요.</div>";
    });
  }

  /* ------------------------------------------------------------ videos --- */
  var gallery = $("#videoGallery");

  function videoInfo(url) {
    var u;
    try { u = new URL(url); } catch (e) { return null; }
    var host = u.hostname.replace(/^www\./, "");
    if (host === "youtube.com" || host === "m.youtube.com") {
      var id = u.searchParams.get("v");
      if (!id && u.pathname.indexOf("/shorts/") === 0) id = u.pathname.split("/")[2];
      if (!id && u.pathname.indexOf("/embed/") === 0) id = u.pathname.split("/")[2];
      if (id) return { type: "youtube", id: id, src: "https://www.youtube.com/embed/" + id, landscape: true };
    }
    if (host === "youtu.be") {
      var vid = u.pathname.split("/")[1];
      if (vid) return { type: "youtube", id: vid, src: "https://www.youtube.com/embed/" + vid, landscape: true };
    }
    if (host === "instagram.com") {
      var parts = u.pathname.split("/").filter(Boolean);
      if (parts.length >= 2 && (parts[0] === "reel" || parts[0] === "p" || parts[0] === "tv")) {
        return {
          type: "instagram",
          id: parts[1],
          src: "https://www.instagram.com/" + parts[0] + "/" + parts[1] + "/embed",
          landscape: false
        };
      }
    }
    return null;
  }

  if (gallery) {
    loadJSON("data/videos.json").then(function (data) {
      var items = (data.items || []).map(function (it) {
        var info = videoInfo(it.url || "");
        return info ? Object.assign({}, it, info) : null;
      }).filter(Boolean);

      if (!items.length) {
        gallery.innerHTML =
          '<div class="empty-state" style="grid-column:1/-1">' +
          "<strong>영상은 인스타그램에서 먼저 만나 보실 수 있습니다.</strong>" +
          "릴스를 올리면 이곳에 영상이 바로 보이도록 준비해 두었습니다.</div>";
        var wrap = document.createElement("div");
        wrap.style.gridColumn = "1/-1";
        wrap.style.textAlign = "center";
        wrap.innerHTML = '<a class="btn btn-ghost btn-sm" href="' +
          (data.instagram || "https://www.instagram.com/aragitan123/") +
          '" target="_blank" rel="noopener">@aragitan123 릴스 보기</a>';
        gallery.appendChild(wrap);
        return;
      }

      gallery.innerHTML = items.map(function (v) {
        var frame = '<iframe src="' + esc(v.src) + '" loading="lazy" scrolling="no" allowfullscreen ' +
          'title="' + esc(v.title || "학원 영상") + '"></iframe>';
        return '<article class="video-card' + (v.landscape ? " landscape" : "") + '">' +
          '<div class="video-frame">' + frame + "</div>" +
          '<div class="cap"><strong>' + esc(v.title || "학원 영상") + "</strong>" +
          esc(v.caption || "") + "</div></article>";
      }).join("");
    }).catch(function () {
      gallery.innerHTML =
        '<div class="empty-state" style="grid-column:1/-1">' +
        "<strong>영상을 불러오지 못했습니다.</strong>" +
        '<a href="https://www.instagram.com/aragitan123/" target="_blank" rel="noopener">인스타그램에서 보기</a>' +
        "</div>";
    });
  }

  /* --------------------------------------------------- phone copy helper -- */
  $$("a[href^='tel:']").forEach(function (a) {
    a.addEventListener("click", function () {
      toast("전화 앱으로 연결합니다");
    });
  });

  /* ------------------------------------------------------- smooth focus --- */
  window.addEventListener("hashchange", function () {
    var id = location.hash.replace("#", "");
    if (id) setActive(id);
  });
})();
