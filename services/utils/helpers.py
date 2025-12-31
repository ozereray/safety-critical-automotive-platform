import os
import re
import math
from typing import List, Union, Any
from datetime import datetime, timezone

# --- Constants ---

# Standard VIN pattern (17 alphanumeric characters, excluding I, O, Q)
VIN_PATTERN = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')

# --- Data Validation Helpers ---

def validate_vin(vin: str) -> bool:
    """
    Validates if the provided string adheres to the standardized 17-character VIN format.
    Required for identifying the vehicle associated with sensor data streams.

    Args:
        vin: The Vehicle Identification Number string.

    Returns:
        True if the VIN is valid, False otherwise.
    """
    if not isinstance(vin, str) or len(vin) != 17:
        return False
    return bool(VIN_PATTERN.match(vin.upper()))

def is_valid_sensor_id(sensor_id: str) -> bool:
    """
    Checks if a sensor ID follows a basic alphanumeric standard expected
    in the automotive data streams (e.g., LIDAR_FRONT_001).
    Ensures structural integrity of key identifiers.
    """
    if not isinstance(sensor_id, str) or not sensor_id:
        return False
    # Allowing alphanumeric, underscores, and hyphens for sensor naming convention
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', sensor_id))

# --- Statistical and Mathematical Helpers (Crucial for SDICS) ---

def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
    """
    Calculates the Root Mean Square Error (RMSE) between actual sensor measurements
    and predicted (or calibrated target) values.

    RMSE is a key metric for quantifying deviation (sensor drift magnitude).

    Args:
        actual: List of actual observed measurements (e.g., Lidar point cloud coordinates).
        predicted: List of predicted or reference measurements (e.g., RANSAC inliers, Kalman filter output).

    Returns:
        The calculated RMSE value. Returns 0.0 if lists are empty or mismatch in size.
    """
    if len(actual) != len(predicted) or not actual:
        return 0.0

    n = len(actual)
    # Calculate the sum of squared differences
    squared_errors = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    mean_squared_error = sum(squared_errors) / n

    return math.sqrt(mean_squared_error)

def calculate_standard_deviation(data: List[float]) -> float:
    """
    Calculates the sample standard deviation of a dataset (N > 1).
    Used to characterize noise and stability of real-time sensor readings,
    feeding into statistical anomaly detection models.
    """
    if len(data) < 2:
        return 0.0

    mean = sum(data) / len(data)
    # Use N-1 for sample standard deviation
    variance = sum([(x - mean) ** 2 for x in data]) / (len(data) - 1)
    return math.sqrt(variance)

# --- Time and Configuration Helpers ---

def convert_timestamp_to_iso(timestamp_ms: Union[int, float]) -> str:
    """
    Converts a Unix timestamp (milliseconds) into a standardized ISO 8601 string
    with UTC timezone, ensuring accurate temporal alignment in log streams.

    Args:
        timestamp_ms: Timestamp in milliseconds.

    Returns:
        ISO 8601 formatted string (e.g., '2023-10-27T10:30:00.123456+00:00').
    """
    if timestamp_ms is None:
        # Return current UTC time if input is None, helpful for logging
        return datetime.now(timezone.utc).isoformat()

    timestamp_s = timestamp_ms / 1000.0
    dt_object = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
    return dt_object.isoformat()

def load_environment_config(key: str, default: Any = None) -> Any:
    """
    Safely retrieves an environment variable, providing a fallback default value.
    Crucial for runtime configuration in containerized microservices.

    Args:
        key: The environment variable key (str).
        default: The default value if the key is not found (Any).

    Returns:
        The environment variable value or the default.
    """
    return os.environ.get(key, default)

def get_service_name() -> str:
    """
    Retrieves the unique service name for logging and metric tagging.
    """
    return load_environment_config("AURIX_SERVICE_NAME", "AURIX_SDICS")