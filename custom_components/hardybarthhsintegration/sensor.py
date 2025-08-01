from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
    SensorEntityDescription,
)
from .coordinator import WallboxCoordinator
from .const import DOMAIN

SENSOR_CONFIG = [
    ("metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash"),
    ("metering.power.active.ac.l2.actual", "Leistung L2", "W", "mdi:flash"),
    ("metering.power.active.ac.l3.actual", "Leistung L3", "W", "mdi:flash"),
    ("metering.voltage.ac.l1.actual", "Spannung L1", "V", "mdi:power-plug"),
    ("metering.voltage.ac.l2.actual", "Spannung L2", "V", "mdi:power-plug"),
    ("metering.voltage.ac.l3.actual", "Spannung L3", "V", "mdi:power-plug"),
    ("metering.current.ac.l1.actual", "Strom L1", "mA", "mdi:current-ac"),
    ("metering.current.ac.l2.actual", "Strom L2", "mA", "mdi:current-ac"),
    ("metering.current.ac.l3.actual", "Strom L3", "mA", "mdi:current-ac"),
    ("metering.energy.active_total.actual", "Energie gesamt", "kWh", "mdi:counter"),
    ("salia.chargemode", "Lademodus", None, "mdi:ev-station"),
    ("salia.ecoplus", "EcoPlus aktiviert", None, "mdi:leaf"),
    ("salia.pausecharging", "Laden pausiert", None, "mdi:pause-circle"),
    ("salia.intctrl_limit", "Strombegrenzung", "A", "mdi:transmission-tower")
]

def get_nested(data, path):
    for key in path.split("."):
        data = data.get(key, {})
    return data if isinstance(data, (int, float, str)) else None

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
          

    sensors = []
    for path, name, unit, icon in SENSOR_CONFIG:
        sensors.append(WallboxSensor(coordinator, path, name, unit, icon))

    async_add_entities(sensors)

class WallboxSensor(SensorEntity,CoordinatorEntity):
    def __init__(self, coordinator, path, name, unit, icon):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._path = path

        state_class = None
        device_class = None
        if "energy" in path:
            state_class = SensorStateClass.TOTAL_INCREASING
            device_class = SensorDeviceClass.ENERGY
        elif "power" in path:
            state_class = SensorStateClass.MEASUREMENT
            device_class = SensorDeviceClass.POWER
        elif "voltage" in path:
            state_class = SensorStateClass.MEASUREMENT
            device_class = SensorDeviceClass.VOLTAGE
        elif "current" in path:
            state_class = SensorStateClass.MEASUREMENT
            device_class = SensorDeviceClass.CURRENT

        self.entity_description = SensorEntityDescription(
            key=path,
            name=name,
            icon=icon,
            state_class=state_class,
            device_class=device_class
        )
        if path == "metering.energy.active_total.actual":
            self._attr_native_unit_of_measurement = "kWh"
        else:
            self._attr_native_unit_of_measurement = unit
                        
        self._attr_unique_id = f"{coordinator._ip}_{path}"
        
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._coordinator._ip)},
            "name": "HardyBarth Wallbox",
            "manufacturer": "HardyBarth",
            "model": "Wallbox",
            "configuration_url": f"http://{self._coordinator._ip}/",
        }

    @property
    def available(self):
        return self._coordinator.last_update_success

    @property
    def native_value(self):
        value = get_nested(self._coordinator.data, self._path)
        if self._path == "metering.energy.active_total.actual" and value is not None:
            try:
                value = float(value)
                value = value / 1000  # Passe ggf. den Divisor an
            except (ValueError, TypeError):
                return None 
        return value

