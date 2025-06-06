"""Entry point for stock-db-influx writer service."""

import sys
import time

from utils.setup_logger import setup_logger

from app.config import get_environment, get_poller_name, get_polling_interval
from app.db_writer import write_batch_to_influx
from app.queue_handler import consume_messages

logger = setup_logger(__name__)


def process_batch(batch: list[dict]) -> None:
    """Callback to process and write a batch of messages to InfluxDB."""
    if not batch:
        logger.warning("⚠️ Received empty batch — skipping.")
        return

    logger.info("📦 Received batch of %d messages", len(batch))

    try:
        write_batch_to_influx(batch)
        logger.info("✅ Successfully wrote batch to InfluxDB.")
    except Exception as e:
        logger.exception("❌ Failed to write batch to InfluxDB: %s", e)
        raise


def main() -> None:
    logger.info("🚀 Starting stock-db-influx writer service...")
    logger.info(f"🌍 Environment: {get_environment()}")
    logger.info(f"📛 Poller Name: {get_poller_name()}")
    logger.info(f"⏱ Polling Interval: {get_polling_interval()}s")

    try:
        consume_messages(callback=process_batch)
    except KeyboardInterrupt:
        logger.info("🛑 Graceful shutdown requested via keyboard interrupt.")
        sys.exit(0)
    except Exception as e:
        logger.exception("❌ Unhandled exception in main(): %s", e)
        raise


if __name__ == "__main__":
    restart_attempts = 0

    while True:
        try:
            main()
            logger.warning("⚠️ main() exited unexpectedly. Restarting...")
        except Exception as e:
            restart_attempts += 1
            logger.error("🔁 Restart #%d due to failure: %s", restart_attempts, e)

            if restart_attempts >= 5:
                logger.critical("🚨 Too many failures — exiting.")
                sys.exit(1)

            time.sleep(5)
