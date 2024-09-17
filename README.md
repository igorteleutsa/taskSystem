
# Ticket System API

## Features

- **Task management**: Create, edit, delete tasks with various fields (title, description, assignees, etc.).
- **Status tracking**: Track tasks with statuses like TODO, In Progress, and Done.
- **Email mock service**: Mock email service to notify users about task status updates.
- **Role-based access control**: Manage access permissions based on user roles.
- **RabbitMQ**: Integration with RabbitMQ for background task processing (future feature).
- **PostgreSQL**: Uses PostgreSQL as the database.
- **Alembic migrations**: For database migrations.

## Technology Stack

- **FastAPI**: Web framework
- **PostgreSQL**: Database
- **SQLAlchemy**: ORM for database access
- **Pydantic**: Data validation and settings management
- **RabbitMQ**: Message broker (to be integrated)
- **Docker**: Containerization of the application and services
- **Docker Compose**: Orchestration of multiple services (FastAPI, PostgreSQL, RabbitMQ)
- **Alembic**: (To be added) Database migration tool

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/igorteleutsa/taskSystem.git
cd taskSystem
```

### 2. Environment Setup

Copy the `.env.sample` file to `.env` and adjust the variables as needed.

```bash
cp .env.sample .env
```

### 3. Building and Running the Application

Using Docker Compose, you can quickly build and run the app, PostgreSQL, and RabbitMQ.

```bash
docker-compose up --build
```

- The app will be available at `http://localhost:8000`.
- The RabbitMQ Management UI will be available at `http://localhost:15672` (default user: `guest`, password: `guest`).

### 4. Running Migrations

After setting up Alembic for database migrations, use the following commands to run the migrations:

```bash
# Initialize the Alembic migrations
alembic upgrade head
```
## Endpoints

Here are some basic endpoints that are currently available in the application:

- **Root (`/`)**: Welcome message to verify that the app is running.
  
  ```
  GET /
  Response:
  {
    "message": "Welcome to the Task Tracker API!"
  }
  ```
  ### AUTH
- **Sign Up (/users/signup)**: Create a new user.
  ```
  POST /users/signup
  Request Body:
  {
  "email": "user@example.com",
  "password": "password123",
  "name": "John",
  "surname": "Doe"
  }
  
  Response:
  {
  "id": 1,
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "role": "user"
  }
  ```
- **Login (/users/login)**: Authenticate a user and get a JWT token.
  ```
  POST /users/login
  Request Body (form-data):
  {
    "username": "user@example.com",
    "password": "password123"
  }
  
  Response:
  {
    "access_token": "<token>",
    "token_type": "bearer"
  }

  ```
  ### User Endpoints
- **Get Current User (/users/me)**: Get the currently logged-in user.
  ```
  GET /users/me
  Response:
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John",
    "surname": "Doe",
    "role": "user"
  }
  ```
- **CRUD USER (/users/{user_id}) Admin can update another user`s details/ 
    delete user/get_user
   ```
    GET/PUT/DELETE /users/{user_id}
   ```
  

## Running Tests

To run the test suite:

1. Ensure that the `tests` directory is present.
2. Use a testing framework like `pytest` to run the tests.

```bash
# Example test run
pytest
```
