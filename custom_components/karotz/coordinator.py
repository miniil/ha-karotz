import aiohttp
import json
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import ENDPOINT_STATUS, ENDPOINT_HEALTH, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class KarotzCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, host: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Karotz",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._host = host

    async def _async_update_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                # Health check
                async with session.get(
                    f"http://{self._host}{ENDPOINT_HEALTH}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        health_text = await response.text()
                        health_data = json.loads(health_text)
                        health_status = "ok" if health_data.get("return") == "0" else "error"
                    else:
                        health_status = "error"

                # Status complet
                async with session.get(
                    f"http://{self._host}{ENDPOINT_STATUS}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        status_text = await response.text()
                        status_data = json.loads(status_text)
                    else:
                        raise UpdateFailed(f"HTTP {response.status}")

                # Fusion des données
                return {**status_data, "health": health_status}

        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Connection error: {e}") from e
        except json.JSONDecodeError as e:
            raise UpdateFailed(f"Invalid JSON: {e}") from e