"""Constants for the NILM Energy Disaggregation integration."""
from homeassistant.const import Platform

DOMAIN = "nilm_energy_disaggregation"

# Platforms that the integration supports
PLATFORMS = [Platform.SENSOR]

# Configuration
CONF_SENSITIVITY = "sensitivity"
CONF_MIN_POWER = "min_power"
CONF_DEVICES_CONFIG = "devices_config"

# Attributes for device entities
ATTR_CURRENT_POWER = "current_power"
ATTR_CUMULATIVE_RUNTIME = "cumulative_runtime"
ATTR_DEVICE_STATE = "device_state"
ATTR_DAILY_ENERGY = "daily_energy"
ATTR_LAST_UPDATE = "last_update"
ATTR_DETECTION_CONFIDENCE = "detection_confidence"

# Default values
DEFAULT_NAME = "NILM Energy Disaggregation"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_SENSITIVITY = 0.6
DEFAULT_MIN_POWER = 10  # watts

# Device types
DEVICE_TYPES = [
    "refrigerator",
    "tv",
    "microwave",
    "washing_machine",
    "dishwasher",
    "oven",
    "dryer",
    "air_conditioner",
    "water_heater",
]

# Device signatures (power ranges in watts)
DEVICE_SIGNATURES = {
    "refrigerator": {"min_power": 40, "max_power": 100, "cycle_time": 30},
    "tv": {"min_power": 80, "max_power": 150, "cycle_time": 0},
    "microwave": {"min_power": 800, "max_power": 1200, "cycle_time": 0},
    "washing_machine": {"min_power": 300, "max_power": 500, "cycle_time": 45},
    "dishwasher": {"min_power": 200, "max_power": 400, "cycle_time": 60},
    "oven": {"min_power": 1500, "max_power": 2500, "cycle_time": 0},
    "dryer": {"min_power": 2000, "max_power": 4000, "cycle_time": 45},
    "air_conditioner": {"min_power": 500, "max_power": 1500, "cycle_time": 20},
    "water_heater": {"min_power": 1000, "max_power": 3000, "cycle_time": 0},
}

# Logging
LOGGER_NAME = "nilm_energy_disaggregation"
