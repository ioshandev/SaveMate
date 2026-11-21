# SaveMate — Telegram Media Assistant Bot

**SaveMate** is a feature-rich Telegram bot for media management, processing, and AI assistance. Built with Python 3.12+ and aiogram 3.x.

---

## Features

| Category | Features |
|----------|----------|
| **Media Assistant** | Extract metadata from YouTube, TikTok, Instagram, Facebook, Pinterest, and direct media URLs |
| **Image Tools** | Convert formats (JPEG, PNG, WEBP, GIF, BMP, TIFF), compress with quality presets, view file info |
| **Video Tools** | Compress (CRF presets), convert formats (MP4, MOV, MKV, WEBM, AVI), extract audio (MP3, AAC, OGG, FLAC, WAV, M4A, OPUS), view file info |
| **AI Assistant** | Chat with OpenAI-compatible API, per-user conversation context, streaming responses |
| **History** | Paginated activity log with clear confirmation |
| **Favorites** | Save and manage favorite media items |
| **Settings** | Language (English/සිංහල), notifications, file preferences, data deletion |
| **Admin Panel** | Statistics, user lookup, broadcast messages, system status |

---

## Requirements

- **Python 3.12+** (tested on 3.12.10)
- **FFmpeg** (for video processing) — install via `winget install ffmpeg` or Docker
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- **Admin User ID(s)** — your Telegram numeric ID(s)

---

## Quick Start (Windows)

> 📖 **Full Setup Guide:** See [SETUP.md](SETUP.md) for detailed step-by-step instructions on getting Telegram tokens, admin IDs, AI keys, systemd services, and Linux/macOS installation.

### 1. Clone & Setup

```cmd
cd D:\Dev\SaveMate
python -m pip install -r requirements.txt
```

### 2. Configure Environment

```cmd
copy .env.example .env
```

Edit `.env` with your values:

```ini
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=123456789,987654321
AI_API_KEY=your_openai_compatible_api_key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

### 3. Run

```cmd
python main.py
```

Or with Docker:

```cmd
docker-compose up -d
```

---

## Project Structure

```
SaveMate/
├── main.py                      # Entry point
├── config.py                    # Configuration (frozen dataclass)
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── HANDOFF.md                   # Development handoff
├── README.md                    # This file
├── bot/
│   ├── __init__.py
│   ├── main.py                  # (legacy - use root main.py)
│   ├── handlers/                # Message & callback handlers
│   │   ├── start.py
│   │   ├── help.py
│   │   ├── links.py
│   │   ├── media_tools.py
│   │   ├── ai_chat.py
│   │   ├── history.py
│   │   ├── favorites.py
│   │   ├── settings.py
│   │   ├── admin.py
│   │   └── __init__.py
│   ├── keyboards/               # Inline & reply keyboards
│   │   ├── inline.py
│   │   ├── reply.py
│   │   ├── callbacks.py
│   │   └── __init__.py
│   ├── middlewares/             # Update middlewares
│   │   ├── database.py
│   │   ├── user.py
│   │   ├── throttling.py
│   │   └── __init__.py
│   └── filters/                 # Custom filters
│       ├── admin.py
│       ├── link.py
│       └── __init__.py
├── core/
│   ├── __init__.py
│   ├── ai_client.py             # OpenAI-compatible client
│   ├── rate_limit.py            # In-memory sliding window
│   ├── security.py              # URL validation, SSRF protection
│   └── media/
│       ├── __init__.py
│       ├── images.py            # Pillow image processing
│       ├── ffmpeg.py            # FFmpeg subprocess wrapper
│       └── processor.py         # Dispatch & validation
├── services/
│   ├── __init__.py
│   └── platform_adapters/       # Platform-specific metadata extractors
│       ├── __init__.py
│       ├── base.py
│       ├── youtube.py
│       ├── tiktok.py
│       ├── instagram.py
│       ├── facebook.py
│       ├── pinterest.py
│       ├── direct.py
│       ├── registry.py
│       └── oembed.py
├── database/
│   ├── __init__.py
│   ├── db.py                    # aiosqlite connection & schema
│   └── repositories/
│       ├── users.py
│       ├── history.py
│       ├── favorites.py
│       ├── stats.py
│       └── __init__.py
├── utils/
│   ├── __init__.py
│   ├── texts.py                 # i18n (EN + Sinhala)
│   ├── tempfiles.py             # Temp file management
│   └── logging.py
├── storage/
│   ├── temp/                    # Temporary files
│   └── downloads/               # Downloaded media
└── tests/
    ├── conftest.py              # Pytest fixtures
    ├── test_config.py
    ├── test_db.py
    ├── test_users.py
    ├── test_history.py
    ├── test_favorites.py
    ├── test_url_validation.py
    ├── test_platform_detection.py
    ├── test_ssrf.py
    ├── test_file_validation.py
    ├── test_ai_client.py
    ├── test_callbacks.py
    └── __init__.py
```

---

## Configuration Reference

All settings in `.env` (loaded via `config.py`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ | — | Telegram bot token from @BotFather |
| `ADMIN_IDS` | ✅ | — | Comma-separated Telegram user IDs |
| `AI_API_KEY` | ❌ | — | OpenAI-compatible API key (optional, disables AI features if not set) |
| `AI_BASE_URL` | ❌ | `https://api.openai.com/v1` | API base URL (OpenAI-compatible) |
| `AI_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `DATABASE_PATH` | ❌ | `storage/database.sqlite3` | SQLite database file path |
| `MAX_FILE_SIZE` | ❌ | `52428800` | Max upload file size in bytes |
| `MAX_DOWNLOAD_SIZE` | ❌ | `104857600` | Max media download size in bytes |
| `RATE_LIMIT_MESSAGES` | ❌ | `30` | Max messages per window |
| `RATE_LIMIT_WINDOW` | ❌ | `60` | Rate limit window in seconds |
| `TEMP_FILE_TTL` | ❌ | `3600` | Temporary file TTL in seconds |
| `DEFAULT_LANGUAGE` | ❌ | `en` | Default language (`en` or `si`) |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Development

### Run Tests

```cmd
python -m pytest -q
python -m pytest tests/ -v
```

### Type Check (if using mypy)

```cmd
python -m mypy bot/ core/ services/ database/ utils/
```

### Code Style

```cmd
python -m black --check .
python -m ruff check .
```

---

## Architecture Overview

### Middleware Chain (order matters)

1. **DatabaseMiddleware** — Provides `db` connection via `data["db"]`
2. **UserMiddleware** — Auto-registers user, provides `user` and `lang`
3. **ThrottlingMiddleware** — Rate limits per user/action bucket

### Callback Data Format

Compact JSON with `"a"` key for action:

```json
{"a":"navigate","section":"media"}
{"a":"convert","format":"PNG","file_id":"abc123"}
```

All callbacks inherit from `CallbackData` base class with `pack()`/`unpack()` methods.

### Platform Adapters

Each platform has an adapter implementing `BaseAdapter`:
- `can_handle(url)` — URL pattern matching
- `fetch_metadata(url)` — Extract title, duration, author, etc.
- `is_download_authorized(metadata)` — Check permissions

Registry auto-detects adapter via `adapter_registry.get_adapter(url)`.

### SSRF Protection

`core/security.py` validates all outbound requests:
- Blocks `localhost`, `127.0.0.1`, `::1`
- Blocks private IP ranges (RFC 1918, link-local, ULA)
- Blocks dangerous ports (22, 3306, 5432, 6379, 27017, etc.)
- Resolves DNS and validates resolved IPs

---

## Internationalization

Full English + Sinhala support via `utils/texts.py`:

```python
from utils.texts import get_text
text = get_text("welcome", lang="si")  # Sinhala
```

Add new languages by extending the `TEXTS` dictionary.

---

## Rate Limiting

In-memory sliding window (`core/rate_limit.py`):

```python
from core.rate_limit import rate_limiter

# Check rate limit
allowed, retry_after = await rate_limiter.check_rate_limit(user_id, "ai_chat", limit=20, window=60)
if not allowed:
    print(f"Rate limited. Wait {retry_after}s")
```

Default limits (applied via `ThrottlingMiddleware`):

| Action | Limit | Window |
|--------|-------|--------|
| messages | 30 | 60s |
| media_download | 10 | 60s |
| media_process | 5 | 60s |
| ai_chat | 20 | 60s |
| history | 30 | 60s |
| favorites | 30 | 60s |
| settings | 30 | 60s |
| admin | 100 | 60s |

---

## Database Schema (SQLite + WAL)

---

## Database Schema (SQLite + WAL)

```sql
-- Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT DEFAULT 'en',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_processed INTEGER DEFAULT 0,
    notifications_enabled INTEGER DEFAULT 1,
    last_activity TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- History
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    platform TEXT,
    original_url TEXT,
    file_id TEXT,
    file_name TEXT,
    file_size INTEGER,
    media_type TEXT,
    thumbnail_url TEXT,
    result_status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Favorites
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT,
    file_size INTEGER,
    caption TEXT,
    platform TEXT,
    original_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**WAL Mode:** SQLite uses Write-Ahead Logging for improved concurrent read performance.

---

## Docker Deployment

```yaml
# docker-compose.yml
services:
  bot:
    build: .
    container_name: savemate-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./storage:/app/storage
    environment:
      - PYTHONUNBUFFERED=1
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p storage/temp storage/downloads && touch storage/temp/.gitkeep storage/downloads/.gitkeep
CMD ["python", "main.py"]
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not found | Use full path: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` or `py` launcher |
| `pip.exe` blocked | Use `python -m pip install` |
| FFmpeg not found | Install via `winget install ffmpeg` or use Docker |
| Bot doesn't respond | Check `BOT_TOKEN` and that bot is started |
| Database locked | Ensure only one bot instance runs; WAL mode handles concurrent reads |

---

## License

MIT License — see `LICENSE` file (if present).

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `python -m pytest -q` and `python -m compileall -q .`
5. Submit a PR

---

## Support

For issues or questions, check the `HANDOFF.md` for development context or open a GitHub issue.