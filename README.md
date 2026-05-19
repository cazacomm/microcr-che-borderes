# Site Micro-crèche Bordères-sur-l'Échez

Site vitrine statique pour une micro-crèche située à Bordères-sur-l'Échez (65370), ouverture juin 2026.

## ✨ Stack

- HTML5 statique (pas de framework, pas de build)
- [Tailwind CSS](https://cdn.tailwindcss.com) via CDN
- [Font Awesome 6.4](https://fontawesome.com/)
- Google Fonts : **Poppins** (corps) + **Quicksand** (titres)
- JavaScript vanilla (smooth scroll, menu mobile)

Hébergement : **GitHub Pages**. Le site fonctionne aussi en local en ouvrant `index.html` directement dans un navigateur.

## 📁 Structure des dossiers

```
.
├── index.html              # Page d'accueil
├── a-propos.html           # Présentation crèche + directrice
├── pedagogie.html          # Projet pédagogique (Montessori/Loczy)
├── tarifs.html             # Forfaits + aides CAF (sans prix affichés)
├── contact.html            # Coordonnées + carte Google Maps
├── mentions-legales.html   # Mentions légales / RGPD
├── bientot-disponible.html # Placeholder pour les autres crèches
├── css/
│   └── style.css           # Styles custom (hero animé, cartes, etc.)
├── js/
│   └── main.js             # Menu mobile, smooth scroll, animations
└── assets/
    └── images/             # Photos du client (à remplir)
```

## 🛠️ Placeholders à remplir manuellement

> Tous ces placeholders sont écrits littéralement dans le code et faciles à retrouver avec un Rechercher/Remplacer.

| Placeholder | Où | Comment remplir |
|---|---|---|
| `[NOM_CRECHE]` | **Toutes les pages** (header, hero, footer, contenus) | Remplacer par le nom commercial définitif de la micro-crèche |
| Lien **Préinscription** | `index.html` (hero) et `contact.html` (gros bouton CTA) — repérables par l'attribut `data-link="preinscription"` | Remplacer le `href="#"` par l'URL réelle de la plateforme de préinscription |
| `[RAISON_SOCIALE]` | `mentions-legales.html` | Raison sociale exacte de l'entité juridique |
| `[FORME_JURIDIQUE]` | `mentions-legales.html` | SARL, SAS, EURL, etc. |
| `[ADRESSE_SIEGE]` | `mentions-legales.html` | Adresse complète du siège social |
| `[SIRET]` | `mentions-legales.html` | Numéro SIRET à 14 chiffres |
| `[NUMÉRO_TVA si applicable]` | `mentions-legales.html` | Si assujetti à TVA |
| `[DIRECTEUR_DE_PUBLICATION]` | `mentions-legales.html` | Nom du directeur de publication |
| `[CRÉDITS_PHOTOS]` | `mentions-legales.html` | Crédits si photos achetées/sous licence |
| Email `contact@[NOM_CRECHE].fr` | `contact.html`, `mentions-legales.html` | Remplacer par l'adresse réelle |

## 📸 Photos à fournir

À déposer dans `assets/images/` (les fichiers HTML pointent déjà vers ces chemins) :

- `directrice.jpg` — portrait de la directrice (carré recommandé, ~600×600px)
- `vie-creche-1.jpg` à `vie-creche-8.jpg` — galerie « La vie à la crèche » (carrés recommandés, ~800×800px)

> Tant que les photos ne sont pas présentes, des icônes Font Awesome s'affichent en fallback automatiquement.

## 🎨 Charte graphique

- **Rose** : `#E8899E` / `#E8556D`
- **Jaune** : `#F5D06C` / `#FFD966`
- **Vert** : `#7FCC7F` / `#5AA85A`
- **Bleu** : `#6BA8CC` / `#4A8AB0`
- **Violet** : `#C89FE6` / `#E6C8FF`
- **Fond** : `#f5f5f5`

## 🚀 Déploiement GitHub Pages

1. Push sur la branche `main`
2. Dans **Settings → Pages**, sélectionner la branche `main` et le dossier `/ (root)`
3. Le site sera disponible à l'URL fournie par GitHub Pages

## 📞 Contact technique

Site conçu par **Caza Comm**.
