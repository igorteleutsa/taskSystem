import uuid

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
from app.tickets.schemas import TicketCreate
from app.users.models import UserRole

# Create a test engine for the database
from app.users.schemas import UserCreate
from app.users.services import UserService

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


@pytest.fixture
async def create_project(test_client: AsyncClient, create_users):
    """Create a project for testing."""
    # Login as the user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    token = login_response.json()["access_token"]

    # Create a project
    project_data = {"title": "Test Project", "description": "Project description."}
    response = await test_client.post(
        "/projects/", json=project_data, headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["id"], token


@pytest.fixture
async def create_ticket(create_project, test_client: AsyncClient):
    """Fixture to create a ticket for tests."""
    project_id, token = await create_project

    # Assuming you have a function or method to retrieve the current user's id
    user_response = await test_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user = user_response.json()
    responsible_user_id = user["id"]

    ticket_data = TicketCreate(
        title="New Ticket",
        description="This is a test ticket",
        priority=1,  # Assuming priority is an integer or change it if it's an enum
        status="todo",
        project_id=project_id,
        responsible_user_id=responsible_user_id,  # Include this required field
    )

    # Create the ticket
    response = await test_client.post(
        "/tickets/",
        json=ticket_data.dict(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    ticket = response.json()

    return ticket["id"], token


@pytest.fixture
async def manager_user(test_client: AsyncClient):
    """
    Fixture to create a manager user and return the manager's id and access token.
    """
    # Sign up as a manager
    # Use a unique email for the manager user
    unique_email = f"manager_{uuid.uuid4()}@example.com"
    manager_signup = await test_client.post(
        "/users/signup",
        json={
            "email": unique_email,
            "password": "managerpassword",
            "name": "Manager",
            "surname": "User",
        },
    )
    assert manager_signup.status_code == 200

    # Log in as the manager to get the access token
    manager_login = await test_client.post(
        "/users/login",
        data={"username": "manager@example.com", "password": "managerpassword"},
    )
    assert manager_login.status_code == 200
    manager_token = manager_login.json()["access_token"]

    # Get the manager's details (id)
    user_response = await test_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    manager_id = user_response.json()["id"]

    # Assign manager role to the user
    role_update = await test_client.put(
        "/users/",
        json={"role": UserRole.MANAGER},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert role_update.status_code == 200

    return manager_id, manager_token
