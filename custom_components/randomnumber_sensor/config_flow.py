import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

class RandomSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        data_schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required(CONF_MIN, default=0): int,
            vol.Required(CONF_MAX, default=100): int,
            vol.Required(CONF_INTERVAL, default=60): int,
            vol.Required(CONF_HISTORIC_ITEMS, default=20): int, # How many points back in time
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)