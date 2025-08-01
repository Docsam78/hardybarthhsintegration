from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from homeassistant.const import Platform
from .coordinator import WallboxCoordinator
from . import api 
import logging
PLATFORMS: list[Platform] = [Platform.SENSOR,Platform.SWITCH,Platform.SELECT]  # Du kannst hier weitere Plattformen ergänzen



async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = WallboxCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh() 
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    ip_address = config_entry.data["ip"]
    api.initialize(ip_address)


   # Service: Lademodus setzen
    async def handle_set_chargemode(call):
        mode = call.data["mode"]
        await hass.async_add_executor_job(api.set_chargemode, coordinator._ip, mode)

    # Service: Laden pausieren
    async def handle_pause_charging(call):
        await hass.async_add_executor_job(api.pause_charging, coordinator._ip)

    # Service: Strombegrenzung setzen
    async def handle_set_current_limit(call):
        limit = call.data["limit"]
        await hass.async_add_executor_job(api.set_current_limit, coordinator._ip, limit)

    hass.services.async_register(DOMAIN, "wallbox_set_chargemode", handle_set_chargemode)
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.warning("Service wallbox_setcurrent registriert!")
    
    hass.services.async_register(DOMAIN, "wallbox_pause_charging", handle_pause_charging)
    _LOGGER.warning("Service wallbox_setcurrent registriert!")
    
    hass.services.async_register(DOMAIN, "wallbox_setcurrent", handle_set_current_limit)
    _LOGGER.warning("Service wallbox_setcurrent registriert!")



    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

