import io
import socket
import struct
import time
import picamera
import requests
import base64
import json
from threading import Thread

import config
from utils import (logger, hw_auth)


class PiCam:
    def __init__(self):
        self.data = b''
        self.img = b''
        self.cam_thread = Thread(target=self.run_camera)
        self.cam_thread.start()

    # def stop(self):
    #     self.cam_thread.join()

    def run_camera(self):
        self.camera = picamera.PiCamera()
        logger.log('cam', 'Camera activated')

        self.camera.resolution = config.pi_cam_resolution
        self.camera.framerate = config.pi_cam_fps
        # cam init
        time.sleep(2)
        start = time.time()
        stream = io.BytesIO()

        # send jpeg format video stream
        for foo in self.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            data = struct.pack('<L', stream.tell())
            # self.connection.write(data)
            # self.connection.flush()
            # self.client_socket.send(data)

            stream.seek(0)
            # self.connection.write(stream.read())
            self.img = stream.read()
            # self.client_socket.send(self.img)
            self.data = data+self.img
            if time.time() - start > 600:
                break
            stream.seek(0)
            stream.truncate()

    def streaming(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((config.pi_cam_conn_host, config.pi_cam_conn_port))
        # self.connection = self.client_socket.makefile('wb')
        logger.log('camera', 'Camera connected')
        try:
            while True:
                if self.data:
                    self.client_socket.send(self.data)
            # self.connection.write(struct.pack('<L', 0))
            self.client_socket.send(struct.pack('<L', 0))
        except ConnectionResetError:
            # ignore
            pass
        except BrokenPipeError:
            # ignore
            pass
        finally:
            self.connection.close()
            self.client_socket.close()

    def capture(self):
        self.camera.capture('tmp.jpeg', format='jpeg', resize=(100, 100))
        with open('tmp.jpeg', 'rb') as f:
            return f.read1()

    def search_face(self, face_bytes=None, face_base64=None) -> dict:
        face_set_name = 'main'
        endpoint = 'face.cn-north-4.myhuaweicloud.com'
        project_id = 'fdd36edb675d44bfaec42595bfdd4466'  # 开通服务所在region的用户项目ID
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': hw_auth.get_token()}

        url = f"https://{endpoint}/v2/{project_id}/face-sets/{face_set_name}/search"
        if face_bytes:
            image_base64 = base64.b64encode(face_bytes).decode("utf-8")
        elif face_base64:
            image_base64 = face_base64
        else:
            return None
        body = {
            "image_base64": image_base64,
            # "sort": [{"name": "asc"}],
            "return_fields": ["name"],
            # "filter": "timestamp:12"
            "threshold": 0.9
        }
        response = requests.post(url, headers=headers, json=body, verify=False)
        return json.loads(response.content.decode('utf-8'))

    def detect_faces(self):
        endpoint = 'face.cn-north-4.myhuaweicloud.com'
        project_id = 'fdd36edb675d44bfaec42595bfdd4466'  # 开通服务所在region的用户项目ID
        url = f"https://{endpoint}/v2/{project_id}/face-detect"

        t = time.time()
        while True:
            if time.time() - t < 1:
                continue

            t = time.time()

            image_data = self.img
            image_data = base64.b64encode(image_data).decode('utf-8')
            headers = {'Content-Type': 'application/json', 'X-Auth-Token': hw_auth.get_token()}
            body = {"image_base64": image_data}

            response = requests.post(url, headers=headers, json=body, verify=False)
            # logger.log('cam', response.content.decode('utf-8'))
            faces = json.loads(response.content.decode('utf-8')).get('faces')
            if faces and len(faces) != 0:
                logger.log('cam', 'Face detected')
                d = self.search_face(face_base64=image_data)
                if len(d['faces']) != 0:
                    most_face = d['faces'][0]
                    face_info = {
                        'name': most_face['external_fields']['name'],
                        'similarity': most_face['similarity']
                    }
                    logger.log('cam', 'Auto booking for '+str(face_info))
                    response = requests.post('http://43.138.249.229:8876/order/book', data={'openid': face_info['name'], 'device': 'bear-esp'})
                    if response.content:
                        oid = json.loads(response.content.decode('utf-8'))['oid']
                        requests.post('http://43.138.249.229:8876/order/start', data={'oid': oid, 'type': 0})
                        logger.log('cam', 'Book done')
                    # TODO


if __name__ == "__main__":
    cam = PiCam()
    cam.detect_faces()
