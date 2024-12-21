"""Sensor platform for NILM Energy Disaggregation."""
from __future__ import annotations

import logging
from typing import Any, Dict, List
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_SOURCE_SENSOR,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    ATTR_CURRENT_POWER,
    ATTR_CUMULATIVE_RUNTIME,
    ATTR_DEVICE_STATE,
    ATTR_DAILY_ENERGY,
    ATTR_LAST_UPDATE,
    ATTR_DETECTION_CONFIDENCE
)

LOGGER = logging.getLogger(__name__)

class NilmDeviceSensor(SensorEntity):
    """Representation of a NILM device sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        hass: HomeAssistant,
        source_sensor: str,
        device_name: str,
        initial_state: str = "OFF"
    ):
        """Initialize the sensor."""
        self._attr_name = f"NILM {device_name}"
        self._attr_unique_id = f"{DOMAIN}_{device_name}"
        self._source_sensor = source_sensor
        self._current_power = 0.0
        self._cumulative_runtime = timedelta()
        self._device_state = initial_state
        self._daily_energy = 0.0  # kWh
        self._last_update = dt_util.utcnow()
        self._detection_confidence = 0.0
        self._last_power_values = []  # Store last N power values for smoothing

    @property
    def native_value(self) -> float:
        """Return the current power consumption."""
        return self._current_power

    @property
    def state(self) -> StateType:
        """Return the state of the device."""
        return self._device_state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return {
            ATTR_CURRENT_POWER: self._current_power,
            ATTR_CUMULATIVE_RUNTIME: str(self._cumulative_runtime),
            ATTR_DEVICE_STATE: self._device_state,
            ATTR_DAILY_ENERGY: round(self._daily_energy, 3),
            ATTR_LAST_UPDATE: self._last_update.isoformat(),
            ATTR_DETECTION_CONFIDENCE: round(self._detection_confidence * 100, 1)
        }

    def update_state(self, power: float, confidence: float, timestamp: datetime):
        """Update the state of the device."""
        # Update power with smoothing
        self._last_power_values.append(power)
        if len(self._last_power_values) > 5:  # Keep last 5 values
            self._last_power_values.pop(0)
        self._current_power = np.mean(self._last_power_values)
        
        # Update confidence
        self._detection_confidence = confidence
        
        # Calculate time since last update
        time_diff = timestamp - self._last_update
        self._last_update = timestamp
        
        # Update state and runtime
        if power > 10:  # Threshold for device being ON
            if self._device_state == "OFF":
                self._device_state = "ON"
            self._cumulative_runtime += time_diff
            
            # Calculate energy consumption (kWh)
            energy_kwh = (power * time_diff.total_seconds()) / (1000 * 3600)
            self._daily_energy += energy_kwh
        else:
            self._device_state = "OFF"
        
        # Reset daily energy at midnight
        if timestamp.hour == 0 and timestamp.minute == 0:
            self._daily_energy = 0.0
        
        self.async_write_ha_state()

class NilmModel:
    """NILM model for device detection."""

    def __init__(self, sensitivity: float = 0.5):
        """Initialize the NILM model."""
        self._sensitivity = sensitivity
        self._model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self._scaler = StandardScaler()
        
        # Example device signatures
        self._device_signatures = {
            "refrigerator": {"min_power": 40, "max_power": 100, "cycle_time": 30},
            "tv": {"min_power": 80, "max_power": 150, "cycle_time": 0},
            "microwave": {"min_power": 800, "max_power": 1200, "cycle_time": 0},
            "washing_machine": {"min_power": 300, "max_power": 500, "cycle_time": 45},
            "dishwasher": {"min_power": 200, "max_power": 400, "cycle_time": 60}
        }
        
        # Initialize training data with device signatures
        power_values = []
        device_labels = []
        for device, signature in self._device_signatures.items():
            # Generate sample points within device power range
            powers = np.linspace(
                signature["min_power"],
                signature["max_power"],
                20
            )
            power_values.extend(powers)
            device_labels.extend([device] * 20)
        
        self._training_data = pd.DataFrame({
            "power": power_values,
            "device": device_labels
        })
        
        # Train initial model
        self.train(self._training_data)

    def train(self, training_data: pd.DataFrame) -> None:
        """Train the NILM model."""
        X = training_data[["power"]].values
        y = training_data["device"].values
        
        # Scale features
        self._scaler.fit(X)
        X_scaled = self._scaler.transform(X)
        
        # Train model
        self._model.fit(X_scaled, y)

    def predict(self, current_power: float) -> Dict[str, Dict[str, float]]:
        """Predict devices from current power consumption."""
        # Scale input power
        power_scaled = self._scaler.transform([[current_power]])
        
        # Get model predictions and probabilities
        device = self._model.predict(power_scaled)[0]
        probabilities = self._model.predict_proba(power_scaled)[0]
        confidence = max(probabilities)
        
        # Only return predictions above sensitivity threshold
        if confidence > self._sensitivity:
            return {device: {"power": current_power, "confidence": confidence}}
        return {}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the NILM sensor platform."""
    source_sensor = config_entry.data.get(CONF_SOURCE_SENSOR)
    
    # Initialize NILM model
    nilm_model = NilmModel(sensitivity=0.6)
    
    # Create sensors for each potential device
    device_sensors = {
        device: NilmDeviceSensor(hass, source_sensor, device)
        for device in nilm_model._device_signatures.keys()
    }
    
    async_add_entities(device_sensors.values(), True)
    
    @callback
    def sensor_state_listener(entity_id: str, old_state: str, new_state: str) -> None:
        """Handle changes in source sensor state."""
        if new_state is None:
            return
        
        try:
            current_power = float(new_state.state)
            current_time = dt_util.utcnow()
            
            # Use NILM model to detect devices
            detected_devices = nilm_model.predict(current_power)
            
            # Update device states
            for device_name, device_data in detected_devices.items():
                if device_name in device_sensors:
                    device_sensors[device_name].update_state(
                        device_data["power"],
                        device_data["confidence"],
                        current_time
                    )
            
            # Update inactive devices
            for device_name, sensor in device_sensors.items():
                if device_name not in detected_devices:
                    sensor.update_state(0.0, 0.0, current_time)
        
        except ValueError as err:
            LOGGER.error("Error processing sensor data: %s", err)
        except Exception as err:
            LOGGER.exception("Unexpected error in NILM processing: %s", err)
    
    # Start monitoring the source sensor
    async_track_state_change(
        hass,
        source_sensor,
        sensor_state_listener
    )
