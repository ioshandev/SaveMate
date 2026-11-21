# SaveMate — Setup & Deployment Guide

This guide provides step-by-step instructions for setting up, configuring, and deploying the **SaveMate** Telegram Media Assistant Bot.

---

## 📋 Pre-requisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.12+** installed (`python --version`)
- [ ] **FFmpeg** installed and added to PATH (required for video processing)
- [ ] A **Telegram Account**
- [ ] An **OpenAI-compatible API key** (Optional — for AI chat features)

---

## 🤖 Step 1: Obtain a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Start a chat and send the `/newbot` command.
3. Follow the prompts:
   - Enter a **name** for your bot (e.g., `SaveMate Assistant`).
   - Enter a **username** ending in `bot` (e.g., `SaveMate_Assistant_bot`).
4. BotFather will provide an **HTTP API Token**. Save this token safely:
   ```
   123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ-example
   ```
5. *(Optional)* Configure your bot profile in BotFather:
   - `/setdescription` — Add a description shown before users start the bot.
   - `/setabouttext` — Add an about text shown on the bot's profile.
   - `/setuserpic` — Upload a profile picture for your bot.
   - `/setcommands` — Set bot command suggestions:
     ```
     start - Start the bot & show main menu
     help - Show help & available commands
     settings - Change bot preferences
     history - View process history
     favorites - Access saved favorites
     ```

---

## 👤 Step 2: Get Your Telegram User ID

The Admin Panel requires your numeric Telegram User ID.

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot) or [@raw_data_bot](https://t.me/raw_data_bot).
2. Send `/start`.
3. Copy your numeric **Id** (e.g., `123456789`).
4. If you have multiple admin users, collect all their IDs.

---

## 🧠 Step 3: Configure AI Assistant (Optional)

SaveMate supports any OpenAI-compatible API endpoint (OpenAI, DeepSeek, OpenRouter, LocalAI, Ollama, etc.).

### Option A: OpenAI
- Get an API key from [platform.openai.com](https://platform.openai.com/api-keys).
- Set `AI_BASE_URL=https://api.openai.com/v1`
- Set `AI_MODEL=gpt-4o-mini`

### Option B: DeepSeek
- Get an API key from [platform.deepseek.com](https://platform.deepseek.com/).
- Set `AI_BASE_URL=https://api.deepseek.com/v1`
- Set `AI_MODEL=deepseek-chat`

### Option C: OpenRouter
- Get an API key from [openrouter.ai](https://openrouter.ai/).
- Set `AI_BASE_URL=https://openrouter.ai/api/v1`
- Set `AI_MODEL=meta-llama/llama-3-70b-instruct`

---

## ⚙️ Step 4: Environment Configuration

1. Clone or download the repository to your server/machine:
   ```bash
   git clone https://github.com/your-username/SaveMate.git
   cd SaveMate
   ```

2. Copy the example environment file:
   ```bash
   # Windows (CMD)
   copy .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```

3. Open `.env` in a text editor and fill in your details:
   ```ini
   # Required
   BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ-example
   ADMIN_IDS=123456789,987654321

   # AI Assistant (Optional)
   AI_API_KEY=your_api_key_here
   AI_BASE_URL=https://api.openai.com/v1
   AI_MODEL=gpt-4o-mini

   # Optional Customization
   DEFAULT_LANGUAGE=en
   LOG_LEVEL=INFO
   ```

---

## 🎬 Step 5: Install FFmpeg

FFmpeg is required for video compression, format conversion, and audio extraction.

### Windows
```cmd
winget install ffmpeg
```
*Note: Restart your terminal after installation so FFmpeg is available in your PATH.*

### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

---

## 🚀 Step 6: Launching the Bot

### Method A: Direct Python Execution

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv

   # Activate on Windows (CMD/PowerShell)
   .\venv\Scripts\activate

   # Activate on Linux/macOS
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run test suite to verify setup:
   ```bash
   python -m pytest
   ```

4. Start the bot:
   ```bash
   python main.py
   ```

---

### Method B: Docker Deployment (Recommended for Production)

Docker handles Python, dependencies, FFmpeg, and persistent storage automatically.

1. Ensure **Docker** and **Docker Compose** are installed.
2. Build and start the container in detached mode:
   ```bash
   docker-compose up -d
   ```
3. View logs:
   ```bash
   docker-compose logs -f
   ```
4. Stop the container:
   ```bash
   docker-compose down
   ```

---

### Method C: Linux Systemd Service (Background Service)

To run SaveMate continuously on a Linux VPS without Docker:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/savemate.service
   ```

2. Add the following content (adjust paths accordingly):
   ```ini
   [Unit]
   Description=SaveMate Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/SaveMate
   ExecStart=/home/ubuntu/SaveMate/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable savemate
   sudo systemctl start savemate
   ```

4. Check status and logs:
   ```bash
   sudo systemctl status savemate
   sudo journalctl -u savemate -f
   ```

---

## 🧪 Verification & Health Check

Once the bot is running:

1. Open Telegram and send `/start` to your bot.
2. You should receive the main menu welcome message.
3. If you are configured in `ADMIN_IDS`, click **Admin Panel** to view system statistics.
4. Send a media link (e.g., YouTube URL) to test the link processing feature.

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `ValueError: BOT_TOKEN is required` | `.env` file missing or invalid `BOT_TOKEN` | Create `.env` from `.env.example` and set `BOT_TOKEN`. |
| `ValueError: ADMIN_IDS is required` | `ADMIN_IDS` is missing in `.env` | Add your numeric Telegram ID to `ADMIN_IDS`. |
| `FFmpeg not found in PATH` | FFmpeg isn't installed or not in PATH | Install FFmpeg via `winget` (Windows) or `apt` (Linux) and restart terminal. |
| Bot does not reply to messages | Incorrect token or process crashed | Check logs (`python main.py` console output or `docker-compose logs`). |
| AI Assistant says unavailable | `AI_API_KEY` not set in `.env` | Add a valid OpenAI-compatible API key to `.env`. |
