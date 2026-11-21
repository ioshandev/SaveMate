import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.db import init_db, close_db
from core.ai_client import init_ai_client
from core.rate_limit import rate_limiter
from utils.logging import setup_logging
from utils.tempfiles import cleanup_old_temp_files

from bot.middlewares import (
    ThrottlingMiddleware,
    DatabaseMiddleware,
    UserMiddleware,
)
from bot.handlers import (
    start,
    help as help_handler,
    links,
    media_tools,
    ai_chat,
    history,
    favorites,
    settings,
    admin,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(dp: Dispatcher):
    """Application lifespan handler."""
    logger.info("Starting SaveMate bot...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize AI client
    init_ai_client()
    logger.info("AI client initialized")

    # Start background tasks
    cleanup_task = asyncio.create_task(periodic_cleanup())
    rate_limit_cleanup_task = asyncio.create_task(periodic_rate_limit_cleanup())

    yield

    # Shutdown
    logger.info("Shutting down SaveMate bot...")
    cleanup_task.cancel()
    rate_limit_cleanup_task.cancel()

    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

    try:
        await rate_limit_cleanup_task
    except asyncio.CancelledError:
        pass

    await close_db()
    logger.info("Database closed")


async def periodic_cleanup():
    """Periodic cleanup of temporary files."""
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour
            removed = await cleanup_old_temp_files(max_age_hours=24)
            if removed > 0:
                logger.info("Cleaned up %d temporary files", removed)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in periodic cleanup: %s", e)


async def periodic_rate_limit_cleanup():
    """Periodic cleanup of expired rate limit buckets."""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            removed = await rate_limiter.cleanup_expired()
            if removed > 0:
                logger.debug("Cleaned up %d expired rate limit buckets", removed)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in rate limit cleanup: %s", e)


async def main() -> None:
    """Main entry point."""
    # Validate config
    if not config.bot_token:
        logger.error("BOT_TOKEN not configured!")
        sys.exit(1)

    # Create bot and dispatcher
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register middlewares (order matters!)
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(ThrottlingMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(help_handler.router)
    dp.include_router(links.router)
    dp.include_router(media_tools.router)
    dp.include_router(ai_chat.router)
    dp.include_router(history.router)
    dp.include_router(favorites.router)
    dp.include_router(settings.router)
    dp.include_router(admin.router)

    # Set lifespan
    dp.startup.register(lambda: None)  # Handled by lifespan
    dp.shutdown.register(lambda: None)

    # Run with lifespan
    async with lifespan(dp):
        # Delete webhook and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started polling")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        sys.exit(1)