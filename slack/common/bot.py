import configparser
import importlib
import pkgutil
import sys
import time
import traceback
from os import path, getenv

from pychatops.slack.common import auth_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from slackclient import SlackClient

# PREVIOUSLY SETUP THE OPERATING SYSTEM ENVIRONMENT VALUE "NETOR" AT OS LEVEL, NET HERE
_PYCHATOPS_HOME_DIRECTORY = getenv('PYCHATOPS')

# DO NOT TOUCH THE FOLLOWING CODE
# Load bot variables value from configuration file

pychatops_config_path_name = _PYCHATOPS_HOME_DIRECTORY + "pychatops.config"
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(pychatops_config_path_name)
multiple_src_dst = config['Ansible']['multiple_src_dst']
max_devices = config['Ansible']['max_devices']
ansible_common_inventory_full_path_name = _PYCHATOPS_HOME_DIRECTORY + config['Ansible']['ansible_hosts_path_name']
_RTM_READ_DELAY = float(config['Slack']['slack_rtm_delay'])
bots_directory = _PYCHATOPS_HOME_DIRECTORY + config['Slack']['bots_directory']
rtm_read_delay = float(config['Slack']['slack_rtm_delay'])


def start(**kwargs):
    script_name = path.basename(__file__)
    bot_name = kwargs['bot_name'].lower()
    if bot_name == 'net':
        _RTM_READ_DELAY = 0.1
    else:
        _RTM_READ_DELAY = rtm_read_delay
    bot_log_file = _PYCHATOPS_HOME_DIRECTORY + config['Slack']['bot_' + bot_name + '_log_file']
    bot_cmd_log_file = config['Slack']['bot_' + bot_name + '_cmd_log']
    bot_oauth_token = config['Slack']['bot_' + bot_name + '_oauth']
    bot_playbooks_directory = _PYCHATOPS_HOME_DIRECTORY + config['Slack']['bot_' + bot_name +
                                                                          '_ansible_playbooks_full_path_name']
    bot_authorized_users_file = _PYCHATOPS_HOME_DIRECTORY + config['Slack']['bot_' + bot_name +
                                                                            '_authorized_users_file']
    extra_data_file = _PYCHATOPS_HOME_DIRECTORY + config['Slack']['bot_' + bot_name + '_extra_data_file']

    # sys.stdout = open(bot_log_file, 'a+')

    plugins_path = bots_directory + bot_name.lower() + "/"

    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)

    discovered_plugins = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in pkgutil.iter_modules([plugins_path])
        # if name.startswith('user_') or name.startswith('help')
    }

    log_ops.log_msg(bot_cmd_log_file=bot_cmd_log_file, status='Ok', username='System',
                    bot_name=bot_name, script_name=script_name, cmd='Start Bot', result="Started")

    slack_client = SlackClient(bot_oauth_token)

    if slack_client.rtm_connect(with_team_state=False):
        log_ops.log_msg(bot_cmd_log_file=bot_cmd_log_file, status='Ok',
                        bot_name=bot_name, script_name=script_name, username='System',
                        cmd='Connect to Slack', result="Bot Started and Running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            try:
                command, channel, slack_userid = slack_ops.parse_bot_commands(starterbot_id, slack_client.rtm_read())
            except Exception:
                trace_string = traceback.format_exc()
                log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                                cmd='Connect to Slack', status='Failed', username='System',
                                result="Can't connect\n" + trace_string + "\nRetrying")
                time.sleep(5)
                slack_client.rtm_connect(with_team_state=False)

            else:
                if command:
                    command_splited = command.split()
                    command_splited[0] = command_splited[0].replace('.', '_')
                    username = auth_ops.get_slack_user_name(bot_oauth_token, slack_userid, bot_name)

                    if command_splited[0] in discovered_plugins.keys():
                        if bot_authorized_users_file.endswith('all'):
                            user_group, auth_cmds = 'neteng', []
                        elif bot_authorized_users_file.endswith('txt'):
                            user_group, auth_cmds = auth_ops.authorize_txt(bot_authorized_users_file, slack_userid, bot_name)
                        else:
                            user_group, auth_cmds = auth_ops.authorize_json(bot_authorized_users_file, slack_userid, bot_name)

                        auth = 'Approved' if user_group else 'Denied'

                        log_ops.log_msg(bot_name=bot_name,
                                        script_name=script_name,
                                        bot_cmd_log_file=bot_cmd_log_file,
                                        channel=channel,
                                        username=username,
                                        cmd=command,
                                        auth=auth,
                                        status='Ok',
                                        result='Command recognized')

                        if (user_group is not False) and (
                                (user_group == "neteng") or (command_splited[0] in auth_cmds)):
                            discovered_plugins[command_splited[0]].run(discovered_plugins=discovered_plugins,
                                                                       command_splited=command_splited,
                                                                       slack_client=slack_client,
                                                                       channel=channel,
                                                                       bot_playbooks_directory=bot_playbooks_directory,
                                                                       ansible_common_inventory_full_path_name=
                                                                       ansible_common_inventory_full_path_name,
                                                                       bots_directory=bots_directory,
                                                                       netor_home_directory=_PYCHATOPS_HOME_DIRECTORY,
                                                                       bot_directory=bots_directory + bot_name,
                                                                       extra_data_file=extra_data_file,
                                                                       username=username,
                                                                       user_group=user_group,
                                                                       bot_cmd_log_file=bot_cmd_log_file,
                                                                       command=command,
                                                                       bot_name=bot_name,
                                                                       multiple_src_dst=multiple_src_dst,
                                                                       max_devices=max_devices,
                                                                       auth_cmds=auth_cmds,
                                                                       bot_authorized_users_file=bot_authorized_users_file,
                                                                       bot_oauth_token=bot_oauth_token)

                        else:
                            slack_ops.send_msg(slack_client, channel,
                                               "`User \"{}\" not authorized`".format(username),
                                               bot_name)
                            log_ops.log_msg(bot_name=bot_name,
                                            script_name=script_name,
                                            bot_cmd_log_file=bot_cmd_log_file,
                                            channel=channel,
                                            username=username,
                                            auth=auth,
                                            cmd=command,
                                            status='Failed',
                                            result='User not authorized')

                    else:
                        response = "`Command unknown. Try \"@Bot-" + bot_name.upper() + \
                                   " help\" to view available commands.`"

                        slack_ops.send_msg(slack_client, channel, response, bot_name)
                        log_ops.log_msg(bot_name=bot_name,
                                        script_name=script_name,
                                        bot_cmd_log_file=bot_cmd_log_file,
                                        channel=channel,
                                        username=username,
                                        cmd=command,
                                        status='Failed',
                                        result='Invalid command')

            time.sleep(_RTM_READ_DELAY)

    else:
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, username='System',
                        bot_cmd_log_file=bot_cmd_log_file,
                        cmd='Connect to Slack', status='Failed', result="Bot restart required")
