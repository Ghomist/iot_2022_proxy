import json
import time


def _init():
    global max_len
    global cut_pos
    global time_log
    global log_file
    with open('utils/utils_config.json') as f:
        cfg = json.loads(f.read())
        max_len = cfg['logger']['max-len']
        cut_pos = int((max_len-4)/2)
        time_log = cfg['logger']['time-log']
        log_file = cfg['logger']['log-file']
    # with open(log_file, 'w+') as f:
    #     f.write(f"LOGGER INIT {time.strftime('%H:%M:%S', time.localtime())}\n\n")


def log(prefix, content):
    log = "["+prefix
    if time_log:
        log += " " + time.strftime('%H:%M:%S', time.localtime())
    log += "] "
    if len(content) < max_len:
        log += content
    else:
        log += content[:cut_pos-1]+'....'+content[1-cut_pos:]
    print(log)
    # with open(log_file, 'a+') as f:
    #     f.write(log)
    #     f.write('\n')


def log_msg(prefix, topic, payload):
    log(f'{prefix}-msg', f'<{topic}> {payload}')


_init()


if __name__ == "__main__":
    log('test', 'ccccttttentdddd!')
