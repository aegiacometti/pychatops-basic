import re
from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net mshow src=_csv_device_list_ \"_command_\"'


def command_help():
    return 'Command \"mshow\" help\n' \
           '********************\n' \
           'Execute a "show running-config" on multiple device, according the list or group.\n' \
           'Example:\n' \
           ' - @Bot-Net mshow src=hq-core-1,network "show ip arp" -> will display the ARP table of the devices'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) >= 3 and str(command_splited[-1]).endswith("\"") and\
            str(command_splited[2]).startswith("\""):
        sources = re.search(r'src=(.*)', command_splited[1])
        destinations = "dummy"

        if sources and destinations:
            list_sources, sources_count, list_destinations, destinations_count =\
                validate_hosts_ops.identify_elements(sources[1], destinations[1])

            if sources_count != 0:

                if sources_count <= int(kwargs['max_devices']):
                    join_cmd = command_splited[2:]
                    pre_cmd = ""
                    for item in join_cmd:
                        pre_cmd += item + " "
                    final_cmd = pre_cmd[1:-2]

                    if len(final_cmd) < 51:
                        if final_cmd.startswith("show"):
                            playbook = "net-ios-show-msg-slack.yml"

                            bot_playbooks_directory = kwargs['bot_playbooks_directory']
                            playbook_full_path = bot_playbooks_directory + playbook
                            ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

                            json = True

                            ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name,
                                                    channel, slack_client, kwargs['username'], kwargs['bot_name'],
                                                    kwargs['bot_cmd_log_file'],
                                                    source=list(list_sources), cmd=final_cmd)

                    else:
                        slack_ops.send_msg(slack_client, channel, "`Command too long, max. 50 characters`",
                                           kwargs['bot_name'])
                        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                        username=kwargs['username'],
                                        cmd=kwargs['command'], auth='Approved', status='Failed',
                                        result='Command too long, max. 50 characters')

                else:
                    slack_ops.send_msg(slack_client, channel, "`Too many devices. Max {}`".format(kwargs['max_devices']), kwargs['bot_name'])
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'],
                                    cmd=kwargs['command'], auth='Approved', status='Failed',
                                    result='Too many devices. Max {}'.format(kwargs['max_devices']))

            else:
                slack_ops.send_msg(slack_client, channel, "`Invalid Sources`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Sources')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Devices`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Devices')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
