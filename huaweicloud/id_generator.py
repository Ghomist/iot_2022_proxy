from hashlib import sha256
import hmac
from datetime import datetime


def generate(device_id: str, secret: str):
    assert device_id
    assert secret

    time_stamp = UTC_format_time()

    client_id = device_id+"_0_0_"+time_stamp
    username = device_id
    password = HmacSHA256(secret, time_stamp)

    return client_id, username, password


def UTC_format_time() -> str:
    time = datetime.utcnow()
    return "%04d%02d%02d%02d" % (time.year, time.month, time.day, time.hour)


def HmacSHA256(msg, key):
    return hmac.new(key.encode('utf-8'), msg.encode('utf-8'), sha256).hexdigest()


if __name__ == "__main__":
    device_id = input('Device id: ')
    secret = input('Secret: ')
    print("\n".join(generate(device_id, secret)))
