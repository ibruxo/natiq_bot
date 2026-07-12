from __future__ import annotations

from pydantic import BaseModel


class Ayah(BaseModel):

    text: str

    translation: str | None = None

    surah_name: str = "Unknown"

    surah_number: int = 0

    ayah_number: int = 0

    page: int | None = None

    juz: int | None = None
