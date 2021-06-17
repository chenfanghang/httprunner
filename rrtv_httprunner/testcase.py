import inspect
from typing import Text, Any, Union, Callable, Dict, List

from deepdiff import DeepDiff

from rrtv_httprunner.models import (
    TConfig,
    TStep,
    TRequest,
    MethodEnum,
    TestCase,
)
from rrtv_httprunner.utils import split_with


class Config(object):
    def __init__(self, name: Text):
        self.__name = name
        self.__variables = {}
        self.__base_url = ""
        self.__verify = False
        self.__export = []
        self.__weight = 1
        self.__datasource = {}
        caller_frame = inspect.stack()[1]
        self.__path = caller_frame.filename

    @property
    def name(self) -> Text:
        return self.__name

    @property
    def path(self) -> Text:
        return self.__path

    @property
    def weight(self) -> int:
        return self.__weight

    def variables(self, **variables) -> "Config":
        self.__variables.update(variables)
        return self

    def base_url(self, base_url: Text) -> "Config":
        self.__base_url = base_url
        return self

    def verify(self, verify: bool) -> "Config":
        self.__verify = verify
        return self

    def export(self, *export_var_name: Text) -> "Config":
        self.__export.extend(export_var_name)
        return self

    def locust_weight(self, weight: int) -> "Config":
        self.__weight = weight
        return self

    def datasource(self, **datasource) -> "Config":
        """

        Args:
            **datasource: 数据源 k:v格式

        Examples:
            >>> Config.datasource(**{"redis": "{'host': 'localhost', 'port': '6379', 'password': '', 'db': '0'}"})

        """
        self.__datasource.update(datasource)
        return self

    def mysql(self, config: Union[Text, Dict]) -> "Config":
        self.__datasource["mysql"] = config
        return self

    def redis(self, config: Union[Text, Dict, List]) -> "Config":
        self.__datasource["redis"] = config
        return self

    def mongodb(self, config: Union[Text, Dict]) -> "Config":
        self.__datasource["mongo"] = config
        return self

    def perform(self) -> TConfig:
        return TConfig(
            name=self.__name,
            base_url=self.__base_url,
            verify=self.__verify,
            variables=self.__variables,
            export=list(set(self.__export)),
            path=self.__path,
            weight=self.__weight,
            datasource=self.__datasource
        )


class StepRequestValidation(object):
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def teardown_hook(
            self, hook: Text, assign_var_name: Text = None
    ) -> "StepRequestValidation":
        if assign_var_name:
            self.__step_context.teardown_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.teardown_hooks.append(hook)

        return self

    def teardown_exec(self, command) -> "StepRequestValidation":
        """ 在接口执行之后执行命令

        Args:
            command: 执行的命令

        Examples:
            >>> StepRequestValidation.teardown_exec("sql:xxx")
            >>> StepRequestValidation.teardown_exec("redis:xxx")
            >>> StepRequestValidation.teardown_exec("mongo:xxx")
            >>> StepRequestValidation.teardown_exec("cmd:xxx")

        """
        self.__step_context.teardown.append(command)
        return self

    def teardown_sql(self, var: Union[Text, List], assign_var_name: Text = None) -> "StepRequestValidation":
        """ 在接口执行之后执行SQL

        Args:
            var: 执行SQL
            assign_var_name: 变量名
        Examples:
            >>> RunRequest.teardown_sql("select * from mysql")
            >>> RunRequest.teardown_sql("select * from rrtv","var_name")
            >>> RunRequest.teardown_sql(["mysql","select * from rrtv"])
            >>> RunRequest.teardown_sql(["mysql","select * from rrtv"],"var_name")

        """
        if isinstance(var, List):
            # 指定环境场景
            db, sql = var[0], var[1]
            if assign_var_name is not None:
                # 存储变量
                self.__step_context.teardown.append("sql:" + str(sql) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("sql:" + str(sql) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                # 存储变量
                self.__step_context.teardown.append("sql:" + str(var) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("sql:" + str(var))
        return self

    def teardown_redis(self, var: Union[Text, List], assign_var_name: Text = None) -> "StepRequestValidation":
        """ 在接口执行之后执行redis

        Args:
            var: 执行SQL
            assign_var_name: 变量名

        Examples:
            >>> StepRequestValidation.teardown_redis("get('key')","var_name") # 取出键key对应的值
            >>> StepRequestValidation.teardown_redis("hget('name','key')","var_name") # 取出hash的key对应的值
            >>> StepRequestValidation.teardown_redis("hget('name')","var_name") # 取出hash中所有的键值对
            >>> StepRequestValidation.teardown_redis("hkeys('name')","var_name") # 取出hash中所有的键值对
            >>> StepRequestValidation.teardown_redis("set('key','rrtv')") # 设置key对应的值
            >>> StepRequestValidation.teardown_redis("hset('name','key','value')") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
            >>> StepRequestValidation.teardown_redis("del('key')") # 删除指定key的键值对
            >>> StepRequestValidation.teardown_redis("hdel(name, k)") # 删除hash中键值对
            >>> StepRequestValidation.teardown_redis("clean") # 清空redis
            >>> StepRequestValidation.teardown_redis("exists(key)") # 判断key是否存在
            >>> StepRequestValidation.teardown_redis("str_get('key')","var_name") # 直接调用api

        """
        if isinstance(var, List):
            # 指定环境场景
            db, cli = var[0], var[1]
            if assign_var_name is not None:
                self.__step_context.teardown.append("redis:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("redis:" + str(cli) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                self.__step_context.teardown.append("redis:" + str(var) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("redis:" + str(var))
        return self

    def teardown_mongo(self, mongo: Union[Text, List], assign_var_name: Text = None) -> "StepRequestValidation":
        if isinstance(mongo, List):
            # 指定环境场景
            db, cli = mongo[0], mongo[1]
            if assign_var_name is not None:
                self.__step_context.teardown.append("mongo:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("mongo:" + str(cli) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                self.__step_context.teardown.append("mongo:" + str(mongo) + "##" + assign_var_name)
            else:
                self.__step_context.teardown.append("mongo:" + str(mongo))
        return self

    def teardown_cmd(self, command: Text) -> "StepRequestValidation":
        """ 在接口执行之后执行cmd命令

        Args:
            command: cmd命令

        Examples:
            >>> StepRequestValidation.teardown_cmd("echo 'Hello World !'")

        """
        self.__step_context.teardown.append("cmd:" + command)
        return self

    def assert_equal(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"equal": [jmes_path, expected_value, message]}
        )
        return self

    def assert_not_equal(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"not_equal": [jmes_path, expected_value, message]}
        )
        return self

    def assert_greater_than(
            self, jmes_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"greater_than": [jmes_path, expected_value, message]}
        )
        return self

    def assert_less_than(
            self, jmes_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"less_than": [jmes_path, expected_value, message]}
        )
        return self

    def assert_greater_or_equals(
            self, jmes_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"greater_or_equals": [jmes_path, expected_value, message]}
        )
        return self

    def assert_less_or_equals(
            self, jmes_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"less_or_equals": [jmes_path, expected_value, message]}
        )
        return self

    def assert_length_equal(
            self, jmes_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_equal": [jmes_path, expected_value, message]}
        )
        return self

    def assert_length_greater_than(
            self, jmes_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_greater_than": [jmes_path, expected_value, message]}
        )
        return self

    def assert_length_less_than(
            self, jmes_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_less_than": [jmes_path, expected_value, message]}
        )
        return self

    def assert_length_greater_or_equals(
            self, jmes_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_greater_or_equals": [jmes_path, expected_value, message]}
        )
        return self

    def assert_length_less_or_equals(
            self, jmes_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_less_or_equals": [jmes_path, expected_value, message]}
        )
        return self

    def assert_string_equals(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"string_equals": [jmes_path, expected_value, message]}
        )
        return self

    def assert_startswith(
            self, jmes_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"startswith": [jmes_path, expected_value, message]}
        )
        return self

    def assert_endswith(
            self, jmes_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"endswith": [jmes_path, expected_value, message]}
        )
        return self

    def assert_regex_match(
            self, jmes_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"regex_match": [jmes_path, expected_value, message]}
        )
        return self

    def assert_contains(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"contains": [jmes_path, expected_value, message]}
        )
        return self

    def assert_contained_by(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"contained_by": [jmes_path, expected_value, message]}
        )
        return self

    def assert_type_match(
            self, jmes_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"type_match": [jmes_path, expected_value, message]}
        )
        return self

    def assert_if_equal(
            self, condition, jmes_path: Text, if_expected_value: Any, else_expected_value: Any = None,
            message: Text = ""
    ) -> "StepRequestValidation":
        """
        if断言 如果condition为True时expect_value为if_expected_value，否则为else_expected_value
        Args:
            condition: 条件
            jmes_path: jmespath语法
            if_expected_value: if值
            else_expected_value: else值
            message: 提示信息

        """

        self.__step_context.validators.append(
            {"equal": [condition, jmes_path, if_expected_value, else_expected_value, message]}
        )
        return self

    def assert_diff(self, check_value: Union[Dict, Text], expected_value: Union[Dict, Text], message: Text = "",
                    **kwargs) -> "StepRequestValidation":
        """
        Verifies two objects are consistent

        Args:
            check_value: 检查值
            expected_value: 预期值
            message: 报错提示
            validate_value: 是否校验值 Boolean类型

        Usage:
            >>> DeepDiff(check_value, expected_value, **kwargs)
        """
        self.__step_context.validators.append(
            {"t1": check_value, "t2": expected_value, "kwargs": kwargs, "message": message}
        )
        return self

    def perform(self) -> TStep:
        return self.__step_context


class StepRequestExtraction(object):
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def __extract__(self, db_type: Text, var: Union[Text, List], var_name: Text = None):
        if isinstance(var, List):
            # 指定环境场景
            db, command = var[0], var[1]
            self.__step_context.extract[var_name] = db_type + ":" + str(command) + "&&db:" + str(db)
        else:
            self.__step_context.extract[var_name] = db_type + ":" + str(var)

    def with_jmespath(self, jmes_path: Text, var_name: Text) -> "StepRequestExtraction":
        self.__step_context.extract[var_name] = jmes_path
        return self

    def with_extra(self, extra: Text, var_name: Text) -> "StepRequestExtraction":
        """ 提取数据

        Args:
            extra: 执行的命令
            var_name: 存储的变量名 后续通过$引用

        Examples:
            >>> StepRequestExtraction.with_extra("sql:xxx","var_name")
            >>> StepRequestExtraction.with_extra("redis:xxx","var_name")
            >>> StepRequestExtraction.with_extra("mongo:xxx","var_name")
            >>> StepRequestExtraction.with_extra("cmd:xxx","var_name")

        """
        self.__step_context.extract[var_name] = extra
        return self

    def with_sql(self, var: Union[Text, List], var_name: Text = None) -> "StepRequestExtraction":
        """ 提取sql数据

        Args:
            var: 执行SQL
            var_name: 存储的变量名 后续通过$引用

        Examples:
            >>> StepRequestExtraction.with_sql("select * from mysql","var_name")
            >>> StepRequestExtraction.with_sql(["mysql","select * from rrtv"],"mysql")

        """
        self.__extract__("sql", var, var_name)
        return self

    def with_redis(self, var: Union[Text, List], var_name: Text = None) -> "StepRequestExtraction":
        """

        Args:
            var: redis命令
            var_name: 存储的变量名 后续通过$引用

        Examples:
            >>> StepRequestExtraction.with_redis("get('key')","var_name") # 取出键key对应的值
            >>> StepRequestExtraction.with_redis("hget('name','key')","var_name") # 取出hash的key对应的值
            >>> StepRequestExtraction.with_redis("hget('name')","var_name") # 取出hash中所有的键值对
            >>> StepRequestExtraction.with_redis("set('key','rrtv')","var_name") # 设置key对应的值
            >>> StepRequestExtraction.with_redis("hset('name','key','value')","var_name") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
            >>> StepRequestExtraction.with_redis("del('key')","var_name") # 删除指定key的键值对
            >>> StepRequestExtraction.with_redis("hdel(name, k)","var_name") # 删除hash中键值对
            >>> StepRequestExtraction.with_redis("clean","var_name") # 清空redis
            >>> StepRequestExtraction.with_redis("exists(key)","var_name") # 判断key是否存在
            >>> StepRequestExtraction.with_redis("str_get('key')","var_name") # 直接调用api

        """
        self.__extract__("redis", var, var_name)
        return self

    def with_mongo(self, var: Text, var_name: Text) -> "StepRequestExtraction":
        """ 提取mongo数据

        Args:
            var: mongo指令
            var_name: 存储的变量名 后续通过$引用

        Returns:self

        """
        self.__extract__("mongo", var, var_name)
        return self

    # def with_regex(self):
    #     # TODO: extract response html with regex
    #     pass
    #
    # def with_jsonpath(self):
    #     # TODO: extract response json with jsonpath
    #     pass

    def validate(self) -> StepRequestValidation:
        return StepRequestValidation(self.__step_context)

    def perform(self) -> TStep:
        return self.__step_context


class RequestWithOptionalArgs(object):
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def with_params(self, str_params: Text = None, **params) -> "RequestWithOptionalArgs":
        if str_params is not None:
            self.__step_context.request.params.update(split_with(str_params))
        else:
            self.__step_context.request.params.update(params)
        return self

    def with_xml(self, xml: Text) -> "RequestWithOptionalArgs":
        self.__step_context.request.headers["Content-Type"] = "text/xml; charset=UTF-8"
        self.__step_context.request.data = xml
        return self

    def with_headers(self, str_headers: Text = None, **headers) -> "RequestWithOptionalArgs":
        if str_headers is not None:
            self.__step_context.request.headers.update(split_with(str_headers))
        else:
            self.__step_context.request.headers.update(headers)
        return self

    def with_cookies(self, str_cookies: Text = None, **cookies) -> "RequestWithOptionalArgs":
        if str_cookies is not None:
            self.__step_context.request.cookies.update(split_with(str_cookies))
        else:
            self.__step_context.request.cookies.update(cookies)
        return self

    def with_data(self, data: Dict = None, str_data: Text = None) -> "RequestWithOptionalArgs":
        if str_data is not None:
            self.__step_context.request.data = split_with(str_data)
        else:
            self.__step_context.request.data = data
        return self

    def with_formdata(self, data: Dict = None) -> "RequestWithOptionalArgs":
        """
        form-data传参

        Example:
            >>> RequestWithOptionalArgs.with_formdata({"test": (None,"rrtv")})
        """
        self.__step_context.request.files = data
        return self

    def with_json(self, req_json) -> "RequestWithOptionalArgs":
        self.__step_context.request.req_json = req_json
        return self

    def set_timeout(self, timeout: Text) -> "RequestWithOptionalArgs":
        self.__step_context.request.timeout = timeout
        return self

    def set_verify(self, verify: bool) -> "RequestWithOptionalArgs":
        self.__step_context.request.verify = verify
        return self

    def set_allow_redirects(self, allow_redirects: bool) -> "RequestWithOptionalArgs":
        self.__step_context.request.allow_redirects = allow_redirects
        return self

    def upload(self, **file_info) -> "RequestWithOptionalArgs":
        self.__step_context.request.upload.update(file_info)
        return self

    def extract(self) -> StepRequestExtraction:
        return StepRequestExtraction(self.__step_context)

    def validate(self) -> StepRequestValidation:
        return StepRequestValidation(self.__step_context)

    def perform(self) -> TStep:
        return self.__step_context


class RunRequest(object):
    def __init__(self, name: Text):
        self.__step_context = TStep(name=name)

    def with_variables(self, **variables) -> "RunRequest":
        self.__step_context.variables.update(variables)
        return self

    def setup_exec(self, command: Text) -> "RunRequest":
        """ 在接口执行之前执行命令

        Args:
            command: 执行的命令

        Examples:
            >>> RunRequest.setup_exec("sql:xxx")
            >>> RunRequest.setup_exec("redis:xxx")
            >>> RunRequest.setup_exec("mongo:xxx")
            >>> RunRequest.setup_exec("cmd:xxx")

        """
        self.__step_context.setup.append(command)
        return self

    # def execute(self, var: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
    #     """ 在接口执行之前执行命令
    #
    #     Args:
    #         var: 执行的命令
    #         assign_var_name: 存储变量
    #
    #     Examples:
    #         >>> RunRequest.execute("sql:xxx")
    #         >>> RunRequest.execute("redis:xxx")
    #         >>> RunRequest.execute("mongo:xxx")
    #         >>> RunRequest.execute("cmd:xxx")
    #
    #     """
    #     if isinstance(var, List):
    #         # 指定环境场景
    #         db, command = var[0], var[1]
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append(command + "&&db:" + str(db) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append(command + "&&db:" + str(db))
    #     else:
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append(var + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append(var)
    #     return self

    def setup_sql(self, var: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
        """ 在接口执行之前执行SQL

        Args:
            var: 执行SQL
            assign_var_name: 变量名

        Examples:
            >>> RunRequest.setup_sql("select * from mysql")
            >>> RunRequest.setup_sql("select * from rrtv","var_name")
            >>> RunRequest.setup_sql(["mysql","select * from rrtv"])
            >>> RunRequest.setup_sql(["mysql","select * from rrtv"],"var_name")
        """
        if isinstance(var, List):
            # 指定环境场景
            db, sql = var[0], var[1]
            if assign_var_name is not None:
                self.__step_context.setup.append("sql:" + str(sql) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("sql:" + str(sql) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                self.__step_context.setup.append("sql:" + str(var) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("sql:" + str(var))
        return self

    def setup_redis(self, redis: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
        """ 在接口执行之前执行redis

        Args:
            redis: redis命令
            assign_var_name: 变量名

        Examples:
            >>> RunRequest.setup_redis("get('key')","var_name") # 取出键key对应的值
            >>> RunRequest.setup_redis("hget('name','key')","var_name") # 取出hash的key对应的值
            >>> RunRequest.setup_redis("hget('name')","var_name") # 取出hash中所有的键值对
            >>> RunRequest.setup_redis("hkeys('name')","var_name") # 取出hash中所有的键值对
            >>> RunRequest.setup_redis("set('key','rrtv')") # 设置key对应的值
            >>> RunRequest.setup_redis("hset('name','key','value')") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
            >>> RunRequest.setup_redis("del('key')") # 删除指定key的键值对
            >>> RunRequest.setup_redis("hdel(name, k)") # 删除hash中键值对
            >>> RunRequest.setup_redis("clean") # 清空redis
            >>> RunRequest.setup_redis("exists(key)") # 判断key是否存在
            >>> RunRequest.setup_redis("str_get('key')","var_name") # 直接调用api

        """
        if isinstance(redis, List):
            # 指定环境场景
            db, cli = redis[0], redis[1]
            if assign_var_name is not None:
                self.__step_context.setup.append("redis:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("redis:" + str(cli) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                self.__step_context.setup.append("redis:" + str(redis) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("redis:" + str(redis))
        return self

    def setup_mongo(self, mongo: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
        if isinstance(mongo, List):
            # 指定环境场景
            db, cli = mongo[0], mongo[1]
            if assign_var_name is not None:
                self.__step_context.setup.append("mongo:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("mongo:" + str(cli) + "&&db:" + str(db))
        else:
            if assign_var_name is not None:
                self.__step_context.setup.append("mongo:" + str(mongo) + "##" + assign_var_name)
            else:
                self.__step_context.setup.append("mongo:" + str(mongo))
        return self

    def setup_cmd(self, command: Text) -> "RunRequest":
        """ 在接口执行之前执行cmd命令

        Args:
            command: cmd命令

        Examples:
            >>> RunRequest.setup_cmd("echo 'Hello World !'")

        """
        self.__step_context.setup.append("cmd:" + command)
        return self

    def setup_hook(self, hook: Text, assign_var_name: Text = None) -> "RunRequest":
        if assign_var_name:
            self.__step_context.setup_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.setup_hooks.append(hook)

        return self

    # def execute_sql(self, var: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
    #     """ 在with_variables之后 在接口执行之前执行SQL
    #
    #     Args:
    #         var: 执行SQL
    #         assign_var_name: 变量名
    #
    #     Examples:
    #         >>> RunRequest.execute_sql("select * from mysql")
    #         >>> RunRequest.execute_sql("select * from rrtv","var_name")
    #         >>> RunRequest.execute_sql(["mysql","select * from rrtv"])
    #         >>> RunRequest.execute_sql(["mysql","select * from rrtv"],"var_name")
    #     """
    #     if isinstance(var, List):
    #         # 指定环境场景
    #         db, sql = var[0], var[1]
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("sql:" + str(sql) + "&&db:" + str(db) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("sql:" + str(sql) + "&&db:" + str(db))
    #     else:
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("sql:" + str(var) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("sql:" + str(var))
    #     return self
    #
    # def execute_redis(self, redis: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
    #     """ 在with_variables之后 在接口执行之前执行redis
    #
    #     Args:
    #         redis: redis命令
    #         assign_var_name: 变量名
    #
    #     Examples:
    #         >>> RunRequest.execute_redis("get('key')","var_name") # 取出键key对应的值
    #         >>> RunRequest.execute_redis("hget('name','key')","var_name") # 取出hash的key对应的值
    #         >>> RunRequest.execute_redis("hget('name')","var_name") # 取出hash中所有的键值对
    #         >>> RunRequest.execute_redis("hkeys('name')","var_name") # 取出hash中所有的键值对
    #         >>> RunRequest.execute_redis("set('key','rrtv')") # 设置key对应的值
    #         >>> RunRequest.execute_redis("hset('name','key','value')") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
    #         >>> RunRequest.execute_redis("del('key')") # 删除指定key的键值对
    #         >>> RunRequest.execute_redis("hdel(name, k)") # 删除hash中键值对
    #         >>> RunRequest.execute_redis("clean") # 清空redis
    #         >>> RunRequest.execute_redis("exists(key)") # 判断key是否存在
    #         >>> RunRequest.execute_redis("str_get('key')","var_name") # 直接调用api
    #
    #     """
    #     if isinstance(redis, List):
    #         # 指定环境场景
    #         db, cli = redis[0], redis[1]
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("redis:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("redis:" + str(cli) + "&&db:" + str(db))
    #     else:
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("redis:" + str(redis) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("redis:" + str(redis))
    #     return self
    #
    # def execute_mongo(self, mongo: Union[Text, List], assign_var_name: Text = None) -> "RunRequest":
    #     """在with_variables之后 在接口执行之前执行mongo
    #     Args:
    #         mongo: mongo命令
    #         assign_var_name: 变量名
    #     """
    #     if isinstance(mongo, List):
    #         # 指定环境场景
    #         db, cli = mongo[0], mongo[1]
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("mongo:" + str(cli) + "&&db:" + str(db) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("mongo:" + str(cli) + "&&db:" + str(db))
    #     else:
    #         if assign_var_name is not None:
    #             self.__step_context.execute.append("mongo:" + str(mongo) + "##" + assign_var_name)
    #         else:
    #             self.__step_context.execute.append("mongo:" + str(mongo))
    #     return self
    #
    # def execute_cmd(self, command: Text) -> "RunRequest":
    #     """ 在with_variables之后 在接口执行之前执行cmd
    #
    #     Args:
    #         command: cmd命令
    #
    #     Examples:
    #         >>> RunRequest.execute_cmd("echo 'Hello World !'")
    #
    #     """
    #     self.__step_context.execute.append("cmd:" + command)
    #     return self

    def get(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.GET, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def post(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.POST, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def put(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.PUT, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def head(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.HEAD, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def delete(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.DELETE, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def options(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.OPTIONS, url=url)
        return RequestWithOptionalArgs(self.__step_context)

    def patch(self, url: Text) -> RequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.PATCH, url=url)
        return RequestWithOptionalArgs(self.__step_context)


class StepRefCase(object):
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def teardown_hook(self, hook: Text, assign_var_name: Text = None) -> "StepRefCase":
        if assign_var_name:
            self.__step_context.teardown_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.teardown_hooks.append(hook)

        return self

    def export(self, *var_name: Text) -> "StepRefCase":
        self.__step_context.export.extend(var_name)
        return self

    def perform(self) -> TStep:
        return self.__step_context


class RunTestCase(object):
    def __init__(self, name: Text):
        self.__step_context = TStep(name=name)

    def with_variables(self, **variables) -> "RunTestCase":
        self.__step_context.variables.update(variables)
        return self

    def setup_hook(self, hook: Text, assign_var_name: Text = None) -> "RunTestCase":
        if assign_var_name:
            self.__step_context.setup_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.setup_hooks.append(hook)

        return self

    def call(self, testcase: Callable) -> StepRefCase:
        self.__step_context.testcase = testcase
        return StepRefCase(self.__step_context)

    def perform(self) -> TStep:
        return self.__step_context


class Step(object):
    def __init__(
            self,
            step_context: Union[
                StepRequestValidation,
                StepRequestExtraction,
                RequestWithOptionalArgs,
                RunTestCase,
                StepRefCase,
            ],
    ):
        self.__step_context = step_context.perform()

    @property
    def request(self) -> TRequest:
        return self.__step_context.request

    @property
    def testcase(self) -> TestCase:
        return self.__step_context.testcase

    def perform(self) -> TStep:
        return self.__step_context
