import random
import datetime
import logging
from homeassistant.components.sensor import (
    SensorEntity, 
    SensorStateClass, 
    SensorDeviceClass
)
from homeassistant.const import UnitOfPower, UnitOfEnergy
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = {**entry.data, **entry.options}
    
    # Create sensors with specific roles
    sensors = [
        RandomSensor(hass, entry, config, "Alpha"),
        RandomSensor(hass, entry, config, "Beta"),
    ]
    
    async_add_entities(sensors)

class RandomSensor(SensorEntity):
    def __init__(self, hass, entry, config, suffix):
        self.hass = hass
        self._entry = entry
        self._config = config
        self._suffix = suffix
        
        self._base_name = config["name"]
        self._attr_name = f"{self._base_name} {suffix}"
        self._attr_unique_id = f"{entry.entry_id}_random_{suffix.lower()}"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=self._base_name,
            manufacturer="Solar Simulator",
            model="Random Gen v2",
        )

        # Solar/Energy specific settings
        if suffix == "Alpha":
            # Energy Sensor (Accumulated production)
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        else:
            # Power Sensor (Real-time production)
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = UnitOfPower.WATT

        self._min = config[CONF_MIN]
        self._max = config[CONF_MAX]
        self._interval = config[CONF_INTERVAL]
        self._state = None

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
        
        backfilled_key = f"backfilled_{self._suffix.lower()}"
        if not self._entry.data.get(backfilled_key):
            await self.async_backfill_history()
            new_data = {**self._entry.data, backfilled_key: True}
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)

    async def _update_state(self, _=None):
        self._state = random.randint(self._min, self._max)
        self.async_write_ha_state()

    async def async_backfill_history(self):
        """Inject historical data aligned to the top of the hour."""
        count = self._config.get(CONF_HISTORIC_ITEMS, 0)
        if count <= 0:
            return

        now = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)
        statistics = []
        
        for i in range(count, 0, -1):
            past_time = now - datetime.timedelta(hours=i)
            val = random.randint(self._min, self._max)
            
            # For energy statistics, we need to provide a sum or a mean
            # The energy dashboard specifically looks for 'sum' for TOTAL_INCREASING
            if self._suffix == "Alpha":
                statistics.append(StatisticData(start=past_time, state=val, sum=float(val)))
            else:
                statistics.append(StatisticData(start=past_time, state=val, mean=val))

        metadata = StatisticMetaData(
            has_mean=(self._suffix == "Beta"),
            has_sum=(self._suffix == "Alpha"),
            name=self._attr_name,
            source="recorder",
            statistic_id=self.entity_id,
            unit_of_measurement=self._attr_native_unit_of_measurement,
            mean_type="arithmetic" if self._suffix == "Beta" else None
        )

        async_import_statistics(self.hass, metadata, statistics)