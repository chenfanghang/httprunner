from typing import Union

import pymysql
from loguru import logger
from pymysql.cursors import DictCursor

from rrtv_httprunner import exceptions


class DBHandler(object):
    """
    初始化数据库
    """

    # 也可以继承 Connection 这里没有选择继承
    def __init__(self, driver: Union[str, dict], **kwargs):
        driver = driver if isinstance(driver, dict) else eval(driver)
        try:
            self.connect = pymysql.connect(
                host=str(driver["host"]),  # 连接名
                port=int(driver["port"]),  # 端口
                user=driver["user"],  # 用户名
                password=driver["password"],  # 密码
                charset=driver["charset"],  # 不能写utf-8 在MySQL里面写utf-8会报错
                database=driver["database"],  # 数据库库名
                cursorclass=DictCursor,  # 数据转换成字典格式
                **kwargs
            )
            # 创建游标对象  **主要**
            self.cursor = self.connect.cursor()
        except TypeError as ex:
            logger.error(f"""MYSQL数据库连接失败:{driver}""")
            raise exceptions.DBConnectionError(f"""MYSQL数据库连接失败:{driver}""")

    def query_one(self, query, args=None):
        """
        查询数据库一条数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        """
        self.cursor.execute(query, args)
        # 将更改提交到数据库
        self.connect.commit()
        return self.cursor.fetchone()

    def delete(self, sql, args=None):
        """
        删除数据库一条数据
        :param sql: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        """
        self.cursor.execute(sql, args)
        self.connect.commit()
        self.connect.rollback()
        return self.cursor.fetchone()

    def query_all(self, query, args=None):
        """
        查询数据库所有数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        """
        self.cursor.execute(query, args)
        # 将更改提交到数据库
        self.connect.commit()
        return self.cursor.fetchall()

    def query(self, query, args=None, one=True):
        """
        主体查询数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        :param one: one是True 时候执行query_one, 否则执行query_all
        """
        if one:
            return self.query_one(query, args)
        return self.query_all(query, args)

    def close(self):
        """
        关闭
        :return:
        """
        # 关闭游标
        self.cursor.close()
        # 断开数据库连接
        self.connect.close()

    def __del__(self):
        try:
            self.close()
        except AttributeError:
            pass
