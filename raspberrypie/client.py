import paho.mqtt.client as mqtt
from threading import Thread

from raspberrypie.database import *
from config import *
import utils.logger as logger
from utils.mqtt_util import on_rc
from utils import voice_player


class LocalClient:
    def __init__(self, client_id="mqtt_proxy", log_all=False):
        self.log = log_all

        # Client id, protocol version
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # Client id, username
        # self.client.username_pw_set(username, password)

        # Callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        if self.log:
            self.client.message_callback_add(local_topics['all'], self.on_message)
        self.client.message_callback_add(local_topics['report'], self.report)
        self.client.message_callback_add(local_topics['data'], self.on_data)
        self.client.message_callback_add(local_topics['login'], self.on_login)
        self.client.message_callback_add(local_topics['energy'], self.on_energy_upload)

        self.devices_databass = DeviceDatabass(history_shape=(2000, 3))

        self.devices_databass.add('bear-esp')

        try:
            self.client.connect(local_url, port=local_port)
            # subscribe
            self.client.subscribe([
                (local_topics['report'], 0),
                (local_topics['data'], 0),
                (local_topics['login'], 0),
                (local_topics['energy'], 0)
            ])
            if self.log:
                self.client.subscribe((local_topics['all'], 0))
        except ConnectionRefusedError:
            print("No local broker found. Try with 'mosquitto -v'.")
            exit()

    def start(self):
        self.thread = Thread(target=self.client.loop_forever)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        self.client.disconnect()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        log = f'Connect with return code: {str(rc)} ({on_rc(rc)})'
        logger.log('local', log)

    def on_login(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        id = message.payload.decode('utf-8')
        if self.devices_databass.check_id(id):
            logger.log('local', f'<{id}> has already in, skip to add')
        else:
            self.devices_databass.add(id)
            logger.log('local', f'<{id}> has logged in')

    def on_data(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Decode
        try:
            payload = message.payload.replace(b"'", b"\"")
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.log("local", "ON_DATA decode Error!")
            return

        id = data['id']
        if not self.devices_databass.check_id(id):
            logger.log('local', f'<{id}> has not logged in but is sending msg')
            return

        data_list = data['voltage'], data['current'], data['capacity']
        p = {
            'id': id,
            'energy': data['capacity']
        }
        self.client.publish(local_topics['energy'].replace('+', id), payload=json.dumps(p))
        self.devices_databass.store(id, data_list)

    def on_energy_upload(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Decode
        try:
            payload = message.payload.replace(b"'", b"\"")
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.log("local", "ON_DATA decode Error!")
            return

        id = data['id']
        if not self.devices_databass.check_id(id):
            logger.log('local', f'<{id}> has not logged in but is sending nrg')
            return

        data = {
            "services": [{
                "service_id": "Energy",
                "properties": {
                    "value": data['energy']
                }
            }]
        }
        # logger.log('test', json.dumps(data))
        self.target.client.publish(cloud_topics['upload'], payload=json.dumps(data))

    def report(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Decode
        try:
            payload = message.payload.replace(b"'", b"\"")
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.log("local", "REPORT decode Error!")
            return

        if not hasattr(self, 'target'):
            logger.log("local", "NO COULD CLIENT")
            return

        """ example msg:
        {"id": "bear-esp", "msg": "smoke", "ppm": 666}
        {"id": "bear-esp", "msg": "undetected"}
        {"id": "bear-esp", "msg": "finished"}
        """

        # upload payload
        if data['msg'] == "undetected":
            voice_player.on_beep()
        elif data['msg'] == "smoke":
            voice_player.on_warning()
        report_data = data
        # publish
        self.target.client.publish(cloud_topics['msg-up'], payload=json.dumps(report_data))

    def on_disconnect(self, client, userdata, rc):
        logger.log('local', f"Disconnect(rc: {str(rc)})")

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        payload = message.payload.decode('utf-8')
        logger.log_msg('local', message.topic, payload)

    def set_target_client(self, client):
        if not hasattr(self, 'target'):
            self.target = client

    def save(self):
        self.devices_databass.save_data_json()

    def get_data_of(self, id) -> dict:
        return self.devices_databass.get_data_json(id)

    def upload(self, oid, id=None):
        if id:
            payload = self.get_data_of(id)
            payload['oid'] = oid
            self.target.client.publish(cloud_topics['up_data'], payload=json.dumps(payload))
        else:
            for db_id in self.devices_databass.dbs.keys():
                payload = self.get_data_of(db_id)
                payload['oid'] = oid
                self.target.client.publish(cloud_topics['up_data'], payload=json.dumps(payload))
        # data = {
        #     'id': id,
        #     'voltage': [1, 2, 3, 4, 5],
        #     'current': [6, 7, 8, 9, 10],
        #     'capacity': [6, 6, 6, 6, 6]
        # }
        # self.target.client.publish(cloud_topics['up_data'], payload=json.dumps(data))

    def list_all_devices(self):
        print(self.devices_databass.dbs.keys())
