"""Entry point for stock-db-influx."""
from app.utils.setup_logger import setup_logger
from app.processor import write_data  # or whatever module holds write_data()
from app.config import get_polling_interval
from app.queue_handler import start_queue_listener

logger = setup_logger(__name__)

def process(message: dict) -> None:
    logger.debug("Processing message: %s", message)
    write_data([message])

def main():
    logger.info("Starting stock-db-influx writer service...")
    interval = get_polling_interval()
    logger.info(f"Polling interval: {interval}s")
    start_queue_listener(process)

if __name__ == "__main__":
    main()
