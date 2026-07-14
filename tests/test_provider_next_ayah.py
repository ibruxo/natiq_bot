import asyncio

from app.api.provider import NatiqProvider
from app.cache.quran import QuranCache


class DummyClient:
    pass


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
            {"uuid": "1", "surah": 4, "ayah": 14},
            {"uuid": "2", "surah": 4, "ayah": 15},
            {"uuid": "3", "surah": 5, "ayah": 1},
        ]
    )
    cache.set_translations([])

    provider = NatiqProvider(client=DummyClient(), cache=cache)

    ayah = asyncio.run(provider.next_ayah("1"))

    assert ayah.text == "second"
    assert ayah.ayah_number == 15
    assert ayah.uuid == "2"
