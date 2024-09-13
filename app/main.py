import uvicorn
import logging
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.core.router import router as api_router

# Initialize logging
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
app = FastAPI(
    title="Ticket System",
    description="A simplified task tracker like Trello or Jira",
    version="1.0.0",
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(api_router)


# FastAPI Startup Event
@app.on_event("startup")
async def on_startup():
    # Initialize anything needed at app startup
    logger.info("Starting up the FastAPI application...")
    # Example: Setup DB connections, RabbitMQ connections, etc.
    # You can initialize database or message queues here if necessary
    # e.g., await init_db()


# FastAPI Shutdown Event
@app.on_event("shutdown")
async def on_shutdown():
    # Perform any necessary cleanup tasks on shutdown
    logger.info("Shutting down the FastAPI application...")
    # Example: Close DB connections, gracefully shut down RabbitMQ, etc.
    # e.g., await close_db()


# Custom logging configuration (can also be defined in a separate logging config file)
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # You can set this to logging.DEBUG for more detailed output
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    # Set up Uvicorn's loggers to use the same format
    uvicorn_log = logging.getLogger("uvicorn")
    uvicorn_log.setLevel(logging.INFO)
    uvicorn_log.handlers = logging.getLogger().handlers


# Main entry point
if __name__ == "__main__":
    setup_logging()
    logger.info("Starting Uvicorn server...")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info",  # This sets the logging level for Uvicorn
    )
