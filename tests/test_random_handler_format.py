from app.bot.handlers.random import format_ayah
from app.schemas.ayah import Ayah


def build_ayah(*, surah_icon: str, surah_period: str) -> Ayah:
    return Ayah(
        uuid="ayah-1",
        text="sample text",
        translation="sample translation",
        surah_uuid="surah-1",
        surah_name="الفاتحة",
        surah_number=1,
        surah_period=surah_period,
        surah_icon=surah_icon,
        ayah_number=7,
        page=1,
        juz=1,
    )


def test_format_ayah_includes_makki_icon() -> None:
    ayah = build_ayah(
        surah_icon="🕋",
        surah_period="makki",
    )

    text = format_ayah(ayah)

    assert "🕋 *سوره الفاتحة*" in text
    assert "📖 *sample text ﴿7﴾*" in text
    assert "📝 sample translation (7)" in text
    assert "@NatiqBot" in text


def test_format_ayah_includes_madani_icon() -> None:
    ayah = build_ayah(
        surah_icon="🕌",
        surah_period="madani",
    )

    text = format_ayah(ayah)

    assert "🕌 *سوره الفاتحة*" in text


def test_format_ayah_omits_extra_space_without_icon() -> None:
    ayah = build_ayah(
        surah_icon="",
        surah_period="unknown",
    )

    text = format_ayah(ayah)

    assert "*سوره الفاتحة*" in text
    assert "\n\n📖 *sample text ﴿7﴾*" in text
    assert " *سوره الفاتحة*" not in text
