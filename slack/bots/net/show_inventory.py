from os import path

from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net show.inventory'


def command_help():
    return 'Command \"show.inventory\" help\n' \
        '********************************\n' \
        'Display the list of devices in the inventory.\n' \
        'The filter option accepts partial strings and one \'*\'.\n ' \
        'Example:\n' \
        ' - @Bot-Net show.inventory -> will display the inventory\n' \
        ' - @Bot-Net show.inventory _filter_ -> will display the inventory filtering the output\n' \
        ' - @Bot-Net show.inventory mtz-*-01 -> will display the inventory filtering the output'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) == 1:
        string_filter = ''
        validate_hosts_ops.list_inventory(slack_client, channel, string_filter, kwargs['bot_cmd_log_file'], kwargs['username'],
                                          kwargs['command'], kwargs['bot_name'])

    elif len(command_splited) == 2:
        string_filter = command_splited[1]
        string_filter = string_filter.replace('*', '.*')
        validate_hosts_ops.list_inventory(slack_client, channel, string_filter, kwargs['bot_cmd_log_file'], kwargs['username'],
                                          kwargs['command'], kwargs['bot_name'])

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'],
                        channel=channel, username=kwargs['username'], cmd=kwargs['command'], auth='Approved',
                        status='Failed', result='Invalid Syntax')
