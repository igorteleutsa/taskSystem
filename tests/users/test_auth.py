import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup(test_client: AsyncClient):
    """
    Test the user signup functionality.
    """
    response = await test_client.post(
        "/users/signup",
        json={
            "email": "test555user@example.com",
            "name": "Test",
            "surname": "User",
            "password": "password15lk23",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test555user@example.com"


@pytest.mark.asyncio
async def test_login(test_client: AsyncClient):
    """
    Test the user login functionality.
    """
    # First, sign up a user
    response = await test_client.post(
        "/users/signup",
        json={
            "email": "testlogin@example.com",
            "password": "password123",
            "name": "Login",
            "surname": "User",
        },
    )
    assert response.status_code == 200

    # Then, log in with the user credentials
    response = await test_client.post(
        "/users/login",
        data={"username": "testlogin@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
