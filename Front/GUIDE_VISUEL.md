# 🎨 Guide Visuel - Design Moderne Moov Africa e-Billings

## 🎯 Design System Appliqué

### Palette de Couleurs
```
Primaire (Moov Blue)  : #003087 → #0052cc (gradient)
Accent (Moov Orange)  : #FF6600 → #ff8533 (gradient)
Neutrals (Zinc)       : zinc-50 → zinc-950
Success               : Emerald (vert)
Warning               : Amber (orange)
Danger                : Rose (rouge)
```

### Typographie
- **Sans-serif système** : 'Segoe UI', Tahoma, Geneva, Verdana
- **Évite** : Inter (AI default)
- **Hiérarchie** :
  - H1/Hero : `text-3xl md:text-4xl font-bold tracking-tight`
  - H2/Section : `text-2xl font-semibold`
  - Body : `text-sm md:text-base`
  - Small : `text-xs`

### Spacing & Layout
- **Conteneur max** : `max-w-7xl mx-auto`
- **Padding page** : `px-4 md:px-6 py-8`
- **Cards** : `rounded-2xl` (non `rounded-lg` - plus moderne)
- **Gaps** : `gap-4 md:gap-6` (grilles), `gap-2` (listes)

## 📱 Pages Redesignées

### 1. Dashboard Agent Facturation (`/agent/dashboard`)

#### Structure
```
┌─────────────────────────────────────────┐
│  Header: Dashboard Agent Facturation    │
├─────────────────────────────────────────┤
│  Hero Card: Publication du mois         │
│  ┌───────────────────────────────────┐  │
│  │ 1,247 factures        [✓ Traitée]│  │
│  │ Publiée le 12/06/2026            │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  Bento Grid (2x2)                       │
│  ┌──────────┬──────────┐               │
│  │ Alerte   │ Échéance │               │
│  │ Retard   │ Proche   │               │
│  ├──────────┼──────────┤               │
│  │ Contacts │ Réclam.  │               │
│  │ Divers   │ Urgentes │               │
│  └──────────┴──────────┘               │
├─────────────────────────────────────────┤
│  Graphiques (2 colonnes)                │
│  ┌──────────┬──────────┐               │
│  │ Chart 1  │ Chart 2  │               │
│  └──────────┴──────────┘               │
└─────────────────────────────────────────┘
```

#### Éléments Visuels
- **Hero Card** :
  - Gradient subtil (emerald pour succès, amber pour en-cours)
  - Glassmorphism : `backdrop-blur-sm` + border translucide
  - Badge arrondi avec icône (✓ / ⏳ / ✕)
  
- **Bento Grid** :
  - Cards avec `hover:scale-[1.02]` transition
  - Icônes colorées (sans bibliothèque externe)
  - Nombre en grand (`text-4xl font-bold`)
  - Label en petit (`text-sm text-zinc-600`)

- **Animation** :
  - Stagger reveal sur les cards (`delay: idx * 0.05`)
  - Pas de scroll-hijack ni de parallax
  - Smooth hover transitions

#### Couleurs Utilisées
- Background : `bg-zinc-50` (clair) / `dark:bg-zinc-950` (dark mode)
- Cards : `bg-white` avec `border border-zinc-200`
- Accents : Orange Moov sur CTAs, Blue sur liens

### 2. Gestion Forfaits (`/agent/forfaits`)

#### Structure
```
┌─────────────────────────────────────────┐
│  Header: Gestion des Forfaits           │
│  [+ Nouveau Forfait]                    │
├─────────────────────────────────────────┤
│  Tabs: Prépayés | Postpayés             │
├─────────────────────────────────────────┤
│  Table Moderne                          │
│  ┌────┬───────────┬────────┬─────────┐ │
│  │ ID │ Nom       │ Prix   │ Actions │ │
│  ├────┼───────────┼────────┼─────────┤ │
│  │ 1  │ Starter   │ 5000 F │ ✎ 🗑   │ │
│  │ 2  │ Pro       │ 15k F  │ ✎ 🗑   │ │
│  └────┴───────────┴────────┴─────────┘ │
└─────────────────────────────────────────┘
```

#### Éléments Visuels
- **Tabs** :
  - Bordure inférieure sur actif (`border-b-2 border-moov-orange`)
  - Transition douce sur hover
  
- **Table** :
  - Header sticky avec `bg-moov-blue text-white`
  - Rows avec `hover:bg-zinc-50` (pas orange intense)
  - Badge pour statuts (Actif/Inactif)
  - Boutons icônes sans texte (✎ = éditer, 🗑 = supprimer)

- **Modal Création** :
  - Overlay `backdrop-blur-md`
  - Modal centré avec animation scale-in
  - Form avec labels au-dessus des inputs
  - Validation inline (rouge sous input si erreur)

### 3. Gestion Services (`/agent/services`)

#### Structure
```
┌─────────────────────────────────────────┐
│  Header: Gestion des Services           │
├─────────────────────────────────────────┤
│  Grid de Services (2 colonnes)          │
│  ┌─────────────────┬─────────────────┐  │
│  │ No Limit        │ BlackBerry      │  │
│  │ [Toggle ON]     │ [Toggle OFF]    │  │
│  │ 1,234 abonnés   │ 89 abonnés      │  │
│  └─────────────────┴─────────────────┘  │
│  ┌─────────────────┬─────────────────┐  │
│  │ Roaming         │ Bonus Data      │  │
│  │ [Toggle ON]     │ [Toggle ON]     │  │
│  └─────────────────┴─────────────────┘  │
└─────────────────────────────────────────┘
```

#### Éléments Visuels
- **Toggle Switch** :
  - Design iOS-style avec `peer` Tailwind pattern
  - Couleur : zinc (OFF) → emerald (ON)
  - Transition smooth sur le cercle intérieur
  
- **Service Cards** :
  - Icon circulaire en haut (couleur selon status)
  - Nom en gras
  - Nombre d'abonnés en gris
  - Toggle en bas
  - Border change selon status (actif = border-emerald)

### 4. Admin Dashboard (`/admin/dashboard`)

#### Structure
```
┌─────────────────────────────────────────┐
│  Header: Dashboard Super Admin          │
├─────────────────────────────────────────┤
│  Stats Row (4 cards)                    │
│  ┌────┬────┬────┬────┐                  │
│  │ Us │ Fa │ Re │ Se │                  │
│  └────┴────┴────┴────┘                  │
├─────────────────────────────────────────┤
│  Bento Grid (asymétrique)               │
│  ┌──────────────┬──────┐                │
│  │ Large Card   │ Sm 1 │                │
│  │              ├──────┤                │
│  │              │ Sm 2 │                │
│  └──────────────┴──────┘                │
└─────────────────────────────────────────┘
```

#### Éléments Visuels
- **Stats Cards** :
  - Fond blanc avec border subtile
  - Icône colorée à gauche (cercle)
  - Nombre en `text-3xl font-bold`
  - Label en petit sous le nombre
  - Variation du mois en badge (+ vert / - rouge)

- **Bento Asymétrique** :
  - Grid responsive (`grid-cols-1 lg:grid-cols-3`)
  - Première card span-2 (plus large)
  - Petites cards à droite empilées
  - Gradient backgrounds subtils

## 🚫 Anti-Patterns Évités

### ❌ Ne PAS faire
- Em-dashes (`—`) nulle part
- Serif fonts (Fraunces, Instrument Serif)
- Palette beige+brass (premium-consumer cliché)
- 3 cards égales horizontales (générique)
- Centered hero avec gradient mesh
- `h-screen` (utiliser `min-h-[100dvh]`)
- Eyebrows partout (`uppercase tracking-widest` sur chaque section)
- Section numbering (`01 / 02 / 03`)
- Pills overlaid sur images
- Scroll cues (`↓ Scroll`)
- Decoration text strips (`BRAND. MOTION. SPATIAL.`)

### ✅ Patterns Utilisés
- **Bento Grid** pour layout non-uniforme
- **Glassmorphism** subtil (pas excessif)
- **Stagger animations** sur entrée
- **Hover micro-interactions** (`scale-[1.02]`, `translate-y-[-2px]`)
- **Badges sémantiques** (couleur = sens)
- **Tables modernes** (sticky header, hover rows)
- **Form avec validation inline**
- **Mobile-first** responsive

## 📐 Responsive Breakpoints

```css
/* Tailwind breakpoints utilisés */
sm:  640px  /* Mobile landscape */
md:  768px  /* Tablet portrait */
lg:  1024px /* Tablet landscape / Desktop */
xl:  1280px /* Desktop large */
2xl: 1536px /* Desktop XL */
```

### Stratégie Mobile
- **< 768px** : Tout en colonne unique (`grid-cols-1`)
- **768-1024px** : 2 colonnes (`md:grid-cols-2`)
- **> 1024px** : 3-4 colonnes (`lg:grid-cols-3`)

## 🎭 Dark Mode (préparé, non activé)

Les pages utilisent `dark:` variants Tailwind :
```jsx
className="bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white"
```

**Pour activer** :
1. Ajouter toggle dans layout
2. Ajouter `class` à `<html>`
3. Les styles s'adapteront automatiquement

## 🔍 Comment Vérifier si ça Marche

### Checklist Visuelle
- [ ] Les cards ont des coins arrondis (`rounded-2xl`)
- [ ] Les boutons ont un hover effect (translation ou scale)
- [ ] Les couleurs Moov (orange/bleu) sont présentes
- [ ] Les textes ont une hiérarchie claire (gras/normal, grand/petit)
- [ ] Les icônes sont des SVG inline (pas d'images externes)
- [ ] Les tables ont un header bleu foncé avec texte blanc
- [ ] Les badges ont des backgrounds colorés et translucides
- [ ] Le layout est responsive (rétrécir la fenêtre)

### Si ça ne ressemble PAS à ça
1. **Tailwind ne charge pas** → Vérifier console, rebuild
2. **CSS conflits** → Les anciennes classes CSS override Tailwind
3. **Motion ne charge pas** → Vérifier import `motion/react`

---

**Exemple de code type** :
```jsx
<div className="min-h-[100dvh] bg-zinc-50 dark:bg-zinc-950">
  <div className="max-w-7xl mx-auto px-4 md:px-6 py-8">
    <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-8">
      Dashboard
    </h1>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, idx) => (
        <motion.div
          key={stat.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800 hover:scale-[1.02] transition-transform"
        >
          <p className="text-sm text-zinc-600 dark:text-zinc-400">{stat.label}</p>
          <p className="text-4xl font-bold text-zinc-900 dark:text-white mt-2">
            {stat.value}
          </p>
        </motion.div>
      ))}
    </div>
  </div>
</div>
```

---

**Dernière mise à jour** : 2026-07-13
**Design System** : Moov Africa + Tailwind v3 + Motion
