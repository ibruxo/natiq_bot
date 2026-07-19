import asyncio

from app.api.client import APIClient
from app.api.provider import NatiqProvider
from app.cache.quran import QuranCache


def make_client_stub() -> APIClient:
    return object.__new__(APIClient)


def test_next_ayah_returns_following_ayah_from_same_surah() -> None:
    cache = QuranCache()
    cache.set_ayahs(
        [
            {"uuid": "1", "text": "first", "number": 1},
            {"uuid": "2", "text": "second", "number": 2},
            {"uuid": "3", "text": "third", "number": 3},
        ]
    )
    cache.set_takhtits(
        [
            {"uuid": "1", "surah": 4, "ayah": 14, "surah_uuid": "surah-4"},
            {"uuid": "2", "surah": 4, "ayah": 15, "surah_uuid": "surah-4"},
            {"uuid": "3", "surah": 5, "ayah": 1, "surah_uuid": "surah-5"},
        ]
    )
    cache.set_translations([])
    cache.set_surahs(
        [
            {
                "uuid": "surah-4",
                "number": 4,
                "name": "النساء",
                "location": "madani",
            },
            {
                "uuid": "surah-5",
                "number": 5,
                "name": "المائدة",
                "location": "madani",
            },
        ]
    )

    provider = NatiqProvider(
        client=make_client_stub(),
        cache=cache,
    )

    ayah = asyncio.run(provider.next_ayah("1"))

    assert ayah.text == "second"
    assert ayah.ayah_number == 15
    assert ayah.uuid == "2"
    assert ayah.surah_uuid == "surah-4"
    assert ayah.surah_name == "النساء"
    assert ayah.surah_period == "madani"
    assert ayah.surah_icon == "🕌"
