#!/usr/bin/env python3
"""Génère le site Les Coteaux de Chaponost (pages statiques) à partir des fichiers content/*.json.

Chaque texte / photo modifiable porte un attribut data-* que edit.js utilise pour
l'édition directe sur le site :
  data-e="page|cle"        texte simple          data-multi  -> plusieurs paragraphes
  data-ei="page|cle"       photo (img ou fond)
  data-list="page|chemin"  liste d'éléments      data-item data-oi="n" = un élément
  data-fd="champ"          texte d'un élément    data-fi="champ" = photo d'un élément
"""
import os, json, html, re
from urllib.parse import quote

OUT = os.path.dirname(os.path.abspath(__file__))
CDIR = os.path.join(OUT, "content")


def esc(o):
    if isinstance(o, str):
        return html.escape(o, quote=True)
    if isinstance(o, list):
        return [esc(x) for x in o]
    if isinstance(o, dict):
        return {k: esc(v) for k, v in o.items()}
    return o


def load(name):
    with open(os.path.join(CDIR, f"{name}.json"), encoding="utf-8") as f:
        return esc(json.load(f))


SITE = load("site")
_digits = re.sub(r"\D", "", html.unescape(SITE["phone"]))
SITE["phone_tel"] = ("+33" + _digits[1:]) if _digits.startswith("0") else ("+" + _digits)

NAV = [("index.html", "Accueil"), ("association.html", "Association"), ("la-vigne.html", "La vigne"),
       ("cerisaie.html", "La Cerisaie"), ("agenda.html", "Agenda"), ("evenements.html", "Événements"),
       ("galerie.html", "Galerie"), ("contact.html", "Contact")]

OLD_PAGES = ["nos-vins.html", "rejoindre.html"]

LOGO = '''<img class="logo" src="img/vendangeur.png" alt="" width="22" height="40">'''

P = ""  # page courante (nom du fichier content/*.json)


# ---------- aides d'édition directe ----------
def E(page, path, v):
    return f'<span data-e="{page}|{path}">{v}</span>'


def paras(text):
    return "".join(f"<p>{p.strip()}</p>" for p in (text or "").split("\n\n") if p.strip())


def EM(page, path, v):
    return f'<div data-e="{page}|{path}" data-multi>{paras(v)}</div>'


def EI(page, path):
    return f'data-ei="{page}|{path}"'


def F(field, v):
    return f'<span data-fd="{field}">{v}</span>'


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
<div><h4>Nous écrire</h4><p>{E("site","address_line1",SITE["address_line1"])}<br>{E("site","address_line2",SITE["address_line2"])}<br>{E("site","address_line3",SITE["address_line3"])}</p><p><a href="mailto:{SITE["email"]}">{E("site","email",SITE["email"])}</a><br><a href="tel:{SITE["phone_tel"]}">{E("site","phone",SITE["phone"])}</a></p><p><a href="{SITE["facebook_url"]}" target="_blank" rel="noopener">Suivez-nous sur Facebook →</a></p></div></div>
<p class="legal">L'abus d'alcool est dangereux pour la santé, à consommer avec modération. · Maquette de démonstration réalisée par AssoVisible. · <a class="adminlink" href="modifier/">Modifier le site</a></p></footer>
<script src="app.js"></script><script src="edit.js" defer></script></body></html>'''


def hero(img, kicker, h1, sub, cls="", ei=""):
    return f'''<section class="hero {cls}" style="--bg:url({img})" {ei}><div class="hero-in"><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="sub">{sub}</p></div><span class="scroll">Défiler</span></section>'''


def band(img, quote, who="", ei=""):
    return f'<section class="band" style="--bg:url({img})" {ei}><blockquote>{quote}<cite>{who}</cite></blockquote></section>'


def title(kicker, h2, intro=""):
    return f'<div class="title reveal"><p class="kicker">{kicker}</p><h2>{h2}</h2>{"<p class=intro>"+intro+"</p>" if intro else ""}</div>'


def seegalerie(tag):
    return f'<p class="note reveal seelink"><a href="galerie.html#{tag}">Voir en images dans la galerie →</a></p>'


FLASH = f'''<div id="flash" class="flash"><p>📅 N'oubliez pas <b>{E("site","flash_event",SITE["flash_event"])}</b> le <b>{E("site","flash_date",SITE["flash_date"])}</b>. <a href="agenda.html">Voir l'agenda →</a></p><button class="flash-x" aria-label="Fermer">×</button></div>'''

pages = {}

# ---------- ACCUEIL
P = "index"; c = load(P)
pages["index.html"] = (head("Accueil", c["meta_desc"], "index.html") +
FLASH +
hero(c["hero_image"], E(P, "hero_kicker", c["hero_kicker"]), "Les Coteaux<br><em>de Chaponost</em>", E(P, "hero_sub", c["hero_sub"]), "bright", EI(P, "hero_image")) +
f'''<section class="wrap welcome reveal"><p class="kicker">Mot de bienvenue</p><p class="lead">{E(P,"welcome_text",c["welcome_text"])}</p></section>
<section class="wrap chiffres reveal"><div><b data-n="130">130</b><span>adhérents bénévoles</span></div><div><b data-n="400">400</b><span>bouteilles par an</span></div><div><b>2</b><span>vins, blanc &amp; rouge</span></div><div><b>1</b><span>dernière vigne du village</span></div></section>
<section class="next wrap reveal"><div class="label"><span class="tag">À ne pas manquer</span><p class="hand">Prochain rendez-vous</p><p>{E(P,"next_text",c["next_text"])}</p></div>
<a class="btn" href="agenda.html">Voir tout l'agenda</a></section>
<section class="wrap shortcuts">''' + title("Le site en un coup d'œil", "Découvrir les Coteaux") + '''<div class="cards shortcuts-grid">
<a class="card reveal" href="association.html"><i>01</i><h3>L'association</h3><p>Histoire, bureau, vie associative.</p></a>
<a class="card reveal" href="la-vigne.html"><i>02</i><h3>La vigne</h3><p>Parcelle, cépages, travaux, nos vins.</p></a>
<a class="card reveal" href="cerisaie.html"><i>03</i><h3>La Cerisaie</h3><p>Le verger et les confitures maison.</p></a>
<a class="card reveal" href="agenda.html"><i>04</i><h3>Agenda</h3><p>Toutes les dates à venir.</p></a>
<a class="card reveal" href="evenements.html"><i>05</i><h3>Événements</h3><p>Nos rendez-vous en photos.</p></a>
<a class="card reveal" href="galerie.html"><i>06</i><h3>Galerie</h3><p>Photos &amp; vidéos de la vigne.</p></a></div></section>
<section class="wrap split">''' + f'''<div class="reveal"><p class="kicker">Notre histoire</p><h2>Une vigne sauvée<br>par ceux qui l'aiment</h2>
{EM(P,"history_text",c["history_text"])}<a class="btn" href="association.html">Découvrir l'association</a></div>
<figure class="reveal"><img src="{c["history_image"]}" {EI(P,"history_image")} alt="Adhérents réunis autour d'un repas" loading="lazy"><figcaption>La vie de l'association</figcaption></figure></section>
<section class="cta"><h2>Une question, une envie de nous rejoindre ?</h2><p>{E(P,"cta_text",c["cta_text"])}</p><a class="btn light" href="contact.html">Nous écrire</a></section>''' + FOOT)

# ---------- ASSOCIATION
P = "association"; c = load(P)
org_items = "".join(f'<li class="evt" data-item data-oi="{i}"><span class="m">{F("date",o["date"])}</span><div><h4>{F("title",o["title"])}</h4><p>{F("text",o["text"])}</p></div></li>' for i, o in enumerate(c["org_items"]))
press_items = "".join(f'<div class="card" data-item data-oi="{i}"><i>—</i><h3>{F("title",p["title"])}</h3><p>{F("text",p["text"])}</p></div>' for i, p in enumerate(c["press_items"]))
pages["association.html"] = (head("L'association", c["meta_desc"], "association.html") +
hero(c["hero_image"], "L'association", "Sauvegarder la<br><em>dernière vigne</em>", "Un patrimoine viticole préservé par des bénévoles passionnés.", "short", EI(P, "hero_image")) +
'<section class="wrap">' + title("Historique", "Une vigne, une histoire") +
f'''<div class="split"><div class="reveal">{EM(P,"history_text",c["history_text"])}
<p><small><i>{E(P,"history_note",c["history_note"])}</i></small></p></div>
<figure class="reveal"><img src="{c["history_image"]}" {EI(P,"history_image")} alt="Trois adhérents taillent la vigne" loading="lazy"><figcaption>Taille de printemps</figcaption></figure></div></section>''' +
band("img/caisses.jpg", "130 adhérents, des retraités aux plus jeunes : la vigne se cultive à plusieurs mains.") +
f'<section class="wrap word reveal"><div class="paper"><p class="hand big">Le mot du Bureau</p><p>{E(P,"word_text",c["word_text"])}</p><p class="sign">— {E(P,"word_signature",c["word_signature"])}<br><small><i>texte de démonstration, à valider par l\'association</i></small></p></div></section>' +
'<section class="wrap">' + title("Composition", "Bureau, Conseil d'administration &amp; commissions", "Composition à faire valider par l'association — tous les champs ci-dessous sont des exemples à remplacer.") +
f'''<div class="fiche reveal"><div><span>Président(e)</span><b>{E(P,"president",c["president"])}</b></div><div><span>Vice-président(e)</span><b>{E(P,"vice_president",c["vice_president"])}</b></div><div><span>Trésorier(ère)</span><b>{E(P,"treasurer",c["treasurer"])}</b></div><div><span>Secrétaire</span><b>{E(P,"secretary",c["secretary"])}</b></div><div><span>Membres du CA</span><b>{E(P,"board_members",c["board_members"])}</b></div><div><span>Commissions</span><b>{E(P,"commissions",c["commissions"])}</b></div></div></section>
<section class="wrap">''' + title("Organisation", "Le rythme de l'année associative") +
f'<ul class="tl reveal" style="max-width:760px;margin:2rem auto 0" data-list="{P}|org_items">{org_items}</ul></section>' +
'<section class="wrap">' + title("Presse", "On parle de nous", "Aucun article n'a été retrouvé à ce jour : les parutions presse (Le Progrès, Le Pays, bulletin municipal…) pourront être ajoutées ici au fur et à mesure.") +
f'<div class="cards reveal" data-list="{P}|press_items">{press_items}</div></section>' + FOOT)


# ---------- LA VIGNE (fusion vigne + vins)
def bouteille(nom, cls, cepage_html, desc_html):
    return f'''<article class="vin {cls} reveal"><div class="etiq"><svg viewBox="0 0 60 150" class="btl"><path d="M24 4h12v26c0 8 14 14 14 34v76c0 4-3 6-6 6H16c-3 0-6-2-6-6V64c0-20 14-26 14-34z" fill="currentColor"/><rect x="14" y="78" width="32" height="40" rx="2" fill="#f3ead7"/><text x="30" y="96" text-anchor="middle" font-size="6" font-family="serif" fill="#5b1424">LES COTEAUX</text><text x="30" y="105" text-anchor="middle" font-size="5" font-family="serif" fill="#5b1424">de Chaponost</text><text x="30" y="113" text-anchor="middle" font-size="4" font-family="serif" fill="#7a5230">Coteaux du Lyonnais</text></svg></div>
<div><h3>{nom}</h3><p>{desc_html}</p><dl><dt>Millésime</dt><dd>à compléter</dd><dt>Cépage</dt><dd>{cepage_html}</dd><dt>Volume</dt><dd>à compléter</dd><dt>Notes de dégustation</dt><dd>à compléter</dd></dl></div></article>'''


P = "la-vigne"; c = load(P)
steps = "".join(f'<li class="reveal" data-item data-oi="{i}"><b>{F("title",s["title"])}</b><span>{F("text",s["text"])}</span></li>' for i, s in enumerate(c["steps"]))
millesimes_rows = "".join(f'<tr data-item data-oi="{i}"><td>{F("year",m["year"])}</td><td>{F("blanc",m["blanc"])}</td><td>{F("rouge",m["rouge"])}</td><td>{F("remarks",m["remarks"])}</td></tr>' for i, m in enumerate(c["millesimes"]))
_loc = html.unescape(c["loc_location"])
_maps = "https://www.google.com/maps/search/?api=1&amp;query=" + quote(_loc)
pages["la-vigne.html"] = (head("La vigne", c["meta_desc"], "la-vigne.html") +
hero(c["hero_image"], "Notre parcelle", "La <em>dernière vigne</em><br>du village", "Un coteau, des rangs de ceps, et des mains qui savent.", "short", EI(P, "hero_image")) +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Le terroir</p><h2>Les Coteaux du Lyonnais</h2>
{EM(P,"terroir_text",c["terroir_text"])}</div>
<figure class="reveal"><img src="{c["terroir_image"]}" {EI(P,"terroir_image")} alt="La parcelle sous la neige" loading="lazy"><figcaption>La parcelle en hiver</figcaption></figure></section>
<section class="wrap">''' + title("Notre parcelle", "Fiche d'identité", "Les éléments ci-dessous sont modulables : l'association peut les compléter.") +
f'''<div class="fiche reveal"><div><span>Localisation</span><b>{E(P,"loc_location",c["loc_location"])}</b></div><div><span>Surface</span><b>{E(P,"loc_surface",c["loc_surface"])}</b></div><div><span>Exposition</span><b>{E(P,"loc_exposition",c["loc_exposition"])}</b></div><div><span>Année de plantation</span><b>{E(P,"loc_plantation_year",c["loc_plantation_year"])}</b></div><div><span>Appellation</span><b>{E(P,"loc_appellation",c["loc_appellation"])}</b></div><div><span>Production</span><b>{E(P,"loc_production",c["loc_production"])}</b></div></div></section>
<section class="wrap">''' + title("Où se trouve la vigne", E(P, "loc_location", c["loc_location"])) +
f'''<div class="duo mapshots reveal"><figure><img src="{c["loc_sat_image"]}" {EI(P,"loc_sat_image")} alt="Vue satellite de la parcelle"><figcaption>Vue satellite — la parcelle est indiquée par la flèche</figcaption></figure>
<figure><img src="{c["loc_plan_image"]}" {EI(P,"loc_plan_image")} alt="Plan de situation de la parcelle"><figcaption>Plan de situation</figcaption></figure></div>
<p class="note reveal seelink"><a target="_blank" rel="noopener" href="{_maps}">Ouvrir le plan interactif →</a></p></section>
<section class="wrap">''' + title("Les cépages", "Présentation des cépages") +
f'''<div class="duo"><div class="grape white reveal"><h3>Vin blanc</h3><p>{E(P,"white_text",c["white_text"])}</p></div><div class="grape red reveal"><h3>Vin rouge</h3><p>{E(P,"red_text",c["red_text"])}</p></div></div></section>''' +
band(c["band_image"], E(P, "band_text", c["band_text"]), "", EI(P, "band_image")) +
'<section class="wrap">' + title("Travaux de la vigne", "Les gestes de l'année", "Dates et saisonnalité données à titre indicatif ; à ajuster avec l'association.") +
f'''<ol class="steps" data-list="{P}|steps">{steps}</ol>
<div class="split" style="margin-top:2.4rem"><figure class="reveal"><img src="{c["step_image1"]}" {EI(P,"step_image1")} alt="Taille de la vigne" loading="lazy"><figcaption>Taille</figcaption></figure><figure class="reveal"><img src="{c["step_image2"]}" {EI(P,"step_image2")} alt="Le pressoir" loading="lazy"><figcaption>Pressage</figcaption></figure></div>
{seegalerie("t")}</section>
<section class="wrap">''' + title("Notre vigneron partenaire", "Un professionnel à nos côtés", "L'association est accompagnée par un vigneron partenaire pour le conseil technique et la vinification. Présentation à fournir par l'association.") +
f'''<div class="paper reveal" style="max-width:760px;margin:2rem auto 0"><p><b>Nom du vigneron / domaine</b> : {E(P,"vigneron_name",c["vigneron_name"])}<br><b>Rôle auprès de l'association</b> : {E(P,"vigneron_role",c["vigneron_role"])}<br><b>Présentation</b> : {E(P,"vigneron_text",c["vigneron_text"])}</p></div></section>
<section class="wrap">''' + title("Production confidentielle", "Nos vins — 400 bouteilles en moyenne par an", "Notre production est limitée et réservée en priorité aux adhérents. Chaque millésime a son histoire, racontée ci-dessous.") +
'<div class="vins">' + bouteille("Blanc des Coteaux", "blanc", E(P, "bottle_white_cepage", c["bottle_white_cepage"]), E(P, "bottle_white_desc", c["bottle_white_desc"])) + bouteille("Rouge des Coteaux", "rouge", E(P, "bottle_red_cepage", c["bottle_red_cepage"]), E(P, "bottle_red_desc", c["bottle_red_desc"])) + '</div>' +
f'''<div class="tablewrap reveal"><table><thead><tr><th>Millésime</th><th>Blanc</th><th>Rouge</th><th>Remarques</th></tr></thead><tbody data-list="{P}|millesimes">{millesimes_rows}</tbody></table></div>
<p class="note reveal">Pour réserver des bouteilles, <a href="contact.html">contactez l'association</a>.</p></section>''' + FOOT)

# ---------- LA CERISAIE
P = "cerisaie"; c = load(P)
pages["cerisaie.html"] = (head("La Cerisaie", c["meta_desc"], "cerisaie.html") +
hero(c["hero_image"], "Le verger", "La <em>Cerisaie</em>", "Nos cerisiers, et les confitures qui en naissent.", "short", EI(P, "hero_image")) +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Le verger</p><h2>Un verger de cerisiers</h2>
<p>{E(P,"intro_text",c["intro_text"])}</p>
<p><small><i>{E(P,"intro_note",c["intro_note"])}</i></small></p></div>
<figure class="reveal"><img src="{c["intro_image"]}" {EI(P,"intro_image")} alt="Cerises du verger" loading="lazy"><figcaption>Cerises du verger</figcaption></figure></section>
<section class="wrap">''' + title("La confiture maison", "Préparée en commun, vendue par l'association") +
f'''<div class="split"><figure class="reveal"><img src="{c["confiture_image"]}" {EI(P,"confiture_image")} alt="Préparation de la confiture de cerises en commun" loading="lazy"><figcaption>Préparation des confitures</figcaption></figure>
<div class="reveal paper cotis"><p class="hand big">Vente de confiture</p><p><b>Prix du pot</b> : {E(P,"price",c["price"])}<br><b>Points de vente</b> : {E(P,"points_de_vente",c["points_de_vente"])}<br><b>Période de vente</b> : {E(P,"periode",c["periode"])}</p><p>Pour réserver des pots ou en savoir plus, <a href="contact.html">contactez l'association</a>.</p></div></div>
''' + seegalerie("f") + '</section>' + FOOT)

# ---------- AGENDA
P = "agenda"; c = load(P)
romans = ["I", "II", "III", "IV", "V", "VI"]
groups_html = ""
for gi, g in enumerate(c["groups"]):
    events = "".join(f'<li class="evt reveal" data-item data-oi="{i}"><span class="m">{F("date",e["date"])}</span><div><h4>{F("title",e["title"])}</h4><p>{F("text",e["text"])}</p></div></li>' for i, e in enumerate(g["events"]))
    groups_html += f'<div id="{g["anchor"]}" class="axe"><h2><i>{romans[gi]}</i> {E(P, f"groups.{gi}.heading", g["heading"])}</h2><ul class="tl" data-list="{P}|groups.{gi}.events">{events}</ul></div>'
pages["agenda.html"] = (head("Agenda", c["meta_desc"], "agenda.html") +
hero(c["hero_image"], "Au fil de l'année", "L'<em>agenda</em>", "Toutes les dates à venir, en un seul endroit.", "short", EI(P, "hero_image")) +
f'<section class="wrap"><p class="note reveal">{E(P,"note_text",c["note_text"])}</p>{groups_html}</section>' + FOOT)

# ---------- EVENEMENTS
P = "evenements"; c = load(P)
evcards = "".join(f'<article class="evcard reveal" data-item data-oi="{i}"><img src="{e["image"]}" data-fi="image" alt="{e["title"]}" loading="lazy"><div><h3>{F("title",e["title"])}</h3><p>{F("text",e["text"])}</p><a href="galerie.html#{e["tag"]}">Voir en photos →</a></div></article>' for i, e in enumerate(c["cards"]))
pages["evenements.html"] = (head("Événements", c["meta_desc"], "evenements.html") +
hero(c["hero_image"], "Nos rendez-vous", "<em>Événements</em>", "Les moments qui rassemblent les 130 adhérents.", "short", EI(P, "hero_image")) +
'<section class="wrap">' + title("Au fil de l'année", "Nos grands rendez-vous") +
f'<div class="evcards" data-list="{P}|cards">{evcards}</div>' + seegalerie("c") + '</section>' + FOOT)

# ---------- GALERIE
P = "galerie"; c = load(P)
TAGLABEL = {"v": "Vendanges", "t": "Travaux", "f": "Festivités", "c": "Événements"}
tiles = "".join(f'<a class="tile reveal" href="{t["image"]}" data-item data-oi="{i}" data-cat="{t["tag"]}" data-tag="{t["tag"]}" data-cap="{t["caption"]}"><img src="{t["image"]}" data-fi="image" alt="{t["caption"]}" loading="lazy"><span class="tlabel">{TAGLABEL.get(t["tag"], "")}</span><em class="tcap" data-fd="caption">{t["caption"]}</em></a>' for i, t in enumerate(c["tiles"]))
pages["galerie.html"] = (head("Galerie photos & vidéos", c["meta_desc"], "galerie.html") +
hero(c["hero_image"], "Photos & vidéos", "La vigne <em>en images</em>", "Travaux, vendanges, festivités, événements.", "short", EI(P, "hero_image")) +
f'''<section class="wrap"><p class="note reveal">{E(P,"note_text",c["note_text"])}</p>
<div class="filters reveal"><button class="on" data-f="all">Tout</button><button data-f="t">Travaux</button><button data-f="v">Vendanges</button><button data-f="f">Festivités</button><button data-f="c">Événements</button><button class="vidbtn" data-f="vid">▶ Vidéos</button></div>
<div class="grid" data-list="{P}|tiles">''' + tiles + '''</div></section>
<section class="wrap">''' + title("Vidéos", "Les vignes en mouvement", E(P, "video_note", c["video_note"])) +
f'''<div class="videos"><div class="vid real reveal"><video controls preload="none" poster="{c["video_poster"]}"><source src="{c["video_file"]}" type="video/mp4"></video><p>{E(P,"video_caption",c["video_caption"])}</p></div><div class="vid reveal" style="--bg:url(img/vendanges.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Vendanges — vidéo à venir</p></div><div class="vid reveal" style="--bg:url(img/banquet.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Banquet annuel — vidéo à venir</p></div></div></section>
<div class="lightbox" id="lb"><button class="x" aria-label="Fermer">×</button><img alt=""><p></p></div>''' + FOOT)

# ---------- CONTACT
P = "contact"; c = load(P)
pages["contact.html"] = (head("Contact", c["meta_desc"], "contact.html") +
hero(c["hero_image"], "Nous écrire", "<em>Contact</em>", "Une question, une envie de vendanger ? Écrivez-nous.", "short", EI(P, "hero_image")) +
'<section class="wrap split">' + f'''<div class="reveal"><p class="kicker">Coordonnées</p><h2>Nous contacter</h2>
<ul class="coords"><li><b>Email</b><a href="mailto:{SITE["email"]}">{E("site","email",SITE["email"])}</a></li><li><b>Téléphone</b><a href="tel:{SITE["phone_tel"]}">{E("site","phone",SITE["phone"])}</a></li><li><b>Siège</b>{E("site","address_line1",SITE["address_line1"])}<br>{E("site","address_line2",SITE["address_line2"])}<br>{E("site","address_line3",SITE["address_line3"])}</li></ul>
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

for name, html_ in pages.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(html_)
for old in OLD_PAGES:
    p = os.path.join(OUT, old)
    if os.path.exists(p):
        os.remove(p)

# ---------- PAGE DE CONNEXION « Modifier le site » ----------
os.makedirs(os.path.join(OUT, "modifier"), exist_ok=True)
with open(os.path.join(OUT, "modifier", "index.html"), "w", encoding="utf-8") as f:
    f.write('''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Modifier le site · Les Coteaux de Chaponost</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="../edit.css"></head><body class="cc-login-page">
<main class="cc-login"><img class="cc-login-logo" src="../img/vendangeur.png" alt="" width="44" height="80">
<h1>Modifier le site</h1>
<p class="cc-login-intro">Connectez-vous pour changer les textes et les photos du site, directement sur les pages.</p>
<form id="cc-form" autocomplete="on">
<label for="cc-email">Votre adresse email</label>
<input id="cc-email" name="email" type="email" autocomplete="username" required>
<label for="cc-pass">Votre mot de passe</label>
<input id="cc-pass" name="password" type="password" autocomplete="current-password" required>
<button type="submit" class="cc-big" id="cc-go">Se connecter</button>
<p id="cc-msg" role="alert"></p>
</form>
<div id="cc-already" hidden><p>Vous êtes déjà connecté.</p><button class="cc-big" id="cc-enter">Modifier le site</button><button class="cc-link" id="cc-logout">Me déconnecter</button></div>
<p class="cc-back"><a href="../index.html">← Retour au site</a></p></main>
<script src="../login.js"></script></body></html>
''')
print("pages:", len(pages) + 1)
