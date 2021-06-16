import collections
import copy
import itertools
import json
import os.path
import platform
import re
import uuid
from multiprocessing import Queue
from typing import Dict, List, Any, Text, NoReturn, Union
from urllib.parse import quote, unquote

import sentry_sdk
from loguru import logger

from rrtv_httprunner import __version__
from rrtv_httprunner import exceptions
from rrtv_httprunner.models import VariablesMapping
from rrtv_httprunner.mongo import MongoHandler
from rrtv_httprunner.mysqls import MySQLHandler
from rrtv_httprunner.rediss import RedisHandler


def init_sentry_sdk():
    sentry_sdk.init(
        dsn="https://460e31339bcb428c879aafa6a2e78098@sentry.io/5263855",
        release="rrtv_httprunner@{}".format(__version__),
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_user({"id": uuid.getnode()})


def set_os_environ(variables_mapping):
    """ set variables mapping to os.environ
    """
    for variable in variables_mapping:
        os.environ[variable] = variables_mapping[variable]
        logger.debug(f"Set OS environment variable: {variable}")


def unset_os_environ(variables_mapping):
    """ set variables mapping to os.environ
    """
    for variable in variables_mapping:
        os.environ.pop(variable)
        logger.debug(f"Unset OS environment variable: {variable}")


def get_os_environ(variable_name):
    """ get value of environment variable.

    Args:
        variable_name(str): variable name

    Returns:
        value of environment variable.

    Raises:
        exceptions.EnvNotFound: If environment variable not found.

    """
    try:
        return os.environ[variable_name]
    except KeyError:
        raise exceptions.EnvNotFound(variable_name)


def lower_dict_keys(origin_dict):
    """ convert keys in dict to lower case

    Args:
        origin_dict (dict): mapping data structure

    Returns:
        dict: mapping with all keys lowered.

    Examples:
        >>> origin_dict = {
            "Name": "",
            "Request": "",
            "URL": "",
            "METHOD": "",
            "Headers": "",
            "Data": ""
        }
        >>> lower_dict_keys(origin_dict)
            {
                "name": "",
                "request": "",
                "url": "",
                "method": "",
                "headers": "",
                "data": ""
            }

    """
    if not origin_dict or not isinstance(origin_dict, dict):
        return origin_dict

    return {key.lower(): value for key, value in origin_dict.items()}


def print_info(info_mapping):
    """ print info in mapping.

    Args:
        info_mapping (dict): input(variables) or output mapping.

    Examples:
        >>> info_mapping = {
                "var_a": "hello",
                "var_b": "world"
            }
        >>> info_mapping = {
                "status_code": 500
            }
        >>> print_info(info_mapping)
        ==================== Output ====================
        Key              :  Value
        ---------------- :  ----------------------------
        var_a            :  hello
        var_b            :  world
        ------------------------------------------------

    """
    if not info_mapping:
        return

    content_format = "{:<16} : {:<}\n"
    content = "\n==================== Output ====================\n"
    content += content_format.format("Variable", "Value")
    content += content_format.format("-" * 16, "-" * 29)

    for key, value in info_mapping.items():
        if isinstance(value, (tuple, collections.deque)):
            continue
        elif isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif value is None:
            value = "None"

        content += content_format.format(key, value)

    content += "-" * 48 + "\n"
    logger.info(content)


def omit_long_data(body, omit_len=512):
    """ omit too long str/bytes
    """
    if not isinstance(body, (str, bytes)):
        return body

    body_len = len(body)
    if body_len <= omit_len:
        return body

    omitted_body = body[0:omit_len]

    appendix_str = f" ... OMITTED {body_len - omit_len} CHARACTORS ..."
    if isinstance(body, bytes):
        appendix_str = appendix_str.encode("utf-8")

    return omitted_body + appendix_str


def get_platform():
    return {
        "httprunner_version": __version__,
        "python_version": "{} {}".format(
            platform.python_implementation(), platform.python_version()
        ),
        "platform": platform.platform(),
    }


def sort_dict_by_custom_order(raw_dict: Dict, custom_order: List):
    def get_index_from_list(lst: List, item: Any):
        try:
            return lst.index(item)
        except ValueError:
            # item is not in lst
            return len(lst) + 1

    return dict(
        sorted(raw_dict.items(), key=lambda i: get_index_from_list(custom_order, i[0]))
    )


class ExtendJSONEncoder(json.JSONEncoder):
    """ especially used to safely dump json data with python object, such as MultipartEncoder
    """

    def default(self, obj):
        try:
            return super(ExtendJSONEncoder, self).default(obj)
        except (UnicodeDecodeError, TypeError):
            return repr(obj)


def merge_variables(
        variables: VariablesMapping, variables_to_be_overridden: VariablesMapping
) -> VariablesMapping:
    """ merge two variables mapping, the first variables have higher priority
    """
    step_new_variables = {}
    for key, value in variables.items():
        if f"${key}" == value or "${" + key + "}" == value:
            # e.g. {"base_url": "$base_url"}
            # or {"base_url": "${base_url}"}
            continue

        step_new_variables[key] = value

    merged_variables = copy.copy(variables_to_be_overridden)
    merged_variables.update(step_new_variables)
    return merged_variables


def is_support_multiprocessing() -> bool:
    try:
        Queue()
        return True
    except (ImportError, OSError):
        # system that does not support semaphores(dependency of multiprocessing), like Android termux
        return False


def gen_cartesian_product(*args: List[Dict]) -> List[Dict]:
    """ generate cartesian product for lists

    Args:
        args (list of list): lists to be generated with cartesian product

    Returns:
        list: cartesian product in list

    Examples:

        >>> arg1 = [{"a": 1}, {"a": 2}]
        >>> arg2 = [{"x": 111, "y": 112}, {"x": 121, "y": 122}]
        >>> args = [arg1, arg2]
        >>> gen_cartesian_product(*args)
        >>> # same as below
        >>> gen_cartesian_product(arg1, arg2)
            [
                {'a': 1, 'x': 111, 'y': 112},
                {'a': 1, 'x': 121, 'y': 122},
                {'a': 2, 'x': 111, 'y': 112},
                {'a': 2, 'x': 121, 'y': 122}
            ]

    """
    if not args:
        return []
    elif len(args) == 1:
        return args[0]

    product_list = []
    for product_item_tuple in itertools.product(*args):
        product_item_dict = {}
        for item in product_item_tuple:
            product_item_dict.update(item)

        product_list.append(product_item_dict)

    return product_list


def split_with(str_params) -> Dict:
    var = str_params.strip().split("&")
    dict_var = {}
    for v in var:
        dict_var[v.split("=")[0]] = v.split("=")[1]
    return dict_var


def get_statement_type(statement: Text) -> Text:
    if isinstance(statement, str):
        if statement.lower().startswith("sql:"):
            return "mysql"
        elif statement.lower().startswith("redis:"):
            return "redis"
        elif statement.lower().startswith("mongo:"):
            return "mongo"
        elif statement.lower().startswith("cmd:"):
            return "cmd"


def execute_sql(db: Union[str, dict], sql: Text) -> Text:
    match_start_position = sql.index(":", 0)
    parsed_string = sql[match_start_position + 1:]
    handler = MySQLHandler(db)
    logger.debug("execute sql: {" + parsed_string + "}")
    if parsed_string.lower().startswith("select"):
        return handler.query(parsed_string, one=True)
    elif parsed_string.lower().startswith("insert"):
        return handler.query(parsed_string, one=True)
    elif parsed_string.lower().startswith("update"):
        return handler.query(parsed_string, one=True)
    elif parsed_string.lower().startswith("delete"):
        return handler.delete(parsed_string)


def execute_cmd(cmd: Text) -> NoReturn:
    match_start_position = cmd.index(":", 0)
    parsed_string = cmd[match_start_position + 1:]
    logger.debug("execute cmd: { " + parsed_string + " }")
    os.system(parsed_string)


def execute_redis(rd: Union[Text, Dict, List], cli: Text) -> Any:
    def is_get():
        get_func = ["get(", "hget(", "hkeys(", "hash_get(", "str_get(", "hash_getall("]
        return any(parsed_string.lower().startswith(func) is True for func in get_func)

    def is_del():
        del_func = ["del(", "hdel(", "delete(", "hash_del("]
        return any(parsed_string.lower().startswith(func) is True for func in del_func)

    def is_exists():
        exists_func = ["exists("]
        return any(parsed_string.lower().startswith(func) is True for func in exists_func)

    def execute(config, content):
        handler = RedisHandler(config)
        if parsed_string.lower().startswith("get("):
            return handler.str_get(content[0])
        elif parsed_string.lower().startswith("hget("):
            handler.hash_hkeys(content[0]) if len(content) == 1 else handler.hash_get(content[0], content[1])
        elif parsed_string.lower().startswith("hkeys("):
            handler.hash_hkeys(content[0])
        elif parsed_string.lower().startswith("set("):
            return handler.str_set(content[0], content[1])
        elif parsed_string.lower().startswith("hset("):
            return handler.hash_set(content[0], content[1], content[2])
        elif parsed_string.lower().startswith("del("):
            return handler.delete(content[0])
        elif parsed_string.lower().startswith("hdel("):
            return handler.str_set(content[0], content[1])
        elif parsed_string.lower().startswith("clean") and parsed_string != "clean_redis":
            return handler.clean_redis
        else:
            scope = {'handler': RedisHandler(config)}
            cli = "handler." + parsed_string
            return eval(cli, scope)

    match_start_position = cli.index(":", 0)
    parsed_string = cli[match_start_position + 1:]
    logger.debug("execute redis: { " + parsed_string + " }")
    content = re.findall(r'\'(.*?)\'', str(parsed_string))

    data_source = eval(rd) if isinstance(rd, Text) else rd
    if isinstance(data_source, List):
        for v in data_source:
            value = execute(v, content)
            if is_get() is True:
                if value is not None:
                    return value
                elif data_source.index(v) == len(data_source) - 1 and value is None:
                    return None
            if is_del() is True:
                if value == 1:  # delete success
                    logger.debug(f"在{v}中删除成功")
                    return 1
                elif data_source.index(v) == len(data_source) - 1 and value == 0:
                    return 0
            if is_exists() is True:
                if value == 1:
                    logger.debug(f"在{v}中存在key:{content}")
                    return value
                elif data_source.index(v) == len(data_source) - 1 and value == 0:
                    return 0
            else:
                return value

    else:
        return execute(data_source, content)


def execute_mongo(db: Union[str, dict], operation: Text) -> Text:
    match_start_position = operation.index(":", 0)
    parsed_string = operation[match_start_position + 1:]
    logger.debug("execute mongodb: { " + parsed_string + " }")
    scope = {'handler': MongoHandler(db)}
    cli = "handler." + parsed_string
    return eval(cli, scope)


def remove_bracket(word):
    if "[" not in word and "]" not in word:
        return word
    data1 = word.find("[")
    data2 = word.find("]")
    left = word[:data1]
    right = word[data2 + 1:]
    word = left + right
    return remove_bracket(word)


def remove_bracket_first(word):
    data1 = word.find("[")
    data2 = word.find("]")
    left = word[:data1]
    right = word[data2 + 1:]
    word = left + right
    return word


def quote_dict(content: Dict):
    for k, v in content.items():
        if isinstance(v, Text):
            content[k] = quote(v)
        else:
            content[k] = v
    return content


def unquote_dict(value: Union[Text, Dict]):
    if isinstance(value, Text):
        return unquote(value)
    if isinstance(value, Dict):
        for k, v in value.items():
            if isinstance(v, Text):
                value[k] = unquote(v)
            else:
                value[k] = unquote_dict(v)
        return value
    else:
        return value
