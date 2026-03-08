# 🚀 Project Handover: Opportunity Navigator (Montgomery, AL)

## 📌 Project Overview

This is a high-fidelity React prototype for a city-scale workforce development dashboard. It is designed to visualize labor market demands and training gaps specifically for NEET youth (Not in Education, Employment, or Training) and long-term unemployed adults.

---

## 🛠 Tech Stack

- **Framework:** React (Vite)
- **Styling:** Tailwind CSS
- **Icons:** Lucide-React
- **Components:** shadcn/ui (Radix UI)
- **State Management:** React `useState` and `useMemo` for real-time filtering logic

---

## 📊 Current Data Architecture (Mocked)

The application currently runs on static JSON files located in `src/data/`. There is currently no live database connected.

### Data Contract

| File | Purpose |
|------|---------|
| `city_stats.json` | Top-level dashboard metrics |
| `skills.json` | Skills Heatmap data (demand trends) |
| `gaps.json` | Training Gap panel (supply vs. demand) |
| `barriers.json` | Definitions for structural filters (degree, car, experience) |
| `roles_reachable.json` | Maps 3 personas to specific roles, including `barrierRequirements` arrays |
| `programmes.json` | Training pathways linked to roles via `relevantRoles` IDs |

---

## 🧠 Core Logic to Maintain (Critical)

### 1. Barrier Filtering ("Systemic Friction")

The app uses a specific exclusion UI logic. When a barrier (e.g., "No Car") is selected, roles requiring that barrier are **not hidden**.

- **Visual Treatment:** Affected cards are styled with `opacity-40` + `grayscale` + `pointer-events-none`
- **Product Vision:** The goal is to make the absence of opportunity visible, highlighting structural gaps in Montgomery rather than just filtering them out

### 2. Persona Context

The `activePersona` state globally controls:
- The "Why it's a good fit" copy
- The filtering of the `TrainingRail` component

---

## 🗄️ Suggested Database Schema (SQL)

To move this to production, migrate the JSON files to a PostgreSQL or Supabase instance using this structure:

### Table: `roles`

```sql
CREATE TABLE roles (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  fit_reason_general TEXT,
  fit_reason_ltu TEXT,
  fit_reason_neet TEXT,
  wage_min INTEGER,
  wage_max INTEGER,
  barrier_requirements TEXT[] -- e.g., ['car_required']
);
```

### Table: `training_programs`

```sql
CREATE TABLE training_programs (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  provider TEXT,
  cost_type ENUM ('free', 'earn_while_learn', 'paid'),
  support_flags TEXT[] -- e.g., ['childcare', 'transit']
);
```

---

## 🛠 Developer "Next Steps" (The Brief)

### Priority 1: Database Migration
Seed a database using the roles and programs currently in the `/data` folder.

### Priority 2: Auth & Onboarding
Currently, onboarding selections are saved to local state. These should be persisted to a `profiles` table with user authentication.

### Priority 3: Real Data Integration
Replace JSON fetches with actual API calls or database queries.

### Priority 4: Responsive Polish
Ensure the horizontal "Training Rail" handles touch-swipe events for mobile-first users.

---

## 📝 Quick Start (Development)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## 📚 Product Documentation

See project briefs and MoSCoW prioritization in the `/docs` folder:
- `Workforce_Pulse_Brief.docx` – Complete project brief
- `Workforce_Pulse_MoSCoW.md` – Feature prioritization matrix
- `WORKFORCE_PULSE.pdf` – Executive summary

---

## 🤝 Support & Questions

For questions about the data schema, persona logic, or barrier filtering, refer to the project briefs or contact the original product team.
