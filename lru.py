#!/usr/bin/python
#coding: utf8
#Author: chenyunyun<hljyunxi@gmail.com>

#redis base lru cache

class LRUCache(object):
    def __init__(self, conn, cahe_name, size=10):
        self.conn = conn
        self.cache_name = cache_name
        self.size = size
        self._count_key = "count_key:%s" % cache_name
        self._zset_key = "zset:%s" % cache_name

    def trim(self):
        length = self.conn.zcard(self._zset_key)
        excess = length - self.size
        if excess < 0:
            return

        for _ in range(excess):
            elements = self.conn.zrevrange(self._zset_key, self.size, -1)
            pipe = self.conn.pipeline()
            for i in elements:
                pipe.hdel(self.cache_name, i)
                pipe.zrem(self._zset_key, i)
            pipe.execute()

    def __str__(self):
        return str(self.conn.hgetall(self.cache_name))

    def __contains__(self, key):
        return True if self.get(key) is not None else False

    def set(self, key, value):
        count = self.conn.incr(self._count_key)

        pipe = self.conn.pipeline()
        pipe.zadd(self._zset_key, key, count)
        pipe.hset(self.cache_name, key, value)
        pipe.execute()

        self.trim()

    def get(self, key):
        count = self.conn.incr(self._count_key)
        value = self.conn.hget(self.cache_name)
        if value:
            self.conn.zadd(self._zset_key, key, count)
            self.trim()

        return None

    def clear(self):
        pipe = self.conn.pipeline()
        pipe.delete(self.cache_name)
        pipe.delete(self._zset_key)
        pipe.delete(self._count_key)
        pipe.execute()
