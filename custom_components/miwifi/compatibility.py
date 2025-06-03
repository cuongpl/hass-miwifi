"""Compatibility detection module for MiWiFi."""

from __future__ import annotations

from .luci import LuciClient
from .exceptions import LuciError
from .logger import _LOGGER

class CompatibilityChecker:
    """Main compatibility detector."""

    def __init__(self, client: LuciClient) -> None:
        self.client = client
        self.result: dict[str, bool] = {}

    async def run(self) -> dict[str, bool]:
        """Run full compatibility checks."""

        self.result["mac_filter"] = await self._check_mac_filter()
        self.result["mac_filter_info"] = await self._check_mac_filter_info()
        self.result["per_device_qos"] = await self._check_qos_info()

        _LOGGER.info(f"[MiWiFi] Compatibility detection finished: {self.result}")

        return self.result

    async def _check_mac_filter(self) -> bool:
        try:
            await self.client.get("xqsystem/set_mac_filter", {"mac": "00:00:00:00:00:00", "wan": 1})
            return True
        except LuciError:
            return False

    async def _check_mac_filter_info(self) -> bool:
        try:
            await self.client.get("xqnetwork/wifi_macfilter_info")
            return True
        except LuciError:
            return False

    async def _check_qos_info(self) -> bool:
        try:
            await self.client.qos_info()
            return True
        except LuciError:
            return False
