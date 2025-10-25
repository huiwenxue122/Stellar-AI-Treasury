import aiohttp, asyncio, time
from typing import Dict, Any

class Horizon:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def _get(self, path: str, params: Dict[str, Any] | None = None):
        url = f"{self.base_url}{path}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=20) as r:
                r.raise_for_status()
                return await r.json()

    async def order_book(self, selling_code: str, selling_issuer: str | None,
                         buying_code: str, buying_issuer: str | None, limit: int = 10):
        params = {
            "selling_asset_type": "native" if selling_code == "XLM" else "credit_alphanum4",
            "buying_asset_type": "native" if buying_code == "XLM" else "credit_alphanum4",
            "limit": limit,
        }
        if selling_code != "XLM":
            params.update({"selling_asset_code": selling_code, "selling_asset_issuer": selling_issuer})
        if buying_code != "XLM":
            params.update({"buying_asset_code": buying_code, "buying_asset_issuer": buying_issuer})
        return await self._get("/order_book", params)

    async def trades(self, base_code: str, base_issuer: str | None,
                     counter_code: str, counter_issuer: str | None,
                     limit: int = 200, cursor: str | None = None):
        params = {
            "base_asset_type": "native" if base_code == "XLM" else "credit_alphanum4",
            "counter_asset_type": "native" if counter_code == "XLM" else "credit_alphanum4",
            "limit": limit,
            "order": "asc",
        }
        if base_code != "XLM":
            params.update({"base_asset_code": base_code, "base_asset_issuer": base_issuer})
        if counter_code != "XLM":
            params.update({"counter_asset_code": counter_code, "counter_asset_issuer": counter_issuer})
        if cursor:
            params["cursor"] = cursor
        return await self._get("/trades", params)

    async def liquidity_pools(self, asset_a: tuple[str, str | None], asset_b: tuple[str, str | None]):
        # Filter by reserves (rough): use assets[] multi-params if supported or post-filter.
        return await self._get("/liquidity_pools", {"limit": 10, "order": "desc"})