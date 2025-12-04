import aiohttp
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DEFAULT_NAME
from .coordinator import KarotzCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    name = data["config"].get(CONF_NAME, DEFAULT_NAME)
    
    async_add_entities([KarotzSleepSwitch(coordinator, entry, name)])

class KarotzSleepSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: KarotzCoordinator,
        entry: ConfigEntry,
        device_name: str
    ) -> None:
        super().__init__(coordinator)
        self._host = entry.data[CONF_HOST]
        self._attr_unique_id = f"{entry.entry_id}_sleep"
        self._attr_name = f"{device_name} Sleep"
        self._attr_icon = "mdi:sleep"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Violet / Mindscape",
            "model": "Karotz",
        }

    @property
    def is_on(self) -> bool:
        if self.coordinator.data:
            return self.coordinator.data.get("sleep") == "1"
        return False

    async def async_turn_on(self, **kwargs) -> None:
        await self._send_command("/cgi-bin/sleep")

    async def async_turn_off(self, **kwargs) -> None:
        await self._send_command("/cgi-bin/wakeup")

    async def _send_command(self, endpoint: str) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self._host}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        await self.coordinator.async_request_refresh()
                    else:
                        _LOGGER.error(f"Karotz command failed: HTTP {response.status}")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Karotz command error: {e}")