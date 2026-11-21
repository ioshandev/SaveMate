import pytest

from database.repositories.history import HistoryRepository


@pytest.mark.asyncio
async def test_add_history(db_context):
    """Test adding history entry."""
    repo = HistoryRepository(db_context)

    await repo.add(
        user_id=12345,
        platform="youtube",
        url="https://youtube.com/watch?v=test",
        title="Test Video",
        action_type="download",
        media_type="video",
        thumbnail_url="https://img.youtube.com/vi/test/maxresdefault.jpg"
    )

    history = await repo.get_user_history(12345)
    assert len(history) == 1
    assert history[0]["platform"] == "youtube"
    assert history[0]["title"] == "Test Video"


@pytest.mark.asyncio
async def test_get_user_history_pagination(db_context):
    """Test history pagination."""
    repo = HistoryRepository(db_context)

    # Add 25 items
    for i in range(25):
        await repo.add(
            user_id=12345,
            platform="youtube",
            url=f"https://youtube.com/watch?v=test{i}",
            title=f"Video {i}",
            action_type="download",
            media_type="video"
        )

    page1 = await repo.get_user_history(12345, page=0, limit=10)
    assert len(page1) == 10

    page2 = await repo.get_user_history(12345, page=1, limit=10)
    assert len(page2) == 10

    page3 = await repo.get_user_history(12345, page=2, limit=10)
    assert len(page3) == 5


@pytest.mark.asyncio
async def test_get_user_history_count(db_context):
    """Test getting history count."""
    repo = HistoryRepository(db_context)

    count_before = await repo.get_user_history_count(12345)

    await repo.add(user_id=12345, platform="youtube", url="https://youtube.com/1", title="1", action_type="download", media_type="video")
    await repo.add(user_id=12345, platform="youtube", url="https://youtube.com/2", title="2", action_type="download", media_type="video")

    count_after = await repo.get_user_history_count(12345)
    assert count_after == count_before + 2


@pytest.mark.asyncio
async def test_clear_user_history(db_context):
    """Test clearing user history."""
    repo = HistoryRepository(db_context)

    await repo.add(user_id=12345, platform="youtube", url="https://youtube.com/1", title="1", action_type="download", media_type="video")
    await repo.add(user_id=12345, platform="youtube", url="https://youtube.com/2", title="2", action_type="download", media_type="video")

    await repo.clear_user_history(12345)

    history = await repo.get_user_history(12345)
    assert len(history) == 0

    count = await repo.get_user_history_count(12345)
    assert count == 0


@pytest.mark.asyncio
async def test_history_isolation(db_context):
    """Test that history is isolated per user."""
    repo = HistoryRepository(db_context)

    await repo.add(user_id=111, platform="youtube", url="https://youtube.com/1", title="1", action_type="download", media_type="video")
    await repo.add(user_id=222, platform="youtube", url="https://youtube.com/2", title="2", action_type="download", media_type="video")

    history1 = await repo.get_user_history(111)
    history2 = await repo.get_user_history(222)

    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0]["user_id"] == 111
    assert history2[0]["user_id"] == 222