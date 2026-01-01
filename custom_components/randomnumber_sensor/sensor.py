import random
import datetime
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

async def async_setup_entry(hass, entry, async_add_entities):
    config = {**entry.data, **entry.options}
    
    # Create TWO sensors for this one device
    sensors = [
        RandomSensor(hass, config, entry.entry_id, "A"),
        RandomSensor(hass, config, entry.entry_id, "B"),
    ]
    
    async_add_entities(sensors)
    
    # Backfill both
    if "backfilled" not in entry.data:
        for sensor in sensors:
            await sensor.async_backfill_history()
        hass.config_entries.async_update_entry(entry, data={**entry.data, "backfilled": True})

class RandomSensor(SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "pts"  # REQUIRED for statistics to show up reliably

    def __init__(self, hass, config, entry_id, suffix):
        self.hass = hass
        self._base_name = config.get("name")
        self._attr_name = f"{self._base_name} Sensor {suffix}"
        self._attr_unique_id = f"{entry_id}_random_{suffix}"
        self._min = config.get(CONF_MIN)
        self._max = config.get(CONF_MAX)
        self._interval = config.get(CONF_INTERVAL)
        self._historic_items = config.get(CONF_HISTORIC_ITEMS, 0)
        self._state = None
        
        # This links both sensors to the same "Device" in the UI
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=self._base_name,
            manufacturer="My Custom Lab",
        )

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        await self._update_state()
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._update_state, datetime.timedelta(seconds=self._interval)
            )
        )

    async def _update_state(self, _=None):
        self._state = random.randint(self._min, self._max)
        self.async_write_ha_state()

    async def async_backfill_history(self):
        """Inject historical data points."""
        now = dt_util.utcnow()
        statistics = []
        
        # Ensure ID is formatted correctly for the recorder
        # Using the unique_id is safer than the name
        stat_id = f"sensor.{self._base_name.lower().replace(' ', '_')}_sensor_{self.unique_id[-1].lower()}"
        
        for i in range(self._historic_items, 0, -1):
            past_time = now - datetime.timedelta(seconds=i * self._interval)
            val = random.randint(self._min, self._max)
            statistics.append(StatisticData(start=past_time, state=val))

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=self._attr_name,
            source="recorder",
            statistic_id=stat_id,
            unit_of_measurement=self._attr_native_unit_of_measurement,
            mean_type="arithmetic"
        )
        
        async_import_statistics(self.hass, metadata, statistics)