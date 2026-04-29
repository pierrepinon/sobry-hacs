from __future__ import annotations

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SobryApiClient, SobryAuthError
from .const import CONF_CUSTOMER_ID, CONF_EMAIL, CONF_TOKEN, DOMAIN


class SobryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Two-step config flow: email → OTP code.

    Step 1 (user): collect the user's email and trigger an OTP send.
    Step 2 (otp):  collect the OTP code, verify it, and create the entry.
    """

    VERSION = 1

    def __init__(self) -> None:
        self._email: str | None = None

    async def async_step_user(self, user_input=None):
        """Step 1: ask for the user's email and send an OTP."""
        errors = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            client = SobryApiClient(async_get_clientsession(self.hass))

            try:
                await client.generate_otp(email)
            except (SobryAuthError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
            else:
                self._email = email
                return await self.async_step_otp()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_EMAIL): str}),
            errors=errors,
        )

    async def async_step_otp(self, user_input=None):
        """Step 2: verify the OTP code and create the config entry."""
        errors = {}

        if user_input is not None:
            client = SobryApiClient(async_get_clientsession(self.hass))

            try:
                data = await client.verify_otp(self._email, user_input["code"])
            except SobryAuthError as err:
                errors["base"] = "invalid_auth" if "invalid_code" in str(err) else "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                customer = data["customer"]
                await self.async_set_unique_id(customer["id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._email,
                    data={
                        CONF_EMAIL: self._email,
                        CONF_TOKEN: data["token"],
                        CONF_CUSTOMER_ID: customer["id"],
                    },
                )

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({vol.Required("code"): str}),
            description_placeholders={"email": self._email},
            errors=errors,
        )
