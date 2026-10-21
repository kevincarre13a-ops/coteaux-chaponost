#!/usr/bin/env python3
"""Génère le site Les Coteaux de Chaponost (pages statiques) à partir des fichiers content/*.json."""
import os, json
OUT = os.path.dirname(os.path.abspath(__file__))
CDIR = os.path.join(OUT, "content")

def load(name):
    with open(os.path.join(CDIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)

SITE = load("site")

NAV = [("index.html", "Accueil"), ("association.html", "Association"), ("la-vigne.html", "La vigne"),
       ("cerisaie.html", "La Cerisaie"), ("agenda.html", "Agenda"), ("evenements.html", "Événements"),
       ("galerie.html", "Galerie"), ("contact.html", "Contact")]

OLD_PAGES = ["nos-vins.html", "rejoindre.html"]  # fusionnées / supprimées dans la v3

LOGO = '''<img class="logo" src="img/vendangeur.png" alt="" width="22" height="40">'''

def paras(text):
    return "".join(f"<p>{p.strip()}</p>" for p in (text or "").split("\n\n") if p.strip())

def head(title, desc, page):
    nav = "".join(f'<a href="{h}"{" class=on" if h==page else ""}>{t}</a>' for h, t in NAV)
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Les Coteaux de Chaponost</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Caveat:wght@500;700&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css"></head><body>
<header class="top" id="top"><a class="brand" href="index.html">{LOGO}<span><b>Les Coteaux</b><i>de Chaponost</i></span></a>
<nav class="navdesktop">{nav}</nav>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</header>
<nav id="nav" class="navmobile">{nav}</nav>
<main>'''

FOOT = f'''</main><footer><div class="fwrap"><div><a class="brand light" href="index.html">{LOGO}<span><b>Les Coteaux</b><i>de Chaponost</i></span></a>
<p>La dernière vigne du village, cultivée par 130 bénévoles.<br>Association loi 1901 · Chaponost (69630)</p></div>
<div><h4>Le site</h4>{"".join(f'<a href="{h}">{t}</a>' for h,t in NAV)}</div>
<div><h4>Liens</h4><a href="https://www.chaponost.fr" target="_blank" rel="noopener">Mairie de Chaponost</a>
<a href="https://www.coteaux-du-lyonnais.com" target="_blank" rel="noopener">Coteaux du Lyonnais</a><a href="mentions-legales.html">Mentions légales</a></div>
<div><h4>Nous écrire</h4><p>{SITE["address_line1"]}<br>{SITE["address_line2"]}<br>{SITE["address_line3"]}</p><p><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><br><a href="tel:{SITE["phone_tel"]}">{SITE["phone"]}</a></p><p><a href="{SITE["facebook_url"]}" target="_blank" rel="noopener">Suivez-nous sur Facebook →</a></p></div></div>
<p class="legal">L'abus d'alcool est dangereux pour la santé, à consommer avec modération. · Maquette de démonstration réalisée par AssoVisible.</p></footer>
<script src="app.js"></script></body></html>'''

def hero(img, kicker, h1, sub, cls=""):
    return f'''<section class="hero {cls}" style="--bg:url({img})"><div class="hero-in"><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="sub">{sub}</p></div><span class="scroll">Défiler</span></section>'''

def band(img, quote, who=""):
    return f'<section class="band" style="--bg:url({img})"><blockquote>{quote}<cite>{who}</cite></blockquote></section>'

def title(kicker, h2, intro=""):
    return f'<div class="title reveal"><p class="kicker">{kicker}</p><h2>{h2}</h2>{"<p class=intro>"+intro+"</p>" if intro else ""}</div>'

def seegalerie(tag):
    return f'<p class="note reveal seelink"><a href="galerie.html#{tag}">Voir en images dans la galerie →</a></p>'

FLASH = f'''<div id="flash" class="flash"><p>📅 N'oubliez pas <b>{SITE["flash_event"]}</b> le <b>{SITE["flash_date"]}</b>. <a href="agenda.html">Voir l'agenda →</a></p><button class="flash-x" aria-label="Fermer">×</button></div>'''

pages = {}

# ---------- ACCUEIL
c = load("index")
pages["index.html"] = (head("Accueil", c["meta_desc"], "index.html") +
FLASH +
hero(c["hero_image"], c["hero_kicker"], "Les Coteaux<br><em>de Chaponost</em>", c["hero_sub"], "bright") +
f'''<section class="wrap welcome reveal"><p class="kicker">Mot de bienvenue</p><p class="lead">{c["welcome_text"]}</p></section>
<section class="wrap chiffres reveal"><div><b data-n="130">130</b><span>adhérents bénévoles</span></div><div><b data-n="400">400</b><span>bouteilles par an</span></div><div><b>2</b><span>vins, blanc &amp; rouge</span></div><div><b>1</b><span>dernière vigne du village</span></div></section>
<section class="next wrap reveal"><div class="label"><span class="tag">À ne pas manquer</span><p class="hand">Prochain rendez-vous</p><p>{c["next_text"]}</p></div>
<a class="btn" href="agenda.html">Voir tout l'agenda</a></section>
<section class="wrap shortcuts">''' + title("Le site en un coup d'œil", "Découvrir les Coteaux") + '''<div class="cards shortcuts-grid">
<a class="card reveal" href="association.html"><i>01</i><h3>L'association</h3><p>Histoire, bureau, vie associative.</p></a>
<a class="card reveal" href="la-vigne.html"><i>02</i><h3>La vigne</h3><p>Parcelle, cépages, travaux, nos vins.</p></a>
<a class="card reveal" href="cerisaie.html"><i>03</i><h3>La Cerisaie</h3><p>Le verger et les confitures maison.</p></a>
<a class="card reveal" href="agenda.html"><i>04</i><h3>Agenda</h3><p>Toutes les dates à venir.</p></a>
<a class="card reveal" href="evenements.html"><i>05</i><h3>Événements</h3><p>Nos rendez-vous en photos.</p></a>
<a class="card reveal" href="galerie.html"><i>06</i><h3>Galerie</h3><p>Photos &amp; vidéos de la vigne.</p></a></div></section>
<section class="wrap split">''' + f'''<div class="reveal"><p class="kicker">Notre histoire</p><h2>Une vigne sauvée<br>par ceux qui l'aiment</h2>
{paras(c["history_text"])}<a class="btn" href="association.html">Découvrir l'association</a></div>
<figure class="reveal"><img src="{c["history_image"]}" alt="Adhérents réunis autour d'un repas" loading="lazy"><figcaption>La vie de l'association</figcaption></figure></section>
<section class="cta"><h2>Une question, une envie de nous rejoindre ?</h2><p>{c["cta_text"]}</p><a class="btn light" href="contact.html">Nous écrire</a></section>''' + FOOT)

# ---------- ASSOCIATION
c = load("association")
org_items = "".join(f'<li class="evt"><span class="m">{o["date"]}</span><div><h4>{o["title"]}</h4><p>{o["text"]}</p></div></li>' for o in c["org_items"])
press_items = "".join(f'<div class="card"><i>—</i><h3>{p["title"]}</h3><p>{p["text"]}</p></div>' for p in c["press_items"])
pages["association.html"] = (head("L'association", c["meta_desc"], "association.html") +
hero(c["hero_image"], "L'association", "Sauvegarder la<br><em>dernière vigne</em>", "Un patrimoine viticole préservé par des bénévoles passionnés.", "short") +
'<section class="wrap">' + title("Historique", "Une vigne, une histoire") +
f'''<div class="split"><div class="reveal">{paras(c["history_text"])}
<p><small><i>{c["history_note"]}</i></small></p></div>
<figure class="reveal"><img src="{c["history_image"]}" alt="Trois adhérents taillent la vigne" loading="lazy"><figcaption>Taille de printemps</figcaption></figure></div></section>''' +
band("img/caisses.jpg", "130 adhérents, des retraités aux plus jeunes : la vigne se cultive à plusieurs mains.") +
f'<section class="wrap word reveal"><div class="paper"><p class="hand big">Le mot du Bureau</p><p>{c["word_text"]}</p><p class="sign">— {c["word_signature"]}<br><small><i>texte de démonstration, à valider par l\'association</i></small></p></div></section>' +
'<section class="wrap">' + title("Composition", "Bureau, Conseil d'administration &amp; commissions", "Composition à faire valider par l'association — tous les champs ci-dessous sont des exemples à remplacer.") +
f'''<div class="fiche reveal"><div><span>Président(e)</span><b>{c["president"]}</b></div><div><span>Vice-président(e)</span><b>{c["vice_president"]}</b></div><div><span>Trésorier(ère)</span><b>{c["treasurer"]}</b></div><div><span>Secrétaire</span><b>{c["secretary"]}</b></div><div><span>Membres du CA</span><b>{c["board_members"]}</b></div><div><span>Commissions</span><b>{c["commissions"]}</b></div></div></section>
<section class="wrap">''' + title("Organisation", "Le rythme de l'année associative") +
f'<ul class="tl reveal" style="max-width:760px;margin:2rem auto 0">{org_items}</ul></section>' +
'<section class="wrap">' + title("Presse", "On parle de nous", "Aucun article n'a été retrouvé à ce jour : les parutions presse (Le Progrès, Le Pays, bulletin municipal…) pourront être ajoutées ici au fur et à mesure.") +
f'<div class="cards reveal">{press_items}</div></section>' + FOOT)

# ---------- LA VIGNE (fusion vigne + vins)
def bouteille(nom, cls, cepage, desc):
    return f'''<article class="vin {cls} reveal"><div class="etiq"><svg viewBox="0 0 60 150" class="btl"><path d="M24 4h12v26c0 8 14 14 14 34v76c0 4-3 6-6 6H16c-3 0-6-2-6-6V64c0-20 14-26 14-34z" fill="currentColor"/><rect x="14" y="78" width="32" height="40" rx="2" fill="#f3ead7"/><text x="30" y="96" text-anchor="middle" font-size="6" font-family="serif" fill="#5b1424">LES COTEAUX</text><text x="30" y="105" text-anchor="middle" font-size="5" font-family="serif" fill="#5b1424">de Chaponost</text><text x="30" y="113" text-anchor="middle" font-size="4" font-family="serif" fill="#7a5230">Coteaux du Lyonnais</text></svg></div>
<div><h3>{nom}</h3><p>{desc}</p><dl><dt>Millésime</dt><dd>à compléter</dd><dt>Cépage</dt><dd>{cepage}</dd><dt>Volume</dt><dd>à compléter</dd><dt>Notes de dégustation</dt><dd>à compléter</dd></dl></div></article>'''

c = load("la-vigne")
steps = "".join(f'<li class="reveal"><b>{s["title"]}</b><span>{s["text"]}</span></li>' for s in c["steps"])
millesimes_rows = "".join(f'<tr><td>{m["year"]}</td><td>{m["blanc"]}</td><td>{m["rouge"]}</td><td>{m["remarks"]}</td></tr>' for m in c["millesimes"])
pages["la-vigne.html"] = (head("La vigne", c["meta_desc"], "la-vigne.html") +
hero(c["hero_image"], "Notre parcelle", "La <em>dernière vigne</em><br>du village", "Un coteau, des rangs de ceps, et des mains qui savent.", "short") +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Le terroir</p><h2>Les Coteaux du Lyonnais</h2>
{paras(c["terroir_text"])}</div>
<figure class="reveal"><img src="{c["terroir_image"]}" alt="La parcelle sous la neige" loading="lazy"><figcaption>La parcelle en hiver</figcaption></figure></section>
<section class="wrap">''' + title("Notre parcelle", "Fiche d'identité", "Les éléments ci-dessous sont modulables : l'association peut les compléter.") +
f'''<div class="fiche reveal"><div><span>Localisation</span><b>{c["loc_location"]}</b></div><div><span>Surface</span><b>{c["loc_surface"]}</b></div><div><span>Exposition</span><b>{c["loc_exposition"]}</b></div><div><span>Année de plantation</span><b>{c["loc_plantation_year"]}</b></div><div><span>Appellation</span><b>{c["loc_appellation"]}</b></div><div><span>Production</span><b>{c["loc_production"]}</b></div></div></section>
<section class="wrap">''' + title("Où se trouve la vigne", c["loc_location"]) +
f'''<div class="duo mapshots reveal"><figure><img src="{c["loc_sat_image"]}" alt="Vue satellite de la parcelle"><figcaption>Vue satellite — la parcelle est indiquée par la flèche</figcaption></figure>
<figure><img src="{c["loc_plan_image"]}" alt="Plan de situation de la parcelle"><figcaption>Plan de situation</figcaption></figure></div>
<p class="note reveal seelink"><a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query={c["loc_location"].replace(" ","+").replace(",","%2C").replace("'","%27")}">Ouvrir le plan interactif →</a></p></section>
<section class="wrap">''' + title("Les cépages", "Présentation des cépages") +
f'''<div class="duo"><div class="grape white reveal"><h3>Vin blanc</h3><p>{c["white_text"]}</p></div><div class="grape red reveal"><h3>Vin rouge</h3><p>{c["red_text"]}</p></div></div></section>''' +
band(c["band_image"], c["band_text"]) +
'<section class="wrap">' + title("Travaux de la vigne", "Les gestes de l'année", "Dates et saisonnalité données à titre indicatif ; à ajuster avec l'association.") +
f'''<ol class="steps">{steps}</ol>
<div class="split" style="margin-top:2.4rem"><figure class="reveal"><img src="{c["step_image1"]}" alt="Taille de la vigne" loading="lazy"><figcaption>Taille</figcaption></figure><figure class="reveal"><img src="{c["step_image2"]}" alt="Le pressoir" loading="lazy"><figcaption>Pressage</figcaption></figure></div>
{seegalerie("t")}</section>
<section class="wrap">''' + title("Notre vigneron partenaire", "Un professionnel à nos côtés", "L'association est accompagnée par un vigneron partenaire pour le conseil technique et la vinification. Présentation à fournir par l'association.") +
f'''<div class="paper reveal" style="max-width:760px;margin:2rem auto 0"><p><b>Nom du vigneron / domaine</b> : {c["vigneron_name"]}<br><b>Rôle auprès de l'association</b> : {c["vigneron_role"]}<br><b>Présentation</b> : {c["vigneron_text"]}</p></div></section>
<section class="wrap">''' + title("Production confidentielle", "Nos vins — 400 bouteilles en moyenne par an", "Notre production est limitée et réservée en priorité aux adhérents. Chaque millésime a son histoire, racontée ci-dessous.") +
'<div class="vins">' + bouteille("Blanc des Coteaux", "blanc", c["bottle_white_cepage"], c["bottle_white_desc"]) + bouteille("Rouge des Coteaux", "rouge", c["bottle_red_cepage"], c["bottle_red_desc"]) + '</div>' +
f'''<div class="tablewrap reveal"><table><thead><tr><th>Millésime</th><th>Blanc</th><th>Rouge</th><th>Remarques</th></tr></thead><tbody>{millesimes_rows}</tbody></table></div>
<p class="note reveal">Pour réserver des bouteilles, <a href="contact.html">contactez l'association</a>.</p></section>''' + FOOT)

# ---------- LA CERISAIE
c = load("cerisaie")
pages["cerisaie.html"] = (head("La Cerisaie", c["meta_desc"], "cerisaie.html") +
hero(c["hero_image"], "Le verger", "La <em>Cerisaie</em>", "Nos cerisiers, et les confitures qui en naissent.", "short") +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Le verger</p><h2>Un verger de cerisiers</h2>
<p>{c["intro_text"]}</p>
<p><small><i>{c["intro_note"]}</i></small></p></div>
<figure class="reveal"><img src="{c["intro_image"]}" alt="Cerises du verger" loading="lazy"><figcaption>Cerises du verger</figcaption></figure></section>
<section class="wrap">''' + title("La confiture maison", "Préparée en commun, vendue par l'association") +
f'''<div class="split"><figure class="reveal"><img src="{c["confiture_image"]}" alt="Préparation de la confiture de cerises en commun" loading="lazy"><figcaption>Préparation des confitures</figcaption></figure>
<div class="reveal paper cotis"><p class="hand big">Vente de confiture</p><p><b>Prix du pot</b> : {c["price"]}<br><b>Points de vente</b> : {c["points_de_vente"]}<br><b>Période de vente</b> : {c["periode"]}</p><p>Pour réserver des pots ou en savoir plus, <a href="contact.html">contactez l'association</a>.</p></div></div>
''' + seegalerie("f") + '</section>' + FOOT)

# ---------- AGENDA
c = load("agenda")
romans = ["I", "II", "III", "IV", "V", "VI"]
groups_html = ""
for i, g in enumerate(c["groups"]):
    events = "".join(f'<li class="evt reveal"><span class="m">{e["date"]}</span><div><h4>{e["title"]}</h4><p>{e["text"]}</p></div></li>' for e in g["events"])
    groups_html += f'<div id="{g["anchor"]}" class="axe"><h2><i>{romans[i]}</i> {g["heading"]}</h2><ul class="tl">{events}</ul></div>'
pages["agenda.html"] = (head("Agenda", c["meta_desc"], "agenda.html") +
hero(c["hero_image"], "Au fil de l'année", "L'<em>agenda</em>", "Toutes les dates à venir, en un seul endroit.", "short") +
f'<section class="wrap"><p class="note reveal">{c["note_text"]}</p>{groups_html}</section>' + FOOT)

# ---------- EVENEMENTS
c = load("evenements")
evcards = "".join(f'<article class="evcard reveal"><img src="{e["image"]}" alt="{e["title"]}" loading="lazy"><div><h3>{e["title"]}</h3><p>{e["text"]}</p><a href="galerie.html#{e["tag"]}">Voir en photos →</a></div></article>' for e in c["cards"])
pages["evenements.html"] = (head("Événements", c["meta_desc"], "evenements.html") +
hero(c["hero_image"], "Nos rendez-vous", "<em>Événements</em>", "Les moments qui rassemblent les 130 adhérents.", "short") +
'<section class="wrap">' + title("Au fil de l'année", "Nos grands rendez-vous") +
f'<div class="evcards">{evcards}</div>' + seegalerie("c") + '</section>' + FOOT)

# ---------- GALERIE
c = load("galerie")
TAGLABEL = {"v": "Vendanges", "t": "Travaux", "f": "Festivités", "c": "Événements"}
tiles = "".join(f'<a class="tile reveal" href="{t["image"]}" data-cat="{t["tag"]}" data-cap="{t["caption"]}"><img src="{t["image"]}" alt="{t["caption"]}" loading="lazy"><span>{TAGLABEL[t["tag"]]}</span></a>' for t in c["tiles"])
pages["galerie.html"] = (head("Galerie photos & vidéos", c["meta_desc"], "galerie.html") +
hero(c["hero_image"], "Photos & vidéos", "La vigne <em>en images</em>", "Travaux, vendanges, festivités, événements.", "short") +
f'''<section class="wrap"><p class="note reveal">{c["note_text"]}</p>
<div class="filters reveal"><button class="on" data-f="all">Tout</button><button data-f="t">Travaux</button><button data-f="v">Vendanges</button><button data-f="f">Festivités</button><button data-f="c">Événements</button><button class="vidbtn" data-f="vid">▶ Vidéos</button></div>
<div class="grid">''' + tiles + '''</div></section>
<section class="wrap">''' + title("Vidéos", "Les vignes en mouvement", c["video_note"]) +
f'''<div class="videos"><div class="vid real reveal"><video controls preload="none" poster="{c["video_poster"]}"><source src="{c["video_file"]}" type="video/mp4"></video><p>{c["video_caption"]}</p></div><div class="vid reveal" style="--bg:url(img/vendanges.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Vendanges — vidéo à venir</p></div><div class="vid reveal" style="--bg:url(img/banquet.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Banquet annuel — vidéo à venir</p></div></div></section>
<div class="lightbox" id="lb"><button class="x" aria-label="Fermer">×</button><img alt=""><p></p></div>''' + FOOT)

# ---------- CONTACT
c = load("contact")
pages["contact.html"] = (head("Contact", c["meta_desc"], "contact.html") +
hero(c["hero_image"], "Nous écrire", "<em>Contact</em>", "Une question, une envie de vendanger ? Écrivez-nous.", "short") +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Coordonnées</p><h2>Nous contacter</h2>
<ul class="coords"><li><b>Email</b><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li><li><b>Téléphone</b><a href="tel:{SITE["phone_tel"]}">{SITE["phone"]}</a></li><li><b>Siège</b>{SITE["address_line1"]}<br>{SITE["address_line2"]}<br>{SITE["address_line3"]}</li></ul>
<a class="btn" target="_blank" rel="noopener" href="https://www.openstreetmap.org/search?query=1%20bis%20rue%20Martel%2069630%20Chaponost">Voir sur la carte</a></div>
<form class="form paper reveal" name="contact" method="POST" action="merci.html" data-netlify="true" netlify-honeypot="bot"><input type="hidden" name="form-name" value="contact"><p class="hp"><input name="bot"></p>
<label>Nom<input name="nom" required></label><label>Email<input type="email" name="email" required></label><label>Sujet<input name="sujet"></label><label>Message<textarea name="message" rows="5" required></textarea></label><button class="btn" type="submit">Envoyer</button></form></section>''' + FOOT)

# ---------- MERCI / MENTIONS
pages["merci.html"] = (head("Merci", "Message bien reçu.", "") + '<section class="wrap merci"><p class="hand big">Merci !</p><h1>Votre message est bien parti.</h1><p>L\'association vous répondra rapidement.</p><a class="btn" href="index.html">Retour à l\'accueil</a></section>' + FOOT)
pages["mentions-legales.html"] = (head("Mentions légales", "Mentions légales du site des Coteaux de Chaponost.", "") + f'''<section class="wrap legalp"><h1>Mentions légales</h1>
<h3>Éditeur</h3><p>Les Coteaux de Chaponost, association loi 1901 — {SITE["address_line1"]}, {SITE["address_line2"]}, {SITE["address_line3"]}. Contact : {SITE["email"]}. RNA / SIRET : à compléter.</p>
<h3>Statut du site</h3><p>Maquette de démonstration réalisée par AssoVisible. Les textes marqués « à compléter » ou « à confirmer » seront validés par l'association.</p>
<h3>Crédits photos</h3><p>Photographies et vidéo transmises par l'association (aperçu, non définitif). Silhouette du vendangeur : visuel de l'association.</p>
<h3>Données personnelles</h3><p>Les informations saisies dans le formulaire de contact servent uniquement à répondre aux demandes. Droit d'accès et de rectification auprès de l'association.</p>
<h3>Santé</h3><p>L'abus d'alcool est dangereux pour la santé, à consommer avec modération.</p></section>''' + FOOT)

for name, html in pages.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(html)
for old in OLD_PAGES:
    p = os.path.join(OUT, old)
    if os.path.exists(p):
        os.remove(p)
print("pages:", len(pages))
