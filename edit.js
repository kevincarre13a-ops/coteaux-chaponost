/* Édition directe sur le site — actif uniquement pour une personne connectée (modifier/). */
(function () {
  'use strict';
  var AUTH = 'cc_auth', EDIT = 'cc_edit', GIT = '/.netlify/git/github', ID = '/.netlify/identity';
  var auth = null;
  try { auth = JSON.parse(localStorage.getItem(AUTH) || 'null'); } catch (e) {}
  if (!auth) return;
  var editing = false;
  try { editing = sessionStorage.getItem(EDIT) === '1'; } catch (e) {}

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    for (var k in (attrs || {})) n.setAttribute(k, attrs[k]);
    if (html != null) n.innerHTML = html;
    return n;
  }

  if (!editing) {
    var pill = el('button', { type: 'button' }, '✏️ Modifier le site');
    pill.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:300;background:#2e7d32;color:#fff;border:0;border-radius:40px;padding:14px 22px;font:700 18px Jost,sans-serif;box-shadow:0 4px 18px #0005;cursor:pointer';
    pill.onclick = function () { try { sessionStorage.setItem(EDIT, '1'); } catch (e) {} location.reload(); };
    document.body.appendChild(pill);
    return;
  }

  /* dialogue intégré : dialog({title, text, input, buttons:[{label,value,primary}]}) -> Promise(valeur du bouton ; texte saisi si input) */
  function dialog(o) {
    return new Promise(function (res) {
      var h = el('div', { 'class': 'cc-help cc-dlg' });
      h.innerHTML = '<div class="cc-help-card"><h2></h2><p></p>' + (o.input !== undefined ? '<input class="cc-dlg-in" type="text">' : '') + '<div class="cc-dlg-btns"></div></div>';
      h.querySelector('h2').textContent = o.title || '';
      var p = h.querySelector('p'); if (o.text) p.textContent = o.text; else p.remove();
      var inp = h.querySelector('input'); if (inp) inp.value = o.input || '';
      var box = h.querySelector('.cc-dlg-btns');
      (o.buttons || [{ label: 'OK', value: true, primary: true }]).forEach(function (b) {
        var bt = el('button', { type: 'button', 'class': b.primary ? 'cc-big' : 'cc-big cc-alt' });
        bt.textContent = b.label;
        bt.addEventListener('click', function () { h.remove(); res(inp && b.value === true ? inp.value : b.value); });
        box.appendChild(bt);
      });
      document.body.appendChild(h);
      if (inp) { inp.focus(); inp.select(); }
    });
  }
  function yesNo(title, text, yes, no) {
    return dialog({ title: title, text: text, buttons: [{ label: yes, value: true, primary: true }, { label: no, value: false }] });
  }

  var dirty = false, saving = false;
  var statusEl, saveBtn;

  function status(msg, kind) {
    if (!statusEl) return;
    statusEl.textContent = msg || '';
    statusEl.className = 'cc-status' + (kind ? ' ' + kind : '');
  }

  var TAGLABEL = { v: 'Vendanges', t: 'Travaux', f: 'Festivités', c: 'Événements' };
  var remote = {}, rev = {}, pub = {};   // empreintes : GitHub / page affichée / dernière mise en ligne

  function pageFiles() {
    var files = {};
    function need(k) { files[k.split('|')[0]] = 1; }
    document.querySelectorAll('[data-e]').forEach(function (n) { need(n.getAttribute('data-e')); });
    document.querySelectorAll('[data-list]').forEach(function (n) { need(n.getAttribute('data-list')); });
    document.querySelectorAll('[data-ei]').forEach(function (n) { need(n.getAttribute('data-ei')); });
    document.querySelectorAll('a[data-href]').forEach(function (n) { need(n.getAttribute('data-href')); });
    return Object.keys(files);
  }

  function pendingFiles() {
    return Object.keys(remote).filter(function (f) { return remote[f] !== rev[f] && remote[f] !== pub[f]; });
  }

  function richHtml(v) {
    var s = String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
  }
  function setImg(n, v) { if (n.tagName === 'IMG') n.src = v; else n.style.setProperty('--bg', 'url(' + v + ')'); }

  function fillItem(c, o) {
    c.querySelectorAll('[data-fd]').forEach(function (x) { if (o[x.getAttribute('data-fd')] != null) x.textContent = o[x.getAttribute('data-fd')]; });
    c.querySelectorAll('[data-fi]').forEach(function (x) { var v = o[x.getAttribute('data-fi')]; if (v) { x.src = v; if (o.title || o.caption) x.alt = o.title || o.caption; } });
    if (c.classList.contains('tile')) {
      c.dataset.tag = o.tag; c.dataset.cat = o.tag; c.dataset.cap = o.caption || '';
      var l = c.querySelector('.tlabel'); if (l) l.textContent = TAGLABEL[o.tag] || '';
    }
    if (c.classList.contains('evcard')) { var a = c.querySelector('a[href^="galerie.html#"]'); if (a) a.setAttribute('href', 'galerie.html#' + o.tag); }
    if (c.hasAttribute('data-youtube')) {
      var cap = c.querySelector('[data-fd="caption"]'), capP = cap.parentNode;
      Array.prototype.slice.call(c.children).forEach(function (x) { if (x !== capP) x.remove(); });
      c.setAttribute('data-youtube', o.youtube || ''); c.setAttribute('data-file', o.file || '');
      var emb = o.youtube ? embedUrl(o.youtube) : null, node;
      if (emb) {
        node = document.createElement('div'); node.className = 'vframe'; node.innerHTML = '<iframe allowfullscreen title="Vidéo"></iframe>'; node.firstChild.src = emb;
        c.className = 'vid real reveal'; c.style.removeProperty('--bg');
      } else if (o.file) {
        node = document.createElement('video'); node.controls = true; node.preload = 'metadata'; if (o.poster) node.poster = o.poster; node.innerHTML = '<source type="video/mp4">'; node.firstChild.src = o.file;
        c.className = 'vid real reveal'; c.style.removeProperty('--bg');
      } else {
        node = document.createElement('button'); node.setAttribute('aria-label', 'Lecture'); node.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        c.className = 'vid reveal'; c.style.setProperty('--bg', 'url(' + (o.bg || 'img/vendanges.jpg') + ')');
      }
      c.insertBefore(node, capP);
    }
  }

  /* la page affichée peut être plus ancienne que le contenu enregistré : on la remet à jour */
  function renderDoc(file, doc) {
    document.querySelectorAll('[data-e]').forEach(function (n) {
      var k = n.getAttribute('data-e').split('|'); if (k[0] !== file) return;
      var v = getPath(doc, k[1]); if (v == null) return;
      if (n.hasAttribute('data-multi')) {
        n.innerHTML = '';
        String(v).split('\n\n').forEach(function (t) { if (!t.trim()) return; var p = document.createElement('p'); p.textContent = t.trim(); n.appendChild(p); });
      } else if (n.hasAttribute('data-rich')) { n.innerHTML = richHtml(v); } else { n.textContent = v; }
    });
    document.querySelectorAll('[data-ei]').forEach(function (n) {
      var k = n.getAttribute('data-ei').split('|'); if (k[0] !== file) return;
      var v = getPath(doc, k[1]); if (v) setImg(n, v);
    });
    document.querySelectorAll('a[data-href]').forEach(function (a) {
      var k = a.getAttribute('data-href').split('|'); if (k[0] !== file) return;
      var v = getPath(doc, k[1]); if (v) a.setAttribute('href', v);
    });
    document.querySelectorAll('[data-list]').forEach(function (l) {
      var k = l.getAttribute('data-list').split('|'); if (k[0] !== file) return;
      var arr = getPath(doc, k[1]); if (!Array.isArray(arr) || !arr.length) return;
      var tpl = l.querySelector(':scope > [data-item]'); if (!tpl) return;
      var old = Array.prototype.slice.call(l.querySelectorAll(':scope > [data-item]'));
      var nodes = arr.map(function (o, i) { var c = tpl.cloneNode(true); c.dataset.oi = i; fillItem(c, o); return c; });
      old.forEach(function (x) { x.remove(); });
      nodes.forEach(function (c) { l.appendChild(c); });
    });
  }

  async function syncWithRepo() {
    var meta = document.querySelector('meta[name="cc-rev"]');
    try { rev = JSON.parse(meta ? meta.content : '{}'); } catch (e) { rev = {}; }
    try { pub = JSON.parse(localStorage.getItem('cc_pub') || '{}'); } catch (e) { pub = {}; }
    var token = await freshToken();
    var list = await gh(token, '/contents/content?ref=main');
    remote = {};
    list.forEach(function (f) { if (/\.json$/.test(f.name)) remote[f.name.replace(/\.json$/, '')] = f.sha; });
    var files = pageFiles();
    for (var i = 0; i < files.length; i++) {
      var f = files[i];
      if (remote[f] && rev[f] && remote[f] !== rev[f]) {
        var r = await gh(token, '/contents/content/' + f + '.json?ref=main');
        renderDoc(f, JSON.parse(b64dec(r.content)));
      }
    }
  }

  function begin() {
    document.body.classList.add('editing');
    document.head.appendChild(el('link', { rel: 'stylesheet', href: 'edit.css' }));
    syncWithRepo().catch(function (e) { console.error(e); }).then(start);
  }

  function updatePending() {
    var n = pendingFiles().length, b = document.querySelector('.cc-pub'), note = document.querySelector('.cc-pending');
    if (b) { b.hidden = !n; }
    if (note) { note.hidden = !n; }
  }

  function start() {
    var fl = document.getElementById('flash'), hd = document.getElementById('top');
    if (fl) { fl.classList.add('show'); if (hd) hd.style.top = fl.offsetHeight + 'px'; }

    makeEditable(document);
    setupLinks();
    document.querySelectorAll('[data-ei],[data-fi]').forEach(addImgBtn);
    document.querySelectorAll('[data-list]').forEach(setupList);
    document.querySelectorAll('a.tile').forEach(function (a) { a.removeAttribute('href'); });

    buildBar();
    updatePending();
    try { if (!sessionStorage.getItem('cc_help')) showHelp(); } catch (e) { showHelp(); }
  }

  /* ---------- textes ---------- */
  function makeEditable(root) {
    root.querySelectorAll('[data-e]:not([data-multi]),[data-fd]').forEach(function (n) { bindText(n, false); });
    root.querySelectorAll('[data-multi]').forEach(function (c) {
      c.querySelectorAll('p').forEach(function (p) { bindText(p, true); });
    });
  }

  function bindText(n, multi) {
    if (n.__b) return; n.__b = 1;
    n.contentEditable = 'true'; n.spellcheck = true; n.setAttribute('lang', 'fr');
    if (n.hasAttribute('data-e') && !multi) n.__o = n.hasAttribute('data-rich') ? richText(n) : txt(n);
    var rich = n.hasAttribute('data-rich');
    n.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (rich) { document.execCommand('insertLineBreak'); }
        else if (multi) {
          var p = document.createElement('p'); bindText(p, true);
          n.parentNode.insertBefore(p, n.nextSibling); p.focus();
        } else { n.blur(); }
      } else if (multi && e.key === 'Backspace' && !n.textContent && n.parentNode.querySelectorAll('p').length > 1) {
        e.preventDefault();
        var other = n.previousElementSibling || n.nextElementSibling; n.remove(); if (other) other.focus();
      }
    });
    n.addEventListener('paste', function (e) {
      e.preventDefault();
      var t = (e.clipboardData || window.clipboardData).getData('text');
      if (!multi && !rich) t = t.replace(/\s*\n\s*/g, ' ');
      document.execCommand('insertText', false, t);
    });
    n.addEventListener('input', function () {
      dirty = true;
      var k = n.getAttribute('data-e');
      if (k && !multi) {
        document.querySelectorAll('[data-e="' + k + '"]').forEach(function (o) { if (o !== n) { if (rich) o.innerHTML = n.innerHTML; else o.textContent = n.textContent; } });
      }
    });
  }

  /* ---------- photos ---------- */
  var fileInput = el('input', { type: 'file', accept: 'image/*' });
  fileInput.style.display = 'none';
  document.body.appendChild(fileInput);
  var target = null;
  fileInput.addEventListener('change', function () {
    var f = fileInput.files[0]; fileInput.value = '';
    if (f && target) handleFile(f, target);
  });
  function pick(t) { target = t; fileInput.click(); }

  function addImgBtn(t) {
    if (t.__btn) return; t.__btn = 1;
    var host = t.tagName === 'IMG' ? t.parentElement : t;
    var b = el('button', { type: 'button', 'class': 'cc-ctl cc-imgbtn' }, '📷 Changer la photo');
    b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); pick(t); });
    host.appendChild(b);
  }

  function handleFile(file, t) {
    status('Préparation de la photo…');
    var img = new Image(), url = URL.createObjectURL(file);
    img.onload = function () {
      var max = 1800, w = img.naturalWidth, h = img.naturalHeight, s = Math.min(1, max / Math.max(w, h));
      var c = document.createElement('canvas'); c.width = Math.round(w * s); c.height = Math.round(h * s);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      var data = c.toDataURL('image/jpeg', 0.82); URL.revokeObjectURL(url);
      var name = 'photo-' + Date.now() + '-' + Math.floor(Math.random() * 1000) + '.jpg';
      t._path = 'img/' + name; t._b64 = data.split(',')[1];
      if (t.tagName === 'IMG') { t.src = data; } else { t.style.setProperty('--bg', 'url(' + data + ')'); }
      dirty = true;
      status('Photo prête. N’oubliez pas de cliquer sur « Enregistrer ».', 'ok');
    };
    img.onerror = function () { URL.revokeObjectURL(url); status('Cette photo n’a pas pu être lue. Essayez-en une autre.', 'err'); };
    img.src = url;
  }

  /* ---------- listes (ajouter / supprimer une ligne) ---------- */
  function setupList(list) {
    var host = list.tagName === 'TBODY' ? list.closest('table') : list;
    var path = list.getAttribute('data-list');
    var label = /\|(tiles|cards)$/.test(path) ? '➕ Ajouter une photo' : (/events$/.test(path) ? '➕ Ajouter une date' : '➕ Ajouter une ligne');
    var bar = el('div', { 'class': 'cc-ctl cc-addbar' });
    var add = el('button', { type: 'button', 'class': 'cc-add' }, label);
    add.addEventListener('click', function (e) { e.preventDefault(); addItem(list); });
    bar.appendChild(add);
    host.insertAdjacentElement('afterend', bar);
    list.querySelectorAll(':scope > [data-item]').forEach(decorateItem);
  }

  function decorateItem(it) {
    if (it.__d) return; it.__d = 1;
    var grp = el('div', { 'class': 'cc-ctl cc-itembar' });
    function mk(cls, label, title, fn) {
      var b = el('button', { type: 'button', 'class': cls, title: title, 'aria-label': title }, label);
      b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); fn(); });
      grp.appendChild(b);
    }
    mk('cc-mv', '⬆', 'Monter', function () {
      var prev = it.previousElementSibling;
      while (prev && !prev.hasAttribute('data-item')) prev = prev.previousElementSibling;
      if (prev) { it.parentNode.insertBefore(it, prev); dirty = true; it.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
    });
    mk('cc-mv', '⬇', 'Descendre', function () {
      var next = it.nextElementSibling;
      while (next && !next.hasAttribute('data-item')) next = next.nextElementSibling;
      if (next) { it.parentNode.insertBefore(next, it); dirty = true; it.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
    });
    mk('cc-del', '✖ Supprimer', 'Supprimer', function () {
      if (it.parentNode.querySelectorAll(':scope > [data-item]').length < 2) { dialog({ title: 'Impossible de supprimer', text: 'Il doit rester au moins un élément dans cette liste.' }); return; }
      yesNo('Supprimer cet élément ?', 'Il disparaîtra du site après l’enregistrement.', 'Oui, supprimer', 'Non, le garder').then(function (ok) {
        if (ok) { it.remove(); dirty = true; status('Élément supprimé. N’oubliez pas de cliquer sur « Enregistrer ».', 'ok'); }
      });
    });
    if (it.tagName === 'TR') {
      var td = el('td', { 'class': 'cc-ctl cc-delcell' }); td.appendChild(grp); it.appendChild(td);
    } else { it.appendChild(grp); }
    if (it.classList.contains('tile')) addTagSelect(it);
    if (it.hasAttribute('data-youtube')) addVideoBtn(it);
  }

  function addTagSelect(it) {
    var s = el('select', { 'class': 'cc-ctl cc-tag', 'aria-label': 'Catégorie de la photo' });
    [['t', 'Travaux'], ['v', 'Vendanges'], ['f', 'Festivités'], ['c', 'Événements']].forEach(function (o) {
      var op = el('option', { value: o[0] }, o[1]); if (it.dataset.tag === o[0]) op.selected = true; s.appendChild(op);
    });
    s.addEventListener('click', function (e) { e.stopPropagation(); });
    s.addEventListener('change', function () {
      it.dataset.tag = s.value; it.dataset.cat = s.value;
      var l = it.querySelector('.tlabel'); if (l) l.textContent = s.options[s.selectedIndex].text;
      dirty = true;
    });
    it.appendChild(s);
  }

  function addItem(list) {
    var items = list.querySelectorAll(':scope > [data-item]');
    var src = items[items.length - 1];
    var c = src.cloneNode(true);
    c.querySelectorAll('.cc-ctl').forEach(function (x) { x.remove(); });
    c.querySelectorAll('[contenteditable]').forEach(function (x) { x.removeAttribute('contenteditable'); });
    c.querySelectorAll('[data-fd]').forEach(function (x) { x.textContent = x.getAttribute('data-fd') === 'caption' ? 'Nouvelle photo' : 'À compléter'; });
    c.dataset.oi = src.dataset.oi;
    if (c.hasAttribute('data-youtube')) {   // nouvelle vidéo : on repart d'un emplacement vide
      var cap = c.querySelector('[data-fd="caption"]');
      Array.prototype.slice.call(c.children).forEach(function (x) { if (x !== cap.parentNode) x.remove(); });
      var ph = document.createElement('button'); ph.setAttribute('aria-label', 'Lecture');
      ph.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
      c.insertBefore(ph, cap.parentNode);
      c.classList.remove('real'); c.style.setProperty('--bg', 'url(img/vendanges.jpg)');
      c.setAttribute('data-youtube', ''); c.setAttribute('data-file', ''); c.dataset.youtube = ''; c.dataset.file = '';
      cap.textContent = 'Nouvelle vidéo';
    }
    list.appendChild(c);
    makeEditable(c);
    c.querySelectorAll('[data-fi]').forEach(addImgBtn);
    decorateItem(c);
    dirty = true;
    c.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  /* ---------- liens modifiables ---------- */
  function setupLinks() {
    document.querySelectorAll('a[data-href]').forEach(function (a) {
      var b = el('button', { type: 'button', 'class': 'cc-ctl cc-linkbtn' }, '🔗 Changer ce lien');
      b.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        dialog({ title: 'Changer ce lien', text: 'Collez ici la nouvelle adresse (par exemple celle de votre page Facebook) :', input: a.getAttribute('href'),
          buttons: [{ label: 'Valider', value: true, primary: true }, { label: 'Annuler', value: null }] }).then(function (v) {
          if (v && v.trim()) {
            v = v.trim(); if (!/^(https?:|mailto:|tel:)/.test(v)) v = 'https://' + v;
            document.querySelectorAll('a[data-href="' + a.getAttribute('data-href') + '"]').forEach(function (x) { x.setAttribute('href', v); });
            dirty = true; status('Lien changé. N’oubliez pas de cliquer sur « Enregistrer ».', 'ok');
          }
        });
      });
      a.insertAdjacentElement('afterend', b);
    });
  }

  /* ---------- vidéos : lien YouTube / Vimeo / Facebook, ou petit fichier ---------- */
  function embedUrl(u) {
    var m = u.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:[^#]*&)?v=|shorts\/|embed\/|live\/))([\w-]{11})/);
    if (m) return 'https://www.youtube-nocookie.com/embed/' + m[1];
    m = u.match(/vimeo\.com\/(?:video\/)?(\d+)/);
    if (m) return 'https://player.vimeo.com/video/' + m[1];
    if (/facebook\.com|fb\.watch/.test(u)) return 'https://www.facebook.com/plugins/video.php?show_text=false&href=' + encodeURIComponent(u);
    return null;
  }
  function addVideoBtn(it) {
    var b = el('button', { type: 'button', 'class': 'cc-ctl cc-imgbtn cc-vidbtn' }, '🎬 Choisir la vidéo');
    b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); videoDialog(it); });
    it.appendChild(b);
  }
  function setVideoMedia(it, node) {
    var cap = it.querySelector('[data-fd="caption"]');
    Array.prototype.slice.call(it.children).forEach(function (c) {
      if (c !== cap.parentNode && !c.classList.contains('cc-ctl')) c.remove();
    });
    it.insertBefore(node, cap.parentNode);
    it.classList.add('real'); it.style.removeProperty('--bg');
  }
  function videoDialog(it) {
    var h = el('div', { 'class': 'cc-help' });
    h.innerHTML = '<div class="cc-help-card"><h2>Choisir la vidéo</h2>' +
      '<p>Le plus simple : mettez votre vidéo sur <b>YouTube</b> ou <b>Facebook</b>, puis collez ici son adresse.</p>' +
      '<button type="button" class="cc-big cc-v-link">🔗 Coller un lien (YouTube, Facebook, Vimeo)</button>' +
      '<button type="button" class="cc-big cc-v-file cc-alt">📁 Envoyer un fichier vidéo (4 Mo maximum)</button>' +
      '<button type="button" class="cc-link cc-v-cancel">Annuler</button></div>';
    document.body.appendChild(h);
    h.querySelector('.cc-v-cancel').onclick = function () { h.remove(); };
    h.querySelector('.cc-v-link').onclick = function () {
      h.remove();
      dialog({ title: 'Lien de la vidéo', text: 'Collez ici l’adresse de la vidéo (YouTube, Facebook ou Vimeo) :', input: '',
        buttons: [{ label: 'Valider', value: true, primary: true }, { label: 'Annuler', value: null }] }).then(function (v) {
        if (!v || !v.trim()) return;
        v = v.trim(); var emb = embedUrl(v);
        if (!emb) { dialog({ title: 'Adresse non reconnue', text: 'Utilisez un lien YouTube, Facebook ou Vimeo.' }); return; }
        var d = document.createElement('div'); d.className = 'vframe';
        d.innerHTML = '<iframe allowfullscreen title="Vidéo"></iframe>'; d.firstChild.src = emb;
        setVideoMedia(it, d);
        it.dataset.youtube = v; it.dataset.file = ''; it._vb64 = null; it._vpath = null;
        dirty = true; status('Vidéo choisie. N’oubliez pas de cliquer sur « Enregistrer ».', 'ok');
      });
    };
    h.querySelector('.cc-v-file').onclick = function () {
      var inp = el('input', { type: 'file', accept: 'video/mp4,video/webm,video/quicktime' });
      inp.addEventListener('change', function () {
        var f = inp.files[0]; if (!f) return;
        if (f.size > 4200000) { h.remove(); dialog({ title: 'Vidéo trop lourde', text: 'Cette vidéo pèse ' + (f.size / 1048576).toFixed(1).replace('.', ',') + ' Mo (maximum 4 Mo). Le plus simple : la mettre sur YouTube ou Facebook, puis coller son adresse.' }); return; }
        var r = new FileReader();
        r.onload = function () {
          var ext = /webm/.test(f.type) ? 'webm' : 'mp4';
          it._vpath = 'img/video-' + Date.now() + '.' + ext; it._vb64 = String(r.result).split(',')[1];
          var v = document.createElement('video'); v.controls = true; v.src = r.result;
          setVideoMedia(it, v);
          it.dataset.file = it._vpath; it.dataset.youtube = '';
          dirty = true; h.remove(); status('Vidéo prête. N’oubliez pas de cliquer sur « Enregistrer ».', 'ok');
        };
        r.readAsDataURL(f);
      });
      inp.click();
    };
  }

  /* ---------- clics : empêcher la navigation pendant l'édition ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t.closest || t.closest('.cc-bar,.cc-help')) return;
    var im = t.closest('img[data-ei],img[data-fi]');
    if (im) { e.preventDefault(); e.stopPropagation(); pick(im); return; }
    if (t.closest('.cc-ctl')) { if (t.closest('a')) e.preventDefault(); return; }
    var a = t.closest('a');
    if (a && (a.hasAttribute('data-href') || a.classList.contains('tile') || a.querySelector('[data-e],[data-fd],[data-fi],[data-ei]'))) {
      e.preventDefault();
      if (a.classList.contains('tile')) e.stopPropagation();
    }
  }, true);

  window.addEventListener('beforeunload', function (e) {
    if (dirty) { e.preventDefault(); e.returnValue = ''; }
  });

  /* ---------- barre du bas + aide ---------- */
  function buildBar() {
    var bar = el('div', { 'class': 'cc-bar' });
    bar.innerHTML =
      '<div class="cc-hint"><b>✏️ Mode modification</b><span>Cliquez sur un texte pour le changer, ou sur une photo pour la remplacer.</span></div>' +
      '<div class="cc-status" id="cc-status" role="status" aria-live="polite"></div>' +
      '<div class="cc-pending" hidden>⏳ Des changements enregistrés ne sont pas encore sur le site.</div>' +
      '<button type="button" class="cc-save">💾 Enregistrer</button>' +
      '<button type="button" class="cc-pub" hidden>🚀 Mettre en ligne</button>' +
      '<button type="button" class="cc-help-btn">❓ Aide</button>' +
      '<button type="button" class="cc-quit">Quitter</button>';
    document.body.appendChild(bar);
    statusEl = bar.querySelector('#cc-status');
    saveBtn = bar.querySelector('.cc-save');
    saveBtn.addEventListener('click', function () { save(); });
    bar.querySelector('.cc-pub').addEventListener('click', publishClick);
    bar.querySelector('.cc-help-btn').addEventListener('click', showHelp);
    bar.querySelector('.cc-quit').addEventListener('click', function () {
      var step2 = function () {
        dialog({ title: 'Quitter le mode modification', text: 'Voulez-vous aussi vous déconnecter ?', buttons: [
          { label: 'Oui, me déconnecter', value: 'out', primary: true }, { label: 'Non, rester connecté', value: 'stay' }] }).then(function (v) {
          dirty = false;
          try { sessionStorage.removeItem(EDIT); if (v === 'out') localStorage.removeItem(AUTH); } catch (e) {}
          location.reload();
        });
      };
      if (dirty) yesNo('Changements non enregistrés', 'Si vous quittez maintenant, vos changements seront perdus.', 'Quitter quand même', 'Revenir à mon travail').then(function (ok) { if (ok) step2(); });
      else step2();
    });
  }

  function showHelp() {
    try { sessionStorage.setItem('cc_help', '1'); } catch (e) {}
    var h = el('div', { 'class': 'cc-help' });
    h.innerHTML =
      '<div class="cc-help-card"><h2>Comment modifier votre site</h2><ol>' +
      '<li><b>Un texte ?</b> Cliquez dessus, puis écrivez. C’est tout.</li>' +
      '<li><b>Une photo ?</b> Cliquez sur la photo (ou sur « 📷 Changer la photo »), puis choisissez-en une sur votre appareil.</li>' +
      '<li><b>Ajouter, supprimer ou déplacer une ligne ?</b> Utilisez les boutons « ➕ Ajouter », « ✖ Supprimer » et les flèches ⬆ ⬇ qui apparaissent.</li>' +
      '<li><b>Un titre ?</b> Cliquez dessus et écrivez. Pour mettre un mot en italique doré, entourez-le d’étoiles : *comme ceci*.</li>' +
      '<li><b>Enregistrer ?</b> Cliquez sur le bouton vert <b>« 💾 Enregistrer »</b> en bas de l’écran : vos changements sont gardés, mais pas encore visibles sur le site.</li>' +
      '<li><b>Plusieurs pages ?</b> Enregistrez, puis allez sur une autre page du site (menu) et modifiez-la de la même façon.</li>' +
      '<li><b>Terminer ?</b> Cliquez sur le bouton orange <b>« 🚀 Mettre en ligne »</b> : tout apparaît sur le site 1 à 2 minutes plus tard, en une seule fois.</li>' +
      '</ol><p>Pour modifier une autre page, utilisez le menu du site comme d’habitude, puis enregistrez avant de changer de page.</p>' +
      '<button type="button" class="cc-big">J’ai compris</button></div>';
    h.querySelector('button').addEventListener('click', function () { h.remove(); });
    document.body.appendChild(h);
  }

  /* ---------- enregistrement (un seul « commit » via Git Gateway) ---------- */
  function ser(n) {
    var s = '';
    n.childNodes.forEach(function (c) {
      if (c.nodeType === 3) s += c.nodeValue;
      else if (c.nodeName === 'BR') s += '\n';
      else if (c.nodeName === 'EM' || c.nodeName === 'I') s += '*' + ser(c) + '*';
      else s += ser(c);
    });
    return s;
  }
  function richText(n) { return ser(n).replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').replace(/ *\n */g, '\n').trim(); }
  function txt(n) { return n.textContent.replace(/ /g, ' ').replace(/\s+/g, ' ').trim(); }
  function multiText(n) { return Array.prototype.map.call(n.querySelectorAll('p'), txt).filter(Boolean).join('\n\n'); }
  function getPath(o, p) { return p.split('.').reduce(function (a, k) { return a == null ? a : a[k]; }, o); }
  function setPath(o, p, v) { var k = p.split('.'), l = k.pop(); var t = k.reduce(function (a, x) { if (a[x] == null) a[x] = {}; return a[x]; }, o); t[l] = v; }
  function b64dec(s) {
    var bin = atob(s.replace(/\s/g, '')), u = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(u);
  }

  function freshToken() {
    if (auth.expires_at - Date.now() > 60000) return Promise.resolve(auth.access_token);
    return fetch(ID + '/token', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: auth.refresh_token })
    }).then(function (r) {
      if (!r.ok) throw new Error('session');
      return r.json();
    }).then(function (d) {
      auth = { access_token: d.access_token, refresh_token: d.refresh_token || auth.refresh_token, expires_at: Date.now() + (d.expires_in || 3600) * 1000, email: auth.email };
      localStorage.setItem(AUTH, JSON.stringify(auth));
      return auth.access_token;
    });
  }

  function gh(token, path, method, body) {
    return fetch(GIT + path, {
      method: method || 'GET',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      if (!r.ok) return r.text().then(function (t) { throw new Error('git ' + r.status + ' ' + path + ' ' + t.slice(0, 200)); });
      return r.json();
    });
  }

  async function save(opts) {
    opts = opts || {};
    var okSaved = false;
    if (saving) return false;
    saving = true; saveBtn.disabled = true;
    status('Enregistrement en cours… (ne fermez pas la page)');
    try {
      var token = await freshToken();

      var names = pageFiles(), docs = {}, orig = {};
      for (var i = 0; i < names.length; i++) {
        var r = await gh(token, '/contents/content/' + names[i] + '.json?ref=main');
        docs[names[i]] = JSON.parse(b64dec(r.content));
        orig[names[i]] = JSON.stringify(docs[names[i]]);
      }

      var imgs = {}, seen = {};
      document.querySelectorAll('[data-e]').forEach(function (n) {
        var k = n.getAttribute('data-e'); if (seen[k]) return; seen[k] = 1;
        var p = k.split('|');
        var val = n.hasAttribute('data-multi') ? multiText(n) : (n.hasAttribute('data-rich') ? richText(n) : txt(n));
        if (/^t\./.test(p[1]) && val === n.__o) return;   // titre/texte fixe non modifié : on ne l'enregistre pas
        setPath(docs[p[0]], p[1], val);
      });
      document.querySelectorAll('a[data-href]').forEach(function (a) {
        var p = a.getAttribute('data-href').split('|');
        setPath(docs[p[0]], p[1], a.getAttribute('href'));
      });
      document.querySelectorAll('[data-ei]').forEach(function (n) {
        if (!n._path) return;
        var p = n.getAttribute('data-ei').split('|');
        setPath(docs[p[0]], p[1], n._path);
        if (n._b64) imgs[n._path] = n._b64;
      });
      document.querySelectorAll('[data-list]').forEach(function (l) {
        var p = l.getAttribute('data-list').split('|');
        var base = getPath(docs[p[0]], p[1]) || [], arr = [];
        l.querySelectorAll(':scope > [data-item]').forEach(function (it) {
          var o = JSON.parse(JSON.stringify(base[+it.dataset.oi] || base[base.length - 1] || {}));
          it.querySelectorAll('[data-fd]').forEach(function (x) { o[x.getAttribute('data-fd')] = txt(x); });
          it.querySelectorAll('[data-fi]').forEach(function (x) {
            if (!x._path) return;
            o[x.getAttribute('data-fi')] = x._path;
            if (x._b64) imgs[x._path] = x._b64;
          });
          if (it.dataset.tag) o.tag = it.dataset.tag;
          if (it.hasAttribute('data-youtube')) {
            o.youtube = it.getAttribute('data-youtube') || '';
            if (it._vpath) { o.file = it._vpath; o.poster = ''; if (it._vb64) imgs[it._vpath] = it._vb64; }
            else if (!o.youtube && it.getAttribute('data-file')) o.file = it.getAttribute('data-file');
          }
          arr.push(o);
        });
        setPath(docs[p[0]], p[1], arr);
      });

      var changed = names.filter(function (f) { return JSON.stringify(docs[f]) !== orig[f]; });
      var imgPaths = Object.keys(imgs);
      if (!changed.length && !imgPaths.length) { status(pendingFiles().length ? 'Rien de nouveau à enregistrer. Cliquez sur « 🚀 Mettre en ligne » pour publier ce qui est déjà enregistré.' : 'Aucune modification à enregistrer.'); return true; }

      var ref = await gh(token, '/git/refs/heads/main');
      var head = ref.object.sha;
      var cm = await gh(token, '/git/commits/' + head);
      var tree = [];
      for (var a = 0; a < imgPaths.length; a++) {
        var bi = await gh(token, '/git/blobs', 'POST', { content: imgs[imgPaths[a]], encoding: 'base64' });
        tree.push({ path: imgPaths[a], mode: '100644', type: 'blob', sha: bi.sha });
      }
      for (var b = 0; b < changed.length; b++) {
        var bj = await gh(token, '/git/blobs', 'POST', { content: JSON.stringify(docs[changed[b]], null, 2) + '\n', encoding: 'utf-8' });
        remote[changed[b]] = bj.sha;
        tree.push({ path: 'content/' + changed[b] + '.json', mode: '100644', type: 'blob', sha: bj.sha });
      }
      var nt = await gh(token, '/git/trees', 'POST', { base_tree: cm.tree.sha, tree: tree });
      var nc = await gh(token, '/git/commits', 'POST', { message: 'Modification du site (enregistrée, pas encore en ligne) [skip ci]', tree: nt.sha, parents: [head] });
      await gh(token, '/git/refs/heads/main', 'PATCH', { sha: nc.sha });

      // les lignes ajoutées / supprimées ont maintenant leur place définitive
      document.querySelectorAll('[data-list]').forEach(function (l) {
        Array.prototype.forEach.call(l.querySelectorAll(':scope > [data-item]'), function (it, idx) { it.dataset.oi = idx; });
      });
      document.querySelectorAll('[data-ei],[data-fi],[data-item]').forEach(function (n) { n._b64 = null; n._vb64 = null; });
      dirty = false; okSaved = true;
      updatePending();
      status('✅ Enregistré. Pas encore en ligne : cliquez sur « 🚀 Mettre en ligne » quand vous avez fini.', 'ok');
    } catch (err) {
      console.error(err);
      if (err && err.message === 'session') status('Votre connexion a expiré. Quittez puis reconnectez-vous (vos changements ne sont pas enregistrés).', 'err');
      else status('L’enregistrement n’a pas fonctionné. Vos changements sont toujours sur cette page : réessayez dans un instant.', 'err');
    } finally {
      saving = false; saveBtn.disabled = false;
    }
    if (okSaved && !opts.silent && pendingFiles().length) {
      var go = await yesNo('Enregistré !', 'Vos modifications sont gardées. Voulez-vous les mettre en ligne maintenant, ou modifier une autre page d’abord ?', '🚀 Mettre en ligne maintenant', 'Modifier une autre page');
      if (go) await publish();
    }
    return okSaved;
  }

  /* mise en ligne : un seul « commit » sans [skip ci] = une seule publication pour toutes les pages enregistrées */
  async function publish() {
    if (saving) return;
    saving = true; saveBtn.disabled = true;
    status('Mise en ligne en cours…');
    try {
      var token = await freshToken();
      var ref = await gh(token, '/git/refs/heads/main');
      var head = ref.object.sha;
      var cm = await gh(token, '/git/commits/' + head);
      var nc = await gh(token, '/git/commits', 'POST', { message: 'Mise en ligne du site', tree: cm.tree.sha, parents: [head] });
      await gh(token, '/git/refs/heads/main', 'PATCH', { sha: nc.sha });
      pub = JSON.parse(JSON.stringify(remote));
      try { localStorage.setItem('cc_pub', JSON.stringify(pub)); } catch (e) {}
      updatePending();
      status('🚀 Mise en ligne lancée ! Le site sera à jour dans 1 à 2 minutes.', 'ok');
    } catch (err) {
      console.error(err);
      status(err && err.message === 'session' ? 'Votre connexion a expiré. Quittez puis reconnectez-vous.' : 'La mise en ligne n’a pas fonctionné. Réessayez dans un instant.', 'err');
    } finally {
      saving = false; saveBtn.disabled = false;
    }
  }

  async function publishClick() {
    if (saving) return;
    if (dirty) { var ok = await save({ silent: true }); if (!ok || dirty) return; }
    if (!pendingFiles().length) { status('Tout est déjà en ligne.'); return; }
    var go = await yesNo('Mettre en ligne ?', 'Toutes les modifications enregistrées vont apparaître sur le site dans 1 à 2 minutes.', 'Oui, mettre en ligne', 'Pas maintenant');
    if (go) await publish();
  }

  begin();
})();
