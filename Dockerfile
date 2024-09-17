# Use the official Python 3.10 image
FROM python:3.10

# Set the working directory in the container to /code
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements.txt /code/requirements.txt

# Copy the .env file for environment variables
COPY .env /code/

# Install Python dependencies using pip, without cache for a smaller image
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code into the working directory
COPY ./app /code/app

# Copy Alembic configuration and migrations for database management
COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic

# Optional: Copy test files to the container (can be used for testing later)
COPY ./tests /code/tests

# Run the FastAPI app with the main module
CMD ["python", "-m", "app.main"]
