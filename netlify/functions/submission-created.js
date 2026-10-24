// Netlify lance cette fonction à chaque envoi de formulaire : on transmet le message par email via Resend.
const TO = "lescoteauxdechaponost@laposte.net";
const FROM = "Site Les Coteaux de Chaponost <contact@lescoteauxdechaponost.com>";

const esc = (s) => String(s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

exports.handler = async (event) => {
  const { payload } = JSON.parse(event.body);
  if (payload.form_name !== "contact") return { statusCode: 200, body: "ignoré" };
  const key = process.env.RESEND_API_KEY;
  if (!key) return { statusCode: 500, body: "RESEND_API_KEY manquante" };

  const d = payload.data || {};
  const sujet = (d.sujet || "Nouveau message").toString().slice(0, 120);
  const html = `<p><b>Nom :</b> ${esc(d.nom)}<br><b>Email :</b> ${esc(d.email)}<br><b>Sujet :</b> ${esc(d.sujet)}</p>
<p style="white-space:pre-wrap">${esc(d.message)}</p>
<p style="color:#888;font-size:12px">Message reçu via le formulaire de contact du site lescoteauxdechaponost.com.<br>Pour répondre, utilisez simplement « Répondre » : la réponse ira au visiteur.</p>`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: FROM, to: [TO], reply_to: d.email || undefined, subject: `[Site] ${sujet}`, html }),
  });
  if (!r.ok) return { statusCode: 502, body: await r.text() };
  return { statusCode: 200, body: "envoyé" };
};
