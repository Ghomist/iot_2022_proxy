import requests
import json
from datetime import datetime

_alive_time = 20*60*60  # 超过这个时间才会申请新 token
_token = ''
_update_t = datetime.now()
_first_ = True


def _update_token():
    global _first_
    global _token
    global _update_t

    # test token alive
    if not _first_:
        now = datetime.now()
        if (now-_update_t).seconds < _alive_time:
            return
    else:
        _first_ = False

    header = {"Content-Type": "application/json;charset=utf8"}
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "dev-user",  # IAM用户名
                        "password": "JFpBUC!4c%",  # 华为云登录密码
                        "domain": {
                            "name": "hw031610095"  # 账号名
                        }
                    }
                }
            },
            "scope": {
                "project": {"name": "cn-north-4"}
            }
        }
    }
    response = requests.post(
        url="https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens",
        data=json.dumps(data),
        headers=header
    )
    _token, _update_t = response.headers['X-Subject-Token'], datetime.now()


def get_token():
    _update_token()

    global _token
    return _token


if __name__ == "__main__":
    print(get_token())
    print(_update_t)
