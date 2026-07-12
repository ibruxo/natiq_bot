from __future__ import annotations

from pydantic import BaseModel


class Ayah(BaseModel):

    text: str

    translation: str | None = None

    surah_name: str = "Unknown"

    surah_number: int = 0

    ayah_number: int = 0



    @classmethod
    def from_api(
        cls,
        ayah: dict,
        surah: dict | None = None,
    ):

        surah = surah or ayah.get(
            "surah",
            {}
        )


        names = surah.get(
            "names",
            []
        )


        name = "Unknown"


        if names:

            first = names[0]

            if isinstance(first, dict):

                name = (
                    first.get("name")
                    or first.get("text")
                    or "Unknown"
                )


        return cls(

            text=(
                ayah.get("text")
                or ayah.get("arabic")
                or ""
            ),


            surah_name=name,


            surah_number=(
                surah.get("number")
                or surah.get("id")
                or 0
            ),


            ayah_number=(
                ayah.get("number")
                or ayah.get("ayah_number")
                or 0
            ),
        )
