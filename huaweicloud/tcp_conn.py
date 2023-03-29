from threading import Thread
from time import sleep
import socket

from config import *
from utils import logger


def send_cmd(cmd: int, delay=0):
    """
    using bytes!!!
    power off: 0
    power on: 1
    lock open: 2
    book: 3
    """
    Thread(target=_send_cmd_, args=[cmd, delay]).start()


def _send_cmd_(cmd, delay):
    sleep(delay)
    with socket.socket() as s:
        try:
            s.connect((pi_ip, pi_port))
            s.send(cmd)
            logger.log('tcp', f'send cmd: {cmd}')
        except Exception as e:
            logger.log('tcp', str(e))


# def _relay_on():
#     with socket.socket() as s:
#         try:
#             s.connect((pi_ip, pi_port))
#             s.send(b'1')
#         except Exception as e:
#             logger.log('tcp', str(e))


# def _relay_off():
#     with socket.socket() as s:
#         try:
#             s.connect((pi_ip, pi_port))
#             s.send(b'0')
#         except Exception as e:
#             logger.log('tcp', str(e))
