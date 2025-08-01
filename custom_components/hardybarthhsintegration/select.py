from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import WallboxCoordinator
from . import api
import logging

_LOGGER = logging.getLogger(__name__)

CHARGEMODES = ["eco", "power"]

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ChargeModeSelect(coordinator)
    ])

class ChargeModeSelect(SelectEntity):
    def __init__(self, coordinator: WallboxCoordinator):
        self._coordinator = coordinator
        self._attr_name = "Lademodus"
        self._attr_unique_id = f"{coordinator._ip}_chargemode_select"
        self._attr_options = CHARGEMODES

    @property
    def current_option(self) -> str:
        mode = self._coordinator.data.get("salia", {}).get("chargemode", "eco")
        _LOGGER.debug("Aktueller Lademodus: %s", mode)
        return mode if mode in CHARGEMODES else "eco"

    async def async_added_to_hass(self):
        self._coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    async def async_select_option(self, option: str):
        if option in CHARGEMODES:
            await self.hass.async_add_executor_job(api.set_chargemode, option)
            await self._coordinator.async_request_refresh()
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Ungültiger Lademodus gewählt: %s", option)

