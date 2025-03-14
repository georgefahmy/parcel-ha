"""Integration for Parcel tracking sensor."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, UPDATE_INTERVAL_SECONDS
from .coordinator import ParcelConfigEntry, ParcelUpdateCoordinator

PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)
SCAN_INTERVAL = timedelta(seconds=UPDATE_INTERVAL_SECONDS)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ParcelConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Parcel sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([RecentShipment(coordinator)])


class RecentShipment(SensorEntity):
    """Representation of a sensor that fetches the top value from an API."""

    def __init__(self, coordinator: ParcelUpdateCoordinator) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._hass_custom_attributes = {}
        self._attr_name = "Recent Parcel Shipment"
        self._attr_unique_id = "Recent_Parcel_Shipment"
        self._globalid = "Recent_Parcel_Shipment"
        self._attr_icon = "mdi:package"
        self._attr_state = None

    @property
    def state(self) -> Any:
        """Return the current state of the sensor."""
        return self._attr_state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._hass_custom_attributes

    async def async_update(self) -> None:
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
        if data := self.coordinator.data:
            self._attr_name = "Deliveries"
            for i, delivery in enumerate(data):
                # if len(self._attr_name) > 20:
                #     self._attr_name = f"{self._attr_name[:20]}..."
                try:
                    self._attr_state = delivery["events"][0]["event"]
                    try:
                        event_date = delivery["events"][0]["date"]
                    except KeyError:
                        event_date = "Unknown"
                    try:
                        event_location = delivery["events"][0]["location"]
                    except KeyError:
                        event_location = "Unknown"
                except KeyError:
                    self._attr_state = "Unknown"
                    event_date = "Unknown"
                    event_location = "Unknown"
                try:
                    description = delivery["description"]
                except KeyError:
                    description = "Parcel"
                try:
                    date_expected = delivery["date_expected"]
                except KeyError:
                    date_expected = "Unknown"

                self._hass_custom_attributes[i] = {
                    "description": description,
                    "latest_event": delivery["events"][0]["event"],
                    "tracking_number": delivery["tracking_number"],
                    "date_expected": date_expected.split(" ")[0],
                    "status_code": delivery["status_code"],
                    "carrier_code": delivery["carrier_code"],
                    "event_date": event_date,
                    "event_location": event_location,
                }
