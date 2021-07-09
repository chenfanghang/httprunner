# @author: chenfanghang
import re
import unittest


class TestReg(unittest.TestCase):
    def legitimate_method_call(self, value):
        if value !="" and value is not None:
            i = 0
            is_show_left: bool = False
            value = list(value)
            while i != len(value) - 1:
                i = i + 1
                if is_show_left is False and (value[i] == ")" or value[i] == "}"):
                    return False
                elif value[i] == "{":
                    is_show_left = True
            return True
        else:
            return True


    def test_parse_variables_mapping(self):
        # function_regex_compile = re.compile(r"\$\{(\w+)\(([\$\S\w\s=,]*)\)\}")
        function_regex_compile1 = re.compile(r"\$\{(\w+)\(([\$\S\w\s=,]*)\)\}")
        function_regex_compile2 = re.compile(r"\$\{(\w+)\(([\$\S\w\s=,]*?)\)\}")
        value1 = '${str2int(${get_user_id(${a()})})}'
        value2 = '${str2int($get_user_id)}'
        value3 = '${string_toDatetime($beginTime)}${string_toDatetime($endTime)}'
        value4='\'${string_toDatetime($beginTime)}\' and \'${string_toDatetime($endTime)}\''
        value5="${a(${b()},c)}"
        value5 = '${sum1($test2[\'a\'],2)}'
        func_match1 = function_regex_compile1.match(value1, 0)
        func_match2 = function_regex_compile1.match(value2, 0)
        func_match3 = function_regex_compile1.match(value3, 0)
        func_match4 = function_regex_compile1.match(value4, 1)
        func_match5 = function_regex_compile1.match(value5, 0)
        # func_match4 = function_regex_compile2.match(value1, 0)
        # func_match5 = function_regex_compile2.match(value2, 0)
        # func_match6 = function_regex_compile2.match(value3, 0)
        # print(func_match.group(0))
        # print(func_match.group(1))
        # print(func_match1.group(2))
        # print(func_match2.group(2))
        # print(func_match3.group(2))
        # print(func_match4.group(2))
        print(func_match5.group(2))
        print(self.legitimate_method_call(func_match5.group(2)))
        if self.legitimate_method_call(func_match5.group(2)) is False:
            function_regex_compile2 = re.compile(r"\$\{(\w+)\(([\$\S\w\s=,]*?)\)\}")
            func_match5 = function_regex_compile2.match(value5, 0)
            print(func_match5.group(2))
            print(self.legitimate_method_call(func_match5.group(2)))
        # print(self.legitimate_method_call(func_match4.group(2)))
        # print(self.legitimate_method_call(func_match3.group(2)))
        # print(func_match4.group(2))
        # print(func_match5.group(2))
        # print(func_match6.group(2))
        # value = str(func_match3.group(2))
        # value2 = str(func_match6.group(2))
        # print(value, value2)
