"""Integration for Karotz."""
import urllib.parse

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .coordinator import KarotzCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.LIGHT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Karotz from a config entry."""
    host = entry.data[CONF_HOST]
    coordinator = KarotzCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "config": entry.data,
    }

    # Enregistrer les services
    await async_setup_services(hass, host)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_setup_services(hass: HomeAssistant, host: str) -> None:
    """Set up Karotz services."""
    async def async_say(call: ServiceCall) -> None:
        text = call.data.get("text", "")
        voice = call.data.get("voice", 2)

        encoded_text = urllib.parse.quote(text)
        url = f"http://{host}/cgi-bin/tts?voice={voice}&text={encoded_text}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    pass
        except aiohttp.ClientError as e:
            pass

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok