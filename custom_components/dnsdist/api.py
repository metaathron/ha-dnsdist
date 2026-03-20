"""API client for dnsdist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession


class DnsdistApiError(Exception):
    """Base exception for dnsdist API errors."""


class DnsdistApiAuthError(DnsdistApiError):
    """Authentication error from dnsdist API."""


@dataclass(slots=True)
class DnsdistApiClient:
    """Small async client for dnsdist API."""

    session: ClientSession
    endpoint: str
    api_key: str

    async def async_get_status(self) -> dict[str, Any]:
        """Fetch status from dnsdist."""
        headers = {"X-API-Key": self.api_key}

        try:
            async with self.session.get(self.endpoint, headers=headers) as response:
                if response.status in (401, 403):
                    raise DnsdistApiAuthError("Invalid API key")
                response.raise_for_status()
                payload = await response.json()
        except DnsdistApiAuthError:
            raise
        except ClientResponseError as err:
            raise DnsdistApiError(
                f"dnsdist API returned HTTP {err.status}: {err.message}"
            ) from err
        except (ClientError, TimeoutError, ValueError) as err:
            raise DnsdistApiError(f"dnsdist API request failed: {err}") from err

        if not isinstance(payload, dict):
            raise DnsdistApiError("dnsdist API returned unexpected payload")

        return payload
