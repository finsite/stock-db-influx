"""Repo-specific configuration for stock-db-influx."""

from app.config_shared import *


def get_poller_name() -> str:
    """Return the name of the poller for this service."""
    return get_config_value("POLLER_NAME", "stock_db_influx")


def get_rabbitmq_queue() -> str:
    """Return the RabbitMQ queue name for this poller."""
    return get_config_value("RABBITMQ_QUEUE", "stock_db_influx_queue")


def get_dlq_name() -> str:
    """Return the Dead Letter Queue (DLQ) name for this poller."""
    return get_config_value("DLQ_NAME", "stock_db_influx_dlq")

"""Repo-specific configuration for stock-db-influx."""

from app.config_shared import *


def get_influxdb_bucket() -> str:
    """Return the InfluxDB bucket name to write data into.

    Returns:
        str: The bucket name from config or default.
    """
    return get_config_value("INFLUXDB_BUCKET", "poller_data")


def get_influxdb_measurement() -> str:
    """Return the InfluxDB measurement name used in this service.

    Returns:
        str: The measurement name from config or default.
    """
    return get_config_value("INFLUXDB_MEASUREMENT", "stock_prices")


def get_influxdb_org() -> str:
    """Return the InfluxDB organization name.

    Returns:
        str: The organization name from config or default.
    """
    return get_config_value("INFLUXDB_ORG", "default_org")


def get_influxdb_token() -> str:
    """Return the token used to authenticate to InfluxDB.

    Returns:
        str: The token from Vault or environment variable.
    """
    return get_secret_or_env("INFLUXDB_TOKEN")


def get_influxdb_url() -> str:
    """Return the base URL of the InfluxDB server.

    Returns:
        str: The URL from config or default.
    """
    return get_config_value("INFLUXDB_URL", "http://localhost:8086")
