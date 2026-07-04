from redis.verses import VerseStore


class CacheManager:
    def __init__(self):
        self.verse_store = VerseStore()
        self.is_loaded = True  # Redis is always ready

    def get_random_verse(self):
        verse = self.verse_store.random()

        if not verse:
            raise ValueError("No verses found in Redis")

        return verse

    def format_verse(self, data):
        period = data.get("period", "")

        if period == "makki":
            icon = "🕋"
        elif period == "madani":
            icon = "🕌"
        else:
            icon = "📖"

        return (
            f"{icon} *سوره {data.get('surah_name','')}*\n\n"
            f"📖 *{data.get('verse_text','')} ﴿{data.get('verse_number','')}﴾*\n\n"
            f"📝 {data.get('translation','')}"
        )
