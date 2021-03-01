# @author: chenfanghang
import sys
from typing import Text

from loguru import logger
from pymongo import MongoClient


class MongoHandler:
    def __init__(self, driver: Text, database: Text):
        self.client = MongoClient(driver)
        self.db = self.client[database]

    def get_state(self):
        return self.client is not None and self.db is not None

    def insert_one(self, collection, data):  # 单个插入
        if self.get_state():
            ret = self.db[collection].insert_one(data)
            return ret.inserted_id
        else:
            return ""

    def insert_many(self, collection, data):  # 批量插入
        if self.get_state():
            ret = self.db[collection].insert_many(data)
            return ret.inserted_id
        else:
            return ""

    def find_one(self, collection, condition=None):  # 获取一条数据
        """condition：只能是dict类型,key大于等于一个即可，也可为空
        可使用修饰符查询：{"name": {"$gt": "H"}}#读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据
        使用正则表达式查询：{"$regex": "^R"}#读取 name 字段中第一个字母为 "R" 的数据"""
        col = self.db[collection]
        try:
            if self.get_state():
                result = col.find_one(condition)  # 这里只会返回一个对象，数据需要自己取
                return result
            else:
                return ""
        except TypeError as e:
            logger.error("查询条件只能是dict类型")
            return None

    def find(self, collection, condition=None, limit=sys.maxsize, sort_col='None_sort',
             sort='asc'):
        """condition：只能是dict类型,key大于等于一个即可，也可为空
        可使用修饰符查询：{"name": {"$gt": "H"}}#读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据
        使用正则表达式查询：{"$regex": "^R"}#读取 name 字段中第一个字母为 "R" 的数据
        limit_num:返回指定条数记录，该方法只接受一个数字参数(sys.maxsize:返回一个最大的整数值)"""
        col = self.db[collection]
        try:
            if self.get_state():
                if sort_col is False or sort_col == 'None_sort':
                    results = col.find(condition).limit(limit)  # 这里只会返回一个对象，数据需要自己取
                else:
                    sort_flag = 1
                    if sort == 'desc':
                        sort_flag = -1
                    results = col.find(condition).sort(sort_col, sort_flag).limit(limit)  # 这里只会返回一个对象，数据需要自己取
                result_all = [i for i in results]  # 将获取到的数据添加至list
                return result_all
            else:
                return ""
        except TypeError as e:
            logger.error(f"{e: }查询条件只能是dict类型")
            return None

    def db(self, collection):
        """condition：只能是dict类型,key大于等于一个即可，也可为空
        可使用修饰符查询：{"name": {"$gt": "H"}}#读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据
        使用正则表达式查询：{"$regex": "^R"}#读取 name 字段中第一个字母为 "R" 的数据
        limit_num:返回指定条数记录，该方法只接受一个数字参数(sys.maxsize:返回一个最大的整数值)"""
        col = self.db[collection]
        return col

    def update_one(self, collection, condition, update_col):
        """该方法第一个参数为查询的条件，第二个参数为要修改的字段。
            如果查找到的匹配数据多余一条，则只会修改第一条。
            修改后字段的定义格式： { "$set": { "alexa": "12345" } }"""
        col = self.db[collection]
        try:
            if self.get_state():
                result = col.update_one(condition, update_col)
                return result
            else:
                return ""
        except TypeError as e:
            logger.error(f"{e: }查询条件与需要修改的字段只能是dict类型")
            return None

    def update_many(self, collection, condition, update_col):
        """批量更新数据"""
        my_col = self.db[collection]
        try:
            if self.get_state():
                result = my_col.update_many(condition, update_col)
                return result
            else:
                return ""
        except TypeError as e:
            logger.error(f"{e: }查询条件与需要修改的字段只能是dict类型")
            return None

    def delete_one(self, collection, condition):  # 删除集合中的文档
        my_col = self.db[collection]
        try:
            if self.get_state():
                result = my_col.delete_one(condition)
                return result
            else:
                return ""
        except TypeError as e:
            logger.error(f"{e: }查询条件与需要修改的字段只能是dict类型")
            return None

    def delete_many(self, collection, condition):  # 删除集合中的多个文档
        """删除所有 name 字段中以 F 开头的文档:{ "name": {"$regex": "^F"} }
        删除所有文档：{}"""
        my_col = self.db[collection]
        try:
            if self.get_state():
                result = my_col.delete_many(condition)
                return result
            else:
                return ""
        except TypeError as e:
            logger.error(f"{e: }查询条件与需要修改的字段只能是dict类型")
            return None

    def drop(self, collection):
        """删除集合，如果删除成功 drop() 返回 true，如果删除失败(集合不存在)则返回 false"""
        my_col = self.db[collection]
        if self.get_state():
            result = my_col.drop()
            return result
        else:
            return ""

    def get_connections(self):  # 获取所有的connections
        return self.db.list_collection_names()

    def close_connect(self):
        self.client.close()
        return 'mongo连接已关闭'

    def __del__(self):
        try:
            self.close_connect()
        except Exception as e:
            pass
