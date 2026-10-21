#!/usr/bin/env python3
"""Génère le site Les Coteaux de Chaponost (pages statiques)."""
import os
OUT = os.path.dirname(os.path.abspath(__file__))

NAV = [("index.html", "Accueil"), ("association.html", "Association"), ("la-vigne.html", "La vigne"),
       ("cerisaie.html", "La Cerisaie"), ("agenda.html", "Agenda"), ("evenements.html", "Événements"),
       ("galerie.html", "Galerie"), ("contact.html", "Contact")]

OLD_PAGES = ["nos-vins.html", "rejoindre.html"]  # fusionnées / supprimées dans la v3

LOGO = '''<img class="logo" src="img/vendangeur.png" alt="" width="22" height="40">'''

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
<div><h4>Nous écrire</h4><p>Maison des Associations<br>1 bis rue Martel<br>69630 Chaponost</p><p><a href="mailto:lescoteauxdechaponost@laposte.net">lescoteauxdechaponost@laposte.net</a><br><a href="tel:+33616241682">06 16 24 16 82</a></p><p><a href="https://www.facebook.com/profile.php?id=61575731934542" target="_blank" rel="noopener">Suivez-nous sur Facebook →</a></p></div></div>
<p class="legal">L'abus d'alcool est dangereux pour la santé, à consommer avec modération. · Maquette de démonstration réalisée par AssoVisible.</p></footer>
<script src="app.js"></script></body></html>'''

def hero(img, kicker, h1, sub, cls=""):
    return f'''<section class="hero {cls}" style="--bg:url({img})"><div class="hero-in"><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="sub">{sub}</p></div><span class="scroll">Défiler</span></section>'''

def band(img, quote, who=""):
    return f'<section class="band" style="--bg:url({img})"><blockquote>{quote}<cite>{who}</cite></blockquote></section>'

def title(kicker, h2, intro=""):
    return f'<div class="title reveal"><p class="kicker">{kicker}</p><h2>{h2}</h2>{"<p class=intro>"+intro+"</p>" if intro else ""}</div>'

def seegalerie(tag, label):
    return f'<p class="note reveal seelink"><a href="galerie.html#{tag}">Voir en images dans la galerie →</a></p>'

FLASH = '''<div id="flash" class="flash"><p>📅 N'oubliez pas <b>[nom de l'événement — à compléter]</b> le <b>[date à compléter]</b>. <a href="agenda.html">Voir l'agenda →</a></p><button class="flash-x" aria-label="Fermer">×</button></div>'''

pages = {}

# ---------- ACCUEIL
pages["index.html"] = (head("Accueil", "La dernière vigne de Chaponost, 130 bénévoles, 400 bouteilles par an. Association Les Coteaux de Chaponost, Coteaux du Lyonnais.", "index.html") +
FLASH +
hero("img/hero-automne.jpg", "Coteaux du Lyonnais · Chaponost (69)", "Les Coteaux<br><em>de Chaponost</em>",
     "La dernière vigne de Chaponost, <b>130 bénévoles</b>, <b>400 bouteilles</b> par an.", "bright") +
'''<section class="wrap welcome reveal"><p class="kicker">Mot de bienvenue</p><p class="lead">Bienvenue chez les Coteaux de Chaponost&nbsp;! Nous cultivons depuis des années la dernière vigne du village, un petit bout de patrimoine que 130 bénévoles font vivre, saison après saison, dans la bonne humeur. Ce site vous invite à nous découvrir, à suivre notre agenda et à nous rejoindre.</p></section>
<section class="wrap chiffres reveal"><div><b data-n="130">130</b><span>adhérents bénévoles</span></div><div><b data-n="400">400</b><span>bouteilles par an</span></div><div><b>2</b><span>vins, blanc &amp; rouge</span></div><div><b>1</b><span>dernière vigne du village</span></div></section>
<section class="next wrap reveal"><div class="label"><span class="tag">À ne pas manquer</span><p class="hand">Prochain rendez-vous</p><p>Le prochain rendez-vous de l'association est annoncé ici dès qu'il est fixé. <small>(à mettre à jour par l'association)</small></p></div>
<a class="btn" href="agenda.html">Voir tout l'agenda</a></section>
<section class="wrap shortcuts">''' + title("Le site en un coup d'œil", "Découvrir les Coteaux") + '''<div class="cards shortcuts-grid">
<a class="card reveal" href="association.html"><i>01</i><h3>L'association</h3><p>Histoire, bureau, vie associative.</p></a>
<a class="card reveal" href="la-vigne.html"><i>02</i><h3>La vigne</h3><p>Parcelle, cépages, travaux, nos vins.</p></a>
<a class="card reveal" href="cerisaie.html"><i>03</i><h3>La Cerisaie</h3><p>Le verger et les confitures maison.</p></a>
<a class="card reveal" href="agenda.html"><i>04</i><h3>Agenda</h3><p>Toutes les dates à venir.</p></a>
<a class="card reveal" href="evenements.html"><i>05</i><h3>Événements</h3><p>Nos rendez-vous en photos.</p></a>
<a class="card reveal" href="galerie.html"><i>06</i><h3>Galerie</h3><p>Photos &amp; vidéos de la vigne.</p></a></div></section>
<section class="wrap split">''' + '''<div class="reveal"><p class="kicker">Notre histoire</p><h2>Une vigne sauvée<br>par ceux qui l'aiment</h2>
<p>À Chaponost, comme dans tout l'ouest lyonnais, la vigne a longtemps rythmé la vie du village. Il n'en reste aujourd'hui qu'une parcelle&nbsp;: la dernière. Des bénévoles de tous âges se sont réunis pour la cultiver, la faire vivre et transmettre ce patrimoine des <b>Coteaux du Lyonnais</b>.</p>
<p>Taille, vendanges, pressage, mise en bouteille&nbsp;: tout se fait ensemble, à la main, dans la bonne humeur.</p><a class="btn" href="association.html">Découvrir l'association</a></div>
<figure class="reveal"><img src="img/pique-nique.jpg" alt="Adhérents réunis autour d'un repas" loading="lazy"><figcaption>La vie de l'association</figcaption></figure></section>
<section class="cta"><h2>Une question, une envie de nous rejoindre ?</h2><p>L'association est ouverte à tous, sans condition d'âge ni d'expérience.</p><a class="btn light" href="contact.html">Nous écrire</a></section>''' + FOOT)

# ---------- ASSOCIATION
pages["association.html"] = (head("L'association", "Historique, composition du bureau et du CA, organisation et actualité presse de l'association Les Coteaux de Chaponost.", "association.html") +
hero("img/pique-nique.jpg", "L'association", "Sauvegarder la<br><em>dernière vigne</em>", "Un patrimoine viticole préservé par des bénévoles passionnés.", "short") +
'<section class="wrap">' + title("Historique", "Une vigne, une histoire") +
'''<div class="split"><div class="reveal"><p>À Chaponost, comme dans tout l'ouest lyonnais, la vigne a longtemps rythmé la vie du village. Il n'en reste aujourd'hui qu'une parcelle&nbsp;: la dernière. C'est pour la sauvegarder qu'est née l'association <b>Les Coteaux de Chaponost</b>, dont la mission est de <b>cultiver et faire vivre</b> ce dernier témoin du vignoble des Coteaux du Lyonnais sur la commune.</p>
<p>Depuis, des bénévoles de tous âges — <b>130 adhérents</b> aujourd'hui, majoritairement retraités mais ouverts à tous — se relaient au fil des saisons&nbsp;: taille, enherbement, traitements, vendanges, pressage, mise en bouteille. Chaque année, la parcelle donne environ <b>400 bouteilles</b> de vin blanc et de vin rouge.</p>
<p><small><i>Date de création, étapes marquantes de l'histoire de la vigne et de l'association : à compléter.</i></small></p></div>
<figure class="reveal"><img src="img/taille.jpg" alt="Trois adhérents taillent la vigne" loading="lazy"><figcaption>Taille de printemps</figcaption></figure></div></section>''' +
band("img/caisses.jpg", "130 adhérents, des retraités aux plus jeunes : la vigne se cultive à plusieurs mains.") +
'<section class="wrap word reveal"><div class="paper"><p class="hand big">Le mot du Bureau</p><p>« Cette vigne est le dernier témoin du passé viticole de Chaponost. Ensemble, nous la cultivons, nous la vendangeons et nous partageons le fruit de notre travail. Venez nous rejoindre&nbsp;! »</p><p class="sign">— Le Bureau de l\'association<br><small><i>texte de démonstration, à valider par l\'association</i></small></p></div></section>' +
'<section class="wrap">' + title("Composition", "Bureau, Conseil d'administration &amp; commissions", "Composition à faire valider par l'association — tous les champs ci-dessous sont des exemples à remplacer.") +
'''<div class="fiche reveal"><div><span>Président(e)</span><b>à compléter</b></div><div><span>Vice-président(e)</span><b>à compléter</b></div><div><span>Trésorier(ère)</span><b>à compléter</b></div><div><span>Secrétaire</span><b>à compléter</b></div><div><span>Membres du CA</span><b>à compléter</b></div><div><span>Commissions</span><b>Travaux de la vigne · Événements · Communication</b></div></div></section>
<section class="wrap">''' + title("Organisation", "Le rythme de l'année associative") +
'''<ul class="tl reveal" style="max-width:760px;margin:2rem auto 0"><li class="evt"><span class="m">À définir</span><div><h4>Réunions du Conseil d'administration</h4><p>Fréquence des CA à préciser par l'association (ex. trimestrielle).</p></div></li>
<li class="evt"><span class="m">Début d'année</span><div><h4>Assemblée générale</h4><p>Bilan de l'année et projets, ouverte à tous les adhérents.</p></div></li>
<li class="evt"><span class="m">Automne</span><div><h4>Vendanges</h4><p>Le grand rendez-vous collectif de la vigne.</p></div></li>
<li class="evt"><span class="m">Annuel</span><div><h4>Banquet annuel</h4><p>Le repas qui réunit tous les adhérents.</p></div></li></ul></section>
<section class="wrap">''' + title("Presse", "On parle de nous", "Aucun article n'a été retrouvé à ce jour : les parutions presse (Le Progrès, Le Pays, bulletin municipal…) pourront être ajoutées ici au fur et à mesure.") +
'''<div class="cards reveal"><div class="card"><i>—</i><h3>Article à venir</h3><p>Coupure de presse ou lien à transmettre à l'association.</p></div><div class="card"><i>—</i><h3>Article à venir</h3><p>Coupure de presse ou lien à transmettre à l'association.</p></div><div class="card"><i>—</i><h3>Article à venir</h3><p>Coupure de presse ou lien à transmettre à l'association.</p></div></div></section>''' + FOOT)

# ---------- LA VIGNE (fusion vigne + vins)
def bouteille(nom, cls, cepage, desc):
    return f'''<article class="vin {cls} reveal"><div class="etiq"><svg viewBox="0 0 60 150" class="btl"><path d="M24 4h12v26c0 8 14 14 14 34v76c0 4-3 6-6 6H16c-3 0-6-2-6-6V64c0-20 14-26 14-34z" fill="currentColor"/><rect x="14" y="78" width="32" height="40" rx="2" fill="#f3ead7"/><text x="30" y="96" text-anchor="middle" font-size="6" font-family="serif" fill="#5b1424">LES COTEAUX</text><text x="30" y="105" text-anchor="middle" font-size="5" font-family="serif" fill="#5b1424">de Chaponost</text><text x="30" y="113" text-anchor="middle" font-size="4" font-family="serif" fill="#7a5230">Coteaux du Lyonnais</text></svg></div>
<div><h3>{nom}</h3><p>{desc}</p><dl><dt>Millésime</dt><dd>à compléter</dd><dt>Cépage</dt><dd>{cepage}</dd><dt>Volume</dt><dd>à compléter</dd><dt>Notes de dégustation</dt><dd>à compléter</dd></dl></div></article>'''

pages["la-vigne.html"] = (head("La vigne", "La parcelle, le terroir, les cépages, les travaux de la vigne, le vigneron partenaire et les vins des Coteaux de Chaponost.", "la-vigne.html") +
hero("img/rangs.jpg", "Notre parcelle", "La <em>dernière vigne</em><br>du village", "Un coteau, des rangs de ceps, et des mains qui savent.", "short") +
'<section class="wrap split">' + '''<div class="reveal"><p class="kicker">Le terroir</p><h2>Les Coteaux du Lyonnais</h2>
<p>Au pied des Monts du Lyonnais, l'AOC <b>Coteaux du Lyonnais</b> s'étend sur les collines à l'ouest de Lyon. Sols de coteaux, expositions variées&nbsp;: un terroir connu pour ses rouges de gamay et ses blancs frais.</p>
<p>La parcelle de Chaponost en est l'un des derniers témoins sur la commune.</p></div>
<figure class="reveal"><img src="img/neige.jpg" alt="La parcelle sous la neige" loading="lazy"><figcaption>La parcelle en hiver</figcaption></figure></section>
<section class="wrap">''' + title("Notre parcelle", "Fiche d'identité", "Les éléments ci-dessous sont modulables : l'association peut les compléter.") +
'''<div class="fiche reveal"><div><span>Localisation</span><b>Chemin de l'Arcelan, 69630 Chaponost</b></div><div><span>Surface</span><b>à compléter</b></div><div><span>Exposition</span><b>à compléter</b></div><div><span>Année de plantation</span><b>à compléter</b></div><div><span>Appellation</span><b>Coteaux du Lyonnais</b></div><div><span>Production</span><b>≈ 400 bouteilles / an</b></div></div></section>
<section class="wrap">''' + title("Où se trouve la vigne", "Chemin de l'Arcelan, 69630 Chaponost") +
'''<div class="duo mapshots reveal"><figure><img src="img/localisation-satellite.jpg" alt="Vue satellite de la parcelle, chemin de l'Arcelan à Chaponost"><figcaption>Vue satellite — la parcelle est indiquée par la flèche</figcaption></figure>
<figure><img src="img/localisation-plan.jpg" alt="Plan de situation de la parcelle, chemin de l'Arcelan à Chaponost"><figcaption>Plan de situation</figcaption></figure></div>
<p class="note reveal seelink"><a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=Chemin+de+l%27Arcelan%2C+69630+Chaponost">Ouvrir le plan interactif →</a></p></section>
<section class="wrap">''' + title("Les cépages", "Présentation des cépages") +
'''<div class="duo"><div class="grape white reveal"><h3>Vin blanc</h3><p>Le vin blanc des Coteaux de Chaponost est issu du <b>chardonnay</b>, cépage emblématique des blancs en Coteaux du Lyonnais.</p></div><div class="grape red reveal"><h3>Vin rouge</h3><p>Le vin rouge est issu du <b>gamay</b>, cépage roi de l'appellation pour les rouges.</p></div></div></section>''' +
band("img/automne.jpg", "Une vigne se cultive toute l'année. Le raisin n'est que la dernière étape.") +
'<section class="wrap">' + title("Travaux de la vigne", "Les gestes de l'année", "Dates et saisonnalité données à titre indicatif ; à ajuster avec l'association.") +
f'''<ol class="steps">
<li class="reveal"><b>Taille</b><span>Hiver (janv.–mars) — on choisit les sarments qui porteront les grappes.</span></li>
<li class="reveal"><b>Enherbement</b><span>Printemps (avril–mai) — on entretient l'herbe entre les rangs.</span></li>
<li class="reveal"><b>Traitements</b><span>Printemps / été (mai–août) — on protège la vigne, au plus juste.</span></li>
<li class="reveal"><b>Vendanges</b><span>Fin d'été / automne (sept.–oct.) — la grande journée collective.</span></li>
<li class="reveal"><b>Pressage</b><span>Octobre — on presse le raisin et on met en cuve.</span></li>
<li class="reveal"><b>Mise en bouteille</b><span>Printemps suivant — étiquette collée main, évidemment.</span></li></ol>
<div class="split" style="margin-top:2.4rem"><figure class="reveal"><img src="img/taille.jpg" alt="Taille de la vigne" loading="lazy"><figcaption>Taille</figcaption></figure><figure class="reveal"><img src="img/pressoir.jpg" alt="Le pressoir" loading="lazy"><figcaption>Pressage</figcaption></figure></div>
{seegalerie("t","Travaux")}</section>
<section class="wrap">''' + title("Notre vigneron partenaire", "Un professionnel à nos côtés", "L'association est accompagnée par un vigneron partenaire pour le conseil technique et la vinification. Présentation à fournir par l'association.") +
'''<div class="paper reveal" style="max-width:760px;margin:2rem auto 0"><p><b>Nom du vigneron / domaine</b> : à compléter<br><b>Rôle auprès de l'association</b> : à compléter<br><b>Présentation</b> : à compléter (quelques lignes sur le partenariat, depuis quand, ce qu'il apporte à la vigne de Chaponost).</p></div></section>
<section class="wrap">''' + title("Production confidentielle", "Nos vins — 400 bouteilles en moyenne par an", "Notre production est limitée et réservée en priorité aux adhérents. Chaque millésime a son histoire, racontée ci-dessous.") +
'<div class="vins">' + bouteille("Blanc des Coteaux", "blanc", "Chardonnay", "Notre vin blanc, issu de la dernière vigne du village.") + bouteille("Rouge des Coteaux", "rouge", "Gamay", "Notre vin rouge, élevé et mis en bouteille par les bénévoles.") + '</div>' +
'''<div class="tablewrap reveal"><table><thead><tr><th>Millésime</th><th>Blanc</th><th>Rouge</th><th>Remarques</th></tr></thead><tbody>
<tr><td>2025</td><td>—</td><td>—</td><td>à compléter</td></tr><tr><td>2024</td><td>—</td><td>—</td><td>à compléter</td></tr><tr><td>2023</td><td>—</td><td>—</td><td>à compléter</td></tr></tbody></table></div>
<p class="note reveal">Pour réserver des bouteilles, <a href="contact.html">contactez l'association</a>.</p></section>''' + FOOT)

# ---------- LA CERISAIE
pages["cerisaie.html"] = (head("La Cerisaie", "Le verger de cerisiers des Coteaux de Chaponost et la vente de confitures de cerises maison.", "cerisaie.html") +
hero("img/cerises.jpg", "Le verger", "La <em>Cerisaie</em>", "Nos cerisiers, et les confitures qui en naissent.", "short") +
'<section class="wrap split">' + '''<div class="reveal"><p class="kicker">Le verger</p><h2>Un verger de cerisiers</h2>
<p>Aux côtés de la vigne, l'association entretient également une <b>cerisaie</b>. Chaque été, les cerises sont récoltées puis transformées en confitures par les bénévoles.</p>
<p><small><i>Nombre et variétés de cerisiers, surface du verger : à compléter par l'association.</i></small></p></div>
<figure class="reveal"><img src="img/cerises.jpg" alt="Cerises du verger" loading="lazy"><figcaption>Cerises du verger</figcaption></figure></section>
<section class="wrap">''' + title("La confiture maison", "Préparée en commun, vendue par l'association") +
'''<div class="split"><figure class="reveal"><img src="img/confiture.jpg" alt="Préparation de la confiture de cerises en commun" loading="lazy"><figcaption>Préparation des confitures</figcaption></figure>
<div class="reveal paper cotis"><p class="hand big">Vente de confiture</p><p><b>Prix du pot</b> : à compléter<br><b>Points de vente</b> : à compléter<br><b>Période de vente</b> : à compléter</p><p>Pour réserver des pots ou en savoir plus, <a href="contact.html">contactez l'association</a>.</p></div></div>
''' + seegalerie("f","Festivités") + '</section>' + FOOT)

# ---------- AGENDA
def evt(mois, titre, desc, axe):
    return f'<li class="evt reveal" data-axe="{axe}"><span class="m">{mois}</span><div><h4>{titre}</h4><p>{desc}</p></div></li>'

pages["agenda.html"] = (head("Agenda", "Toutes les dates à venir des Coteaux de Chaponost : travaux de la vigne, cerisaie, vie associative et événements festifs.", "agenda.html") +
hero("img/rangs.jpg", "Au fil de l'année", "L'<em>agenda</em>", "Toutes les dates à venir, en un seul endroit.", "short") +
'<section class="wrap"><p class="note reveal">Les mois indiqués suivent le calendrier habituel de la vigne&nbsp;; les dates précises sont communiquées par l’association.</p>' +
'<div id="travaux" class="axe"><h2><i>I</i> Travaux de la vigne</h2><ul class="tl">' +
evt("Janv.–Mars", "Taille", "On taille les ceps pour préparer la récolte.", "t") + evt("Avril–Mai", "Enherbement", "Entretien de l'herbe entre les rangs.", "t") + evt("Mai–Août", "Traitements", "Soins raisonnés de la vigne.", "t") + evt("Sept.–Oct.", "Vendanges", "La grande journée collective de cueillette.", "t") + evt("Oct.", "Pressage", "Pressage du raisin et mise en cuve.", "t") + evt("Printemps", "Mise en bouteille", "Embouteillage et étiquetage par les bénévoles.", "t") +
'</ul></div><div id="cerisaie" class="axe"><h2><i>II</i> La Cerisaie</h2><ul class="tl">' +
evt("Été", "Récolte des cerises", "Cueillette dans le verger, à compléter avec les dates précises.", "c") + evt("Été", "Confitures", "Fabrication des confitures de cerises, en commun.", "c") +
'</ul></div><div id="festif" class="axe"><h2><i>III</i> Événements festifs</h2><ul class="tl">' +
evt("Au fil de l'année", "Rendez-vous conviviaux", "Repas, dégustations, balades dans la vigne : le programme est à compléter par l'association.", "f") +
'</ul></div><div id="asso" class="axe"><h2><i>IV</i> Vie associative</h2><ul class="tl">' +
evt("Début d'année", "Assemblée générale", "Bilan de l'année et projets, ouvert à tous les adhérents.", "a") + evt("Annuel", "Banquet annuel", "Le grand repas qui réunit tous les adhérents.", "a") + '</ul></div></section>' + FOOT)

# ---------- EVENEMENTS
def evcard(img, titre, desc, tag):
    return f'''<article class="evcard reveal"><img src="{img}" alt="{titre}" loading="lazy"><div><h3>{titre}</h3><p>{desc}</p><a href="galerie.html#{tag}">Voir en photos →</a></div></article>'''

pages["evenements.html"] = (head("Événements", "Les événements festifs et associatifs des Coteaux de Chaponost : vendanges, banquet annuel, rendez-vous conviviaux.", "evenements.html") +
hero("img/banquet.jpg", "Nos rendez-vous", "<em>Événements</em>", "Les moments qui rassemblent les 130 adhérents.", "short") +
'<section class="wrap">' + title("Au fil de l'année", "Nos grands rendez-vous") +
'<div class="evcards">' +
evcard("img/vendanges.jpg", "Les vendanges", "Le grand rendez-vous de l'automne&nbsp;: toute la vigne se cueille à la main, en une ou plusieurs journées conviviales.", "v") +
evcard("img/banquet.jpg", "Le banquet annuel", "Le repas qui réunit chaque année tous les adhérents de l'association.", "c") +
evcard("img/pique-nique.jpg", "Rendez-vous conviviaux", "Au fil des saisons, des moments partagés autour de la vigne. Programme à compléter par l'association.", "f") +
'</div>' + seegalerie("c","Événements") + '</section>' + FOOT)

# ---------- GALERIE
G = [("v", "img/vendanges.jpg", "Vendanges dans la parcelle", "Vendanges"), ("v", "img/caisses.jpg", "Les caisses de raisin, noir et blanc", "Vendanges"),
     ("c", "img/banquet.jpg", "Repas en plein air, vue du ciel", "Événements"), ("f", "img/pique-nique.jpg", "Déjeuner entre adhérents", "Festivités"),
     ("t", "img/automne.jpg", "La vigne en automne", "Travaux"), ("t", "img/neige.jpg", "La parcelle sous la neige", "Travaux"),
     ("t", "img/rangs.jpg", "Les rangs au printemps", "Travaux"), ("t", "img/taille.jpg", "Taille de la vigne", "Travaux"),
     ("t", "img/pressoir.jpg", "Le pressoir ancien", "Travaux"), ("f", "img/confiture.jpg", "Préparation des confitures, en commun", "Festivités"),
     ("t", "img/cerises.jpg", "Cerises du verger", "Travaux"), ("c", "img/panneau.jpg", "Le panneau de l'association", "Événements")]
tiles = "".join(f'<a class="tile reveal" href="{src}" data-cat="{c}" data-cap="{cap}"><img src="{src}" alt="{cap}" loading="lazy"><span>{lab}</span></a>' for c, src, cap, lab in G)
pages["galerie.html"] = (head("Galerie photos & vidéos", "La vigne au fil des saisons, les travaux, les vendanges, les festivités et les événements des Coteaux de Chaponost.", "galerie.html") +
hero("img/banquet.jpg", "Photos & vidéos", "La vigne <em>en images</em>", "Travaux, vendanges, festivités, événements.", "short") +
'''<section class="wrap"><p class="note reveal">Photos et vidéo transmises par l'association (aperçu, non définitif). Cet espace accueillera la suite : chaque saison, chaque vendange.</p>
<div class="filters reveal"><button class="on" data-f="all">Tout</button><button data-f="t">Travaux</button><button data-f="v">Vendanges</button><button data-f="f">Festivités</button><button data-f="c">Événements</button><button class="vidbtn" data-f="vid">▶ Vidéos</button></div>
<div class="grid">''' + tiles + '''</div></section>
<section class="wrap">''' + title("Vidéos", "Les vignes en mouvement", "Une première vidéo en ligne ; la taille, les vendanges, le pressage et le banquet suivront.") +
'''<div class="videos"><div class="vid real reveal"><video controls preload="none" poster="img/poster-video.jpg"><source src="img/histoire-du-vin.mp4" type="video/mp4"></video><p>La petite histoire du vin</p></div><div class="vid reveal" style="--bg:url(img/vendanges.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Vendanges — vidéo à venir</p></div><div class="vid reveal" style="--bg:url(img/banquet.jpg)"><button aria-label="Lecture"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button><p>Banquet annuel — vidéo à venir</p></div></div></section>
<div class="lightbox" id="lb"><button class="x" aria-label="Fermer">×</button><img alt=""><p></p></div>''' + FOOT)

# ---------- CONTACT
pages["contact.html"] = (head("Contact", "Contacter les Coteaux de Chaponost par email, Maison des Associations, 1 bis rue Martel, 69630 Chaponost.", "contact.html") +
hero("img/panneau.jpg", "Nous écrire", "<em>Contact</em>", "Une question, une envie de vendanger ? Écrivez-nous.", "short") +
'<section class="wrap split">' + '''<div class="reveal"><p class="kicker">Coordonnées</p><h2>Nous contacter</h2>
<ul class="coords"><li><b>Email</b><a href="mailto:lescoteauxdechaponost@laposte.net">lescoteauxdechaponost@laposte.net</a></li><li><b>Téléphone</b><a href="tel:+33616241682">06 16 24 16 82</a></li><li><b>Siège</b>Maison des Associations<br>1 bis rue Martel<br>69630 Chaponost</li></ul>
<a class="btn" target="_blank" rel="noopener" href="https://www.openstreetmap.org/search?query=1%20bis%20rue%20Martel%2069630%20Chaponost">Voir sur la carte</a></div>
<form class="form paper reveal" name="contact" method="POST" action="merci.html" data-netlify="true" netlify-honeypot="bot"><input type="hidden" name="form-name" value="contact"><p class="hp"><input name="bot"></p>
<label>Nom<input name="nom" required></label><label>Email<input type="email" name="email" required></label><label>Sujet<input name="sujet"></label><label>Message<textarea name="message" rows="5" required></textarea></label><button class="btn" type="submit">Envoyer</button></form></section>''' + FOOT)

# ---------- MERCI / MENTIONS
pages["merci.html"] = (head("Merci", "Message bien reçu.", "") + '<section class="wrap merci"><p class="hand big">Merci !</p><h1>Votre message est bien parti.</h1><p>L\'association vous répondra rapidement.</p><a class="btn" href="index.html">Retour à l\'accueil</a></section>' + FOOT)
pages["mentions-legales.html"] = (head("Mentions légales", "Mentions légales du site des Coteaux de Chaponost.", "") + '''<section class="wrap legalp"><h1>Mentions légales</h1>
<h3>Éditeur</h3><p>Les Coteaux de Chaponost, association loi 1901 — Maison des Associations, 1 bis rue Martel, 69630 Chaponost. Contact : lescoteauxdechaponost@laposte.net. RNA / SIRET : à compléter.</p>
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
