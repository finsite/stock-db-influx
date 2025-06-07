"""Writes processed analysis data to InfluxDB 2.x with batching and retries."""

from typing import Any

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from influxdb_client.domain.write_precision import WritePrecision
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.config import (
    get_influxdb_bucket,
    get_influxdb_measurement,
    get_influxdb_org,
    get_influxdb_token,
    get_influxdb_url,
)
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

_client: InfluxDBClient | None = None
_write_api: WriteApi | None = None


def _get_write_api() -> WriteApi:
    global _client, _write_api
    if _client is None:
        logger.info("🔌 Initializing InfluxDB client...")
        _client = InfluxDBClient(
            url=get_influxdb_url(),
            token=get_influxdb_token(),
            org=get_influxdb_org(),
        )
        _write_api = _client.write_api(write_options=SYNCHRONOUS)

    if _write_api is None:
        raise RuntimeError("InfluxDB Write API failed to initialize.")

    return _write_api


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_fixed(5),
    stop=stop_after_attempt(5),
)
def write_batch_to_influx(data_batch: list[dict[str, Any]]) -> None:
    """Writes a batch of records to InfluxDB."""
    if not data_batch:
        logger.warning("🟡 No data to write to InfluxDB.")
        return

    try:
        write_api = _get_write_api()
        bucket = get_influxdb_bucket()
        org = get_influxdb_org()
        measurement = get_influxdb_measurement()

        points: list[Point] = []

        for record in data_batch:
            symbol = record.get("symbol")
            source = record.get("source", "unknown")
            timestamp = record.get("timestamp")  # ISO8601 or datetime
            analysis = record.get("analysis", {})

            if not isinstance(analysis, dict):
                logger.warning("⚠️ Skipping invalid analysis record: %s", record)
                continue

            try:
                point = (
                    Point(measurement)
                    .tag("symbol", symbol)
                    .tag("source", source)
                    .time(timestamp, WritePrecision.NS)
                )
                for k, v in analysis.items():
                    point.field(k, v)
                points.append(point)
            except Exception:
                logger.exception("❌ Failed to build point from record: %s", record)

        if not points:
            logger.warning("⚠️ No valid points to write to InfluxDB.")
            return

        write_api.write(bucket=bucket, org=org, record=points)
        logger.info("✅ Wrote %d points to InfluxDB", len(points))

    except Exception as e:
        logger.exception("❌ Failed to write batch to InfluxDB: %s", e)
        raise
