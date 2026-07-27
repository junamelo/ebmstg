# Sidebar Rétractable - Documentation

## 📋 Résumé des modifications

La barre de navigation latérale (sidebar) est maintenant **rétractable** avec un bouton de toggle.

## ✨ Fonctionnalités ajoutées

### 1. Bouton de toggle
- **Position** : En haut à droite de la sidebar (flottant sur le bord)
- **Icône** : Chevron gauche/droite qui s'adapte à l'état
- **Effet hover** : Agrandissement léger + changement de couleur

### 2. État rétracté
- **Largeur normale** : 230px
- **Largeur réduite** : 70px
- **Animation** : Transition fluide de 0.3s
- **Contenu masqué** :
  - Labels des liens de navigation
  - Texte du bandeau de rôle
  - Version en bas de page

### 3. État agrandi (par défaut)
- Affichage complet des labels
- Texte du bandeau visible
- Numéro de version visible

### 4. Comportement responsive
- **Tooltips** : Les labels apparaissent au survol quand la sidebar est rétractée
- **Icônes** : Restent toujours visibles et centrées
- **Couleurs d'accentuation** : Conservées selon le rôle (bleu #002a7a ou orange #e05500)

## 🎨 Design

### Bouton de toggle
```css
- Cercle blanc avec bordure grise
- Ombre portée légère
- Position absolue sur le bord droit
- Animation au hover et au clic
```

### Transitions
```css
- Largeur de la sidebar : 0.3s ease
- Opacité des labels : 0.2s ease
- Transformation du bouton : 0.2s ease
```

## 📁 Fichiers modifiés

### `Front/src/components/layout/Sidebar.jsx`
- Ajout du state `collapsed` avec `useState`
- Ajout du composant `IconChevron`
- Ajout du bouton toggle
- Rendu conditionnel des labels et du footer
- Ajout de l'attribut `title` pour les tooltips

### `Front/src/components/layout/Sidebar.css`
- Ajout de la classe `.sidebar.collapsed`
- Styles pour le bouton `.sidebar-toggle`
- Transitions pour les animations
- Gestion du overflow et du whitespace

## 🎯 Utilisation

1. **Réduire la sidebar** : Cliquer sur le bouton chevron (←)
2. **Agrandir la sidebar** : Cliquer sur le bouton chevron (→)
3. **Voir un label** : Survoler une icône quand la sidebar est rétractée

## 🔧 Compatibilité

- ✅ Tous les rôles (Admin, Agent, Payeur, Employé)
- ✅ Toutes les pages
- ✅ Mode light (dark mode non implémenté pour le moment)
- ✅ Préserve les couleurs d'accentuation par rôle

## 🎨 Couleurs utilisées

- **Bouton normal** : Blanc (#ffffff)
- **Bouton hover** : Bleu clair (#f0f4ff)
- **Bordure hover** : Bleu Moov (#002a7a)
- **Ombre** : rgba(0,0,0,0.1)

## 📝 Notes techniques

- Le state `collapsed` est local au composant (non persisté dans localStorage)
- La sidebar se réinitialise à l'état agrandi au rechargement de la page
- Les icônes Tabler Icons sont utilisées pour le chevron
- L'animation est fluide grâce aux transitions CSS

## 🚀 Améliorations futures possibles

1. Persister l'état dans `localStorage` pour le conserver entre les sessions
2. Ajouter un raccourci clavier (ex: Ctrl+B)
3. Mode auto-collapse sur les petits écrans
4. Animation plus sophistiquée (slide + fade)

---

**Date de création** : 23/07/2026  
**Version** : 1.0.0
