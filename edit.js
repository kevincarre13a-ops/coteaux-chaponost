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

  var dirty = false, saving = false;
  var statusEl, saveBtn;

  function status(msg, kind) {
    if (!statusEl) return;
    statusEl.textContent = msg || '';
    statusEl.className = 'cc-status' + (kind ? ' ' + kind : '');
  }

  function start() {
    document.body.classList.add('editing');
    document.head.appendChild(el('link', { rel: 'stylesheet', href: 'edit.css' }));

    var fl = document.getElementById('flash'), hd = document.getElementById('top');
    if (fl) { fl.classList.add('show'); if (hd) hd.style.top = fl.offsetHeight + 'px'; }

    makeEditable(document);
    document.querySelectorAll('[data-ei],[data-fi]').forEach(addImgBtn);
    document.querySelectorAll('[data-list]').forEach(setupList);
    document.querySelectorAll('a.tile').forEach(function (a) { a.removeAttribute('href'); });

    buildBar();
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
    n.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (multi) {
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
      if (!multi) t = t.replace(/\s*\n\s*/g, ' ');
      document.execCommand('insertText', false, t);
    });
    n.addEventListener('input', function () {
      dirty = true;
      var k = n.getAttribute('data-e');
      if (k && !multi) {
        document.querySelectorAll('[data-e="' + k + '"]').forEach(function (o) { if (o !== n) o.textContent = n.textContent; });
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
    var b = el('button', { type: 'button', 'class': 'cc-ctl cc-del' }, '✖ Supprimer');
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      if (it.parentNode.querySelectorAll(':scope > [data-item]').length < 2) { alert('Il doit rester au moins un élément.'); return; }
      if (confirm('Supprimer cet élément ?')) { it.remove(); dirty = true; }
    });
    if (it.tagName === 'TR') {
      var td = el('td', { 'class': 'cc-ctl cc-delcell' }); td.appendChild(b); it.appendChild(td);
    } else { it.appendChild(b); }
    if (it.classList.contains('tile')) addTagSelect(it);
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
    list.appendChild(c);
    makeEditable(c);
    c.querySelectorAll('[data-fi]').forEach(addImgBtn);
    decorateItem(c);
    dirty = true;
    c.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  /* ---------- clics : empêcher la navigation pendant l'édition ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t.closest || t.closest('.cc-bar,.cc-help')) return;
    var im = t.closest('img[data-ei],img[data-fi]');
    if (im) { e.preventDefault(); e.stopPropagation(); pick(im); return; }
    if (t.closest('.cc-ctl')) { if (t.closest('a')) e.preventDefault(); return; }
    var a = t.closest('a');
    if (a && (a.classList.contains('tile') || a.querySelector('[data-e],[data-fd],[data-fi],[data-ei]'))) {
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
      '<button type="button" class="cc-save">💾 Enregistrer</button>' +
      '<button type="button" class="cc-help-btn">❓ Aide</button>' +
      '<button type="button" class="cc-quit">Quitter</button>';
    document.body.appendChild(bar);
    statusEl = bar.querySelector('#cc-status');
    saveBtn = bar.querySelector('.cc-save');
    saveBtn.addEventListener('click', save);
    bar.querySelector('.cc-help-btn').addEventListener('click', showHelp);
    bar.querySelector('.cc-quit').addEventListener('click', function () {
      if (dirty && !confirm('Vous avez des changements non enregistrés. Quitter quand même ?')) return;
      dirty = false;
      var out = confirm('Voulez-vous aussi vous déconnecter ?\n\nOK = me déconnecter\nAnnuler = rester connecté (le bouton « Modifier le site » restera disponible)');
      try { sessionStorage.removeItem(EDIT); if (out) localStorage.removeItem(AUTH); } catch (e) {}
      location.reload();
    });
  }

  function showHelp() {
    try { sessionStorage.setItem('cc_help', '1'); } catch (e) {}
    var h = el('div', { 'class': 'cc-help' });
    h.innerHTML =
      '<div class="cc-help-card"><h2>Comment modifier votre site</h2><ol>' +
      '<li><b>Un texte ?</b> Cliquez dessus, puis écrivez. C’est tout.</li>' +
      '<li><b>Une photo ?</b> Cliquez sur la photo (ou sur « 📷 Changer la photo »), puis choisissez-en une sur votre appareil.</li>' +
      '<li><b>Ajouter ou supprimer une ligne ?</b> Utilisez les boutons « ➕ Ajouter » et « ✖ Supprimer » qui apparaissent.</li>' +
      '<li><b>Terminer ?</b> Cliquez sur le gros bouton vert <b>« 💾 Enregistrer »</b> en bas de l’écran. Les changements apparaissent sur le site 1 à 2 minutes plus tard.</li>' +
      '</ol><p>Pour modifier une autre page, utilisez le menu du site comme d’habitude, puis enregistrez avant de changer de page.</p>' +
      '<button type="button" class="cc-big">J’ai compris</button></div>';
    h.querySelector('button').addEventListener('click', function () { h.remove(); });
    document.body.appendChild(h);
  }

  /* ---------- enregistrement (un seul « commit » via Git Gateway) ---------- */
  function txt(n) { return n.textContent.replace(/ /g, ' ').replace(/\s+/g, ' ').trim(); }
  function multiText(n) { return Array.prototype.map.call(n.querySelectorAll('p'), txt).filter(Boolean).join('\n\n'); }
  function getPath(o, p) { return p.split('.').reduce(function (a, k) { return a == null ? a : a[k]; }, o); }
  function setPath(o, p, v) { var k = p.split('.'), l = k.pop(); var t = k.reduce(function (a, x) { return a[x]; }, o); t[l] = v; }
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

  async function save() {
    if (saving) return;
    saving = true; saveBtn.disabled = true;
    status('Enregistrement en cours… (ne fermez pas la page)');
    try {
      var token = await freshToken();

      var files = {};
      function need(k) { files[k.split('|')[0]] = 1; }
      document.querySelectorAll('[data-e]').forEach(function (n) { need(n.getAttribute('data-e')); });
      document.querySelectorAll('[data-list]').forEach(function (n) { need(n.getAttribute('data-list')); });
      document.querySelectorAll('[data-ei]').forEach(function (n) { need(n.getAttribute('data-ei')); });
      var names = Object.keys(files), docs = {}, orig = {};
      for (var i = 0; i < names.length; i++) {
        var r = await gh(token, '/contents/content/' + names[i] + '.json?ref=main');
        docs[names[i]] = JSON.parse(b64dec(r.content));
        orig[names[i]] = JSON.stringify(docs[names[i]]);
      }

      var imgs = {}, seen = {};
      document.querySelectorAll('[data-e]').forEach(function (n) {
        var k = n.getAttribute('data-e'); if (seen[k]) return; seen[k] = 1;
        var p = k.split('|');
        setPath(docs[p[0]], p[1], n.hasAttribute('data-multi') ? multiText(n) : txt(n));
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
          arr.push(o);
        });
        setPath(docs[p[0]], p[1], arr);
      });

      var changed = names.filter(function (f) { return JSON.stringify(docs[f]) !== orig[f]; });
      var imgPaths = Object.keys(imgs);
      if (!changed.length && !imgPaths.length) { status('Aucune modification à enregistrer.'); return; }

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
        tree.push({ path: 'content/' + changed[b] + '.json', mode: '100644', type: 'blob', sha: bj.sha });
      }
      var nt = await gh(token, '/git/trees', 'POST', { base_tree: cm.tree.sha, tree: tree });
      var nc = await gh(token, '/git/commits', 'POST', { message: 'Modification du site (espace de modification)', tree: nt.sha, parents: [head] });
      await gh(token, '/git/refs/heads/main', 'PATCH', { sha: nc.sha });

      // les lignes ajoutées / supprimées ont maintenant leur place définitive
      document.querySelectorAll('[data-list]').forEach(function (l) {
        Array.prototype.forEach.call(l.querySelectorAll(':scope > [data-item]'), function (it, idx) { it.dataset.oi = idx; });
      });
      document.querySelectorAll('[data-ei],[data-fi]').forEach(function (n) { n._b64 = null; });
      dirty = false;
      status('✅ Enregistré ! Vos modifications seront visibles sur le site dans 1 à 2 minutes.', 'ok');
    } catch (err) {
      console.error(err);
      if (err && err.message === 'session') status('Votre connexion a expiré. Quittez puis reconnectez-vous (vos changements ne sont pas enregistrés).', 'err');
      else status('L’enregistrement n’a pas fonctionné. Vos changements sont toujours sur cette page : réessayez dans un instant.', 'err');
    } finally {
      saving = false; saveBtn.disabled = false;
    }
  }

  start();
})();
