"""Initializes the utilities package for the application.

Included utilities:
- setup_logger: Configures structured logging
- validate_data: Validates the structure and content of input data
- track_polling_metrics: Prometheus polling metrics (optional)
- track_request_metrics: Prometheus request metrics (optional)
- validate_environment_variables: Ensures required environment variables are set
- vault_client: Retrieves secrets from Vault
"""

from .setup_logger import setup_logger
from .track_polling_metrics import track_polling_metrics
from .track_request_metrics import track_request_metrics
from .validate_data import validate_data
from .validate_environment_variables import validate_environment_variables
from .vault_client import VaultClient

__all__ = [
    "validate_data",
    "track_polling_metrics",
    "track_request_metrics",
    "validate_environment_variables",
    "setup_logger",
    "VaultClient",
]

# Package-level logger (optional for internal utils usage)
logger = setup_logger(name="utils")
