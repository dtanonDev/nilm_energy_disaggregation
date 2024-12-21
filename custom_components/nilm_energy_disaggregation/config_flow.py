"""Config flow for NILM Energy Disaggregation integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SOURCE_SENSOR
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class NilmEnergyDisaggregationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NILM Energy Disaggregation."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting async_step_user")
        _LOGGER.debug(f"User input: {user_input}")
        
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                _LOGGER.debug("Processing user input")
                # Validate source sensor
                source_sensor = user_input.get(CONF_SOURCE_SENSOR)
                _LOGGER.debug(f"Selected source sensor: {source_sensor}")
                
                # Create the entry
                _LOGGER.debug("Creating config entry")
                return self.async_create_entry(
                    title="NILM Energy Disaggregation",
                    data={
                        CONF_SOURCE_SENSOR: source_sensor,
                    }
                )
            except Exception as e:
                _LOGGER.error(f"Error in config flow: {str(e)}")
                _LOGGER.exception("Full exception details:")
                errors["base"] = "cannot_connect"

        # Create the form
        _LOGGER.debug("Creating configuration form")
        data_schema = vol.Schema({
            vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor",
                    multiple=False
                )
            )
        })

        _LOGGER.debug(f"Showing form with errors: {errors}")
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    async def async_step_import(self, config: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        _LOGGER.debug(f"Starting async_step_import with config: {config}")
        return await self.async_step_user(config)
