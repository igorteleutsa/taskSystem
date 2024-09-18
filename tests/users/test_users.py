import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_me(test_client: AsyncClient):
    """
    Test fetching the current user's profile (protected route).
    """
    # First, sign up and log in to get a token
    signup_response = await test_client.post(
        "/users/signup",
        json={
            "email": "profiletest@example.com",
            "password": "password",
            "name": "Profile",
            "surname": "Test",
        },
    )
    assert signup_response.status_code == 200

    login_response = await test_client.post(
        "/users/login",
        data={"username": "profiletest@example.com", "password": "password"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Use the token to access the /users/me route
    response = await test_client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "profiletest@example.com"


@pytest.mark.asyncio
async def test_update_user(test_client: AsyncClient):
    """
    Test updating the current user's profile.
    """
    # First, sign up and log in to get a token
    signup_response = await test_client.post(
        "/users/signup",
        json={
            "email": "updatetest@example.com",
            "password": "password123",
            "name": "Update",
            "surname": "Test",
        },
    )
    assert signup_response.status_code == 200

    login_response = await test_client.post(
        "/users/login",
        data={"username": "updatetest@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Use the token to update the user's profile
    response = await test_client.put(
        "/users/",
        json={"name": "Updated", "surname": "User"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["surname"] == "User"


@pytest.mark.asyncio
async def test_get_users_admin(test_client: AsyncClient, create_users):
    """
    Test that an admin user can fetch a list of all users.
    """
    # Login as admin
    login_response = await test_client.post(
        "/users/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Get users (requires admin/manager role)
    response = await test_client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_user_by_id_admin(test_client: AsyncClient, create_users):
    """
    Test that an admin user can fetch a specific user by ID.
    """
    # Sign up as a regular user first
    signup_response = await test_client.post(
        "/users/signup",
        json={
            "email": "testuser2@example.com",
            "password": "password123",
            "name": "Test",
            "surname": "User2",
        },
    )
    assert signup_response.status_code == 200

    # Login as admin
    login_response = await test_client.post(
        "/users/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Fetch user by ID (using the ID from the previous signup)
    user_id = signup_response.json()["id"]
    response = await test_client.get(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "testuser2@example.com"


@pytest.mark.asyncio
async def test_delete_user_as_admin(test_client: AsyncClient, create_users):
    """
    Test that an admin user can delete a user.
    """
    # Sign up a user to be deleted
    signup_response = await test_client.post(
        "/users/signup",
        json={
            "email": "tobedeleted@example.com",
            "password": "password123",
            "name": "Delete",
            "surname": "User",
        },
    )
    assert signup_response.status_code == 200
    user_id = signup_response.json()["id"]

    # Login as admin
    login_response = await test_client.post(
        "/users/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Delete the user
    delete_response = await test_client.delete(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200

    # Ensure the user no longer exists
    response = await test_client.get(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_forbidden_access_for_non_admin(test_client: AsyncClient, create_users):
    """
    Test that a regular user cannot delete or access other users.
    """
    # Login as the regular user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "user@example.com", "password": "userpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Try to delete another user (should be forbidden)
    response = await test_client.delete(
        "/users/1",  # Assume user 1 is admin or another user
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

    # Try to get all users (should be forbidden)
    response = await test_client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_profile_as_manager(test_client: AsyncClient, create_users):
    """
    Test that a manager can update their own profile.
    """
    # Login as the manager
    login_response = await test_client.post(
        "/users/login",
        data={"username": "manager@example.com", "password": "managerpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Update the manager's profile
    update_response = await test_client.put(
        "/users/",
        json={"name": "UpdatedManager", "surname": "NewSurname"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "UpdatedManager"
    assert update_response.json()["surname"] == "NewSurname"
