# Frontend — Nexus AI Chat

This folder contains the React + Vite frontend for Nexus AI Chat.

## Quick Start

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start development server:

```bash
npm run dev
```

The default Vite dev server runs on `http://localhost:5173`.

## Environment

- Set the API base URL via `VITE_API_BASE_URL`. Example in a `.env` file at `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

If not provided, the app defaults to `http://localhost:8000/api/v1` (see `src/constants.ts`).

## Build & Preview

```bash
npm run build
npm run preview
```

## Notes

- The frontend uses `axios` and reads the API base URL from `VITE_API_BASE_URL`.
- If you see CORS errors, ensure the backend `CORS_ORIGINS` includes the frontend origin (e.g. `http://localhost:5173`).
- I updated the `dev` script in `package.json` to run the Vite dev server.

## Useful files

- `src/api/client.ts` — axios instance using the configured API base URL
- `src/constants.ts` — default API base and token key
