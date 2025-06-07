"""Handles writing data to InfluxDB."""
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.domain.write_precision import WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config import get_influxdb_url, get_influxdb_token, get_influxdb_org, get_influxdb_bucket
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def write_data(data_points: list[dict]):
    """Writes list of data points to InfluxDB."""
    url = get_influxdb_url()
    token = get_influxdb_token()
    org = get_influxdb_org()
    bucket = get_influxdb_bucket()

    with InfluxDBClient(url=url, token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for entry in data_points:
            try:
                point = Point(entry["measurement"])
                for k, v in entry.get("fields", {}).items():
                    point = point.field(k, v)
                for k, v in entry.get("tags", {}).items():
                    point = point.tag(k, v)
                write_api.write(bucket=bucket, org=org, record=point)
                logger.info("Wrote point to InfluxDB: %s", point.to_line_protocol())
            except Exception as e:
                logger.exception("Failed to write point: %s", entry)
