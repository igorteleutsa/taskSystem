from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from app.tickets.schemas import (
    TicketCreate,
    TicketUpdate,
    ExecutorAssign,
    TicketStatusUpdate,
)
from app.tickets.models import TicketStatus


@pytest.mark.asyncio
async def test_create_ticket(test_client: AsyncClient, create_project, manager_user):
    """Test creating a ticket."""
    project_id, token = await create_project

    # Create ticket data
    ticket_data = TicketCreate(
        title="New Ticket",
        description="This is a test ticket",
        priority=3,
        status="todo",
        project_id=project_id,
    )

    # Create the ticket
    response = await test_client.post(
        "/tickets/",
        json=ticket_data.dict(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Ticket"


@pytest.mark.asyncio
async def test_get_ticket(test_client: AsyncClient, create_ticket):
    """Test retrieving a ticket by its ID."""
    ticket_id, token = await create_ticket

    response = await test_client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    ticket = response.json()
    assert ticket["id"] == ticket_id
    assert ticket["title"] == "New Ticket"


@pytest.mark.asyncio
async def test_update_ticket(test_client: AsyncClient, create_ticket):
    """Test updating a ticket."""
    ticket_id, token = await create_ticket

    update_data = TicketUpdate(
        title="Updated Ticket",
        description="Updated description",
        priority=2,
    )

    response = await test_client.put(
        f"/tickets/{ticket_id}",
        json=update_data.dict(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    updated_ticket = response.json()
    assert updated_ticket["title"] == "Updated Ticket"


@pytest.mark.asyncio
async def test_add_and_remove_executor(
    test_client: AsyncClient, create_ticket, manager_user
):
    """Test adding an executor to a ticket."""
    ticket_id, token = await create_ticket
    manager_id, manager_token = await manager_user

    # Get the project ID from the ticket (assuming this information is available)
    ticket_response = await test_client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ticket_response.status_code == 200
    project_id = ticket_response.json()["project_id"]

    # Add the manager as a member of the project before assigning as executor
    add_member_response = await test_client.post(
        f"/projects/{project_id}/members",
        json={"user_id": manager_id},
        headers={
            "Authorization": f"Bearer {token}"
        },  # Assume token belongs to the owner
    )
    assert add_member_response.status_code == 200

    # Now, assign the manager as an executor to the ticket
    executor_data = ExecutorAssign(user_id=manager_id)

    response = await test_client.post(
        f"/tickets/{ticket_id}/executors",
        json=executor_data.dict(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    response = await test_client.get(
        f"/tickets/{ticket_id}/executors",
        headers={"Authorization": f"Bearer {token}"},
    )
    executor_ids = [executor.get("id") for executor in response.json()]
    assert manager_id in executor_ids

    response = await test_client.delete(
        f"/tickets/{ticket_id}/executors/{manager_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    response = await test_client.get(
        f"/tickets/{ticket_id}/executors",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["detail"] == "No executors found for this ticket."


@pytest.mark.asyncio
async def test_change_ticket_status(mocker, test_client, create_ticket):
    """Test changing the status of a ticket with RabbitMQ mocked."""
    ticket_id, token = await create_ticket

    # Mock RabbitMQ's send_message function
    mock_rabbitmq = mocker.patch(
        "app.core.rabbitmq.RabbitMQConnection.send_message", new_callable=AsyncMock
    )

    new_status = TicketStatusUpdate(new_status="in_progress")

    response = await test_client.put(
        f"/tickets/{ticket_id}/status",
        json=new_status.dict(),  # Ensure we pass a dictionary
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    updated_ticket = response.json()
    assert updated_ticket["status"] == "in_progress"

    # Ensure RabbitMQ message was called once with expected parameters
    mock_rabbitmq.assert_called_once_with(
        queue_name="ticket_updates",
        message_body=mocker.ANY,  # Mock the message body to check if it was called
    )


@pytest.mark.asyncio
async def test_delete_ticket(test_client: AsyncClient, create_ticket):
    """Test deleting a ticket."""
    ticket_id, token = await create_ticket

    response = await test_client.delete(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Confirm the ticket no longer exists
    get_response = await test_client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
