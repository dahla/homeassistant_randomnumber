class RandomSensorOptionsFlow(config_entries.OptionsFlow):
    # REMOVED __init__ assignment to fix AttributeError

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Access config_entry directly via the base class property
        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_MIN, default=current.get(CONF_MIN)): int,
                vol.Required(CONF_MAX, default=current.get(CONF_MAX)): int,
                vol.Required(CONF_INTERVAL, default=current.get(CONF_INTERVAL)): int,
            })
        )