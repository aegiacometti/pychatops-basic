import json
from os import path

from pychatops.slack.common import auth_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops


def command_syntax():
    return '@Botnet users list/add/delete'


def command_help():
    return 'Command \"users\" help\n' \
           '********************\n' \
           'List, add or delete users authorization to execute commands.\n' \
           'The full detail of the command has to be specified.\n' \
           'Example:\n' \
           ' - @Botnet users list  ->  list all\n' \
           ' - @Botnet users delete _slack_id_  ->  delete user\n' \
           ' - @Botnet users add _group_ _slack_id_  ->  add to group'


def list_users(_authorization_file, bot_name, bot_oauth_token):
    text = ""
    try:
        with open(_authorization_file) as file:
            authorized_ids = json.load(file)

    except:
        script_name = path.basename(__file__)
        text = '`Authorization file not found`'
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='List userIDs', status='Failed',
                        result=text, auth='Denied')

    else:
        for group_id in authorized_ids.keys():
            text += "* Group name: {}\n".format(group_id)
            text += "Commands: {}\n".format(str(authorized_ids[group_id]['cmds']))
            if group_id != 'free':
                text += "Users:\n"
                for item in authorized_ids[group_id]['user_ids']:
                    username, user_email = auth_ops.get_slack_user_info(bot_oauth_token, item, bot_name)
                    text += f"{item} - {username} - {user_email}\n"
                text += "\n"
            else:
                text += "Users: all\n"
        text = "```" + text + "```"

    return text


def delete_user(_authorization_file, bot_name, user_id):
    found = False
    try:
        with open(_authorization_file) as file:
            authorized_ids = json.load(file)

    except:
        script_name = path.basename(__file__)
        text = '`Authorization file not found`'
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Delete userID', status='Failed',
                        result=text, auth='Denied')

    else:
        for group_id in authorized_ids.keys():
            if user_id in authorized_ids[group_id]['user_ids']:
                authorized_ids[group_id]['user_ids'].remove(user_id)
                found = True

    if found:
        file = open(_authorization_file, "w")
        json.dump(authorized_ids, file)
        file.close()
        return "```User deleted```"
    else:
        return "`User not found`"


def add_user(_authorization_file, bot_name, group, user_id, bot_oauth_token):
    try:
        with open(_authorization_file) as file:
            authorized_ids = json.load(file)

    except:
        script_name = path.basename(__file__)
        text = '`Authorization file not found`'
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Delete userID', status='Failed',
                        result=text, auth='Denied')

    else:
        if group in authorized_ids.keys():
            if user_id not in authorized_ids[group]['user_ids']:
                user = auth_ops.slack_valid_user(bot_oauth_token, user_id, bot_name)
                if user:
                    authorized_ids[group]['user_ids'].append(user_id)
                    file = open(_authorization_file, "w")
                    json.dump(authorized_ids, file)
                    file.close()
                    return "```User \"{}\" added to group \"{}\"```".format(user, group)
                else:
                    return "`userID does not exist in Slack`"
            else:
                return "`userID already in group`"
        else:
            return "`Invalid group`"


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']
    text = ''
    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) == 2 and command_splited[1] == 'list':
        text = list_users(kwargs['bot_authorized_users_file'], kwargs['bot_name'], kwargs['bot_oauth_token'])
        status = 'OK'
    elif len(command_splited) == 3 and command_splited[1] == 'delete':
        text = delete_user(kwargs['bot_authorized_users_file'], kwargs['bot_name'], command_splited[2])
        status = 'OK'
    elif len(command_splited) == 4 and command_splited[1] == 'add':
        text = add_user(kwargs['bot_authorized_users_file'], kwargs['bot_name'], command_splited[2], command_splited[3],
                        kwargs['bot_oauth_token'])
        status = 'OK'
    else:
        text = "`Invalid Syntax`"
        status = 'Failed'

    slack_ops.send_msg(slack_client, channel, text, kwargs['bot_name'])
    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status=status, result=text)
