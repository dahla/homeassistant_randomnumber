import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_MIN, CONF_MAX, CONF_INTERVAL, CONF_HISTORIC_ITEMS

class RandomSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Random Sensor."""

    async def async_step_user(self, user_input=None):
        """Initial setup (Add Integration)."""
        if user_input is not None:
            # We store the inputs in 'data' for the first time
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required(CONF_MIN, default=0): int,
                vol.Required(CONF_MAX, default=100): int,
                vol.Required(CONF_INTERVAL, default=60): int,
                vol.Required(CONF_HISTORIC_ITEMS, default=20): int,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RandomSensorOptionsFlow(config_entry)

class RandomSensorOptionsFlow(config_entries.OptionsFlow):
    """Handle the 'Configure' button flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Use current values as defaults (look in options first, then data)
        current_config = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_MIN, default=current_config.get(CONF_MIN)): int,
                vol.Required(CONF_MAX, default=current_config.get(CONF_MAX)): int,
                vol.Required(CONF_INTERVAL, default=current_config.get(CONF_INTERVAL)): int,
                # Note: No Historic Items here!
            })
        )