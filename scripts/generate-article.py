#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération automatique d'un article de blog.

Principe (identique au setup Adesign) :
  - le gabarit HTML n'est PAS dupliqué dans ce script : il est relu à chaque
    exécution depuis un article déjà publié dans /blog/ ;
  - seules les zones de contenu sont remplacées (title, metas, JSON-LD, hero,
    fil d'ariane, corps, FAQ) ; header, décors SVG, CTA et footer sont conservés
    tels quels ;
  - un marqueur <!-- <site-slug>-topic: N --> rend l'opération idempotente.

Codes de sortie :
    0  -> un article a été généré (ou simulé en --dry-run)
    1  -> erreur
   78  -> aucun nouveau sujet à traiter (rien à faire, ce n'est pas une erreur)
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "blog-config.json")
WORKFLOW_PATH = os.path.join(ROOT, "BLOG_WORKFLOW.md")
BLOG_DIR = os.path.join(ROOT, "blog")
BLOG_INDEX = os.path.join(BLOG_DIR, "index.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
RSS = os.path.join(ROOT, "rss.xml")

EXIT_OK, EXIT_ERROR, EXIT_NOTHING = 0, 1, 78

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]


def log(msg):
    print(msg, flush=True)


class Fail(Exception):
    """Erreur bloquante : on sort proprement, sans rien écrire."""


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

# Mots vides retirés des slugs. « sur » est volontairement conservé : il fait
# partie du nom de la commune (Bordères-sur-l'Échez).
SLUG_STOPWORDS = {
    "a", "au", "aux", "avec", "ce", "cette", "comment", "dans", "de", "des",
    "du", "elle", "en", "et", "il", "l", "la", "le", "les", "leur", "ou",
    "pour", "qu", "que", "qui", "quoi", "sa", "ses", "son", "un", "une", "vos",
    "votre", "y",
}


def slugify(text, max_words=9, drop_stopwords=True):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("'", " ").replace("’", " ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    words = [w for w in text.split("-") if w]
    if drop_stopwords:
        # on retire aussi les lettres isolées issues des élisions (d'une, l'enfant…)
        kept = [w for w in words
                if w not in SLUG_STOPWORDS and not (len(w) == 1 and w.isalpha())]
        words = kept or words
    words = words[:max_words]
    while words and words[-1] in SLUG_STOPWORDS:
        words.pop()
    return "-".join(words)


def site_slug(config):
    """Identifiant court du site, déduit de l'URL de prod (sert au marqueur)."""
    host = re.sub(r"^https?://", "", config["site_url"]).split("/")[0]
    host = re.sub(r"^www\.", "", host)
    return slugify(host.rsplit(".", 1)[0], max_words=10, drop_stopwords=False)


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def date_fr(d):
    return "%d %s %d" % (d.day, MOIS_FR[d.month - 1], d.year)


def clamp_description(text, limit=154):
    """La meta description doit rester sous 155 caractères."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,;:—-") + "."


def word_count(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


# ---------------------------------------------------------------------------
# Lecture de la configuration et des sujets
# ---------------------------------------------------------------------------

def load_config():
    if not os.path.isfile(CONFIG_PATH):
        raise Fail("blog-config.json introuvable à la racine du dépôt.")
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    required = ["site_name", "site_url", "sector", "location", "author",
                "target_word_count", "faq_questions_count", "language"]
    missing = [k for k in required if k not in config]
    if missing:
        raise Fail("blog-config.json : clés manquantes -> %s" % ", ".join(missing))
    config["site_url"] = config["site_url"].rstrip("/")
    return config


def load_topics():
    """Extrait les sujets du tableau markdown de BLOG_WORKFLOW.md."""
    if not os.path.isfile(WORKFLOW_PATH):
        raise Fail("BLOG_WORKFLOW.md introuvable : impossible de lister les sujets.")
    topics = []
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", line)
            if m:
                topics.append({
                    "n": int(m.group(1)),
                    "title": m.group(2).strip(),
                    "angle": m.group(3).strip(),
                })
    if not topics:
        raise Fail("Aucun sujet trouvé dans BLOG_WORKFLOW.md (tableau attendu).")
    topics.sort(key=lambda t: t["n"])
    return topics


def load_editorial_rules():
    """Récupère la section 'Règles éditoriales' pour la transmettre au modèle."""
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"##\s*3\.\s*Règles éditoriales(.*?)\n---", content, re.S)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Analyse du blog existant
# ---------------------------------------------------------------------------

def scan_existing(config):
    """Retourne (slugs existants, numéros de sujets déjà traités)."""
    slugs, done = set(), set()
    marker_re = re.compile(r"<!--\s*%s-topic:\s*(\d+)\s*-->" % re.escape(site_slug(config)))
    if not os.path.isdir(BLOG_DIR):
        raise Fail("Le dossier /blog/ est introuvable.")
    for name in sorted(os.listdir(BLOG_DIR)):
        page = os.path.join(BLOG_DIR, name, "index.html")
        if not os.path.isfile(page):
            continue
        slugs.add(name)
        with open(page, encoding="utf-8") as f:
            m = marker_re.search(f.read())
        if m:
            done.add(int(m.group(1)))
    return slugs, done


def pick_template(config):
    """
    Choisit l'article de référence dont on relit le gabarit.
    On privilégie un article rédigé à la main (sans marqueur d'automatisation),
    à défaut le premier article par ordre alphabétique.
    """
    marker_re = re.compile(r"<!--\s*%s-topic:" % re.escape(site_slug(config)))
    candidates = []
    for name in sorted(os.listdir(BLOG_DIR)):
        page = os.path.join(BLOG_DIR, name, "index.html")
        if os.path.isfile(page):
            with open(page, encoding="utf-8") as f:
                candidates.append((name, page, bool(marker_re.search(f.read()))))
    if not candidates:
        raise Fail("Aucun article existant dans /blog/ : gabarit introuvable.")
    handwritten = [c for c in candidates if not c[2]]
    name, page, _ = (handwritten or candidates)[0]
    log("  gabarit relu depuis : blog/%s/index.html" % name)
    return page


# ---------------------------------------------------------------------------
# Appel OpenAI
# ---------------------------------------------------------------------------

SCHEMA_HINT = """Réponds UNIQUEMENT par un objet JSON valide, sans balise markdown, de la forme :
{
  "title": "titre de l'article, 55 à 70 caractères, avec la ville si c'est naturel",
  "subtitle": "sous-titre court affiché sous le titre (6 à 12 mots)",
  "meta_description": "résumé de 140 à 152 caractères maximum",
  "excerpt": "résumé de 20 à 35 mots pour la carte de la page liste",
  "tag": "catégorie courte, 1 à 3 mots",
  "reading_time": 6,
  "lead": "chapô d'introduction de 45 à 70 mots",
  "sections": [
    {
      "h2": "titre de section",
      "blocks": [
        {"type": "p", "text": "paragraphe"},
        {"type": "h3", "text": "sous-titre"},
        {"type": "ul", "items": ["puce 1", "puce 2"]},
        {"type": "note", "text": "encadré À retenir, au maximum une fois dans l'article"}
      ]
    }
  ],
  "faq": [{"question": "...", "answer": "réponse autoportante de 45 à 90 mots"}]
}"""


def build_prompt(config, topic, facts, rules):
    system = (
        "Tu es rédacteur web SEO spécialisé dans la petite enfance. "
        "Tu écris en français, au ton %s. "
        "Tu n'inventes JAMAIS de prix, de montants, de pourcentages, de statistiques, "
        "de noms de personnes ou de familles, de dates de création ou d'agrément, "
        "ni de références réglementaires (articles de loi, décrets, seuils CAF). "
        "En cas de doute tu restes qualitatif et tu renvoies vers un contact direct. "
        "Tu n'utilises que les faits vérifiés qui te sont fournis."
        % config["tone"]
    )
    user = f"""Rédige un article de blog pour le site de {config['site_name']}
({config['sector']}), établi à {config['location']}.

SUJET IMPOSÉ : {topic['title']}
ANGLE : {topic['angle']}

FAITS VÉRIFIÉS (les seuls chiffres et données autorisés) :
{facts}

MOTS-CLÉS D'ANCRAGE LOCAL (à intégrer naturellement, sans bourrage) :
{', '.join(config.get('geo_keywords', []))}

CONTRAINTES :
- environ {config['target_word_count']} mots pour le corps de l'article (hors FAQ), avec une tolérance de 15 %
- 4 à 6 sections H2, chacune pouvant contenir des H3
- au moins une liste à puces et au maximum un encadré "note"
- exactement {config['faq_questions_count']} questions de FAQ, chaque réponse devant se suffire à elle-même si elle est citée hors contexte
- au moins une mention naturelle de la ville et une du nom de la structure
- pas de conclusion générique : terminer par un paragraphe utile invitant au contact
- vouvoiement des parents, pas de jargon non expliqué
- ne pas répéter le titre en début de chapô

RÈGLES ÉDITORIALES DU SITE (à respecter strictement) :
{rules}

{SCHEMA_HINT}"""
    return system, user


def call_openai(config, topic, facts, rules):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Fail("OPENAI_API_KEY absent de l'environnement.")
    try:
        from openai import OpenAI
    except ImportError:
        raise Fail("Le paquet 'openai' n'est pas installé (pip install openai).")

    system, user = build_prompt(config, topic, facts, rules)
    log("  appel OpenAI (gpt-4o-mini, temperature 0.7)...")
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        )
        raw = resp.choices[0].message.content
    except Exception as exc:
        raise Fail("Appel OpenAI en échec : %s" % exc)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Fail("Réponse OpenAI illisible (JSON invalide) : %s" % exc)
    return data


def mock_payload(config, topic):
    """Contenu de démonstration : sert au test hors ligne (--mock)."""
    ville = config["location"].split(",")[0]
    para = ("Cette section détaille, exemples concrets à l'appui, ce que les familles "
            "de %s observent au quotidien et la manière dont l'équipe de %s accompagne "
            "chaque enfant à son rythme, sans jamais forcer les étapes." % (ville, config["site_name"]))
    return {
        "title": topic["title"],
        "subtitle": "Repères pratiques pour les familles",
        "meta_description": "%s : conseils pratiques de la micro-crèche Le Jardin des Merveilles à %s (65)." % (topic["title"], ville),
        "excerpt": "Un tour d'horizon concret du sujet, avec les repères utiles aux parents et les réponses aux questions les plus fréquentes.",
        "tag": "Conseils parents",
        "reading_time": 6,
        "lead": "Contenu de démonstration généré hors ligne pour valider la chaîne de publication. "
                "En production, ce chapô est rédigé par le modèle à partir du sujet et des faits vérifiés.",
        "sections": [
            {"h2": "Premier axe du sujet", "blocks": [
                {"type": "p", "text": para},
                {"type": "h3", "text": "Un point de détail"},
                {"type": "p", "text": para},
            ]},
            {"h2": "Deuxième axe du sujet", "blocks": [
                {"type": "ul", "items": ["Premier repère pratique.",
                                         "Deuxième repère pratique.",
                                         "Troisième repère pratique."]},
                {"type": "note", "text": "Le déroulé précis se construit toujours avec l'équipe, selon le rythme de l'enfant."},
            ]},
            {"h2": "En pratique à %s" % ville, "blocks": [{"type": "p", "text": para}]},
        ],
        "faq": [{"question": "Question de démonstration n°%d ?" % i,
                 "answer": "Réponse de démonstration, autoportante, telle qu'elle serait rédigée en production par le modèle."}
                for i in range(1, config["faq_questions_count"] + 1)],
    }


def validate_payload(config, data):
    for key in ("title", "meta_description", "lead", "sections", "faq"):
        if not data.get(key):
            raise Fail("Réponse du modèle incomplète : champ '%s' manquant." % key)
    if not isinstance(data["sections"], list) or not data["sections"]:
        raise Fail("Réponse du modèle : 'sections' vide.")
    if len(data["faq"]) != config["faq_questions_count"]:
        log("  ! FAQ : %d questions reçues au lieu de %d, ajustement."
            % (len(data["faq"]), config["faq_questions_count"]))
        data["faq"] = data["faq"][:config["faq_questions_count"]]
        if not data["faq"]:
            raise Fail("Réponse du modèle : FAQ vide.")
    for item in data["faq"]:
        if not item.get("question") or not item.get("answer"):
            raise Fail("Réponse du modèle : une entrée de FAQ est incomplète.")
    data["meta_description"] = clamp_description(data["meta_description"])
    data.setdefault("subtitle", config["location"].split(",")[0])
    data.setdefault("tag", "Conseils parents")
    data.setdefault("excerpt", data["meta_description"])
    try:
        data["reading_time"] = max(3, int(data.get("reading_time") or 6))
    except (TypeError, ValueError):
        data["reading_time"] = 6
    return data


# ---------------------------------------------------------------------------
# Rendu HTML (sur la base du gabarit relu)
# ---------------------------------------------------------------------------

def render_body(data):
    out = ['<p class="post-lead">%s</p>' % esc(data["lead"])]
    for section in data["sections"]:
        if section.get("h2"):
            out.append("<h2>%s</h2>" % esc(section["h2"]))
        for block in section.get("blocks", []):
            kind = block.get("type")
            if kind == "h3" and block.get("text"):
                out.append("<h3>%s</h3>" % esc(block["text"]))
            elif kind == "p" and block.get("text"):
                out.append("<p>%s</p>" % esc(block["text"]))
            elif kind == "ul" and block.get("items"):
                items = "".join("\n            <li>%s</li>" % esc(i) for i in block["items"])
                out.append("<ul>%s\n          </ul>" % items)
            elif kind == "note" and block.get("text"):
                out.append('<div class="post-note">\n            <p><strong>À retenir :</strong> %s</p>\n          </div>'
                           % esc(block["text"]))
    inner = "\n\n          ".join(out)
    return '<article class="post-body">\n\n          %s\n\n        </article>' % inner


def render_faq(data):
    out = ['<h2 class="title-green mt-14">Questions fréquentes des parents</h2>']
    for item in data["faq"]:
        out.append('<div class="faq-item">\n          <h3>%s</h3>\n          <p>%s</p>\n        </div>'
                   % (esc(item["question"]), esc(item["answer"])))
    return "\n\n        ".join(out) + "\n\n        "


def replace_meta(html, pattern, value):
    new, n = re.subn(pattern, lambda m: m.group(1) + value + m.group(3), html, count=1)
    if n == 0:
        raise Fail("Gabarit inattendu : balise introuvable (%s)." % pattern[:60])
    return new


def rewrite_jsonld(html, data, config, url, today, breadcrumb_name):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if len(blocks) < 3:
        raise Fail("Gabarit inattendu : 3 blocs JSON-LD attendus, %d trouvé(s)." % len(blocks))
    iso = today.isoformat()

    def rebuild(raw):
        obj = json.loads(raw)
        kind = obj.get("@type")
        if kind == "Article":
            obj["headline"] = data["title"]
            obj["description"] = data["meta_description"]
            obj["datePublished"] = iso
            obj["dateModified"] = iso
            obj["mainEntityOfPage"]["@id"] = url
        elif kind == "BreadcrumbList":
            last = obj["itemListElement"][-1]
            last["name"] = breadcrumb_name
            last["item"] = url
        elif kind == "FAQPage":
            obj["mainEntity"] = [
                {"@type": "Question", "name": item["question"],
                 "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}}
                for item in data["faq"]
            ]
        else:
            return None
        return json.dumps(obj, ensure_ascii=False, indent=2)

    for raw in blocks:
        rebuilt = rebuild(raw)
        if rebuilt is None:
            continue
        indented = "\n".join(("  " + l if l.strip() else l) for l in rebuilt.splitlines())
        html = html.replace(
            '<script type="application/ld+json">%s</script>' % raw,
            '<script type="application/ld+json">\n%s\n  </script>' % indented,
            1)
    return html


def build_article_html(template_html, data, config, slug, topic_n, today):
    url = "%s/blog/%s/" % (config["site_url"], slug)
    iso = today.isoformat()
    title = data["title"]
    breadcrumb_name = title if len(title) <= 60 else title[:57].rsplit(" ", 1)[0] + "…"

    html = template_html
    html = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % esc(title), html, count=1, flags=re.S)
    html = replace_meta(html, r'(<meta name="description" content=")(.*?)(">)', esc(data["meta_description"]))
    html = replace_meta(html, r'(<link rel="canonical" href=")(.*?)(">)', url)
    html = replace_meta(html, r'(<meta property="og:title" content=")(.*?)(">)', esc(title))
    html = replace_meta(html, r'(<meta property="og:description" content=")(.*?)(">)', esc(data["meta_description"]))
    html = replace_meta(html, r'(<meta property="og:url" content=")(.*?)(">)', url)
    html = replace_meta(html, r'(<meta property="article:published_time" content=")(.*?)(">)', iso)
    html = replace_meta(html, r'(<meta property="article:modified_time" content=")(.*?)(">)', iso)
    html = replace_meta(html, r'(<meta name="twitter:title" content=")(.*?)(">)', esc(breadcrumb_name))
    html = replace_meta(html, r'(<meta name="twitter:description" content=")(.*?)(">)', esc(data["meta_description"]))

    html = rewrite_jsonld(html, data, config, url, today, breadcrumb_name)

    # Hero : h1 + sous-titre
    html = re.sub(r"<h1>.*?</h1>", lambda m: "<h1>%s</h1>" % esc(title), html, count=1, flags=re.S)
    html = re.sub(r'<p class="subtitle">.*?</p>',
                  lambda m: '<p class="subtitle">%s</p>' % esc(data["subtitle"]),
                  html, count=1, flags=re.S)

    # Fil d'ariane
    html = re.sub(
        r'(<nav class="blog-breadcrumb" aria-label="Fil d\'ariane">).*?(</nav>)',
        lambda m: ('%s\n          <a href="/index.html">Accueil</a> <span>›</span> '
                   '<a href="/blog/">Blog</a> <span>›</span> %s\n        %s'
                   % (m.group(1), esc(breadcrumb_name), m.group(2))),
        html, count=1, flags=re.S)

    # Ligne de date
    html = re.sub(
        r'<p class="post-meta-line">.*?</p>',
        lambda m: ('<p class="post-meta-line">\n          Publié le <time datetime="%s">%s</time> · %s · Lecture %d min\n        </p>'
                   % (iso, date_fr(today), esc(config["site_name"]), data["reading_time"])),
        html, count=1, flags=re.S)

    # Corps
    body = render_body(data)
    html, n = re.subn(r'<article class="post-body">.*?</article>', lambda m: body, html, count=1, flags=re.S)
    if n == 0:
        raise Fail("Gabarit inattendu : bloc <article class=\"post-body\"> introuvable.")

    # FAQ
    faq = render_faq(data)
    html, n = re.subn(r'<h2 class="title-green mt-14">.*?(?=<div class="post-back">)',
                      lambda m: faq, html, count=1, flags=re.S)
    if n == 0:
        raise Fail("Gabarit inattendu : bloc FAQ introuvable.")

    # Marqueur d'idempotence
    marker = "<!-- %s-topic: %d -->" % (site_slug(config), topic_n)
    html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n%s" % marker, 1)
    return html


# ---------------------------------------------------------------------------
# Mise à jour des fichiers annexes
# ---------------------------------------------------------------------------

def update_blog_index(data, slug, today, dry_run):
    with open(BLOG_INDEX, encoding="utf-8") as f:
        html = f.read()
    href = "/blog/%s/" % slug
    if 'href="%s"' % href in html:
        log("  = carte déjà présente dans blog/index.html")
        return
    anchor = '<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">'
    if anchor not in html:
        raise Fail("blog/index.html : grille d'articles introuvable.")
    card = ('%s\n\n          <a href="%s" class="post-card">\n'
            '            <span class="post-tag">%s</span>\n'
            '            <h3>%s</h3>\n'
            '            <div class="post-meta"><time datetime="%s">%s</time> · Lecture %d min</div>\n'
            '            <p class="post-excerpt">%s</p>\n'
            '            <span class="card-cta">Lire l\'article <i class="fa-solid fa-arrow-right"></i></span>\n'
            '          </a>\n'
            % (anchor, href, esc(data["tag"]), esc(data["title"]),
               today.isoformat(), date_fr(today), data["reading_time"], esc(data["excerpt"])))
    html = html.replace(anchor, card, 1)
    if not dry_run:
        with open(BLOG_INDEX, "w", encoding="utf-8") as f:
            f.write(html)
    log("  + carte ajoutée dans blog/index.html")


def update_sitemap(config, slug, today, dry_run):
    url = "%s/blog/%s/" % (config["site_url"], slug)
    with open(SITEMAP, encoding="utf-8") as f:
        xml = f.read()
    if "<loc>%s</loc>" % url in xml:
        log("  = URL déjà présente dans sitemap.xml")
        return
    iso = today.isoformat()
    entry = ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
             "    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n</urlset>"
             % (url, iso))
    if "</urlset>" not in xml:
        raise Fail("sitemap.xml : balise </urlset> introuvable.")
    xml = xml.replace("</urlset>", entry, 1)
    # rafraîchit le lastmod de la page liste du blog
    xml = re.sub(r"(<loc>%s/blog/</loc>\s*<lastmod>)[^<]+(</lastmod>)" % re.escape(config["site_url"]),
                 lambda m: m.group(1) + iso + m.group(2), xml, count=1)
    ET.fromstring(xml)
    if not dry_run:
        with open(SITEMAP, "w", encoding="utf-8") as f:
            f.write(xml)
    log("  + URL ajoutée dans sitemap.xml")


def update_rss(config, data, slug, today, dry_run):
    url = "%s/blog/%s/" % (config["site_url"], slug)
    with open(RSS, encoding="utf-8") as f:
        xml = f.read()
    if "<link>%s</link>" % url in xml:
        log("  = article déjà présent dans rss.xml")
        return
    stamp = dt.datetime(today.year, today.month, today.day, 9, 0, 0).strftime(
        "%a, %d %b %Y %H:%M:%S +0000")
    item = ('    <item>\n'
            '      <title>%s</title>\n'
            '      <link>%s</link>\n'
            '      <guid isPermaLink="true">%s</guid>\n'
            '      <pubDate>%s</pubDate>\n'
            '      <description>%s</description>\n'
            '    </item>\n\n'
            % (esc(data["title"]), url, url, stamp, esc(data["excerpt"])))
    anchor = re.search(r'\n(\s*)<item>', xml)
    if anchor:
        xml = xml[:anchor.start() + 1] + item + xml[anchor.start() + 1:]
    else:
        xml = xml.replace("  </channel>", item + "  </channel>", 1)
    xml = re.sub(r"(<lastBuildDate>)[^<]+(</lastBuildDate>)",
                 lambda m: m.group(1) + stamp + m.group(2), xml, count=1)
    ET.fromstring(xml)
    if not dry_run:
        with open(RSS, "w", encoding="utf-8") as f:
            f.write(xml)
    log("  + item ajouté dans rss.xml")


# ---------------------------------------------------------------------------
# Faits vérifiés (extraits de llms.txt, jamais inventés)
# ---------------------------------------------------------------------------

def load_facts():
    path = os.path.join(ROOT, "llms.txt")
    if not os.path.isfile(path):
        return "(aucun fait complémentaire disponible : rester strictement qualitatif)"
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"##\s*Identité et coordonnées.*?\n(.*?)\n##", content, re.S)
    block = m.group(1).strip() if m else ""
    intro = re.search(r"^>\s?(.*?)(?:\n\n|\n#)", content, re.S | re.M)
    if intro:
        block = re.sub(r"^>\s?", "", intro.group(1), flags=re.M).strip() + "\n\n" + block
    return block


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Génère un article de blog.")
    parser.add_argument("--dry-run", action="store_true",
                        help="génère et affiche sans écrire aucun fichier")
    parser.add_argument("--mock", action="store_true",
                        help="contenu de démonstration hors ligne, sans appel OpenAI")
    parser.add_argument("--topic", type=int, default=None,
                        help="force le numéro de sujet à traiter")
    args = parser.parse_args()

    log("=== Génération d'article — %s ===" % dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    if args.dry_run:
        log("MODE DRY-RUN : aucun fichier ne sera écrit.")

    config = load_config()
    log("Site : %s (%s)" % (config["site_name"], config["site_url"]))

    topics = load_topics()
    slugs, done = scan_existing(config)
    log("Sujets disponibles : %d — articles publiés : %d — sujets déjà traités : %s"
        % (len(topics), len(slugs), sorted(done) or "aucun"))

    if args.topic is not None:
        topic = next((t for t in topics if t["n"] == args.topic), None)
        if topic is None:
            raise Fail("Sujet n°%d absent de BLOG_WORKFLOW.md." % args.topic)
    else:
        topic = next((t for t in topics if t["n"] not in done), None)

    if topic is None:
        log("Aucun sujet non traité : rien à publier. Ajoutez des sujets dans BLOG_WORKFLOW.md.")
        return EXIT_NOTHING

    slug = slugify(topic["title"])
    log("Sujet retenu : n°%d — %s" % (topic["n"], topic["title"]))
    log("Slug : %s" % slug)

    if slug in slugs:
        log("L'article blog/%s/ existe déjà : rien à faire (pas de réécriture)." % slug)
        return EXIT_NOTHING

    target_dir = os.path.join(BLOG_DIR, slug)
    target = os.path.join(target_dir, "index.html")
    if os.path.exists(target):
        log("Le fichier %s existe déjà : abandon sans modification." % target)
        return EXIT_NOTHING

    template_path = pick_template(config)
    with open(template_path, encoding="utf-8") as f:
        template_html = f.read()

    facts = load_facts()
    rules = load_editorial_rules()

    if args.mock:
        log("  mode --mock : contenu de démonstration, aucun appel réseau.")
        data = mock_payload(config, topic)
    else:
        data = call_openai(config, topic, facts, rules)
    data = validate_payload(config, data)

    today = dt.date.today()
    html = build_article_html(template_html, data, config, slug, topic["n"], today)

    words = word_count(re.search(r'<article class="post-body">.*?</article>', html, re.S).group(0))
    log("  titre : %s" % data["title"])
    log("  corps : %d mots (cible %d)" % (words, config["target_word_count"]))
    if not 900 <= words <= 2000:
        log("  ! volume inhabituel : à relire manuellement.")

    if args.dry_run:
        log("--- APERÇU (dry-run, rien n'a été écrit) ---")
        preview = re.sub(r"<[^>]+>", " ", re.search(r'<article class="post-body">.*?</article>', html, re.S).group(0))
        log(" ".join(preview.split())[:1200])
        update_blog_index(data, slug, today, dry_run=True)
        update_sitemap(config, slug, today, dry_run=True)
        update_rss(config, data, slug, today, dry_run=True)
        log("--- FIN DRY-RUN ---")
        return EXIT_OK

    os.makedirs(target_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)
    log("  + blog/%s/index.html écrit" % slug)

    update_blog_index(data, slug, today, dry_run=False)
    update_sitemap(config, slug, today, dry_run=False)
    update_rss(config, data, slug, today, dry_run=False)

    log("Article publié : %s/blog/%s/" % (config["site_url"], slug))
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as exc:
        print("ERREUR : %s" % exc, file=sys.stderr, flush=True)
        sys.exit(EXIT_ERROR)
    except Exception as exc:  # filet de sécurité : jamais de commit sur une erreur inattendue
        print("ERREUR INATTENDUE : %r" % exc, file=sys.stderr, flush=True)
        sys.exit(EXIT_ERROR)
