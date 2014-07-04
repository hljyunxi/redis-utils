#!/usr/bin/python
#coding: utf8
#Author: chenyunyun<hljyunxi@gmail.com>


#在redis的基础上构建的bloom filter
import redis

class Bloom(object):
    def __init__(self, conn, name, capacity, error_rate=0.001):
        self.conn = conn

    def __contains__(self, key):
        pass

    def add(self, key):
        pass

    @property
    def count():
        pass


def FNVHash(key):
    fnv_prime = 0x811C9DC5
    hash = 0
    for i in range(len(key)):
      hash *= fnv_prime
      hash ^= ord(key[i])
    return hash


def APHash(key):
    hash = 0xAAAAAAAA
    for i in range(len(key)):
      if ((i & 1) == 0):
        hash ^= ((hash <<  7) ^ ord(key[i]) * (hash >> 3))
      else:
        hash ^= (~((hash << 11) + ord(key[i]) ^ (hash >> 5)))
    return hash

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes > :
    elif:
    elif:
    else:

    return size
