from . import api
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN
from .coordinator import WallboxCoordinator
import logging


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ChargingPauseSwitch(coordinator),
        EcoPlusSwitch(coordinator)
    ])

class ChargingPauseSwitch(SwitchEntity):
    def __init__(self, coordinator: WallboxCoordinator):
        self._coordinator = coordinator
        self._attr_name = "Wallbox Laden pausieren"
        self._attr_unique_id = f"{coordinator._ip}_pause_switch"
        # self._attr_entity_category = EntityCategory.CONFIG
        self._is_paused = False  # interner Status

    @property
    def is_on(self) -> bool:
        pause_status = (
            self._coordinator.data
            .get("salia", {})
            .get("pausecharging", "fehlt")
        )
        _LOGGER = logging.getLogger(__name__)
        _LOGGER.debug("Pausecharging-Wert aus Coordinator: %s", pause_status)
        return str(pause_status) in ["1", "true", "True"]


    async def async_added_to_hass(self):
        self._coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()


    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(
            api.set_pausecharging, 1            
        )
        await self._coordinator.async_request_refresh()
        self._is_paused = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(
            api.set_pausecharging, 0  
        )
        await self._coordinator.async_request_refresh()
        self._is_paused = False
        self.async_write_ha_state()

class EcoPlusSwitch(SwitchEntity):
    def __init__(self, coordinator: WallboxCoordinator):
        self._coordinator = coordinator
        self._attr_name = "Eco-Plus Modus"
        self._attr_unique_id = f"{coordinator._ip}_ecoplus_switch"

    @property
    def is_on(self) -> bool:
        ecoplus = self._coordinator.data.get("salia", {}).get("ecoplus", "fehlt")
        return str(ecoplus) in ["1", "true", "True"]

    async def async_added_to_hass(self):
        self._coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(api.post_json, {"salia/ecoplus": 1})
        await self._coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(api.post_json, {"salia/ecoplus": 0})
        await self._coordinator.async_request_refresh()
        self.async_write_ha_state()

