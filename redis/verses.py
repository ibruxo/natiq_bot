import random
from typing import Optional, Dict
from redis.client import redis_client


class VerseStore:
    PREFIX = "verse:"
    INDEX_KEY = "verses:all"

    def save(self, uuid: str, data: Dict):
        key = self.PREFIX + uuid

        redis_client.hset(key, mapping=data)
        redis_client.sadd(self.INDEX_KEY, uuid)

    def get(self, uuid: str) -> Optional[Dict]:
        key = self.PREFIX + uuid
        data = redis_client.hgetall(key)

        if not data:
            return None

        return data

    def random(self) -> Optional[Dict]:
        uuid = redis_client.srandmember(self.INDEX_KEY)

        if not uuid:
            return None

        return self.get(uuid)
