# Workflow blog — Micro-crèche Le Jardin des Merveilles

Procédure de publication d'un nouvel article sur `www.micro-creche-borderes.fr`.
Site statique HTML/CSS hébergé sur GitHub Pages : **aucun générateur, aucune build**.
Chaque article est une page HTML autonome.

---

## 1. Structure des fichiers

```
/blog/index.html                      → liste des articles
/blog/<slug>/index.html               → un article
/assets/blog.css                      → styles spécifiques au blog (complète css/style.css)
/sitemap.xml                          → à mettre à jour à chaque publication
/rss.xml                              → à mettre à jour à chaque publication
/llms.txt                             → à mettre à jour à chaque publication
/robots.txt                           → ne change plus (crawlers SEO + IA déjà autorisés)
```

**URL canonique du site : `https://www.micro-creche-borderes.fr/`** (avec `www`, avec `https`, telle que définie dans le `CNAME`). Toutes les URL absolues des balises `canonical`, Open Graph, JSON-LD, sitemap et RSS doivent utiliser cette forme exacte.

**Slugs** : minuscules, tirets, sans accent, avec un ancrage local quand c'est pertinent.
Exemple : `adaptation-micro-creche-borderes-sur-lechez`.
Les URL se terminent par un `/` (dossier + `index.html`), jamais par `.html`.

---

## 2. Publier un nouvel article

### Étape 1 — Créer la page

Dupliquer `/blog/adaptation-micro-creche-borderes-sur-lechez/index.html` dans
`/blog/<nouveau-slug>/index.html`, puis remplacer :

- `<title>` (≈ 60 caractères max, avec la ville quand c'est naturel)
- `<meta name="description">` — **strictement moins de 155 caractères**
- `<link rel="canonical">` → nouvelle URL complète
- balises `og:title`, `og:description`, `og:url`, `article:published_time`, `article:modified_time`
- balises `twitter:title`, `twitter:description`
- JSON-LD `Article` : `headline`, `description`, `datePublished`, `dateModified`, `mainEntityOfPage.@id`
- JSON-LD `BreadcrumbList` : 3ᵉ élément (`name` + `item`)
- JSON-LD `FAQPage` : les 5 questions/réponses
- le `<h1>` du hero, le fil d'ariane, la ligne de date, le corps de l'article et le bloc FAQ

> Les blocs header, menu mobile, décors SVG du hero, pré-footer CTA et footer se recopient **tels quels**, sans modification. Ne jamais toucher à `css/style.css`.

### Étape 2 — Référencer l'article dans `/blog/index.html`

Ajouter une carte `.post-card` **en haut** de la grille (ordre antéchronologique) :

```html
<a href="/blog/<slug>/" class="post-card">
  <span class="post-tag">Catégorie</span>
  <h3>Titre de l'article</h3>
  <div class="post-meta"><time datetime="AAAA-MM-JJ">JJ mois AAAA</time> · Lecture X min</div>
  <p class="post-excerpt">Résumé en une à deux phrases.</p>
  <span class="card-cta">Lire l'article <i class="fa-solid fa-arrow-right"></i></span>
</a>
```

### Étape 3 — Mettre à jour les fichiers de diffusion

1. **`sitemap.xml`** : ajouter un bloc `<url>` (`priority` 0.6, `changefreq` monthly) et passer le `lastmod` de `/blog/` à la date du jour.
2. **`rss.xml`** : ajouter un `<item>` en haut de la liste et mettre à jour `lastBuildDate`. Format de date RFC 822 : `Sat, 15 Aug 2026 09:00:00 +0200`.
3. **`llms.txt`** : ajouter la ligne de l'article dans la section « Blog ».

### Étape 4 — Vérifier avant de pousser

- [ ] Toutes les URL absolues sont en `https://www.micro-creche-borderes.fr/...`
- [ ] `meta description` < 155 caractères
- [ ] Un seul `<h1>` par page, hiérarchie H2 / H3 respectée
- [ ] Les trois blocs JSON-LD passent le [Rich Results Test](https://search.google.com/test/rich-results)
- [ ] Les liens internes du blog sont **racine-absolus** (`/index.html`, `/contact.html`), jamais relatifs — le blog est dans un sous-dossier
- [ ] Le NAP est identique partout : *Le Jardin des Merveilles · 6 rue du Colombard, 65320 Bordères-sur-l'Échez · 06 31 00 68 71*
- [ ] Rendu mobile vérifié
- [ ] Après mise en ligne : soumettre l'URL dans la Google Search Console

---

## 3. Règles éditoriales

**Longueur** : 1200 à 1500 mots, plus une FAQ de 5 questions.

**Structure type** : chapô → 4 à 6 `H2` → `H3` en sous-parties → paragraphe de rattachement local → FAQ → CTA.

**Ancrage local** : citer Bordères-sur-l'Échez, et selon le sujet Tarbes, Ibos, les Hautes-Pyrénées ou le bassin tarbais. Au moins une mention naturelle du NAP par article.

**Interdits absolus** — ne jamais écrire sans source validée par la direction :
- montants de tarifs, de participation familiale ou d'aides
- chiffres précis (taux, pourcentages, statistiques, effectifs autres que les 12 places)
- noms de familles ou d'enfants accueillis
- textes réglementaires cités de mémoire (articles de loi, décrets, seuils CAF)
- dates de création, d'agrément ou d'ouverture

En cas de doute : rester qualitatif (« selon votre situation », « renseignez-vous auprès de votre caisse ») et renvoyer vers la page Tarifs ou le contact direct.

**Ton** : bienveillant, concret, accessible. Vouvoiement des parents. Pas de jargon non expliqué.

**Optimisation GEO (moteurs de réponse IA)** : une question = une réponse autoportante dans la FAQ, formulée pour pouvoir être citée hors contexte. Les faits vérifiables (adresse, horaires, âges, nombre de places) doivent apparaître en clair dans le texte, pas seulement dans le JSON-LD.

**Rythme conseillé** : 1 à 2 articles par mois.

---

## 4. Douze sujets d'articles suggérés

| # | Sujet | Angle / intention de recherche |
|---|-------|-------------------------------|
| 1 | Micro-crèche ou assistante maternelle à Bordères-sur-l'Échez : comment choisir | Comparatif des modes de garde, intention « choix » — fort potentiel local |
| 2 | Le déroulé d'une journée type à la micro-crèche, de 7h30 à 18h30 | Rassurer les parents, montrer le quotidien réel |
| 3 | La motricité libre selon Emmi Pikler : ce que cela change au quotidien | Pilier pédagogique, complète la page Pédagogie |
| 4 | Montessori chez les tout-petits : ce que c'est vraiment (et ce que ce n'est pas) | Déconstruction des idées reçues, requête informationnelle forte |
| 5 | Quand commencer ses démarches de garde d'enfant dans les Hautes-Pyrénées | Calendrier d'anticipation, sans citer de délais chiffrés officiels |
| 6 | Le sommeil du tout-petit en collectivité : siestes, rituels et repères | Sujet à très forte recherche parentale |
| 7 | La diversification alimentaire vue depuis la crèche | Conseils pratiques + articulation maison / crèche |
| 8 | Les bienfaits de la petite structure : pourquoi 12 places changent tout | Différenciation concurrentielle assumée |
| 9 | Sorties et activités avec un tout-petit autour de Bordères et Tarbes | Contenu 100 % local, fort potentiel de partage |
| 10 | Langage et communication avant les premiers mots | Signes, babillage, accompagnement du langage |
| 11 | La rentrée en septembre : préparer son enfant et s'organiser en famille | Article saisonnier à republier chaque année |
| 12 | Les questions à poser lors d'une visite de micro-crèche | Checklist parents — excellent aimant à liens et à citations IA |

---

## 5. Commandes utiles

```bash
# Aperçu local
python3 -m http.server 8000
# → http://localhost:8000/blog/

# Publication
git add .
git commit -m "Blog : nouvel article <titre>"
git push origin main
```

GitHub Pages redéploie automatiquement après le push (compter quelques minutes).
