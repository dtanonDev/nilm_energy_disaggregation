"""Sensor platform for NILM Energy Disaggregation."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SOURCE_SENSOR
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN, 
    ATTR_CURRENT_POWER, 
    ATTR_CUMULATIVE_RUNTIME, 
    ATTR_DEVICE_STATE
)

LOGGER = logging.getLogger(__name__)

class NilmDeviceSensor(SensorEntity):
    """Representation of a NILM device sensor."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        source_sensor: str, 
        device_name: str, 
        initial_state: str = 'OFF'
    ):
        """Initialize the sensor."""
        self._attr_name = f"NILM {device_name}"
        self._attr_unique_id = f"{DOMAIN}_{device_name}"
        self._source_sensor = source_sensor
        self._current_power = 0
        self._cumulative_runtime = 0
        self._device_state = initial_state

    @property
    def state(self) -> StateType:
        """Return the state of the device."""
        return self._device_state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return {
            ATTR_CURRENT_POWER: self._current_power,
            ATTR_CUMULATIVE_RUNTIME: self._cumulative_runtime,
            ATTR_DEVICE_STATE: self._device_state
        }

    def update_state(self, power: float, timestamp: float):
        """Update the state of the device."""
        # Simple state detection logic (to be improved with ML model)
        if power > 10:  # Threshold for device being ON
            if self._device_state == 'OFF':
                self._device_state = 'ON'
                self._cumulative_runtime = 0
            self._cumulative_runtime += timestamp
        else:
            self._device_state = 'OFF'
        
        self._current_power = power
        self.async_write_ha_state()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the NILM sensor platform."""
    source_sensor = config_entry.data.get(CONF_SOURCE_SENSOR)
    
    # Initialize NILM model (placeholder for now)
    nilm_model = NilmModel()
    
    # Create a device sensor for each detected device
    device_sensors = []
    
    # Track changes in the source sensor
    @callback
    def sensor_state_listener(entity, old_state, new_state):
        if new_state is None:
            return
        
        try:
            current_power = float(new_state.state)
            
            # Use NILM model to detect devices
            detected_devices = nilm_model.predict(current_power)
            
            for device_name, device_power in detected_devices.items():
                # Find or create sensor for this device
                device_sensor = next(
                    (sensor for sensor in device_sensors if sensor._attr_name == f"NILM {device_name}"),
                    None
                )
                
                if device_sensor is None:
                    device_sensor = NilmDeviceSensor(
                        hass, 
                        source_sensor, 
                        device_name
                    )
                    device_sensors.append(device_sensor)
                    async_add_entities([device_sensor])
                
                # Update device sensor state
                device_sensor.update_state(device_power, 1.0)  # Timestamp placeholder
        
        except (TypeError, ValueError) as e:
            LOGGER.error(f"Error processing sensor state: {e}")
    
    # Start tracking the source sensor
    async_track_state_change(
        hass, 
        source_sensor, 
        sensor_state_listener
    )

class NilmModel:
    """Simple NILM model for device detection."""
    
    def __init__(self, sensitivity: float = 0.5):
        """Initialize the NILM model."""
        self._sensitivity = sensitivity
        self._model = RandomForestClassifier()
        self._scaler = StandardScaler()
        
        # Placeholder training data
        self._training_data = pd.DataFrame({
            'power': [50, 100, 200, 300, 500],
            'device': ['refrigerator', 'tv', 'microwave', 'oven', 'washing_machine']
        })
    
    def train(self, training_data: pd.DataFrame):
        """Train the NILM model."""
        # Preprocess data
        X = self._scaler.fit_transform(training_data['power'].values.reshape(-1, 1))
        y = training_data['device']
        
        # Train model
        self._model.fit(X, y)
    
    def predict(self, current_power: float) -> Dict[str, float]:
        """Predict devices from current power consumption."""
        # Simple device detection logic
        devices = {}
        
        # Predefined device power signatures (example)
        device_signatures = {
            'refrigerator': (50, 150),
            'tv': (80, 200),
            'microwave': (600, 1200),
            'oven': (1500, 2500),
            'washing_machine': (300, 800)
        }
        
        for device, (min_power, max_power) in device_signatures.items():
            if min_power <= current_power <= max_power:
                devices[device] = current_power
        
        return devices
