"""Tests for hardybarthhsintegration sensor platform."""

import pytest
from custom_components.hardybarthhsintegration.sensor import WallboxSensor, get_nested
from custom_components.hardybarthhsintegration.const import DOMAIN

class DummyCoordinator:
    def __init__(self, ip, data=None, last_update_success=True):
        self._ip = ip
        self.data = data or {}
        self.last_update_success = last_update_success

def test_get_nested_simple():
    data = {"a": {"b": {"c": 42}}}
    assert get_nested(data, "a.b.c") == 42

def test_get_nested_missing():
    data = {"a": {"b": {}}}
    assert get_nested(data, "a.b.c") is None

def test_wallbox_sensor_initialization():
    coordinator = DummyCoordinator("1.2.3.4")
    sensor = WallboxSensor(coordinator, "metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash")
    assert sensor.entity_description.name == "Leistung L1"
    assert sensor.entity_description.device_class.name == "POWER"
    assert sensor._attr_native_unit_of_measurement == "W"
    assert sensor._attr_unique_id == "1.2.3.4_metering.power.active.ac.l1.actual"

def test_wallbox_sensor_device_info():
    coordinator = DummyCoordinator("1.2.3.4")
    sensor = WallboxSensor(coordinator, "metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash")
    info = sensor.device_info
    assert info["identifiers"] == {(DOMAIN, "1.2.3.4")}
    assert info["manufacturer"] == "HardyBarth"
    assert info["model"] == "Wallbox"
    assert info["configuration_url"] == "http://1.2.3.4/"

def test_wallbox_sensor_available_true():
    coordinator = DummyCoordinator("1.2.3.4", last_update_success=True)
    sensor = WallboxSensor(coordinator, "metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash")
    assert sensor.available is True

def test_wallbox_sensor_available_false():
    coordinator = DummyCoordinator("1.2.3.4", last_update_success=False)
    sensor = WallboxSensor(coordinator, "metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash")
    assert sensor.available is False

def test_wallbox_sensor_native_value_regular():
    coordinator = DummyCoordinator("1.2.3.4", data={"metering": {"power": {"active": {"ac": {"l1": {"actual": 123}}}}}})
    sensor = WallboxSensor(coordinator, "metering.power.active.ac.l1.actual", "Leistung L1", "W", "mdi:flash")
    assert sensor.native_value == 123

def test_wallbox_sensor_native_value_energy_conversion():
    coordinator = DummyCoordinator("1.2.3.4", data={"metering": {"energy": {"active_total": {"actual": 2000}}}})
    sensor = WallboxSensor(coordinator, "metering.energy.active_total.actual", "Energie gesamt", "kWh", "mdi:counter")
    assert sensor.native_value == 2.0

def test_wallbox_sensor_native_value_energy_invalid():
    coordinator = DummyCoordinator("1.2.3.4", data={"metering.energy.active_total.actual": "invalid"})
    sensor = WallboxSensor(coordinator, "metering.energy.active_total.actual", "Energie gesamt", "kWh", "mdi:counter")
    assert sensor.native_value is None