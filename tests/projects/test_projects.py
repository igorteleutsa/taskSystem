import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.settings import settings


@pytest.mark.asyncio
async def test_create_project(test_client: AsyncClient, create_users):
    """Test that a user can create a project."""
    # Login as a regular user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "user@example.com", "password": "userpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a new project
    project_data = {
        "title": "New Project",
        "description": "This is a new project.",
    }
    response = await test_client.post(
        "/projects/", json=project_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    project = response.json()
    assert project["title"] == "New Project"
    assert project["description"] == "This is a new project."
    assert project["owner_id"] is not None


@pytest.mark.asyncio
async def test_get_project_by_owner(test_client: AsyncClient, create_users):
    """Test that the project owner can retrieve a project by ID."""
    # Login as user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "user@example.com", "password": "userpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a project to retrieve
    project_data = {
        "title": "Retrievable Project",
        "description": "This project will be retrieved.",
    }
    create_response = await test_client.post(
        "/projects/", json=project_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Retrieve the project by ID
    response = await test_client.get(
        f"/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    project = response.json()
    assert project["title"] == "Retrievable Project"


@pytest.mark.asyncio
async def test_update_project(test_client: AsyncClient, create_users):
    """Test that the project owner can update a project."""
    # Login as user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "user@example.com", "password": "userpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a project to update
    project_data = {
        "title": "Old Project",
        "description": "This project will be updated.",
    }
    create_response = await test_client.post(
        "/projects/", json=project_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Update the project
    update_data = {
        "title": "Updated Project",
        "description": "This project has been updated.",
    }
    update_response = await test_client.put(
        f"/projects/{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_response.status_code == 200
    updated_project = update_response.json()
    assert updated_project["title"] == "Updated Project"
    assert updated_project["description"] == "This project has been updated."


@pytest.mark.asyncio
async def test_delete_project(test_client: AsyncClient, create_users):
    """Test that the project owner can delete a project."""
    # Login as user
    login_response = await test_client.post(
        "/users/login",
        data={"username": "user@example.com", "password": "userpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a project to delete
    project_data = {
        "title": "Project to Delete",
        "description": "This project will be deleted.",
    }
    create_response = await test_client.post(
        "/projects/", json=project_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Delete the project
    delete_response = await test_client.delete(
        f"/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project deleted successfully"
