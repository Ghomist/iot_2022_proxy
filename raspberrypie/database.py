import numpy as np
import json


class DeviceMemory:
    def __init__(self, shape):
        self.max_memory_cnt = shape[0]
        self.memory_len = shape[1]
        self.memory_cnt = 0
        self.array = np.zeros(shape, dtype=np.float16)

    def store(self, data):
        # out of bound
        if self.memory_cnt >= self.max_memory_cnt:
            return
        # store
        self.array[self.memory_cnt, :] = np.array(data, dtype=np.float16)
        self.memory_cnt += 1


class DeviceDatabass:
    def __init__(self, history_shape: tuple):
        self.device_cnt = 0
        self.shape = history_shape
        self.dbs = {}

    def add(self, id):
        self.dbs[id] = DeviceMemory(self.shape)
        self.device_cnt += 1

    def get(self, id) -> DeviceMemory:
        return self.dbs.get(id)

    def store(self, id, data):
        db = self.get(id)
        db.store(data)

    def get_data_json(self, id) -> dict:
        data = {
            'id': id,
            'voltage': [],
            'current': [],
            'capacity': []
        }
        db = self.dbs[id]
        # db: DeviceMemory
        for l in range(db.memory_cnt):
            data['voltage'].append(str(db.array[l, 0]))
            data['current'].append(str(db.array[l, 1]))
            data['capacity'].append(str(db.array[l, 2]))
        return data

    def save_data_json(self):
        for id, db in self.dbs:
            with open(f'{id}.json', 'w+') as f:
                data = self.get_data_json(id)
                json.dump(data, f)

    def check_id(self, id):
        return id in self.dbs.keys()
