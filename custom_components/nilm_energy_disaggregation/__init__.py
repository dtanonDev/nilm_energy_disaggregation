"""NILM Energy Disaggregation Integration for Home Assistant."""
from __future__ import annotations

import logging
import sys
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SOURCE_SENSOR
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS

# Setup logger with debug level
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Add a file handler to write detailed logs
handler = logging.FileHandler("nilm_debug.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
_LOGGER.addHandler(handler)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the NILM Energy Disaggregation component from configuration.yaml."""
    try:
        _LOGGER.debug("Starting async_setup")
        _LOGGER.debug(f"Python version: {sys.version}")
        _LOGGER.debug(f"Config: {config}")
        
        # Store configuration 
        hass.data.setdefault(DOMAIN, {})
        
        # If a configuration exists in configuration.yaml, handle it
        if DOMAIN in config:
            source_sensor = config[DOMAIN].get(CONF_SOURCE_SENSOR)
            _LOGGER.info(f"NILM Energy Disaggregation configured with source sensor: {source_sensor}")
            _LOGGER.debug(f"Full domain config: {config[DOMAIN]}")
        
        _LOGGER.debug("async_setup completed successfully")
        return True
        
    except Exception as e:
        _LOGGER.error(f"Error in async_setup: {str(e)}")
        _LOGGER.exception("Full exception details:")
        return False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for NILM Energy Disaggregation."""
    try:
        _LOGGER.debug(f"Starting async_setup_entry with entry_id: {entry.entry_id}")
        _LOGGER.debug(f"Entry data: {entry.data}")
        
        # Store the config entry in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = entry.data
        
        _LOGGER.debug(f"Setting up platforms: {PLATFORMS}")
        # Setup platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        _LOGGER.debug("async_setup_entry completed successfully")
        return True
        
    except Exception as e:
        _LOGGER.error(f"Error in async_setup_entry: {str(e)}")
        _LOGGER.exception("Full exception details:")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        _LOGGER.debug(f"Starting async_unload_entry for entry_id: {entry.entry_id}")
        
        # Unload platforms
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        
        # Remove config entry data
        if unload_ok:
            _LOGGER.debug("Platforms unloaded successfully")
            hass.data[DOMAIN].pop(entry.entry_id)
            _LOGGER.debug(f"Removed entry {entry.entry_id} from hass.data")
        else:
            _LOGGER.warning("Failed to unload some platforms")
        
        return unload_ok
        
    except Exception as e:
        _LOGGER.error(f"Error in async_unload_entry: {str(e)}")
        _LOGGER.exception("Full exception details:")
        return False
