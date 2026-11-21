import os
import tempfile
import shutil
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config import config

logger = logging.getLogger(__name__)

TEMP_DIR = Path("storage/temp").resolve()
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def temp_file(suffix: str = "", prefix: str = "savemate_") -> AsyncGenerator[Path, None]:
    """Create a temporary file that's automatically cleaned up."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=TEMP_DIR)
    os.close(fd)
    try:
        yield Path(path)
    finally:
        try:
            if Path(path).exists():
                Path(path).unlink()
        except Exception as e:
            logger.warning("Failed to clean up temp file %s: %s", path, e)


@asynccontextmanager
async def temp_dir(prefix: str = "savemate_") -> AsyncGenerator[Path, None]:
    """Create a temporary directory that's automatically cleaned up."""
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=TEMP_DIR))
    try:
        yield path
    finally:
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            logger.warning("Failed to clean up temp dir %s: %s", path, e)


async def cleanup_old_temp_files() -> int:
    """Remove temp files older than TTL. Returns count of deleted files."""
    import time
    now = time.time()
    ttl = config.temp_file_ttl
    deleted = 0

    try:
        for entry in TEMP_DIR.iterdir():
            if entry.is_file():
                mtime = entry.stat().st_mtime
                if now - mtime > ttl:
                    entry.unlink()
                    deleted += 1
            elif entry.is_dir():
                mtime = entry.stat().st_mtime
                if now - mtime > ttl:
                    shutil.rmtree(entry, ignore_errors=True)
                    deleted += 1
    except Exception as e:
        logger.warning("Error during temp cleanup: %s", e)

    if deleted:
        logger.info("Cleaned up %d old temp files", deleted)
    return deleted


def get_temp_path(suffix: str = "") -> Path:
    """Get a path for a temporary file (caller responsible for cleanup)."""
    import uuid
    return TEMP_DIR / f"savemate_{uuid.uuid4().hex}{suffix}"