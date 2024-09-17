from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    # Application settings
    UNSEPARATED_CORS_ORIGINS: str
    HOST: str
    PORT: int
    RELOAD: bool = True if 1 else False

    # RabbitMQ settings
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str
    RABBITMQ_MANAGEMENT_PORT: int

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(env_file=".env")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return self.UNSEPARATED_CORS_ORIGINS.split(",")

    @property
    def RABBITMQ_URL(self) -> str:
        # The AMQP URL for RabbitMQ remains the same for async libraries like aio-pika
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"
        )

    @property
    def RABBITMQ_MANAGEMENT_URL(self) -> str:
        return f"http://{self.RABBITMQ_HOST}:{self.RABBITMQ_MANAGEMENT_PORT}"


settings = Settings()
