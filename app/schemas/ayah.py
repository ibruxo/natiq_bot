from pydantic import BaseModel


class Ayah(BaseModel):
    text: str
    surah_name: str
    surah_number: int
    ayah_number: int
