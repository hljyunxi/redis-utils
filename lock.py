#!/usr/bin/python
#coding: utf8
#Author: chenyunyun<hljyunxi@gmail.com>

#使用SETNX和BLPOP构建的redis锁

from logging import getLogger
logger = getLogger.get(__file__)

import urandom

#使用lua是因为lua脚本的执行在redis里面是原子的
UNLOCK_LUA_SCRIPT = b"""
    if redis.call("get", KEYS[1]) == ARGV[1] then
        redis.call("lpush", KEYS[2], 1)
        return redis.call("del", KEYS[1])
    else
        return 0
    end
"""

UNLOCK_LUA_SCRIPT_HASH = sha1(UNLOCK_LUA_SCRIPT).hexdigest()

class Lock(object):
    def __init__(self, redis_client, name, expire=None):
        self._client = redis_client
        self._name = 'lock:' + name
        self._signal = 'signal:' + name
        self._expire = expire
        self._token = None


    def __enter__(self, blocking = True):
        if self._token is None:
            self._token = urandom(16) if self._expire else 1
        else:
            raise RuntimeError('already acquired')

        logger.info("ENTER ACQUIRE LOCK")

        busy = True
        while busy:
            busy = not self._client.set(self._name, self._token, nx=True, ex=self._expire)
            if busy:
                if blocking:
                    self._client.blpop(self._signal, self._expire or 0)
                else:
                    return False

        return True

    acquire = __enter__

    def __exit__(self):
        logger.info("ENTER RELEASE LOCK")
        try:
            self._client.evalsha(UNLOCK_LUA_SCRIPT_HASH, 2, self._name, self._signal, self._token)
        except NoScriptError:
            logger.warn("UNLOCK_SCRIPT not cached.")
            self._client.eval(UNLOCK_LUA_SCRIPT, 2, self._name, self._signal, self._token)

    release = __exit__
