import pytest

from database.repositories.favorites import FavoritesRepository


@pytest.mark.asyncio
async def test_add_favorite(db_context):
    """Test adding a favorite."""
    repo = FavoritesRepository(db_context)

    await repo.add(
        user_id=12345,
        file_id="file_123",
        file_type="video",
        title="Test Video",
        platform="youtube",
        url="https://youtube.com/watch?v=test",
        thumbnail_url="https://img.youtube.com/vi/test/maxresdefault.jpg"
    )

    favorites = await repo.get_user_favorites(12345)
    assert len(favorites) == 1
    assert favorites[0]["platform"] == "youtube"
    assert favorites[0]["title"] == "Test Video"


@pytest.mark.asyncio
async def test_get_user_favorites_pagination(db_context):
    """Test favorites pagination."""
    repo = FavoritesRepository(db_context)

    # Add 25 items
    for i in range(25):
        await repo.add(
            user_id=12345,
            file_id=f"file_{i}",
            file_type="video",
            title=f"Video {i}",
            platform="youtube",
            url=f"https://youtube.com/watch?v=test{i}"
        )

    page1 = await repo.get_user_favorites(12345, page=0, limit=10)
    assert len(page1) == 10

    page2 = await repo.get_user_favorites(12345, page=1, limit=10)
    assert len(page2) == 10

    page3 = await repo.get_user_favorites(12345, page=2, limit=10)
    assert len(page3) == 5


@pytest.mark.asyncio
async def test_get_user_favorites_count(db_context):
    """Test getting favorites count."""
    repo = FavoritesRepository(db_context)

    count_before = await repo.get_user_favorites_count(12345)

    await repo.add(user_id=12345, file_id="f1", file_type="video", title="1", platform="youtube", url="https://youtube.com/1")
    await repo.add(user_id=12345, file_id="f2", file_type="video", title="2", platform="youtube", url="https://youtube.com/2")

    count_after = await repo.get_user_favorites_count(12345)
    assert count_after == count_before + 2


@pytest.mark.asyncio
async def test_remove_favorite(db_context):
    """Test removing a favorite."""
    repo = FavoritesRepository(db_context)

    await repo.add(user_id=12345, file_id="f1", file_type="video", title="1", platform="youtube", url="https://youtube.com/1")
    await repo.add(user_id=12345, file_id="f2", file_type="video", title="2", platform="youtube", url="https://youtube.com/2")

    favorites = await repo.get_user_favorites(12345)
    fav_id = favorites[0]["id"]

    await repo.remove_favorite(12345, fav_id)

    favorites = await repo.get_user_favorites(12345)
    assert len(favorites) == 1
    assert favorites[0]["id"] != fav_id


@pytest.mark.asyncio
async def test_remove_nonexistent_favorite(db_context):
    """Test removing a non-existent favorite."""
    repo = FavoritesRepository(db_context)

    # Should not raise an error
    await repo.remove_favorite(12345, 99999)


@pytest.mark.asyncio
async def test_get_favorite(db_context):
    """Test getting a specific favorite."""
    repo = FavoritesRepository(db_context)

    await repo.add(
        user_id=12345,
        file_id="file_123",
        file_type="video",
        title="Test Video",
        platform="youtube",
        url="https://youtube.com/watch?v=test"
    )

    favorites = await repo.get_user_favorites(12345)
    fav_id = favorites[0]["id"]

    favorite = await repo.get_favorite(12345, fav_id)
    assert favorite is not None
    assert favorite["id"] == fav_id
    assert favorite["title"] == "Test Video"


@pytest.mark.asyncio
async def test_get_nonexistent_favorite(db_context):
    """Test getting a non-existent favorite."""
    repo = FavoritesRepository(db_context)

    favorite = await repo.get_favorite(12345, 99999)
    assert favorite is None


@pytest.mark.asyncio
async def test_favorites_isolation(db_context):
    """Test that favorites are isolated per user."""
    repo = FavoritesRepository(db_context)

    await repo.add(user_id=111, file_id="f1", file_type="video", title="1", platform="youtube", url="https://youtube.com/1")
    await repo.add(user_id=222, file_id="f2", file_type="video", title="2", platform="youtube", url="https://youtube.com/2")

    favs1 = await repo.get_user_favorites(111)
    favs2 = await repo.get_user_favorites(222)

    assert len(favs1) == 1
    assert len(favs2) == 1
    assert favs1[0]["user_id"] == 111
    assert favs2[0]["user_id"] == 222


@pytest.mark.asyncio
async def test_is_favorite(db_context):
    """Test checking if URL is already favorited."""
    repo = FavoritesRepository(db_context)

    await repo.add(user_id=12345, file_id="file_1", file_type="video", title="Test", platform="youtube", url="https://youtube.com/test")

    is_fav = await repo.is_favorite(12345, "https://youtube.com/test")
    assert is_fav is True

    is_fav = await repo.is_favorite(12345, "https://youtube.com/other")
    assert is_fav is False