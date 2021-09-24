# Forked from: https://www.geeksforgeeks.org/lru-cache-in-python-using-ordereddict/

from collections import OrderedDict
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")


class LRUDict(Generic[K, V]):

    """This is basically a dict (without the full API) that only remembers a fixed number of things."""

    def __init__(self, capacity: int):
        self.cache: OrderedDict[K, V] = OrderedDict()
        self.capacity = capacity

    def get(self, key: K, default: V = None) -> V:
        if key not in self.cache:
            return default
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: K, value: V) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
