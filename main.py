import paho.mqtt.client as mqtt
import json
from threading import Thread
import sys

from config import *
from raspberrypie.client import LocalClient
from huaweicloud.cam import PiCam
from huaweicloud.client import CloudClient
from utils import logger
from utils.location import get_loc

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    # start argv
    log_all = False
    raspberry = True
    for arg in sys.argv:
        if arg == '--log' or arg == '-d':
            logger.log('arg', 'Log mode on')
            log_all = True
        elif arg == '--test' or arg == '-t':
            logger.log('arg', 'Test mode on, no locate-model or pi-cam')
            raspberry = False

    cam = None
    if raspberry:
        cam = PiCam()
        cam_thread = Thread(target=cam.detect_faces)
        cam_thread.start()

    # lease client
    cloud_client = CloudClient(device_id, secret, cam=cam, log_all=log_all)
    local_client = LocalClient(log_all=log_all)

    # bind target client
    local_client.set_target_client(cloud_client)
    cloud_client.set_target_client(local_client)

    cloud_client.start()
    local_client.start()

    # if raspberry:
    # loc, desc = get_loc()
    # loc = {
    #     'id': 'bear-esp',
    #     'msg': 'upload_location',
    #     'longi': loc[0],
    #     'lati': loc[1],
    #     'desc': desc
    # }
    # cloud_client.client.publish(cloud_topics['msg-up'], payload=json.dumps(loc))

    login_msg = {
        'id': 'bear-esp',
        'msg': 'login'
    }
    cloud_client.client.publish(cloud_topics['msg-up'], payload=json.dumps(login_msg))

    cmd_payload = {'cmd': 'grid_power'}
    cmd_payload = json.dumps(cmd_payload)
    local_client.client.publish(specific_cmd('bear-esp'), payload=cmd_payload)

    logger.log('cmd', 'Enter console')
    while True:
        try:
            cmd = input().split()
            response = f'ok: {cmd[0]}'
            if cmd[0] == 'stop':
                local_client.stop()
                cloud_client.stop()
                logger.log('cmd', 'Exiting')
                quit(0)
                exit(0)
            elif cmd[0] == 'list':
                local_client.list_all_devices()
            elif cmd[0] == 'save':
                local_client.save()
            elif cmd[0] == 'upload':
                local_client.upload(cmd[1])
            else:
                response = f'No such command: {cmd[0]}'
            logger.log('cmd', response)
        except KeyboardInterrupt:
            logger.log('cmd', 'Exiting')
            local_client.stop()
            cloud_client.stop()
            exit(0)
        except Exception as e:
            logger.log('cmd-err', str(e))


if __name__ == "__main__":
    main()
