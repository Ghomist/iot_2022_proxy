import paho.mqtt.client as mqtt
from threading import Thread
import socket
import base64

import huaweicloud.id_generator as generator
import huaweicloud.tcp_conn as tcp
from config import *
from utils import logger
from utils.mqtt_util import *
from huaweicloud.cam import PiCam
from utils import voice_player


class CloudClient:
    def __init__(self, device_id, secret, cam=None, log_all=False):
        self.cam = cam
        self.log = log_all
        # Client id, username, password
        self.client_id, self.username, self.password = generator.generate(device_id, secret)

        # Client id, protocol version
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)

        # Client id, username
        self.client.username_pw_set(self.username, self.password)

        # Set callback functions
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.message_callback_add(cloud_topics['cmd'], self.on_command_down)
        if self.log:
            self.client.message_callback_add(cloud_topics['all'], self.on_message)

        try:
            self.client.connect(cloud_url, port=cloud_port)
            # subscribe
            # self.client.subscribe()
        except Exception as e:
            print(f"Exception: {e}")
            exit()

    def start(self):
        self.thread = Thread(target=self.client.loop_forever)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        self.client.disconnect()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        log = f'Connect with return code: {str(rc)} ({on_rc(rc)})'
        logger.log('cloud', log)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        payload = msg.payload.decode('utf-8')
        logger.log_msg('cloud', msg.topic, payload)

    def on_disconnect(self, client, userdata, rc):
        logger.log('cloud', f"Disconnect(rc: {str(rc)})")

    def on_command_down(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        # Exclude response messages
        if "response" in msg.topic:
            return

        payload = json.loads(msg.payload)
        # Down command
        service_id = payload['service_id']
        cmd = payload['command_name']
        paras = payload['paras']
        if service_id == "Pile":
            if cmd == "POWER":
                if paras['ON'] == 1:  # open
                    tcp.send_cmd(b'1')
                    self.target.client.publish(specific_cmd('bear-esp'), payload='{"cmd": "detect_on"}')
                    voice_player.on_info()
                else:  # close
                    self.target.client.publish(specific_cmd('bear-esp'), payload='{"cmd": "detect_off"}')
                    tcp.send_cmd(b'0')
                    _id_ = paras['ID']
                    _oid_ = paras['ORDER']
                    self.target.upload(_oid_, _id_)
            elif cmd == "POWER_DELAY":
                if paras['ON'] == 1:  # open
                    tcp.send_cmd(b'1', paras['TIMEOUT'])
                    self.target.client.publish(specific_cmd('bear-esp'), payload='{"cmd": "detect_on"}')
                else:  # close
                    pass
                    # self.target.client.publish(specific_cmd('bear-esp'), payload='{"cmd": "detect_off"}')
                    # tcp.send_cmd(b'0')
                    # _id_ = paras['ID']
                    # _oid_ = paras['ORDER']
                    # self.target.upload(_oid_, _id_)
            elif cmd == "LOCK_OPEN":
                tcp.send_cmd(b'2')
            elif cmd == "BOOK":
                tcp.send_cmd(b'3')
        elif service_id == "Switch":
            if cmd == "SWITCH":
                target_id = paras['ID']
                cmd_payload = {'cmd': paras['MODE']}
                cmd_payload = json.dumps(cmd_payload)
                self.target.client.publish(specific_cmd(target_id), payload=cmd_payload)
        elif service_id == "Monitor":
            if cmd == "CAM":
                # cam = PiCam()
                if self.cam:
                    Thread(target=self.cam.streaming).start()
            elif cmd == "CAPTURE":
                if self.cam:
                    img_base64 = base64.b64encode(self.cam.img)
                    response_data = {
                        'result_code': 0,
                        'paras': {
                            'pic': img_base64.decode('utf-8')
                        }
                    }
                    self.client.publish(
                        topic=cmd_response_topic(msg.topic),
                        payload=json.dumps(response_data)
                    )
                    return

        response_topic = cmd_response_topic(msg.topic)
        self.client.publish(response_topic, payload=json.dumps({"result_code": 0}))

    def set_target_client(self, client):
        if not hasattr(self, 'target'):
            self.target = client
