from __future__ import annotations

from pydantic import BaseModel


class Ayah(BaseModel):
    """
    Fully hydrated Quran ayah.

    The provider resolves all metadata before creating this model,
    so handlers never need to search the cache.
    """

    # --------------------------------------------------
    # Ayah
    # --------------------------------------------------

    uuid: str

    text: str

    translation: str | None = None

    # --------------------------------------------------
    # Surah
    # --------------------------------------------------

    surah_uuid: str

    surah_name: str

    surah_number: int

    surah_period: str

    surah_icon: str

    bismillah_text: str | None = None

    bismillah_is_ayah: bool = False

    show_bismillah_line: bool = False

    # --------------------------------------------------
    # Position
    # --------------------------------------------------

    ayah_number: int

    page: int | None = None

    juz: int | None = None
