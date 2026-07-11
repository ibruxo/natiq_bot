from __future__ import annotations

import random

from app.api.client import APIClient
from app.schemas.ayah import Ayah


class NatiqProvider:

    def __init__(
        self,
        client: APIClient,
    ) -> None:
        self._client = client

    async def random_ayah(self) -> Ayah:
        #
        # Fetch first page.
        #
        response = await self._client.get("/ayahs/")

        response.raise_for_status()

        ayahs = response.json()

        if not ayahs:
            raise RuntimeError("No ayahs returned from API.")

        data = random.choice(ayahs)

        surah = data.get("surah") or {}

        names = surah.get("names") or []

        if names:
            surah_name = names[0]["name"]
        else:
            surah_name = "Unknown"

        return Ayah.parse_obj(
            {
                "text": data["text"],
                "surah_name": surah_name,
                "surah_number": surah.get("number", 0),
                "ayah_number": data["number"],
            }
        )
