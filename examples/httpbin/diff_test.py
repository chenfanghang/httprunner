# @author: chenfanghang
# FROM: diff_test.yml


from rrtv_httprunner import HttpRunner, Config, Step, RunRequest


class TestCaseValidate(HttpRunner):
    config = Config("basic test with httpbin").base_url("http://httpbin.org/")
    a = {
        "code": "0",
        "message": "success"
    }
    b = {
        "message": "a",
        "code": "0",
    }
    teststeps = [
        Step(
            RunRequest("validate response with json diff")
                .get("/get")
                .with_params(**{"a": 1, "b": 2})
                .validate()
                .assert_diff(a, b, validate_value=False)
        ),
    ]


if __name__ == "__main__":
    TestCaseValidate().test_start()
