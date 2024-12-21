"""Constants for the NILM Energy Disaggregation integration."""
from homeassistant.const import Platform

DOMAIN = "nilm_energy_disaggregation"

# Platforms that the integration supports
PLATFORMS = [Platform.SENSOR]

# Configuration keys
CONF_MODEL_PATH = "model_path"
CONF_SENSITIVITY = "sensitivity"

# Default values
DEFAULT_SENSITIVITY = 0.5
DEFAULT_MODEL_PATH = "nilm_model.pkl"

# Attributes for device entities
ATTR_CURRENT_POWER = "current_power"
ATTR_CUMULATIVE_RUNTIME = "cumulative_runtime"
ATTR_DEVICE_STATE = "device_state"

# Logging
LOGGER_NAME = "nilm_energy_disaggregation"
