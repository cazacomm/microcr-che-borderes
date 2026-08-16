# Génération automatique d'articles

Un article de blog est généré et publié **chaque lundi à 9h00 UTC** par le workflow
`.github/workflows/blog-auto.yml`, qui exécute `scripts/generate-article.py`.

## 1. Ajouter la clé API (à faire une seule fois)

Sur GitHub : **Settings → Secrets and variables → Actions → New repository secret**

| Champ | Valeur |
|-------|--------|
| Name  | `OPENAI_API_KEY` |
| Secret | la clé `sk-...` du compte OpenAI |

Sans ce secret, le workflow échoue proprement avec le message
`OPENAI_API_KEY absent de l'environnement` et **ne publie rien**.

## 2. Lancer une exécution manuelle

Depuis GitHub : onglet **Actions → Blog auto → Run workflow**. Deux options facultatives :

- `topic` : force le numéro de sujet (liste dans `BLOG_WORKFLOW.md`, section 4)
- `dry_run` : simule sans écrire ni publier

En local :

```bash
export OPENAI_API_KEY="sk-..."
pip install openai

python3 scripts/generate-article.py --dry-run     # simulation, aucun fichier écrit
python3 scripts/generate-article.py               # génère et écrit (sans committer)
python3 scripts/generate-article.py --topic 7     # force un sujet précis
python3 scripts/generate-article.py --dry-run --mock  # test hors ligne, sans clé ni réseau
```

Codes de sortie : `0` article généré · `78` aucun nouveau sujet (cas normal, pas d'erreur) · `1` erreur.

## 3. Ce que fait le script

1. lit `blog-config.json` et les 12 sujets du tableau de `BLOG_WORKFLOW.md` ;
2. scanne `/blog/*/index.html`, relève les marqueurs `<!-- micro-creche-borderes-topic: N -->`
   et retient le **premier sujet non traité** dans l'ordre ;
3. relit le gabarit HTML depuis l'article existant rédigé à la main — le template n'est
   jamais dupliqué dans le script, il suit donc automatiquement toute évolution du design ;
4. appelle OpenAI (`gpt-4o-mini`, `temperature` 0.7) en lui transmettant les règles
   éditoriales de `BLOG_WORKFLOW.md` et les seuls faits vérifiés issus de `llms.txt` ;
5. écrit `/blog/<slug>/index.html` (metas, Open Graph, Twitter Card, JSON-LD
   Article + BreadcrumbList + FAQPage régénérés), puis met à jour `blog/index.html`,
   `sitemap.xml` et `rss.xml`.

Header, menu mobile, décors SVG du hero, CTA et footer sont recopiés **à l'identique**
depuis le gabarit. `css/style.css` et `assets/blog.css` ne sont jamais modifiés.

**Idempotence** : un sujet déjà marqué, un slug déjà présent ou un fichier existant
provoquent une sortie en code 78 sans aucune écriture. Rejouer le workflow ne peut pas
écraser un article publié.

## 4. Coût estimé

Un article ≈ 1 500 tokens en entrée et 3 000 en sortie avec `gpt-4o-mini`.
Aux tarifs publics d'OpenAI à date (≈ 0,15 $ / M tokens en entrée, 0,60 $ / M en sortie) :

| Volume | Coût indicatif |
|--------|----------------|
| 1 article | ≈ 0,002 $ |
| 52 articles (1 an) | ≈ 0,11 $ |

Les tarifs OpenAI évoluent : vérifier sur <https://openai.com/api/pricing/>.
Le coût GitHub Actions est nul sur un dépôt public.

## 5. Après épuisement des 12 sujets

Le workflow sort en code 78 sans rien publier. Il suffit d'ajouter des lignes au tableau
de la section 4 de `BLOG_WORKFLOW.md` (même format `| n | Sujet | Angle |`) pour relancer
la production.

## 6. Relecture

Le contenu est publié sans validation humaine : **relire l'article du lundi** est
recommandé, en particulier l'absence de montants, de chiffres précis et de références
réglementaires, que le prompt interdit mais qu'aucun modèle ne garantit à 100 %.
