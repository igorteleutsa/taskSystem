import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.settings import settings


@pytest.mark.asyncio
async def test_add_member_to_project(test_client: AsyncClient, create_project):
    """Test adding a member to a project."""
    project_id, token = await create_project

    # Login as manager to get manager ID
    login_response = await test_client.post(
        "/users/login",
        data={"username": "manager@example.com", "password": "managerpassword"},
    )
    assert login_response.status_code == 200
    manager_token = login_response.json()["access_token"]

    # Decode the token to extract manager's user ID
    decoded_token = jwt.decode(
        manager_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    manager_id = decoded_token["id"]

    # Add the manager as a member to the project
    response = await test_client.post(
        f"/projects/{project_id}/members",
        json={"user_id": manager_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    response = await test_client.get(
        f"/projects/{project_id}/members", headers={"Authorization": f"Bearer {token}"}
    )
    assert manager_id in [member["id"] for member in response.json()]


@pytest.mark.asyncio
async def test_remove_member_from_project(test_client: AsyncClient, create_project):
    """Test removing a member from a project."""
    project_id, token = await create_project

    # Login as manager to get manager ID
    login_response = await test_client.post(
        "/users/login",
        data={"username": "manager@example.com", "password": "managerpassword"},
    )
    assert login_response.status_code == 200
    manager_token = login_response.json()["access_token"]

    # Decode the token to extract manager's user ID
    decoded_token = jwt.decode(
        manager_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    manager_id = decoded_token["id"]

    # Add the manager as a member first
    response = await test_client.post(
        f"/projects/{project_id}/members",
        json={"user_id": manager_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Remove the manager from the project
    remove_response = await test_client.delete(
        f"/projects/{project_id}/members/{manager_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert remove_response.status_code == 200
