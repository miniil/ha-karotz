"""Config flow for Karotz integration."""

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME

from .const import DEFAULT_NAME, DOMAIN


class KarotzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Karotz config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            # Test de connexion
            try:
                async with aiohttp.ClientSession() as session, session.get(
                    f"http://{host}/cgi-bin/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return self.async_create_entry(
                            title=user_input.get(CONF_NAME, DEFAULT_NAME),
                            data=user_input
                        )
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }),
            errors=errors
        )
