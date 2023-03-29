import json
import os

# DO NOT MODIFY
with open('DEVICES-KEY.bib') as bib:
    _devices_key = json.load(bib)
    device_id = _devices_key['device_id']
    secret = _devices_key['secret']

# cloud settings
cloud_url = 'a16236a40f.iot-mqtts.cn-north-4.myhuaweicloud.com'
cloud_port = 1883
cloud_topics = {
    "all": "$oc/#",
    "upload": f"$oc/devices/{device_id}/sys/properties/report",
    "cmd": f"$oc/devices/{device_id}/sys/commands/#",
    # "msg-down": f"$oc/devices/{device_id}/sys/messages/down"
    # "msg-up": f"$oc/devices/{device_id}/sys/messages/up"
    "up_data": "up_data",
    "msg-up": "msg_up"
}

# local client settings
local_url = '127.0.0.1'
local_port = 1883
local_topics = {
    "all": "dev/#",
    "login": "dev/+/login",
    "data": "dev/+/data",
    "energy": "dev/+/nrg",
    "report": "dev/+/report",
    "cmd": "dev/+/cmd"
}

# address of bear-pi micro
# pi_ip = '192.168.43.136'  # test hot spot (vivo)
pi_ip = '192.168.43.16'  # raspberry
pi_ip_backup = '192.168.43.17'
pi_port = 2506

# used by pi camera model
pi_cam_resolution = (320, 240)
pi_cam_fps = 15
pi_cam_conn_host = '43.138.249.229'
pi_cam_conn_port = 8878

# voice player settings
voice_path = '/home/pi/Music'
voice_vol_base = 0
voice_list = {
    'warning': 'warning_short.mp3',
    'info': 'info.mp3',
    'beep': 'beep.mp3',
}


def specific_cmd(id=None):
    """
    Get specific topic for each device with their id
    NONE FOR ALL
    """
    if id:
        return local_topics['cmd'].replace('+', id)
    else:
        return local_topics['cmd']
