from datetime import timedelta
import logging
import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

    

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://deine-wallbox-api.de/status"

class WallboxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry):
        self.hass = hass  # <--- Speichern!
        self._ip = config_entry.data["ip"]
        _LOGGER.debug("Config Entry Data: %s", config_entry.data)

        interval = config_entry.options.get("scan_interval", config_entry.data.get("scan_interval", 10))
        _LOGGER.debug("Verwendeter Scan-Intervall: %s Sekunden", interval)

        super().__init__(
            hass,
            _LOGGER,
            name="Wallbox Status",
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self):
        try:
            url = f"http://{self._ip}/api/secc/port0"
            response = await self.hass.async_add_executor_job(requests.get, url)
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug("Wallbox API Response: %s", data)
            return data
    
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Wallbox-Daten: {err}")
