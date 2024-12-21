"""Config flow for NILM Energy Disaggregation integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_NAME,
    CONF_SOURCE_SENSOR,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector, config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    CONF_SENSITIVITY,
    CONF_MIN_POWER,
    CONF_DEVICES_CONFIG,
    DEFAULT_SENSITIVITY,
    DEFAULT_MIN_POWER,
    DEVICE_TYPES,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class NilmEnergyDisaggregationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NILM Energy Disaggregation."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.data = {}
        self.options = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting async_step_user")
        _LOGGER.debug(f"User input: {user_input}")
        
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                _LOGGER.debug("Processing user input")
                # Store basic configuration
                self.data = {
                    CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                    CONF_SOURCE_SENSOR: user_input[CONF_SOURCE_SENSOR],
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                }
                
                # Move to device configuration
                return await self.async_step_devices()
                
            except Exception as e:
                _LOGGER.error(f"Error in config flow: {str(e)}")
                _LOGGER.exception("Full exception details:")
                errors["base"] = "cannot_connect"

        # Create the form
        _LOGGER.debug("Creating configuration form")
        data_schema = vol.Schema({
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor",
                    device_class="energy",
                    multiple=False
                )
            ),
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=3600,
                    step=5,
                    unit_of_time="seconds",
                    mode="slider"
                )
            ),
        })

        _LOGGER.debug(f"Showing form with errors: {errors}")
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "default_name": DEFAULT_NAME,
                "default_scan_interval": str(DEFAULT_SCAN_INTERVAL),
            },
        )

    async def async_step_devices(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Configure NILM device detection settings."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                # Store device configuration
                self.data.update({
                    CONF_SENSITIVITY: user_input.get(CONF_SENSITIVITY, DEFAULT_SENSITIVITY),
                    CONF_MIN_POWER: user_input.get(CONF_MIN_POWER, DEFAULT_MIN_POWER),
                    CONF_DEVICES_CONFIG: {
                        device: user_input.get(f"enable_{device}", True)
                        for device in DEVICE_TYPES
                    }
                })
                
                # Create the config entry
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data
                )
                
            except Exception as e:
                _LOGGER.error(f"Error configuring devices: {str(e)}")
                errors["base"] = "device_config_error"

        # Create device configuration form
        device_schema = {
            vol.Optional(CONF_SENSITIVITY, default=DEFAULT_SENSITIVITY): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    mode="slider"
                )
            ),
            vol.Optional(CONF_MIN_POWER, default=DEFAULT_MIN_POWER): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100,
                    step=1,
                    unit_of_measurement="W",
                    mode="box"
                )
            ),
        }

        # Add toggles for each device type
        for device in DEVICE_TYPES:
            device_schema[vol.Optional(f"enable_{device}", default=True)] = selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            )

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(device_schema),
            errors=errors,
            description_placeholders={
                "default_sensitivity": str(DEFAULT_SENSITIVITY),
                "default_min_power": str(DEFAULT_MIN_POWER),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=3600,
                    step=5,
                    unit_of_time="seconds",
                    mode="slider"
                )
            ),
            vol.Optional(
                CONF_SENSITIVITY,
                default=self.config_entry.options.get(
                    CONF_SENSITIVITY, DEFAULT_SENSITIVITY
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    mode="slider"
                )
            ),
            vol.Optional(
                CONF_MIN_POWER,
                default=self.config_entry.options.get(
                    CONF_MIN_POWER, DEFAULT_MIN_POWER
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100,
                    step=1,
                    unit_of_measurement="W",
                    mode="box"
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
