# Law Engine — Web App

The Next.js 16 / TypeScript / React frontend for Law Engine. Reads the real, ingested UCC statutory data under `../library/normalized/` directly — no backend server or database beyond the JSON files this repository already ships. Requires Node.js **>=20.9.0**.

See the repository root `README.md` for the full project overview, and `NOTICE.md` for the statutory-source licensing statement.

## Real pages/routes

- `/` — browse all ingested sections across both Articles
- `/sections/[id]` — one section's full text, definitions, cross-references, and language-analysis panel
- `/learn` — an interactive, multi-stage transaction-lifecycle learner
- `/api/search` — real search endpoint
- `/api/lifecycle` — real lifecycle-data endpoint

## Setup

```bash
npm install
npm run dev      # local development server, http://localhost:3000
```

## Tests and build

```bash
npm test         # Vitest + React Testing Library
npm run build    # production build, includes a full TypeScript type-check
npm run start    # serve the production build
```
