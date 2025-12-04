import aiohttp
import logging
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    LightEntityFeature,
    ATTR_RGB_COLOR,
    ATTR_EFFECT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DEFAULT_NAME
from .coordinator import KarotzCoordinator

_LOGGER = logging.getLogger(__name__)

EFFECT_NONE = "none"
EFFECT_PULSE = "pulse"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    name = data["config"].get(CONF_NAME, DEFAULT_NAME)
    
    async_add_entities([KarotzLed(coordinator, entry, name)])

class KarotzLed(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = [EFFECT_NONE, EFFECT_PULSE]

    def __init__(
        self,
        coordinator: KarotzCoordinator,
        entry: ConfigEntry,
        device_name: str
    ) -> None:
        super().__init__(coordinator)
        self._host = entry.data[CONF_HOST]
        self._attr_unique_id = f"{entry.entry_id}_led"
        self._attr_name = f"{device_name} LED"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Violet / Mindscape",
            "model": "Karotz",
        }
        self._pulse_speed = 700
        self._secondary_color = (0, 0, 0)
        self._last_color = (0, 81, 255)  # Bleu Karotz par défaut
        self._last_effect = EFFECT_NONE

    @property
    def is_on(self) -> bool:
        if self.coordinator.data:
            color = self.coordinator.data.get("led_color", "000000")
            return color != "000000"
        return False

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        if self.coordinator.data:
            color = self.coordinator.data.get("led_color", "000000")
            rgb = self._hex_to_rgb(color)
            if color != "000000":
                self._last_color = rgb
            return rgb
        return None

    @property
    def effect(self) -> str | None:
        if self.coordinator.data:
            pulse = self.coordinator.data.get("led_pulse", "0")
            current_effect = EFFECT_PULSE if pulse == "1" else EFFECT_NONE
            if self.is_on:
                self._last_effect = current_effect
            return current_effect
        return None

    async def async_turn_on(self, **kwargs) -> None:
        rgb = kwargs.get(ATTR_RGB_COLOR, self._last_color)
        effect = kwargs.get(ATTR_EFFECT, self._last_effect)
        
        self._last_color = rgb
        self._last_effect = effect
        
        color_hex = self._rgb_to_hex(rgb)
        
        if effect == EFFECT_PULSE:
            secondary_hex = self._rgb_to_hex(self._secondary_color)
            endpoint = f"/cgi-bin/leds?pulse=1&color={color_hex}&speed={self._pulse_speed}&color2={secondary_hex}"
        else:
            endpoint = f"/cgi-bin/leds?color={color_hex}"
        
        await self._send_command(endpoint)

    async def async_turn_off(self, **kwargs) -> None:
        await self._send_command("/cgi-bin/leds?color=000000")

    async def _send_command(self, endpoint: str) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self._host}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    await self.coordinator.async_request_refresh()
        except aiohttp.ClientError as e:
            _LOGGER.warning(f"Karotz LED command warning: {e}")
            await self.coordinator.async_request_refresh()

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"