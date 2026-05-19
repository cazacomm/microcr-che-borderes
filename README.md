# Site Le Jardin des Merveilles — Micro-crèche Bordères-sur-l'Échez

Site vitrine statique pour la micro-crèche **Le Jardin des Merveilles** située à Bordères-sur-l'Échez (65370), ouverture juin 2026.

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

Il ne reste que **3 placeholders** à compléter avant mise en ligne :

### 1. Lien de préinscription
Le bouton « Préinscription » (hero accueil) et « Accéder à la plateforme de préinscription » (page contact) pointent vers `href="#"`. Repérables avec l'attribut `data-link="preinscription"`. Remplacer par l'URL réelle de la plateforme.

### 2. Email de contact
L'adresse `contact@lejardindesmerveilles.fr` est utilisée comme placeholder dans `contact.html` et `mentions-legales.html`. À remplacer par l'adresse email officielle.

### 3. Informations légales (mentions-legales.html)
Compléter les balises restantes :
- `[RAISON_SOCIALE]` — raison sociale exacte
- `[FORME_JURIDIQUE]` — SARL, SAS, EURL, etc.
- `[ADRESSE_SIEGE]` — adresse complète du siège social
- `[SIRET]` — numéro SIRET à 14 chiffres
- `[NUMÉRO_TVA si applicable]` — si assujetti à TVA
- `[DIRECTEUR_DE_PUBLICATION]` — nom du directeur de publication
- `[CRÉDITS_PHOTOS]` — crédits photos si applicable

## 📸 Photos à fournir

À déposer dans `assets/images/` (les fichiers HTML pointent déjà vers ces chemins) :

- `directrice.jpg` — portrait de la directrice (carré recommandé, ~600×600px)
- `vie-creche-1.jpg` à `vie-creche-4.jpg` — galerie « La vie à la crèche » (carrés recommandés, ~800×800px)

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
