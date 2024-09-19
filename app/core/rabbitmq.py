import aio_pika
from aio_pika import Message
import json
from app.core.settings import settings


class RabbitMQConnection:
    """Class to handle RabbitMQ connection and messaging."""

    def __init__(self, rabbitmq_url: str = None):
        self.rabbitmq_url = rabbitmq_url or settings.RABBITMQ_URL

    async def connect(self):
        """Connect to RabbitMQ server."""
        return await aio_pika.connect_robust(self.rabbitmq_url)

    async def send_message(self, queue_name: str, message_body: dict):
        """Send a message to the RabbitMQ queue."""
        connection = await self.connect()
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                Message(body=json.dumps(message_body).encode()),
                routing_key=queue_name,
            )


# Dependency to inject RabbitMQ connection where needed
async def get_rabbitmq_connection():
    return RabbitMQConnection(settings.RABBITMQ_URL)
