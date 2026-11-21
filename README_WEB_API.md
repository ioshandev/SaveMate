# SaveMate Web API & Admin Dashboard

This document covers the Web API and Admin Dashboard integration for SaveMate.

## Web API

The Web API (FastAPI) provides RESTful endpoints for the Admin Dashboard.

### Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check | No |
| `/bot-status` | GET | Bot system status | No |
| `/stats` | GET | Detailed statistics | Yes |
| `/users` | GET | Paginated user list | Yes |
| `/users/{user_id}` | GET | User details | Yes |
| `/activity` | GET | Recent activity | Yes |
| `/history` | GET | History entries | Yes |
| `/daily-stats` | GET | Daily statistics | Yes |
| `/platforms` | GET | Platform breakdown | Yes |

### Running the API

```bash
cd web_api
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEB_API_KEY` | API key for admin endpoints | (required) |
| `DATABASE_PATH` | Path to SQLite database | `storage/database.sqlite3` |
| `WEB_API_DB_PATH` | Web API database path override | None |
| `WEB_CORS_ORIGINS` | Allowed CORS origins | `*` |
| `WEB_ALLOW_PUBLIC_STATS` | Allow unauthenticated stats | `false` |
| `WEB_RATE_LIMIT_REQUESTS` | Rate limit requests per window | `100` |
| `WEB_RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |

## Admin Dashboard

The Admin Dashboard is a React/TypeScript SPA with Tailwind CSS styling.

### Development

```bash
cd web_ui
npm install
npm run dev
```

The dev server runs on http://localhost:3000 and proxies `/api` requests to http://localhost:8080.

### Build

```bash
cd web_ui
npm run build
```

The build output is in `web_ui/dist/`.

### Deployment to Vercel

1. Connect the `web_ui` directory to Vercel
2. Set environment variables in Vercel dashboard:
   - `WEB_API_KEY` - Your API key for dashboard authentication
   - `DATABASE_PATH` - Path to SQLite database (if different from default)

3. For production API, deploy `web_api` separately:
   ```bash
   cd web_api
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

### API URL Configuration

The dashboard uses `/api` as the proxy path in development. For production deployments:

1. Option A: Deploy API and Dashboard together:
   - Configure `WEB_API_URL` environment variable in the frontend
   - Or use the same origin (both on same domain)

2. Option B: Separate deployments:
   - Set `VITE_API_URL` environment variable for the frontend build
   - Update `vite.config.ts` proxy configuration for production

## Authentication

Both the API and Dashboard use Bearer token authentication:

- API key is passed in `Authorization: Bearer <api_key>` header
- Dashboard stores the API key in `localStorage` under `savemate_api_key`

## Frontend Dependencies

- React 18.3.0
- React Router 6.23.0
- Recharts 2.12.7 (for data visualization)
- Tailwind CSS 3.4.0
- Lucide React 0.378.0 (icons)

## Database Schema

The API reads from the existing SaveMate SQLite database with tables:
- `users` - User registrations and settings
- `history` - Download/history entries
- `favorites` - User favorites/bookmarks