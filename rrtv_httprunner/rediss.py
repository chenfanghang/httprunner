# @author: chenfanghang
from typing import Union

import redis
from loguru import logger

from rrtv_httprunner import exceptions


class RedisHandler:
    def __init__(self, driver: Union[str, dict]):

        driver = driver if isinstance(driver, dict) else eval(driver)
        try:
            self.r = redis.Redis(host=str(driver["host"]), password=driver["password"], port=int(driver["port"]),
                                 db=driver["db"])  # 连接redis固定方法,这里的值必须固定写死
        except Exception as e:
            logger.error("redis连接失败，错误信息:%s" % e)
            raise exceptions.DBConnectionError("redis连接失败，错误信息:%s" % e)

    def command(self):
        return self.r

    def str_get(self, k):
        res = self.r.get(k)  # 会从服务器传对应的值过来，性能慢
        if res:
            return res.decode()  # 从redis里面拿到的是bytes类型的数据，需要转换一下

    def str_set(self, k, v, time=None):  # time默认失效时间
        self.r.set(k, v, time)

    def delete(self, k):
        tag = self.r.exists(k)
        # 判断这个key是否存在,相对于get到这个key他只是传回一个存在火灾不存在的信息，
        # 而不用将整个k值传过来（如果k里面存的东西比较多，那么传输很耗时）
        if tag:
            self.r.delete(k)
        else:
            logger.debug(f"{k}:这个key不存在")

    def hash_get(self, name, k):  # 哈希类型存储的是多层字典（嵌套字典）
        res = self.r.hget(name, k)
        if res:
            return res.decode()  # 因为get不到值得话也不会报错所以需要判断一下

    def hash_set(self, name, k, v):  # 哈希类型的是多层
        self.r.hset(name, k, v)  # set也不会报错

    def hash_getall(self, name):
        res = self.r.hgetall(name)  # 得到的是字典类型的，里面的k,v都是bytes类型的
        data = {}
        if res:
            for k, v in res.items():  # 循环取出字典里面的k,v，在进行decode
                k = k.decode()
                v = v.decode()
                data[k] = v
        return data

    def hash_del(self, name, k):
        res = self.r.hdel(name, k)
        if res:
            return 1
        else:
            logger.debug(f"{name, k} 删除失败，该key不存在")
            return 0

    @property  # 属性方法，
    def clean_redis(self):
        self.r.flushdb()  # 清空 redis
        logger.debug("清空redis成功！")
        return 0
