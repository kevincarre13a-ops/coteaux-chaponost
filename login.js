(function () {
  var KEY = 'cc_auth';
  var $ = function (id) { return document.getElementById(id); };
  function getAuth() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return null; } }
  function enter() { try { sessionStorage.setItem('cc_edit', '1'); } catch (e) {} location.href = '../index.html'; }

  if (getAuth()) { $('cc-form').hidden = true; $('cc-already').hidden = false; }
  $('cc-enter').onclick = enter;
  $('cc-logout').onclick = function () {
    try { localStorage.removeItem(KEY); sessionStorage.removeItem('cc_edit'); } catch (e) {}
    location.reload();
  };

  $('cc-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('cc-msg'), btn = $('cc-go');
    msg.textContent = ''; btn.disabled = true; btn.textContent = 'Connexion…';
    var email = $('cc-email').value.trim();
    var body = new URLSearchParams({ grant_type: 'password', username: email, password: $('cc-pass').value });
    fetch('/.netlify/identity/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (x) {
        if (!x.ok || !x.d.access_token) throw new Error('bad');
        localStorage.setItem(KEY, JSON.stringify({
          access_token: x.d.access_token, refresh_token: x.d.refresh_token,
          expires_at: Date.now() + (x.d.expires_in || 3600) * 1000, email: email
        }));
        enter();
      })
      .catch(function () {
        msg.textContent = 'Adresse email ou mot de passe incorrect. Vérifiez et réessayez.';
        btn.disabled = false; btn.textContent = 'Se connecter';
      });
  });
})();
