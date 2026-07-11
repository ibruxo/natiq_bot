from dataclasses import dataclass


@dataclass(slots=True)
class Ayah:
    uuid: str
    surah_number: int
    surah_name: str
    ayah_number: int
    text: str
