import json
import traceback
from os import path

import requests
from pychatops.slack.common import log_ops


def authorize_txt(_authorization_file, item_id, bot_name):
    try:
        file = open(_authorization_file, 'r')
        authorized_ids = file.read()
        file.close()
    except:
        script_name = path.basename(__file__)
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Authorize userID', status='Failed',
                        result='Authorization file not found', auth='Denied')
        return False, []
    else:
        if item_id in authorized_ids:
            return "neteng", []
        else:
            return False, []


def authorize_json(_authorization_file, user_id, bot_name):
    try:
        with open(_authorization_file) as file:
            authorized_ids = json.load(file)
    except:
        script_name = path.basename(__file__)
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Authorize userID', status='Failed',
                        result='Authorization file not found', auth='Denied')
        return False, []
    else:
        for group_id in authorized_ids.keys():
            if user_id in authorized_ids[group_id]['user_ids']:
                return group_id, authorized_ids[group_id]['cmds']
        return 'free', authorized_ids['free']['cmds']


def get_slack_user_name(bot_oauth_token, slack_user_id, bot_name):
    script_name = path.basename(__file__)
    payload = {'token': bot_oauth_token, 'user': slack_user_id}
    response = requests.get('https://slack.com/api/users.info', params=payload)
    response_to_dict = json.loads(response.text)
    # noinspection PyBroadException
    try:
        return response_to_dict['user']['real_name']
    except Exception:
        trace_string = traceback.format_exc()
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Query username', status='Failed',
                        result=trace_string, auth='Approved')


def get_slack_user_info(bot_oauth_token, slack_user_id, bot_name):
    script_name = path.basename(__file__)
    payload = {'token': bot_oauth_token, 'user': slack_user_id}
    response = requests.get('https://slack.com/api/users.info', params=payload)
    response_to_dict = json.loads(response.text)
    # noinspection PyBroadException
    try:
        return response_to_dict['user']['real_name'], response_to_dict['user']['profile']['email']
    except Exception:
        trace_string = traceback.format_exc()
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Query username', status='Failed',
                        result=trace_string, auth='Approved')
        return 'null', 'null'


def slack_valid_user(bot_oauth_token, slack_user_id, bot_name):
    script_name = path.basename(__file__)
    payload = {'token': bot_oauth_token, 'user': slack_user_id}
    response = requests.get('https://slack.com/api/users.info', params=payload)
    response_to_dict = json.loads(response.text)
    # noinspection PyBroadException
    try:
        return response_to_dict['user']['real_name']
    except KeyError:
        return False
    except Exception:
        trace_string = traceback.format_exc()
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Query username', status='Failed',
                        result=trace_string, auth='Approved')
        return False
