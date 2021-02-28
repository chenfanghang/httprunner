import inspect
from typing import Text, Any, Union, Callable, Dict

from rrtv_httprunner.models import (
    TConfig,
    TStep,
    TRequest,
    MethodEnum,
    TestCase,
)


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

    def redis(self, config: Union[Text, Dict]) -> "Config":
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

    def perform(self) -> TStep:
        return self.__step_context


class StepRequestExtraction(object):
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

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

    def with_sql(self, sql: Text, var_name: Text) -> "StepRequestExtraction":
        """ 提取sql数据

        Args:
            sql: 执行SQL
            var_name: 存储的变量名 后续通过$引用

        Examples:
            >>> StepRequestExtraction.with_sql("select * from mysql","var_name")

        """
        self.__step_context.extract[var_name] = "sql:" + sql
        return self

    def with_redis(self, redis: Text, var_name: Text) -> "StepRequestExtraction":
        """

        Args:
            redis: redis命令
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

        """
        self.__step_context.extract[var_name] = "redis:" + redis
        return self

    def with_mongo(self, mongo: Text, var_name: Text) -> "StepRequestExtraction":
        # TODO
        self.__step_context.extract[var_name] = "mongo:" + mongo
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

    def with_params(self, **params) -> "RequestWithOptionalArgs":
        self.__step_context.request.params.update(params)
        return self

    def with_headers(self, **headers) -> "RequestWithOptionalArgs":
        self.__step_context.request.headers.update(headers)
        return self

    def with_cookies(self, **cookies) -> "RequestWithOptionalArgs":
        self.__step_context.request.cookies.update(cookies)
        return self

    def with_data(self, data) -> "RequestWithOptionalArgs":
        self.__step_context.request.data = data
        return self

    def with_json(self, req_json) -> "RequestWithOptionalArgs":
        self.__step_context.request.req_json = req_json
        return self

    def set_timeout(self, timeout: float) -> "RequestWithOptionalArgs":
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

    def teardown_hook(
            self, hook: Text, assign_var_name: Text = None
    ) -> "RequestWithOptionalArgs":
        if assign_var_name:
            self.__step_context.teardown_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.teardown_hooks.append(hook)

        return self

    def teardown_exec(self, command) -> "RequestWithOptionalArgs":
        """ 在接口执行之后执行命令

        Args:
            command: 执行的命令

        Examples:
            >>> RequestWithOptionalArgs.teardown_exec("sql:xxx")
            >>> RequestWithOptionalArgs.teardown_exec("redis:xxx")
            >>> RequestWithOptionalArgs.teardown_exec("mongo:xxx")
            >>> RequestWithOptionalArgs.teardown_exec("cmd:xxx")

        """
        self.__step_context.teardown.append(command)
        return self

    def teardown_sql(self, sql: Text) -> "RequestWithOptionalArgs":
        """ 在接口执行之后执行SQL

        Args:
            sql: 执行SQL

        Examples:
            >>> RequestWithOptionalArgs.teardown_sql("select * from mysql")

        """
        self.__step_context.teardown.append("sql:" + sql)
        return self

    def teardown_redis(self, redis: Text) -> "RequestWithOptionalArgs":
        """ 在接口执行之后执行redis

        Args:
            redis: redis命令

        Examples:
            >>> RequestWithOptionalArgs.teardown_redis("get('key')") # 取出键key对应的值
            >>> RequestWithOptionalArgs.teardown_redis("hget('name','key')") # 取出hash的key对应的值
            >>> RequestWithOptionalArgs.teardown_redis("hget('name')") # 取出hash中所有的键值对
            >>> RequestWithOptionalArgs.teardown_redis("set('key','rrtv')") # 设置key对应的值
            >>> RequestWithOptionalArgs.teardown_redis("hset('name','key','value')") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
            >>> RequestWithOptionalArgs.teardown_redis("del('key')") # 删除指定key的键值对
            >>> RequestWithOptionalArgs.teardown_redis("hdel(name, k)") # 删除hash中键值对
            >>> RequestWithOptionalArgs.teardown_redis("clean") # 清空redis

        """
        self.__step_context.teardown.append("redis:" + redis)
        return self

    def teardown_mongo(self, mongo: Text) -> "RequestWithOptionalArgs":
        # TODO
        self.__step_context.teardown.append("mongo:" + mongo)
        return self

    def teardown_cmd(self, command: Text) -> "RequestWithOptionalArgs":
        """ 在接口执行之后执行cmd命令

        Args:
            command: cmd命令

        Examples:
            >>> RequestWithOptionalArgs.teardown_cmd("echo 'Hello World !'")

        """
        self.__step_context.teardown.append("cmd:" + command)
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

    def setup_sql(self, sql: Text) -> "RunRequest":
        """ 在接口执行之前执行SQL

        Args:
            sql: 执行SQL

        Examples:
            >>> RunRequest.setup_sql("select * from mysql")

        """
        self.__step_context.setup.append("sql:" + sql)
        return self

    def setup_redis(self, redis: Text) -> "RunRequest":
        """ 在接口执行之前执行redis

        Args:
            redis: redis命令

        Examples:
            >>> RunRequest.setup_redis("get('key')") # 取出键key对应的值
            >>> RunRequest.setup_redis("hget('name','key')") # 取出hash的key对应的值
            >>> RunRequest.setup_redis("hget('name')") # 取出hash中所有的键值对
            >>> RunRequest.setup_redis("set('key','rrtv')") # 设置key对应的值
            >>> RunRequest.setup_redis("hset('name','key','value')") # name对应的hash中设置一个键值对--没有就新增，有的话就修改
            >>> RunRequest.setup_redis("del('key')") # 删除指定key的键值对
            >>> RunRequest.setup_redis("hdel(name, k)") # 删除hash中键值对
            >>> RunRequest.setup_redis("clean") # 清空redis

        """
        self.__step_context.setup.append("redis:" + redis)
        return self

    def setup_mongo(self, mongo: Text) -> "RunRequest":
        # TODO
        self.__step_context.setup.append("mongo:" + mongo)
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
