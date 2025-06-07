"""Generic queue handler for RabbitMQ or SQS."""
import json
import time
import boto3
import pika
from botocore.exceptions import BotoCoreError, NoCredentialsError
from pika.exceptions import AMQPConnectionError

from app import config
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


def start_queue_listener(callback):
    """Dispatch to the appropriate queue listener based on config."""
    queue_type = config.get_queue_type().lower()

    if queue_type == "rabbitmq":
        _start_rabbitmq_listener(callback)
    elif queue_type == "sqs":
        _start_sqs_listener(callback)
    else:
        raise ValueError(f"Unsupported QUEUE_TYPE: {queue_type}")


def _start_rabbitmq_listener(callback):
    """Connect to RabbitMQ and consume messages."""
    credentials = pika.PlainCredentials(
        config.get_rabbitmq_user(),
        config.get_rabbitmq_password(),
    )
    parameters = pika.ConnectionParameters(
        host=config.get_rabbitmq_host(),
        port=config.get_rabbitmq_port(),
        virtual_host=config.get_rabbitmq_vhost(),
        credentials=credentials,
        blocked_connection_timeout=30,
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    queue_name = config.get_rabbitmq_queue()
    channel.queue_declare(queue=queue_name, durable=True)

    def on_message(ch, method, properties, body):
        try:
            message = json.loads(body)
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.exception("❌ Failed to process RabbitMQ message")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)

    logger.info("📡 Listening on RabbitMQ queue: %s", queue_name)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping RabbitMQ listener...")
        channel.stop_consuming()
        connection.close()


def _start_sqs_listener(callback):
    """Poll SQS and process messages."""
    queue_url = config.get_sqs_queue_url()
    region = config.get_sqs_region()
    polling_interval = config.get_polling_interval()
    batch_size = config.get_batch_size()

    try:
        sqs_client = boto3.client("sqs", region_name=region)
    except (BotoCoreError, NoCredentialsError) as e:
        logger.error("Failed to initialize SQS client: %s", e)
        return

    logger.info("📡 Polling SQS queue: %s", queue_url)

    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=batch_size,
                WaitTimeSeconds=10,
            )

            for msg in response.get("Messages", []):
                try:
                    message = json.loads(msg["Body"])
                    callback(message)

                    sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
                    logger.info("✅ Deleted SQS message: %s", msg.get("MessageId"))
                except Exception as e:
                    logger.exception("❌ Failed to process SQS message")

        except Exception as e:
            logger.error("SQS polling error: %s", e)
            time.sleep(polling_interval)
