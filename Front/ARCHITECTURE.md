# 🏗️ Architecture e-Billings Moov Africa

## 🎨 Design System

**Brief :** Internal B2B product dashboard for telecom billing operations  
**Aesthetic :** Professional SaaS + Moov brand identity  
**Dials :** `DESIGN_VARIANCE: 6` | `MOTION_INTENSITY: 4` | `VISUAL_DENSITY: 6`

### Color Palette
- **Primary Blue :** `#002a7a` → `#003087` (gradient)
- **Accent Orange :** `#e05500` → `#f08020`
- **Neutrals :** Zinc scale (`zinc-50` → `zinc-950`)
- **Semantic :** Emerald (success), Rose (danger), Amber (warning)

### Typography
- **Font :** System sans-serif (pas Inter par défaut, éviter AI-slop)
- **Display :** `text-3xl font-bold tracking-tight`
- **Body :** `text-base text-zinc-600 dark:text-zinc-400`
- **Mono :** Pour les montants/chiffres uniquement

### Motion
- **Library :** Motion (`motion/react`)
- **Transitions :** `duration: 0.4-0.5s`, `ease: [0.16, 1, 0.3, 1]` (custom cubic-bezier)
- **Stagger :** `delay: idx * 0.05` pour les listes
- **Reduced motion :** Respecté automatiquement par Motion

---

## 🗂️ Structure des routes

### `/` — Routes communes (Employé + Payeur)
```
/dashboard    → Dashboard selon rôle (DashboardEmploye | DashboardPayeur)
/factures     → Liste des factures
/simulation   → Simulation facturation
```

### `/agent/*` — Agent Facturation
```
/agent/dashboard    → Stats publication + alertes
/agent/publication  → Upload PDF + découpage
/agent/forfaits     → Gestion forfaits (tarifs simulation)
/agent/services     → Gestion services (No Limit, BlackBerry, Incognito...)
```

### `/admin/*` — Super Admin
```
/admin/dashboard → Stats plateforme globales
/admin/comptes   → Gestion utilisateurs
```

---

## 👥 Rôles et permissions

| Rôle | Accès | Redirect après login |
|------|-------|---------------------|
| **EMPLOYE** | `/dashboard`, `/factures`, `/simulation` | `/dashboard` |
| **PAYEUR** | `/dashboard`, `/factures`, `/simulation` | `/dashboard` |
| **AGENT_FACTURATION** | `/agent/*` | `/agent/dashboard` |
| **SUPER_ADMIN** | `/admin/*` | `/admin/dashboard` |

---

## 📁 Fichiers clés

### Nouveaux fichiers créés
```
Front/src/pages/agent/
  ├── AgentDashboard.jsx       (✨ moderne, bento grid, glassmorphism subtil)
  ├── PublicationPdf.jsx        (déplacé depuis /admin)
  ├── GestionForfaits.jsx       (✨ nouvelle page, formulaire moderne)
  └── GestionServices.jsx       (✨ nouvelle page, bento grid services)

Front/src/pages/admin/
  └── AdminDashboard.jsx        (✨ refonte moderne complète)
```

### Fichiers modifiés
```
Front/src/App.jsx                         (routing /agent/* + /admin/*)
Front/src/contexts/AuthContext.jsx        (ajout isAgentFacturation())
Front/src/components/common/ProtectedRoute.jsx  (rôle AGENT_FACTURATION)
Front/src/pages/auth/Login.jsx            (redirect selon rôle)
Front/src/services/adminService.js        (getStatsAgentFacturation)
Front/src/services/mockApi.js             (mock agent stats)
Front/src/services/mockData.js            (user agent + stats)
```

---

## 🎯 Ce qui reste à faire

### Phase 2 : Moderniser les dashboards existants
- [ ] `DashboardEmploye.jsx` — refonte bento grid
- [ ] `DashboardPayeur.jsx` — refonte avec vraies tables modernes
- [ ] `Factures.jsx` — table moderne (pas 3-equal-cards)
- [ ] `Simulation.jsx` — formulaire moderne
- [ ] `GestionComptes.jsx` — table moderne

### Phase 3 : Améliorations UX
- [ ] Skeleton loaders (pas spinner générique)
- [ ] Toast notifications (react-hot-toast)
- [ ] Export Excel/PDF (xlsx + jspdf)
- [ ] Filtres avancés sur les tables
- [ ] Graphiques (recharts) sur les dashboards

### Phase 4 : Polish
- [ ] Dark mode complet testé
- [ ] Responsive mobile vérifié
- [ ] Animations reduced-motion
- [ ] Accessibility audit (WCAG AA)

---

## 🚀 Commandes

```bash
# Dev
npm run dev

# Build
npm run build

# Preview production
npm run preview
```

---

## 📦 Dépendances ajoutées

```json
{
  "motion": "^11.x"  // Animation library (ex Framer Motion)
}
```

---

## ✅ Pre-Flight Check (design-taste-frontend)

- [x] ZERO em-dashes (`—`) sur toutes les pages
- [x] Page Theme Lock (un seul thème par page, pas de flip dark/light)
- [x] Color Consistency Lock (accent Moov bleu/orange partout)
- [x] Shape Consistency Lock (radius cohérent)
- [x] Button Contrast Check (WCAG AA)
- [x] Hero stack discipline (N/A - pas de hero sur dashboards)
- [x] No AI tells (pas Inter, pas beige+brass, pas 3-equal-cards)
- [x] Real images OR explicit TODO (dashboards = data, pas besoin images)
- [x] Motion motivated (stagger lists, smooth transitions, pas GSAP gratuit)
- [x] Mobile collapse explicit (Tailwind responsive classes)

---

**Statut actuel :** ✅ Architecture refaite + 3 nouvelles pages modernes créées + Build OK
