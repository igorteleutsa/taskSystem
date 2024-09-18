import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.base import Base
from app.core.settings import settings
from app.main import app
from app.core.database import get_db
from app.users.models import UserRole

# Create a test engine for the database
engine_test = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

# Create a session maker for the test database
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession
)


# Override the get_db dependency to use the test session
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


# Apply the override in FastAPI for tests
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # Override the FastAPI get_db dependency with our test session
    app.dependency_overrides[get_db] = override_get_db

    # Create the database schema before tests
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop the database schema after tests
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Test client fixture for httpx AsyncClient
@pytest_asyncio.fixture(scope="session")
async def test_client():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def create_users(test_client: AsyncClient):
    """
    Create admin, manager, and regular user for future use.
    """
    # Create an admin user
    admin_signup = await test_client.post(
        "/users/signup",
        json={
            "email": "admin@example.com",
            "password": "adminpassword",
            "name": "Admin",
            "surname": "User",
        },
    )
    assert admin_signup.status_code == 200

    # Login as the admin to assign the 'admin' role
    admin_login = await test_client.post(
        "/users/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    admin_role_update = await test_client.put(
        "/users/",
        json={"role": UserRole.ADMIN},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_role_update.status_code == 200

    # Create a manager user
    manager_signup = await test_client.post(
        "/users/signup",
        json={
            "email": "manager@example.com",
            "password": "managerpassword",
            "name": "Manager",
            "surname": "User",
        },
    )
    assert manager_signup.status_code == 200

    # Login as the manager to assign the 'manager' role
    manager_login = await test_client.post(
        "/users/login",
        data={"username": "manager@example.com", "password": "managerpassword"},
    )
    assert manager_login.status_code == 200
    manager_token = manager_login.json()["access_token"]

    # Update the manager's role
    manager_role_update = await test_client.put(
        "/users/",
        json={"role": UserRole.MANAGER},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert manager_role_update.status_code == 200

    # Create a regular user
    user_signup = await test_client.post(
        "/users/signup",
        json={
            "email": "user@example.com",
            "password": "userpassword",
            "name": "Regular",
            "surname": "User",
        },
    )
    assert user_signup.status_code == 200
