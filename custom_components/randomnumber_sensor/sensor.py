import random
import datetime
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors from a config entry."""
    config = {**entry.data, **entry.options}
    
    # We create two sensors: "Alpha" and "Beta"
    sensors = [
        RandomSensor(hass, entry, config, "Alpha"),
        RandomSensor(hass, entry, config, "Beta"),
    ]
    
    async_add_entities(sensors)

class RandomSensor(SensorEntity):
    """Representation of a Random Sensor."""
    
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "pts" # Required for statistics

    def __init__(self, hass, entry, config, suffix):
        self.hass = hass
        self._entry = entry
        self._config = config
        self._suffix = suffix
        
        # Unique ID and Name
        self._attr_name = f"{config['name']} {suffix}"
        self._attr_unique_id = f"{entry.entry_id}_random_{suffix.lower()}"
        
        # Group both sensors under one device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=config["name"],
            manufacturer="Custom Integration",
            model="Random Generator",
        )

        self._min = config[CONF_MIN]
        self._max = config[CONF_MAX]
        self._interval = config[CONF_INTERVAL]
        self._state = None

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        await self._update_state()
        
        # Schedule updates
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._update_state, datetime.timedelta(seconds=self._interval)
            )
        )
        
        # Check if we need to backfill history
        # We check the entry data to see if this specific sensor was backfilled
        backfilled_key = f"backfilled_{self._suffix.lower()}"
        if not self._entry.data.get(backfilled_key):
            await self.async_backfill_history()
            
            # Mark this sensor as backfilled in the entry
            new_data = {**self._entry.data, backfilled_key: True}
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)

    async def _update_state(self, _=None):
        """Update the state of the sensor."""
        self._state = random.randint(self._min, self._max)
        self.async_write_ha_state()

    async def async_backfill_history(self):
        """Inject historical data points aligned to the top of the hour."""
        count = self._config.get(CONF_HISTORIC_ITEMS, 0)
        if count <= 0:
            return

        # Start from the current hour, minutes/seconds set to 0
        now = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)
        statistics = []
        
        for i in range(count, 0, -1):
            # Move back X hours
            past_time = now - datetime.timedelta(hours=i)
            val = random.randint(self._min, self._max)
            
            statistics.append(
                StatisticData(
                    start=past_time,
                    state=val,
                    mean=val
                )
            )

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=self._attr_name,
            source="recorder",
            statistic_id=self.entity_id,
            unit_of_measurement=self._attr_native_unit_of_measurement,
            mean_type="arithmetic"
        )

        async_import_statistics(self.hass, metadata, statistics)