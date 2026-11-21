import pytest

from database.repositories.users import UserRepository


@pytest.mark.asyncio
async def test_get_or_create_new_user(db_context):
    """Test creating a new user."""
    repo = UserRepository(db_context)
    user = await repo.get_or_create(
        user_id=12345,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en"
    )

    assert user.id == 12345
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.language == "en"
    assert user.notifications_enabled is True
    assert user.total_processed == 0


@pytest.mark.asyncio
async def test_get_or_create_existing_user(db_context):
    """Test getting an existing user."""
    repo = UserRepository(db_context)

    # Create user
    await repo.get_or_create(user_id=12345, username="testuser", first_name="Test")

    # Get existing user
    user = await repo.get_or_create(user_id=12345, username="newuser", first_name="New")
    assert user.username == "testuser"  # Original username preserved
    assert user.first_name == "Test"


@pytest.mark.asyncio
async def test_update_language(db_context):
    """Test updating user language."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    await repo.update_language(12345, "si")
    user = await repo.get_user(12345)
    assert user.language == "si"


@pytest.mark.asyncio
async def test_update_notifications(db_context):
    """Test updating notifications setting."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    await repo.update_notifications(12345, False)
    user = await repo.get_user(12345)
    assert user.notifications_enabled is False

    await repo.update_notifications(12345, True)
    user = await repo.get_user(12345)
    assert user.notifications_enabled is True


@pytest.mark.asyncio
async def test_increment_processed(db_context):
    """Test incrementing processed count."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    await repo.increment_processed(12345)
    user = await repo.get_user(12345)
    assert user.total_processed == 1

    await repo.increment_processed(12345)
    await repo.increment_processed(12345)
    user = await repo.get_user(12345)
    assert user.total_processed == 3


@pytest.mark.asyncio
async def test_update_last_activity(db_context):
    """Test updating last activity."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    await repo.update_last_activity(12345)
    user = await repo.get_user(12345)
    assert user.last_activity is not None


@pytest.mark.asyncio
async def test_get_user_stats(db_context):
    """Test getting user stats."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    stats = await repo.get_user_stats(12345)
    assert "history_count" in stats
    assert "favorites_count" in stats
    assert stats["history_count"] == 0
    assert stats["favorites_count"] == 0


@pytest.mark.asyncio
async def test_delete_user_data(db_context):
    """Test deleting user data."""
    repo = UserRepository(db_context)
    await repo.get_or_create(user_id=12345, username="testuser")

    await repo.delete_user_data(12345)
    user = await repo.get_user(12345)
    assert user is None


@pytest.mark.asyncio
async def test_get_all_users(db_context):
    """Test getting all users with pagination."""
    repo = UserRepository(db_context)

    # Create multiple users
    for i in range(25):
        await repo.get_or_create(user_id=1000 + i, username=f"user{i}")

    # Test pagination
    users_page1 = await repo.get_all_users(page=0, limit=10)
    assert len(users_page1) == 10

    users_page2 = await repo.get_all_users(page=1, limit=10)
    assert len(users_page2) == 10

    users_page3 = await repo.get_all_users(page=2, limit=10)
    assert len(users_page3) == 5


@pytest.mark.asyncio
async def test_get_total_users_count(db_context):
    """Test getting total users count."""
    repo = UserRepository(db_context)

    count_before = await repo.get_total_users_count()

    await repo.get_or_create(user_id=12345, username="testuser1")
    await repo.get_or_create(user_id=12346, username="testuser2")

    count_after = await repo.get_total_users_count()
    assert count_after == count_before + 2