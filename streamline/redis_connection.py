import redis


class Redis:
    def __init__(self, host: str, port: int):
        self.connection = redis.Redis(
            host="localhost",
            port=6379,
        )

    def exists(self, key: str) -> bool:
        return self.connection.exists(key)

    def hexists(self, key: str, field: str) -> bool:
        return self.connection.hexists(key, field)

    def get(self, key: str) -> str:
        return self.connection.get(key)

    def set(self, key: str, value: str) -> None:
        self.connection.set(key, value)

    def hget(self, key: str, field: str) -> str:
        return self.connection.hget(key, field)

    def hset(self, key: str, field: str, value: str) -> None:
        self.connection.hset(key, field, value)

    def delete(self, key: str) -> None:
        self.connection.delete(key)

    def hdel(self, key: str, field: str) -> None:
        self.connection.hdel(key, field)
