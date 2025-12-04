from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import KarotzCoordinator

SENSORS = [
    {"key": "health", "name": "Health", "icon": "mdi:heart-pulse"},
    {"key": "sleep", "name": "Sleep", "icon": "mdi:sleep"},
    {"key": "led_color", "name": "LED Color", "icon": "mdi:led-on"},
    {"key": "led_pulse", "name": "LED Pulse", "icon": "mdi:pulse"},
    {"key": "ears_disabled", "name": "Ears Disabled", "icon": "mdi:ear-hearing-off"},
    {"key": "karotz_free_space", "name": "Free Space", "icon": "mdi:harddisk"},
    {"key": "karotz_percent_used_space", "name": "Used Space", "icon": "mdi:harddisk", "unit": PERCENTAGE},
    {"key": "nb_tags", "name": "RFID Tags", "icon": "mdi:tag-multiple"},
    {"key": "nb_sounds", "name": "Sounds", "icon": "mdi:music-box-multiple"},
    {"key": "nb_moods", "name": "Moods", "icon": "mdi:emoticon-outline"},
    {"key": "version", "name": "Version", "icon": "mdi:information-outline"},
    {"key": "wlan_mac", "name": "MAC Address", "icon": "mdi:network"},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    name = data["config"].get(CONF_NAME, DEFAULT_NAME)
    
    entities = [KarotzSensor(coordinator, entry, name, sensor) for sensor in SENSORS]
    async_add_entities(entities)

class KarotzSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: KarotzCoordinator,
        entry: ConfigEntry,
        device_name: str,
        sensor_config: dict
    ) -> None:
        super().__init__(coordinator)
        self._key = sensor_config["key"]
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_name = f"{device_name} {sensor_config['name']}"
        self._attr_icon = sensor_config.get("icon")
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Violet / Mindscape",
            "model": "Karotz",
        }

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get(self._key)
        return None