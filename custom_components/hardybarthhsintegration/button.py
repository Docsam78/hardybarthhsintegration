from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN
from .coordinator import WallboxCoordinator

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinator: WallboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PauseChargingButton(coordinator)
    ])

class PauseChargingButton(ButtonEntity):
    def __init__(self, coordinator: WallboxCoordinator):
        self._attr_name = "Laden pausieren"
        self._attr_unique_id = f"{coordinator._ip}_pause_button"
        self._attr_entity_category = EntityCategory.CONFIG
        self._coordinator = coordinator

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(
            self._coordinator.api.pause_charging,
            self._coordinator._ip
        )
