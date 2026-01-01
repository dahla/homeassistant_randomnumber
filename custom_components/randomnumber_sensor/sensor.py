import random
import datetime
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

async def async_setup_entry(hass, entry, async_add_entities):
    # Merge initial data and updated options
    config = {**entry.data, **entry.options}
    
    sensor = RandomSensor(hass, config, entry.entry_id)
    async_add_entities([sensor])
    
    # Only backfill if we haven't done it for this specific entry ID yet
    if "backfilled" not in entry.data:
        await sensor.async_backfill_history()
        # Mark as backfilled so a reload (options change) doesn't trigger it again
        hass.config_entries.async_update_entry(entry, data={**entry.data, "backfilled": True})

class RandomSensor(SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass, config, entry_id):
        self.hass = hass
        self._attr_name = config.get("name")
        self._attr_unique_id = f"{entry_id}_random_sensor"
        self._min = config.get(CONF_MIN)
        self._max = config.get(CONF_MAX)
        self._interval = config.get(CONF_INTERVAL)
        self._historic_items = config.get(CONF_HISTORIC_ITEMS, 0)
        self._state = None

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        self._update_state()
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._update_state, datetime.timedelta(seconds=self._interval)
            )
        )

    def _update_state(self, _=None):
        self._state = random.randint(self._min, self._max)
        self.async_write_ha_state()

    async def async_backfill_history(self):
        """Inject historical data points into the recorder."""
        now = dt_util.utcnow()
        statistics = []
        entity_id = f"sensor.{self._attr_name.lower().replace(' ', '_')}"
        
        for i in range(self._historic_items, 0, -1):
            past_time = now - datetime.timedelta(seconds=i * self._interval)
            # Home Assistant statistics usually prefer hourly alignment, 
            # but measurements can be imported at specific timestamps.
            statistics.append(
                StatisticData(start=past_time, state=random.randint(self._min, self._max))
            )

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=self._attr_name,
            source="recorder",
            statistic_id=entity_id,
            unit_of_measurement=None,
        )
        async_import_statistics(self.hass, metadata, statistics)