import json
import sys
from datetime import datetime
from os import getenv

_PYCHATOPS_HOME_DIRECTORY = getenv('PYCHATOPS')


def make_json(dt_string, bot_name, script_name, channel, username, cmd, auth, result, task_id, status):
    return {"date": dt_string, "bot_name": bot_name, "script_name": script_name, "channel": channel,
            "username": username, "cmd": cmd, "auth": auth, "status": status, "task_id": task_id, "result": result}


def log_msg(bot_name='NA', script_name='NA', bot_cmd_log_file='NA', channel='NA', username='NA', cmd='NA', auth='NA',
            status='NA', task_id='NA', result='NA'):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log_json = make_json(dt_string, bot_name, script_name, channel, username, cmd, auth, result, task_id, status)
    print(json.dumps(log_json))
    sys.stdout.flush()

    if bot_cmd_log_file != 'NA':
        file = open(_PYCHATOPS_HOME_DIRECTORY + bot_cmd_log_file, 'a')
        file.write(json.dumps(log_json) + "\n")
        file.close()
