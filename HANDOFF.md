# SaveMate — Development Handoff

**Last updated:** 2026-11-20  
**Project directory:** D:\dev\savemate  
**Python:** 3.12.10 at `C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe` (not on PATH; use full path or `py` launcher at `C:\Users\User\AppData\Local\Programs\Python\Launcher\py.exe`)  
**pip:** Use `python -m pip` (pip.exe blocked by Application Control)

---

## ✅ Completed Tasks

### Project Structure & Configuration
- [x] Directory structure created (bot/, core/, services/, database/, utils/, storage/, tests/)
- [x] `requirements.txt` — aiogram 3.x, aiosqlite, aiohttp, python-dotenv, Pillow, pytest, pytest-asyncio, pytest-mock
- [x] `.env.example` — all required env vars documented (BOT_TOKEN, ADMIN_IDS, AI_API_KEY, AI_BASE_URL, AI_MODEL, limits, etc.)
- [x] `.gitignore` — covers env, db, pycache, venv, IDE, temp files
- [x] `config.py` — frozen dataclass Config loaded from .env with validation
- [x] `Dockerfile` — python:3.12-slim, installs ffmpeg, copies app
- [x] `docker-compose.yml` — bot service with volume mount for storage
- [x] `storage/temp/.gitkeep` and `storage/downloads/.gitkeep`
- [x] All `__init__.py` files created

### Database Layer
- [x] `database/db.py` — aiosqlite connection, WAL mode, schema (users, history, favorites), init_db()
- [x] `database/repositories/users.py` — get_or_create_user, update_language, update_notifications, increment_processed, get_user, get_user_count, get_active_user_count, delete_user_data
- [x] `database/repositories/history.py` — add_history, get_user_history (paginated), get_history_count, clear_user_history
- [x] `database/repositories/favorites.py` — add_favorite, remove_favorite, get_user_favorites (paginated), get_favorites_count, is_favorite
- [x] `database/repositories/stats.py` — get_bot_stats, get_user_stats (admin panel)

### Utils & Core Security
- [x] `utils/tempfiles.py` — async context managers for temp files/dirs, cleanup_old_temp_files, get_temp_path
- [x] `utils/logging.py` — setup_logging, get_logger
- [x] `utils/texts.py` — full i18n dict (EN + Sinhala), get_text() helper
- [x] `core/security.py` — URL validation, SSRF protection (resolve DNS, block private IPs, blocked ports), extract_urls

---

## ⏳ In Progress

**Task #1:** Initialize project structure and configuration files — *mostly complete, waiting on remaining core modules and bot handlers*

---

## 📋 Pending Tasks (in planned order)

1. **Platform Adapters** (`services/platform_adapters/`)
   - base.py — BaseAdapter ABC (matches, validate, is_authorized, fetch_metadata)
   - youtube.py — official oEmbed/noembed metadata only
   - tiktok.py, instagram.py, facebook.py, pinterest.py — metadata via official endpoints
   - direct.py — validated download with SSRF guard
   - registry.py — adapter registry, detect_platform()
   - oembed.py — shared oEmbed client

2. **Core Media Processor** (`core/media/`)
   - images.py — Pillow: convert, compress, info
   - ffmpeg.py — subprocess wrapper (args list, no shell), compress, convert, extract_audio
   - processor.py — dispatch, validation, size/type checks

3. **AI Client** (`core/ai_client.py`)
   - aiohttp OpenAI-compatible chat completions
   - per-user context (last N turns, in-memory)
   - timeout, error handling, unavailable message

4. **Rate Limiter** (`core/rate_limit.py`) — in-memory sliding window

5. **Bot Keyboards** (`bot/keyboards/`)
   - inline.py — main menu, media tools, settings, admin, pagination
   - reply.py — reply keyboards if needed
   - callbacks.py — callback data factory (pack/unpack)

6. **Bot Middlewares** (`bot/middlewares/`)
   - throttling.py — rate limit per user/action
   - database.py — session per update (or DI)
   - user.py — auto-register user on each update

7. **Bot Filters** (`bot/filters/`)
   - admin.py — IsAdmin filter (checks ADMIN_IDS)
   - link.py — LinkFilter (detects URLs in messages)

8. **Bot Handlers** (`bot/handlers/`)
   - start.py — /start, main menu callback
   - links.py — auto-detect URLs, platform adapter dispatch
   - media_tools.py — image/video tool handlers
   - ai_chat.py — AI conversation handler
   - history.py — paginated history, clear
   - favorites.py — add/remove/list favorites
   - settings.py — language, notifications, delete data
   - help.py — /help, about
   - admin.py — admin panel, stats, user lookup, broadcast, status

9. **Bot Entry Point** (`main.py`)
   - Dispatcher setup, router registration
   - startup/shutdown (init_db, cleanup temp)
   - polling with graceful shutdown

10. **Tests** (`tests/`)
    - conftest.py — fixtures
    - test_config.py, test_db.py, test_users.py, test_history.py, test_favorites.py
    - test_url_validation.py, test_platform_detection.py, test_ssrf.py
    - test_file_validation.py, test_ai_client.py, test_callbacks.py

11. **Documentation**
    - README.md — full setup, Windows instructions, testing guide

---

## ⚠️ Known Issues / Blockers

- **Python not on PATH:** Must use full path or `py` launcher. Verified working:
  - `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip --version` ✅
  - `py -m pip --version` ✅ (if py launcher in PATH)
- **pip.exe blocked:** Use `python -m pip install` or `py -m pip install`
- **No .env file yet:** User must create from `.env.example` with real BOT_TOKEN and ADMIN_IDS
- **FFmpeg not installed on host:** Dockerfile includes it; for local dev, install via winget/choco or use Docker
- **No dependencies installed yet:** Run `python -m pip install -r requirements.txt` (or `py -m pip install...`)

---

## 🔧 Next Steps (when resuming)

1. **Install dependencies:**
   ```cmd
   cd D:\dev\savemate
   python -m pip install -r requirements.txt
   ```

2. **Create `.env` from `.env.example`:**
   - Fill in `BOT_TOKEN` (from @BotFather)
   - Fill in `ADMIN_IDS` (your Telegram user ID, comma-separated)
   - Optional: `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`

3. **Continue implementation** from platform adapters onward per the plan.

4. **Run verification:**
   ```cmd
   python -m compileall -q .
   python -m pytest -q
   ```

---

## 🛑 Shutdown Instructions

**To safely stop work now:**
1. All files are saved (verified by the file list above).
2. No running processes — this is a source-only project.
3. Simply close the terminal / Claude Code window.

**To resume later:**
1. Open terminal / command prompt.
2. Run the provided `start-savemate.bat` (see below) — it will:
   - Change to `D:\dev\savemate`
   - Start `claude` (Claude Code CLI) in that directory
3. Continue from the pending tasks list above.

---

## 📂 File Inventory (for reference)

```
D:\dev\savemate\
├── main.py (NOT YET CREATED)
├── requirements.txt
├── .env.example
├── .gitignore
├── config.py
├── Dockerfile
├── docker-compose.yml
├── HANDOFF.md (this file)
├── start-savemate.bat (TO BE CREATED)
├── bot/
│   ├── __init__.py
│   ├── handlers/ (all __init__.py only)
│   ├── keyboards/ (all __init__.py only)
│   ├── middlewares/ (all __init__.py only)
│   └── filters/ (all __init__.py only)
├── core/
│   ├── __init__.py
│   ├── media/ (all __init__.py only)
│   ├── security/
│   │   ├── __init__.py
│   │   └── security.py
│   └── rate_limit/ (all __init__.py only)
├── services/
│   ├── __init__.py
│   └── platform_adapters/ (all __init__.py only)
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── repositories/
│       ├── __init__.py
│       ├── users.py
│       ├── history.py
│       ├── favorites.py
│       └── stats.py
├── utils/
│   ├── __init__.py
│   ├── tempfiles.py
│   ├── logging.py
│   └── texts.py
├── storage/
│   ├── temp/.gitkeep
│   └── downloads/.gitkeep
└── tests/ (all __init__.py only)
```