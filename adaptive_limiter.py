#!/usr/bin/env python
#coding: gb2312

#基于redis zset实现的限速组件
#实现主要是参考了：
#opensourcehacker.com/2014/07/09/\
#rolling-time-window-counters-with-redis-and-mitigating-botnet-driven-login-attacks

import time

class AdaptiveLimiter(object):
    def __init__(self, conn, limiter_name, window, limit):
        self.conn = conn
        self.limiter_name = limiter_name
        self.window = window
        self.limit = limit

    def trim(self, key):
        expires = time.time() - self.window
        self.conn.zremrangebyscore(key, '-inf', expires)

    def add(self, key, value):
        now = time.time()
        zset_key = 'zset:%s:%s' % (self.limiter_name, key)

        self.conn.zadd(zset_key, now, now)

        self.trim(zset_key)

    def delete(self, key):
        zset_key = 'zset:%s:%s' % (self.limiter_name, key)
        self.conn.delete(zset_key)

    def is_exceed(self, key):
        zset_key = 'zset:%s:%s' % (self.limiter_name, key)

        self.trim(zset_key)
        if self.conn.zcard(zset_key) >= self.limit:
            return True

        return False

    def clear(self):
        pipe = self.conn.pipeline()
        for key in self.conn.keys('zset:%s*' % self.limiter_name):
            pipe.delete(key)
        pipe.execute()
