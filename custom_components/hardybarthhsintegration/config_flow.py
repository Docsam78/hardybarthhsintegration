from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_IP

class WallboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Wallbox", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP): vol.Coerce(str),
                vol.Optional("scan_interval", default=10): vol.All(int, vol.Range(min=5, max=3600)),
            }),
            description_placeholders={"help_url": "https://example.com"},
        )
    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

  


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Hole aktuellen Wert oder setze Default
        current_interval = self.config_entry.options.get(
            "scan_interval", self.config_entry.data.get("scan_interval", 10)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("scan_interval", default=current_interval): vol.All(int, vol.Range(min=5, max=3600)),
            })
        )
