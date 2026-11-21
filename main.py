#!/usr/bin/env python3
"""SaveMate - Telegram Media Assistant Bot

Entry point - imports and runs the main application from bot.main.
"""

from bot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())