import random
import datetime
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.util import dt as dt_util

from .const import CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data
    sensor = RandomSensor(hass, config, entry.entry_id)
    async_add_entities([sensor])
    
    # After adding the entity, trigger the history backfill
    await sensor.async_backfill_history()

class RandomSensor(SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT # Required for statistics/graphs

    def __init__(self, hass, config, entry_id):
        self.hass = hass
        self._config = config
        self._attr_name = config.get("name")
        self._attr_unique_id = f"{entry_id}_random_sensor"
        self._min = config.get(CONF_MIN)
        self._max = config.get(CONF_MAX)
        self._interval = config.get(CONF_INTERVAL)
        self._historic_items = config.get(CONF_HISTORIC_ITEMS)
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
        
        for i in range(self._historic_items, 0, -1):
            # Calculate past time: now - (item_index * interval)
            past_time = now - datetime.timedelta(seconds=i * self._interval)
            random_val = random.randint(self._min, self._max)
            
            statistics.append(
                StatisticData(
                    start=past_time,
                    state=random_val,
                    sum=None # Not needed for simple measurement
                )
            )

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=self._attr_name,
            source="recorder", # Standard recorder source
            statistic_id=f"sensor.{self._attr_name.lower().replace(' ', '_')}",
            unit_of_measurement=None,
        )

        # This adds the data to the Long Term Statistics database
        async_import_statistics(self.hass, metadata, statistics)