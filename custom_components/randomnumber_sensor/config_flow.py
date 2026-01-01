from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import logging

from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

_LOGGER = logging.getLogger(__name__)

class RandomSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Random Number Generator."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required(CONF_MIN, default=0): int,
                vol.Required(CONF_MAX, default=100): int,
                vol.Required(CONF_INTERVAL, default=60): int,
                vol.Required(CONF_HISTORIC_ITEMS, default=24): int,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RandomSensorOptionsFlow()

class RandomSensorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # In modern HA, self.config_entry is available automatically
        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_MIN, default=current.get(CONF_MIN)): int,
                vol.Required(CONF_MAX, default=current.get(CONF_MAX)): int,
                vol.Required(CONF_INTERVAL, default=current.get(CONF_INTERVAL)): int,
            })
        )